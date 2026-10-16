"""ASR (faster-whisper small) + prosody stats for v4 takes. Run with a venv that has faster-whisper, librosa."""
import sys,json,re,glob,subprocess
import numpy as np,librosa
from faster_whisper import WhisperModel
ROOT='/workspace/koubo'
SENT=json.load(open(f'{ROOT}/scripts/v4-sentences.json',encoding='utf-8'))
D='零一二三四五六七八九'
def norm(s):
    s=s.lower().replace('他','它').replace('她','它').replace('科西','柯西').replace('哪儿','哪')
    s=re.sub(r'\d',lambda m:D[int(m.group())],s).replace('.','点')
    return re.sub(r'[^\w]|_','',s)
def cer(a,b):
    import difflib
    sm=difflib.SequenceMatcher(None,a,b);return 1-sm.ratio()
m=WhisperModel('small',device='cpu',compute_type='int8')
rows=[]
for f in sorted(glob.glob(f'{ROOT}/output/v4-voice/{sys.argv[1]}-*.mp3')):
    i=int(f[-6:-4]);y,sr=librosa.load(f,sr=16000)
    segs,_=m.transcribe(y,language='zh',initial_prompt='以下是普通话的句子，涉及梯度下降、误差、斜率a、截距b。')
    txt=''.join(s.text for s in segs)
    f0,vf,_=librosa.pyin(y,fmin=70,fmax=400,sr=sr);f0=f0[~np.isnan(f0)]
    semis=12*np.log2(f0/np.median(f0)) if len(f0) else np.array([0])
    dur=len(y)/sr;rate=len(norm(SENT[i]['text']))/dur
    c=cer(norm(SENT[i]['text']),norm(txt))
    rows.append(dict(i=i,cer=round(c,3),pitch_std_semitone=round(float(semis.std()),2),chars_per_s=round(rate,2),dur=round(dur,2),asr=txt))
    print(json.dumps(rows[-1],ensure_ascii=False))
json.dump(rows,open(f'{ROOT}/output/v4-voice/eval-{sys.argv[1]}.json','w'),ensure_ascii=False,indent=1)
