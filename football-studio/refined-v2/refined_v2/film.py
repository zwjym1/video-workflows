"""观众版装配。

输入是源片、EDL、可选的已有字幕。输出沿用精修板的层次，再接回实拍。
这里不生成配音。没有旁白音轨时成片静音，字幕只来自 EDL 里已经写好的句子。

成片按帧写进一个 ffmpeg 进程。内存里只留交叠所需的几帧，不把整段画面收成列表。
实拍音轨按每个镜头的 src_in/src_out 铺到成片时间上。板段默认没有源声，
除非 EDL 显式写了 authorized 的环境底。
"""

from __future__ import annotations

import json
import subprocess
import threading
from pathlib import Path

from PIL import Image, ImageDraw

from .board import render_board
from .draw import font as load_font
from .draw import resolve_font
from .errors import EpisodeRejected

DISSOLVE_FRAMES = {4, 5, 6}
TAIL_LIMIT = 6
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


def _overlaps(a0, a1, b0, b1):
    return float(a0) < float(b1) and float(b0) < float(a1)


def _shot_count(shot, board, fps):
    kind = shot.get("kind")
    if kind == "live":
        start, end = float(shot["src_in"]), float(shot["src_out"])
        if end <= start:
            raise EpisodeRejected("timeline", "实拍区间的结束必须晚于开始。")
        return max(1, int(round((end - start) * fps)))
    if kind == "board":
        t0 = float(shot.get("t0", 0))
        t1 = float(shot.get("t1", board["duration_s"]))
        if t1 <= t0 or t0 < -1e-6 or t1 > board["duration_s"] + 1e-6:
            raise EpisodeRejected("timeline", f"{board['id']} 的板上时间 {t0}–{t1} 无效。")
        return max(1, int(round((t1 - t0) * fps)))
    raise EpisodeRejected("timeline", f"镜头类型 {kind} 不能装配。")


def plan_timeline(episode, edl):
    """算出成片帧数和每个镜头在成片上的位置。不解码、不攒帧。"""
    fps = int(edl.get("output", {}).get("fps", 25))
    boards = {board["id"]: board for board in episode["boards"]}
    forbidden = episode.get("forbidden_clip_s") or []
    cursor = 0
    placements = []
    for index, shot in enumerate(edl["shots"]):
        kind = shot.get("kind")
        if kind == "board_hold":
            raise EpisodeRejected("timeline", "拒绝用末帧冻住。把层次铺进整段旁白，不要在动画结束后停住。")
        dissolve = int(shot.get("dissolve_frames") or 0)
        if dissolve and dissolve not in DISSOLVE_FRAMES:
            raise EpisodeRejected("timeline", "回实拍只接受 4、5 或 6 帧交叠，不把转场做成一段效果。")
        if kind == "live":
            board = None
            src_in, src_out = float(shot["src_in"]), float(shot["src_out"])
            for ban in forbidden:
                if _overlaps(src_in, src_out, ban[0], ban[1]):
                    raise EpisodeRejected(
                        "continuity",
                        f"实拍 {src_in}–{src_out} 落在禁止的裁切窗 {ban}。中圈开球不能铺进成片。",
                    )
        elif kind == "board":
            board = boards.get(shot.get("board"))
            if board is None:
                raise EpisodeRejected("geometry", f"EDL 指向不存在的板 {shot.get('board')}。")
            src_in = src_out = None
        else:
            raise EpisodeRejected("timeline", f"第 {index} 个镜头类型 {kind} 不能装配。")
        count = _shot_count(shot, board, fps)
        if dissolve and count <= dissolve:
            raise EpisodeRejected("timeline", "镜头比交叠还短，拒绝装配。")
        overlap = dissolve if index else 0
        start = cursor - overlap
        if start < 0:
            raise EpisodeRejected("timeline", "交叠比前面的镜头还长，拒绝装配。")
        placements.append(
            {
                "index": index,
                "kind": kind,
                "board": board,
                "shot": shot,
                "dissolve": overlap,
                "count": count,
                "src_in": src_in,
                "src_out": src_out,
                "out_frame": start,
                "out_s": start / fps,
                "out_dur": count / fps,
                "label": shot.get("label") or "",
            }
        )
        cursor = start + count
    return cursor, placements


