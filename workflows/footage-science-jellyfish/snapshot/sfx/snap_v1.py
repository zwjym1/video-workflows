# -*- coding: utf-8 -*-
"""切点 = 口播锚字起点，吸附 BGM 强拍（画面只许领先口播 ≤0.33 s/往后不超过 0.06 s，避免画面落后口播）。
BGM：一切都在变好（生命力BGM），从曲内 BGM_OFF 秒起播（曲中 45 s 的 break 落在「少一样…什么也没有」）。"""
import json
from pathlib import Path
R=Path(__file__).resolve().parent.parent
cards=json.load(open(R/'vo/cards_master.json'))
BGM_OFF=0.50
sb=json.load(open(R/'audio/bgm/02_一切都在变好（生命力BGM）.strong_beat.json'))
beats=sorted(set(round(x-BGM_OFF,3) for x in sb['onsets_easy']+sb['onsets_hard'] if x-BGM_OFF>0))
def at(ci,ch=None,n=1):
    c=cards[ci]
    if ch is None: return c['chars'][0][1]
    k=0
    for x in c['chars']:
        if x[0]==ch:
            k+=1
            if k==n: return x[1]
    raise KeyError((ci,ch))
SHOTS=[('c01_am_open',0.0),('c02_jn_city',at(0,'为')),('c03_jn_ufo',at(1)),('c04_am_rocket',at(1,'是',2)),
 ('c05_cc_lift',at(2)),('c06_am_rise',at(2,'从')),('c07_cc_bj',at(3)),('c08_tl_sx',at(3,'山')),('c09_jn_sd',at(3,'山',2)),
 ('c10_tl_climb',at(4)),('d1_shadow',at(5)),('c11_ws_lit',at(7)),('c12_ws_why',at(8)),('d2_plume',at(9)),
 ('c13_am_burst',at(11)),('c14_ws_ice',at(12)),('c15_am_jelly',at(13)),('c16_tl_campus',at(14)),('c17_ws_clear',at(15)),
 ('c18_ws_empty',at(16)),('c19_jn_end',at(17))]
out=[];log=[]
for n,t in SHOTS:
    if t<=0: out.append((n,0.0)); continue
    t0=t-0.05  # 画面略领先口播
    cand=[b for b in beats if -0.28<=b-t0<=0.06]
    s=min(cand,key=lambda b:abs(b-t0)) if cand else t0
    out.append((n,round(s,3))); log.append(f'{n}: 字{t:.3f} → 切{s:.3f} {"强拍" if cand else "无拍"}')
TOTAL=round(json.load(open(R/'vo/vo_v1.meta.json'))['total_s']+0.6,3)
ts=R/'remotion/src/data/cuts_v1.ts'
ts.write_text('// 由 sfx/snap_v1.py 生成\nexport const NAMES = '+json.dumps([n for n,_ in out])+';\nexport const CUTS = '+json.dumps([s for _,s in out])+f';\nexport const TOTAL = {TOTAL};\nexport const BGM_OFF = {BGM_OFF};\n')
json.dump(dict(cuts=out,total=TOTAL,bgm_off=BGM_OFF),open(R/'sfx/cuts_v1.json','w'),ensure_ascii=False,indent=1)
print('\n'.join(log)); print('TOTAL',TOTAL)
