"""Continue the approved concept audition. Existing opening assets are read only."""
import asyncio
import json
import math
from pathlib import Path
import subprocess
import edge_tts

ROOT = Path(__file__).resolve().parents[1]
TEXTS = [
    "还要说清什么不改。按钮保留青色，说明弱化。这样，修改才有明确的边界。",
    "最后对照前后：标题更突出，其他内容保持。每条意见，都能检查。",
]

def probe(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], text=True).strip())

async def main():
    opening = json.loads((ROOT / "src/concept-timing.json").read_text(encoding="utf-8"))
    opening["start"] = 0
    timeline = [opening]
    start = opening["frames"]
    for i, text in enumerate(TEXTS, 1):
        raw = ROOT / f"public/story-voice-{i}-raw.mp3"
        audio = ROOT / f"public/story-voice-{i}.mp3"
        metadata = ROOT / f"public/story-voice-{i}.jsonl"
        await edge_tts.Communicate(text, "zh-CN-YunxiNeural", rate="+10%", boundary="WordBoundary").save(str(raw), str(metadata))
        tail = 0.25 if i == 1 else 1.0
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", f"apad=pad_dur={tail}", "-c:a", "libmp3lame", "-b:a", "128k", str(audio)], check=True)
        duration = probe(audio)
        boundaries = []
        for line in metadata.read_text(encoding="utf-8").splitlines():
            b = json.loads(line)
            boundaries.append({"text": b["text"], "offset": b["offset"]/10_000_000, "duration": b["duration"]/10_000_000})
        item = {"audio": audio.name, "text": text, "start": start, "frames": math.ceil(duration*30), "duration": duration, "voice": "zh-CN-YunxiNeural", "rate": "+10%", "tailSeconds": tail, "boundaries": boundaries}
        timeline.append(item)
        start += item["frames"]
        print(json.dumps(item, ensure_ascii=True), flush=True)
    (ROOT/"src/story-timing.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Total {start} frames / {start/30:.3f}s")

if __name__ == "__main__":
    asyncio.run(main())
