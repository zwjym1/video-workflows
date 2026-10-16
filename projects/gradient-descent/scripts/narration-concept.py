"""Single-idea Yunxi audition. Requires edge-tts 7.3.1 and FFmpeg."""
import asyncio
import json
import math
from pathlib import Path
import subprocess

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
TEXT = "再高级一点？改颜色，还是改排版？先锁定标题，再明确改法：放大。"
VOICE = "zh-CN-YunxiNeural"


def probe(path):
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", str(path),
    ], text=True).strip())


async def main():
    raw = ROOT / "public/concept-voice-raw.mp3"
    audio = ROOT / "public/concept-voice.mp3"
    meta = ROOT / "public/concept-voice.jsonl"
    await edge_tts.Communicate(
        TEXT, VOICE, rate="+10%", boundary="WordBoundary",
    ).save(str(raw), str(meta))
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(raw),
        "-af", "apad=pad_dur=0.6", "-c:a", "libmp3lame", "-b:a", "128k", str(audio),
    ], check=True)
    boundaries = []
    for line in meta.read_text(encoding="utf-8").splitlines():
        b = json.loads(line)
        boundaries.append({"text": b["text"], "offset": b["offset"] / 10_000_000,
                           "duration": b["duration"] / 10_000_000, "type": b["type"]})
    duration = probe(audio)
    result = {"audio": audio.name, "text": TEXT, "voice": VOICE, "rate": "+10%",
              "duration": duration, "frames": math.ceil(duration * 30),
              "tailSeconds": 0.6, "speechDuration": probe(raw), "boundaries": boundaries}
    (ROOT / "src/concept-timing.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
