import json,glob,re,sys,difflib,numpy as np,librosa,soundfile as sf
from faster_whisper import WhisperModel
from pypinyin import lazy_pinyin
S=json.load(open('sentences.json'));SR=44100
D='零一二三四五六七八九'
def norm(s): return re.sub(r'[^\u4e00-\u9fff]','',re.sub(r'\d',lambda m:D[int(m.group())],s))
def compress(y):
    hop=441;rms=librosa.feature.rms(y=y,frame_length=1323,hop_length=hop)[0];db=20*np.log10(rms+1e-9);thr=db.max()-40
    voiced=db>thr;idx=np.where(voiced)[0]
    a,b=idx[0]*hop,min(len(y),(idx[-1]+1)*hop+int(.03*SR));a=max(0,a-int(.02*SR))
    keep=[];cuts=[] # (time_in_orig, removed)
    i=idx[0]
    runs=[];start=None
    for k in range(idx[0],idx[-1]+1):
        if not voiced[k] and start is None: start=k
        if voiced[k] and start is not None: runs.append((start,k));start=None
    out=[];pos=a;removed=0;mp=[(a/SR,0.0)]
    for s0,s1 in runs:
        L=(s1-s0)*hop/SR
        if L>0.3:
            cs=s0*hop+int(.15*SR);ce=s1*hop-int(.15*SR)
            out.append(y[pos:cs]);pos=ce;removed+=(ce-cs)/SR;mp.append((ce/SR,removed))
    out.append(y[pos:b]);return np.concatenate(out),a/SR,mp
def remap(t,a,mp):
    r=0
    for tt,rm in mp:
        if t>=tt: r=rm
    return max(0,t-a-r)
m=WhisperModel('medium',device='cpu',compute_type='int8');rows=[]
for f in sorted(glob.glob('takes/t*.mp3')):
    i=int(f[-6:-4]);y,_=librosa.load(f,sr=SR,mono=True);yc,a,mp=compress(y)
    fn='comp/'+f.split('/')[-1].replace('.mp3','.wav');sf.write(fn,yc,SR)
    words=[dict(text=w['text'],start=round(remap(w['offset'],a,mp),3),end=round(remap(w['offset']+w['duration'],a,mp),3)) for w in json.load(open(f+'.json'))]
    y16=librosa.resample(yc,orig_sr=SR,target_sr=16000)
    ref=S[i]['text'];yy=np.concatenate([np.zeros(8000,np.float32),y16.astype(np.float32),np.zeros(8000,np.float32)])
    def E(t):
        pa,pb=lazy_pinyin(norm(ref)),lazy_pinyin(norm(t))
        return sum(max(i2-i1,j2-j1) for op,i1,i2,j1,j2 in difflib.SequenceMatcher(None,pa,pb).get_opcodes() if op!='equal')
    cands=[''.join(s.text for s in m.transcribe(yy,language='zh',beam_size=5,condition_on_previous_text=False,initial_prompt=p)[0]) for p in ['以下是普通话的句子。','以下是普通话的句子，关于特斯拉Roadster、SpaceX和马斯克。']]
    txt=min(cands,key=E);err=E(txt)
    lat=lambda q:re.sub('[^a-z]','',q.lower().replace('space x','spacex'))
    if 'AI' in ref and not re.search('A ?I|ai',txt,re.I): err+=1
    if 'SpaceX' in ref and 'spacex' not in lat(txt): err+=1
    if 'Roadster' in ref and 'roadster' not in lat(txt): err+=0.5
    dur=len(yc)/SR;rms=librosa.feature.rms(y=yc,hop_length=441)[0];sil=(20*np.log10(rms+1e-9)<20*np.log10(rms.max())-40).sum()*0.01
    n=len(re.findall(r'[\u4e00-\u9fff]',ref))+len(re.findall(r'[A-Za-z]+',ref))*1+len(re.findall(r'\d',ref))
    f0=librosa.yin(y16,fmin=70,fmax=400,sr=16000);r16=librosa.feature.rms(y=y16,frame_length=2048,hop_length=512)[0][:len(f0)];v=f0[:len(r16)][r16>r16.max()*0.1]
    rise=float(12*np.log2(np.median(v[-max(3,len(v)//5):])/np.median(v))) if len(v)>10 else 0
    rows.append(dict(file=fn,i=i,err=err,dur=round(dur,3),cps_speech=round(n/max(.1,dur-sil),2),cps=round(n/dur,2),rise=round(rise,2),asr=txt,words=words,n=n))
    print(fn,err,rows[-1]['cps_speech'],rows[-1]['rise'],txt,flush=True)
json.dump(rows,open('eval.json','w'),ensure_ascii=False,indent=1)
