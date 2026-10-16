import json,subprocess,math
S=json.load(open('sentences.json'));R=json.load(open('eval-takes.json'))+json.load(open('eval-extra.json'))
FORCE={15:'td-15.mp3',19:'te-19.mp3',23:'td-23.mp3'}
sel={}
for i in range(len(S)):
    c=[r for r in R if r['i']==i and (i not in FORCE or r['file']==FORCE[i])]
    c.sort(key=lambda r:(r['pinyin_err'],-r['pitch_std']));sel[i]=c[0]
json.dump(sel,open('selection.json','w'),ensure_ascii=False,indent=1)
dur=lambda f:float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
t=0.25;words=[];sents=[];inp=[];flt=[]
for i,s in enumerate(S):
    f='takes/'+sel[i]['file'];d=dur(f)
    for b in json.load(open(f+'.json')): words.append({'text':b['text'],'start':round(b['offset']+t,3),'end':round(b['offset']+b['duration']+t,3),'sentence':i})
    sents.append({'i':i,'text':s['text'],'start':round(t,3),'end':round(t+d,3),'pause_after':s['pause'],'take':sel[i]['file'],'speed':s['speed']})
    inp+=['-i',f];flt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=mono,apad=pad_dur={s["pause"]}[a{i}]');t+=d+s['pause']
flt.append(''.join(f'[a{i}]' for i in range(len(S)))+f'concat=n={len(S)}:v=0:a=1,adelay=250,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100[o]')
subprocess.check_call(['ffmpeg','-v','error','-y',*inp,'-filter_complex',';'.join(flt),'-map','[o]','-b:a','192k','tesla-voice.mp3'])
D=dur('tesla-voice.mp3')
json.dump({'audio':'tesla-voice.mp3','duration':D,'fps':30,'frames':math.ceil(D*30)+5,'lead_in':0.25,'note':'seconds; Fish word timestamps offset into stitched track','sentences':sents,'words':words},open('alignment.json','w'),ensure_ascii=False,indent=1)
print(D)
for i in sel: print(i,sel[i]['file'],sel[i]['dur'])
