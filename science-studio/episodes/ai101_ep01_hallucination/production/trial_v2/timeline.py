import json,numpy as np,soundfile as sf
V='/workspace/science-studio/episodes/ai101_ep01_hallucination/vo_v2/'
TF=json.load(open(V+'timeline_full.json'));LAST=20
L=[l for l in TF['lines'] if l['shot']<=LAST and l['who']!='—']
SH={int(k):v for k,v in TF['shots'].items() if int(k)<=LAST}
DUR=round(SH[LAST]['t1']+1.0,2);SH[LAST]['s1']=DUR
SR=48000;N=int(DUR*SR)
for w in ['vo_O','vo_F','vo_full']:
    a,_=sf.read(V+w+'.wav',dtype='float32');a=a[:N];sf.write((w if w!='vo_full' else 'vo_all')+'.wav',np.pad(a,(0,N-len(a))),SR)
json.dump(dict(dur=DUR,lines=L,shots=SH),open('timeline.json','w'),ensure_ascii=False,indent=1)
print(DUR)
