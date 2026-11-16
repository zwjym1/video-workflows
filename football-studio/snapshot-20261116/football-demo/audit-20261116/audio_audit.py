import json,subprocess,csv,numpy as np
from pathlib import Path
from faster_whisper.audio import decode_audio
from faster_whisper.vad import get_speech_timestamps,VadOptions
def decode_audio(path,sampling_rate=16000):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',path,'-f','f32le','-ar',str(sampling_rate),'-ac','1','-']),np.float32)
R=Path(__file__).parent;P=Path('/workspace/football-demo/manutd-tactics');tl=json.loads((P/'src/timeline.json').read_text())
rows=[];placements=[]
for v in tl['voice']:
 f=P/v['file'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(f)]));dur=float(probe['format']['duration'])
 words=json.loads(f.with_suffix('.mp3.json').read_text());lo=min(w['offset'] for w in words);hi=max(w['offset']+w['duration'] for w in words)
 snd=decode_audio(str(f),sampling_rate=16000);vad=get_speech_timestamps(snd,VadOptions(min_speech_duration_ms=150,min_silence_duration_ms=150,speech_pad_ms=30))
 rows.append({'id':v['id'],'placement':v['start'],'file_duration':dur,'file_end':v['start']+dur,'first_word':v['start']+lo,'last_word_end':v['start']+hi,'text':tl['captions'][v['id']],'han_char_count':sum('\u4e00'<=x<='\u9fff' for x in tl['captions'][v['id']]),'vad_local':[{'start':x['start']/16000,'end':x['end']/16000} for x in vad]})
 placements.append((v['start'],v['start']+dur,v['id']))
with (R/'sample_voice_intervals.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=[x for x in rows[0] if x!='vad_local']);w.writeheader();w.writerows({k:v for k,v in x.items() if k!='vad_local'} for x in rows)
(R/'sample_voice_detail.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
# Reference VAD: model-based speech candidates, not a declaration of narrator identity.
snd=decode_audio('/workspace/douyin-download-parser/7707868557603025643/video.mp4',sampling_rate=16000)
v=get_speech_timestamps(snd,VadOptions(min_speech_duration_ms=200,min_silence_duration_ms=200,speech_pad_ms=30))
(R/'reference_vad.json').write_text(json.dumps([{'start':x['start']/16000,'end':x['end']/16000} for x in v],indent=2))
print('sample VO',json.dumps(rows,ensure_ascii=False),flush=True)
print('reference VAD candidates',len(v),'seconds',sum(x['end']-x['start'] for x in v)/16000,flush=True)
