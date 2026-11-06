# 独立强制对齐：faster-whisper(medium) 词级时间 vs Fish 逐字时间，按字符匹配比较起点
import json,re,numpy as np,soundfile as sf
from faster_whisper import WhisperModel
TL=json.load(open('timeline.json'));m=WhisperModel('medium',device='cpu',compute_type='int8')
a,sr=sf.read('vo_all.wav',dtype='float32');import librosa
diffs=[];per=[]
for l in TL['lines']:
    s0=max(0,l['t0']-0.1);seg=a[int(s0*sr):int((l['t1']+0.1)*sr)];seg=librosa.resample(seg,orig_sr=sr,target_sr=16000)
    segs,_=m.transcribe(seg,language='zh',word_timestamps=True,initial_prompt=l['text'],beam_size=5,vad_filter=False)
    ws=[w for s in segs for w in s.words];ch=[]
    for w in ws:
        t=re.sub(r'\W','',w.word)
        for k,c in enumerate(t):ch.append((c,s0+w.start+(w.end-w.start)*k/len(t)))
    fw=[(w['c'],w['t0']) for w in l['words']];d=[];j=0
    for c,t in fw:
        for k in range(j,min(j+4,len(ch))):
            if ch[k][0]==c[0]:d.append(t-ch[k][1]);j=k+1;break
    per.append(dict(i=l['idx'],n=len(d),med=round(float(np.median(d)),3) if d else None));diffs+=d
d=np.abs(diffs);print('matched',len(d),'median |fish-whisper|',round(float(np.median(d)),3),'p90',round(float(np.percentile(d,90)),3))
json.dump(dict(per_line=per,median=float(np.median(d)),p90=float(np.percentile(d,90))),open('align_check.json','w'),indent=1)
for p in per:print(p)
