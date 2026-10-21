import subprocess,json
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=6)
spots=[(19.0,30.5),(55.5,63.5),(129.5,144.0),(143.5,149.0),(155.5,161.2)]
out=[]
for a,b in spots:
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(a),'-to',str(b),'-i','vo_master.wav','-ar','16000','-ac','1','/tmp/spot.wav'],check=True)
    for beam,temp in ((5,0.0),(1,0.0)):
        s,_=m.transcribe('/tmp/spot.wav',language='zh',beam_size=beam,temperature=temp,condition_on_previous_text=False,vad_filter=True)
        txt=''.join(x.text for x in s); out.append(dict(a=a,b=b,beam=beam,text=txt)); print(a,b,beam,txt,flush=True)
json.dump(out,open('asr_spot.json','w'),ensure_ascii=False,indent=1)
