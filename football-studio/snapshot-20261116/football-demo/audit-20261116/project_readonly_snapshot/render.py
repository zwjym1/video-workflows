#!/usr/bin/env python3
"""1280x720 30fps tactical film renderer.

Local Python/Pillow implementation. Not the official Lemo-Opuscar engine.
Style distilled from visible structure of the reference film (question open,
live freeze rings + black 2D board alternating, unmarked full-speed review).
Does not copy reference copy, branding, voice, or music.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "src/fonts"
W, H = 1280, 720
FPS = 30

GOLD = (232, 201, 86)
GOLD_SOFT = (232, 201, 86, 160)
WHITE = (240, 240, 236)
RED = (196, 42, 42)
RED_D = (150, 28, 32)
CLARET = (118, 52, 74)
CLARET_L = (160, 80, 100)
PITCH = (210, 210, 206)
BG = (10, 10, 12)
SUB_FILL = (255, 255, 255)
SUB_OUT = (12, 12, 12)


def load_fonts():
    def f(name, size):
        return ImageFont.truetype(str(FONT_DIR / name), size)

    return {
        "cn_h": f("NotoSansSC-900.ttf", 52),
        "cn_h2": f("NotoSansSC-900.ttf", 44),
        "cn_b": f("NotoSansSC-700.ttf", 34),
        "cn_b2": f("NotoSansSC-700.ttf", 30),
        "cn_s": f("NotoSansSC-500.ttf", 22),
        "cn_xs": f("NotoSansSC-500.ttf", 18),
        "en_b": f("BarlowCondensed-SemiBold.ttf", 42),
        "en_s": f("BarlowCondensed-SemiBold.ttf", 22),
        "mono": f("IBMPlexMono-Medium.ttf", 16),
        "num": f("BarlowCondensed-SemiBold.ttf", 20),
        "num2": f("BarlowCondensed-SemiBold.ttf", 18),
    }


FONTS = None


def fonts():
    global FONTS
    if FONTS is None:
        FONTS = load_fonts()
    return FONTS


def text_size(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]


def draw_text_outline(draw, xy, text, font, fill=SUB_FILL, outline=SUB_OUT, width=2, anchor="lt"):
    x, y = xy
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx * dx + dy * dy <= width * width:
                draw.text((x + dx, y + dy), text, font=font, fill=outline, anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


def rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def dashed_polyline(draw, pts, fill, width=3, on=12, off=8):
    if len(pts) < 2:
        return
    # flatten to segments
    dist = 0
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        seg = math.hypot(x2 - x1, y2 - y1)
        if seg < 1:
            continue
        ux, uy = (x2 - x1) / seg, (y2 - y1) / seg
        t = 0
        drawing = True
        # continue dash phase from dist
        phase = dist % (on + off)
        if phase >= on:
            drawing = False
            t = (on + off) - phase
        else:
            drawing = True
            t = on - phase
        px, py = x1, y1
        traveled = 0
        while traveled < seg:
            step = min(t, seg - traveled)
            nx, ny = px + ux * step, py + uy * step
            if drawing:
                draw.line((px, py, nx, ny), fill=fill, width=width)
            traveled += step
            px, py = nx, ny
            drawing = not drawing
            t = on if drawing else off
        dist += seg


def arrow(draw, p1, p2, fill, width=3, head=14):
    x1, y1 = p1
    x2, y2 = p2
    draw.line((x1, y1, x2, y2), fill=fill, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    for da in (2.6, -2.6):
        hx = x2 + head * math.cos(ang + da)
        hy = y2 + head * math.sin(ang + da)
        draw.line((x2, y2, hx, hy), fill=fill, width=width)


def dashed_arrow(draw, p1, p2, fill, width=3, head=14, on=12, off=8):
    # shorten so head sits at p2
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    end = (p2[0] - head * 0.4 * math.cos(ang), p2[1] - head * 0.4 * math.sin(ang))
    dashed_polyline(draw, [p1, end], fill=fill, width=width, on=on, off=off)
    arrow(draw, (end[0] - 2 * math.cos(ang), end[1] - 2 * math.sin(ang)), p2, fill, width=width, head=head)


def ring(draw, c, r, fill, width=3, alpha=None):
    x, y = c
    bbox = [x - r, y - r, x + r, y + r]
    base = fill[3] / 255 if len(fill) == 4 else 1.0
    if alpha is None:
        col = fill if len(fill) == 4 else (*fill, 255)
    else:
        col = (*fill[:3], int(alpha * base))
    draw.ellipse(bbox, outline=col, width=width)


def concentric_rings(draw, c, r0, n=3, fill=GOLD, width=2, fade=True):
    for i in range(n):
        rr = r0 + i * 10
        a = 220 if not fade else max(70, 220 - i * 70)
        ring(draw, c, rr, fill, width=width if i == 0 else 2, alpha=a)


class SourceCache:
    def __init__(self, folder: Path):
        self.folder = folder
        self._mem = {}

    def get(self, n: int) -> Image.Image:
        if n not in self._mem:
            p = self.folder / f"n{n:04d}.jpg"
            # files are 0001.jpg = n 0
            p = self.folder / f"{n + 1:04d}.jpg"
            im = Image.open(p).convert("RGB")
            self._mem[n] = im
        return self._mem[n].copy()


def stamp_replay_label(im: Image.Image, tl: dict) -> Image.Image:
    """Corner tag only. Do not cover the official 3-4 bug or invent a live score."""
    l, t0, r, b = tl["replay_label"]
    draw = ImageDraw.Draw(im)
    rounded_rect(draw, [l, t0, r, b], 8, fill=(18, 18, 20), outline=(70, 70, 74), width=1)
    cx, cy = (l + r) / 2, (t0 + b) / 2 - 1
    draw.text((cx, cy), "回放拆解", font=fonts()["cn_s"], fill=WHITE, anchor="mm")
    return im


def zoom_at(im: Image.Image, cx, cy, scale: float) -> Image.Image:
    w, h = im.size
    nw, nh = max(2, int(round(w / scale))), max(2, int(round(h / scale)))
    l = int(round(cx - nw / 2))
    t = int(round(cy - nh / 2))
    l = max(0, min(l, w - nw))
    t = max(0, min(t, h - nh))
    return im.crop((l, t, l + nw, t + nh)).resize((w, h), Image.Resampling.LANCZOS)


def subtitle(draw, text, y=668, font=None, fill=SUB_FILL):
    if not text:
        return
    font = font or fonts()["cn_b"]
    draw_text_outline(draw, (W // 2, y), text, font, fill=fill, outline=SUB_OUT, width=3, anchor="mm")


# ---------- live freeze overlays ----------
def overlay_freeze(im: Image.Image, key: str, tl: dict, t_local: float, n_out: int) -> Image.Image:
    fz = tl["freeze"][key]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    appear = min(1.0, t_local / 0.25)

    def a(c, alpha=220):
        return (*c[:3], int(alpha * appear))

    if key == "f62400":
        concentric_rings(d, fz["winger"], 26, n=2, fill=a(GOLD, 230), width=3)
        ring(d, fz["ball"], 9, a(WHITE, 230), width=2)
        concentric_rings(d, fz["p11"], 28, n=2, fill=a(GOLD, 230), width=3)
        # small 11 chip
        chip(d, (fz["p11"][0] + 26, fz["p11"][1] - 28), "11", a(RED, 240))
        # no arrow yet — he is still holding
    elif key == "f62488":
        concentric_rings(d, fz["winger"], 24, n=2, fill=a(GOLD, 230), width=3)
        ring(d, fz["ball"], 9, a(WHITE, 230), width=2)
        # pass into left of the box (direction of the ball, toward space #11 is attacking)
        target = (720, 300)
        dashed_arrow(d, fz["ball"], target, a(GOLD, 230), width=3, head=12, on=10, off=7)
        concentric_rings(d, fz["p11"], 28, n=2, fill=a(GOLD, 230), width=3)
        chip(d, (fz["p11"][0] + 26, fz["p11"][1] - 28), "11", a(RED, 240))
    elif key == "f62704":
        # space lens between #11 and the nearest defender, toward the shooting lane
        gap_c = ((fz["p11"][0] + fz["ball"][0]) / 2 + 8, (fz["p11"][1] + fz["ball"][1]) / 2 - 6)
        bbox = [gap_c[0] - 36, gap_c[1] - 22, gap_c[0] + 48, gap_c[1] + 28]
        d.ellipse(bbox, outline=a(GOLD, 180), width=2)
        concentric_rings(d, fz["p11"], 30, n=2, fill=a(GOLD, 230), width=3)
        ring(d, fz["ball"], 9, a(WHITE, 230), width=2)
        # discreet marks on the three seen defenders (no numbers unless worn; we read 14/22/3 earlier? don't force if not clearly read in VO)
        # Official shirts were visible in tight crops as 14/22/3 — only mark as opponents, no names.
        for pt in (fz["v14"], fz["v22"], fz["v3"]):
            ring(d, pt, 16, a(CLARET_L, 180), width=2)
        chip(d, (fz["p11"][0] - 30, fz["p11"][1] - 32), "11", a(RED, 240))
        # far-post hint, short dashed
        far = (1098, 306)
        dashed_arrow(d, fz["ball"], far, a(GOLD, 200), width=3, head=12, on=10, off=7)

    out = im.convert("RGBA")
    out = Image.alpha_composite(out, layer)
    return out.convert("RGB")


def chip(draw, c, text, fill):
    r = 13
    x, y = c
    draw.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=(255, 255, 255, fill[3] if len(fill) == 4 else 255), width=1)
    col = (255, 255, 255, fill[3] if len(fill) == 4 else 255)
    draw.text((x, y), text, font=fonts()["num"], fill=col, anchor="mm")


def overlay_shot_mark(im: Image.Image, src: SourceCache, n: int, tl: dict, t_local: float) -> Image.Image:
    """Very discreet #11 ring only around the first-time contact window."""
    # src n 133 = 627.08, contact through ~627.16 (n 135), ball gone by 627.24 (n 137)
    if n > 140:
        return im
    fz = tl["freeze"]["f62704"]
    # interpolate a little from 627.04 feet toward the ball direction
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fade = 1.0 if n <= 136 else max(0.0, 1.0 - (n - 136) / 5)
    ring(d, fz["p11"], 30, (*GOLD, int(200 * fade)), width=3)
    chip(d, (fz["p11"][0] - 30, fz["p11"][1] - 32), "11", (*RED, int(220 * fade)))
    out = Image.alpha_composite(im.convert("RGBA"), layer)
    return out.convert("RGB")


