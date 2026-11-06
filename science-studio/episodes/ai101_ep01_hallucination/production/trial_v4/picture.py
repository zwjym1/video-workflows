# 试片画面（无字幕）：python3 picture.py <f0> <f1> -> part_<f0>.mp4
import sys,json,math,subprocess,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
EP='/workspace/science-studio/episodes/ai101_ep01_hallucination';A=EP+'/assets'
OK=A+'/chars/host_o';sys.path[:0]=['/workspace/oss/sprite-talk',OK,A+'/chars/fish','/workspace/science-studio/assets/fx_lib']
import pose_api as PO, fish_api as FA, fxkit as FX
from sprite_talk.mouth import audio_rms,mouth_levels
from sprite_talk.blink import blink_schedule
from sprite_talk.presets import ANING_DYN,aning_dyn_series,LinearPinWarp
FPS=30;W,H=1920,1080
TL=json.load(open('timeline.json'));LN=TL['lines'];DUR=TL['dur'];N=int(DUR*FPS)
SN={int(k):v for k,v in TL['shots'].items()}
OLD={l['n']:l for l in json.load(open('timeline_v1.json'))['lines']}
def remap(n,rt):
    # map new shot-relative time -> v1 shot-relative time (stage choreography was timed on v1 VO)
    if n not in OLD:return rt
    o=OLD[n];a=SN[n];lo=o['t0']-o['s0'];ln=a['t0']-a['s0'];do=o['t1']-o['t0'];dn=a['t1']-a['t0']
    if rt<ln:return rt*lo/ln if ln>0.01 else lo
    return lo+(rt-ln)*do/dn
FB='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';_f={}
def F(s):
    if s not in _f:_f[s]=ImageFont.truetype(FB,s,index=2)
    return _f[s]
INK=(34,30,48)
def ease_out(p):p=min(1,max(0,p));return 1-(1-p)**3
def ease_io(p):p=min(1,max(0,p));return 4*p**3 if p<.5 else 1-(-2*p+2)**3/2
def over(p):
    p=min(1,max(0,p))-1;return 1+3.2*p**3+2.2*p**2
# ---------- O geometry (EP kit)
def o_geom(p):
    rgba=cv2.imread(OK+'/'+PO.REG[p]['img'],-1);al=rgba[...,3];top=float(np.where((al>20).any(1))[0][0])
    M=np.array(PO.REG[p]['M']);chin=M@np.array([395.0,669.0,1])
    return dict(rgba=rgba,top=top,chin=float(chin[1]),hh=float(chin[1]-top))
OG={};OW={}
def hostO(p,lv,bl,dx,dy,h):
    if p not in OG:
        g=OG[p]=o_geom(p);OW[p]=LinearPinWarp(g['rgba'][...,3].shape,g['chin']-ANING_DYN['rigid_above_chin']*g['hh'],1079.0)
    g=OG[p];rgb=np.array(PO.frame(p,lv,bl));im=OW[p](np.dstack([rgb,g['rgba'][...,3]]),float(dx),float(dy))
    pi=Image.fromarray(np.clip(im,0,255).astype(np.uint8),'RGBA');s=h/1080
    return pi.resize((int(pi.width*s),int(pi.height*s)),Image.BILINEAR)
# ---------- audio-driven series
def series(wav,who):
    rms=audio_rms(wav,FPS,DUR);lv,env=mouth_levels(rms,N,FPS,None)
    spk=np.zeros(N,bool)
    for l in LN:
        if l['who']==who:spk[int(l['t0']*FPS):int(l['t1']*FPS)+2]=True
    return lv*spk,env*spk,spk
_M=np.load('mouth.npz');_E=np.load('mouth_env.npz')
OLV=np.r_[_M['O'],np.zeros(N)][:N];FLV=np.r_[_M['F'],np.zeros(N)][:N]
OENV=np.clip(np.r_[_E['O'],np.zeros(N)][:N],0,1.5)/1.5;FENV=np.clip(np.r_[_E['F'],np.zeros(N)][:N],0,1.5)/1.5
OSPK=OLV>=0
for l in LN:
    if l['who']=='O':pass
