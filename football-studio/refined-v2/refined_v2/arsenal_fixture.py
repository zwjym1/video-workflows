"""把快照里的阿森纳关系几何收成回归场次包。

渲染器不导入这个模块。新场次缺数据时也不会走到这里。
板上的秒数是分层时钟，用来回归「对象 → 防守 → 球路」的顺序。
精修 v2 的新版字级旁白不在快照里，这里不假装那些词已经有了时点。
"""

from __future__ import annotations

import json
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "regression_data"
SNAPSHOT = Path(__file__).resolve().parents[2] / "snapshot-20261116"


def _pack_or_snapshot(pack_name, snapshot_rel):
    packaged = PACK / pack_name
    if packaged.is_file():
        return packaged
    return SNAPSHOT / snapshot_rel


RELATIONS = _pack_or_snapshot(
    "BOARD_RELATIONS.json",
    "football-demo/full-phase-production/assets/BOARD_RELATIONS.json",
)
EXECUTION = _pack_or_snapshot(
    "BOARD_RELATION_EXECUTION_MAP.json",
    "football-demo/two-reference-refinement/BOARD_RELATION_EXECUTION_MAP.json",
)

QUESTIONS = {
    "Q1": "过掉眼前这一人，下一脚怎么办？",
    "Q2": "中间这脚中转，多接上哪条路？",
    "Q3": "球在边上，里面的人为什么还要跑？",
    "Q4": "回传点前还有中卫，怎么续到身后？",
    "Q5": "门将来到这一侧，横传改变了什么？",
}


