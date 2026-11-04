#!/usr/bin/env python3
"""丝滑度 QC：针对连续动画（非硬切像素风）。
指标：
  static_rate  相邻帧几乎不变的比例（mean|Δ| < 0.35/255）
  diff_min/med 逐帧差的最小/中位（0 = 完全静止）
  jitter       帧差的变异系数（std/mean），越低越平顺
  beat_hit     帧差局部极大值落在拍点 ±3 帧内的比例
"""
import sys, subprocess
import numpy as np
W,H,FPS = 480,270,60.0
BPM=120.0; OFFSET=0.03
PERIOD=60.0/BPM

def load(path):
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-vf',f'fps={FPS},scale={W}:{H},format=gray',
                        '-f','rawvideo','-'],capture_output=True).stdout
    n=len(raw)//(W*H)
    return np.frombuffer(raw[:n*W*H],dtype=np.uint8).reshape(n,H,W).astype(np.float32)

def main():
    path=sys.argv[1]
    F=load(path)
    d=np.abs(np.diff(F,axis=0)).mean(axis=(1,2))
    static=(d<0.35).mean()
    jitter=d.std()/max(d.mean(),1e-6)
    # 局部极大 -> 动作事件
    ev=[]
    for i in range(2,len(d)-2):
        seg=d[i-2:i+3]
        if d[i]==seg.max() and d[i]>d.mean()*0.6:
            if not ev or i-ev[-1]>3: ev.append(i)
    # 拍点帧
    beats=[]
    k=0
    while True:
        f=(OFFSET+k*PERIOD)*FPS
        if f>len(d): break
        beats.append(f); k+=1
    hit=sum(1 for e in ev if min(abs(e-b) for b in beats)<=3)
    print(f"file        : {path}")
    print(f"frames      : {len(F)} @ {FPS:g}fps  ({len(F)/FPS:.2f}s)")
    print(f"diff min/med/max : {d.min():.3f} / {np.median(d):.3f} / {d.max():.3f}")
    print(f"static_rate : {static*100:.2f}%   (阈值 mean|Δ|<0.35)")
    print(f"jitter      : {jitter:.2f}")
    print(f"motion events: {len(ev)}  ({len(ev)/(len(F)/FPS):.2f}/s)")
    print(f"beat_hit    : {hit}/{len(ev)} = {100*hit/max(len(ev),1):.1f}%  (±3 frames of {BPM:g}BPM grid)")

if __name__=='__main__': main()
