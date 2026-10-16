import sys,json,re,glob,difflib
import numpy as np,librosa
from faster_whisper import WhisperModel
from pypinyin import lazy_pinyin
S=json.load(open('/workspace/pi/voice/sentences.json'))
D='零一二三四五六七八九'
def norm(s):
    s=s.replace('π','派').replace('Π','派')
    s=re.sub(r'\d',lambda m:D[int(m.group())],s).replace('.','点')
    return re.sub(r'[^\u4e00-\u9fff]','',s)
def py(s): return lazy_pinyin(s)
def per(a,b):
    a,b=py(a),py(b);sm=difflib.SequenceMatcher(None,a,b)
    e=sum(max(i2-i1,j2-j1) for op,i1,i2,j1,j2 in sm.get_opcodes() if op!='equal');return e/max(1,len(a))
m=WhisperModel('small',device='cpu',compute_type='int8')
rows=[]
for f in sorted(glob.glob(sys.argv[1])):
    i=int(f[-6:-4]);y,sr=librosa.load(f,sr=16000)
    segs,_=m.transcribe(y,language='zh',initial_prompt='以下是普通话的句子，讲圆周率派、割圆术、刘徽、祖冲之、算筹。')
    txt=''.join(s.text for s in segs)
    f0,_,_=librosa.pyin(y,fmin=70,fmax=500,sr=sr);f0=f0[~np.isnan(f0)]
    semis=12*np.log2(f0/np.median(f0)) if len(f0) else np.array([0])
    ref=norm(S[i]['tts']);dur=len(y)/sr
    rows.append(dict(file=f.split('/')[-1],i=i,pinyin_err=round(per(ref,norm(txt)),3),pitch_std=round(float(np.clip(semis,-12,12).std()),2),f0_med=round(float(np.median(f0)),1) if len(f0) else 0,cps=round(len(ref)/dur,2),dur=round(dur,2),asr=txt))
    print(json.dumps(rows[-1],ensure_ascii=False),flush=True)
json.dump(rows,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
