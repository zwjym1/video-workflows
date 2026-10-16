import json,os,sys
sys.path.insert(0,'/workspace/pi/voice/scripts')
from fish import synth
from concurrent.futures import ThreadPoolExecutor
L=[l.strip() for l in open('script.txt',encoding='utf-8') if l.strip()]
PUNCH={0:.55,2:.6,4:.45,5:.5,12:.6,19:.5,21:.7,25:.5}
S=[]
for i,t in enumerate(L):
    tts=t.replace('2028年','二零二八年').replace('AI','A I')
    S.append(dict(i=i,text=t,tts=tts,speed=1.1 if i not in (21,) else 1.04,pause=PUNCH.get(i,.28)))
S[-1]['pause']=0.6
json.dump(S,open('sentences.json','w'),ensure_ascii=False,indent=1)
tags=sys.argv[1].split(','); ids=range(len(S)) if len(sys.argv)<3 else [int(x) for x in sys.argv[2].split(',')]
def job(a):
    tag,i=a;s=S[i]
    for _ in range(3):
        try: synth(s['tts'],f'takes/{tag}-{i:02d}.mp3','b4bdf5dc66004241a21ff2df165bf442',s['speed'],.65);return f'{tag}{i} ok'
        except Exception as e: err=str(e)
    return f'{tag}{i} FAIL {err}'
with ThreadPoolExecutor(4) as ex:
    for r in ex.map(job,[(t,i) for t in tags for i in ids]): print(r,flush=True)
