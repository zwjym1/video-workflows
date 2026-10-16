import json,librosa
from faster_whisper import WhisperModel
from pypinyin import lazy_pinyin
import re,difflib
A=json.load(open('alignment.json'));y,sr=librosa.load('tesla-voice.mp3',sr=16000)
m=WhisperModel('medium',device='cpu',compute_type='int8');out=[];tot=0
D='零一二三四五六七八九'
n=lambda s:re.sub(r'[^\u4e00-\u9fff]','',re.sub(r'\d',lambda m:D[int(m.group())],s))
for s in A['sentences']:
    import numpy as np;seg=np.concatenate([np.zeros(6400,dtype=y.dtype),y[max(0,int((s['start']-.03)*sr)):int((s['end']+.02)*sr)],np.zeros(6400,dtype=y.dtype)])
    txt=''.join(x.text for x in m.transcribe(seg,language='zh',beam_size=5,initial_prompt='特斯拉，SpaceX。')[0])
    a,b=lazy_pinyin(n(s['text'])),lazy_pinyin(n(txt))
    lat=lambda q:re.sub('[^a-z]','',q.lower())
    le=int(lat(s['text'])!=lat(txt))
    e=sum(max(i2-i1,j2-j1) for op,i1,i2,j1,j2 in difflib.SequenceMatcher(None,a,b).get_opcodes() if op!='equal')
    e+=le;tot+=e;out.append(dict(i=s['i'],ref=s['text'],asr=txt,pinyin_err=e));print(out[-1],flush=True)
full=''.join(x.text for x in m.transcribe(y,language='zh')[0])
json.dump({'total_pinyin_err':tot,'sentences':out,'full_asr':full},open('final-asr.json','w'),ensure_ascii=False,indent=1);print('TOTAL',tot);print(full)