# ---------- 2D board ----------
# Pitch: goal on the right, United left wing at the top.
GL = 1100  # goal line x
TY, BY = 100, 620
CY = (TY + BY) / 2
PPM = (BY - TY) / 68.0  # px per metre


def X(meters_from_goal: float) -> float:
    return GL - meters_from_goal * PPM


def Y_from_left_touch(meters: float) -> float:
    return TY + meters * PPM


def pitch_layer() -> Image.Image:
    im = Image.new("RGB", (W, H), BG)
    px = im.load()
    # faint vertical shade like a dark pitch
    for x in range(W):
        shade = 10 + int(6 * math.sin(x / 38.0))
        for y in range(H):
            # slight vignette
            vx = abs(x - W / 2) / (W / 2)
            vy = abs(y - H / 2) / (H / 2)
            v = 1.0 - 0.18 * (vx * vx + vy * vy)
            g = max(0, min(20, int(shade * v)))
            px[x, y] = (g, g, g + 1)
    d = ImageDraw.Draw(im)
    # touch + goal line + halfway hint + 18 / 6 / D / spots
    box18 = 16.5 * PPM
    box6 = 5.5 * PPM
    w18 = 40.32 * PPM
    w6 = 18.32 * PPM
    x18 = GL - box18
    x6 = GL - box6
    y18a, y18b = CY - w18 / 2, CY + w18 / 2
    y6a, y6b = CY - w6 / 2, CY + w6 / 2
    # halfway
    xh = X(52.5)
    d.line([(xh, TY), (xh, BY)], fill=PITCH, width=2)
    # center circle
    cr = 9.15 * PPM
    d.ellipse([xh - cr, CY - cr, xh + cr, CY + cr], outline=PITCH, width=2)
    # sidelines + goal line + a bit of the far half
    left_x = 120
    d.line([(left_x, TY), (GL, TY)], fill=PITCH, width=2)
    d.line([(left_x, BY), (GL, BY)], fill=PITCH, width=2)
    d.line([(left_x, TY), (left_x, BY)], fill=PITCH, width=2)
    d.line([(GL, TY), (GL, BY)], fill=PITCH, width=3)
    # 18-yard
    d.line([(x18, y18a), (GL, y18a)], fill=PITCH, width=2)
    d.line([(x18, y18b), (GL, y18b)], fill=PITCH, width=2)
    d.line([(x18, y18a), (x18, y18b)], fill=PITCH, width=2)
    # 6-yard
    d.line([(x6, y6a), (GL, y6a)], fill=PITCH, width=2)
    d.line([(x6, y6b), (GL, y6b)], fill=PITCH, width=2)
    d.line([(x6, y6a), (x6, y6b)], fill=PITCH, width=2)
    # D
    ps = (X(11), CY)
    rad = 9.15 * PPM
    # only the part left of the 18-yard line
    d.arc([ps[0] - rad, ps[1] - rad, ps[0] + rad, ps[1] + rad], start=110, end=250, fill=PITCH, width=2)
    # penalty spot + centre spot
    r = 3
    d.ellipse([ps[0] - r, ps[1] - r, ps[0] + r, ps[1] + r], fill=PITCH)
    d.ellipse([xh - r, CY - r, xh + r, CY + r], fill=PITCH)
    # goal mouth
    gw = 7.32 * PPM
    d.line([(GL, CY - gw / 2), (GL + 14, CY - gw / 2)], fill=PITCH, width=3)
    d.line([(GL, CY + gw / 2), (GL + 14, CY + gw / 2)], fill=PITCH, width=3)
    d.line([(GL + 14, CY - gw / 2), (GL + 14, CY + gw / 2)], fill=PITCH, width=3)
    return im


