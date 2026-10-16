import json,sys,numpy as np,librosa
def syl(mp3,ch='量'):
    b=json.load(open(mp3+'.json'));y,sr=librosa.load(mp3,sr=16000);res=[]
    for k,w in enumerate(b):
        if ch not in w['text']:continue
        t0=w['offset'];t1=t0+w['duration'];seg=y[int(max(0,t0-.02)*sr):int((t1+.03)*sr)]
        f0,v,_=librosa.pyin(seg,fmin=80,fmax=500,sr=sr,frame_length=512,hop_length=80);f=f0[~np.isnan(f0)]
        if len(f)<6:res.append(dict(k=k,t=round(t0,2),tone='?',n=len(f)));continue
        st=12*np.log2(f/np.median(f));n=len(st);a=st[:max(2,n//3)].mean();z=st[-max(2,n//3):].mean();slope=float(np.polyfit(np.arange(n),st,1)[0]*n)
        tone='2 rise' if z-a>1.0 and slope>0 else ('4 fall' if a-z>1.0 else 'flat')
        res.append(dict(k=k,t=round(t0,2),dur=round(t1-t0,2),start_st=round(a,1),end_st=round(z,1),delta=round(z-a,1),tone=tone))
    return res
if __name__=='__main__':
    for f in sys.argv[1:]:print(f,json.dumps(syl(f),ensure_ascii=False))
