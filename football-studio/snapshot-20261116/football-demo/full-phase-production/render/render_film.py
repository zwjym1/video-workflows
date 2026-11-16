from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,math,json,functools,subprocess,csv,sys,hashlib
R=Path(__file__).resolve().parents[1];O=R/'out';Q=R/'qc';W,H,FPS,SS=1280,720,25,2
T=json.loads((R/'script/ACTUAL_TIMELINE.json').read_text());B={b['id']:b for b in json.loads((R/'assets/BOARD_RELATIONS.json').read_text())['boards']};CUES=json.loads((R/'script/ANIMATION_CUES.json').read_text());N=round(T['duration_s']*FPS)
FONT='/workspace/football-demo/manutd-tactics/src/fonts/NotoSansSC-700.ttf'
BG=(11,21,27);WHITE=(242,243,233);MUT=(145,163,166);ATT=(192,221,61);DEF=(241,106,83);BALL=(241,219,70);RUN=(185,232,88)
@functools.lru_cache(None)
def font(n,s=2):return ImageFont.truetype(FONT,round(n*s))
def ease(v):v=max(0,min(1,v));return v*v*v*(v*(v*6-15)+10)
def pr(t,a,b):return ease((t-a)/max(.001,b-a))
def mix(a,b,p):return tuple(x+(y-x)*p for x,y in zip(a,b))
def xy(p,s=2):return tuple(round(z*s) for z in p)
def col(c,a=255):return tuple(c)+(round(max(0,min(255,a))),)
def line(d,points,c,w=2,s=2):
 if len(points)>1:d.line([xy(p,s) for p in points],fill=c,width=max(1,round(w*s)),joint='curve')
def text(d,p,st,n=24,c=WHITE,anchor='lt',s=2,a=255):
 d.text(xy(p,s),st,font=font(n,s),fill=col(c,a),anchor=anchor,stroke_width=max(1,round(.45*s)),stroke_fill=(0,0,0,round(a*.5)))
def trace(d,ps,c,width=2.4,p=1,dash=None,arrow=True,s=2):
 if p<=0:return None
 ls=[math.dist(a,b) for a,b in zip(ps,ps[1:])];lim=sum(ls)*min(1,p);dist=0;endp=ps[0];endangle=0
 for a,b,L in zip(ps,ps[1:],ls):
  if not L or dist>=lim:break
  take=min(L,lim-dist);q=0
  while q<take-1e-6:
   if dash:
    phase=(dist+q)%sum(dash);on=phase<dash[0];step=min(take-q,(dash[0]-phase) if on else (sum(dash)-phase))
   else:on=True;step=take-q
   step=max(.001,step)
   if on:line(d,[mix(a,b,q/L),mix(a,b,(q+step)/L)],c,width,s)
   q+=step
  endp=mix(a,b,take/L);endangle=math.atan2(b[1]-a[1],b[0]-a[0]);dist+=L
 if arrow and p>.08:
  rr=8;pts=[endp,(endp[0]-rr*math.cos(endangle-.43),endp[1]-rr*math.sin(endangle-.43)),(endp[0]-rr*math.cos(endangle+.43),endp[1]-rr*math.sin(endangle+.43))];d.polygon([xy(z,s) for z in pts],fill=c)
 return endp
@functools.lru_cache(96)
def src(t):
 n=max(1,min(510,round((t-83.2)*25)+1));return Image.open(R/'render/source'/f'{n:04d}.jpg').convert('RGB')
@functools.lru_cache(12)
def still(t):return Image.open(R/'evidence'/f'source_{t:.2f}.jpg').convert('RGB')
def proj(b,uv):
 v=b['view'];return (42+(uv[0]*1.05-v['xmin_m'])*v['scale_px_per_m'],80+(uv[1]*.68-v['ymin_m'])*v['scale_px_per_m'])