PITCH_BG = None


def pitch():
    global PITCH_BG
    if PITCH_BG is None:
        PITCH_BG = pitch_layer()
    return PITCH_BG.copy()


def player_dot(draw, c, team, number=None, focus=False, alpha=255, r=16):
    x, y = c
    if team == "utd":
        fill = (*RED, alpha)
        outline = (255, 255, 255, alpha)
    else:
        fill = (*CLARET, alpha)
        outline = (230, 200, 210, alpha)
    if focus:
        for i, rr in enumerate((r + 20, r + 12, r + 6)):
            ring(draw, c, rr, (*GOLD, int(alpha * (0.45 - i * 0.1))), width=2)
    draw.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=outline, width=2)
    if number is not None:
        draw.text((x, y + 1), str(number), font=fonts()["num"], fill=(255, 255, 255, alpha), anchor="mm")


# schematic positions (metres): from goal, from left touch (United left = 0)
# United attacking to the right (decreasing metres-from-goal).
POS = {
    "winger_1": (X(24.0), Y_from_left_touch(4.5)),
    "winger_2": (X(18.5), Y_from_left_touch(4.0)),
    "p11_1": (X(18.0), Y_from_left_touch(22.0)),
    "p11_2": (X(15.5), Y_from_left_touch(20.5)),
    "p11_3": (X(12.0), Y_from_left_touch(19.5)),
    "ball_2": (X(16.0), Y_from_left_touch(12.0)),
    "ball_in": (X(12.5), Y_from_left_touch(18.0)),
    "v14": (X(10.0), Y_from_left_touch(18.5)),
    "v22": (X(9.5), Y_from_left_touch(26.5)),
    "v3": (X(8.0), Y_from_left_touch(15.5)),
    "gk": (X(2.5), Y_from_left_touch(33.5)),
    "far_post": (GL, CY + 7.32 * PPM / 2 - 2),
}


