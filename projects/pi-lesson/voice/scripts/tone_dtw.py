# Classify each 量 by comparing its local pitch contour (syllable ±0.25 s, semitones re. speaker median)
# against same-voice controls synthesized with unambiguous 梁 (liang2) and 亮 (liang4) in the same sentence position.
import json,sys,numpy as np,librosa
from faster_whisper import WhisperModel
from pypinyin import lazy_pinyin
m=WhisperModel('small',device='cpu',compute_type='int8')
def track(f):
    y,sr=librosa.load(f,sr=16000);segs,_=m.transcribe(y,language='zh',word_timestamps=True,initial_prompt='量一量，测量。')
    ch=[]
    for s in segs:
        for w in s.words:
            t=w.word.strip();n=len(t)
            for j,c in enumerate(t):ch.append((c,w.start+(w.end-w.start)*j/max(1,n),w.start+(w.end-w.start)*(j+1)/max(1,n)))
    f0,vf,_=librosa.pyin(y,fmin=80,fmax=500,sr=sr,frame_length=512,hop_length=160);med=np.nanmedian(f0)
    st=12*np.log2(f0/med)
    out=[]
    for c,a,b in ch:
        if lazy_pinyin(c)[0]!='liang':continue
        i0,i1=int(max(0,a-.15)*100),int((b+.25)*100);seg=st[i0:i1];idx=~np.isnan(seg)
        out.append(np.interp(np.arange(len(seg)),np.where(idx)[0],seg[idx]) if idx.sum()>5 else None)
    return out
def dtw(a,b):
    n,m_=len(a),len(b);D=np.full((n+1,m_+1),np.inf);D[0,0]=0
    for i in range(1,n+1):
        for j in range(1,m_+1):D[i,j]=abs(a[i-1]-b[j-1])+min(D[i-1,j],D[i,j-1],D[i-1,j-1])
    return D[n,m_]/(n+m_)
if __name__=='__main__':
    sid=sys.argv[1];ctl={t:[track(f'takes/{t}{r}-{sid}.mp3') for r in 'ab'] for t in ('c2','c4')}
    res={}
    for f in sys.argv[2:]:
        tr=track(f);row=[]
        for k,c in enumerate(tr):
            d2=np.mean([dtw(c,x[k]) for x in ctl['c2'] if k<len(x) and x[k] is not None]);d4=np.mean([dtw(c,x[k]) for x in ctl['c4'] if k<len(x) and x[k] is not None])
            row.append(dict(n=k+1,d2=round(float(d2),2),d4=round(float(d4),2),tone='liang2' if d2<d4 else 'liang4'))
        res[f]=row;print(f.split('/')[-1],json.dumps(row),flush=True)