def pitch(d,f,colr=(84,106,108),width=1.3,s=2):
 for ps in [[(0,0),(100,0),(100,100),(0,100),(0,0)],[(50,0),(50,100)],[(0,20.35),(15.714,20.35),(15.714,79.65),(0,79.65)],[(0,36.53),(5.238,36.53),(5.238,63.47),(0,63.47)],[(100,20.35),(84.286,20.35),(84.286,79.65),(100,79.65)],[(100,36.53),(94.762,36.53),(94.762,63.47),(100,63.47)],[(0,44.6),(-2,44.6),(-2,55.4),(0,55.4)],[(100,44.6),(102,44.6),(102,55.4),(100,55.4)]]:line(d,[f(z) for z in ps],colr,width,s)
 a=f((50-9.15/1.05,50-9.15/.68));bb=f((50+9.15/1.05,50+9.15/.68));d.ellipse((*xy(a,s),*xy(bb,s)),outline=colr,width=max(1,round(width*s)))
@functools.lru_cache(6)
def boardbase(k):
 b=B[k];a=Image.new('RGBA',(W*2,H*2),BG+(255,));g=Image.new('RGBA',a.size);d=ImageDraw.Draw(g);pitch(d,lambda uv:proj(b,uv));a.alpha_composite(g.crop((76,140,1960,1220)),(76,140));d=ImageDraw.Draw(a)
 text(d,(42,25),b['title'],28);text(d,(1025,37),'← 进攻方向',20);line(d,[(42,66),(970,66)],(63,83,86),1)
 mx,my,mw,mh=1013,86,225,146
 def mp(uv):return(mx+uv[0]/100*mw,my+uv[1]/100*mh)
 d.rectangle((mx*2,my*2,(mx+mw)*2,(my+mh)*2),outline=(101,119,122),width=2);line(d,[mp((50,0)),mp((50,100))],(101,119,122),.8)
 v=b['view'];sc=v['scale_px_per_m'];u=max(0,v['xmin_m']/105);vv=max(0,v['ymin_m']/68);uw=min(1,(v['xmin_m']+942/sc)/105)-u;vh=min(1,(v['ymin_m']+540/sc)/68)-vv
 if uw>0 and vh>0:d.rectangle(tuple(round(x*2) for x in [mx+u*mw,my+vv*mh,mx+(u+uw)*mw,my+(vv+vh)*mh]),outline=ATT,width=2)
 text(d,(1013,246),'本段可见对象',17,MUT)
 for yy,cc,lab in [(423,BALL,'球的传递'),(461,RUN,'人的移动'),(499,DEF,'防守变化')]:
  trace(d,[(1017,yy+9),(1050,yy+9)],cc,2,1,(5,5) if cc!=BALL else None);text(d,(1061,yy),lab,18,MUT)
 text(d,(42,619),'局部关系示意 · 不补画外站位',17,MUT)
 return a

