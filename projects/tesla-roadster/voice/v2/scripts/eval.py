import sys,json,re,glob,difflib
import numpy as np,librosa
from faster_whisper import WhisperModel
from pypinyin import lazy_pinyin
S=json.load(open('sentences.json'))
D='零一二三四五六七八九'
def norm(s):
    s=re.sub(r'\d',lambda m:D[int(m.group())],s)
    return re.sub(r'[^\u4e00-\u9fff]','',s)
def lat(s): return re.sub(r'[^a-z]','',s.lower().replace('space x','spacex'))
def per(a,b):
    a,b=lazy_pinyin(a),lazy_pinyin(b);sm=difflib.SequenceMatcher(None,a,b)
    return sum(max(i2-i1,j2-j1) for op,i1,i2,j1,j2 in sm.get_opcodes() if op!='equal')
m=WhisperModel(sys.argv[3] if len(sys.argv)>3 else 'medium',device='cpu',compute_type='int8')
rows=[]
for f in sorted(glob.glob(sys.argv[1])):
    i=int(f[-6:-4]);y,sr=librosa.load(f,sr=16000)
    segs,_=m.transcribe(y,language='zh',initial_prompt='以下是普通话的句子，讲特斯拉Roadster跑车、SpaceX、推进器、风扇。')
    txt=''.join(s.text for s in segs)
    f0,_,_=librosa.pyin(y,fmin=60,fmax=400,sr=sr);f0=f0[~np.isnan(f0)]
    semis=12*np.log2(f0/np.median(f0)) if len(f0) else np.array([0])
    ref=S[i]['text'];dur=len(y)/sr
    le=0 if lat(ref)==lat(txt) or (lat(ref)=='ai' and re.search('A ?I|ai|诶爱|欸爱',txt,re.I)) else 1
    rows.append(dict(file=f.split('/')[-1],i=i,pinyin_err=per(norm(ref),norm(txt))+le,pitch_std=round(float(np.clip(semis,-12,12).std()),2),cps=round(len(norm(ref))/dur,2),dur=round(dur,2),asr=txt))
    print(json.dumps(rows[-1],ensure_ascii=False),flush=True)
json.dump(rows,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
