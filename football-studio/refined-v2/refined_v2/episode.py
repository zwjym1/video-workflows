"""场次包校验。

渲染器只接受已经通过这里的结构。缺字段、旧队员泄漏、坐标出界、
箭头退化、攻向不一致、证据指针缺失，都在这里拒绝，不会回退到阿森纳几何。
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from .draw import ease_inv, qtime
from .errors import EpisodeRejected
from .legacy import find_legacy, regression_id_allowed

CLAIMS = {
    "regression_arsenal_2018": "回归 · 2018阿森纳关系板 · 非新场次",
    "sample_not_a_match": "样例 · 非比赛几何 · 不是2020-08-14穆勒回合",
    "evidence_locked": "证据稿 · 坐标未逐帧核完前不得当作最终真实板",
    "lock_draft": "锁帧草稿 · 未见源帧 · 几何未核验",
}
UV_KEYS = {"uv", "frm", "to"}
TIME_KEYS = {"appear_s", "t0", "t1", "t"}


def load_episode(path) -> dict:
    file_path = Path(path)
    if file_path.is_dir():
        file_path = file_path / "episode.json"
    if not file_path.is_file():
        raise EpisodeRejected(
            "missing_episode",
            f"没有场次包 {file_path}。拒绝渲染，不会改用 2018 阿森纳关系板。",
        )
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EpisodeRejected("missing_episode", f"场次包不是合法 JSON：{exc}") from exc
    compiled = compile_episode(data, base_dir=file_path.parent)
    compiled["source_path"] = str(file_path)
    return compiled


def compile_episode(data, base_dir=None) -> dict:
    if not isinstance(data, dict):
        raise EpisodeRejected("missing_episode", "场次包必须是一个 JSON 对象。")
    claim = data.get("claim")
    if claim not in CLAIMS:
        raise EpisodeRejected(
            "claim",
            "claim 只能是 regression_arsenal_2018、sample_not_a_match、evidence_locked 或 lock_draft。"
            "不接受把未核实回合标成真实板。",
        )
    episode_id = data.get("episode_id")
    if not isinstance(episode_id, str) or not episode_id:
        raise EpisodeRejected("claim", "缺少 episode_id。")
    if claim == "regression_arsenal_2018" and episode_id != "arsenal-2018-regression":
        raise EpisodeRejected("claim", "回归包的 episode_id 固定为 arsenal-2018-regression，不能改名当新场次。")
    if claim == "sample_not_a_match" and episode_id != "sample-not-a-match":
        raise EpisodeRejected("claim", "样例包的 episode_id 固定为 sample-not-a-match，不能改名当真实回合。")
    statement = data.get("statement")
    if not isinstance(statement, str) or not statement.strip():
        raise EpisodeRejected("claim", "缺少 statement。场次必须写明自己是回归、样例还是证据稿。")
    if claim == "regression_arsenal_2018" and "回归" not in statement:
        raise EpisodeRejected("claim", "回归包的 statement 必须写明「回归」。")
    if claim == "sample_not_a_match" and ("样例" not in statement or "不是" not in statement):
        raise EpisodeRejected("claim", "样例包的 statement 必须同时包含「样例」和「不是」。")
    if claim == "evidence_locked" and "证据" not in statement:
        raise EpisodeRejected("claim", "证据稿的 statement 必须写明「证据」。")
    if claim == "lock_draft":
        if "未核验" not in statement or "不是" not in statement:
            raise EpisodeRejected("claim", "锁帧草稿的 statement 必须写明「未核验」和「不是」。")
        if data.get("geometry_verified") is not False:
            raise EpisodeRejected("evidence", "没有源帧时不能把 geometry_verified 标成通过。缺帧就拒绝核验。")
    elif data.get("geometry_verified") is True and claim != "evidence_locked":
        raise EpisodeRejected("evidence", "只有证据稿能声明几何已核验，而且帧文件必须在。")
    attack = data.get("input_attack")
    if attack not in ("left", "right"):
        raise EpisodeRejected("orientation", "input_attack 只能是 left 或 right。攻向不明时拒绝渲染。")
    basis = data.get("timing_basis")
    if basis not in ("board_local_seconds", "word_clock"):
        raise EpisodeRejected("timeline", "timing_basis 只能是 board_local_seconds 或 word_clock。")
    if claim != "regression_arsenal_2018":
        leaked = find_legacy(json.dumps(data, ensure_ascii=False))
        if leaked:
            raise EpisodeRejected(
                "legacy_leak",
                "这个场次包里出现了 2018 阿森纳/莱斯特身份："
                + "、".join(leaked)
                + "。拒绝渲染，不会把旧队员或旧旁白画进新板。",
            )
    clock = _clock(data, basis)
    raw_boards = data.get("boards")
    if not isinstance(raw_boards, list) or not raw_boards:
        raise EpisodeRejected("geometry", "boards 不能为空。空板不会用旧场次填上。")
    working = json.loads(json.dumps(data))
    flipped_paths = []
    if attack == "right":
        _flip_uvs(working, "$", flipped_paths)
        if not flipped_paths:
            raise EpisodeRejected("orientation", "声明了攻右，但没有任何可翻转的坐标。")
    evidence = _evidence_index(working, base_dir, claim)
    boards = []
    seen = set()
    for index, board in enumerate(working["boards"]):
        compiled = _compile_board(board, index, basis, clock, claim, evidence, data.get("number_policy") or {})
        if compiled["id"] in seen:
            raise EpisodeRejected("geometry", f"板号重复：{compiled['id']}")
        seen.add(compiled["id"])
        boards.append(compiled)
    _continuity(data, boards)
    return {
        "episode_id": episode_id,
        "claim": claim,
        "stamp": CLAIMS[claim],
        "statement": statement,
        "timing_basis": basis,
        "timing_note": working.get("timing_note") or "",
        "native_size": [1280, 720],
        "fps": 25,
        "supersample": 2,
        "upscaled": False,
        "audio": None,
        "geometry_verified": data.get("geometry_verified") is True,
        "orientation": {
            "input_attack": attack,
            "rendered_attack": "left",
            "transform": "identity" if attack == "left" else "u' = 100 - u",
            "paths": flipped_paths,
            "consistent": True,
        },
        "evidence_frames": evidence,
        "boards": boards,
        "demo": working.get("demo") or {},
    }


def _clock(data, basis):
    if basis == "board_local_seconds":
        return {}
    clock = data.get("clock")
    if not isinstance(clock, dict) or not isinstance(clock.get("scenes"), dict) or not clock["scenes"]:
        raise EpisodeRejected("word_clock", "word_clock 需要 clock.scenes。没有字级时间轴就拒绝，不会沿用旧旁白。")
    scenes = {}
    for key, scene in clock["scenes"].items():
        if not isinstance(scene, dict):
            raise EpisodeRejected("word_clock", f"场景 {key} 不是对象。")
        if "output_start_s" not in scene or "words" not in scene:
            raise EpisodeRejected("word_clock", f"场景 {key} 缺少 output_start_s 或 words。")
        words = scene["words"]
        if not isinstance(words, list) or not words:
            raise EpisodeRejected("word_clock", f"场景 {key} 没有词。")
        for word in words:
            if not isinstance(word, dict) or "text" not in word:
                raise EpisodeRejected("word_clock", f"场景 {key} 的词条不完整。")
            _number(word.get("offset"), f"{key}.offset")
            _number(word.get("duration"), f"{key}.duration")
            if word["duration"] <= 0:
                raise EpisodeRejected("word_clock", f"场景 {key} 有非正词长。")
        scenes[key] = scene
    return scenes


def _evidence_index(data, base_dir, claim):
    frames = {}
    for item in data.get("evidence_frames") or []:
        if not isinstance(item, dict) or "id" not in item or "path" not in item:
            raise EpisodeRejected("evidence", "evidence_frames 每一条都要有 id 和 path。")
        if item["id"] in frames:
            raise EpisodeRejected("evidence", f"证据帧 id 重复：{item['id']}")
        path = Path(item["path"])
        if not path.is_absolute():
            if base_dir is None:
                raise EpisodeRejected("evidence", f"证据帧 {item['id']} 是相对路径，但没有场次目录。")
            path = Path(base_dir) / path
        if not path.is_file():
            raise EpisodeRejected("evidence", f"证据帧文件不存在：{path}。不会用别的画面顶上。")
        native = item.get("native_size")
        from PIL import Image

        with Image.open(path) as image:
            actual = [image.width, image.height]
        if native is not None and list(native) != actual:
            raise EpisodeRejected(
                "evidence",
                f"证据帧 {item['id']} 声明尺寸 {native}，文件实际 {actual}。拒绝渲染，不会把尺寸差异藏起来。",
            )
        frames[item["id"]] = {
            "id": item["id"],
            "path": str(path),
            "native_size": actual,
            "role": item.get("role") or "",
        }
    if claim == "evidence_locked" and not frames:
        raise EpisodeRejected("evidence", "证据稿没有任何证据帧。拒绝渲染。")
    return frames


def _overlaps(a0, a1, b0, b1):
    return float(a0) < float(b1) and float(b0) < float(a1)


def _continuity(data, boards):
    for ban in data.get("forbidden_source_s") or []:
        if not isinstance(ban, list) or len(ban) != 2:
            raise EpisodeRejected("continuity", "forbidden_source_s 必须是 [起, 止] 列表。")
        for board in boards:
            span = board.get("source_s")
            if span and _overlaps(span[0], span[1], ban[0], ban[1]):
                raise EpisodeRejected(
                    "continuity",
                    f"{board['id']} 的源时间 {span} 落在禁止拼接的 {ban}。中圈开球不能和禁区射门接成连续推进。",
                )
    if data.get("claim") == "lock_draft":
        for board in boards:
            span = board.get("source_s")
            if not isinstance(span, list) or len(span) != 2:
                raise EpisodeRejected("continuity", f"{board['id']} 缺少 source_s，锁帧草稿不能省掉镜头时间。")


def _compile_board(board, index, basis, clock, claim, evidence, number_policy):
    if not isinstance(board, dict):
        raise EpisodeRejected("geometry", f"第 {index} 块板不是对象。")
    board_id = board.get("id")
    question = board.get("question")
    if not isinstance(board_id, str) or not board_id:
        raise EpisodeRejected("geometry", "板缺少 id。")
    if not isinstance(question, str) or not question.strip():
        raise EpisodeRejected("geometry", f"{board_id} 缺少问句。")
    if len(question) > 24:
        raise EpisodeRejected("geometry", f"{board_id} 问句超过 24 字，一块板只放一个短问题。")
    duration = qtime(_number(board.get("duration_s"), f"{board_id}.duration_s"))
    if duration <= 0:
        raise EpisodeRejected("timeline", f"{board_id} 时长必须大于 0。")
    scene_name = board.get("scene")
    output_start = board.get("output_start_s")
    if basis == "word_clock":
        if scene_name not in clock:
            raise EpisodeRejected("word_clock", f"{board_id} 的 scene 不在字级时钟里。")
        if output_start is None:
            raise EpisodeRejected("word_clock", f"{board_id} 缺少 output_start_s，词级时间无法折成板上时间。")
        output_start = float(output_start)
    nodes = []
    for node in board.get("nodes") or []:
        nodes.append(_node(node, board_id, basis, clock, scene_name, output_start, duration, claim, evidence, number_policy))
    if sum(1 for node in nodes if node["focus"]) < 2:
        raise EpisodeRejected("geometry", f"{board_id} 至少要有两个焦点球员。")
    ids = [node["id"] for node in nodes]
    if len(ids) != len(set(ids)):
        raise EpisodeRejected("geometry", f"{board_id} 有重复球员 id。")
    extras = {}
    for extra in board.get("extra_points") or []:
        if not isinstance(extra, dict) or "id" not in extra:
            raise EpisodeRejected("geometry", f"{board_id} 的附加点不完整。")
        _uv(extra.get("uv"), f"{board_id}.{extra['id']}")
        if extra["id"] in ids or extra["id"] in extras:
            raise EpisodeRejected("geometry", f"{board_id} 附加点 {extra['id']} 与已有 id 冲突。")
        if claim == "regression_arsenal_2018" and not regression_id_allowed(extra["id"]):
            raise EpisodeRejected("legacy_leak", f"回归板出现了名册以外的点 {extra['id']}。")
        _require_evidence(extra, claim, evidence, f"{board_id}.{extra['id']}")
        extras[extra["id"]] = [float(extra["uv"][0]), float(extra["uv"][1])]
    catalog = {node["id"]: node["uv"] for node in nodes}
    catalog.update(extras)
    motions = [
        _motion(item, board_id, basis, clock, scene_name, output_start, duration, ids, claim, evidence)
        for item in board.get("motions") or []
    ]
    routes = [
        _route(item, board_id, basis, clock, scene_name, output_start, duration, catalog)
        for item in board.get("routes") or []
    ]
    labels = [
        _label(item, board_id, basis, clock, scene_name, output_start, duration, ids)
        for item in board.get("labels") or []
    ]
    _label_overlap(labels, duration, board_id)
    annotations = [
        _annotation(item, board_id, basis, clock, scene_name, output_start, duration, catalog, claim, evidence)
        for item in board.get("annotations") or []
    ]
    rules = list(board.get("order_rules") or [])
    _order_rules(rules, routes, motions, catalog, board_id)
    layers = _layers(board.get("layers") or [], duration, board_id, basis, clock, scene_name, output_start)
    stills = _stills(board.get("still_marks") or [], board_id)
    if claim == "regression_arsenal_2018":
        for node in nodes:
            if not regression_id_allowed(node["id"]):
                raise EpisodeRejected("legacy_leak", f"回归板出现了名册以外的 id {node['id']}。")
    projection = _projection(nodes, motions, extras)
    return {
        "id": board_id,
        "base_id": board.get("base_id"),
        "question": question,
        "duration_s": duration,
        "legend_s": float(board.get("legend_s") or 0),
        "legend_fade_s": float(board.get("legend_fade_s") or 0),
        "nodes": nodes,
        "extras": extras,
        "motions": motions,
        "routes": routes,
        "labels": labels,
        "annotations": annotations,
        "layers": layers,
        "still_marks": stills,
        "notes": board.get("notes") or "",
        "source_s": board.get("source_s"),
        "projection": projection,
    }


def _node(node, board_id, basis, clock, scene_name, output_start, duration, claim, evidence, number_policy):
    if not isinstance(node, dict):
        raise EpisodeRejected("geometry", f"{board_id} 的球员不是对象。")
    identifier = node.get("id")
    number = node.get("number")
    team = node.get("team")
    if not isinstance(identifier, str) or not identifier:
        raise EpisodeRejected("geometry", f"{board_id} 有球员缺少 id。")
    if team not in ("attack", "defense"):
        raise EpisodeRejected("geometry", f"{identifier} 的 team 只能是 attack 或 defense。")
    if number is None:
        if claim != "lock_draft":
            raise EpisodeRejected("identity", f"{identifier} 缺少号码。没有回放确认时不能留空，也不能猜一个号。")
        number_out = None
    else:
        if not isinstance(number, str) or not number.isdigit() or not 1 <= int(number) <= 99:
            raise EpisodeRejected("geometry", f"{identifier} 的号码必须是 1–99 的字符串，不能从旧 id 里切。")
        if claim == "lock_draft":
            allowed = number_policy.get(str(int(number)))
            lock = node.get("number_lock")
            if not isinstance(allowed, list) or lock not in allowed:
                raise EpisodeRejected(
                    "identity",
                    f"{identifier} 的 {int(number)} 号没有落在允许的回放/实况锁帧 {allowed} 上。"
                    "未知白衣不能标成 9 或 25。",
                )
        number_out = str(int(number))
    uv = _uv(node.get("uv"), identifier)
    appear = _time(node.get("appear_s"), f"{identifier}.appear_s", basis, clock, scene_name, output_start)
    if appear < -1e-9 or appear > duration + 1e-9:
        raise EpisodeRejected("timeline", f"{identifier} 的出现时间 {appear} 不在 0–{duration}。")
    if claim == "evidence_locked" and node.get("focus", True):
        _require_evidence(node, claim, evidence, identifier)
    elif claim == "evidence_locked":
        _require_evidence(node, claim, evidence, identifier)
    return {
        "id": identifier,
        "number": number_out,
        "team": team,
        "uv": uv,
        "focus": bool(node.get("focus", True)),
        "appear_s": appear,
        "evidence_id": node.get("evidence_id"),
    }


def _motion(item, board_id, basis, clock, scene_name, output_start, duration, ids, claim, evidence):
    if not isinstance(item, dict):
        raise EpisodeRejected("timeline", f"{board_id} 的运动不是对象。")
    identifier = item.get("id")
    if identifier not in ids:
        raise EpisodeRejected("arrow", f"{board_id} 的运动指向不存在的球员 {identifier}。")
    if item.get("kind") not in ("run", "def"):
        raise EpisodeRejected("arrow", f"{identifier} 的运动 kind 只能是 run 或 def。")
    frm = _uv(item.get("frm"), f"{identifier}.frm")
    to = _uv(item.get("to"), f"{identifier}.to")
    _separated(frm, to, f"{board_id}.{identifier}")
    t0 = _time(item.get("t0"), f"{identifier}.t0", basis, clock, scene_name, output_start)
    t1 = _time(item.get("t1"), f"{identifier}.t1", basis, clock, scene_name, output_start)
    _span(t0, t1, duration, f"{board_id}.{identifier}")
    if claim == "evidence_locked":
        _require_evidence(item, claim, evidence, f"{board_id}.{identifier}.motion")
    return {"id": identifier, "frm": frm, "to": to, "t0": t0, "t1": t1, "kind": item["kind"]}


def _route(item, board_id, basis, clock, scene_name, output_start, duration, catalog):
    if not isinstance(item, dict):
        raise EpisodeRejected("arrow", f"{board_id} 的球路不是对象。")
    ids = item.get("ids")
    if not isinstance(ids, list) or len(ids) < 2:
        raise EpisodeRejected("arrow", f"{board_id} 的球路至少要有起点和终点。")
    points = []
    for identifier in ids:
        if identifier not in catalog:
            raise EpisodeRejected("arrow", f"{board_id} 的球路包含未知点 {identifier}。")
        points.append(catalog[identifier])
    for left, right in zip(points, points[1:]):
        _separated(left, right, f"{board_id}.route")
    intent = item.get("intent") or "keep"
    if intent not in ("forward", "keep"):
        raise EpisodeRejected("direction", f"{board_id} 的球路 intent 只能是 forward 或 keep。")
    if intent == "forward" and points[-1][0] >= points[0][0] - 1e-9:
        raise EpisodeRejected(
            "direction",
            f"{board_id} 的球路标成向前，但归一化后终点 u={points[-1][0]} 没有小于起点 u={points[0][0]}。"
            "攻左约定下，向前必须走向更小的 u。整板已用同一次翻转，不能只改这一条。",
        )
    t0 = _time(item.get("t0"), f"{board_id}.route.t0", basis, clock, scene_name, output_start)
    t1 = _time(item.get("t1"), f"{board_id}.route.t1", basis, clock, scene_name, output_start)
    _span(t0, t1, duration, f"{board_id}.route")
    return {"ids": list(ids), "t0": t0, "t1": t1, "intent": intent}


def _label(item, board_id, basis, clock, scene_name, output_start, duration, ids):
    if not isinstance(item, dict):
        raise EpisodeRejected("geometry", f"{board_id} 的标签不完整。")
    if item.get("id") not in ids:
        raise EpisodeRejected("geometry", f"{board_id} 的标签 {item.get('id')} 没有对应球员。")
    text = item.get("text")
    if not isinstance(text, str) or not text.strip() or len(text) > 16:
        raise EpisodeRejected("geometry", f"{board_id} 的标签要是 1–16 字的短句。")
    offset = item.get("offset") or [24, -28]
    if not isinstance(offset, list) or len(offset) != 2:
        raise EpisodeRejected("geometry", f"{board_id} 的标签偏移无效。")
    t0 = _time(item.get("t0"), f"{item['id']}.label.t0", basis, clock, scene_name, output_start)
    t1 = _time(item.get("t1"), f"{item['id']}.label.t1", basis, clock, scene_name, output_start)
    _span(t0, t1, duration, f"{board_id}.{item['id']}.label")
    return {"id": item["id"], "text": text, "t0": t0, "t1": t1, "offset": [float(offset[0]), float(offset[1])]}


def _annotation(item, board_id, basis, clock, scene_name, output_start, duration, catalog, claim, evidence):
    if not isinstance(item, dict) or "type" not in item:
        raise EpisodeRejected("geometry", f"{board_id} 的注释不完整。")
    kind = item["type"]
    t0 = _time(item.get("t0"), f"{board_id}.annotation.t0", basis, clock, scene_name, output_start)
    if kind == "origin_ring":
        if item.get("point") not in catalog:
            raise EpisodeRejected("geometry", f"{board_id} 的原位环指向未知点。")
        if t0 < -1e-9 or t0 > duration + 1e-9:
            raise EpisodeRejected("timeline", f"{board_id} 的原位环时间越界。")
        return {"type": kind, "point": item["point"], "t0": t0, "label": item.get("label") or "原位", "radius": 25}
    t1 = _time(item.get("t1"), f"{board_id}.annotation.t1", basis, clock, scene_name, output_start)
    _span(t0, t1, duration, f"{board_id}.annotation")
    if kind == "screen_channel":
        if item.get("node") not in catalog:
            raise EpisodeRejected("geometry", f"{board_id} 的通道注释指向未知球员。")
        return {
            "type": kind,
            "node": item["node"],
            "t0": t0,
            "t1": t1,
            "dx0": float(item.get("dx0", 52)),
            "dx1": float(item.get("dx1", -45)),
            "width": float(item.get("width", 13)),
        }
    if kind == "segment":
        frm = _uv(item.get("frm"), f"{board_id}.segment.frm")
        to = _uv(item.get("to"), f"{board_id}.segment.to")
        _separated(frm, to, f"{board_id}.segment")
        if item.get("kind") not in ("run", "def"):
            raise EpisodeRejected("arrow", f"{board_id} 的线段 kind 无效。")
        if claim == "evidence_locked":
            _require_evidence(item, claim, evidence, f"{board_id}.segment")
        return {"type": kind, "frm": frm, "to": to, "t0": t0, "t1": t1, "kind": item["kind"]}
    raise EpisodeRejected("geometry", f"{board_id} 有不认识的注释类型 {kind}。")


def _layers(layers, duration, board_id, basis, clock, scene_name, output_start):
    compiled = []
    previous = -1.0
    for layer in layers:
        if not isinstance(layer, dict) or "name" not in layer:
            raise EpisodeRejected("timeline", f"{board_id} 的分层缺少 name。")
        moment = _time(layer.get("t"), f"{board_id}.layer", basis, clock, scene_name, output_start)
        if moment < previous - 1e-9:
            raise EpisodeRejected("timeline", f"{board_id} 的分层时间必须递增。")
        if moment < -1e-9 or moment > duration + 1e-9:
            raise EpisodeRejected("timeline", f"{board_id} 的分层时间越出板时长。")
        previous = moment
        compiled.append({"t": moment, "name": str(layer["name"])})
    return compiled


def _stills(marks, board_id):
    compiled = []
    for mark in marks:
        if not isinstance(mark, dict):
            raise EpisodeRejected("mask", f"{board_id} 的实拍标记无效。")
        if mark.get("moving"):
            raise EpisodeRejected("mask", f"{board_id} 的实拍圈只能定格。没有逐帧脚点之前不能做动圈。")
        if "foot_px" not in mark or not mark.get("mask_path") and not mark.get("mask_polygon"):
            raise EpisodeRejected("mask", f"{board_id} 缺少脚点或 mask。只写一个 mask 字段不算通过，这里连圈都不画。")
        foot = mark["foot_px"]
        if not isinstance(foot, list) or len(foot) != 2:
            raise EpisodeRejected("mask", f"{board_id} 的脚点必须是像素坐标 [x, y]。")
        compiled.append(mark)
    return compiled


def _order_rules(rules, routes, motions, catalog, board_id):
    motion_by_id = {item["id"]: item for item in motions}
    for rule in rules:
        if not isinstance(rule, dict) or rule.get("type") != "route_clears_point_before_motion":
            raise EpisodeRejected("order_rule", f"{board_id} 的顺序规则无法识别。")
        route = routes[rule["route"]]
        if rule["point"] not in route["ids"]:
            raise EpisodeRejected("order_rule", f"{board_id} 的顺序规则点不在球路上。")
        if rule["motion"] not in motion_by_id:
            raise EpisodeRejected("order_rule", f"{board_id} 的顺序规则找不到对应跑动。")
        points = [catalog[identifier] for identifier in route["ids"]]
        lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
        total = sum(lengths)
        cursor = 0.0
        target = rule["point"]
        seen = 0.0
        for identifier, length in zip(route["ids"][1:], lengths):
            cursor += length
            if identifier == target:
                seen = cursor
                break
        fraction = 0.0 if total == 0 else seen / total
        cleared = route["t0"] + (route["t1"] - route["t0"]) * ease_inv(fraction)
        motion = motion_by_id[rule["motion"]]
        if motion["t0"] + 1e-6 < cleared:
            raise EpisodeRejected(
                "order_rule",
                f"{board_id}：{rule['motion']} 在 {motion['t0']:.3f}s 启动，"
                f"早于球到达 {rule['point']} 的 {cleared:.3f}s。拒绝渲染。",
            )


def _projection(nodes, motions, extras):
    points = [node["uv"] for node in nodes if node["focus"]]
    for motion in motions:
        points.extend([motion["frm"], motion["to"]])
    points.extend(extras.values())
    meters = [(point[0] * 1.05, point[1] * 0.68) for point in points]
    min_x = min(point[0] for point in meters) - 4
    min_y = min(point[1] for point in meters) - 3
    max_x = max(point[0] for point in meters) + 4
    max_y = max(point[1] for point in meters) + 3
    span_x = max_x - min_x
    span_y = max_y - min_y
    scale = min(900 / span_x, 490 / span_y)
    return {
        "cx": 560,
        "cy": 359,
        "centre_m": [(min_x + max_x) / 2, (min_y + max_y) / 2],
        "scale": scale,
    }


def _flip_uvs(node, path, found):
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}"
            if key in UV_KEYS and _is_uv(value):
                value[0] = 100 - float(value[0])
                value[1] = float(value[1])
                found.append(child)
            elif key in ("foot_px", "mask_polygon", "offset", "native_size"):
                continue
            else:
                _flip_uvs(value, child, found)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _flip_uvs(value, f"{path}[{index}]", found)


def _is_uv(value):
    return (
        isinstance(value, list)
        and len(value) == 2
        and isinstance(value[0], (int, float))
        and not isinstance(value[0], bool)
        and isinstance(value[1], (int, float))
        and not isinstance(value[1], bool)
    )


def _uv(value, label):
    if not _is_uv(value):
        raise EpisodeRejected("geometry_range", f"{label} 缺少 [u, v] 坐标。不会用旧场次的点补上。")
    u, v = float(value[0]), float(value[1])
    if not math.isfinite(u) or not math.isfinite(v) or u < 0 or u > 100 or v < 0 or v > 100:
        raise EpisodeRejected("geometry_range", f"{label} 的坐标 ({u}, {v}) 超出 0–100。拒绝渲染。")
    return [u, v]


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise EpisodeRejected("timeline", f"{label} 不是有限数字。")
    return float(value)


def _time(value, label, basis, clock, scene_name, output_start):
    if isinstance(value, dict):
        if basis != "word_clock":
            raise EpisodeRejected("word_clock", f"{label} 使用了词级触发，但这份包的 timing_basis 不是 word_clock。")
        token = value.get("word")
        if not isinstance(token, str) or not token:
            raise EpisodeRejected("word_clock", f"{label} 的词级触发缺少 word。")
        scene_key = value.get("scene") or scene_name
        if scene_key not in clock:
            raise EpisodeRejected("word_clock", f"{label} 找不到场景 {scene_key}。")
        absolute = _word_absolute(clock[scene_key], token, int(value.get("occ") or 0), float(value.get("add") or 0))
        return qtime(absolute - output_start)
    if value is None:
        raise EpisodeRejected("timeline", f"{label} 缺少时间。")
    return qtime(_number(value, label))


def _word_absolute(scene, token, occ, add):
    words = scene["words"]
    full = "".join(word["text"] for word in words)
    index = -1
    for _ in range(occ + 1):
        index = full.find(token, index + 1)
        if index < 0:
            raise EpisodeRejected("word_clock", f"场景里找不到词「{token}」。不会改用别的场次旁白。")
    cursor = 0
    for word in words:
        if cursor + len(word["text"]) > index:
            local = word["offset"] + (index - cursor) * word["duration"] / len(word["text"])
            return qtime(float(scene["output_start_s"]) + local + add)
        cursor += len(word["text"])
    raise EpisodeRejected("word_clock", f"词「{token}」没有落到字级时间上。")


def _span(t0, t1, duration, label):
    if t1 <= t0:
        raise EpisodeRejected("timeline", f"{label} 的结束时间必须晚于开始。")
    if t0 < -1e-9 or t1 > duration + 1e-6:
        raise EpisodeRejected("timeline", f"{label} 的时间 {t0}–{t1} 越出板时长 {duration}。")


def _separated(start, end, label):
    if math.dist(start, end) < 0.05:
        raise EpisodeRejected("arrow", f"{label} 的起终点几乎重合，拒绝画箭头。")


def _label_overlap(labels, duration, board_id):
    step = 1 / 25
    moment = 0.0
    while moment <= duration + 1e-9:
        active = [label for label in labels if label["t0"] - 1e-9 <= moment < label["t1"] - 1e-9]
        if len(active) > 3:
            raise EpisodeRejected("geometry", f"{board_id} 在 {moment:.2f}s 同时有 {len(active)} 个标签，最多 3 个。")
        moment += step


def _require_evidence(item, claim, evidence, label):
    if claim != "evidence_locked":
        return
    pointer = item.get("evidence_id")
    if not pointer or pointer not in evidence:
        raise EpisodeRejected(
            "evidence",
            f"{label} 没有可用的证据帧指针。缺证据的坐标拒绝渲染，不会装成真实回合。",
        )
