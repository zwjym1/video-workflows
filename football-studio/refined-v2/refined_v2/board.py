"""一块关系板的画面。

布局和画法跟精修 render_v2.board 一致：问句、攻左、局部正俯视、
黄实球路、绿虚跑动、红虚防守、右上同向总览、编号圆点、最多三个短标签。
球员号码和颜色来自场次包的 number / team，不再从 A/L 前缀猜测。
"""

from __future__ import annotations

import json
import math

from PIL import Image, ImageDraw

from . import draw as D
from .errors import EpisodeRejected
from .legacy import find_legacy

_BASES = {}


def clear_cache():
    _BASES.clear()


def project(projection, uv):
    return (
        projection["cx"] + (uv[0] * 1.05 - projection["centre_m"][0]) * projection["scale"],
        projection["cy"] + (uv[1] * 0.68 - projection["centre_m"][1]) * projection["scale"],
    )


def render_board(episode, board, t):
    if t < -1e-6 or t > board["duration_s"] + 1e-6:
        raise EpisodeRejected("timeline", f"{board['id']} 的时间 {t} 超出 0–{board['duration_s']}。")
    font_info = D.resolve_font()
    image = _base(episode, board, font_info["path"]).copy()
    pen = ImageDraw.Draw(image)
    catalog = {node["id"]: list(node["uv"]) for node in board["nodes"]}
    catalog.update({key: list(value) for key, value in board["extras"].items()})
    positions = {node["id"]: list(node["uv"]) for node in board["nodes"]}
    motion_progress = {}
    for motion in board["motions"]:
        progress = D.pr(t, motion["t0"], motion["t1"])
        positions[motion["id"]] = list(D.mix(motion["frm"], motion["to"], progress))
        motion_progress[motion["id"]] = round(progress, 5)
        kind = motion["kind"]
        D.trace(
            pen,
            [project(board["projection"], motion["frm"]), project(board["projection"], motion["to"])],
            D.col(D.RUN if kind == "run" else D.DEF, 220 if kind == "run" else 155),
            2.8 if kind == "run" else 1.8,
            progress,
            (7, 5) if kind == "run" else (4, 6),
        )
    _annotations(pen, board, t, positions)
    route_progress = {}
    balls = []
    for route in board["routes"]:
        progress = D.pr(t, route["t0"], route["t1"])
        key = "-".join(route["ids"])
        route_progress[key] = round(progress, 5)
        if t + 1e-9 < route["t0"]:
            continue
        points = [project(board["projection"], catalog[identifier]) for identifier in route["ids"]]
        end = D.trace(pen, points, D.col(D.BALL, 245), 2.8, progress)
        balls.append((route["t0"], end))
    if board["legend_s"] and t < board["legend_s"]:
        fade_from = board["legend_fade_s"] or max(0.0, board["legend_s"] - 0.45)
        alpha = round(255 * (1 - D.pr(t, fade_from, board["legend_s"])))
        D.text(pen, (48, 593), "实线：球路    虚线：跑动", 18, D.MUT, a=alpha, font_path=font_info["path"])
    if balls:
        end = max(balls, key=lambda item: item[0])[1]
        if end:
            x, y = end
            pen.ellipse((*D.xy((x - 6, y - 6)), *D.xy((x + 6, y + 6))), fill=D.WHITE, outline=D.BALL, width=2)
    visible = []
    for node in board["nodes"]:
        fade = D.pr(t, node["appear_s"], node["appear_s"] + 0.22)
        if fade <= 0:
            continue
        if _player(pen, board["projection"], node, positions[node["id"]], t, fade, font_info["path"]):
            visible.append(node["id"])
    active = [label for label in board["labels"] if label["t0"] <= t < label["t1"]][-3:]
    for label in active:
        if t < _appear(board, label["id"]):
            continue
        _pill(pen, board, positions, label, t, font_info["path"])
    rgb = image.convert("RGB").resize((D.W, D.H), Image.Resampling.LANCZOS)
    state = {
        "episode_id": episode["episode_id"],
        "claim": episode["claim"],
        "stamp": episode["stamp"],
        "board": board["id"],
        "t": D.qtime(t),
        "question": board["question"],
        "native_size": [D.W, D.H],
        "fps": D.FPS,
        "supersample": D.SS,
        "upscaled": False,
        "audio": None,
        "font": font_info,
        "orientation": episode["orientation"],
        "ids": [node["id"] for node in board["nodes"]],
        "numbers": {node["id"]: node["number"] for node in board["nodes"]},
        "labels": [label["text"] for label in active],
        "visible_ids": visible,
        "motion_progress": motion_progress,
        "route_progress": route_progress,
    }
    if episode["claim"] != "regression_arsenal_2018":
        leaked = find_legacy(json.dumps(state, ensure_ascii=False))
        if leaked:
            raise EpisodeRejected("legacy_leak", "渲染结果里出现了旧场次身份：" + "、".join(leaked) + "。这帧不会写出。")
    return rgb, state


def _base(episode, board, font_path):
    key = (episode["episode_id"], board["id"], episode["stamp"], font_path)
    cached = _BASES.get(key)
    if cached is not None:
        return cached
    image = Image.new("RGBA", (D.W * D.SS, D.H * D.SS), D.BG + (255,))
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pen = ImageDraw.Draw(layer)
    D.pitch(pen, lambda uv: project(board["projection"], uv), D.PITCH, 1.2)
    image.alpha_composite(layer.crop((76, 178, 2070, 1238)), (76, 178))
    pen = ImageDraw.Draw(image)
    D.text(pen, (44, 27), board["question"], 27, D.WHITE, font_path=font_path)
    D.text(pen, (1080, 41), "← 进攻", 19, D.MUT, font_path=font_path)
    _minimap(image, board)
    stamp_color = D.ATT if episode["claim"] != "regression_arsenal_2018" else D.MUT
    D.text(pen, (44, 624), episode["stamp"], 16, stamp_color, font_path=font_path)
    _BASES[key] = image
    return image


