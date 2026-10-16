"""Stitch selected per-sentence takes into one track + combined word alignment."""
import json,subprocess,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;V=ROOT/'output/v4-voice'
S=json.loads((ROOT/'scripts/v4-sentences.json').read_text(encoding='utf-8'))
sel={r['i']:r['take'] for r in json.loads((V/'selection.json').read_text(encoding='utf-8'))}
sel[10]='fb'  # fa-10 ASR heard 一步不走; fb reads 一步步走
dur=lambda f:float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)]))
t=0.0;bounds=[];inputs=[];filt=[]
for i,s in enumerate(S):
    f=V/f"{sel[i]}-{i:02d}.mp3";d=dur(f)
    for b in json.loads(Path(str(f)+'.json').read_text(encoding='utf-8')):bounds.append({**b,'offset':b['offset']+t})
    inputs+=['-i',str(f)];filt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=mono,apad=pad_dur={s["pause"]}[a{i}]')
    t+=d+s['pause']
filt.append(''.join(f'[a{i}]' for i in range(len(S)))+f'concat=n={len(S)}:v=0:a=1[o]')
out=ROOT/'public/fish-gradient-v4-full.mp3'
subprocess.check_call(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(filt),'-map','[o]','-b:a','192k',str(out)])
D=dur(out)
res={'audio':out.name,'text':''.join(s['text'] for s in S),'duration':D,'frames':math.ceil(D*30)+5,'boundaries':bounds,'selection':sel}
(ROOT/'output/fish-gradient-v4-full-alignment.json').write_text(json.dumps(res,ensure_ascii=False,indent=1),encoding='utf-8')
print('total',D,'expected',t,len(bounds))
