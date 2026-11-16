from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import json,numpy as np,math,sys,functools,subprocess,csv
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(__file__).parent));import core as C
C.FONT=str(R/'assets/NotoSansSC-700.ttf')
T=json.loads((R/'script/ACTUAL_TIMELINE.json').read_text());SH=json.loads((R/'script/SHOT_TIMELINE.json').read_text());V={v['id']:v for v in json.loads((R/'script/VOICE_TIMESTAMPS.json').read_text())};S=T['starts'];FPS=25;W,H=1280,720;END=T['duration_s'];N=round(END*FPS);O=R/'out';Q=R/'qc'
BG=C.BG;WHITE=C.WHITE;MUT=C.MUT;ATT=C.ATT;DEF=C.DEF;BALL=C.BALL;RUN=C.RUN
pr=C.pr;xy=C.xy;mix=C.mix;trace=C.trace;text=C.text;col=C.col;line=C.line
q=lambda t:round(t*25)/25

def wt(k,tok,occ=0):
 words=V[k]['words'];full=''.join(w['text'] for w in words);i=-1
 for _ in range(occ+1):i=full.find(tok,i+1)
 assert i>=0,(k,tok)
 n=0
 for w in words:
  if n+len(w['text'])>i:return q(S[k]+w['offset']+(i-n)*w['duration']/len(w['text']))
  n+=len(w['text'])
def rel(k,tok,add=0,occ=0):return wt(k,tok,occ)+add
BASE={b['id']:b for b in json.loads((R/'assets/BOARD_RELATIONS.json').read_text())['boards']}
SPECS={}
def make(k,base,question,scene):
 b=json.loads(json.dumps(BASE[base]));b.update(id=k,question=question,scene=scene);b['pos']={n['id']:n['uv'] for n in b['nodes']};b['extra']=b.get('extra_points',{});b['motion']=[];b['routes']=[];b['labels']=[];b['appear']={n['id']:-10 for n in b['nodes']};b['focus']=set();SPECS[k]=b;return b