def fade(t, t0, t1):
    if t <= t0:
        return 0.0
    if t >= t1:
        return 1.0
    return (t - t0) / (t1 - t0)


def render_board(kind: str, t_local: float, dur: float, caption: str) -> Image.Image:
    im = pitch()
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    a1 = int(255 * fade(t_local, 0.05, 0.45))
    a2 = int(255 * fade(t_local, 0.35, 0.85))
    a3 = int(255 * fade(t_local, 0.9, 1.5))

    if kind == "receive":
        player_dot(d, POS["winger_1"], "utd", number=None, focus=True, alpha=a1)
        player_dot(d, POS["p11_1"], "utd", number=11, focus=True, alpha=a1)
        # a couple of seen Villa shapes near the box, no invented off-ball story
        player_dot(d, POS["v14"], "vil", alpha=int(a1 * 0.85), r=14)
        player_dot(d, POS["v22"], "vil", alpha=int(a1 * 0.85), r=14)
        player_dot(d, POS["v3"], "vil", alpha=int(a1 * 0.85), r=14)
        player_dot(d, POS["gk"], "vil", alpha=int(a1 * 0.7), r=13)
    elif kind == "pass":
        player_dot(d, POS["winger_2"], "utd", focus=True, alpha=a1)
        # carry ghost
        if a1:
            dashed_polyline(d, [POS["winger_1"], POS["winger_2"]], (*GOLD, a1), width=3, on=10, off=7)
        if a2:
            dashed_arrow(d, POS["winger_2"], POS["ball_in"], (*GOLD, a2), width=3, head=14, on=10, off=7)
        player_dot(d, POS["p11_2"], "utd", number=11, focus=True, alpha=a1)
        if a2:
            dashed_polyline(d, [POS["p11_1"], POS["p11_2"]], (*WHITE, int(a2 * 0.7)), width=2, on=8, off=6)
        player_dot(d, POS["v14"], "vil", alpha=int(a1 * 0.85), r=14)
        player_dot(d, POS["v22"], "vil", alpha=int(a1 * 0.85), r=14)
        player_dot(d, POS["v3"], "vil", alpha=int(a1 * 0.85), r=14)
        player_dot(d, POS["gk"], "vil", alpha=int(a1 * 0.7), r=13)
    elif kind == "recap":
        player_dot(d, POS["winger_2"], "utd", focus=False, alpha=a1)
        dashed_polyline(d, [POS["winger_1"], POS["winger_2"]], (*GOLD, a1), width=3, on=10, off=7)
        if a2:
            dashed_arrow(d, POS["winger_2"], POS["ball_in"], (*GOLD, a2), width=3, head=14)
        # 11 run
        dashed_polyline(d, [POS["p11_1"], POS["p11_3"]], (*WHITE, a1), width=2, on=8, off=6)
        player_dot(d, POS["p11_3"], "utd", number=11, focus=True, alpha=a1)
        player_dot(d, POS["v14"], "vil", alpha=int(a1 * 0.9), r=14)
        player_dot(d, POS["v22"], "vil", alpha=int(a1 * 0.85), r=14)
        player_dot(d, POS["v3"], "vil", alpha=int(a1 * 0.85), r=14)
        player_dot(d, POS["gk"], "vil", alpha=int(a1 * 0.7), r=13)
        if a3:
            arrow(d, POS["p11_3"], POS["far_post"], (*GOLD, a3), width=3, head=14)
            # small space mark
            gx, gy = (POS["p11_3"][0] + POS["v14"][0]) / 2, (POS["p11_3"][1] + POS["v14"][1]) / 2
            d.ellipse([gx - 28, gy - 18, gx + 34, gy + 20], outline=(*GOLD, a3), width=2)

    im = Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")
    d2 = ImageDraw.Draw(im)
    if caption and t_local > 0.3:
        subtitle(d2, caption, y=678, font=fonts()["cn_b2"])
    return im


