"""2020-08-14 拜仁对巴萨首球的锁帧草稿。

像素来自 FRAME_LOCK_HD.json。uv 由 lock_map 的同一公式算出。
本环境没有源帧，geometry_verified 必须是 false。
"""

from __future__ import annotations

import json
from pathlib import Path

from .lock_map import CAMERAS, to_uv

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "episodes" / "bayern-20200814-mueller-open-lock-draft" / "FRAME_LOCK_HD.json"


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
            "question": "14号身前，边路还有空当吗？",
            "duration_s": 4.4,
            "legend_s": 1.75,
            "legend_fade_s": 1.3,
            "source_s": [72, 74],
            "camera": high,
            "nodes": [
                _player(high, "K14", "attack", 14, "B1_flank_t072", 790, 835, 0.16),
                _player(high, "Cnear", "defense", None, None, 770, 720, 0.28),
                _player(high, "Kbox", "attack", None, None, 1100, 690, 0.84),
                _player(high, "Cbox", "defense", None, None, 1080, 600, 0.92),
                _player(high, "Kcen", "attack", None, None, 880, 430, 1.04),
                _player(high, "Ccen", "defense", None, None, 830, 410, 1.08),
                _player(high, "Kpost", "attack", None, None, 1010, 400, 1.16),
                _player(high, "Cpost", "defense", None, None, 980, 380, 1.2),
                _player(high, "Cd", "defense", None, None, 1190, 370, 1.24, False),
                _player(high, "Kkeep", "defense", None, None, 530, 430, 0.36),
            ],
            "extra_points": [{"id": "R1ahead", "uv": _pt(high, 790, 780)}],
            "motions": [
                {
                    "id": "K14",
                    "frm": _pt(high, 790, 835),
                    "to": _pt(high, 790, 780),
                    "t0": 0.48,
                    "t1": 1.2,
                    "kind": "run",
                }
            ],
            "labels": [
                {"id": "K14", "text": "左边路持球", "t0": 0.2, "t1": 1.6, "offset": [36, 24]},
                {"id": "Cnear", "text": "身前有人", "t0": 0.4, "t1": 1.8, "offset": [-150, -36]},
                {"id": "Kbox", "text": "禁区里已有人", "t0": 1.0, "t1": 4.4, "offset": [28, -40]},
            ],
            "layers": [
                {"t": 0.24, "name": "14与身前"},
                {"t": 1.0, "name": "向禁区带"},
                {"t": 1.8, "name": "禁区里的人"},
                {"t": 3.4, "name": "停在边路"},
            ],
            "notes": "回放 A，源 72–74 秒。只给 14 号编号。远处两名在锁帧里，但不放进主关系，避免把边路缩成全场。没有从中圈画传球。",
        },
        {
            "id": "N2",
            "question": "禁区这一脚，球是怎么出去的？",
            "duration_s": 5.2,
            "source_s": [59.0, 61.5],
            "camera": side,
            "nodes": [
                _player(side, "Kshot", "attack", None, None, 1310, 520, 0.16),
                _player(side, "Ktall", "attack", None, None, 1105, 490, 0.28),
                _player(side, "Ctall", "defense", None, None, 1040, 480, 0.72),
                _player(side, "Cshot", "defense", None, None, 1365, 490, 0.76),
                _player(side, "C20", "defense", 20, "B2_box_live_t059", 1045, 640, 0.84),
                _player(side, "C5", "defense", 5, "B2_box_live_t059", 150, 720, 0.92),
                _player(side, "C2", "defense", 2, "B2_box_live_t059", 990, 940, 1.0),
                _player(side, "C3", "defense", 3, "B2_box_live_t059", 300, 660, 1.04),
                _player(side, "Kkeep", "defense", None, None, 215, 480, 0.4),
                _player(side, "Kleft", "attack", None, None, 120, 620, 1.12, False),
            ],
            "extra_points": [
                {"id": "ball_a", "uv": _pt(side, 1145, 553)},
                {"id": "ball_b", "uv": _pt(side, 845, 637)},
                {"id": "ball_c", "uv": _pt(side, 583, 558)},
            ],
            "routes": [
                {"ids": ["ball_a", "ball_b", "ball_c"], "t0": 1.6, "t1": 2.8, "intent": "forward"}
            ],
            "labels": [
                {"id": "Kshot", "text": "出球人无号码", "t0": 0.2, "t1": 1.84, "offset": [24, -44]},
                {"id": "Ktall", "text": "另一白衣无号码", "t0": 0.36, "t1": 2.0, "offset": [20, 28]},
                {"id": "Kkeep", "text": "门将在球门侧", "t0": 0.84, "t1": 5.2, "offset": [28, -36]},
            ],
            "layers": [
                {"t": 0.28, "name": "两名白衣"},
                {"t": 1.2, "name": "附近防守"},
                {"t": 2.2, "name": "球向球门"},
                {"t": 3.6, "name": "球已离地"},
            ],
            "notes": "实况 59.0–61.5 秒，计时牌 3:02–3:04，同一机位。白衣不标 9，也不标 25。3 号在 59.6 秒更清楚，这里仍用 59.0 的像素。不接 56–58 秒的中圈开球。",
        },
        {
            "id": "R3",
            "question": "门后回放里，哪几个号码清楚？",
            "duration_s": 4.8,
            "source_s": [75.0, 77.5],
            "camera": back,
            "nodes": [
                _player(back, "K9", "attack", 9, "B3_behind_goal_t075_t077", 540, 560, 0.28),
                _player(back, "C21", "defense", 21, "B3_behind_goal_t075_t077", 680, 550, 0.4),
                _player(back, "K18", "attack", 18, "B3_behind_goal_t075_t077", 1900, 650, 0.56),
                _player(back, "Kkeep", "defense", None, None, 1100, 850, 0.2),
                _player(back, "Kair", "attack", None, None, 750, 400, 0.72),
                _player(back, "Cair", "defense", None, None, 750, 430, 0.8),
            ],
            "extra_points": [
                {"id": "ball_d", "uv": _pt(back, 750, 370)},
                {"id": "ball_e", "uv": _pt(back, 960, 580)},
            ],
            "routes": [{"ids": ["ball_d", "ball_e"], "t0": 1.4, "t1": 2.2, "intent": "forward"}],
            "labels": [
                {"id": "K9", "text": "回放确认9号", "t0": 0.32, "t1": 4.8, "offset": [-170, 8]},
                {"id": "C21", "text": "回放确认21号", "t0": 0.48, "t1": 1.16, "offset": [-40, -48]},
                {"id": "K18", "text": "回放确认18号", "t0": 0.64, "t1": 1.16, "offset": [36, 28]},
                {"id": "Kair", "text": "起脚人无号码", "t0": 1.28, "t1": 4.8, "offset": [48, -56]},
            ],
            "layers": [
                {"t": 0.24, "name": "门将"},
                {"t": 0.7, "name": "回放号码"},
                {"t": 1.7, "name": "球朝门"},
                {"t": 3.2, "name": "起脚人仍无号"},
            ],
            "notes": "门后机位，源 75–77.5 秒。进攻朝画面下方，所有点先逆时针转再翻成攻左。9、18、21 只在这一镜编号。起脚人这帧没有清楚号码，不标 25。",
        },
    ]
    return {
        "episode_id": "bayern-20200814-mueller-open-lock-draft",
        "claim": "lock_draft",
        "geometry_verified": False,
        "statement": "这是 2020-08-14 拜仁对巴萨首球的锁帧草稿，几何未核验。本环境没有源帧，不是已经核对过的关系板，也不是中圈开球接上射门的连续推进。",
        "timing_basis": "board_local_seconds",
        "timing_note": "分层秒数只用来把对象、防守和球路分开，不是字级旁白。源 56–58 秒是中圈开球，禁止和 59 秒之后的禁区剪成一段。",
        "input_attack": "left",
        "coordinate_kind": "lock_pixel_relative_not_calibrated",
        "forbidden_source_s": [[56, 58]],
        "number_policy": {
            "14": ["B1_flank_t072", "B1b_flank_t073"],
            "2": ["B2_box_live_t059"],
            "3": ["B2_box_live_t059"],
            "5": ["B2_box_live_t059", "B1b_flank_t073"],
            "20": ["B2_box_live_t059"],
            "9": ["B3_behind_goal_t075_t077"],
            "18": ["B3_behind_goal_t075_t077"],
            "21": ["B3_behind_goal_t075_t077"],
            "25": [],
        },
        "evidence_frames": [],
        "boards": boards,
        "demo": {"mp4_boards": ["N2", "R1"]},
    }


def main():
    target = LOCK.parent / "episode.json"
    target.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
