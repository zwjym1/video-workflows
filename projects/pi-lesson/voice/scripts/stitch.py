import json,subprocess,math,glob
from pathlib import Path
V=Path('/workspace/pi/voice');T=V/'takes'
S=json.load(open(V/'sentences.json'))
rows=[]
for f in ['eval-takes.json','eval-extra.json','eval-extra2.json','eval-plaza.json','eval-plaza2.json','eval-liang-01.json','eval-liang-05.json','eval-liang-15.json','eval-cut-40.json']: rows+=json.load(open(V/f))
rows=[r for r in rows if not (r['i']==33 and r['file'][:2] in ('fa','fb','fc','fd'))]  # 33 text changed
rows=[r for r in rows if not (r['i']==70 and r['file']!='gb-70.mp3')]  # 70 text changed (plaza); gb chosen: whisper-medium pinyin err 0
sel={}
FORCE={1:'lc-01.mp3',5:'pa-05.mp3',15:'lb-15.mp3',40:'ra-40.mp3'}  # 40: re-voiced 想一想 question after ch3 cut (f0 closest to neighbours)  # 量 must be liang2: picked by pitch-contour DTW vs 梁/亮 controls (scripts/tone_dtw.py)
rows=[r for r in rows if r['i'] not in FORCE or r['file']==FORCE[r['i']]]  # FORCE keys are take_i (original sentence numbers)
for i in range(len(S)):
    ti=S[i].get('take_i',i);pre=S[i].get('take_prefix')
    c=[r for r in rows if r['i']==ti and (pre is None or r['file'].startswith(pre))]
    c.sort(key=lambda r:(r['pinyin_err'],-r['pitch_std']))
    sel[i]=c[0]
json.dump({i:{k:sel[i][k] for k in ('file','pinyin_err','pitch_std','cps','dur','asr')} for i in sel},open(V/'selection.json','w'),ensure_ascii=False,indent=1)
dur=lambda f:float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)]))
def build(ids,out,align_out):
    t=0.0;words=[];sents=[];inputs=[];filt=[]
    for n,i in enumerate(ids):
        f=T/sel[i]['file'];d=dur(f);s=S[i]
        for b in json.load(open(str(f)+'.json')): words.append({'text':b['text'],'start':round(b['offset']+t,3),'end':round(b['offset']+b['duration']+t,3),'sentence':i})
        sents.append({'i':i,'chapter':s['ch'],'text':s['text'],'start':round(t,3),'end':round(t+d,3),'pause_after':s['pause'],'take':sel[i]['file']})
        inputs+=['-i',str(f)];filt.append(f'[{n}:a]aresample=44100,aformat=channel_layouts=mono,apad=pad_dur={s["pause"]}[a{n}]')
        t+=d+s['pause']
    filt.append(''.join(f'[a{n}]' for n in range(len(ids)))+f'concat=n={len(ids)}:v=0:a=1[o]')
    subprocess.check_call(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(filt),'-map','[o]','-b:a','192k',str(out)])
    D=dur(out)
    if align_out: json.dump({'audio':out.name,'duration':D,'fps':30,'frames':math.ceil(D*30)+5,'note':'word start/end in seconds; Fish timestamps; π spoken as 派','sentences':sents,'words':words},open(align_out,'w'),ensure_ascii=False,indent=1)
    return D
tot=build(range(len(S)),V/'pi-lesson-voice.mp3',V/'pi-lesson-alignment.json')
print('full',round(tot,2))
names=['ch0-opening','ch1-measure','ch2-zhousan','ch3-geyuanshu','ch4-zuchongzhi','ch5-computer','ch6-piday']
for c in range(7):
    ids=[i for i,s in enumerate(S) if s['ch']==c]
    d=build(ids,V/f'chapters/{c}-{names[c]}.mp3',V/f'chapters/{c}-{names[c]}.json');print(c,names[c],round(d,2))
# 30s sample: ch0 + start of ch1 up to ~30s
ids=[];acc=0
for i,s in enumerate(S):
    d=dur(T/sel[i]['file'])+s['pause']
    if acc+d>31: break
    ids.append(i);acc+=d
d=build(ids,V/'pi-lesson-sample-30s.mp3',None);print('sample',round(d,2),ids)
