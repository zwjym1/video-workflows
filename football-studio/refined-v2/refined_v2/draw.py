"""精修 v2 的绘制原语。

参数对齐 vendor/core.py 与 vendor/render_v2.py：正俯视、2 倍超采样、
平滑步进、虚线箭头。这里不读取任何场次文件。
"""

from __future__ import annotations

import math
import os
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SS = 1280, 720, 25, 2
BG = (11, 21, 27)
WHITE = (242, 243, 233)
MUT = (145, 163, 166)
ATT = (192, 221, 61)
DEF = (241, 106, 83)
BALL = (241, 219, 70)
RUN = (185, 232, 88)
PITCH = (68, 88, 91)
MINI_PITCH = (86, 106, 108)

SPEC_FONT_NAME = "NotoSansSC-700"


def ease(v: float) -> float:
    v = max(0.0, min(1.0, v))
    return v * v * v * (v * (v * 6 - 15) + 10)


def ease_inv(p: float) -> float:
    p = max(0.0, min(1.0, p))
    lo, hi = 0.0, 1.0
    for _ in range(48):
        mid = (lo + hi) / 2
        if ease(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def pr(t, a, b) -> float:
    return ease((t - a) / max(0.001, b - a))


def mix(a, b, p):
    return tuple(x + (y - x) * p for x, y in zip(a, b))


def qtime(t: float) -> float:
    return round(float(t) * FPS) / FPS


def xy(p, s=SS):
    return tuple(round(z * s) for z in p)


def col(c, a=255):
    return tuple(c) + (round(max(0, min(255, a))),)


def resolve_font():
    env = os.environ.get("REFINED_V2_FONT")
    candidates = []
    if env:
        candidates.append(env)
    candidates.append("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
    for raw in candidates:
        path = Path(raw)
        if path.is_file():
            spec = SPEC_FONT_NAME in path.name
            note = (
                "文件名符合 NotoSansSC-700。"
                if spec
                else "使用系统里的文泉驿微米黑。这不是规范写的 NotoSansSC-700，字重不完全相同，没有把它当成已经对齐。"
            )
            return {"path": str(path), "spec_match": spec, "note": note}
    from .errors import EpisodeRejected

    raise EpisodeRejected("font", "没有可用的中文字体，拒绝渲染。不用缺字方框代替关系板。")


@lru_cache(None)
def font(n, s=SS, path=""):
    if not path:
        path = resolve_font()["path"]
    return ImageFont.truetype(path, round(n * s))


def line(d, points, c, w=2, s=SS):
    if len(points) > 1:
        d.line([xy(p, s) for p in points], fill=c, width=max(1, round(w * s)), joint="curve")


def text(d, p, st, n=24, c=WHITE, anchor="lt", s=SS, a=255, font_path=""):
    d.text(
        xy(p, s),
        st,
        font=font(n, s, font_path),
        fill=col(c, a),
        anchor=anchor,
        stroke_width=max(1, round(0.45 * s)),
        stroke_fill=(0, 0, 0, round(a * 0.5)),
    )


def trace(d, ps, c, width=2.4, p=1, dash=None, arrow=True, s=SS):
    if p <= 0 or len(ps) < 2:
        return None
    lengths = [math.dist(a, b) for a, b in zip(ps, ps[1:])]
    limit = sum(lengths) * min(1, p)
    dist = 0.0
    endp = ps[0]
    endangle = 0.0
    for a, b, length in zip(ps, ps[1:], lengths):
        if not length or dist >= limit:
            break
        take = min(length, limit - dist)
        cursor = 0.0
        while cursor < take - 1e-6:
            if dash:
                phase = (dist + cursor) % sum(dash)
                on = phase < dash[0]
                step = min(take - cursor, (dash[0] - phase) if on else (sum(dash) - phase))
            else:
                on = True
                step = take - cursor
            step = max(0.001, step)
            if on:
                line(d, [mix(a, b, cursor / length), mix(a, b, (cursor + step) / length)], c, width, s)
            cursor += step
        endp = mix(a, b, take / length)
        endangle = math.atan2(b[1] - a[1], b[0] - a[0])
        dist += length
    if arrow and p > 0.08:
        radius = 8
        pts = [
            endp,
            (endp[0] - radius * math.cos(endangle - 0.43), endp[1] - radius * math.sin(endangle - 0.43)),
            (endp[0] - radius * math.cos(endangle + 0.43), endp[1] - radius * math.sin(endangle + 0.43)),
        ]
        d.polygon([xy(z, s) for z in pts], fill=c)
    return endp


def pitch(d, project, color=PITCH, width=1.3, s=SS):
    loops = [
        [(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)],
        [(50, 0), (50, 100)],
        [(0, 20.35), (15.714, 20.35), (15.714, 79.65), (0, 79.65)],
        [(0, 36.53), (5.238, 36.53), (5.238, 63.47), (0, 63.47)],
        [(100, 20.35), (84.286, 20.35), (84.286, 79.65), (100, 79.65)],
        [(100, 36.53), (94.762, 36.53), (94.762, 63.47), (100, 63.47)],
        [(0, 44.6), (-2, 44.6), (-2, 55.4), (0, 55.4)],
        [(100, 44.6), (102, 44.6), (102, 55.4), (100, 55.4)],
    ]
    for pts in loops:
        line(d, [project(z) for z in pts], color, width, s)
    a = project((50 - 9.15 / 1.05, 50 - 9.15 / 0.68))
    b = project((50 + 9.15 / 1.05, 50 + 9.15 / 0.68))
    d.ellipse((*xy(a, s), *xy(b, s)), outline=color, width=max(1, round(width * s)))


def logical_text_width(draw, content, size, font_path):
    box = draw.textbbox((0, 0), content, font=font(size, SS, font_path))
    return (box[2] - box[0]) / SS