def board(k,t):
 b=B[k];a=boardbase(k).copy();d=ImageDraw.Draw(a);uv={n['id']:tuple(n['uv']) for n in b['nodes']};uv.update({z:tuple(v) for z,v in b.get('extra_points',{}).items()});positions={n['id']:uv[n['id']] for n in b['nodes']};appear={z:-100 for z in positions};routes=[];runs=[];defs=[];tags=[];note=''
 if k=='B1':
  appear.update(A19=6.16,A16=6.76,A34=8.76,F1=9.36,F2=9.36,L14=9.36,A11=9.0)
  routes=[(['A19','A16'],7.05,7.6),(['A16','A34'],9.0,9.32)];defs=[('F1',(80,70),(77,76),9.48,10.0)]
  tags=[('A19','门将',6.16,(30,-12)),('A16','后场接点',6.76,(-142,-15)),('A34','边线接点',8.76,(-142,25))];note='黄绿：阿森纳\n珊瑚红：蓝衣方'
 elif k=='B2':
  appear.update(A34=15.28,L14=15.28,A11=19.12,L10=22.16)
  positions['A34']=mix((72,94),(66,76),pr(t,15.72,16.92));positions['L14']=mix((65,93),(72,85),pr(t,17.84,18.48));positions['L10']=mix((49,66),(53,57),pr(t,22.32,23.04))
  runs=[('A34',(72,94),(66,76),15.6,16.56)];defs=[('L14',(65,93),(72,85),17.84,18.48),('L10',(49,66),(53,57),22.32,23.04)];routes=[(['A34','A11'],19.42,20.12)]
  tags=[('A34','带向内侧',15.72,(35,-34)),('L14','由前到后',17.84,(35,15)),('A11','前内侧接点',19.12,(-180,-47)),('L10','新的接近者',22.16,(-177,24))]
  note='不是防守消失\n而是换了接点' if t<22.16 else '14 追着 34\n10 接近 11'
 elif k=='B3':
  appear.update(A11=30.92,A10=30.92,A29=30.92,A2=31.52,A17=32.15,L24=31.05,L25=31.05,L6=31.05)
  routes=[(['A11','A10'],30.92,31.09),(['A10','A29'],31.09,31.5),(['A29','A2'],31.72,32.48)];runs=[('A10',(49,52),(39,52),32.48,33.18),('A17',(40,29),(32,29),32.64,33.36)]
  for z,aa,bb,ta,tb in runs:positions[z]=mix(aa,bb,pr(t,ta,tb))
  tags=[('A10','中间中转',30.92,(-160,15)),('A29','转向外侧',31.05,(40,-18)),('A2','外侧接应',31.52,(-170,-5))];note='中间：一脚交接\n外侧：继续前送'
 elif k=='B4':
  appear.update(A2=36.56,A17=38.24,A10=38.88,L3=40.28,L25=41.08,L24=37.1,L15=39.4,L6=39.4)
  runs=[('A2',(34,8),(23,8),37.12,37.96),('A17',(30,28),(18,28),38.44,39.24),('A10',(39,54),(25,54),39.08,39.92)]
  defs=[('L3',(34,29),(24,29),40.4,41.08),('L24',(42,15),(29,15),37.28,38.08),('L25',(45,61),(32,61),41.16,41.64)]
  for z,aa,bb,ta,tb in runs+defs:positions[z]=mix(aa,bb,pr(t,ta,tb))
  tags=[('A2','外侧持球',36.96,(-165,-20)),('A17','内侧跟进',38.24,(-170,-30)),('A10','内侧跟进',38.88,(60,-22)),('L3','近 17 号',40.28,(35,-6)),('L25','近 10 号',41.08,(40,-25))];note='外侧不是单打\n内侧也在接应'
 elif k=='B5':
  appear.update(A10=46.08,L15=46.88,A9=48.24,A2=46.08,L25=47.25,L18=48.24)
  positions['A10']=mix(uv['A10'],uv['A10_next'],pr(t,51.52,52.36));positions['L15']=mix((18,56),(15,45),pr(t,52.12,53.1))
  # Exactly through A10's original point; player cannot leave before ball crosses it.
  routes=[(['A2','A10_origin','A9'],49.44,50.72),(['A9','A10_next'],53.52,54.12)];uv['A10_origin']=uv['A10'];runs=[('A10',uv['A10'],uv['A10_next'],51.52,52.36)];defs=[('L15',(18,56),(15,45),52.12,53.1)]
  tags=[('A10','10：先在原位',46.08,(105,-45)),('L15','15 在身前',46.88,(-180,-45)),('A9','9：另一侧接点',48.24,(55,7))]
  if t>=51.52:
   op=proj(b,uv['A10']);trace(d,[(op[0]+24*math.cos(q),op[1]+24*math.sin(q)) for q in np.linspace(0,math.pi*2,70)],col(ATT,125),1.2,1,(4,5),False);text(d,(op[0]+56,op[1]-55),'原位',19,MUT)
  if t>=52.36:
   npnt=proj(b,uv['A10_next']);trace(d,[(npnt[0]+27*math.cos(q),npnt[1]+27*math.sin(q)) for q in np.linspace(0,math.pi*2,70)],col(RUN,220),1.4,pr(t,52.36,52.76),(4,4),False);text(d,(npnt[0]-20,npnt[1]-60),'新接点',23,RUN)
  note='先让球通过\n再接九号回做' if t<53.52 else '不是接回原位\n而是接前插'
 elif k=='B6':
  appear.update(A10=62.7,A14=64.2,L14=65.48,L1=66.68,A9=63,L18=63,L15=63)
  defs=[('L14',(14,81),(10,73),65.6,66.3),('L1',(1.5,50),(5,45),66.68,67.4)]
  for z,aa,bb,ta,tb in defs:positions[z]=mix(aa,bb,pr(t,ta,tb))
  routes=[(['A10','A14'],68.44,68.96)]
  tags=[('A10','持球一侧',62.7,(40,-40)),('A14','阿森纳14：已到位',64.2,(45,5)),('L14','蓝衣14：仍在追',65.48,(45,10)),('L1','门将向球侧出击',66.68,(105,-15))];note='两处门前接应\n由横传连起来'
 # Runs and defensive trails are separate from ball routes, no linear default tween.
 for z,aa,bb,ta,tb in runs:trace(d,[proj(b,aa),proj(b,bb)],col(RUN,220),2.5,pr(t,ta,tb),(7,5))
 for z,aa,bb,ta,tb in defs:trace(d,[proj(b,aa),proj(b,bb)],col(DEF,190),1.7,pr(t,ta,tb),(4,6))
 balls=[]
 for ids,ta,tb in routes:
  if t<ta:continue
  ps=[proj(b,uv[z]) for z in ids];pp=pr(t,ta,tb);ep=trace(d,ps,col(BALL,240),2.5,pp,None,True)
  if ep:balls.append((ta,ep))
 for z,po in positions.items():
  if z not in appear:continue
  q=pr(t,appear[z],appear[z]+.25)
  if q<=0:continue
  x,y=proj(b,po);r=18 if z.startswith('A') else 16;cc=ATT if z.startswith('A') else DEF;fill=(35,47,29) if z.startswith('A') else (79,38,34)
  if not(36<x<981 and 65<y<614):continue
  glow=(1-pr(t,appear[z]+.2,appear[z]+.65))*q
  if glow>0:d.ellipse(xy((x-r-6,y-r-6))+xy((x+r+6,y+r+6)),outline=col(cc,70*glow),width=3)
  d.ellipse(xy((x-r,y-r))+xy((x+r,y+r)),fill=col(fill,255*q),outline=col(cc,255*q),width=4)
  number=z[1:] if z.startswith(('A','L')) else '·';text(d,(x,y-.5),number,20,WHITE,'mm',a=255*q)
  # Minimap contains only the stage's actually revealed observed actors.
  mx,my=1013+po[0]/100*225,86+po[1]/100*146;d.ellipse(xy((mx-2.6,my-2.6))+xy((mx+2.6,my+2.6)),fill=col(cc,255*q))
 if balls:
  ep=max(balls)[1];x,y=ep;d.ellipse(xy((x-6,y-6))+xy((x+6,y+6)),fill=WHITE,outline=BALL,width=2)
 # Relationship labels reveal after the object, and are attached, not a name list.
 for z,lab,ta,off in tags:
  if t<ta:continue
  if k=='B5' and z in ['A10','L15'] and t>=51.52:continue
  pnt=proj(b,positions[z]);dest=(pnt[0]+off[0],pnt[1]+off[1]);q=pr(t,ta,ta+.25)
  if dest[1]<580:
   trace(d,[pnt,(dest[0]-7 if off[0]>0 else dest[0]+len(lab)*22+5,dest[1]+14)],col(MUT,130*q),.9,q,None,False);text(d,dest,lab,22,WHITE,a=255*q)
 for i,lab in enumerate(note.split('\n')):text(d,(1013,302+i*34),lab,20,WHITE)
 return a.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)

