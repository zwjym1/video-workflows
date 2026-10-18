HAS_RB=True
import json,os,numpy as np,soundfile as sf,subprocess,re
R=json.load(open('eval.json'));S=[json.loads(l) for l in open('meta.jsonl')] if False else None
exec(open('gen.py').read().split('import requests')[0]) if False else None
L=[l.strip() for l in open('script.txt') if l.strip()]
P={0:.55,10:.55,3:.35}
RISE={2,11,18,21}
pick={}
for i in range(len(L)):
    c=[r for r in R if r['i']==i]
    key=lambda r:(r['err'], -r['rise'] if i in RISE and r['err']==min(x['err'] for x in c) else 0, abs(r['cps_speech']-6.0))
    pick[i]=min(c,key=key)
pick[5]=[r for r in R if r['file']=='comp/tc-05.wav'][0]
TEMPO=1.15
FLT='rubberband=tempo=1.15' if HAS_RB else 'atempo=1.15'
import os
os.makedirs('tempo',exist_ok=True)
SR=44100;out=[];t=0.12;sents=[];out.append(np.zeros(int(.12*SR)))
for i in range(len(L)):
    r=pick[i];tf='tempo/'+r['file'].split('/')[-1];subprocess.run(f"ffmpeg -v error -y -i {r['file']} -af {FLT} -ar 44100 -ac 1 {tf}",shell=True,check=True);y,_=sf.read(tf);y=y if y.ndim==1 else y.mean(1)
    sents.append(dict(i=i,text=L[i],take=r['file'],start=round(t,3),end=round(t+len(y)/SR,3),words=[dict(text=w['text'],start=round(t+w['start']/TEMPO,3),end=round(t+w['end']/TEMPO,3)) for w in r['words']]))
    out.append(y);t+=len(y)/SR;g=P.get(i,.6 if i==len(L)-1 else .3);out.append(np.zeros(int(g*SR)));t+=g
a=np.concatenate(out);sf.write('voice-v3-raw.wav',a,SR)
subprocess.run('ffmpeg -v error -y -i voice-v3-raw.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 44100 voice-v3.wav && ffmpeg -v error -y -i voice-v3.wav -b:a 192k ../voice-v3.mp3',shell=True,check=True)
n=sum(r['n'] for r in pick.values());dur=len(a)/SR;sp=sum(r['n']/r['cps_speech'] for r in pick.values())/TEMPO
st=dict(duration=round(dur,2),units=n,cps_overall=round(n/dur,2),cps_speech=round(n/sp,2),picks={i:dict(file=pick[i]['file'],err=pick[i]['err'],cps_speech=pick[i]['cps_speech'],rise=pick[i]['rise'],asr=pick[i]['asr']) for i in pick})
json.dump(dict(sentences=sents,stats=st),open('alignment-v3.json','w'),ensure_ascii=False,indent=1)
print(json.dumps({k:v for k,v in st.items() if k!='picks'}));[print(i,p['err'],p['cps_speech'],p['rise'],p['asr']) for i,p in st['picks'].items()]