def assemble(episode, edl, source, out_path, audience=True, states_path=None):
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
    total, placements = plan_timeline(episode, edl)
    _validate_bed(edl, episode.get("forbidden_clip_s") or [])
    captions = _caption_index(edl.get("captions") or [], fps)
    margin = subtitle_margin(out_h)
    silent = Path(str(out_path) + ".video.mp4") if edl.get("audio") else Path(out_path)
    states = []
    state_file = None
    if states_path:
        state_file = open(states_path, "w", encoding="utf-8")
    sampler = _RssSampler()
    sampler.start()
    encoder = _Encoder(silent, fps, out_w, out_h)
    try:
        _stream(episode, placements, source, fps, out_w, out_h, duration, audience, encoder, captions, margin, states, state_file)
        encoder.close()
    except Exception:
        encoder.abort()
        raise
    finally:
        sampler.stop()
        if state_file is not None:
            state_file.close()
    if len(states) != total:
        raise EpisodeRejected("timeline", f"写出了 {len(states)} 帧，时间轴是 {total} 帧。")
    if edl.get("audio"):
        _mux_audio(silent, edl, Path(edl.get("_dir", ".")), Path(out_path), source, placements, total / fps, episode.get("forbidden_clip_s") or [])
        silent.unlink(missing_ok=True)
    return {
        "path": str(out_path),
        "width": out_w,
        "height": out_h,
        "fps": fps,
        "frames": total,
        "duration_s": round(total / fps, 3),
        "audience": audience,
        "master": False,
        "audio": "voice_sfx_and_mapped_live_windows" if edl.get("audio") else None,
        "upscaled": False,
        "source_size": [width, height],
        "subtitle_margin_px": margin,
        "peak_rss_kib": sampler.peak,
        "synthetic": bool(edl.get("synthetic")),
        "states": states,
    }


def _probe(path):
    raw = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_type,duration", "-of", "json", str(path)],
        text=True,
    )
    data = json.loads(raw)
    video = next(stream for stream in data["streams"] if stream.get("codec_type") == "video")
    duration = float(video.get("duration") or data.get("format", {}).get("duration") or 0)
    return int(video["width"]), int(video["height"]), duration


def _has_audio(path):
    raw = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "json", str(path)],
        text=True,
    )
    return bool(json.loads(raw).get("streams"))


def _iter_live(source, start, end, fps, out_w, out_h, duration, count, label):
    start, end = float(start), float(end)
    if not 0 <= start < end <= duration + 0.05:
        raise EpisodeRejected("timeline", f"实拍区间 {start}–{end} 不在源片 {duration:.2f} 秒里。")
    src_w, src_h, _ = _probe(source)
    scale = ""
    if (out_w, out_h) != (src_w, src_h):
        if out_w > src_w or out_h > src_h:
            raise EpisodeRejected("evidence", "实拍只允许缩小，不允许放大。")
        scale = f",scale={out_w}:{out_h}:flags=lanczos"
    command = [
        "ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}", "-i", str(source),
        "-vf", f"fps={fps}{scale}", "-frames:v", str(count), "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ]
    frame_bytes = out_w * out_h * 3
    process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=frame_bytes)
    produced = 0
    try:
        while produced < count:
            blob = _read_exact(process.stdout, frame_bytes)
            if blob is None:
                break
            image = Image.frombytes("RGB", (out_w, out_h), blob)
            yield image, {
                "kind": "live",
                "source_s": round(start + produced / fps, 3),
                "board": None,
                "label": label,
                "route_progress": {},
                "motion_progress": {},
            }
            produced += 1
            del image
    finally:
        if process.stdout:
            process.stdout.close()
        if process.poll() is None:
            process.kill()
            process.wait()
        else:
            process.wait()
    if produced < count:
        raise EpisodeRejected("timeline", "源片这一段没有解出足够的画面。")


