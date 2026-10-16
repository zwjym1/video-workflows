"""Generate an Edge TTS audition; fail visibly if the remote service fails.

Requires: Python 3.11+, edge-tts==7.3.1, ffmpeg and ffprobe on PATH.
Run from any directory: python scripts/narration-edge-v3.py
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
TAIL_SECONDS = [0.12, 0.12, 0.18, 0.7]
TEXTS = [
    "再高级一点？这句话，AI该改哪里？",
    "先指出位置：首页标题。说清问题：太小，重点不清。",
    "再给出目标：标题放大，说明弱化。也划清限制：按钮保留青色。",
    "看，修改前后，一眼就能检查。把感觉，变成具体改法。",
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
        raw = ROOT / f"public/v3-voice-{i}-raw.mp3"
        audio = ROOT / f"public/v3-voice-{i}.mp3"
        metadata = ROOT / f"public/v3-voice-{i}.jsonl"
        await edge_tts.Communicate(
            text, VOICE, rate="+10%", pitch="+0Hz", volume="+0%",
            boundary="WordBoundary",
        ).save(str(raw), str(metadata))
        raw_duration = duration(raw)
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", str(raw),
            "-af", f"apad=pad_dur={TAIL_SECONDS[i]}", "-c:a", "libmp3lame",
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
            "tailSeconds": TAIL_SECONDS[i], "voice": VOICE, "rate": "+10%",
            "audio": audio.name, "boundaries": boundaries,
        })
        start += frames
        print(json.dumps({"segment": i, "duration": padded_duration,
                          "frames": frames, "boundaries": len(boundaries)},
                         ensure_ascii=False), flush=True)
    target = ROOT / "src/v3-timings.json"
    target.write_text(json.dumps(timings, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {target}; {start} frames; {start/FPS:.3f} seconds", flush=True)


if __name__ == "__main__":
    asyncio.run(main())

