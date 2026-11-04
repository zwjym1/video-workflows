#!/usr/bin/env python3
"""画面填满度质检：非背景像素占比 + 边缘能量，每 10s 分段。
用法: python3 qc_density.py <video> [--fps 2] [--w 480]
阈值: occupancy >= 0.25, edge >= 6.0
"""
import subprocess, sys, json

def probe(p):
    o = subprocess.run(['ffprobe','-v','error','-select_streams','v:0',
        '-show_entries','stream=width,height','-of','json',p],capture_output=True,text=True).stdout
    s = json.loads(o)['streams'][0]
    return int(s['width']), int(s['height'])

def load(p, fps, w):
    W,H = probe(p); h = int(w*H/W)//2*2
    raw = subprocess.run(['ffmpeg','-v','error','-i',p,'-vf',
        f'fps={fps},scale={w}:{h},format=gray','-f','rawvideo','-'],capture_output=True).stdout
    n = len(raw)//(w*h)
    return memoryview(raw)[:n*w*h], n, h, w

def score(raw, n, h, w):
    import numpy as np
    F = np.frombuffer(bytes(raw), dtype=np.uint8).reshape(n,h,w).astype(np.float32)
    edge = float((np.abs(np.diff(F,axis=2)).mean() + np.abs(np.diff(F,axis=1)).mean())/2)
    occ = []
    for f in F:
        med = np.median(f)
        occ.append(float(np.mean(np.abs(f-med) > 12)))
    return edge, float(np.mean(occ)), F

def main():
    p = sys.argv[1]
    fps = int(sys.argv[sys.argv.index('--fps')+1]) if '--fps' in sys.argv else 2
    w = int(sys.argv[sys.argv.index('--w')+1]) if '--w' in sys.argv else 480
    raw,n,h,w = load(p,fps,w)
    edge, occ, F = score(raw,n,h,w)
    import numpy as np
    print(f"file: {p}")
    print(f"occupancy(非背景像素占比): {occ:.3f}   阈值 0.25   {'PASS' if occ>=0.25 else 'FAIL'}")
    print(f"edge(边缘能量):            {edge:.2f}   阈值 6.0    {'PASS' if edge>=6.0 else 'FAIL'}")
    print("每 20 秒分段:")
    seg = fps*20
    for i in range(0, n, seg):
        blk = F[i:i+seg]
        if len(blk)<2: break
        e = float((np.abs(np.diff(blk,axis=2)).mean()+np.abs(np.diff(blk,axis=1)).mean())/2)
        o = float(np.mean([np.mean(np.abs(f-np.median(f))>12) for f in blk]))
        flag = '' if (o>=0.25 and e>=6.0) else '  <-- 不达标'
        print(f"  {i/fps:6.1f}s  occ={o:.3f} edge={e:5.2f}{flag}")

if __name__ == '__main__':
    main()