def _read_exact(stream, size):
    blob = bytearray()
    while len(blob) < size:
        chunk = stream.read(size - len(blob))
        if not chunk:
            return None
        blob += chunk
    return bytes(blob)


def _iter_board(episode, board, shot, fps, audience, present, count, label):
    t0 = float(shot.get("t0", 0))
    for index in range(count):
        moment = min(board["duration_s"], t0 + index / fps)
        image, state = render_board(episode, board, moment, show_stamp=not audience, present=present)
        state = dict(state)
        state["kind"] = "board"
        state["label"] = label
        if audience:
            state["stamp_burned"] = False
        yield image, state


def _stream(episode, placements, source, fps, out_w, out_h, duration, audience, encoder, captions, margin, states, state_file):
    tail = []
    for place in placements:
        overlap = place["dissolve"] if place["index"] else 0
        frames = _frames_for(episode, place, source, fps, out_w, out_h, duration, audience)
        if overlap:
            if overlap > len(tail):
                raise EpisodeRejected("timeline", "交叠窗口比实际留下的帧多。")
            encoder.commit(tail[:-overlap], captions, margin, states, state_file, fps, audience)
            base = tail[-overlap:]
        else:
            encoder.commit(tail, captions, margin, states, state_file, fps, audience)
            base = []
        tail = []
        for index, (image, state) in enumerate(frames):
            if index < overlap:
                alpha = (index + 1) / (overlap + 1)
                mixed = Image.blend(base[index][0].convert("RGB"), image.convert("RGB"), alpha)
                state = dict(state)
                state["kind"] = "dissolve"
                tail.append((mixed, state))
                del image
            else:
                tail.append((image.convert("RGB"), state))
            while len(tail) > TAIL_LIMIT:
                encoder.commit(tail[:1], captions, margin, states, state_file, fps, audience)
                del tail[0]
        del base
    encoder.commit(tail, captions, margin, states, state_file, fps, audience)


def _frames_for(episode, place, source, fps, out_w, out_h, duration, audience):
    shot = place["shot"]
    label = place["label"]
    if place["kind"] == "live":
        return _iter_live(source, shot["src_in"], shot["src_out"], fps, out_w, out_h, duration, place["count"], label)
    return _iter_board(episode, place["board"], shot, fps, audience, (out_w, out_h), place["count"], label)


def _caption_index(captions, fps):
    indexed = []
    for item in captions:
        for token in FORBIDDEN_CAPTION:
            if token in item.get("text", ""):
                raise EpisodeRejected("timeline", f"观众字幕不能出现「{token}」。")
        start = int(round(float(item["start_s"]) * fps))
        end = int(round(float(item["end_s"]) * fps))
        indexed.append((start, end, item["text"]))
    return indexed


class _Encoder:
    def __init__(self, path, fps, width, height):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.width = width
        self.height = height
        self.fps = fps
        self.face = None
        self._closed = False
        command = [
            "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
            "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(self.path),
        ]
        self.proc = subprocess.Popen(command, stdin=subprocess.PIPE, bufsize=width * height * 3)

    def commit(self, frames, captions, margin, states, state_file, fps, audience):
        for image, state in frames:
            index = len(states)
            burned = _burn_one(image, index, captions, margin, self.width, self.height, self._face())
            self.proc.stdin.write(burned.tobytes())
            del burned
            del image
            public = _public_state(state, index, fps, audience)
            states.append(public)
            if state_file is not None:
                row = {k: v for k, v in public.items() if k != "stamp"}
                state_file.write(json.dumps(row, ensure_ascii=False) + "\n")
                state_file.flush()

    def _face(self):
        if self.face is None:
            self.face = load_font(33, 1, resolve_font()["path"])
        return self.face

    def close(self):
        if self._closed:
            return
        self._closed = True
        self.proc.stdin.close()
        code = self.proc.wait()
        if code != 0:
            self.path.unlink(missing_ok=True)
            raise EpisodeRejected("timeline", "成片编码失败。")

    def abort(self):
        if self._closed:
            self.path.unlink(missing_ok=True)
            return
        self._closed = True
        try:
            if self.proc.stdin:
                self.proc.stdin.close()
        except Exception:
            pass
        if self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait()
        self.path.unlink(missing_ok=True)


