from pathlib import Path
from faster_whisper import WhisperModel
import subprocess,numpy as np,json
R=Path(__file__).resolve().parents[1];m=WhisperModel('/home/box/.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120',device='cpu',compute_type='int8',cpu_threads=6,local_files_only=True);a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(R/'reference/video.mp4'),'-f','f32le','-ar','16000','-ac','1','-']),np.float32);segs,info=m.transcribe(a,language='zh',beam_size=3,vad_filter=True,word_timestamps=True,initial_prompt='足球战术分析，阿根廷，法国，梅西，阿尔瓦雷斯，麦卡利斯特，迪马利亚，德保罗。');out=[]
for s in segs:
 out.append({'start':s.start,'end':s.end,'text':s.text,'avg_logprob':s.avg_logprob,'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in s.words or []]});print(s.start,s.end,s.text,flush=True)
(R/'analysis/local_asr.json').write_text(json.dumps({'source':'local_asr','needs_review':True,'model':'faster-whisper-small local int8','segments':out},ensure_ascii=False,indent=2));(R/'analysis/local_asr.txt').write_text('\n'.join(f"{s['start']:.2f}–{s['end']:.2f} {s['text']}" for s in out));print('ASR_COMPLETE',flush=True)
