#!/usr/bin/env python3
"""Generate 原创近似音效: independent production assets, not extracted from the reference mix."""
from pathlib import Path
import numpy as np
import soundfile as sf

SR = 44100
OUT = Path("/workspace/football-demo/full-phase-new-reference/audio-analysis/sfx_original_approx")
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(20261116)


def fade(n, a, b):
    env = np.ones(n, dtype=np.float64)
    na, nb = int(a * n), int(b * n)
    if na > 0:
        env[:na] *= np.linspace(0, 1, na, endpoint=True)
    if nb > 0:
        env[-nb:] *= np.linspace(1, 0, nb, endpoint=True)
    return env


def lowpass(x, cutoff, sr=SR, order=2):
    # simple one-pole cascade, zero-phase-ish by forward-back
    if cutoff >= sr / 2:
        return x
    a = np.exp(-2 * np.pi * cutoff / sr)
    y = np.copy(x)
    acc = 0.0
    for _ in range(order):
        acc = 0.0
        for i in range(len(y)):
            acc = (1 - a) * y[i] + a * acc
            y[i] = acc
        acc = 0.0
        for i in range(len(y) - 1, -1, -1):
            acc = (1 - a) * y[i] + a * acc
            y[i] = acc
    return y


def highpass(x, cutoff, sr=SR):
    # x - lowpass
    return x - lowpass(x, cutoff, sr, order=2)


def bandpass(x, lo, hi, sr=SR):
    return highpass(lowpass(x, hi, sr, order=2), lo, sr)


def normalize(x, peak_db=-14.0):
    peak = np.max(np.abs(x)) + 1e-12
    target = 10 ** (peak_db / 20)
    return (x / peak) * target


def stereo(x, width=0.12):
    # slight mid/side width, still mono-compatible
    n = len(x)
    delay = int(0.0004 * SR)
    r = np.zeros_like(x)
    r[delay:] = x[:-delay]
    mid = 0.5 * (x + r)
    side = 0.5 * (x - r) * width
    L = mid + side
    R = mid - side
    return np.stack([L, R], axis=1)


def write(name, x, meta):
    y = stereo(x)
    path = OUT / name
    sf.write(str(path), y, SR, subtype="PCM_16")
    peak = float(np.max(np.abs(y)))
    rms = float(np.sqrt(np.mean(y ** 2)))
    meta.update({
        "path": str(path),
        "sr": SR,
        "channels": 2,
        "duration_s": len(y) / SR,
        "peak_dbfs": 20 * np.log10(peak + 1e-12),
        "rms_dbfs": 20 * np.log10(rms + 1e-12),
        "source": "原创近似音效（合成，非参考片抽段）",
    })
    print(name, f"dur={meta['duration_s']:.3f}s peak={meta['peak_dbfs']:.1f} rms={meta['rms_dbfs']:.1f}")
    return meta


# 1) short muted low cut-hit, ~80ms body in 200ms file
n = int(0.200 * SR)
t = np.arange(n) / SR
hit = (
    0.85 * np.sin(2 * np.pi * 92 * t) * np.exp(-t / 0.028)
    + 0.45 * np.sin(2 * np.pi * 138 * t) * np.exp(-t / 0.018)
    + 0.18 * np.sin(2 * np.pi * 55 * t) * np.exp(-t / 0.040)
    + 0.22 * lowpass(rng.normal(0, 1, n), 450) * np.exp(-t / 0.012)
)
hit *= fade(n, 0.02, 0.35)
m1 = write("cut_hit_low_muted.wav", normalize(hit, -14), {
    "id": "cut_hit_low_muted",
    "type": "硬切低频顿点",
    "design": "80–140Hz 阻尼正弦 + 短促低频噪声，约80ms有效体，峰值-14 dBFS",
})

# 2) soft UI tick, ~50ms in 160ms file
n = int(0.160 * SR)
t = np.arange(n) / SR
# tiny transient + faint high click, no long ring
click = (
    0.7 * highpass(rng.normal(0, 1, n) * np.exp(-t / 0.004), 1800)
    + 0.25 * np.sin(2 * np.pi * 3200 * t) * np.exp(-t / 0.006)
    + 0.12 * np.sin(2 * np.pi * 2100 * t) * np.exp(-t / 0.008)
)
click *= fade(n, 0.01, 0.55)
m2 = write("ui_tick_soft.wav", normalize(click, -16), {
    "id": "ui_tick_soft",
    "type": "轻UI提示音",
    "design": "2–3kHz 短点击，约40–60ms，峰值-16 dBFS，避免长余响",
})

# 3) short line/route whoosh, ~180ms in 280ms file
n = int(0.280 * SR)
t = np.arange(n) / SR
noise = rng.normal(0, 1, n)
# rising then falling bandpass center
cen = 500 + 2800 * np.sin(np.pi * np.clip(t / 0.200, 0, 1)) ** 1.2
who = np.zeros(n)
# piecewise bandpass in hops
hop = 64
for i in range(0, n, hop):
    sl = slice(i, min(n, i + hop * 2))
    c = float(cen[i])
    who[sl] += bandpass(noise[sl], max(200, c * 0.5), min(8000, c * 1.8))
who = who / (np.max(np.abs(who)) + 1e-12)
env = np.sin(np.pi * np.clip(t / 0.220, 0, 1)) ** 1.1
who *= env
# very slight pitchy air, not musical
air = highpass(rng.normal(0, 1, n), 2500) * env * 0.15
whoosh = who * 0.9 + air
m3 = write("whoosh_line_short.wav", normalize(whoosh, -18), {
    "id": "whoosh_line_short",
    "type": "短促路线/画线气流",
    "design": "带通噪声扫频约180–220ms，峰值-18 dBFS，比切点和旁白更弱",
})

# 4) soft circle/lock accent, ~90ms in 200ms file
n = int(0.200 * SR)
t = np.arange(n) / SR
lock = (
    0.35 * np.sin(2 * np.pi * 780 * t) * np.exp(-t / 0.035)
    + 0.20 * np.sin(2 * np.pi * 1560 * t) * np.exp(-t / 0.020)
    + 0.28 * highpass(rng.normal(0, 1, n) * np.exp(-t / 0.006), 1200)
)
lock *= fade(n, 0.02, 0.45)
m4 = write("circle_lock_soft.wav", normalize(lock, -17), {
    "id": "circle_lock_soft",
    "type": "轻圈注/锁定提示",
    "design": "中频短促＋极短空气点击，约90ms，峰值-17 dBFS",
})

import json
meta = {
    "disclaimer": "四条均为原创合成近似音效，不是从参考成片抽段，也不是官方授权库素材。",
    "assets": [m1, m2, m3, m4],
}
(OUT / "MANIFEST.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print("WROTE", OUT / "MANIFEST.json")
