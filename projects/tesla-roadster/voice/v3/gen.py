import json,sys
sys.path.insert(0,'/workspace/pi/voice/scripts')
from fish import synth
from concurrent.futures import ThreadPoolExecutor
R='cfd828bdf120410c923fac0056c687c2'
L=[l.strip() for l in open('script.txt',encoding='utf-8') if l.strip()]
S=[]
for i,t in enumerate(L):
    tts=t.replace('2028年','二零二八年').replace('AI','A I')
    S.append(dict(i=i,text=t,tts=tts,speed=1.05,pause={0:.55,10:.55,len(L)-1:.6}.get(i,.3),rise=i in (2,11,18,21)))
S[3]['pause']=.35
json.dump(S,open('sentences.json','w'),ensure_ascii=False,indent=1)
tags=sys.argv[1].split(',');ids=range(len(S)) if len(sys.argv)<3 else [int(x) for x in sys.argv[2].split(',')]
def job(a):
    tag,i=a;s=S[i];err=''
    for _ in range(3):
        try: synth(s['tts'],f'takes/{tag}-{i:02d}.mp3',R,s['speed'],.65);return f'{tag}{i} ok'
        except Exception as e: err=type(e).__name__
    return f'{tag}{i} FAIL {err}'
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(job,[(t,i) for t in tags for i in ids]): print(r,flush=True)