b=make('Q1','B2','过掉眼前这一人，下一脚怎么办？','N02');be=next(s['start_s'] for s in SH if s['board']=='Q1');b['focus']={'A34','L14','A11','L10'}
b['appear'].update(A34=be,L14=be,A11=wt('N02','托雷拉'),L10=wt('N02','下一名'))
b['motion']=[['A34',[72,94],[66,76],be+.12,wt('N02','身后')+.35,'run'],['L14',[65,93],[72,85],be+.16,wt('N02','身后')+.35,'def'],['L10',[49,66],[53,57],wt('N02','下一名'),wt('N02','蓝衣')+.35,'def']]
b['routes']=[(['A34','A11'],wt('N02','接点'),wt('N02','球再')+.20)]
b['labels']=[('L14','由前侧，变到身后',be+.24,(30,20),wt('N02','托雷拉')),('L10','下一名防守者',wt('N02','蓝衣'),(-218,-28),1e4),('A11','前内侧接点',wt('N02','托雷拉'),(32,-60),1e4)]
b=make('Q2','B3','中间这脚中转，多接上哪条路？','N03');be=next(s['start_s'] for s in SH if s['board']=='Q2');b['focus']={'A10','A29','A2','L24'}
b['appear'].update(A10=be,A29=wt('N03','借队友'),A2=wt('N03','球就'),L24=wt('N03','借队友'))
b['motion']=[['L24',[49,31],[43,25],wt('N03','二十四号'),wt('N03','回追')+.3,'def']]
b['routes']=[(['A10','A29'],wt('N03','一脚'),wt('N03','中转')+.35),(['A29','A2'],wt('N03','外侧'),wt('N03','贝莱林')+.45)]
b['labels']=[('A10','中间接应',be,(40,24),wt('N03','球就')),('A29','一脚中转',wt('N03','借队友'),(38,-30),1e4),('A2','外侧继续推进',wt('N03','外侧'),(-260,-45),1e4)]
b=make('Q3','B4','球在边上，里面的人为什么还要跑？','N04');be=next(s['start_s'] for s in SH if s['board']=='Q3');b['focus']={'A2','L24','A17','L3','A10','L25'}
b['appear'].update(A2=be,L24=be,A17=wt('N04','内侧两人'),A10=wt('N04','内侧两人')+.2,L3=wt('N04','内侧两人'),L25=wt('N04','内侧两人')+.2)
b['motion']=[['A2',[34,8],[23,8],be+.12,wt('N04','内侧两人'),'run'],['A17',[30,28],[18,28],wt('N04','内侧两人'),wt('N04','继续跟')+.45,'run'],['A10',[39,54],[25,54],wt('N04','内侧两人')+.2,wt('N04','继续跟')+.5,'run'],['L24',[42,15],[29,15],be+.2,wt('N04','蓝衣'),'def'],['L3',[34,29],[24,29],wt('N04','蓝衣'),wt('N04','回撤')+.25,'def'],['L25',[45,61],[32,61],wt('N04','蓝衣')+.15,wt('N04','回撤')+.35,'def']]
b['labels']=[('A2','外侧推进',be,(38,-40),wt('N04','里面也有')),('A17','内侧接点',wt('N04','内侧两人'),(-188,-68),1e4),('A10','下一脚仍可接',wt('N04','里面也有'),(58,-8),1e4)]
b=make('Q4','B5','回传点前还有中卫，怎么续到身后？','N05');be=next(s['start_s'] for s in SH if s['board']=='Q4');b['focus']={'A10','L15','A9','A2'};b['pos']['L6']=[12,31];b['appear']['L6']=-10;b['extra']['A10_origin']=b['pos']['A10']
b['appear'].update(A10=be,L15=be,A9=be+.22,A2=be)
b['motion']=[['A10',b['pos']['A10'],b['extra']['A10_next'],wt('N05','厄齐尔',1),wt('N05','队友'),'run'],['L15',[18,56],[15,45],wt('N05','身侧'),wt('N05','立即')+.2,'def']]
b['routes']=[(['A2','A10_origin','A9'],wt('N05','不在'),wt('N05','拉卡泽特')+.66),(['A9','A10_next'],wt('N05','回做'),wt('N05','再看')-.08)]
b['labels']=[('L15','身前的中卫',be,(-220,-22),wt('N05','厄齐尔',1)),('A9','接下，立即回做',be+.22,(48,0),1e4),('A10','新的接球点',wt('N05','插进去'),(40,-66),1e4)]
b=make('Q5','B6','门将来到这一侧，横传改变了什么？','N06');be=next(s['start_s'] for s in SH if s['board']=='Q5');b['focus']={'A10','L1','A14','L14'}
b['appear'].update(A10=be,L1=be,A14=wt('N06','奥巴'),L14=wt('N06','回追者'))
b['motion']=[['L14',[10,73],[8,68],wt('N06','回追者'),wt('N06','前面')+.35,'def']]
b['routes']=[(['A10','A14'],wt('N06','横传'),wt('N06','终结')+.45)]
b['labels']=[('L1','门将已向球侧出来',be,(-280,-52),wt('N06','横传')),('A14','另一侧的终结点',wt('N06','奥巴'),(-290,6),1e4),('L14','回追仍在身后',wt('N06','回追者'),(38,8),1e4)]
# Uniform orthographic scale in real pitch coordinates. No artificial x/y distortion.
for k,b in SPECS.items():
 pp=[p for z,p in b['pos'].items() if z in b['focus']]
 for z,a,bb,ta,tb,kind in b['motion']:pp.extend([a,bb])
 pp.extend(b['extra'].values());ar=np.array(pp,float)*[1.05,.68];mn=ar.min(0)-[4,3];mx=ar.max(0)+[4,3];scale=min(900/(mx[0]-mn[0]),490/(mx[1]-mn[1]));b['projection']={'cx':560,'cy':359,'centre_m':((mn+mx)/2).tolist(),'scale':float(scale)}
 # focus set serialized separately below

def proj(b,uv):
 p=b['projection'];return (p['cx']+(uv[0]*1.05-p['centre_m'][0])*p['scale'],p['cy']+(uv[1]*.68-p['centre_m'][1])*p['scale'])