def build():
    relations = json.loads(RELATIONS.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    bases = {board["id"]: board for board in relations["boards"]}
    focus = {board["id"]: board["focus_ids"] for board in execution["boards"]}
    boards = [
        _q1(bases, focus),
        _q2(bases, focus),
        _q3(bases, focus),
        _q4(bases, focus),
        _q5(bases, focus),
    ]
    return {
        "episode_id": "arsenal-2018-regression",
        "claim": "regression_arsenal_2018",
        "statement": "这是 2018 阿森纳对莱斯特的关系板回归。几何来自已确认的关系数据和精修 v2 动作表。不是 2020-08-14 的任何回合。",
        "timing_basis": "board_local_seconds",
        "timing_note": "新版配音没有生成，快照里没有 Q 板的字级时钟。这里用板上的分层秒数回归出现顺序，不把旧旁白词时点冒充成新版。仓库里也没有这场的实拍帧，所以回归包不输出并排画面。",
        "input_attack": "left",
        "coordinate_kind": "hand_relation_uv",
        "evidence_frames": [],
        "boards": boards,
        "demo": {
            "mp4_boards": ["Q4"],
            "pairs": [
                {
                    "board": "Q4",
                    "before": 1.0,
                    "after": 4.4,
                    "before_name": "之前：球还没过原位",
                    "after_name": "之后：前插并完成回做",
                }
            ],
        },
    }


def _player(base, identifier, appear):
    source = next(node for node in base["nodes"] if node["id"] == identifier)
    team = "attack" if identifier.startswith("A") else "defense"
    number = "".join(ch for ch in identifier if ch.isdigit())
    return {
        "id": identifier,
        "number": number,
        "team": team,
        "uv": [source["uv"][0], source["uv"][1]],
        "focus": True,
        "appear_s": appear,
    }


def _q1(bases, focus):
    base = bases["B2"]
    _expect(focus, "Q1", ["A34", "L14", "A11", "L10"])
    return {
        "id": "Q1",
        "base_id": "B2",
        "question": QUESTIONS["Q1"],
        "duration_s": 5.2,
        "legend_s": 1.75,
        "legend_fade_s": 1.3,
        "nodes": [
            _player(base, "A34", 0.16),
            _player(base, "L14", 0.2),
            _player(base, "A11", 1.84),
            _player(base, "L10", 3.04),
        ],
        "motions": [
            {"id": "A34", "frm": [72, 94], "to": [66, 76], "t0": 0.28, "t1": 1.56, "kind": "run"},
            {"id": "L14", "frm": [65, 93], "to": [72, 85], "t0": 0.32, "t1": 1.56, "kind": "def"},
            {"id": "L10", "frm": [49, 66], "to": [53, 57], "t0": 3.04, "t1": 3.84, "kind": "def"},
        ],
        "routes": [{"ids": ["A34", "A11"], "t0": 2.16, "t1": 2.76, "intent": "forward"}],
        "labels": [
            {"id": "L14", "text": "由前侧，变到身后", "t0": 0.4, "t1": 2.0, "offset": [30, 20]},
            {"id": "A11", "text": "前内侧接点", "t0": 1.92, "t1": 5.2, "offset": [32, -60]},
            {"id": "L10", "text": "下一名防守者", "t0": 3.2, "t1": 5.2, "offset": [-218, -28]},
        ],
        "layers": [
            {"t": 0.2, "name": "对象"},
            {"t": 1.0, "name": "跑动与防守"},
            {"t": 2.4, "name": "球路"},
            {"t": 3.6, "name": "下一名"},
        ],
        "notes": "位移端点来自精修 render_v2 的 Q1。B2 节点坐标是收束位置。",
    }


def _q2(bases, focus):
    base = bases["B3"]
    _expect(focus, "Q2", ["A10", "A29", "A2", "L24"])
    return {
        "id": "Q2",
        "base_id": "B3",
        "question": QUESTIONS["Q2"],
        "duration_s": 5.0,
        "nodes": [
            _player(base, "A10", 0.16),
            _player(base, "A29", 0.56),
            _player(base, "A2", 1.4),
            _player(base, "L24", 0.56),
        ],
        "motions": [
            {"id": "L24", "frm": [49, 31], "to": [43, 25], "t0": 2.4, "t1": 3.16, "kind": "def"},
        ],
        "routes": [
            {"ids": ["A10", "A29"], "t0": 0.72, "t1": 1.24, "intent": "keep"},
            {"ids": ["A29", "A2"], "t0": 1.56, "t1": 2.2, "intent": "forward"},
        ],
        "labels": [
            {"id": "A10", "text": "中间接应", "t0": 0.16, "t1": 1.48, "offset": [40, 24]},
            {"id": "A29", "text": "一脚中转", "t0": 0.72, "t1": 5.0, "offset": [38, -30]},
            {"id": "A2", "text": "外侧继续推进", "t0": 1.56, "t1": 5.0, "offset": [-260, -45]},
        ],
        "layers": [
            {"t": 0.2, "name": "接点"},
            {"t": 1.0, "name": "中转"},
            {"t": 2.0, "name": "外侧"},
            {"t": 3.4, "name": "防守尾迹"},
        ],
        "notes": "L24 的终点是精修 v2 的 [43, 25]。旧 B3.defense 写的是 [43, 24]，回归跟的是精修动作表。",
    }


def _q3(bases, focus):
    base = bases["B4"]
    _expect(focus, "Q3", ["A2", "L24", "A17", "L3", "A10", "L25"])
    return {
        "id": "Q3",
        "base_id": "B4",
        "question": QUESTIONS["Q3"],
        "duration_s": 5.4,
        "nodes": [
            _player(base, "A2", 0.16),
            _player(base, "L24", 0.16),
            _player(base, "A17", 1.72),
            _player(base, "L3", 1.72),
            _player(base, "A10", 1.88),
            _player(base, "L25", 1.92),
        ],
        "motions": [
            {"id": "A2", "frm": [34, 8], "to": [23, 8], "t0": 0.28, "t1": 1.16, "kind": "run"},
            {"id": "A17", "frm": [30, 28], "to": [18, 28], "t0": 1.72, "t1": 2.72, "kind": "run"},
            {"id": "A10", "frm": [39, 54], "to": [25, 54], "t0": 1.92, "t1": 2.84, "kind": "run"},
            {"id": "L24", "frm": [42, 15], "to": [29, 15], "t0": 0.36, "t1": 1.2, "kind": "def"},
            {"id": "L3", "frm": [34, 29], "to": [24, 29], "t0": 2.0, "t1": 2.68, "kind": "def"},
            {"id": "L25", "frm": [45, 61], "to": [32, 61], "t0": 2.08, "t1": 2.76, "kind": "def"},
        ],
        "labels": [
            {"id": "A2", "text": "外侧推进", "t0": 0.16, "t1": 1.6, "offset": [38, -40]},
            {"id": "A17", "text": "内侧接点", "t0": 1.8, "t1": 5.4, "offset": [-188, -68]},
            {"id": "A10", "text": "下一脚仍可接", "t0": 2.0, "t1": 5.4, "offset": [58, -8]},
        ],
        "annotations": [
            {"type": "screen_channel", "node": "A2", "t0": 3.2, "t1": 3.64, "dx0": 52, "dx1": -45, "width": 13},
            {"type": "screen_channel", "node": "A10", "t0": 3.48, "t1": 3.92, "dx0": 52, "dx1": -45, "width": 13},
        ],
        "layers": [
            {"t": 0.2, "name": "外侧持球"},
            {"t": 1.4, "name": "内侧启动"},
            {"t": 2.6, "name": "跟进"},
            {"t": 3.8, "name": "接应通道"},
        ],
        "notes": "通道只表示可接应的位置，不是视野扇区。",
    }


def _q4(bases, focus):
    base = bases["B5"]
    _expect(focus, "Q4", ["A2", "A10", "L15", "A9"])
    if any(node["id"] == "L6" for node in base["nodes"]):
        raise RuntimeError("B5 若已经有 L6，回归脚本不该再声称缺少这个人。")
    origin = next(node["uv"] for node in base["nodes"] if node["id"] == "A10")
    nxt = base["extra_points"]["A10_next"]
    return {
        "id": "Q4",
        "base_id": "B5",
        "question": QUESTIONS["Q4"],
        "duration_s": 6.2,
        "nodes": [
            _player(base, "A2", 0.16),
            _player(base, "A10", 0.16),
            _player(base, "L15", 0.16),
            _player(base, "A9", 0.36),
        ],
        "extra_points": [
            {"id": "A10_origin", "uv": [origin[0], origin[1]]},
            {"id": "A10_next", "uv": [nxt[0], nxt[1]]},
        ],
        "motions": [
            {"id": "A10", "frm": [origin[0], origin[1]], "to": [nxt[0], nxt[1]], "t0": 2.2, "t1": 3.12, "kind": "run"},
            {"id": "L15", "frm": [18, 56], "to": [15, 45], "t0": 2.36, "t1": 3.16, "kind": "def"},
        ],
        "routes": [
            {"ids": ["A2", "A10_origin", "A9"], "t0": 1.2, "t1": 2.08, "intent": "forward"},
            {"ids": ["A9", "A10_next"], "t0": 3.28, "t1": 3.96, "intent": "forward"},
        ],
        "labels": [
            {"id": "L15", "text": "身前的中卫", "t0": 0.2, "t1": 1.8, "offset": [-220, -22]},
            {"id": "A9", "text": "接下，立即回做", "t0": 0.4, "t1": 6.2, "offset": [48, 0]},
            {"id": "A10", "text": "新的接球点", "t0": 2.52, "t1": 6.2, "offset": [40, -66]},
        ],
        "annotations": [
            {"type": "origin_ring", "point": "A10_origin", "t0": 2.16, "label": "原位"},
        ],
        "order_rules": [
            {"type": "route_clears_point_before_motion", "route": 0, "point": "A10_origin", "motion": "A10"},
        ],
        "layers": [
            {"t": 0.2, "name": "身前"},
            {"t": 1.6, "name": "球穿原位"},
            {"t": 2.8, "name": "前插"},
            {"t": 3.8, "name": "回做"},
        ],
        "notes": "执行映射把 L6 列在「若在画面中则保留」。B5 没有 L6 的坐标，精修源码那一行会直接报错。回归板不补这个人。",
    }


def _q5(bases, focus):
    base = bases["B6"]
    _expect(focus, "Q5", ["A10", "L1", "A14", "L14"])
    return {
        "id": "Q5",
        "base_id": "B6",
        "question": QUESTIONS["Q5"],
        "duration_s": 4.8,
        "nodes": [
            _player(base, "A10", 0.16),
            _player(base, "L1", 0.16),
            _player(base, "A14", 0.72),
            _player(base, "L14", 1.16),
        ],
        "motions": [
            {"id": "L14", "frm": [10, 73], "to": [8, 68], "t0": 1.16, "t1": 1.92, "kind": "def"},
        ],
        "routes": [{"ids": ["A10", "A14"], "t0": 2.08, "t1": 2.68, "intent": "forward"}],
        "labels": [
            {"id": "L1", "text": "门将已向球侧出来", "t0": 0.16, "t1": 2.0, "offset": [-280, -52]},
            {"id": "A14", "text": "另一侧的终结点", "t0": 0.76, "t1": 4.8, "offset": [-290, 6]},
            {"id": "L14", "text": "回追仍在身后", "t0": 1.2, "t1": 4.8, "offset": [38, 8]},
        ],
        "annotations": [
            {"type": "segment", "frm": [1.5, 50], "to": [5, 45], "t0": 0.16, "t1": 0.56, "kind": "def"},
        ],
        "layers": [
            {"t": 0.2, "name": "门将"},
            {"t": 1.0, "name": "另一侧"},
            {"t": 1.72, "name": "回追"},
            {"t": 2.48, "name": "横传"},
        ],
        "notes": "L14 的短尾用精修 v2 的 [10, 73] 到 [8, 68]。门将那一段是同一份源码里的 (1.5, 50) 到 (5, 45)。",
    }


def _expect(focus, board_id, ids):
    if set(focus[board_id]) != set(ids):
        raise RuntimeError(f"{board_id} 焦点与执行映射不一致：{focus[board_id]}")


def main():
    target = Path(__file__).resolve().parents[1] / "episodes" / "arsenal-2018-regression" / "episode.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
