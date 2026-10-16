# Locate each 'liang' syllable with Whisper char timestamps, then classify its pitch contour (pyin, semitones)
import json,sys,numpy as np,librosa
from faster_whisper import WhisperModel
from pypinyin import lazy_pinyin
m=WhisperModel('small',device='cpu',compute_type='int8')
def analyse(f):
    y,sr=librosa.load(f,sr=16000);segs,_=m.transcribe(y,language='zh',word_timestamps=True,initial_prompt='量一量，测量。')
    chars=[]
    for s in segs:
        for w in s.words:
            t=w.word.strip();n=len(t)
            for j,c in enumerate(t):chars.append((c,w.start+(w.end-w.start)*j/max(1,n),w.start+(w.end-w.start)*(j+1)/max(1,n)))
    out=[]
    for c,a,b in chars:
        if lazy_pinyin(c)[0] not in ('liang',):continue
        w0=max(0,a-.06);seg=y[int(w0*sr):int((b+.12)*sr)];f0,vf,_=librosa.pyin(seg,fmin=80,fmax=500,sr=sr,frame_length=512,hop_length=80)
        mid=int(((a+b)/2-w0)*sr/80);runs=[];cur=[]
        for k,v in enumerate(vf):
            if v and not np.isnan(f0[k]):cur.append(k)
            elif cur:runs.append(cur);cur=[]
        if cur:runs.append(cur)
        runs=[r for r in runs if len(r)>=8]
        if not runs:out.append(dict(ch=c,t=round(a,2),tone='?'));continue
        r=min(runs,key=lambda r:0 if r[0]<=mid<=r[-1] else min(abs(r[0]-mid),abs(r[-1]-mid)))
        lim=int((b+.04-w0)*sr/80);r=[k for k in r if k<=lim] if len([k for k in r if k<=lim])>=8 else r
        f=f0[r];st=12*np.log2(f/np.median(f));n=len(st);st=st[int(n*.15):];n=len(st)
        sm=np.convolve(st,np.ones(5)/5,'valid');n=len(sm);e=sm[-max(2,n//5):].mean();mn=sm.min();mx=sm.max();imn=sm.argmin()/n;imx=sm.argmax()/n
        rise=e-mn;fall=mx-e
        tone='2 rise' if rise>1.2 and imn<.7 and rise>fall else ('4 fall' if fall>1.5 and imx<.5 else 'level/unclear')
        out.append(dict(ch=c,t=round(w0+r[0]*80/sr,2),dur=round(len(r)*80/sr,2),rise=round(float(rise),1),fall=round(float(fall),1),contour=[round(float(x),1) for x in sm[::max(1,n//6)]],tone=tone))
    return out
if __name__=='__main__':
    for f in sys.argv[1:]:print(f.split('/')[-1],json.dumps(analyse(f),ensure_ascii=False),flush=True)