@functools.lru_cache(8)
def boardbase(k):
 b=SPECS[k];a=Image.new('RGBA',(2560,1440),BG+(255,));layer=Image.new('RGBA',a.size);d=ImageDraw.Draw(layer);C.pitch(d,lambda p:proj(b,p),(68,88,91),1.2);a.alpha_composite(layer.crop((76,178,2070,1238)),(76,178));d=ImageDraw.Draw(a)
 text(d,(44,27),b['question'],27,WHITE);text(d,(1080,41),'← 进攻',19,MUT)
 mx,my,mw,mh=1078,94,155,100
 def mp(uv):return(mx+uv[0]*mw/100,my+uv[1]*mh/100)
 C.pitch(d,mp,(86,106,108),.75)
 # Actual viewport marker, same orientation and uniform main projection.
 p=b['projection'];sc=p['scale'];u0=(p['centre_m'][0]+(40-p['cx'])/sc)/1.05;u1=(p['centre_m'][0]+(1035-p['cx'])/sc)/1.05;v0=(p['centre_m'][1]+(89-p['cy'])/sc)/.68;v1=(p['centre_m'][1]+(619-p['cy'])/sc)/.68
 aa=mp((max(0,u0),max(0,v0)));bb=mp((min(100,u1),min(100,v1)))
 if aa[0]<bb[0] and aa[1]<bb[1]:d.rectangle((*xy(aa),*xy(bb)),outline=col(ATT,150),width=2)
 return a

def pill(d,p,lab,cc=WHITE,alpha=255):
 x,y=p;n=23;bb=d.textbbox((0,0),lab,font=C.font(n));ww=(bb[2]-bb[0])/2;x=max(46,min(x,1020-ww));y=max(107,min(580,y));d.rounded_rectangle((*xy((x-8,y-4)),*xy((x+ww+8,y+31))),radius=8,fill=(9,19,24,round(alpha*.85)));text(d,(x,y),lab,n,cc,a=alpha);return(x,y,ww)

def board(k,t):
 b=SPECS[k];a=boardbase(k).copy();d=ImageDraw.Draw(a);uv={z:tuple(p) for z,p in b['pos'].items()};uv.update({z:tuple(p) for z,p in b['extra'].items()});positions={z:tuple(p) for z,p in b['pos'].items()}
 for z,aa,bb,ta,tb,kind in b['motion']:
  positions[z]=mix(aa,bb,pr(t,ta,tb));trace(d,[proj(b,aa),proj(b,bb)],col(RUN if kind=='run' else DEF,220 if kind=='run' else 155),2.8 if kind=='run' else 1.8,pr(t,ta,tb),(7,5) if kind=='run' else (4,6))
 if k=='Q3' and t>=wt('N04','这让防守'):
  # Contextual parallel channels, not a claim of uncontested free space.
  for zz,aa in [('A2',wt('N04','这让防守')),('A10',wt('N04','里面也有'))]:
   p=proj(b,positions[zz]);qq=pr(t,aa,aa+.45)
   if qq>0:trace(d,[(p[0]+52,p[1]),(p[0]-45,p[1])],col(ATT,80),13,qq,None,False)
 if k=='Q4' and t>=wt('N05','厄齐尔',1):
  p=proj(b,uv['A10_origin']);trace(d,[(p[0]+25*math.cos(z),p[1]+25*math.sin(z)) for z in np.linspace(0,math.pi*2,80)],col(MUT,140),1.3,1,(3,5),False);text(d,(p[0]+64,p[1]-58),'原位',18,MUT)
 if k=='Q5':trace(d,[proj(b,(1.5,50)),proj(b,(5,45))],col(DEF,150),1.9,pr(t,next(s['start_s'] for s in SH if s['board']=='Q5'),next(s['start_s'] for s in SH if s['board']=='Q5')+.42),(4,6))
 balls=[]
 for ids,ta,tb in b['routes']:
  if t>=ta:
   ps=[proj(b,uv[z]) for z in ids];ep=trace(d,ps,col(BALL,245),2.8,pr(t,ta,tb));balls.append((ta,ep))
 # A small fixed legend only at the first analysis scale transition.
 be=next(s['start_s'] for s in SH if s['board']==k)
 if k=='Q1' and t<be+1.75:
  text(d,(48,593),'实线：球路    虚线：跑动',18,MUT,a=round(255*(1-pr(t,be+1.3,be+1.75))))
 for z,p in positions.items():
  aa=b['appear'].get(z,-10);fade=pr(t,aa,aa+.22)
  if fade<=0:continue
  focus=z in b['focus'];x,y=proj(b,p);cc=ATT if z.startswith('A') else DEF;r=22 if focus else 15;opacity=255*fade if focus else 125*fade
  if 42+r<x<1043-r and 90+r<y<616-r:
   glow=(1-pr(t,aa+.18,aa+.56))*fade
   if focus and glow>0:d.ellipse((*xy((x-r-8,y-r-8)),*xy((x+r+8,y+r+8))),outline=col(cc,68*glow),width=4)
   fill=(80,93,22) if z.startswith('A') else (104,43,39)
   d.ellipse((*xy((x-r,y-r)),*xy((x+r,y+r))),fill=col(fill,opacity),outline=col(cc,opacity),width=4 if focus else 2)
   text(d,(x,y-.5),z[1:],22 if focus else 17,WHITE,'mm',a=opacity)
  mx,my=1078+p[0]*155/100,94+p[1]*100/100;d.ellipse((*xy((mx-2.5,my-2.5)),*xy((mx+2.5,my+2.5))),fill=col(cc,opacity))
 if balls:
  ep=max(balls,key=lambda z:z[0])[1]
  if ep:
   x,y=ep;d.ellipse((*xy((x-6,y-6)),*xy((x+6,y+6))),fill=WHITE,outline=BALL,width=2)
 labels=[v for v in b['labels'] if v[2]<=t<v[4]][-3:]
 for z,lab,ta,off,tend in labels:
  if t<b['appear'].get(z,-10):continue
  p=proj(b,positions[z]);dest=(p[0]+off[0],p[1]+off[1]);fade=pr(t,ta,ta+.24);x,y,ww=pill(d,dest,lab,WHITE,round(255*fade));trace(d,[p,(x if x>p[0] else x+ww,y+13)],col(MUT,100*fade),.85,fade,None,False)
 return a.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)

