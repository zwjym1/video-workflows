#!/usr/bin/env python3
"""Mix VO + quiet bed + (on 1x watches only) ducked source stadium/commentary."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TL = json.loads((ROOT / "src/timeline.json").read_text())
DUR = sum(s["n_out"] for s in TL["segments"]) / TL["fps_out"]
OUT = ROOT / "audio/mix.wav"
VOICE = ROOT / "audio/voice"
BED = ROOT / "audio/bgm/bed.wav"
STAD = ROOT / "src/clips/audio/wide_62176_62900.wav"
TMP = ROOT / "audio/_mixbuild"
TMP.mkdir(parents=True, exist_ok=True)

# voice start times already in timeline
# Build a filter: anullsrc base, adelay each VO, amix, sidechain-ish bed dip via volume keyframes

def dur_of(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        text=True,
    ).strip()
    return float(out)

# Decode VOs to wav
inputs = ["-f", "lavfi", "-t", f"{DUR:.4f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
# 0: silence
inputs += ["-i", str(BED)]  # 1
# voice files 2..
vmeta = []
for i, v in enumerate(TL["voice"]):
    vp = ROOT / v["file"]
    inputs += ["-i", str(vp)]
    vmeta.append((2 + i, v["start"], dur_of(vp), v["id"]))
# source stadium:  last input
stad_i = 2 + len(vmeta)
inputs += ["-i", str(STAD)]

# volume keyframes for bed: default 0.16, dip to 0.07 under VO (+0.15s pad)
# volume env as volume=...:eval=frame:volume='...'
# Use sidechaincompress if available, else keyframes.

def dips():
    pts = []
    for _, start, d, _ in vmeta:
        pts.append((max(0, start - 0.12), 0.16))
        pts.append((start, 0.07))
        pts.append((start + d, 0.07))
        pts.append((start + d + 0.35, 0.16))
    # fade out last 2.2s
    pts.append((DUR - 2.2, 0.16))
    pts.append((DUR, 0.0))
    return pts

# ffmpeg volume expression with ifs is messy; use a volume csv via aeval or send a sidechain.
# Simpler: generate a volume automation wav? Even simpler: use alimiter / acrossfade chains.
# I'll build bed volume with a python envelope wav (mono) and multiply.

import numpy as np, wave
sr = 44100
n = int(round(DUR * sr))
env = np.full(n, 0.16, dtype=np.float64)
for _, start, d, _ in vmeta:
    a = int(max(0, (start - 0.12) * sr))
    b = int(start * sr)
    c = int((start + d) * sr)
    e = int(min(n, (start + d + 0.35) * sr))
    if b > a:
        env[a:b] = np.linspace(env[a] if a < n else 0.16, 0.07, b - a)
    env[b:c] = 0.07
    if e > c:
        env[c:e] = np.linspace(0.07, 0.16, e - c)
# end fade
f0 = int((DUR - 2.2) * sr)
env[f0:] = np.linspace(env[f0] if f0 < n else 0.16, 0.0, n - f0)
# write env as a 1-ch wav 0-1 scaled to 0.5 mid so we can use it? We'll apply in numpy after ffmpeg concat of VO.

# Approach rewrite: mix in python after decoding everything to pcm. Cleaner.
print("mixing in numpy, duration", DUR)

def read_wav_ffmpeg(path, start=0.0, duration=None, atempo=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.4f}", "-i", str(path)]
    if duration is not None:
        cmd += ["-t", f"{duration:.4f}"]
    if atempo:
        cmd += ["-af", f"atempo={atempo}"]
    cmd += ["-ar", str(sr), "-ac", "2", "-f", "f32le", "-"]
    data = subprocess.check_output(cmd)
    arr = np.frombuffer(data, dtype=np.float32)
    if arr.size % 2:
        arr = arr[: arr.size // 2 * 2]
    return arr.reshape(-1, 2)

# bed
bed = read_wav_ffmpeg(BED)
if len(bed) < n:
    bed = np.vstack([bed, np.zeros((n - len(bed), 2), np.float32)])
bed = bed[:n].copy()
bed *= env[: len(bed), None].astype(np.float32)

mix = bed.astype(np.float64)

# voices
for _, start, d, vid in vmeta:
    audio = read_wav_ffmpeg(ROOT / f"audio/voice/{vid}.mp3")
    off = int(round(start * sr))
    end = min(n, off + len(audio))
    mix[off:end] += audio[: end - off] * 1.05

# source stadium on first_watch (8.000-15.267) and play1 (15.267-17.500) and replay (51.333-58.600)
# source wav is 7.28s = frames 0-181 at 1x. first_watch and replay use the full clip.
# play1 is n0=0..55 = 0.00-2.24s of the source (56/25=2.24)
stad = read_wav_ffmpeg(STAD)
# trim/pad to 7.28s already
GAIN = 0.11  # low; mixed English commentary + crowd, not claimed as pure ambience
placements = [
    # (mix_start, src_start, duration)
    (8.000, 0.0, 7.2667),      # first_watch 218f
    (15.267, 0.0, 2.2333),     # play1 67f  (n 0-55)
    (51.333, 0.0, 7.2667),     # replay
]
for ms, ss, dd in placements:
    a = int(round(ms * sr))
    b = int(round(ss * sr))
    k = int(round(dd * sr))
    chunk = stad[b : b + k]
    k = min(k, len(chunk), n - a)
    # short fade 40ms to avoid clicks
    fade = int(0.04 * sr)
    win = np.ones(k, np.float64)
    if k > 2 * fade:
        win[:fade] = np.linspace(0, 1, fade)
        win[-fade:] = np.linspace(1, 0, fade)
    mix[a : a + k] += chunk[:k] * GAIN * win[:, None]

# peak protect
peak = np.max(np.abs(mix))
print("raw peak", float(peak))
if peak > 0.95:
    mix *= 0.95 / peak
    print("limited to 0.95")

pcm = np.clip(mix * 32767, -32768, 32767).astype(np.int16)
OUT.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(OUT), "w") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(pcm.tobytes())
print("wrote", OUT, "seconds", len(pcm) / sr)
