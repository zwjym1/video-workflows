import json,re
b=json.load(open('take_v2.mp3.json'))
SUB=[l.strip() for l in open('../script/v2_edit.md',encoding='utf-8').read().splitlines()[1:] if l.strip()]
import importlib.util,sys
src=open('gen_v2.py',encoding='utf-8').read(); TTS=eval(src[src.index('TTS=[')+4:src.index(']',src.index('TTS=['))+1])
norm=lambda t: re.sub(r'[^\u4e00-\u9fff0-9A-Za-z]','',t)
chars=[]  # per-char times
for x in b:
    t=norm(x['text'])
    for i,c in enumerate(t): chars.append((c,x['offset']+x['duration']*i/len(t),x['offset']+x['duration']*(i+1)/len(t)))
pos=0; out=[]
for s,sub in zip(TTS,SUB):
    n=len(norm(s)); seg=chars[pos:pos+n]; assert ''.join(c for c,_,_ in seg)==norm(s),(s,''.join(c for c,_,_ in seg)); pos+=n
    out.append(dict(text=sub.rstrip('，。：'),tts=s,a=round(seg[0][1],3),b=round(seg[-1][2],3),chars=[(c,round(a,3),round(e,3)) for c,a,e in seg]))
assert pos==len(chars)
json.dump(out,open('cards_timed.json','w'),ensure_ascii=False,indent=1)
for o in out: print(o['a'],o['b'],o['text'])
