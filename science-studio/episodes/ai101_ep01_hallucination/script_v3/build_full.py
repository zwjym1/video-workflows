import json,sys
EPD='/workspace/science-studio/episodes/ai101_ep01_hallucination'
sys.path.insert(0,EPD+'/script_v3');import cues_full as C
import os
TLP=os.environ.get('TLP',EPD+'/production/full_v2/timeline.json');TL=json.load(open(TLP))
GR=json.load(open(EPD+'/production/full_v2/beat_grid.json'));OFF,PER=GR['offset'],GR['period'];MAXS=float(os.environ.get('MAXS','0.2'));NSNAP=[0,0]
def snap(t,hi=1e9):
    b=OFF+round((t-OFF)/PER)*PER;NSNAP[1]+=1
    if b>hi and t<=hi:b-=PER
    if abs(b-t)<=MAXS:NSNAP[0]+=1;return round(b,3)
    return t
SN={int(k):v for k,v in TL['shots'].items()}
LS={};[LS.setdefault(l['shot'],[]).append(l) for l in TL['lines']]
def base(n,b):
    s=SN[n]
    if b=='s':return s['s0']
    if b=='v':return LS[n][0]['t0'] if n in LS else s['s0']
    if b.startswith('l'):return LS[n][int(b[1:])-1]['t0']
    if b=='v':pass