OSPK=np.zeros(N,bool)
for l in LN:
    if l['who']=='O':OSPK[int(l['t0']*FPS):int(l['t1']*FPS)+1]=True
_HH=float(np.mean([o_geom(p)['hh'] for p in PO.REG]))
ODX,ODY,_=aning_dyn_series(N,_HH,(OENV>0.08)&OSPK,FPS,ANING_DYN,amp=1.0,env=OENV)
OBL=blink_schedule(N,FPS,seed=11);FBL=blink_schedule(N,FPS,seed=29)
FENS=np.convolve(FENV,np.ones(5)/5,'same')
LVN={0:'X',1:'open_s',2:'open_l'};FLVN={0:'X',1:'open_s',2:'open_l'}
# v4: script_v3/shots_v3.json drives poses
SJ=json.load(open(EP+'/script_v3/shots_v3.json'))['shots'];SJ={int(k):v for k,v in SJ.items()}
FMD=A+'/chars/fish/mouth_v1/';_fm={}
def fish_img(p,lv,bl):
    k=(p,lv,bl)
    if k not in _fm:
        im=Image.open(FMD+f'{p}__{lv}.png').convert('RGBA').copy()
        if bl and FA.REG['poses'][p].get('blink_ok'):
            q=FA.REG['poses'][p];s_=q['scale'];ox,oy=q['face_xy'];key='eyes_half' if bl==1 else 'eyes_closed'
            pt=FA._l('patches/'+key+'.png');x,y=FA.REG['patches'][key]['xy'];pt=pt.resize((int(pt.width*s_),int(pt.height*s_)),Image.BICUBIC)
            im.alpha_composite(pt,(int(ox+x*s_),int(oy+y*s_)))
        _fm[k]=im
    return _fm[k]
def opose_at(n,t):
    p=SJ[n]['o'][0]['pose']
    for c in SJ[n]['o']:
        if t>=c['t']:p=c['pose']
    return p
# ---------- shot design
S=OLD
OPOSE={1:'pose_talk_point',2:'pose_talk_idle',3:'pose_deadpan',4:'pose_talk_idle',5:'pose_talk_point',6:'pose_think',7:'pose_talk_idle',8:'pose_talk_point',9:'pose_peace',10:'pose_deadpan',11:'pose_peace',12:'pose_think',13:'pose_talk_point',14:'pose_talk_idle',15:'pose_think',16:'pose_talk_idle',17:'pose_deadpan',18:'pose_talk_point',19:'pose_think',20:'pose_deadpan'}
FPOSE={n:v['fish'][0]['pose'] for n,v in SJ.items() if v['fish']}
def shot_at(t):
    for k,v in SN.items():
        if v['s0']<=t<v['s1']:return k
    return max(SN)
_im={}
def img(p,w=None,h=None):
    k=(p,w,h)
    if k not in _im:
        im=Image.open(p).convert('RGBA')
        if w and not h:im=im.resize((w,int(im.height*w/im.width)),Image.LANCZOS)
        elif h and not w:im=im.resize((int(im.width*h/im.height),h),Image.LANCZOS)
        a=np.array(im);ys,xs=np.where(a[...,3]>8)
        if len(xs) and (xs.min()>4 or ys.min()>4):im=im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
        _im[k]=im
    return _im[k]
PR=A+'/props/';NW=A+'/news/'
def paste(c,im,cx,cy,s=1.0,rot=0,alpha=1.0):
    if s<=0.01 or alpha<=0.01:return
    e=im
    if abs(s-1)>1e-3:e=e.resize((max(1,int(e.width*s)),max(1,int(e.height*s))),Image.BICUBIC)
    if rot:e=e.rotate(rot,expand=True,resample=Image.BICUBIC)
    if alpha<1:a=e.split()[3].point(lambda v:int(v*alpha));e=e.copy();e.putalpha(a)
    c.alpha_composite(e,(int(cx-e.width/2),int(cy-e.height/2)))
def popin(c,im,cx,cy,rt,t0,s=1.0,rot=0,dur=0.3):
    if rt<t0:return
    paste(c,im,cx,cy,s*over((rt-t0)/dur),rot)
