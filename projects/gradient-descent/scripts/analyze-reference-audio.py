"""Local CPU ASR and signal measurements. Does not identify sound-effect timbre."""
import json, math
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import find_peaks
from faster_whisper import WhisperModel
from faster_whisper.vad import get_speech_timestamps, VadOptions

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/reference-analysis'
REPORT=ROOT/'参考研究'
def stamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def db(v):return 20*np.log10(np.maximum(v,1e-8))
def main():
    sr,raw=wavfile.read(OUT/'audio-16k.wav');audio=raw.astype(np.float32)/32768
    duration=len(audio)/sr
    speech=get_speech_timestamps(audio,VadOptions(min_silence_duration_ms=180,min_speech_duration_ms=200))
    vad=[{'start':s['start']/sr,'end':s['end']/sr} for s in speech]
    print(f'VAD {len(vad)} intervals',flush=True)
    n=320;length=len(audio)//n;blocks=audio[:length*n].reshape(length,n)
    rms=np.sqrt(np.mean(blocks**2,axis=1));peak=np.max(np.abs(blocks),axis=1);times=(np.arange(length)+.5)*n/sr
    voice_mask=np.zeros(length,dtype=bool)
    for item in vad:voice_mask|=(times>=item['start'])&(times<=item['end'])
    onset=np.maximum(0,db(rms)-np.roll(db(rms),1));onset[0]=0
    indices,_=find_peaks(onset,height=6,distance=6)
    transients=[{'time':round(float(times[i]),3),'rise_db_20ms':round(float(onset[i]),2),'rms_dbfs':round(float(db(rms[i])),2),'peak_dbfs':round(float(db(peak[i])),2),'within_vad':bool(voice_mask[i])} for i in indices if db(peak[i])>-30]
    pauses=[];last=0
    for v in vad:
        if v['start']-last>=.18:pauses.append({'start':last,'end':v['start'],'duration':v['start']-last})
        last=v['end']
    if duration-last>=.18:pauses.append({'start':last,'end':duration,'duration':duration-last})
    np.savetxt(OUT/'loudness-20ms.csv',np.column_stack([times,db(rms),db(peak),voice_mask.astype(int)]),delimiter=',',header='seconds,rms_dbfs,peak_dbfs,vad_speech',comments='',fmt='%.4f')
    signal={'duration':duration,'sample_rate':sr,'global_rms_dbfs':float(db(np.sqrt(np.mean(audio**2)))),'sample_peak_dbfs':float(db(np.max(np.abs(audio)))),'speech_seconds':sum(v['end']-v['start'] for v in vad),'vad':vad,'pauses':pauses,'transients':transients,'note':'Energy/VAD estimates only. Transients do not prove added sound effects; speech consonants and music may also trigger detection.'}
    (OUT/'signal-analysis.json').write_text(json.dumps(signal,ensure_ascii=False,indent=2),encoding='utf8')
    model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=8,local_files_only=True)
    segments,info=model.transcribe(str(OUT/'audio-16k.wav'),language='zh',beam_size=5,vad_filter=True,vad_parameters={'min_silence_duration_ms':180},word_timestamps=True,condition_on_previous_text=False)
    transcript=[]
    with (OUT/'transcript-progress.jsonl').open('w',encoding='utf8') as progress:
        for seg in segments:
            item={'start':seg.start,'end':seg.end,'text':seg.text,'avg_logprob':seg.avg_logprob,'no_speech_prob':seg.no_speech_prob,'words':[{'start':w.start,'end':w.end,'text':w.word,'probability':w.probability} for w in seg.words or []]}
            transcript.append(item);progress.write(json.dumps(item,ensure_ascii=False)+'\n');progress.flush()
            print(f'{seg.start:.1f}-{seg.end:.1f}: {seg.text}',flush=True)
    payload={'source':'C:/Users/Administrator/Downloads/浙大.mp4','method':'faster-whisper small CPU int8 local cache, Chinese, beam5, Silero VAD, word timestamps','language':info.language,'duration':duration,'segments':transcript,'caution':'Automatic transcription, not manual listening verification. Word timestamps and emphases need audiovisual correction.'}
    (REPORT/'reference-transcript.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
    (REPORT/'reference-transcript.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(s["start"])} --> {stamp(s["end"])}\n{s["text"].strip()}' for i,s in enumerate(transcript))+'\n',encoding='utf8')
    (REPORT/'reference-transcript.txt').write_text('\n'.join(f'[{s["start"]:.2f}–{s["end"]:.2f}] {s["text"].strip()}' for s in transcript)+'\n',encoding='utf8')
    print('DONE',flush=True)
if __name__=='__main__':main()