# Hand-localized body/boot regions with chroma refinement, only on fixed stills.
MASK_SPEC={88.6:{'A34':{'foot':(878,539),'roi':(844,440,905,552)},'L14':{'foot':(954,564),'roi':(891,489,974,574)}},90.2:{'A11':{'foot':(918,449),'roi':(888,383,947,462)},'L10':{'foot':(835,459),'roi':(808,393,870,474)}},98.4:{'A10':{'foot':(706,403),'roi':(681,323,737,412)},'L15':{'foot':(533,405),'roi':(503,340,574,415)}},100.8:{'A10':{'foot':(662,372),'roi':(648,283,716,380)},'L15':{'foot':(786,390),'roi':(749,298,816,401)}}}
@functools.lru_cache(10)
def bootmask(t):
 a=still(t);ar=np.asarray(a.convert('HSV'));h,s,v=ar[:,:,0],ar[:,:,1],ar[:,:,2];notgrass=~((h>45)&(h<135)&(s>65)) # PIL H is 0..255, not OpenCV 0..179.
 # All shoes/kit are restricted to manually verified actor ROIs; grass holes stay transparent.
 zone=np.zeros((H,W),bool)
 for z,sp in MASK_SPEC[t].items():x1,y1,x2,y2=sp['roi'];zone[y1:y2,x1:x2]=True
 m=Image.fromarray(np.uint8(zone&notgrass)*255);md=ImageDraw.Draw(m)
 # Explicit native-pixel sole polygons: fluorescent yellow-green must not be classified as grass.
 soles={88.6:[[(945,561),(950,558),(958,557),(965,556),(966,563),(960,567),(951,567),(944,564)],[(955,548),(960,548),(965,552),(963,558),(958,557),(953,553)]],90.2:[[(887,445),(898,443),(907,445),(910,449),(904,453),(894,453),(885,449)],[(935,438),(941,438),(945,443),(944,448),(939,448),(935,443)]],100.8:[[(653,367),(660,367),(667,370),(668,376),(659,378),(651,374)]]}
 for poly in soles.get(t,[]):md.polygon(poly,fill=255)
 return m.filter(ImageFilter.MaxFilter(3))

