# 试片时间轴：镜1–15，按真实配音排
import json,numpy as np,soundfile as sf
EP='/workspace/science-studio/episodes/ai101_ep01_hallucination'
R=[r for r in json.load(open(EP+'/vo/takes.json')) if r['n']<=15]
SR=48000;t=0.45;L=[];prev=None
for r in R:
    if prev is not None:t+=0.28 if prev==r['who'] else 0.42
    if r['n'] in(4,9,11,13):t+=0.15   # 停顿给画面
    a,_=sf.read(EP+'/vo/'+r['cut']);d=len(a)/SR
    L.append(dict(n=r['n'],who=r['who'],text=r['text'],t0=round(t,3),t1=round(t+d,3),wav='vo/'+r['cut']));t+=d;prev=r['who']
DUR=round(t+1.2,2)
for i,l in enumerate(L):
    l['s0']=0.0 if i==0 else round(l['t0']-0.18,3)
    l['s1']=round(L[i+1]['t0']-0.18,3) if i+1<len(L) else DUR
N=int(DUR*SR);O=np.zeros(N,np.float32);Fh=np.zeros(N,np.float32)
for l in L:
    a,_=sf.read(EP+'/'+l['wav'],dtype='float32');i=int(l['t0']*SR);(O if l['who']=='O' else Fh)[i:i+len(a)]+=a[:N-i]
sf.write('vo_O.wav',O,SR);sf.write('vo_F.wav',Fh,SR);sf.write('vo_all.wav',O+Fh,SR)
json.dump(dict(dur=DUR,lines=L),open('timeline.json','w'),ensure_ascii=False,indent=1)
for l in L:print(l['n'],l['who'],l['s0'],l['t0'],l['t1'])
print('DUR',DUR)
