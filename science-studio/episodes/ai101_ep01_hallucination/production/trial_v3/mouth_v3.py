# 嘴型：从最终混音所用分轨的实际人声逐帧计算（无平滑滞后），只在该角色的实际发声区间开口；按 Fish 逐字时间做辅音闭口
import json,numpy as np,soundfile as sf
from pypinyin import lazy_pinyin
FPS=30;TL=json.load(open('timeline.json'));LN=TL['lines'];DUR=TL['dur'];N=int(DUR*FPS)
def env(w):
    a,sr=sf.read(f'vo_{w}.wav',dtype='float32');h=int(sr*0.005);n=len(a)//h
    r=np.sqrt((a[:n*h].reshape(n,h)**2).mean(1));return r,0.005
OUT={};ENV={}
for w in 'OF':
    r,hop=env(w);lv=np.zeros(N,np.int8);ev=np.zeros(N,np.float32)
    for l in [l for l in LN if l['who']==w]:
        i0=int((l['t0']-0.1)/hop);i1=int((l['t1']+0.1)/hop);seg=r[i0:i1];db=20*np.log10(seg+1e-9);act=db>db.max()-38
        k=np.where(act)[0];a0=(i0+k[0])*hop;a1=(i0+k[-1]+1)*hop;ref=np.percentile(seg[act],90)
        f0=int(round(a0*FPS));f1=int(np.ceil(a1*FPS))
        for f in range(f0,min(f1,N)):
            c=(f+0.5)/FPS;j=int(c/hop);e=r[max(0,j-4):j+5].mean()/ref;ev[f]=e   # 45 ms centred window
            lv[f]=2 if e>0.55 else (1 if e>0.12 else 0)
        lv[f0]=max(lv[f0],1)
        for x in l['words'][1:]:
            py=lazy_pinyin(x['c'])[0] if x['c'] else ''
            f=int(round(x['t0']*FPS))
            if py and py[0] not in 'aeiouv' and f0<f<f1-1 and lv[f-1]>0:lv[f]=0
        for f in range(f0+1,f1-1):
            if lv[f]>0 and lv[f-1]==0 and lv[f+1]==0 and f!=f0:lv[f]=0
    OUT[w]=lv;ENV[w]=ev
np.savez('mouth.npz',**OUT);np.savez('mouth_env.npz',**ENV)
print({w:int((OUT[w]>0).sum()) for w in OUT})
