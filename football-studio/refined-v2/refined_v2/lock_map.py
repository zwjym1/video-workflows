"""把锁帧像素收成攻左 uv。

同一机位的所有点共用一个公式。门后机位先按画面坐标逆时针转 90 度
（底边到右侧），再把朝右的轴翻成攻左。没有源帧时，这只是像素相对位置，
不是 18 码区校准，也不能叫核验通过。
"""

from __future__ import annotations

# Windows are in the 1280×720 review proxy. 1080p contact sheets use the same moments at 1.5×.
CAMERAS = {
    "high_wide_attack_left": {
        "kind": "attack_left",
        "width": 1280,
        "window": {"x0": 250, "x1": 900, "y0": 250, "y1": 650, "u0": 4, "u1": 72, "v0": 8, "v1": 88},
    },
    "sideline_attack_left": {
        "kind": "attack_left",
        "width": 1280,
        "window": {"x0": 80, "x1": 1000, "y0": 280, "y1": 700, "u0": 4, "u1": 72, "v0": 8, "v1": 90},
    },
    "behind_goal_attack_bottom": {
        "kind": "attack_bottom",
        "width": 1280,
        "window": {"x0": 600, "x1": 1100, "y0": 0, "y1": 1000, "u0": 6, "u1": 68, "v0": 6, "v1": 90},
    },
}


def attack_left_pixel(x, y, camera):
    kind = camera["kind"]
    width = camera["width"]
    if kind == "attack_left":
        return float(x), float(y)
    if kind == "attack_bottom":
        return (width - 1) - float(y), (width - 1) - float(x)
    raise ValueError(kind)


def to_uv(x, y, camera):
    px, py = attack_left_pixel(x, y, camera)
    window = camera["window"]
    u = (px - window["x0"]) / (window["x1"] - window["x0"]) * (window["u1"] - window["u0"]) + window["u0"]
    v = (py - window["y0"]) / (window["y1"] - window["y0"]) * (window["v1"] - window["v0"]) + window["v0"]
    return [round(u, 2), round(v, 2)]
