"""2020-08-14 首球。坐标来自 720p 审阅代理上实际看过的帧。

1080p 接触图是同一时刻的缩图，母带不在这棵树里。俯视用同一机位的一个窗口，
是示意，不是测绘。巴萨 5 号按裁切 9.6 秒重标，不再用 (150, 720)。
"""

from __future__ import annotations

import json
from pathlib import Path

from .lock_map import CAMERAS, to_uv

ROOT = Path(__file__).resolve().parents[1]
EP_DIR = ROOT / "episodes" / "bayern-20200814-mueller-open-lock-draft"


def _pt(camera_name, x, y):
    uv = to_uv(x, y, CAMERAS[camera_name])
    if not (0 <= uv[0] <= 100 and 0 <= uv[1] <= 100):
        raise RuntimeError(f"{camera_name} {(x, y)} -> {uv} 超出 0–100")
    return uv


def _player(camera, identifier, team, number, lock, x, y, appear, focus=True):
    node = {
        "id": identifier,
        "number": None if number is None else str(number),
        "team": team,
        "uv": _pt(camera, x, y),
        "source_px": [x, y],
        "source_canvas": [1280, 720],
        "focus": focus,
        "appear_s": appear,
    }
    if number is not None:
        node["number_lock"] = lock
    return node


def build():
    high = "high_wide_attack_left"
    side = "sideline_attack_left"
    back = "behind_goal_attack_bottom"
    boards = [
        {
            "id": "R1",
            "segment": "replay_a",
            "question": "14号身前，边路还有空当吗？",
            "duration_s": 6.4,
            "legend_s": 0,
            "legend_fade_s": 0,
            "source_s": [72.0, 74.0],
            "clip_s": [22.0, 24.0],
            "camera": high,
            "open_visible": True,
            "label_px": 30,
            "nodes": [
                _player(high, "K14", "attack", 14, "clip_22", 520, 570, 0.0),
                _player(high, "Cmark", "defense", None, None, 510, 540, 0.45),
                _player(high, "Kkeep", "defense", None, None, 340, 310, 1.6),
                _player(high, "Kin", "attack", None, None, 560, 340, 3.4),
                _player(high, "Kin2", "attack", None, None, 700, 330, 3.8, False),
            ],
            "motions": [],
            "annotations": [
                {"type": "emphasis", "ids": ["K14"], "t0": 0.0, "t1": 6.4, "link": False},
                {"type": "emphasis", "ids": ["K14", "Cmark"], "t0": 1.6, "t1": 6.4, "link": True},
                {"type": "emphasis", "ids": ["Kin", "Kin2"], "t0": 3.4, "t1": 6.4, "link": True},
            ],
            "labels": [
                {"id": "K14", "text": "左边路持球", "t0": 0.7, "t1": 6.4, "offset": [36, 20]},
                {"id": "Cmark", "text": "身前有人", "t0": 1.8, "t1": 6.4, "offset": [-150, -28]},
                {"id": "Kin", "text": "禁区里已有人", "t0": 3.6, "t1": 6.4, "offset": [28, -36]},
            ],
            "layers": [
                {"t": 0.0, "name": "14号"},
                {"t": 1.7, "name": "门将"},
                {"t": 3.6, "name": "禁区里的人"},
                {"t": 5.6, "name": "层次收束"},
            ],
            "notes": "回放 A，裁切 22.0 秒，源 72 秒。只给 14 号编号。不是中圈开球。没有实测位移，不画跑动虚线，也不写跑动图例。标签留到这块板结束。",
        },
        {
            "id": "N2",
            "segment": "live",
            "question": "禁区这一脚，球是怎么出去的？",
            "duration_s": 10.4,
            "source_s": [59.0, 61.5],
            "clip_s": [9.0, 11.5],
            "camera": side,
            "open_visible": True,
            "nodes": [
                _player(side, "Kshot", "attack", None, None, 850, 445, 0.0),
                _player(side, "Ktall", "attack", None, None, 760, 370, 0.0),
                _player(side, "C20", "defense", 20, "clip_9p6", 690, 460, 7.2),
                _player(side, "C5", "defense", 5, "clip_9p6", 395, 490, 7.6),
                _player(side, "C3", "defense", 3, "clip_9p6", 255, 490, 8.0),
                _player(side, "C2", "defense", 2, "clip_9p6", 630, 630, 8.4),
                _player(side, "Kkeep", "defense", None, None, 155, 365, 1.2),
                _player(side, "Cjump", "defense", None, None, 490, 400, 2.3, False),
            ],
            "extra_points": [
                {"id": "ball_96", "uv": _pt(side, 810, 440)},
                {"id": "ball_102", "uv": _pt(side, 430, 375)},
            ],
            "routes": [{"ids": ["ball_96", "ball_102"], "t0": 3.84, "t1": 5.5, "intent": "forward"}],
            "annotations": [
                {"type": "zone", "ids": ["ball_96", "ball_102"], "t0": 5.8, "t1": 10.4, "width": 16},
            ],
            "labels": [
                {"id": "Kshot", "text": "回做点", "t0": 0.0, "t1": 10.4, "offset": [28, -42]},
                {"id": "Ktall", "text": "接应点", "t0": 0.0, "t1": 10.4, "offset": [24, 26]},
                {"id": "C5", "text": "5号在禁区左侧", "t0": 7.8, "t1": 10.4, "offset": [32, 18]},
            ],
            "layers": [
                {"t": 0.0, "name": "两名白衣"},
                {"t": 1.4, "name": "门将"},
                {"t": 4.6, "name": "球路生长"},
                {"t": 6.2, "name": "未封住的空当"},
                {"t": 7.6, "name": "周边号码"},
                {"t": 9.6, "name": "层次收束"},
            ],
            "notes": "实况裁切 9.6 秒，计时 3:02。5 号按这一帧重标，不用旧的 (150, 720)。两名白衣不标 9 或 25，标签留到和 20、5、3、2 号同框。空当色块沿着同一机位 9.6 到 10.2 的球路，不是跑位。18 号不在这镜。",
        },
        {
            "id": "R3",
            "segment": "replay_b",
            "question": "门后回放里，哪几个号码清楚？",
            "duration_s": 6.4,
            "source_s": [75.0, 77.5],
            "clip_s": [25.0, 27.5],
            "camera": back,
            "open_visible": True,
            "label_px": 30,
            "nodes": [
                _player(back, "K9", "attack", 9, "clip_25", 370, 380, 0.0),
                _player(back, "C21", "defense", 21, "clip_25", 450, 390, 0.7),
                _player(back, "K18", "attack", 18, "clip_25", 1235, 450, 3.2),
                _player(back, "Kkeep", "defense", None, None, 680, 620, 0.0),
                _player(back, "Kair", "attack", None, None, 500, 280, 4.6),
            ],
            "extra_points": [{"id": "ball_d", "uv": _pt(back, 510, 270)}],
            "annotations": [
                {"type": "emphasis", "ids": ["Kkeep"], "t0": 0.0, "t1": 6.4, "link": False},
                {"type": "emphasis", "ids": ["K9", "C21"], "t0": 1.7, "t1": 6.4, "link": True},
                {"type": "emphasis", "ids": ["K18"], "t0": 3.2, "t1": 6.4, "link": False},
                {"type": "emphasis", "ids": ["Kair"], "t0": 4.6, "t1": 6.4, "link": False},
            ],
            "labels": [
                {"id": "K9", "text": "回放确认9号", "t0": 0.4, "t1": 6.4, "offset": [-248, 42]},
                {"id": "C21", "text": "回放确认21号", "t0": 1.0, "t1": 3.3, "offset": [86, -64]},
                {"id": "K18", "text": "远端18未参与", "t0": 3.4, "t1": 6.4, "offset": [28, 24]},
                {"id": "Kair", "text": "射门点", "t0": 4.8, "t1": 6.4, "offset": [36, -40]},
            ],
            "layers": [
                {"t": 0.0, "name": "门将与9号"},
                {"t": 1.1, "name": "21号"},
                {"t": 3.4, "name": "远端18"},
                {"t": 4.8, "name": "射门点"},
                {"t": 5.6, "name": "层次收束"},
            ],
            "notes": "回放 B，裁切 25.0 秒。门后进攻朝画面下方，所有点同一公式转成攻左。18 号只在右缘远端，不画进回做，光环不连向禁区。门将背上的数字在 720p 代理里不够清楚，不标 1。不标 25。9号、远端18和射门点的字留到这块板结束。",
        },
    ]
    return {
        "episode_id": "bayern-20200814-mueller-open-lock-draft",
        "claim": "lock_draft",
        "geometry_verified": True,
        "pitch_calibration": "schematic_shared_window",
        "measurement": {
            "proxy": "1280x720 review copy of the 1080p cut",
            "proxy_scale_from_1080p": 0.6667,
            "contact_sheets": "1080p montages, same moments, not re-measured pixel by pixel",
            "uncertainty_px_on_proxy": 20,
        },
        "statement": "已对照 720p 证据帧。俯视是同一机位的示意，不是场地测绘。不是中圈开球接上的连续推进，也不是 84 秒成片。",
        "timing_basis": "board_local_seconds",
        "timing_note": "板上的秒数只排层次。能连续播放的画面只有三段，合计 8.8 秒。讲解稿的 84 秒要等配音，这里不凑。",
        "input_attack": "left",
        "coordinate_kind": "proxy_pixel_schematic",
        "forbidden_source_s": [[56, 58]],
        "segments": [
            {"id": "live", "kind": "live", "clip_s": [9.0, 12.0], "source_s": [59.0, 62.0], "duration_s": 3.0, "clock": "3:02-3:04"},
            {"id": "replay_a", "kind": "replay", "clip_s": [21.8, 24.6], "source_s": [71.8, 74.6], "duration_s": 2.8},
            {"id": "replay_b", "kind": "replay", "clip_s": [24.8, 27.8], "source_s": [74.8, 77.8], "duration_s": 3.0},
        ],
        "number_policy": {
            "14": ["clip_22"],
            "2": ["clip_9p6"],
            "3": ["clip_9p6"],
            "5": ["clip_9p6"],
            "20": ["clip_9p6"],
            "9": ["clip_25"],
            "18": ["clip_25"],
            "21": ["clip_25"],
            "25": [],
            "1": [],
        },
        "evidence_frames": [
            {"id": "clip_9p6", "path": "evidence/clip_9p6.jpg", "role": "实况 裁切9.6秒 计时3:02 720p代理", "native_size": [1280, 720]},
            {"id": "clip_10p2", "path": "evidence/clip_10p2.jpg", "role": "实况 裁切10.2秒 计时3:03 720p代理", "native_size": [1280, 720]},
            {"id": "clip_22", "path": "evidence/clip_22.jpg", "role": "回放A 裁切22.0秒 720p代理", "native_size": [1280, 720]},
            {"id": "clip_25", "path": "evidence/clip_25.jpg", "role": "回放B 裁切25.0秒 720p代理", "native_size": [1280, 720]},
        ],
        "boards": boards,
        "demo": {
            "mp4_boards": ["N2", "R1", "R3"],
            "side_by_side": [
                {"board": "N2", "t": 9.6, "evidence": "clip_9p6"},
                {"board": "R1", "t": 6.4, "evidence": "clip_22"},
                {"board": "R3", "t": 6.4, "evidence": "clip_25"},
            ],
        },
    }


def main():
    target = EP_DIR / "episode.json"
    target.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