def comparison(local):
 a=Image.new('RGB',(W,H),BG);C.native_text(a,(44,38),'同一个中卫：从身前，到身后',30)
 for j,(st,box,pnt,lab) in enumerate([(98.4,(455,250,800,440),(35,183),'之前：15 在身前'),(100.8,(520,235,870,430),(655,183),'之后：15 在身后')]):
  im=C.freeze(st,1,[('A10',0),('L15',.1)]);crop=im.crop(box);hh=round(crop.height/crop.width*590);crop=crop.resize((590,hh),Image.Resampling.LANCZOS)
  if j and local<.24:crop=Image.blend(Image.new('RGB',crop.size,BG),crop,pr(local,0,.24))
  a.paste(crop,pnt);C.native_text(a,(pnt[0]+8,130),lab,26,ATT if j else MUT)
 return a

def caption(im,t):
 cc=[c for c in T['captions'] if c['start_s']-.001<=t<c['end_s']+.04]
 if not cc:return im
 c=cc[-1];st=c['text'];d=ImageDraw.Draw(im);bb=d.textbbox((0,0),st,font=C.font(33,1));ww=bb[2]-bb[0];a=Image.new('RGBA',(W,H));dd=ImageDraw.Draw(a);dd.rounded_rectangle(((W-ww)/2-17,645,(W+ww)/2+17,699),radius=8,fill=(4,10,14,135));dd.text((W/2,655),st,font=C.font(33,1),fill=WHITE,anchor='mt',stroke_width=2,stroke_fill=(0,0,0,225));return Image.alpha_composite(im.convert('RGBA'),a).convert('RGB')

