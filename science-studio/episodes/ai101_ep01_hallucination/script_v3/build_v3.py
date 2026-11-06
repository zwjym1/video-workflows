import json,os,sys
sys.path.insert(0,'.');from cues_v3 import SH,VOICE
TLD='../production/trial_v4/';TL=json.load(open(TLD+'timeline.json'))
V2={r['text']:r for r in json.load(open('../script_v2/lines_v2.json')) if r['who']!='—'}
EV=json.load(open(TLD+'sfx_events.json')) if os.path.exists(TLD+'sfx_events.json') else []
BEAT=60/117.5;SHOTS={int(k):v for k,v in TL['shots'].items()}
out={'dur':TL['dur'],'voice':VOICE,'beat':BEAT,'shots':{}}
def R(n,b,x):
    L=[l for l in TL['lines'] if l['shot']==n]
    if b=='s':return SHOTS[n]['s0']+x
    if b=='v':return L[0]['t0']+x
    return L[int(b[1:])-1]['t0']+x
md=['# 第1期《AI 给你推荐的餐馆，可能根本不存在》脚本 v3（镜1–20 样板，逐秒时间轴）','',
'> 内容与 v2 相同（方案A、事实红线不变），只把执行细节写到秒。由 `script_v3/cues_v3.py` + `trial_v4/timeline.json` 生成，渲染读 `script_v3/shots_v3.json`。',
f'> 时间均为成片绝对秒。BGM：阿柠同款，117.5 BPM，1 拍 = {BEAT:.3f}s，平铺比人声低 14 LU。音色：O = `{VOICE["O"]}`，大肥鱼 = `{VOICE["F"]}`（混音前逐句断言）。','']
rev=['## 逐镜审核表','','| 镜 | 时段 | 内容要点 | 过关 | 录屏? | 备注 |','|---|---|---|---|---|---|']
for n in sorted(SH):
    c=SH[n];s0,s1=SHOTS[n]['s0'],SHOTS[n]['s1'];L=[l for l in TL['lines'] if l['shot']==n]
    oc=[dict(t=round(R(n,b,x),3),pose=p,face=e) for b,x,p,e in c['o']]
    fc=[dict(t=round(R(n,b,x),3),pose=p,face=e) for b,x,p,e in (c['f'] or [])]
    el=[dict(t=round(R(n,b,x),3),what=w,where=pos,fx_in=fi,out=fo) for b,x,w,pos,fi,fo in c['el']]
    ln=[dict(idx=l['idx'],who=l['who'],voice=l['reference_id'],t0=l['t0'],t1=l['t1'],text=l['text'],tone=V2[l['text']]['emo'],stress=V2[l['text']]['stress']) for l in L]
    sfx=[dict(t=round(e[0],3),sfx=e[1],db=e[2]) for e in EV if s0<=e[0]<s1]
    import math
    beats=[round(k*BEAT,3) for k in range(math.ceil(s0/BEAT),math.ceil(s1/BEAT))]
    out['shots'][n]=dict(s0=s0,s1=s1,lines=ln,o=oc,fish=fc,react=c['react'],el=el,sfx=sfx,beats=beats)
    md+=[f'## 镜 {n}　{s0:.2f}–{s1:.2f}s（{s1-s0:.2f}s）','','**台词**','','| 时间 | 说话人 / 音色ID | 台词 | 语气 | 重音 |','|---|---|---|---|---|']
    md+=[f"| {x['t0']:.2f}–{x['t1']:.2f} | {'O' if x['who']=='O' else '大肥鱼'} `{x['voice'][:8]}…` | {x['text']} | {x['tone']} | {x['stress']} |" for x in ln]
    md+=['','**角色**','']
    md+=[f"- {x['t']:.2f}s　O → `{x['pose']}`（{x['face']}）" for x in oc]
    md+=[f"- {x['t']:.2f}s　鱼 → `{x['pose']}`（{x['face']}），{'说话时用该姿势专属开口图' if any(l['who']=='F' for l in L) else '本镜不说话，嘴闭'}" for x in fc] or ['- 鱼：不在场']
    md+=[f"- 不说话一方：{c['react']}",'','**画面元素**','','| 入点 | 元素 / 字卡文字 | 位置（舞台坐标） | 入场动效 | 出场 |','|---|---|---|---|---|']
    md+=[f"| {x['t']:.2f} | {x['what']} | {x['where']} | {x['fx_in']} | {x['out']} |" for x in el]
    md+=['','**音效**：'+('；'.join(f"{x['t']:.2f}s `{x['sfx']}` {x['db']}dB" for x in sfx) or '无'),'',
         '**BGM 拍点**：'+' / '.join(f'{b:.2f}' for b in beats)+f'（镜头切点 {s0:.2f}s 距最近拍 {min(abs(b-s0) for b in beats+[s0]) if beats else 0:.2f}s）','']
    rev.append(f"| {n} | {s0:.2f}–{s1:.2f} | {'；'.join(x['text'][:14] for x in ln)} |  |  |  |")
md+=['## 全局规则','','- 切镜：上一镜舞台 0.14s 缩小淡出，人物硬切姿势；字幕永远在最上层，最后叠。',
'- 嘴型：只有说话人动嘴，按本人音轨逐句 VAD 计算；鱼只用每个姿势专属的闭/半开/大开三张图（GPT image_gen 生成后贴回原图），不用通用贴片。',
'- 音色：每句 lines.json 记 reference_id/seed，O 句另过基频闸门（中位 <170Hz 且 >220Hz 帧 <15%），混音前断言，不过不出片。','']+rev
json.dump(out,open('shots_v3.json','w'),ensure_ascii=False,indent=1)
open('../script_tzs_v3.md','w').write('\n'.join(md)+'\n');print('ok',len(md))
