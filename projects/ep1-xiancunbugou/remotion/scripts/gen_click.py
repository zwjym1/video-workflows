#!/usr/bin/env python3
"""生成占位节拍轨：112 BPM，16 小节 4/4，干净 click。
   第 1 拍重音（1000Hz），其余拍 1500Hz 短促 —— 便于 librosa 稳定检测。
   用法：python3 scripts/gen_click.py [out.wav] [bpm] [bars]"""
import sys, numpy as np
from scipy.io import wavfile

out = sys.argv[1] if len(sys.argv) > 1 else 'public/bgm/placeholder_112.wav'
BPM = float(sys.argv[2]) if len(sys.argv) > 2 else 112.0
BARS = int(sys.argv[3]) if len(sys.argv) > 3 else 16
SR = 44100
SPB = 60.0 / BPM                      # seconds per beat
N = int(round(BARS * 4 * SPB * SR))
buf = np.zeros(N, dtype=np.float64)

def click(t0, freq, amp, dur=0.045, decay=90.0):
    i0 = int(round(t0 * SR)); n = int(dur * SR)
    if i0 >= N: return
    n = min(n, N - i0)
    t = np.arange(n) / SR
    # 短促正弦 + 指数包络 + 极小噪声起音，避免纯正弦被 librosa 判成谐波
    env = np.exp(-decay * t)
    sig = np.sin(2 * np.pi * freq * t) * env * amp
    sig[:24] += (np.random.default_rng(int(t0 * 1000)).random(24) - 0.5) * 0.06 * amp
    buf[i0:i0 + n] += sig

beats = []
for bar in range(BARS):
    for b in range(4):
        t0 = (bar * 4 + b) * SPB
        beats.append(round(t0, 6))
        if b == 0: click(t0, 1000.0, 0.85)          # 小节首拍重音
        elif b == 2: click(t0, 1500.0, 0.55)        # 次强
        else: click(t0, 1500.0, 0.40)

# 归一化到 -3 dBFS 附近
peak = np.abs(buf).max()
if peak > 0: buf = buf / peak * 0.70
wavfile.write(out, SR, (buf * 32767).astype(np.int16))
print(f"{out}: {BARS} bars, {BPM} BPM, {len(beats)} beats, {N/SR:.3f}s")