def render(t,cap=True):
 s=next(x for x in SH if x['start_s']-.0001<=t<x['end_s']-.0001);kind=s['kind'];k=s['board'];src=None;mask=None
 if kind=='board':im=board(k,t)
 elif kind=='compare':im=comparison(t-s['start_s']);src=[98.4,100.8];mask='fixed_still_manualROI_chroma_sole'
 elif kind=='freeze':
  src=s['source_start_s'];im=C.freeze(src,t,s['marks']);mask='fixed_still_manualROI_chroma_sole'
  if s['scene']=='N00':C.native_text(im,(44,126),'回传，为何仍能向前？',29)
  if s['scene']=='N05' and t>=wt('N05','中卫'):C.native_text(im,(44,128),'回传接点前，仍有中卫',27)
  if s['scene']=='N06' and t>=wt('N06','门将'):C.native_text(im,(44,126),'门将已向持球侧出来',27)
 elif kind=='plain_freeze':
  src=s['source_start_s'];im=C.still(src).copy();C.native_text(im,(44,130),'蓝衣逼近边线接点',26)
  if t>=wt('N01','内侧')-.4:C.native_text(im,(44,171),'下一步：接上内侧',26,ATT)
 else:
  src=q(s['source_start_s']+t-s['start_s']);im=C.src(src).copy()
  if kind=='summary' and t<wt('N07','去掉'):C.native_text(im,(44,126),s['note'],28,WHITE)
  if s['scene']=='N01' and t<S['N01']+3.4:C.native_text(im,(44,124),'从后场接起',25,MUT)
 if cap and kind!='replay':im=caption(im,t)
 state={'frame':round(t*25),'output_s':q(t),'scene':s['scene'],'kind':kind,'source_s':src,'source_speed':1 if kind in ['live','summary','replay'] else None,'board':k,'mask':mask,'new_caption':[c['text'] for c in T['captions'] if abs(c['start_s']-t)<.019]}
 if kind=='board':
  b=SPECS[k];state['active_cues']=[f'object:{z}' for z,ta in b['appear'].items() if ta<=t and z in b['focus']]+[f'path:{"-".join(ids)}' for ids,ta,tb in b['routes'] if ta<=t]
  state['motion_progress']={z:round(pr(t,ta,tb),5) for z,aa,bb,ta,tb,kind in b['motion']};state['route_progress']={'-'.join(ids):round(pr(t,ta,tb),5) for ids,ta,tb in b['routes']}
 return im,state

def save_design():
 serial=[]
 for k,b in SPECS.items():
  z=dict(b);z['focus']=sorted(b['focus']);serial.append(z)
 (O/'ANIMATION_DESIGN_EXECUTED.json').write_text(json.dumps(serial,ensure_ascii=False,indent=2))

def preflight():
 ts=[.8,2.16,S['N01']+4.8]
 for sh in SH:
  if sh['kind']=='board':ts.extend([sh['start_s']+.32,(sh['start_s']+sh['end_s'])/2,sh['end_s']-.24])
 ts.extend([S['N05']+1.5,S['N05']+12,S['N06']+1.5,T['verify_start_s']+.8,END-.08]);cols=4;sheet=Image.new('RGB',(1280,math.ceil(len(ts)/cols)*205),BG)
 for i,t in enumerate(ts):
  im,state=render(q(t));im.save(Q/f'preflight_{q(t):.2f}.jpg',quality=95);sheet.paste(im.resize((320,180)),((i%4)*320,(i//4)*205));ImageDraw.Draw(sheet).text(((i%4)*320+5,(i//4)*205+182),f'{t:.2f}s {state["kind"]} {state["board"] or ""}',fill='white')
 sheet.save(Q/'PREFLIGHT_CONTACT.jpg',quality=95);save_design();print('PREFLIGHT',ts,flush=True)

if __name__=='__main__':
 if '--preflight' in sys.argv:preflight();sys.exit()
 save_design();out=O/'arsenal_refined_v2_main.mp4';cmd=['ffmpeg','-v','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','25','-i','-','-i',str(O/'final_mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','18','-profile:v','high','-level:v','3.1','-pix_fmt','yuv420p','-c:a','aac','-profile:a','aac_low','-b:a','192k','-ar','48000','-ac','2','-disposition:a:0','default','-af','asetpts=PTS-STARTPTS','-t',str(END),'-movflags','+faststart',str(out)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE);f=(O/'FRAME_SOURCE_STATE_MAP.jsonl').open('w')
 try:
  for i in range(N):
   im,state=render(i/25);p.stdin.write(im.tobytes());f.write(json.dumps(state,ensure_ascii=False)+'\n')
   if i%100==0:print('RENDER',i,N,state['kind'],flush=True)
  p.stdin.close();assert p.wait()==0
 finally:f.close()
 print('RENDER_COMPLETE',out,flush=True)
