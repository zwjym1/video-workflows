from pathlib import Path
import json,subprocess,io
from PIL import Image,ImageDraw
R=Path(__file__).parent
V={'reference':'/workspace/douyin-download-parser/7707868557603025643/video.mp4','sample':'/workspace/football-demo/manutd-tactics/out/manutd-tactics-v2-light.mp4'}
CACHE={}
DETAIL={'reference':[8.5,10,13,16,19,21,23,27,28,30,32,35,37,40,54,60,75,105,125,136],'sample':[18,20.3,21.5,23,25.8,28,30.5,31.5,33,36,40.5,42,45,46.5,49.5,50.8]}
for name in V:
 data=json.loads((R/f'{name}_scan_summary.json').read_text())
 inds=set(round(x*30) for x in DETAIL[name])
 for c in data['candidate_transitions']:
  inds.update(max(0,min(data['frames']-1,c['frame']+off)) for off in [-2,0,2])
 inds=sorted(inds);dest=R/f'{name}_precise';dest.mkdir(exist_ok=True)
 terms=[f'eq(n\\,{n})' for n in inds]
 while len(terms)>1:terms=['('+terms[i]+'+'+terms[i+1]+')' if i+1<len(terms) else terms[i] for i in range(0,len(terms),2)]
 expr=terms[0]
 subprocess.run(['ffmpeg','-v','error','-i',V[name],'-vf',f'select={expr},scale=1280:720','-fps_mode','vfr','-q:v','2',str(dest/'%04d.jpg')],check=True)
 CACHE[name]={n:dest/f'{i+1:04d}.jpg' for i,n in enumerate(inds)}
 (R/f'{name}_precise_manifest.json').write_text(json.dumps({str(n):str(f) for n,f in CACHE[name].items()},indent=2))
 print(name,'single-pass exact extraction',len(inds),flush=True)
def frame(name,n,w=1280):
 im=Image.open(CACHE[name][n]).convert('RGB')
 return im if w==1280 else im.resize((w,int(w*9/16)))
# Each strip uses the same decoded output indices as metrics; candidate != confirmed camera cut.
for name in V:
 data=json.loads((R/f'{name}_scan_summary.json').read_text());cuts=data['candidate_transitions']
 for pg in range(0,len(cuts),10):
  sheet=Image.new('RGB',(960,10*205),(22,22,22));d=ImageDraw.Draw(sheet)
  for j,c in enumerate(cuts[pg:pg+10]):
   for k,off in enumerate([-2,0,2]):
    n=max(0,min(data['frames']-1,c['frame']+off));im=frame(name,n,320);sheet.paste(im,(k*320,j*205));d.text((k*320+4,j*205+182),f"{name} F{n} {n/30:.3f}s",fill='white')
  sheet.save(R/f'{name}_candidate_review_{pg//10:02d}.jpg',quality=94)
 print(name,'candidate sheets done',flush=True)
for name,times in {'reference':[8.5,10,13,16,19,21,23,27,28,30,32,35,37,40,54,60,75,105,125,136],'sample':[18,20.3,21.5,23,25.8,28,30.5,31.5,33,36,40.5,42,45,46.5,49.5,50.8]}.items():
 for t in times:frame(name,round(t*30),1280).save(R/f'{name}_{t:06.2f}_1280.jpg',quality=96)
 print(name,'detail frames done',flush=True)
