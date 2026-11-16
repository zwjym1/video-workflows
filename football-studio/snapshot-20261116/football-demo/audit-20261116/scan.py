import numpy as np,subprocess,json,csv
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).parent
V={'reference':'/workspace/douyin-download-parser/7707868557603025643/video.mp4','sample':'/workspace/football-demo/manutd-tactics/out/manutd-tactics-v2-light.mp4'}
def runs(mask,minlen=1):
 st=None;o=[]
 for i,v in enumerate(list(mask)+[False]):
  if v and st is None:st=i
  elif not v and st is not None:
   if i-st>=minlen:o.append((st,i))
   st=None
 return o
for name,path in V.items():
 print('start',name,flush=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',path]))
 (R/f'{name}_probe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2))
 p=subprocess.Popen(['ffmpeg','-v','error','-i',path,'-an','-vf','scale=320:180','-pix_fmt','gray','-f','rawvideo','-'],stdout=subprocess.PIPE)
 rows=[];prev=None;ph=None;i=0
 while True:
  b=p.stdout.read(320*180)
  if len(b)!=320*180:break
  a=np.frombuffer(b,np.uint8).reshape(180,320).astype(np.int16)
  hist=np.bincount((a.ravel()//16),minlength=16)/a.size
  if prev is None:row=[i,i/30,0,0,0,0,0]
  else:
   d=np.abs(a-prev);roi=d[25:150,25:295]
   row=[i,i/30,float(d.mean()),float((d>5).mean()),float(roi.mean()),float((roi>5).mean()),float(np.abs(hist-ph).sum()/2)]
  rows.append(row);prev=a;ph=hist;i+=1
 p.wait();a=np.asarray(rows)
 with (R/f'{name}_allframe_metrics.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['frame','time_s','mad_gray','pct_absdiff_gt5','roi_mad','roi_pct_absdiff_gt5','hist_tv']);w.writerows(rows)
 # A low-change run contains transitions between near-identical adjacent output frames. It is not an editorial shot boundary.
 masks={'near_static_full':(a[:,2]<.25)&(a[:,3]<.01),'near_static_roi':(a[:,4]<.25)&(a[:,5]<.01)}
 summary={'frames':i,'fps_assumed_and_probe':30,'decoded_duration':i/30,'static_threshold':'MAD<0.25/255 AND fraction(|difference|>5)<1%; contiguous >=0.75s; gray 320x180. ROI x25:295,y25:150 excludes most top/bottom graphics.','runs':{}}
 for k,mask in masks.items():summary['runs'][k]=[{'start_frame':max(0,s-1),'end_frame_exclusive':e,'start':max(0,s-1)/30,'end':e/30,'duration':(e-max(0,s-1))/30} for s,e in runs(mask,23)]
 can=np.flatnonzero((a[:,2]>12)|((a[:,6]>.16)&(a[:,2]>4)))
 selected=[]
 for v in can:
  if not selected or v-selected[-1]>8:selected.append(int(v))
  elif a[v,2]>a[selected[-1],2]:selected[-1]=int(v)
 summary['candidate_transitions']=[{'frame':x,'time':x/30,'mad':a[x,2],'hist_tv':a[x,6]} for x in selected]
 (R/f'{name}_scan_summary.json').write_text(json.dumps(summary,indent=2))
 print(name,'frames',i,'candidates',len(selected),'long near-static runs',len(summary['runs']['near_static_full']),flush=True)
 dest=R/f'{name}_1s';dest.mkdir(exist_ok=True)
 subprocess.run(['ffmpeg','-v','error','-i',path,'-vf','fps=1,scale=640:360','-q:v','2',str(dest/'%04d.jpg')],check=True)
 files=sorted(dest.glob('*.jpg'))
 for page in range(0,len(files),20):
  sheet=Image.new('RGB',(1920,5*300),(25,25,25));draw=ImageDraw.Draw(sheet)
  for n,pic in enumerate(files[page:page+20]):
   im=Image.open(pic).resize((480,270));x=n%4*480;y=n//4*300
   sheet.paste(im,(x,y));draw.text((x+8,y+273),f'{name} t~{page+n+0.5:.1f}s (fps=1 representative frame)',fill='white')
  sheet.save(R/f'{name}_contact_{page//20:02d}.jpg',quality=92)
 print('done',name,flush=True)
