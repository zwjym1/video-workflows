# -*- coding: utf-8 -*-
"""cards_master.json → remotion/src/data/subs_v1.ts：一句一屏；>13 字的句子在逗号处拆成两屏（时间取 Fish 字级时间戳）。"""
import json,re
from pathlib import Path
R=Path(__file__).resolve().parent.parent
c=json.load(open(R/'vo/cards_master.json'))
norm=lambda t: re.sub(r'[^\u4e00-\u9fff0-9A-Za-z]','',t)
segs=[]
for x in c:
    st=[s for s in re.split('[，]',x['text'].rstrip('。')) if s]
    D={'10月23号':'十月二十三号','UFO':'UFO'}
    def tl(s):
        for a,b in D.items(): s=s.replace(a,b)
        return len(norm(s))
    tt=st; assert sum(tl(s) for s in st)==len(norm(x['tts'])),(st,x['tts'])
    if len(norm(x['text']))<=13 or len(st)==1: groups=[(x['text'].rstrip('，。'),len(norm(x['tts'])))]
    else:
        L=[len(norm(s)) for s in st]; best=min(range(1,len(st)),key=lambda k:abs(sum(L[:k])-sum(L[k:])))
        groups=[('，'.join(st[:best]),sum(tl(s) for s in tt[:best])),('，'.join(st[best:]),sum(tl(s) for s in tt[best:]))]
    k=0
    for txt,n in groups:
        ch=x['chars'][k:k+n]; k+=n
        segs.append(dict(text=txt.replace('，',' ').replace('“','「').replace('”','」'),a=ch[0][1],b=ch[-1][2]))
for i,s in enumerate(segs):
    nb=segs[i+1]['a'] if i+1<len(segs) else s['b']+0.8
    s['show_a']=0.0 if i==0 else round(s['a']-0.05,3); s['show_b']=round(nb-0.05,3)
(R/'remotion/src/data/subs_v1.ts').write_text('// 由 vo/build_subs.py 生成（Fish 字级时间戳，提前 0.05 s 出字）\nimport type {Sub} from "../common/OneLineSubtitles";\nexport const SUBS: Sub[] = '+json.dumps(segs,ensure_ascii=False,indent=0)+';\n')
json.dump(segs,open(R/'vo/subs_v1.json','w'),ensure_ascii=False,indent=1)
for s in segs: print(s['show_a'],s['show_b'],s['text'])
