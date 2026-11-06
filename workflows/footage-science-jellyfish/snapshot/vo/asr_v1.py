import json,re,difflib
from faster_whisper import WhisperModel
m=WhisperModel('medium',device='cpu',compute_type='int8')
segs,info=m.transcribe(__import__('numpy').fromfile('/tmp/ep0429_16k.f32',dtype='float32'),language='zh',initial_prompt='以下是普通话科普口播。水母，UFO，长征六号改，太原，地球的影子，追光灯，尾焰，气压，冰晶，触须。',vad_filter=False,word_timestamps=True)
segs=list(segs)
hyp=''.join(s.text for s in segs)
ref=re.sub(r'\[.*?\]','',open('tts_input_v1.txt',encoding='utf-8').read())
norm=lambda t: re.sub(r'[^\u4e00-\u9fff0-9A-Za-z%.]','',t)
h=norm(hyp); r=norm(ref)
sm=difflib.SequenceMatcher(None,r,h,autojunk=False)
diffs=[(op,r[a1:a2],h[b1:b2],r[max(0,a1-6):a2+6]) for op,a1,a2,b1,b2 in sm.get_opcodes() if op!='equal']
json.dump(dict(hyp=hyp,ratio=sm.ratio(),diffs=diffs,words=[(round(w.start,2),round(w.end,2),w.word) for s in segs for w in s.words]),open('asr_v1_medium.json','w'),ensure_ascii=False,indent=1)
print('sim',round(sm.ratio(),4)); print(hyp)
for d in diffs: print(d)
