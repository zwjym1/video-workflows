#!/usr/bin/env python3
"""动作事件密度质检 —— 与 STYLE_RESEARCH.md §0 完全同口径
（256×144 灰度 @ 8fps，帧差曲线的局部极大值 >1.2 且高于前后各 2 个采样点，计数 ÷ 时长）

用法：
  python3 qc_action.py a.mp4 [b.mp4 ...] [--start 40 --dur 10]
"""
import sys, json, subprocess, argparse
import numpy as np

W, H, FPS = 256, 144, 8.0

def load(path, start=0.0, dur=None):
    cmd = ['ffmpeg','-v','error']
    if start: cmd += ['-ss', str(start)]
    if dur: cmd += ['-t', str(dur)]
    cmd += ['-i', path, '-vf', f'fps={FPS},scale={W}:{H},format=gray', '-f','rawvideo','-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = len(raw) // (W*H)
    return np.frombuffer(raw[:n*W*H], dtype=np.uint8).reshape(n, H, W).astype(np.float32)

def events(F, thr=1.2, win=2):
    d = np.abs(np.diff(F, axis=0)).mean(axis=(1,2))     # 每 1/8 s 一个值
    pk = []
    for i in range(len(d)):
        lo, hi = max(0, i-win), min(len(d), i+win+1)
        neigh = np.delete(d[lo:hi], i-lo)
        if d[i] > thr and d[i] >= neigh.max():
            pk.append(i)
    # 0.15s（≈1 采样）内合并
    merged = []
    for i in pk:
        if merged and i - merged[-1] <= 1: continue
        merged.append(i)
    return d, merged

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('videos', nargs='+')
    ap.add_argument('--start', type=float, default=0.0)
    ap.add_argument('--dur', type=float, default=None)
    ap.add_argument('--thr', type=float, default=1.2)
    a = ap.parse_args()
    for v in a.videos:
        F = load(v, a.start, a.dur)
        d, pk = events(F, a.thr)
        seconds = (len(F)-1)/FPS
        print(json.dumps({
            'video': v.split('/')[-1], 'start': a.start, 'dur': round(seconds,2),
            'events': len(pk), 'events_per_s': round(len(pk)/seconds, 2),
            'diff_mean': round(float(d.mean()),2), 'diff_p95': round(float(np.percentile(d,95)),2),
            'still_ratio': round(float((d<0.6).mean()),3),
        }, ensure_ascii=False))

if __name__ == '__main__': main()