def R(n,v):
    if isinstance(v,tuple) and len(v)==2 and isinstance(v[0],str) and v[0][0] in 'svl':return round(base(n,v[0])+v[1],3)
    if isinstance(v,dict):return {k:R(n,x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [R(n,x) for x in v]
    return v
OUT={'shots':{},'global':{'counter':[],'sfx':[]}}
for n,s in C.SH.items():
    J={'o':[{'t':(R(n,(b,a)) if (b,a)==('s',0) else snap(R(n,(b,a)))),'pose':p,'note':d} for b,a,p,d in s['o']],
       'fish':[{'t':(R(n,(b,a)) if (b,a)==('s',0) else snap(R(n,(b,a)))),'pose':p,'note':d,**({'jump':True} if s.get('fish_jump') else {})} for b,a,p,d in s['f']],
       'el':[],'tab':s.get('tab'),'react':s.get('react','')}
    for k in('o_layout','stage_zoom','xf','xf_seq','o_shake'):
        if k in s:J[k]=R(n,s[k])
    J['punch']=[snap(R(n,p)) for p in s.get('punch',[])]
    for e in s['el']:
        e=R(n,dict(e));sf=e.pop('sfx',[])
        if True:   # v4：src_tag 也吸附拍点
            hi=SN[n]['s1']-0.35;t2=e['t'] if e.get('nosnap') else snap(min(e['t'],hi),hi);t2=max(t2,SN[n]['s0']) if t2<=hi else t2;d=t2-e['t'];e['t']=t2
            for kk in ('t_draw','r0','r1','tf'):
                if kk in e:e[kk]=round(e[kk]+d,3)
        for nm,g,dt in sf:OUT['global']['sfx'].append({'t':round(e['t']+dt,3),'f':nm,'db':g,'shot':n})
        J['el'].append(e)
    for b,a,nm,g in s.get('sfx',[]):OUT['global']['sfx'].append({'t':snap(R(n,(b,a))),'f':nm,'db':g,'shot':n})
    OUT['shots'][n]=J
for b,n,a,v in C.COUNTER:OUT['global']['counter'].append({'t':snap(R(n,(b,a))),'v':v})
def wtime(li,ch):
    l=TL['lines'][li-1];w=[x for x in l['words'] if ch in x['c']];return w[0]['t0'] if w else l['t0']
OUT['global']['net']=[]
def gap_free(t,d):return all(not(l['t0']-0.02<t+d and l['t1']+0.02>t) for l in TL['lines'])
for k in C.NET:
    n=k['shot'];at=k['at']
    t=wtime(at[1],at[2]) if at[0]=='w' else R(n,at)
    b=OFF+round((t-OFF)/PER)*PER;t=round(b if abs(b-t)<=k['snap'] else t,3)
    K=dict(k['kinds']);rec=dict(t=t,shot=n,desc=k['desc'],kinds=sorted(K))
    if 'freeze' in K and not gap_free(t,K['freeze']):
        # 往前找无人声空隙
        t2=max(l['t1'] for l in TL['lines'] if l['t1']<=t+0.3)+0.03
        if gap_free(t2,K['freeze']):t=rec['t']=round(t2,3)
        else:K.pop('freeze');rec['kinds']=sorted(K);rec['note']='定格取消：无空隙'
    for a,b2,dt in K.get('sfx',[]):OUT['global']['sfx'].append({'t':round(t+dt,3),'f':a,'db':b2,'shot':n,'net':k['desc']})
    if 'push' in K:OUT['shots'][n]['punch'].append(t)
    if 'sticker' in K:
        st=K['sticker'];OUT['shots'][n]['el'].append(dict(t=t,k='card',text=st['text'],size=46,bg=st['bg'],fg=(255,255,255) if st['bg']!=(255,214,64) else (34,30,48),x=st['x'],y=st['y'],rot=st['rot'],anim='pop',until=round(t+1.4,3),top=True,net='sticker'))
    rec.update({x:K[x] for x in ('shake','freeze','duck','accent') if x in K});OUT['global']['net'].append(rec)
OUT['global']['sfx'].sort(key=lambda x:x['t'])
json.dump(OUT,open(EPD+'/script_v3/shots_v3.json','w'),ensure_ascii=False,indent=1)
# ---- MD ----
REC={32:'是·实测原文回放（2026-11-03 qodercn 未联网）',33:'是·实测原文回放 + 北京日报截图',36:'是·实测原文（Qwen 两次回答）',37:'是·OSM 真实地图测距',48:'演示 mock（标「演示」）'}
def fm(t):return f'{int(t//60):02d}:{t%60:05.2f}'
def desc(e):
    k=e['k'];w=e.get('text') or e.get('src') or e.get('name') or e.get('title') or e.get('label') or ''
    if k=='term':w=e['title']+(' 高亮「'+'」「'.join(h['s'] for h in e.get('hl',[]))+'」' if e.get('hl') else '')
    if k=='roll':w=f"{e['a']}→{e['b']}"
    if k=='phone':w='搜 '+' / '.join(q['q']+('✓' if q['ok'] else '✗') for q in e['seq'])
    if k=='merge':w='+'.join(e['words'])
    if k=='ruler_map':w=f"{e['a']}→{e['b']} {e['label']}"
    return f"{k}「{w}」@({e.get('x','')},{e.get('y','')}) {e.get('anim','pop') if k not in('fx','src_tag') else ''}"
L=['# 第1期 · 逐镜精确时间轴（全片 50 镜，v3 自动生成）','',f'> 由 cues_full.py + production/full_v1/timeline.json 生成；画面元素、音效、计数器全部写进 shots_v3.json，picture.py/final.py 直接读取。全片 {TL["dur"]:.2f}s。',
 '> 声线：O=ebea2d…（speed 1.35）、鱼=9510b5…（speed 1.3，[playful]）；逐句单生成+O 音高闸门。BGM 117.5BPM，拍长 0.511s。','']
for n in sorted(OUT['shots']):
    J=OUT['shots'][n];s=SN[n]
    L+=[f"## 镜 {n}  {fm(s['s0'])} – {fm(s['s1'])}（{s['s1']-s['s0']:.2f}s）{'  【无台词缓冲】' if s.get('silent') else ''}  {('｜'+J['tab']) if J['tab'] else ''}",'']
    for l in LS.get(n,[]):L.append(f"- **{'O' if l['who']=='O' else '大肥鱼'}** {fm(l['t0'])}–{fm(l['t1'])}：{l['text']}（seed {l.get('seed')}）")
    L.append('- 姿势：O '+' → '.join(f"{fm(o['t'])} {o['pose']}（{o['note']}）" for o in J['o'])+('；鱼 '+' → '.join(f"{fm(o['t'])} {o['pose']}（{o['note']}）" for o in J['fish']) if J['fish'] else '；鱼 不在场'))
    L.append(f"- 反应：{J['react']}")
    for e in sorted(J['el'],key=lambda e:e['t']):L.append(f"  - {fm(e['t'])} {desc(e)}")
    sf=[x for x in OUT['global']['sfx'] if x['shot']==n]
    if sf:L.append('- 音效：'+'；'.join(f"{fm(x['t'])} {x['f'].split('/')[-1]} {x['db']}dB" for x in sf))
    if J['punch']:L.append('- 推镜：'+'、'.join(fm(p) for p in J['punch']))
    L.append('')
L+=['## 审核表','','| 镜 | 时间 | 台词（首句） | 过关 | 录屏? |','|---|---|---|---|---|']
for n in sorted(OUT['shots']):
    s=SN[n];t=(LS[n][0]['text'][:22]+'…') if n in LS else '（无台词）'
    L.append(f"| {n} | {fm(s['s0'])}–{fm(s['s1'])} | {t} | ☐ | {REC.get(n,'')} |")
open(EPD+'/script_v3/script_tzs_v3.md','w').write('\n'.join(L)+'\n')
print('snap',NSNAP);print(len(OUT['shots']),len(OUT['global']['sfx']),OUT['global']['counter'])
