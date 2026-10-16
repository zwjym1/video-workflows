"""Generate an Edge TTS audition; fail visibly if the remote service fails.

Requires: Python 3.11+, edge-tts==7.3.1, ffmpeg and ffprobe on PATH.
Run from any directory: python scripts/narration-edge.py
Existing Windows system-voice assets are preserved.
"""
import asyncio
import json
import math
from pathlib import Path
import subprocess

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
VOICE = "zh-CN-YunxiNeural"
FPS = 30
TAIL_SECONDS = 0.5
TEXTS = [
    "和 AI 改作品，你是不是也说过：再高级一点？",
    "把感觉拆成四件事。位置，哪里要改？问题，哪里不好？目标，改成什么？限制，保留什么？",
    "比如这个页面。标题太小，重点不清。把标题放大，说明弱化；按钮保留原来的青色。每一条，都能检查。",
    "再看前后对比。把模糊的不满意，写成看得见的变化。",
]


def duration(path):
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], text=True).strip())


async def main():
    (ROOT / "public").mkdir(exist_ok=True)
    (ROOT / "src").mkdir(exist_ok=True)
    timings = []
    start = 0
    for i, text in enumerate(TEXTS):
        raw = ROOT / f"public/edge-voice-{i}-raw.mp3"
        audio = ROOT / f"public/edge-voice-{i}.mp3"
        metadata = ROOT / f"public/edge-voice-{i}.jsonl"
        await edge_tts.Communicate(
            text, VOICE, rate="+0%", pitch="+0Hz", volume="+0%",
            boundary="WordBoundary",
        ).save(str(raw), str(metadata))
        raw_duration = duration(raw)
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", str(raw),
            "-af", f"apad=pad_dur={TAIL_SECONDS}", "-c:a", "libmp3lame",
            "-b:a", "128k", str(audio),
        ], check=True)
        padded_duration = duration(audio)
        frames = math.ceil(padded_duration * FPS)
        boundaries = []
        for line in metadata.read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            boundaries.append({
                "type": item["type"], "text": item["text"],
                "offset": item["offset"] / 10_000_000,
                "duration": item["duration"] / 10_000_000,
            })
        timings.append({
            "text": text, "start": start, "frames": frames,
            "duration": padded_duration, "speechDuration": raw_duration,
            "tailSeconds": TAIL_SECONDS, "voice": VOICE, "rate": "+0%",
            "audio": audio.name, "boundaries": boundaries,
        })
        start += frames
        print(json.dumps({"segment": i, "duration": padded_duration,
                          "frames": frames, "boundaries": len(boundaries)},
                         ensure_ascii=False), flush=True)
    target = ROOT / "src/edge-timings.json"
    target.write_text(json.dumps(timings, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {target}; {start} frames; {start/FPS:.3f} seconds", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