def ring(d,p,cc,q=1,s=2):
 x,y=p;rx,ry=25,7.5
 for aa,bb,alpha,ww in [(math.pi,2*math.pi,190,2.1),(0,math.pi,250,2.5)]:
  ps=[(x+rx*math.cos(u),y+ry*math.sin(u)) for u in np.linspace(aa,bb,90)];trace(d,ps,(0,0,0,155),ww+2.2,q,None,False,s);trace(d,ps,col(cc,alpha),ww,q,None,False,s)

def freeze(t,now,marks,masked=True):
 a=still(t).convert('RGBA').resize((W*2,H*2),Image.Resampling.LANCZOS);l=Image.new('RGBA',a.size);d=ImageDraw.Draw(l)
 for z,ta in marks:
  if now>=ta:ring(d,MASK_SPEC[t][z]['foot'],ATT if z.startswith('A') else DEF,pr(now,ta,ta+.26))
 out=Image.alpha_composite(a,l)
 if masked:out=Image.composite(a,out,bootmask(t).resize(a.size,Image.Resampling.LANCZOS))
 return out.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)

def native_text(im,p,lab,n=25,c=WHITE,anchor='lt'):
 d=ImageDraw.Draw(im);d.text(p,lab,font=font(n,1),fill=c,anchor=anchor,stroke_width=2,stroke_fill=(4,10,13));return im

