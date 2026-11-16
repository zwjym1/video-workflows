"""观众版装配。

输入是源片、EDL、可选的已有字幕。输出沿用精修板的层次，再接回实拍。
这里不生成配音。没有旁白音轨时成片静音，字幕只来自 EDL 里已经写好的句子。
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from .board import render_board
from .draw import font as load_font
from .draw import resolve_font
from .errors import EpisodeRejected

DISSOLVE_FRAMES = {4, 5, 6}
FORBIDDEN_CAPTION = ("无号码", "25号", "已对照", "非测绘", "geometry")


def subtitle_margin(height):
    """1080p 底边留白超过 60px，其它高度按同一比例。"""
    return int(60 * height / 1080) + 1


def _with_punctuation(scene):
    text = scene.get("text") or ""
    cursor = 0
    timed = []
    for word in scene["words"]:
        token = word["text"]
        found = text.find(token, cursor)
        if found < 0:
            timed.append(word)
            continue
        if found > cursor:
            timed.append({"text": text[cursor:found], "offset": word["offset"], "duration": 0.04})
        timed.append(word)
        cursor = found + len(token)
    return timed


def captions_from_words(scenes, starts):
    """把已有字级时间收成能读完的字幕。不改词，不新配音。"""
    cues = []
    for scene in scenes:
        origin = float(starts[scene["id"]])
        bucket = []
        phrases = []
        for word in _with_punctuation(scene):
            bucket.append(word)
            if word["text"] in "。！？，；":
                phrases.append(bucket)
                bucket = []
        if bucket:
            phrases.append(bucket)
        for phrase in phrases:
            text = "".join(word["text"] for word in phrase)
            start = origin + float(phrase[0]["offset"])
            end = origin + float(phrase[-1]["offset"]) + float(phrase[-1]["duration"])
            cues.append({"start_s": round(start, 3), "end_s": round(end, 3), "text": text, "scene": scene["id"]})
    fixed = []
    for index, cue in enumerate(cues):
        nxt = cues[index + 1]["start_s"] if index + 1 < len(cues) and cues[index + 1]["scene"] == cue["scene"] else cue["end_s"] + 1.2
        end = max(cue["end_s"], cue["start_s"] + 0.9)
        end = min(end, nxt - 0.04)
        if end <= cue["start_s"] + 0.2:
            end = cue["start_s"] + 0.8
        fixed.append({**cue, "start_s": round(cue["start_s"], 3), "end_s": round(end, 3)})
    return fixed


def load_edl(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data["_dir"] = str(Path(path).resolve().parent)
    if data.get("version") != 1:
        raise EpisodeRejected("timeline", "EDL version 只能是 1。")
    if not data.get("shots"):
        raise EpisodeRejected("timeline", "EDL 没有镜头。")
    if data.get("master") is True:
        raise EpisodeRejected("claim", "这份装配不能标成最终母带。")
    return data


def assemble(episode, edl, source, out_path, audience=True):
    source = Path(source)
    if not source.is_file():
        raise EpisodeRejected("missing_episode", f"找不到源片 {source}。不会改用别的素材顶上。")
    width, height, duration = _probe(source)
    if edl.get("output", {}).get("width", width) > width or edl.get("output", {}).get("height", height) > height:
        raise EpisodeRejected("evidence", "成片尺寸不能大于源片。不把较小的画面放大当母带。")
    out_w = edl.get("output", {}).get("width", width)
    out_h = edl.get("output", {}).get("height", height)
    if (out_w, out_h) not in ((1280, 720), (1920, 1080)):
        raise EpisodeRejected("evidence", "观众装配只接受 1280×720，或在源片本身达到 1920×1080 时直接出 1080p。")
    if width < out_w or height < out_h:
        raise EpisodeRejected("evidence", "源片比成片小。拒绝把 720p 代理放大成 1080p。")
    fps = int(edl.get("output", {}).get("fps", 25))
    boards = {board["id"]: board for board in episode["boards"]}
    shots = []
    for index, shot in enumerate(edl["shots"]):
        kind = shot.get("kind")
        if kind == "board_hold":
            raise EpisodeRejected("timeline", "拒绝用末帧冻住。把层次铺进整段旁白，不要在动画结束后停住。")
        dissolve = int(shot.get("dissolve_frames") or 0)
        if dissolve and dissolve not in DISSOLVE_FRAMES:
            raise EpisodeRejected("timeline", "回实拍只接受 4、5 或 6 帧交叠，不把转场做成一段效果。")
        if kind == "live":
            frames = _live_frames(source, shot["src_in"], shot["src_out"], fps, out_w, out_h, duration)
        elif kind == "board":
            board = boards.get(shot.get("board"))
            if board is None:
                raise EpisodeRejected("geometry", f"EDL 指向不存在的板 {shot.get('board')}。")
            frames = _board_frames(episode, board, float(shot.get("t0", 0)), float(shot.get("t1", board["duration_s"])), fps, audience, (out_w, out_h))
        else:
            raise EpisodeRejected("timeline", f"第 {index} 个镜头类型 {kind} 不能装配。")
        if dissolve and len(frames) <= dissolve:
            raise EpisodeRejected("timeline", "镜头比交叠还短，拒绝装配。")
        shots.append({"dissolve": dissolve, "frames": frames, "kind": kind})
    sequence = _join(shots)
    margin = subtitle_margin(out_h)
    _burn_captions(sequence, edl.get("captions") or [], fps, margin, out_w, out_h)
    silent = Path(str(out_path) + ".video.mp4")
    _write_mp4(sequence, silent if edl.get("audio") else out_path, fps, out_w, out_h)
    if edl.get("audio"):
        _mux_audio(silent, edl, Path(edl.get("_dir", ".")), out_path, source)
        silent.unlink(missing_ok=True)
    states = []
    for index, (image, state) in enumerate(sequence):
        state = dict(state)
        state["frame"] = index
        state["output_s"] = round(index / fps, 3)
        state["audience"] = audience
        state["stamp_burned"] = False if audience else state.get("stamp_burned", True)
        states.append(state)
    return {
        "path": str(out_path),
        "width": out_w,
        "height": out_h,
        "fps": fps,
        "frames": len(sequence),
        "duration_s": round(len(sequence) / fps, 3),
        "audience": audience,
        "master": False,
        "audio": "existing_voice_and_lowered_source" if edl.get("audio") else None,
        "upscaled": False,
        "source_size": [width, height],
        "subtitle_margin_px": margin,
        "states": states,
    }


def _probe(path):
    raw = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,duration", "-of", "json", str(path)],
        text=True,
    )
    stream = json.loads(raw)["streams"][0]
    return int(stream["width"]), int(stream["height"]), float(stream.get("duration") or 0)


def _live_frames(source, start, end, fps, out_w, out_h, duration):
    start, end = float(start), float(end)
    if not 0 <= start < end <= duration + 0.05:
        raise EpisodeRejected("timeline", f"实拍区间 {start}–{end} 不在源片 {duration:.2f} 秒里。")
    count = max(1, int(round((end - start) * fps)))
    scale = ""
    if (out_w, out_h) != _probe(source)[:2]:
        if out_w > _probe(source)[0] or out_h > _probe(source)[1]:
            raise EpisodeRejected("evidence", "实拍只允许缩小，不允许放大。")
        scale = f",scale={out_w}:{out_h}:flags=lanczos"
    command = [
        "ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}", "-i", str(source),
        "-vf", f"fps={fps}{scale}", "-frames:v", str(count), "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ]
    raw = subprocess.check_output(command)
    frame_bytes = out_w * out_h * 3
    if len(raw) < frame_bytes:
        raise EpisodeRejected("timeline", "源片这一段没有解出画面。")
    frames = []
    for index in range(len(raw) // frame_bytes):
        image = Image.frombytes("RGB", (out_w, out_h), raw[index * frame_bytes:(index + 1) * frame_bytes])
        frames.append((image, {"kind": "live", "source_s": round(start + index / fps, 3), "board": None, "route_progress": {}, "motion_progress": {}}))
    return frames[:count]


def _board_frames(episode, board, t0, t1, fps, audience, present):
    if t1 <= t0 or t0 < -1e-6 or t1 > board["duration_s"] + 1e-6:
        raise EpisodeRejected("timeline", f"{board['id']} 的板上时间 {t0}–{t1} 无效。")
    count = max(1, int(round((t1 - t0) * fps)))
    frames = []
    for index in range(count):
        moment = min(board["duration_s"], t0 + index / fps)
        image, state = render_board(episode, board, moment, show_stamp=not audience, present=present)
        state = dict(state)
        state["kind"] = "board"
        if audience:
            state["stamp_burned"] = False
        frames.append((image, state))
    return frames


def _join(shots):
    sequence = []
    for shot in shots:
        frames = shot["frames"]
        overlap = shot["dissolve"] if sequence else 0
        if overlap:
            for index in range(overlap):
                alpha = (index + 1) / (overlap + 1)
                base, _ = sequence[-overlap + index]
                incoming, state = frames[index]
                mixed = Image.blend(base.convert("RGB"), incoming.convert("RGB"), alpha)
                state = dict(state)
                state["kind"] = "dissolve"
                sequence[-overlap + index] = (mixed, state)
            sequence.extend(frames[overlap:])
        else:
            sequence.extend(frames)
    return sequence


def _burn_captions(sequence, captions, fps, margin, width, height):
    face = load_font(33, 1, resolve_font()["path"])
    for item in captions:
        for token in FORBIDDEN_CAPTION:
            if token in item.get("text", ""):
                raise EpisodeRejected("timeline", f"观众字幕不能出现「{token}」。")
        start = int(round(float(item["start_s"]) * fps))
        end = int(round(float(item["end_s"]) * fps))
        for index in range(max(0, start), min(len(sequence), end)):
            image, state = sequence[index]
            frame = image.convert("RGBA")
            overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            pen = ImageDraw.Draw(overlay)
            text = item["text"]
            box = pen.textbbox((0, 0), text, font=face)
            text_w = box[2] - box[0]
            text_h = box[3] - box[1]
            x = (width - text_w) / 2
            y = height - margin - text_h - 8
            if y + text_h > height - margin:
                raise EpisodeRejected("timeline", "字幕进入了底边安全区。")
            pen.rounded_rectangle((x - 14, y - 6, x + text_w + 14, y + text_h + 8), radius=8, fill=(4, 10, 14, 140))
            pen.text((x, y), text, font=face, fill=(242, 243, 233, 255))
            sequence[index] = (Image.alpha_composite(frame, overlay).convert("RGB"), state)


def main(argv=None):
    import argparse
    import sys

    from .episode import load_episode

    parser = argparse.ArgumentParser(description="按 EDL 装配观众版。不生成配音，不标成母带。")
    parser.add_argument("--episode", required=True)
    parser.add_argument("--edl", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--qc", help="把逐帧状态写到这个目录。观众成片本身不烧核验戳。")
    args = parser.parse_args(argv)
    try:
        episode = load_episode(args.episode)
        edl = load_edl(args.edl)
        report = assemble(episode, edl, args.source, args.out, audience=True)
    except EpisodeRejected as exc:
        print(exc, file=sys.stderr)
        return 2
    if args.qc:
        qc = Path(args.qc)
        qc.mkdir(parents=True, exist_ok=True)
        public = [{k: v for k, v in state.items() if k != "stamp"} for state in report["states"]]
        (qc / "FILM_STATES.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in public), encoding="utf-8")
        report_out = {k: v for k, v in report.items() if k != "states"}
        report_out["master"] = False
        report_out["note"] = "示例装配，不是最终母带。核验戳只在这个 QC 目录。"
        (qc / "FILM.json").write_text(json.dumps(report_out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("path", "duration_s", "width", "height", "master", "audio")}, ensure_ascii=False))
    return 0


def _mux_audio(video, edl, base, out_path, source_media):
    audio = edl["audio"]
    source = Path(audio.get("source") or source_media)
    if not source.is_absolute():
        source = base / source
    inputs = ["-i", str(video), "-i", str(source)]
    parts = [f"[1:a]volume={audio.get('source_gain_db', -18)}dB,aresample=48000[bed]"]
    labels = ["[bed]"]
    index = 2
    for item in audio.get("voice") or []:
        path = Path(item["file"])
        if not path.is_absolute():
            path = base / path
        inputs += ["-i", str(path)]
        delay = int(round(float(item["start"]) * 1000))
        parts.append(f"[{index}:a]adelay={delay}|{delay},aresample=48000[v{index}]")
        labels.append(f"[v{index}]")
        index += 1
    for item in audio.get("sfx") or []:
        path = Path(item["file"])
        if not path.is_absolute():
            path = base / path
        inputs += ["-i", str(path)]
        delay = int(round(float(item["start"]) * 1000))
        parts.append(f"[{index}:a]adelay={delay}|{delay},volume={item.get('gain_db', -16)}dB,aresample=48000[s{index}]")
        labels.append(f"[s{index}]")
        index += 1
    mix = "".join(labels) + f"amix=inputs={len(labels)}:duration=first:dropout_transition=0:normalize=0[a]"
    command = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(parts + [mix]), "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(out_path)]
    if subprocess.call(command) != 0:
        raise EpisodeRejected("timeline", "混音失败。没有改用新的配音。")


def _write_mp4(sequence, out_path, fps, width, height):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
        "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out_path),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    for image, _ in sequence:
        process.stdin.write(image.convert("RGB").tobytes())
    process.stdin.close()
    if process.wait() != 0:
        raise EpisodeRejected("timeline", "成片编码失败。")


if __name__ == "__main__":
    raise SystemExit(main())