def _public_state(state, index, fps, audience):
    state = dict(state)
    state["frame"] = index
    state["output_s"] = round(index / fps, 3)
    state["audience"] = audience
    state["stamp_burned"] = False if audience else state.get("stamp_burned", True)
    return state


def _burn_one(image, index, captions, margin, width, height, face):
    text = None
    for start, end, cue in captions:
        if start <= index < end:
            text = cue
            break
    if not text:
        return image.convert("RGB")
    frame = image.convert("RGBA")
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    pen = ImageDraw.Draw(overlay)
    box = pen.textbbox((0, 0), text, font=face)
    text_w = box[2] - box[0]
    text_h = box[3] - box[1]
    x = (width - text_w) / 2
    y = height - margin - text_h - 8
    if y + text_h > height - margin:
        raise EpisodeRejected("timeline", "字幕进入了底边安全区。")
    pen.rounded_rectangle((x - 14, y - 6, x + text_w + 14, y + text_h + 8), radius=8, fill=(4, 10, 14, 140))
    pen.text((x, y), text, font=face, fill=(242, 243, 233, 255))
    return Image.alpha_composite(frame, overlay).convert("RGB")


class _RssSampler:
    def __init__(self):
        self.peak = _rss_kib()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self.peak = max(self.peak, _rss_kib())
        self._stop.set()
        self._thread.join(timeout=1)

    def _run(self):
        while not self._stop.wait(0.1):
            self.peak = max(self.peak, _rss_kib())


def _rss_kib():
    try:
        with open("/proc/self/status", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except OSError:
        return 0
    return 0


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
    states_path = None
    try:
        episode = load_episode(args.episode)
        edl = load_edl(args.edl)
        if args.qc:
            qc = Path(args.qc)
            qc.mkdir(parents=True, exist_ok=True)
            states_path = qc / "FILM_STATES.jsonl"
        report = assemble(episode, edl, args.source, args.out, audience=True, states_path=states_path)
    except EpisodeRejected as exc:
        print(exc, file=sys.stderr)
        return 2
    if args.qc:
        qc = Path(args.qc)
        report_out = {k: v for k, v in report.items() if k != "states"}
        report_out["master"] = False
        report_out["note"] = "观众装配，不是最终母带。核验戳只在这个 QC 目录。音轨按 EDL 实拍窗对齐，板段默认无源声。"
        (qc / "FILM.json").write_text(json.dumps(report_out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("path", "duration_s", "frames", "width", "height", "master", "audio", "peak_rss_kib")}, ensure_ascii=False))
    return 0


def _validate_bed(edl, forbidden):
    audio = edl.get("audio") or {}
    bed = audio.get("board_bed")
    if bed is None:
        return
    if not isinstance(bed, dict) or bed.get("authorized") is not True:
        raise EpisodeRejected("timeline", "板下环境底必须显式写 authorized: true。不能把源片从 0 秒整段垫进去。")
    try:
        src_in = float(bed["src_in"])
        src_out = float(bed["src_out"])
    except (KeyError, TypeError, ValueError) as exc:
        raise EpisodeRejected("timeline", "板下环境底要写 src_in 和 src_out。") from exc
    if src_out <= src_in:
        raise EpisodeRejected("timeline", "板下环境底的源窗无效。")
    _reject_window(src_in, src_out, forbidden, "板下环境底")