def render_open(src: SourceCache, tl: dict, i_local: int, n_out: int, n: int) -> Image.Image:
    """Real continuous build-up (not a Ken-Burns still). Stops before the strike."""
    im = stamp_replay_label(src.get(n), tl)
    # light bottom fade only so the outlined question stays readable; pitch remains visible
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bp = band.load()
    y0_fade = 600
    for y in range(y0_fade, H):
        a = int(130 * (y - y0_fade) / max(1, H - 1 - y0_fade))
        for x in range(W):
            bp[x, y] = (0, 0, 0, a)
    im = Image.alpha_composite(im.convert("RGBA"), band).convert("RGB")
    d = ImageDraw.Draw(im)
    f = fonts()["cn_h"]
    y0 = 580
    draw_text_outline(d, (W // 2, y0), "这个射门空间，", f, fill=WHITE, width=3, anchor="mm")
    draw_text_outline(d, (W // 2, y0 + 64), "是怎么出现的？", f, fill=WHITE, width=3, anchor="mm")
    return im


def render_endcard() -> Image.Image:
    im = Image.new("RGB", (W, H), (8, 8, 10))
    d = ImageDraw.Draw(im)
    f = fonts()
    draw_text_outline(d, (W // 2, 330), "学习样片", f["cn_h2"], fill=WHITE, width=2, anchor="mm")
    draw_text_outline(
        d,
        (W // 2, 400),
        "画面来源：曼联官方 YouTube 加长集锦",
        f["cn_b2"],
        fill=(200, 200, 196),
        width=2,
        anchor="mm",
    )
    return im


def src_index(n0, n1, i, n_out):
    if n_out <= 1:
        return n1
    span = n1 - n0 + 1
    return min(n1, n0 + int(i * span / n_out))


def caption_for_time(t, tl):
    """Active VO line as subtitle (full sentence, not karaoke)."""
    # (start, end, text)
    lines = [
        (1.00, 5.20, tl["captions"]["open"]),
        (8.15, 10.20, tl["captions"]["first"]),
        (17.55, 22.00, tl["captions"]["s1"]),
        (27.72, 31.90, tl["captions"]["s2"]),
        (39.85, 44.70, tl["captions"]["s3"]),
        (45.10, 49.00, tl["captions"]["recap"]),
    ]
    for a, b, text in lines:
        if a - 0.05 <= t < b:
            return text
    return ""


def render_frame(out_i: int, tl: dict, src: SourceCache, index) -> tuple[Image.Image, dict]:
    seg, local, t0 = index[out_i]
    t = out_i / FPS
    kind = seg["kind"]
    rec = {
        "out_idx": out_i,
        "out_t": round(t, 4),
        "seg": seg["id"],
        "src_t": "",
        "src_frame": "",
        "src_file": "",
        "overlay": kind,
    }
    if kind == "open":
        n = src_index(seg.get("n0", 0), seg.get("n1", 131), local, seg["n_out"])
        im = render_open(src, tl, local, seg["n_out"], n)
        rec["src_t"] = round(tl["clip_start_t"] + n / tl["src_fps"], 4)
        rec["src_frame"] = tl["clip_start_frame"] + n
        rec["src_file"] = f"{n + 1:04d}.jpg"
        rec["overlay"] = "open_question"
        return im, rec
    if kind == "endcard":
        return render_endcard(), rec
    if kind == "board":
        cap_key = {"receive": "s1", "pass": "s2", "recap": "recap"}[seg["board"]]
        im = render_board(seg["board"], local / FPS, seg["n_out"] / FPS, tl["captions"][cap_key])
        rec["overlay"] = "board_" + seg["board"]
        return im, rec
    if kind in ("play", "freeze"):
        if kind == "freeze":
            n = tl["freeze"][seg["key"]]["n"]
            src_t = tl["clip_start_t"] + n / tl["src_fps"]
            im = stamp_replay_label(src.get(n), tl)
            im = overlay_freeze(im, seg["key"], tl, local / FPS, seg["n_out"])
            # freeze subtitles via global caption clock
        else:
            n = src_index(seg["n0"], seg["n1"], local, seg["n_out"])
            src_t = tl["clip_start_t"] + n / tl["src_fps"]
            im = stamp_replay_label(src.get(n), tl)
            if seg.get("mark_shot"):
                im = overlay_shot_mark(im, src, n, tl, local / FPS)
        rec["src_t"] = round(tl["clip_start_t"] + n / tl["src_fps"], 4)
        rec["src_frame"] = tl["clip_start_frame"] + n
        rec["src_file"] = f"{n + 1:04d}.jpg"
        rec["overlay"] = seg["id"]
        # captions: none on unmarked replay; first_watch has its own short caption
        d = ImageDraw.Draw(im)
        if not seg.get("unmarked"):
            if seg["id"] == "first_watch" and local / FPS < seg.get("caption_s", 0):
                subtitle(d, seg.get("caption") or "", y=668)
            else:
                cap = caption_for_time(t, tl)
                # don't repeat the opening question during open (handled there); play/freeze/slow yes
                if cap and seg["id"] != "first_watch":
                    # first_watch only uses the short lead; its VO line already shown
                    subtitle(d, cap, y=668)
        return im, rec
    raise RuntimeError("unknown kind " + kind)


def build_index(tl):
    idx = []
    for seg in tl["segments"]:
        t0 = len(idx) / FPS
        for i in range(seg["n_out"]):
            idx.append((seg, i, t0))
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "out/frames"))
    args = ap.parse_args()
    tl = json.loads((ROOT / "src/timeline.json").read_text())
    fonts()  # preload
    src = SourceCache(ROOT / tl["clip_dir"])
    index = build_index(tl)
    total = len(index)
    print("total frames", total, "duration", total / FPS, flush=True)

    still_ids = {
        "open_0s": 0,
        "open_1s": 30,
        "open_3s": 90,
        "open_6s": 180,
        "first_start": 240,
        "first_mid": 240 + 109,
        "freeze1": 525 + 12,
        "board1_mid": 606 + 96,
        "freeze2": 830 + 12,
        "board2_mid": 911 + 96,
        "freeze3": 1194 + 16,
        "slow_mid": 1278 + 20,
        "recap_mid": 1348 + 96,
        "replay_mid": 1540 + 109,
        "replay_goal": 1720,
        "endcard": 1758 + 20,
    }

    if args.stills:
        dest = ROOT / "out/stills"
        dest.mkdir(parents=True, exist_ok=True)
        for name, i in still_ids.items():
            im, rec = render_frame(i, tl, src, index)
            p = dest / f"{name}_{i:05d}.jpg"
            im.save(p, quality=92, subsampling=0)
            print("still", name, rec, flush=True)
        return

    if not args.full:
        print("pass --stills or --full", file=sys.stderr)
        sys.exit(2)

    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    map_path = ROOT / "out/map/frame-map.csv"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    with map_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["out_idx", "out_t", "seg", "src_t", "src_frame", "src_file", "overlay"])
        w.writeheader()
        for i in range(total):
            im, rec = render_frame(i, tl, src, index)
            im.save(dest / f"{i + 1:05d}.jpg", quality=90)
            w.writerow(rec)
            if i % 50 == 0 or i == total - 1:
                print(f"render {i + 1}/{total}", flush=True)


if __name__ == "__main__":
    main()
