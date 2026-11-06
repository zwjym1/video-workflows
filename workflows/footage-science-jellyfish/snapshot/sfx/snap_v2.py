# -*- coding: utf-8 -*-
"""v6b：删掉与 c04 同源同构图的 c06_am_rise（审片三次都说「两条差不多的白线」），c05 起飞镜延到 ~1.4 s，c06b 6.186 起。
v6 切点：同 snap_v1（口播锚字起点吸附 BGM 强拍，画面领先 ≤0.28 s / 落后 ≤0.06 s），改动：
c05 压到 ~1 s；新增 c06b_cc_ty（央视·太原网友拍摄，配「从太原起飞」）；北京/山西/山东三镜锚到实测地名起音（口播已在地名间加停顿），
且北京、山西镜头各 ≥0.9 s。BGM 与入点用环境变量 BGM / BGM_OFF 指定，输出 OUT（默认 cuts_v2.json + remotion cuts_v1.ts）。"""
import json, os
from pathlib import Path
R=Path(__file__).resolve().parent.parent
cards=json.load(open(R/'vo/cards_master.json'))
BGM=os.environ.get('BGM', str(R/'audio/bgm/02_一切都在变好（生命力BGM）.mp3')); BGM_OFF=float(os.environ.get('BGM_OFF','0.5'))
OUT=os.environ.get('OUT', str(R/'sfx/cuts_v2.json')); WRITE_TS=os.environ.get('WRITE_TS','1')=='1'
sb=json.load(open(BGM[:-4]+'.strong_beat.json'))
LAG=float(os.environ.get('BEAT_LAG','0.045'))  # 抖音强拍时间比实际可闻起音早 ~40–60 ms（librosa 实测），切点对齐可闻起音
beats=sorted(set(round(x-BGM_OFF+LAG,3) for x in sb['onsets_easy']+sb['onsets_hard'] if x-BGM_OFF>0))
def at(ci,ch=None,n=1):
    c=cards[ci]
    if ch is None: return c['chars'][0][1]
    k=0
    for x in c['chars']:
        if x[0]==ch:
            k+=1
            if k==n: return x[1]
    raise KeyError((ci,ch))
ONSET={'bj':7.66,'sx':8.51,'sd':9.46}   # vo_v4.wav 实测起音
SHOTS=[('c01_am_open',0.0),('c02_jn_city',at(0,'为')),('c03_jn_ufo',at(1)),('c04_am_rocket',at(1,'是',2)),
 ('c05_cc_lift',at(2)),('c06b_cc_ty',at(2,'长')),('c07_cc_bj',ONSET['bj']),('c08_tl_sx',ONSET['sx']),('c09_jn_sd',ONSET['sd']),
 ('c10_tl_climb',at(4)),('d1_shadow',at(5)),('c11_ws_lit',at(7)),('c12_ws_why',at(8)),('d2_plume',at(9)),
 ('c13_am_burst',at(11)),('c14_ws_ice',at(12)),('c15_am_jelly',at(13)),('c16_tl_campus',at(14)),('c17_ws_clear',at(15)),
 ('c18_ws_empty',at(16)),('c19_jn_end',at(17))]
# c04 保持 v5 的 3.61（UFO 打叉动画要在 c03 内播完）；c05 推后一拍到 4.769、只留 2 拍 ~0.93 s（仅对当前 BGM 有效）
FORCE={'c04_am_rocket':3.61,'c05_cc_lift':4.6,'c06b_cc_ty':6.186} if 'BGM' not in os.environ or '一切都在变好' in BGM else {}
out=[];log=[]
for n,t in SHOTS:
    if t<=0: out.append((n,0.0)); continue
    t0=t-0.05
    cand=[b for b in beats if -0.28<=b-t0<=0.11]  # 画面最多落后口播 0.06 s
    s=min(cand,key=lambda b:abs(b-t0)) if cand else t0
    if n in FORCE: s=FORCE[n]
    out.append((n,round(s,3))); log.append(f'{n}: 字{t:.3f} → 切{s:.3f} {"强拍" if cand else "无拍"}')
TOTAL=round(json.load(open(R/'vo/vo_v4.meta.json'))['total_s']+0.6,3)
d=[(out[i][0],round((out[i+1][1] if i+1<len(out) else TOTAL)-out[i][1],3)) for i in range(len(out))]
json.dump(dict(cuts=out,total=TOTAL,bgm_off=BGM_OFF,bgm=BGM),open(OUT,'w'),ensure_ascii=False,indent=1)
if WRITE_TS:
    (R/'remotion/src/data/cuts_v1.ts').write_text('// 由 sfx/snap_v2.py 生成\nexport const NAMES = '+json.dumps([n for n,_ in out])+';\nexport const CUTS = '+json.dumps([s for _,s in out])+f';\nexport const TOTAL = {TOTAL};\nexport const BGM_OFF = {BGM_OFF};\n')
print('\n'.join(log)); print('TOTAL',TOTAL); print('dur', [x for x in d if x[0][:3] in ('c04','c05','c06','c07','c08','c09','c10')])