_cc={}
def card(text,size=60,bg=(255,255,250),fg=INK,pad=30,r=20,border=6):
    k=(text,size,bg,fg)
    if k not in _cc:
        f=F(size);w=int(ImageDraw.Draw(Image.new('RGB',(1,1))).textlength(text,font=f));h=int(size*1.35)
        im=Image.new('RGBA',(w+2*pad+12,h+pad+14));d=ImageDraw.Draw(im)
        d.rounded_rectangle((8,12,im.width-1,im.height-1),r,fill=(0,0,0,90))
        d.rounded_rectangle((0,0,im.width-9,im.height-13),r,fill=bg,outline=INK,width=border)
        d.text(((im.width-9)/2,(im.height-13)/2),text,font=f,fill=fg,anchor='mm');_cc[k]=im
    return _cc[k]
def bigword(text,size=120,col=(255,214,64)):
    k=('B',text,size,col)
    if k not in _cc:
        f=F(size);w=int(ImageDraw.Draw(Image.new('RGB',(1,1))).textlength(text,font=f))
        im=Image.new('RGBA',(w+60,int(size*1.5)));ImageDraw.Draw(im).text((30,im.height/2),text,font=f,fill=col,anchor='lm',stroke_width=10,stroke_fill=INK);_cc[k]=im
    return _cc[k]
def browser(path,crop,w,title):
    k=('BR',path,crop,w)
    if k not in _cc:
        sc=Image.open(path).convert('RGB').crop(crop);sc=sc.resize((w,int(sc.height*w/sc.width)),Image.LANCZOS)
        im=Image.new('RGBA',(w+24,sc.height+76));d=ImageDraw.Draw(im)
        d.rounded_rectangle((10,14,im.width-1,im.height-1),18,fill=(0,0,0,100));d.rounded_rectangle((0,0,im.width-11,im.height-15),18,fill=(236,238,244),outline=INK,width=5)
        for i,cl in enumerate([(255,95,87),(255,189,46),(40,201,64)]):d.ellipse((22+i*30,18,40+i*30,36),fill=cl)
        d.rounded_rectangle((130,14,im.width-40,42),10,fill=(255,255,255));d.text((146,28),title,font=F(18),fill=(90,90,100),anchor='lm')
        im.paste(sc,(6,52));_cc[k]=im
    return _cc[k]