def _minimap(image, board):
    mx, my, mw, mh = 1078, 94, 155, 100
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pen = ImageDraw.Draw(layer)

    def mp(uv):
        return (mx + uv[0] * mw / 100, my + uv[1] * mh / 100)

    D.pitch(pen, mp, D.MINI_PITCH, 0.75)
    projection = board["projection"]
    scale = projection["scale"]
    u0 = (projection["centre_m"][0] + (40 - projection["cx"]) / scale) / 1.05
    u1 = (projection["centre_m"][0] + (1035 - projection["cx"]) / scale) / 1.05
    v0 = (projection["centre_m"][1] + (89 - projection["cy"]) / scale) / 0.68
    v1 = (projection["centre_m"][1] + (619 - projection["cy"]) / scale) / 0.68
    aa = mp((max(0, u0), max(0, v0)))
    bb = mp((min(100, u1), min(100, v1)))
    if aa[0] < bb[0] and aa[1] < bb[1]:
        pen.rectangle((*D.xy(aa), *D.xy(bb)), outline=D.col(D.ATT, 150), width=2)
    left, top = mx * D.SS, my * D.SS
    right, bottom = (mx + mw) * D.SS, (my + mh) * D.SS
    image.alpha_composite(layer.crop((left, top, right, bottom)), (left, top))


def _annotations(pen, board, t, positions):
    for note in board["annotations"]:
        if note["type"] == "screen_channel" and t >= note["t0"]:
            anchor = project(board["projection"], positions[note["node"]])
            progress = D.pr(t, note["t0"], note["t1"])
            if progress <= 0:
                continue
            D.trace(
                pen,
                [(anchor[0] + note["dx0"], anchor[1]), (anchor[0] + note["dx1"], anchor[1])],
                D.col(D.ATT, 80),
                note["width"],
                progress,
                None,
                False,
            )
        elif note["type"] == "origin_ring" and t >= note["t0"]:
            center = project(board["projection"], board["extras"][note["point"]])
            circle = [
                (center[0] + note["radius"] * math.cos(angle), center[1] + note["radius"] * math.sin(angle))
                for angle in [index * math.tau / 80 for index in range(81)]
            ]
            D.trace(pen, circle, D.col(D.MUT, 140), 1.3, 1, (3, 5), False)
            D.text(pen, (center[0] + 64, center[1] - 58), note["label"], 18, D.MUT)
        elif note["type"] == "segment":
            D.trace(
                pen,
                [project(board["projection"], note["frm"]), project(board["projection"], note["to"])],
                D.col(D.RUN if note["kind"] == "run" else D.DEF, 220 if note["kind"] == "run" else 155),
                2.8 if note["kind"] == "run" else 1.8,
                D.pr(t, note["t0"], note["t1"]),
                (7, 5) if note["kind"] == "run" else (4, 6),
            )


def _player(pen, projection, node, uv, t, fade, font_path):
    x, y = project(projection, uv)
    radius = 22 if node["focus"] else 15
    if not (42 + radius < x < 1043 - radius and 90 + radius < y < 616 - radius):
        return False
    color = D.ATT if node["team"] == "attack" else D.DEF
    fill = (80, 93, 22) if node["team"] == "attack" else (104, 43, 39)
    opacity = (255 if node["focus"] else 125) * fade
    glow = (1 - D.pr(t, node["appear_s"] + 0.18, node["appear_s"] + 0.56)) * fade
    if node["focus"] and glow > 0:
        pen.ellipse(
            (*D.xy((x - radius - 8, y - radius - 8)), *D.xy((x + radius + 8, y + radius + 8))),
            outline=D.col(color, 68 * glow),
            width=4,
        )
    pen.ellipse(
        (*D.xy((x - radius, y - radius)), *D.xy((x + radius, y + radius))),
        fill=D.col(fill, opacity),
        outline=D.col(color, opacity),
        width=4 if node["focus"] else 2,
    )
    if node["number"]:
        D.text(pen, (x, y - 0.5), node["number"], 22 if node["focus"] else 17, D.WHITE, "mm", a=opacity, font_path=font_path)
    mx = 1078 + uv[0] * 155 / 100
    my = 94 + uv[1] * 100 / 100
    pen.ellipse((*D.xy((mx - 2.5, my - 2.5)), *D.xy((mx + 2.5, my + 2.5))), fill=D.col(color, opacity))
    return True


def _appear(board, identifier):
    for node in board["nodes"]:
        if node["id"] == identifier:
            return node["appear_s"]
    return 1e9


def _pill(pen, board, positions, label, t, font_path):
    fade = D.pr(t, label["t0"], label["t0"] + 0.24)
    anchor = project(board["projection"], positions[label["id"]])
    dest = (anchor[0] + label["offset"][0], anchor[1] + label["offset"][1])
    size = 23
    width = D.logical_text_width(pen, label["text"], size, font_path)
    x = max(46, min(dest[0], 1020 - width))
    y = max(107, min(580, dest[1]))
    alpha = round(255 * fade)
    pen.rounded_rectangle(
        (*D.xy((x - 8, y - 4)), *D.xy((x + width + 8, y + 31))),
        radius=8,
        fill=(9, 19, 24, round(alpha * 0.85)),
    )
    D.text(pen, (x, y), label["text"], size, D.WHITE, a=alpha, font_path=font_path)
    end_x = x if x > anchor[0] else x + width
    D.trace(pen, [anchor, (end_x, y + 13)], D.col(D.MUT, 100 * fade), 0.85, fade, None, False)
