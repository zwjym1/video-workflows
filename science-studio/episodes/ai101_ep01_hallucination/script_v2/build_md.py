import re,json
from lines_v2 import L,SILENT
BEAT=60/117.5
def clean(t):return re.sub(r'^\[[^\]]*\]\s*','',t)
def nch(t):return len(re.sub(r'[\s,，。！？!?、:：;；"“”—…（）()+]','',t))
rows=[];t=0;shots={}
items=[(s,None) for s in SILENT]+[(l[0],l) for l in L]
items.sort(key=lambda x:(x[0],0 if x[1] is None else 1))
order=[]
for s,l in items:
    if l is None:
        d=SILENT[s];rows.append(dict(shot=s,who='—',text='（无台词）',tag='',emo='',stress='',cps='',pause=0,dur=d,t0=t,act='缓冲/片尾',sfx='',pic=''));t+=d
    else:
        s,who,text,tag,emo,stress,cps,pause,act,sfx,pic=l;text=clean(text);d=nch(text)/cps
        rows.append(dict(shot=s,who=who,text=text,tag=tag,emo=emo,stress=stress,cps=cps,pause=pause,dur=round(d,2),t0=t,act=act,sfx=sfx,pic=pic,tts=tag+' '+text));t+=d+pause
total=t
def mmss(x):return f'{int(x//60)}:{x%60:04.1f}'
# shot table
S={}
for r in rows:
    S.setdefault(r['shot'],dict(t0=r['t0'],lines=[],pic=r['pic']));S[r['shot']]['lines'].append(r)
json.dump(rows,open('lines_v2.json','w'),ensure_ascii=False,indent=1)
json.dump(dict(total=total),open('total.json','w'))
out=[]
out.append('| # | 镜 | 时间 | 角色 | 台词（字幕） | Fish 标签 | 语气/情绪 | 重音 | 字/s | 句后停顿 | 动作/姿态 | 切点·拍 | 音效 |')
out.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
prev=None
for i,r in enumerate(rows,1):
    cut='' 
    if r['shot']!=prev:
        b=round(r['t0']/BEAT);cut=f"切@{mmss(r['t0'])}→拍{b}（{b*BEAT:.2f}s）"
    prev=r['shot']
    out.append(f"| {i} | {r['shot']} | {mmss(r['t0'])}–{mmss(r['t0']+r['dur'])} | {r['who']} | {r['text']} | `{r['tag']}` | {r['emo']} | **{r['stress']}** | {r['cps']} | {r['pause']} | {r['act']} | {cut} | {r['sfx']} |")
open('table_lines.md','w').write('\n'.join(out))
# review table
o2=['| 镜号 | 时长(累计) | 画面 | 台词 | 录屏? | 过关 |','|---|---|---|---|---|---|']
open('shots.json','w').write(json.dumps({k:dict(t0=v['t0'],dur=sum(x['dur']+x['pause'] for x in v['lines']),pic=v['pic'],who=[x['who'] for x in v['lines']]) for k,v in S.items()},ensure_ascii=False))
print('total',round(total,1),mmss(total),'lines',len(rows),'chars',sum(nch(r['text']) for r in rows if r['who']!='—'))
