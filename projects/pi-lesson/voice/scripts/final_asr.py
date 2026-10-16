import json,sys
sys.path.insert(0,'/workspace/pi/voice/scripts')
from score import norm,per
from faster_whisper import WhisperModel
import difflib
from pypinyin import lazy_pinyin
S=json.load(open('/workspace/pi/voice/sentences.json'))
m=WhisperModel('small',device='cpu',compute_type='int8')
import librosa;y,_=librosa.load('/workspace/pi/voice/pi-lesson-voice.mp3',sr=16000)
segs,_=m.transcribe(y,language='zh',initial_prompt='以下是普通话的课程讲解，讲圆周率派、割圆术、刘徽、祖冲之、算筹。')
segs=list(segs);asr=''.join(s.text for s in segs)
ref=norm(''.join(s['tts'] for s in S));hyp=norm(asr)
a,b=lazy_pinyin(ref),lazy_pinyin(hyp);sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
diffs=[(op,''.join(ref[i1:i2]),''.join(hyp[j1:j2])) for op,i1,i2,j1,j2 in sm.get_opcodes() if op!='equal']
e=sum(max(len(x[1]),len(x[2])) for x in diffs)/len(ref)
hd=difflib.SequenceMatcher(None,ref,hyp,autojunk=False)
ce=sum(max(i2-i1,j2-j1) for op,i1,i2,j1,j2 in hd.get_opcodes() if op!='equal')/len(ref)
json.dump({'pinyin_err_toneless':round(e,4),'char_err':round(ce,4),'pinyin_diffs':diffs,'asr_raw':asr,'segments':[{'start':s.start,'end':s.end,'text':s.text} for s in segs]},open('/workspace/pi/voice/final-asr.json','w'),ensure_ascii=False,indent=1)
print('pinyin',round(e,4),'char',round(ce,4));print(diffs)