def source_tag(c,path,crop,label,rt,t0=0.4):
    c=TOPL[0]
    if rt<t0:return
    th=browser(path,crop,250,label);p=ease_out((rt-t0)/0.35)
    x=W-th.width//2-150+int((1-p)*500);y=20
    paste(c,th,x,y+th.height//2,1.0,-3)
    paste(c,card('来源：'+label,22,(255,240,160)),x-th.width//2-60,y+th.height-20)
CNT=[0];TOPL=[None]
def counter(c,val,flip_t,rt):
    # 翻车计数卡 左上
    v=val if rt>=flip_t else val-1;p=over((rt-flip_t)/0.3) if rt>=flip_t else 1
    paste(c,card(f'翻车计数  {v}',40,(255,120,100),(255,255,255)),210,90,p if rt>=flip_t else 1)
# fx clips
_fxc={}
def fxc(name,**kw):
    k=(name,tuple(kw.items()))
    if k not in _fxc:_fxc[k]=FX.CLIPS[name](**kw)
    return _fxc[k]
def fxo(c,name,rt,t0,pos,s=1.0,ease='overshoot',**kw):
    cl=fxc(name,**kw);u=rt-t0
    if 0<=u<=cl.dur:FX.overlay(c,cl,u,pos,s,ease)
# ---------- stage drawing per shot (center area, everything except characters)
SX=820  # stage centre x when O right only
def stage(n,rt,c):
    L=S[n];d=L['t1']-L['t0'];lead=L['t0']-L['s0'];tv=rt-lead  # tv: time since VO start
    if n==1:
        br=browser(NW+'01_cctv_bjd_20261101.png',(0,0,1280,1600),720,'news.bjd.com.cn · 2026-11-01')
        z=1.0+0.01*rt;paste(c,br,640,545,z,-2)
        tA=lead+1.85;tB=lead+3.8
        fxo(c,'impact_star',rt,tA-0.05,(330,330),0.8);fxo(c,'impact_star',rt,tB-0.05,(1230,760),0.8)
        popin(c,bigword('推荐的餐馆：不存在',84,(255,255,255)),700,420,rt,tA,1.0,-4)
        popin(c,bigword('推荐的索道：停运两年',84,(255,214,64)),720,700,rt,tB,1.0,3)
    elif n==2:
        sc=img(PR+'p01_scroll.png',h=640);fl=0.02*math.sin(rt*3)
        popin(c,sc,980,520,rt,0.25,1.0,6+fl*50)
        fxo(c,'sparkle_burst',rt,0.35,(980,380),1.4);fxo(c,'twinkle',rt,1.0,(1180,300),1.2);fxo(c,'twinkle',rt,1.8,(820,720),1.0)
        fxo(c,'sparkle_burst',rt,2.6,(1120,620),1.0)
    elif n==3:
        sc=img(PR+'p01_scroll.png',h=640);paste(c,sc,930,540,1.0,4)
        for i in range(3):popin(c,bigword('？',90,(240,60,60)),830+i*110,380+i*150,rt,lead+0.35+i*0.4,1.0,-8+i*8)
        counter(TOPL[0],1,lead+1.6,rt)
    elif n==4:
        m=img(PR+'p02b_local_map.png',h=620);paste(c,m,SX,560,1.0+0.02*rt,0)
        popin(c,card('北京',44,(255,255,255)),SX-200,330,rt,0.0,1.0)
        popin(c,img(PR+'p02c_map_pin.png',h=170),SX+180,460,rt,lead+0.1,1.0)
        popin(c,card('济南',54,(255,214,64)),SX+180,330,rt,lead+0.25,1.0)
        fxo(c,'shockwave',rt,lead+0.15,(SX+180,540),1.0)
    elif n==5:
        sw=img(PR+'p03_stopwatch.png',h=560);paste(c,sw,SX-60,600,1.0,0)
        k1=lead+0.1;k2=lead+3.0
        if tv<2.2:txt,col='AI：8 分钟',(255,255,255)
        elif tv<3.0:
            v=8+int(29*ease_io((tv-2.2)/0.8)) ;txt,col=f'实际：{v} 分钟',(255,214,64)
        else:txt,col='实际：37 分钟',(255,120,100)
        s=1.0 if not(3.0<=tv<3.3) else 1+0.15*math.sin((tv-3)/0.3*math.pi)
        paste(c,card(txt,64,col),SX-60,250,s)
        if tv>=3.0:fxo(c,'impact_star',rt,lead+3.0,(SX+170,230),0.7)
        source_tag(c,NW+'02_jinan_qlwb.png',(80,0,1200,700),'齐鲁晚报',rt)
    elif n==6:
        popin(c,card('地铁 · 直达站',52,(40,120,220),(255,255,255)),SX,300,rt,0.0)
        cs=img(PR+'p04_construction.png',h=540);u=ease_out((rt-lead-0.5)/0.35)
        if rt>lead+0.5:paste(c,cs,SX,620-int((1-u)*500),1.0)
        fxo(c,'dust_poof',rt,lead+0.85,(SX,860),1.6)
    elif n==7:
        bp=img(PR+'p05_boarding_pass.png',w=900);tf=lead+2.3
        u=(rt-tf)/0.4
        sx=1.0 if u<0 else (abs(math.cos(min(1,u)*math.pi)))
        face=bp if u<0.5 else bp.transpose(Image.FLIP_LEFT_RIGHT)
        e=face.resize((max(2,int(face.width*max(sx,0.02))),face.height));paste(c,e,SX,560)
        if u<0.5:paste(c,card('直飞',60,(255,214,64)),SX,330,sx if u>=0 else 1)
        else:
            popin(c,card('这个航班号 → 另一条航线',50,(255,120,100),(255,255,255)),SX,330,rt,tf+0.2)
            fxo(c,'cross_draw',rt,tf+0.45,(SX+300,560),1.3)
        source_tag(c,NW+'03_jinan_flight_dzplus.png',(0,0,1280,900),'大众新闻',rt)
    elif n==8:
        b=card('！！！',90,(255,255,255),(240,60,60))
        popin(c,b,900,300,rt,lead+0.2,1.0,-6)
        fxo(c,'pop_exclaim',rt,lead+1.2,(1040,520),1.2);fxo(c,'pop_exclaim',rt,lead+2.0,(780,560),1.0)
        fxo(c,'impact_star',rt,lead+0.15,(620,700),1.3)
        if tv>2.7:popin(c,card('从不说“我猜”',50,(255,214,64)),900,820,rt,lead+2.7)
    elif n==9:
        fxo(c,'pop_question',rt,lead+0.05,(SX,420),1.6)
        popin(c,card('这个毛病叫……',56,(255,214,64)),SX,300,rt,lead+0.1,1.0,-3)
        t=lead+1.0;cd=card('幻觉 ＝ 一本正经地胡说',84,(255,255,250))
        if rt>t:fxo(c,'marker_highlight',rt,t+0.2,(SX,560+20),2.0,ease=None)
        z=1.0 if rt<t else 1+0.08*math.sin(min(1,(rt-t)/0.35)*math.pi)
        popin(c,cd,SX,540,rt,t,z)
        popin(c,card('定义参考：OpenAI《Why language models hallucinate》',26,(235,235,240)),SX,690,rt,t+0.5)
        source_tag(c,NW+'05_openai_blog.png',(0,0,1280,900),'OpenAI 博客',rt,t+0.6)
    elif n==10:
        fxo(c,'sweat_drop',rt,lead+0.3,(620,250),1.2);fxo(c,'sweat_drop',rt,lead+1.6,(560,240),1.0)
        popin(c,card('记性不好？',54,(255,255,255)),980,330,rt,lead+1.8,1.0,4)
    elif n==11:
        for i,(lab,col) in enumerate([('①',(255,214,64)),('②',(120,200,255))]):
            popin(c,card(lab+'  ？？？',64,col),SX+90,420+i*200,rt,lead+1.5+i*0.35)
        fxo(c,'sparkle_burst',rt,lead+1.5,(SX,420),1.0)
    elif n==12:
        popin(c,card('① 这些话从哪来？',56,(255,214,64)),980,360,rt,lead+0.05,1.0,-3)
        fxo(c,'pop_question',rt,lead+1.6,(1180,560),1.3)
    elif n==13:
        tL=lead+0.25;tR=lead+1.4
        popin(c,card('查资料',60,(255,255,255)),SX-260,520,rt,tL)
        popin(c,card('接龙',60,(255,214,64)),SX+260,520,rt,tR)
        fxo(c,'cross_draw',rt,tL+0.6,(SX-260,520),1.3,ease=None);fxo(c,'check_draw',rt,tR+0.3,(SX+260,520),1.3,ease=None)
        if rt>tR:z=1+0.07*math.sin(min(1,(rt-tR)/0.35)*math.pi);c_=c.copy();c.paste(c_.resize((int(W*z),int(H*z))).crop((int((W*z-W)/2),int((H*z-H)/2),int((W*z-W)/2)+W,int((H*z-H)/2)+H)))
    elif n==14:
        # 逐字生成 + 候选概率条
        txt='香山脚下有家百年老店，招牌菜是……';box=Image.new('RGBA',(1060,130));d=ImageDraw.Draw(box)
        d.rounded_rectangle((0,0,1059,129),24,fill=(255,255,255),outline=INK,width=6)
        k=int(max(0,tv-0.6)/0.32);k=min(k,len(txt));shown=txt[:k]
        d.text((36,65),shown+('▍' if int(rt*3)%2==0 else ''),font=F(52),fill=INK,anchor='lm');paste(c,box,SX,720)
        if k<len(txt):
            nxt=txt[k];cands=[(nxt,0.62),('家' if nxt!='家' else '座',0.23),('的',0.15)];ph=(max(0,tv-0.6)%0.32)/0.32
            for i,(ch,p) in enumerate(cands):
                x=SX-300+i*300;bh=int(220*p*ease_out(ph*2))
                cb=Image.new('RGBA',(200,300));dd=ImageDraw.Draw(cb)
                dd.rounded_rectangle((60,260-bh,140,260),10,fill=(255,214,64) if i==0 else (200,205,220),outline=INK,width=4)
                dd.text((100,285),f'{int(p*100)}%',font=F(26),fill=INK,anchor='mm')
                paste(c,cb,x,460);paste(c,card(ch,50,(255,255,255) if i else (255,214,64)),x,270)
        popin(c,card('猜下一个字',40,(120,200,255)),SX,140,rt,lead+0.2)
        paste(c,card('演示 · 非真实数据',26,(235,235,240)),SX+420,840)
    elif n==15:
        br=img(PR+'p18_brain_section.png',h=620);popin(c,br,SX,560,rt,0.05,1.0)
        if tv>1.2:fxo(c,'circle_draw',rt,lead+1.3,(SX,560),1.3,ease=None)
        fxo(c,'pop_question',rt,lead+1.9,(SX+260,300),1.0)
def stage_new(n,rt,c):
    L=SN[n];lead=L['t0']-L['s0'];tv=rt-lead
    if n==16:
        pz=img(PR+'p07_puzzle.png',h=560);popin(c,pz,SX,560,rt,0.0)
        fxo(c,'check_draw',rt,lead+0.9,(SX+250,330),1.2,ease=None)
        popin(c,card('资料多 → 又准又顺',46,(120,220,140)),SX,180,rt,lead+0.3)
    elif n==17:
        pz=img(PR+'p07_puzzle.png',h=560);paste(c,pz,SX,560)
        u=ease_out((tv-1.2)/0.5);popin(c,card('听起来很像',50,(255,214,64)),SX+int((1-u)*520),560,rt,lead+1.0,1.0,8*(1-u))
        popin(c,card('资料空着 → 照样接',46,(255,120,100),(255,255,255)),SX,180,rt,lead+0.2)
        if tv>2.4:fxo(c,'wavy_underline',rt,lead+2.4,(SX,640),1.4,ease=None)
    elif n==18:
        m=img(PR+'p02b_local_map.png',h=600);paste(c,m,SX,600,1.0)
        for i,w in enumerate(['湖景','网红咖啡','人均 68']):
            popin(c,card(w,44,(255,255,255)),SX-300+i*300,300,rt,lead+0.4+i*0.45,1.0,(-1)**i*5)
            fxo(c,'slash',rt,lead+0.6+i*0.45,(SX-300+i*300,300),0.9)
        popin(c,img(PR+'p02c_map_pin.png',h=150),SX,600,rt,lead+2.4)
        popin(c,card('拼出来的“新地点”',42,(255,214,64)),SX,760,rt,lead+2.6)
    elif n==19:
        sg=img(PR+'p08_cafe_sign.png',h=480);u=ease_out((tv-0.9)/0.35)
        for i,w in enumerate(['网红咖啡馆','湖景','人均68']):
            t0=lead+0.05+i*0.3
            if rt>=t0:
                p=ease_out((rt-t0-0.35)/0.3);x=980+(i-1)*260;y=260;paste(c,card(w,44,(255,255,255)),x+(980-x)*p,y+(520-y)*p,over((rt-t0)/0.3)*(1-0.7*p))
        if tv>0.9:paste(c,sg,980,520,over(u));fxo(c,'sparkle_burst',rt,lead+0.95,(980,420),1.2)
    elif n==20:
        rv=img(PR+'p09b_reservoir_dry.png',h=640);sg=img(PR+'p08_cafe_sign.png',h=480)
        if tv<0.7:paste(c,sg,SX,520)
        else:paste(c,rv,SX,560,over((tv-0.7)/0.35))
        fxo(c,'smoke_puff',rt,lead+0.6,(SX,520),1.6)
        popin(c,card('像，但不在',56,(255,120,100),(255,255,255)),SX,200,rt,lead+0.2,1.0,-3)
        source_tag(c,NW+'04_xiamen_xmnn.png',(0,0,1280,900),'厦门网',rt,lead+1.4)
# background
bg=Image.new('RGB',(W,H),(252,246,236));d=ImageDraw.Draw(bg)
for y in range(18,H,36):
    for x in range(18,W,36):d.ellipse((x-2,y-2,x+2,y+2),fill=(236,226,210))
BG=bg.convert('RGBA')
CHTAB={k:'① 从哪冒出来' for k in range(12,21)};CHTAB[11]='？'
LN3=[l for l in LN if l['shot']==3]
def STG(n,rt,c):
    if n in OLD:stage(n,remap(n,rt),c)
    else:stage_new(n,rt,c)
def draw(f):
    t=f/FPS;n=shot_at(t);rt=t-SN[n]['s0'];c=BG.copy()
    # stage with crossfade from previous shot
    TOPL[0]=Image.new('RGBA',(W,H));st=Image.new('RGBA',(W,H));STG(n,rt,st)
    XF=0.14
    if rt<XF and n>1:
        p=ease_io(rt/XF);pv=Image.new('RGBA',(W,H));keep=TOPL[0];TOPL[0]=Image.new('RGBA',(W,H));STG(n-1,t-SN[n-1]['s0'],pv);TOPL[0]=keep
        sc=1-0.25*p;pv=pv.resize((int(W*sc),int(H*sc)),Image.BILINEAR);a=pv.split()[3].point(lambda v:int(v*(1-p)));pv.putalpha(a)
        tmp=Image.new('RGBA',(W,H));tmp.alpha_composite(pv,(int(SX-SX*sc),int(560-560*sc)));tmp.alpha_composite(st);st=tmp
    Z=1.0 if n==1 else 1.22;cx0,cy0=(SX,560)
    st=st.resize((int(W*Z),int(H*Z)),Image.BICUBIC);st=st.crop((int(cx0*Z-cx0),int(cy0*Z-cy0),int(cx0*Z-cx0)+W,int(cy0*Z-cy0)+H))
    c.alpha_composite(st)
    # fish (left)
    fp=FPOSE.get(n);ex=0
    if not fp and (n-1) in FPOSE and rt<0.35:fp=FPOSE[n-1];ex=ease_io(rt/0.35)
    if fp:
        lv=FLVN[int(FLV[f])];bl=FBL.get(f,0) if FA.REG['poses'][fp].get('blink_ok') else 0
        fi=fish_img(fp,lv,bl);hh=820;fi=fi.resize((int(fi.width*hh/1080),hh),Image.BILINEAR)
        enter=ease_out((t-SN[n]['s0'])/0.35) if (n-1 not in FPOSE) else 1
        bob=-10*FENS[f]-4*math.sin(t*2.2)
        x=260-int((1-enter)*600)-int(ex*700);c.alpha_composite(fi,(x-fi.width//2+30,H-hh+40+int(bob)))
    # O (right) hard pose cut
    p=opose_at(n,t)
    o=hostO(p,LVN[int(OLV[f])],OBL.get(f,0),ODX[f],ODY[f],880)
    c.alpha_composite(o,(W-o.width+60,H-o.height+60))
    c.alpha_composite(TOPL[0])
    # chapter tab
    if n in CHTAB:
        s0=SN[11]['s0'];u=ease_out((t-s0-1.2)/0.4) if n==11 else 1
        if n>=12:u=1
        tab=card(CHTAB[n] if n>=12 else '两个毛病',32,(64,64,80),(255,255,255),20,14,3)
        paste(c,tab,W-tab.width//2-30+int((1-u)*400),56)
    if n>=4:paste(c,card('翻车计数  1',40,(255,120,100),(255,255,255)),210,90)
    # global camera drift + punch on shot1/9
    z=1.0+0.012*math.sin(t*0.35)
    if n==1 and rt<0.4:z+=0.06*math.sin(rt/0.4*math.pi)
    if abs(z-1)>1e-4:
        cw,ch=int(W/z),int(H/z);c=c.crop(((W-cw)//2,(H-ch)//2,(W-cw)//2+cw,(H-ch)//2+ch)).resize((W,H),Image.BILINEAR)
    return c.convert('RGB')
if __name__=='__main__':
    if sys.argv[1]=='-1':
        for t in map(float,sys.argv[2:]):draw(int(t*FPS)).save(f'/tmp/ep01_chk_{t}.jpg')
        sys.exit()
    f0,f1=int(sys.argv[1]),min(int(sys.argv[2]),N)
    p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','17','-preset','fast','-pix_fmt','yuv420p',f'part_{f0:05d}.mp4'],stdin=subprocess.PIPE)
    for f in range(f0,f1):p.stdin.write(draw(f).tobytes())
    p.stdin.close();p.wait()