def comparison(t):
 a=Image.new('RGB',(W,H),BG);native_text(a,(40,40),'同一个 15 号，位置关系变了',31)
 specs=[(98.4,(455,250,800,440),(35,176),'此前：15 在身前'),(100.8,(520,235,870,430),(655,176),'此时：15 在身后')]
 for st,box,pnt,lab in specs:
  marks=[('A10',56.8),('L15',57.64)] if st==100.8 else [('A10',56.8),('L15',57.1)]
  f=freeze(st,t,marks);crop=f.crop(box);h=round(crop.height/crop.width*590);a.paste(crop.resize((590,h),Image.Resampling.LANCZOS),pnt);native_text(a,(pnt[0]+8,125),lab,26,ATT if st==100.8 else MUT)
 if t>=58.1:native_text(a,(640,560),'接应点继续向门内延伸',28,WHITE,'mt')
 return a

SHOTS=[
(0,6.06,'live',83.2,None),(6.06,10.12,'board',None,'B1'),(10.12,13.52,'live',83.2,None),
(13.52,14.64,'live',86.6,None),(14.64,15.28,'freeze',88.6,None),(15.28,23.36,'board',None,'B2'),(23.36,24.96,'live',89.4,None),(24.96,27.8,'freeze',90.2,None),
(27.8,30.92,'live',90.6,None),(30.92,33.76,'board',None,'B3'),(33.76,35.66,'live',93.7,None),
(35.66,36.56,'live',95.6,None),(36.56,41.68,'board',None,'B4'),(41.68,44.56,'live',97.12,None),
(44.56,46.08,'freeze',98.4,None),(46.08,54.4,'board',None,'B5'),(54.4,56.8,'live',98.4,None),(56.8,59.2,'compare',None,None),(59.2,62.7,'live',98.4,None),
(62.7,68.96,'board',None,'B6'),(68.96,70.48,'live',102.08,None),
(70.48,71.6,'summary',83.2,'后场留接点'),(71.6,73.44,'summary',86.6,'内切后有人接'),(73.44,73.92,'summary',91.6,'中间一脚中转'),(73.92,76.08,'summary',95.2,'外侧继续推进'),(76.08,78.96,'summary',98.4,'门前接上回做'),
(78.96,99.36,'replay',83.2,None)]

def render(t,withcap=True):
 seg=next(s for s in SHOTS if s[0]-.0001<=t<s[1]-.0001);start,end,kind,st,k=seg;source_t=None;maskid=None
 if kind=='board':im=board(k,t)
 elif kind=='freeze':
  if st==88.6:marks=[('A34',14.64),('L14',14.8)];maskid='88.6_A34_L14_chroma_handROI'
  elif st==90.2:marks=[('A11',24.96),('L10',25.28)];maskid='90.2_A11_L10_chroma_handROI'
  else:marks=[]
  im=freeze(st,t,marks);source_t=st
  if st==90.2:
   native_text(im,(44,140),'下一接点：托雷拉',26,ATT)
   if t>=26.16:native_text(im,(44,182),'新的接近者，不是刚才的14号',26)
  if st==98.4:
   if t>=44.8:
    l=Image.new('RGBA',im.size);d=ImageDraw.Draw(l);trace(d,[(935,316),(755,384)],col(BALL,235),2.4,pr(t,44.8,45.4),None,True,1);im=Image.alpha_composite(im.convert('RGBA'),l).convert('RGB')
 elif kind=='compare':im=comparison(t);source_t=[98.4,100.8];maskid='both_frames_handROI_chroma'
 else:
  source_t=round((st+t-start)*25)/25;im=src(source_t).copy()
  if kind=='summary':
   # Fresh real-motion proofs for each responsibility, not a fake simultaneous formation.
   native_text(im,(42,105),'职责链回看',22,MUT);native_text(im,(42,145),k,30)
  elif kind=='live' and 1.2<t<5.8:native_text(im,(44,112),'从门将到门前',30)
  elif 27.8<=t<30.92:
   if t>=28.36:native_text(im,(44,140),'中间接应',26)
   if t>=30.12:native_text(im,(44,182),'转交下一点',26,ATT)
 if 13.6<=t<15.28:
  native_text(im,(44,140),'边线接点：34号',26)
  if t>=14.8:native_text(im,(44,182),'带向内侧',26,ATT)
 if withcap:
  cs=[c for c in T['captions'] if c['start_s']-.02<=t<=c['end_s']+.09]
  if cs:
   cap=cs[-1]['text'];d=ImageDraw.Draw(im);bb=d.textbbox((0,0),cap,font=font(33,1));ww=bb[2]-bb[0]
   lay=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(lay)
   # Narrow translucent subtitle bed only, no opaque strip across the action.
   ld.rounded_rectangle(((W-ww)/2-18,645,(W+ww)/2+18,699),radius=8,fill=(4,10,14,132));ld.text((W/2,655),cap,font=font(33,1),fill=WHITE,anchor='mt',stroke_width=2,stroke_fill=(0,0,0,230));im=Image.alpha_composite(im.convert('RGBA'),lay).convert('RGB')
 scene=next((s['id'] for s in T['scenes'] if s['output_start_s']-.0001<=t<s['output_end_s']-.0001),'S00')
 state={'frame':round(t*25),'output_s':round(t,2),'scene':scene,'kind':kind,'source_s':source_t,'board':k if kind=='board' else None,'mask':maskid,'active_cues':[c['event'] for c in CUES if c['output_s']<=t and c['board']==k]}
 if kind=='board' and k=='B5':state.update(ball_in_progress=round(pr(t,49.44,50.72),4),run_10_progress=round(pr(t,51.52,52.36),4),return_progress=round(pr(t,53.52,54.12),4))
 return im,state