def _mux_audio(video, edl, base, out_path, source_media, placements, total_s, forbidden):
    audio = edl["audio"]
    gain = audio.get("source_gain_db", -18)
    bed = audio.get("board_bed")
    bed_span = None
    if bed is not None:
        if not isinstance(bed, dict) or bed.get("authorized") is not True:
            raise EpisodeRejected("timeline", "板下环境底必须显式写 authorized: true。不能把源片从 0 秒整段垫进去。")
        try:
            src_in = float(bed["src_in"])
            src_out = float(bed["src_out"])
        except (KeyError, TypeError, ValueError) as exc:
            raise EpisodeRejected("timeline", "板下环境底要写 src_in 和 src_out。") from exc
        if src_out <= src_in:
            raise EpisodeRejected("timeline", "板下环境底的源窗无效。")
        _reject_window(src_in, src_out, forbidden, "板下环境底")
        bed_span = (src_in, src_out)
    source_uses = []
    for item in placements:
        if item["kind"] == "live":
            _reject_window(item["src_in"], item["src_out"], forbidden, item["label"] or "实拍")
            source_uses.append({"src_in": item["src_in"], "src_out": item["src_out"], "out_s": item["out_s"]})
        elif item["kind"] == "board" and bed_span is not None:
            play = min(item["out_dur"], bed_span[1] - bed_span[0])
            source_uses.append({"src_in": bed_span[0], "src_out": bed_span[0] + play, "out_s": item["out_s"]})
    inputs = ["-i", str(video)]
    filters = []
    labels = []
    next_input = 1
    if source_uses:
        source = Path(audio.get("source") or source_media)
        if not source.is_absolute():
            source = base / source
        if not source.is_file():
            raise EpisodeRejected("missing_episode", f"找不到垫底音轨 {source}。")
        if not _has_audio(source):
            raise EpisodeRejected("timeline", "源片没有音轨，不能按实拍窗铺底。")
        inputs += ["-i", str(source)]
        n = len(source_uses)
        if n == 1:
            filters.append("[1:a]anull[src0]")
        else:
            filters.append("[1:a]asplit=" + str(n) + "".join(f"[src{i}]" for i in range(n)))
        for i, item in enumerate(source_uses):
            delay = max(0, int(round(float(item["out_s"]) * 1000)))
            filters.append(
                f"[src{i}]atrim=start={item['src_in']:.3f}:end={item['src_out']:.3f},"
                f"asetpts=PTS-STARTPTS,adelay={delay}|{delay},volume={gain}dB,aresample=48000[bed{i}]"
            )
            labels.append(f"[bed{i}]")
        next_input = 2
    for item in audio.get("voice") or []:
        path = _audio_path(item["file"], base)
        inputs += ["-i", str(path)]
        delay = int(round(float(item["start"]) * 1000))
        filters.append(f"[{next_input}:a]adelay={delay}|{delay},aresample=48000[v{next_input}]")
        labels.append(f"[v{next_input}]")
        next_input += 1
    for item in audio.get("sfx") or []:
        path = _audio_path(item["file"], base)
        inputs += ["-i", str(path)]
        delay = int(round(float(item["start"]) * 1000))
        filters.append(f"[{next_input}:a]adelay={delay}|{delay},volume={item.get('gain_db', -16)}dB,aresample=48000[s{next_input}]")
        labels.append(f"[s{next_input}]")
        next_input += 1
    if not labels:
        raise EpisodeRejected("timeline", "音轨没有任何可混的素材。")
    total = f"{total_s:.3f}"
    if len(labels) == 1:
        filters.append(f"{labels[0]}atrim=0:{total},asetpts=PTS-STARTPTS[a]")
    else:
        filters.append("".join(labels) + f"amix=inputs={len(labels)}:duration=longest:dropout_transition=0:normalize=0,atrim=0:{total},asetpts=PTS-STARTPTS[a]")
    command = [
        "ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters),
        "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", str(out_path),
    ]
    if subprocess.call(command) != 0:
        raise EpisodeRejected("timeline", "混音失败。没有改用新的配音。")


def _audio_path(raw, base):
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    if not path.is_file():
        raise EpisodeRejected("timeline", f"找不到已有音轨 {path}。不会新配音。")
    return path


def _reject_window(src_in, src_out, forbidden, label):
    for ban in forbidden:
        if _overlaps(src_in, src_out, ban[0], ban[1]):
            raise EpisodeRejected("continuity", f"{label} 的源窗 {src_in}–{src_out} 落在禁止的裁切窗 {ban}。")


if __name__ == "__main__":
    raise SystemExit(main())
