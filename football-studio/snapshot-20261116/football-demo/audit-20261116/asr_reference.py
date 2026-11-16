from faster_whisper import WhisperModel
import json,time,subprocess,numpy as np
from pathlib import Path
r=Path(__file__).parent
m=WhisperModel('/home/box/.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120',device='cpu',compute_type='int8',cpu_threads=6,local_files_only=True)
audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i','/workspace/douyin-download-parser/7707868557603025643/video.mp4','-f','f32le','-ar','16000','-ac','1','-']),np.float32)
segs,info=m.transcribe(audio,language='zh',beam_size=3,vad_filter=True,word_timestamps=True)
a=[]
for s in segs:
 a.append({'start':s.start,'end':s.end,'text':s.text,'avg_logprob':s.avg_logprob,'no_speech_prob':s.no_speech_prob,'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in (s.words or [])]})
 print(s.start,s.end,s.text,flush=True)
(r/'reference_asr.json').write_text(json.dumps(a,ensure_ascii=False,indent=2))
(r/'reference_asr.txt').write_text('\n'.join(f"{x['start']:.2f}--{x['end']:.2f} {x['text']}" for x in a))