def previews():
 ts=[.8,7.4,9.8,15.04,16.4,18.6,22.8,26.,31.4,32.4,39.5,41.4,45.4,47.8,50.25,51.4,52.,54.,55.6,58.,65.9,67.9,69.8,74.5,82.2,99.0]
 a=Image.new('RGB',(1280,math.ceil(len(ts)/4)*200),BG)
 for j,t in enumerate(ts):
  im,s=render(t);im.save(Q/f'preflight_{t:.2f}.jpg',quality=94);th=im.resize((320,180));a.paste(th,((j%4)*320,(j//4)*200));ImageDraw.Draw(a).text(((j%4)*320+6,(j//4)*200+182),f'{t:.2f}s {s["kind"]} {s["board"] or ""}',fill='white')
 a.save(Q/'PREFLIGHT_CONTACT.jpg',quality=94)

if __name__=='__main__':
 if '--preflight' in sys.argv:previews();print('PREFLIGHT_READY');sys.exit()
 outfile=O/'arsenal_full_phase_main.mp4'
 cmd=['ffmpeg','-v','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','25','-i','-','-i',str(O/'final_mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','18','-profile:v','high','-level:v','3.1','-pix_fmt','yuv420p','-c:a','aac','-profile:a','aac_low','-b:a','192k','-ar','48000','-ac','2','-disposition:a:0','default','-af','asetpts=PTS-STARTPTS','-t','99.36','-movflags','+faststart',str(outfile)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE);m=(O/'FRAME_SOURCE_STATE_MAP.jsonl').open('w');prev=None;motion=[]
 try:
  for n in range(N):
   t=n/FPS;im,state=render(t);p.stdin.write(im.tobytes());m.write(json.dumps(state,ensure_ascii=False)+'\n')
   small=np.asarray(im.resize((128,72)).convert('L')).astype(float);delta=None if prev is None else float(np.mean(abs(small-prev)));prev=small;motion.append({'frame':n,'t':t,'delta_luma_128x72':delta})
   if n%100==0:print(f'RENDER {n}/{N} t={t:.2f} {state["kind"]}',flush=True)
  p.stdin.close();code=p.wait();assert code==0,code
 finally:m.close()
 (Q/'RENDER_MOTION_METRICS.json').write_text(json.dumps(motion));print('RENDER_COMPLETE',outfile,flush=True)
