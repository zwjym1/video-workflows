from faster_whisper import WhisperModel
import subprocess,numpy as np,json
from pathlib import Path
R=Path(__file__).parent
m=WhisperModel('/home/box/.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120',device='cpu',compute_type='int8',cpu_threads=4,local_files_only=True)
a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i','/workspace/douyin-download-parser/7707868557603025643/video.mp4','-t','30','-f','f32le','-ar','16000','-ac','1','-']),np.float32)
out=[]
for lo,hi in [(3.9,10.3),(10.3,16),(16,22),(22,27)]:
 s,_=m.transcribe(a[int(lo*16000):int(hi*16000)],language='zh',beam_size=5,vad_filter=False,condition_on_previous_text=False,word_timestamps=True)
 for x in s:out.append({'start':lo+x.start,'end':lo+x.end,'text':x.text})
print(json.dumps(out,ensure_ascii=False,indent=2));(R/'reference_intro_asr_recheck.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
