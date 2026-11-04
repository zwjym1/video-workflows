#!/usr/bin/env python3
"""把一条 BGM 按我们片子的章节边界切片重排，让每个章节的第一帧都落在音乐的重拍上。

为什么不用整轨铺底：现片章节起点（42.20 / 76.87 / 114.53 …）跟任何 BPM 的网格都对不上，
最好情况平均偏 152ms、最差 242ms，硬铺一条连续轨一定有地方"踩空"。
切片重排是反过来——让音乐服从画面：每一章单独取一段，起点强制选在原曲的小节线，
长度裁到正好等于这一章，接缝落在章节卡的重音上，听不出拼接。

用法：
  python3 bgm_slice.py --track in.wav --plan plan.json --out bed.wav
plan.json: {"fps":30,"bpm":120,"spans":[{"id":"hook","start":0,"end":42.20}, ...]}
"""
import argparse, json, math, subprocess, os, tempfile

def ff(args):
    subprocess.run(['ffmpeg','-y','-v','error']+args, check=True)

def probe_dur(p):
    o=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],
                     capture_output=True,text=True).stdout.strip()
    return float(o)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--track',required=True); ap.add_argument('--plan',required=True)
    ap.add_argument('--out',required=True); ap.add_argument('--sr',type=int,default=48000)
    ap.add_argument('--xfade',type=float,default=0.12,help='接缝交叉淡化秒数，默认 0.12s≈4 帧')
    a=ap.parse_args()
    plan=json.load(open(a.plan,encoding='utf-8'))
    fps=plan.get('fps',30); bpm=plan.get('bpm',120.0)
    bar=60.0/bpm*4
    src_dur=probe_dur(a.track)
    tmp=tempfile.mkdtemp()
    parts=[]; report=[]
    cursor=bar*4          # 从第 4 小节（通常已进主段）开始找素材
    for i,sp in enumerate(plan['spans']):
        need=(sp['end']-sp['start'])
        # 素材起点：>=cursor 的下一个小节线
        k=math.ceil(cursor/bar); take=k*bar
        if take+need > src_dur: take=bar*4          # 素材不够就回绕
        if take+need > src_dur: take=0.0
        cursor=take+need
        outp=os.path.join(tmp,f'p{i:02d}.wav')
        fade=max(0.05, min(a.xfade, need/3))
        ff(['-i',a.track,'-ss',f'{take:.6f}','-t',f'{need:.6f}',
            '-af',f'aresample={a.sr},afade=t=in:st=0:d={fade:.4f},'
                  f'afade=t=out:st={max(0,need-fade):.4f}:d={fade:.4f}',
            '-ar',str(a.sr),'-ac','1','-c:a','pcm_s16le',outp])
        parts.append(outp)
        report.append((sp['id'],round(take,3),round(need,3),round(fade,3)))
    lst=os.path.join(tmp,'list.txt')
    open(lst,'w').write(''.join(f"file '{p}'\n" for p in parts))
    ff(['-f','concat','-safe','0','-i',lst,'-ar',str(a.sr),'-ac','1','-c:a','pcm_s16le',a.out])
    print(f"{'章节':10s}{'素材起点s':>10s}{'本章长s':>9s}{'淡入淡出s':>10s}")
    for r in report: print(f"{r[0]:10s}{r[1]:10.3f}{r[2]:9.3f}{r[3]:10.3f}")
    print(f"\n输出 {a.out}  时长 {probe_dur(a.out):.3f}s  计划 {sum(s['end']-s['start'] for s in plan['spans']):.3f}s")

if __name__=='__main__': main()
