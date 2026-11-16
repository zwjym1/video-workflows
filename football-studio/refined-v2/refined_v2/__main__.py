"""渲染一份场次包。没有场次包就退出，不会去找阿森纳旧板。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

from .board import render_board
from .draw import FPS, H, W
from .episode import load_episode
from .errors import EpisodeRejected
from .qc import before_after, progress_sheet, side_by_side


def main(argv=None):
    parser = argparse.ArgumentParser(description="用精修 v2 画法渲染一份场次包。")
    parser.add_argument("episode", nargs="?", help="场次目录或 episode.json。必填。")
    parser.add_argument("--out", required=True, help="输出目录。")
    parser.add_argument("--board", action="append", default=[], help="只渲染这些板，可重复。")
    args = parser.parse_args(argv)
    if not args.episode:
        print("缺少场次包。拒绝渲染，不会改用 2018 阿森纳关系板。", file=sys.stderr)
        return 2
    try:
        episode = load_episode(args.episode)
    except EpisodeRejected as exc:
        print(exc, file=sys.stderr)
        return 2
    try:
        manifest = render_to(episode, args.out, set(args.board))
    except EpisodeRejected as exc:
        print(exc, file=sys.stderr)
        return 2
    print(json.dumps({"out": str(args.out), "files": len(manifest["files"]), "claim": episode["claim"]}, ensure_ascii=False))
    return 0


def render_to(episode, out_dir, only_boards=None):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    boards = [board for board in episode["boards"] if not only_boards or board["id"] in only_boards]
    if only_boards and len(boards) != len(only_boards):
        found = {board["id"] for board in boards}
        missing = sorted(set(only_boards) - found)
        raise EpisodeRejected("geometry", "场次里没有这些板：" + "、".join(missing))
    files = []
    cache = {}

    def frame(board, t):
        key = (board["id"], round(t * FPS) / FPS)
        if key not in cache:
            image, state = render_board(episode, board, key[1])
            cache[key] = (image, state)
        return cache[key]

    for board in boards:
        moments = board["layers"] or [{"t": board["duration_s"], "name": "完成"}]
        stills = []
        for layer in moments:
            image, state = frame(board, layer["t"])
            name = f"{board['id']}_t{layer['t']:.2f}.png"
            image.save(out / name)
            (out / f"{board['id']}_t{layer['t']:.2f}.json").write_text(
                json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            files.append(name)
            stills.append((f"{layer['t']:.2f}s {layer['name']}", image))
        sheet = progress_sheet(stills)
        sheet_name = f"{board['id']}_PROGRESS.png"
        sheet.save(out / sheet_name)
        files.append(sheet_name)
    demo = episode.get("demo") or {}
    for pair in demo.get("pairs") or []:
        if only_boards and pair["board"] not in only_boards:
            continue
        board = _board(episode, pair["board"])
        before, _ = frame(board, pair["before"])
        after, _ = frame(board, pair["after"])
        sheet = before_after(before, after, pair["before_name"], pair["after_name"], episode["stamp"])
        name = f"{board['id']}_BEFORE_AFTER.png"
        sheet.save(out / name)
        files.append(name)
    for item in demo.get("side_by_side") or []:
        if only_boards and item["board"] not in only_boards:
            continue
        board = _board(episode, item["board"])
        evidence = episode["evidence_frames"].get(item["evidence"])
        if evidence is None:
            raise EpisodeRejected("evidence", f"并排 QC 找不到证据帧 {item['evidence']}。")
        with Image.open(evidence["path"]) as source:
            evidence_image = source.convert("RGB")
        image, _ = frame(board, item["t"])
        role = evidence.get("role") or ""
        title = episode["stamp"]
        if role:
            title = role + " · " + title
        sheet, meta = side_by_side(image, evidence_image, title)
        if meta["upscaled"]:
            raise EpisodeRejected("evidence", "并排 QC 发生了放大。拒绝写出这张图。")
        name = f"{board['id']}_SIDE_BY_SIDE.png"
        sheet.save(out / name)
        (out / f"{board['id']}_SIDE_BY_SIDE.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        files.extend([name, f"{board['id']}_SIDE_BY_SIDE.json"])
    mp4_boards = demo.get("mp4_boards") or []
    for board_id in mp4_boards:
        if only_boards and board_id not in only_boards:
            continue
        board = _board(episode, board_id)
        name = f"{board_id}_LAYERS.mp4"
        _write_mp4(episode, board, out / name)
        files.append(name)
    manifest = {
        "episode_id": episode["episode_id"],
        "claim": episode["claim"],
        "stamp": episode["stamp"],
        "statement": episode["statement"],
        "timing_basis": episode["timing_basis"],
        "timing_note": episode["timing_note"],
        "native_size": episode["native_size"],
        "fps": episode["fps"],
        "supersample": episode["supersample"],
        "upscaled": False,
        "audio": None,
        "audio_note": "本轮不渲音频，不调用配音。",
        "geometry_verified": episode.get("geometry_verified", False),
        "orientation": episode["orientation"],
        "font": _font_of(cache),
        "limits": "没有核实过的 2020-08-14 穆勒回合坐标。本目录不是那粒进球的真实关系板。",
        "files": files,
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def _board(episode, board_id):
    for board in episode["boards"]:
        if board["id"] == board_id:
            return board
    raise EpisodeRejected("geometry", f"场次里没有板 {board_id}。")


def _font_of(cache):
    for image, state in cache.values():
        return state["font"]
    return None


def _write_mp4(episode, board, path):
    count = int(round(board["duration_s"] * FPS))
    command = [
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for index in range(count):
            image, _ = render_board(episode, board, index / FPS)
            process.stdin.write(image.tobytes())
    finally:
        process.stdin.close()
    code = process.wait()
    if code != 0:
        raise EpisodeRejected("timeline", f"ffmpeg 退出码 {code}，没有生成可冒充完成的视频。")


if __name__ == "__main__":
    sys.exit(main())
