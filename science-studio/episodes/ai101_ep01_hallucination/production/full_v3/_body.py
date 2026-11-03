# ======== 全片引擎：画面元素 / 姿势 / 计数 / 章节 tab 全部由 script_v3/shots_v3.json 驱动 ========
SJ={int(k):v for k,v in json.load(open(EP+'/script_v3/shots_v3.json'))['shots'].items()}
G=json.load(open(EP+'/script_v3/shots_v3.json'))['global']
_M=np.load('mouth.npz');_E=np.load('mouth_env.npz')
OLV=np.r_[_M['O'],np.zeros(N)][:N];FLV=np.r_[_M['F'],np.zeros(N)][:N]
OENV=np.clip(np.r_[_E['O'],np.zeros(N)][:N],0,1.5)/1.5;FENV=np.clip(np.r_[_E['F'],np.zeros(N)][:N],0,1.5)/1.5
OSPK=np.zeros(N,bool)
for l in LN:
    if l['who']=='O':OSPK[int(l['t0']*FPS):int(l['t1']*FPS)+1]=True
_HH=float(np.mean([o_geom(p)['hh'] for p in PO.REG]))
ODX,ODY,_=aning_dyn_series(N,_HH,(OENV>0.08)&OSPK,FPS,ANING_DYN,amp=1.0,env=OENV)
_BG=json.load(open('beat_grid.json'));BOFF,BPER=_BG['offset'],_BG['period'];STEP=0.17
def tq(t):
    '''拍点步进时间：每拍的进度压进拍后 0.17s，其余时间停住（连续动作一步一步卡拍）'''
    k=math.floor((t-BOFF)/BPER);b=BOFF+k*BPER;return b+min(BPER,(t-b)*BPER/STEP)
def tbeat(t):return BOFF+math.floor((t-BOFF)/BPER)*BPER
def bon(t):return math.floor((t-BOFF)/BPER)%2==0
def beat_blinks(D):
    ev=[];fs=sorted(D)
    for f in fs:
        if ev and f==ev[-1][-1]+1:ev[-1].append(f)
        else:ev.append([f])
    out={}
    for e in ev:
        t=e[0]/FPS;b=BOFF+round((t-BOFF)/BPER)*BPER;sh=int(round(b*FPS))-e[0]
        for f in e:out[f+sh]=D[f]
    return out
OBL=beat_blinks(blink_schedule(N,FPS,seed=11));FBL=beat_blinks(blink_schedule(N,FPS,seed=29))
FENS=np.convolve(FENV,np.ones(5)/5,'same')
LVN={0:'X',1:'open_s',2:'open_l'}
FMD=A+'/chars/fish/mouth_v1/';_fm={}
def fish_img(p,lv,bl):
    k=(p,lv,bl)
    if k not in _fm:
        im=Image.open(FMD+f'{p}__{lv}.png').convert('RGBA').copy()
        if p=='fish_f14_sign_idk':   # 牌面字直接画进鱼图，随鱼一起动
            dd=ImageDraw.Draw(im);dd.text((415,812),'不知道',font=F(118),fill=INK,anchor='mm')
        q=FA.REG['poses'][p]
        if bl and q.get('blink_ok'):
            s_=q['scale'];ox,oy=q['face_xy'];key='eyes_half' if bl==1 else 'eyes_closed'
            pt=FA._l('patches/'+key+'.png');x,y=FA.REG['patches'][key]['xy'];pt=pt.resize((int(pt.width*s_),int(pt.height*s_)),Image.BICUBIC)
            im.alpha_composite(pt,(int(ox+x*s_),int(oy+y*s_)))
        _fm[k]=im
    return _fm[k]
def cue_at(lst,t):
    p=None
    for c in lst:
        if t>=c['t']:p=c
    return p or (lst[0] if lst else None)
def shot_at(t):
    for k,v in SN.items():
        if v['s0']<=t<v['s1']:return k
    return max(SN)
FM=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22,index=7)
_fmc={}
def FMs(s):
    if s not in _fmc:_fmc[s]=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',s,index=7)
    return _fmc[s]
def wrap(text,font,w):
    out=[]
    for para in text.split('\n'):
        cur=''
        for ch in para:
            if font.getlength(cur+ch)>w:out.append(cur);cur=ch
            else:cur+=ch
        out.append(cur)
    return out
def term(e,t):
    """终端窗口：原文逐字出现（cps）+ marker 高亮"""
    w,h=e['w'],e['h'];fs=e.get('fs',22);f=FMs(fs);lh=int(fs*1.45)
    im=Image.new('RGBA',(w+14,h+16));d=ImageDraw.Draw(im)
    d.rounded_rectangle((8,10,w+13,h+15),16,fill=(0,0,0,90));d.rounded_rectangle((0,0,w,h),16,fill=(30,32,44),outline=INK,width=4)
    for i,cl in enumerate([(255,95,87),(255,189,46),(40,201,64)]):d.ellipse((16+i*24,13,30+i*24,27),fill=cl)
    d.text((100,20),e.get('title',''),font=F(18),fill=(200,200,215),anchor='lm')
    text=e['text'];cps=e.get('cps',0);k=len(text) if not cps else int(max(0,tq(t)-tq(e['t']))*cps)
    lines=wrap(text,f,w-36);maxl=(h-50)//lh
    # reveal
    shown=[];left=k
    for L in lines:
        if left<=0:break
        shown.append(L[:left]);left-=len(L)+1
    shown=shown[-maxl:] if e.get('scroll',True) else shown[:maxl]
    y=44
    for L in shown:
        x=18
        for hl in e.get('hl',[]):
            if tq(t)>=hl['t'] and hl['s'] in L:
                i0=L.index(hl['s']);x0=x+f.getlength(L[:i0]);x1=x0+f.getlength(hl['s'])*min(1,(tq(t)-hl['t'])/0.3)
                d.rectangle((x0-2,y+2,x1+2,y+lh-2),fill=tuple(hl.get('col',(255,214,64)))+(170,))
        col=(235,235,240)
        d.text((x,y),L,font=f,fill=col);y+=lh
    if cps and k<len(text) and bon(t):d.rectangle((18,y+4,30,y+lh-4),fill=(235,235,240))
    return im
_st={}
def stamp_im(text,col,size):
    k=(text,tuple(col),size)
    if k not in _st:
        f=F(size);tw=int(f.getlength(text));im=Image.new('RGBA',(tw+60,int(size*1.6)));d=ImageDraw.Draw(im)
        d.rounded_rectangle((4,4,im.width-5,im.height-5),14,outline=tuple(col)+(235,),width=8)
        d.text((im.width/2,im.height/2),text,font=f,fill=tuple(col)+(235,),anchor='mm');_st[k]=im
    return _st[k]
def phone(e,t):
    """手机地图搜索演示（仿制，标「演示」）"""
    pw,ph=420,820;im=Image.new('RGBA',(pw+20,ph+20));d=ImageDraw.Draw(im)
    d.rounded_rectangle((10,14,pw+19,ph+19),56,fill=(0,0,0,90));d.rounded_rectangle((0,0,pw,ph),56,fill=(28,28,34))
    scr=Image.open(e['map']).convert('RGB').resize((pw-36,ph-60));im.paste(scr,(18,30));d=ImageDraw.Draw(im)
    d.rounded_rectangle((150,40,270,62),11,fill=(28,28,34))
    u=tq(t)-e['t']
    for q in e['seq']:
        a=q['t']-e['t']
        if u<a:continue
        txt=q['q'][:int((u-a)*8)+1];d.rounded_rectangle((36,84,pw-36,140),22,fill=(255,255,255),outline=(200,200,210),width=2)
        d.text((60,112),'🔍 '+txt if False else txt,font=F(26),fill=INK,anchor='lm')
        if u>a+len(q['q'])/8+0.4:
            ok=q['ok'];d.rounded_rectangle((36,ph-250,pw-36,ph-60),24,fill=(255,255,255),outline=(200,200,210),width=2)
            d.text((pw/2,ph-185),q['q'],font=F(28),fill=INK,anchor='mm')
            d.text((pw/2,ph-120),'✓ 找到地点' if ok else '✗ 未找到相关地点',font=F(30),fill=(40,160,80) if ok else (220,60,60),anchor='mm')
            if ok:d.ellipse((pw/2-18,ph/2-60,pw/2+18,ph/2-24),fill=(230,60,60),outline=(255,255,255),width=4)
    d.text((40,ph-34),'© OpenStreetMap contributors',font=F(14),fill=(80,80,90),anchor='lm',stroke_width=2,stroke_fill=(255,255,255))
    d.rounded_rectangle((pw-140,ph-50,pw-30,ph-18),10,fill=(255,214,64));d.text((pw-85,ph-34),'演示',font=F(22),fill=INK,anchor='mm')
    return im
def ruler_map(e,t):
    k=('RM',e['map'],e['w'])
    if k not in _cc:
        m=Image.open(e['map']).convert('RGBA');s=e['w']/m.width;_cc[k]=(m.resize((e['w'],int(m.height*s)),Image.LANCZOS),s)
    m,s=_cc[k];m=m.copy();d=ImageDraw.Draw(m);ax,ay,bx,by=[v*s for v in e['pts']]
    for (x,y),lab in (((ax,ay),e['a']),((bx,by),e['b'])):
        d.ellipse((x-12,y-12,x+12,y+12),fill=(230,60,60),outline=(255,255,255),width=4);d.text((x+18,y),lab,font=F(28),fill=INK,anchor='lm',stroke_width=4,stroke_fill=(255,255,255))
    p=ease_io((t-e['t_draw'])/e.get('dur',0.8))
    if p>0:
        x=ax+(bx-ax)*p;y=ay+(by-ay)*p;d.line((ax,ay,x,y),fill=(230,60,60),width=7)
        if p>=1:d.text(((ax+bx)/2+20,(ay+by)/2),e['label'],font=F(40),fill=(230,60,60),anchor='lm',stroke_width=6,stroke_fill=(255,255,255))
    d.text((m.width-10,m.height-8),'© OpenStreetMap contributors',font=F(16),fill=(80,80,90),anchor='rd',stroke_width=3,stroke_fill=(255,255,255))
    fr=Image.new('RGBA',(m.width+16,m.height+16));dd=ImageDraw.Draw(fr);dd.rounded_rectangle((0,0,m.width+15,m.height+15),14,fill=(255,255,255),outline=INK,width=5);fr.alpha_composite(m,(8,8));return fr
def get_im(e,t):
    k=e['k']
    if k=='img':return img(PR+e['src'] if not e['src'].startswith('/') else e['src'],w=e.get('w'),h=e.get('h'))
    if k=='card':return card(e['text'],e.get('size',56),tuple(e.get('bg',(255,255,255))),tuple(e.get('fg',INK)))
    if k=='big':return bigword(e['text'],e.get('size',120),tuple(e.get('col',(255,214,64))))
    if k=='browser':return browser(NW+e['src'],tuple(e['crop']),e['w'],e['title'])
    if k=='term':return term(e,t)
    if k=='stamp':return stamp_im(e['text'],e.get('col',(220,40,40)),e.get('size',64))
    if k=='phone':return phone(e,t)
    if k=='ruler_map':return ruler_map(e,t)
    if k=='roll':
        if t<e['r0']:txt,col=e['a'],e.get('col_a',(255,255,255))
        elif t<e['r1']:v=e['va']+int((e['vb']-e['va'])*ease_io((t-e['r0'])/(e['r1']-e['r0'])));txt,col=e['fmt'].format(v),(255,214,64)
        else:txt,col=e['b'],e.get('col_b',(255,120,100))
        return card(txt,e.get('size',64),tuple(col))
    return None
def anim(e,t):
    """返回 (dx,dy,scale,alpha,rot) 入场/出场"""
    u=t-e['t'];a=e.get('anim','pop');dx=dy=0;s=1.0;al=1.0;rot=e.get('rot',0)
    if a=='pop':s=over(u/0.3)
    elif a=='slide_up':dy=int((1-ease_out(u/0.35))*500)
    elif a=='slide_r':dx=int((1-ease_out(u/0.35))*700)
    elif a=='slide_l':dx=-int((1-ease_out(u/0.35))*700)
    elif a=='drop':dy=-int((1-ease_out(u/0.35))*700)
    elif a=='fade':al=min(1,u/e.get('fd',0.3))
    elif a=='stamp':s=1+1.2*(1-ease_out(u/0.18));al=min(1,u/0.1)
    elif a=='spin':rot=rot+(1-ease_out(u/0.8))*360
    if e.get('sway'):rot+=e['sway']*math.sin(t*3)
    if e.get('zoom'):s*=1+e['zoom']*max(0,u)
    if e.get('until') is not None and t>e['until']:
        o=e.get('anim_out','shrink');v=(t-e['until'])/0.2
        if o=='fade':v=(t-e['until'])/e.get('fo',0.5);al*=max(0,1-v);s=s if v<1 else 0
        elif o=='fly_up':dy-=int(ease_out(v)*900);rot+=v*40
        else:s*=max(0,1-v)
        if v>=1 and o not in('fly_up','fade'):s=0
        if o=='fly_up' and v>1.5:s=0
    return dx,dy,s,al,rot
def draw_el(c,e,t):
    if t<e['t']:return
    if e['k']=='fx':
        fxo(c,e['name'],t,e['t'],(e['x'],e['y']),e.get('s',1.0),ease=e.get('ease','overshoot'));return
    if e['k']=='src_tag':
        source_tag(c,NW+e['src'],tuple(e['crop']),e['label'],t,e['t']);return
    if e['k']=='flip':   # 牌面翻转：front→back
        im=img(PR+e['src'],w=e['w']);u=(t-e['tf'])/0.4;sx=1.0 if u<0 else abs(math.cos(min(1,u)*math.pi))
        face=im if u<0.5 else im.transpose(Image.FLIP_LEFT_RIGHT);q=face.resize((max(2,int(face.width*max(sx,0.02))),face.height));paste(c,q,e['x'],e['y']);return
    if e['k']=='typing':   # 镜14 逐字 + 概率条（演示）
        txt=e['text'];tv=tq(t)-e['t'];box=Image.new('RGBA',(1060,130));d=ImageDraw.Draw(box)
        d.rounded_rectangle((0,0,1059,129),24,fill=(255,255,255),outline=INK,width=6)
        k=min(int(max(0,tv)/e['dt']),len(txt));d.text((36,65),txt[:k]+('▍' if bon(t) else ''),font=F(52),fill=INK,anchor='lm');paste(c,box,e['x'],e['y'])
        if k<len(txt):
            nxt=txt[k];cands=[(nxt,0.62),('家' if nxt!='家' else '座',0.23),('的',0.15)];ph=(max(0,tv)%e['dt'])/e['dt']
            for i,(ch,p) in enumerate(cands):
                x=e['x']-300+i*300;bh=int(220*p*ease_out(ph*2));cb=Image.new('RGBA',(200,300));dd=ImageDraw.Draw(cb)
                dd.rounded_rectangle((60,260-bh,140,260),10,fill=(255,214,64) if i==0 else (200,205,220),outline=INK,width=4)
                dd.text((100,285),f'{int(p*100)}%',font=F(26),fill=INK,anchor='mm');paste(c,cb,x,e['y']-260);paste(c,card(ch,50,(255,255,255) if i else (255,214,64)),x,e['y']-450)
        return
    if e['k']=='merge':   # 字卡逐个弹出后飞向中心合并
        for i,w in enumerate(e['words']):
            t0=e['t']+i*e['dt']
            if t>=t0:
                p=ease_out((t-t0-e['fly'])/0.3);x=e['xs'][i];y=e['y'];paste(c,card(w,44,(255,255,255)),x+(e['tx']-x)*p,y+(e['ty']-y)*p,over((t-t0)/0.3)*(1-0.7*p))
        return
    im=get_im(e,t)
    if im is None:return
    dx,dy,s,al,rot=anim(e,t)
    if s<=0.01:return
    tgt=TOPL[0] if e.get('top') else c
    paste(tgt,im,e['x']+dx,e['y']+dy,s*e.get('s',1.0),rot,al)
def STG(n,t,c):
    for e in SJ[n]['el']:draw_el(c,e,t if (e.get('anim')=='fade' or e.get('anim_out')=='fade' or e['k'] in('term','phone','typing')) else max(t,min(tq(t),SN[n]['s1'])) if t>=e['t'] else t)
# background
bg=Image.new('RGB',(W,H),(252,246,236));d=ImageDraw.Draw(bg)
for y in range(18,H,36):
    for x in range(18,W,36):d.ellipse((x-2,y-2,x+2,y+2),fill=(236,226,210))
BG=bg.convert('RGBA');SX=820
def counter_val(t):
    v=0
    for c in G['counter']:
        if t>=c['t']:v=c['v']
    return v
def tab_at(n):return SJ[n].get('tab')
NET=G.get('net',[])
def draw(f):
    t=f/FPS
    for k in NET:
        if k.get('freeze') and k['t']<=t<k['t']+k['freeze']:
            im=draw(int(k['t']*FPS)-1);g=im.convert('L').convert('RGB');return Image.blend(im,g,0.35)
    c=draw0(f)
    for k in NET:
        if k.get('shake') and 0<=t-k['t']<k['shake'][1]:
            u=(t-k['t'])/k['shake'][1];a=k['shake'][0]*(1-u);dx=int(a*math.sin(t*95));dy=int(a*math.cos(t*77))
            c2=Image.new('RGB',(W,H),(252,246,236));c2.paste(c,(dx,dy));c=c2
    return c
def draw0(f):
    t=f/FPS;n=shot_at(t);rt=t-SN[n]['s0'];c=BG.copy();J=SJ[n]
    TOPL[0]=Image.new('RGBA',(W,H));st=Image.new('RGBA',(W,H));STG(n,t,st)
    XF=J.get('xf',0.14);TZ=0.5
    if XF>0 and rt<XF and n>1:
        p=min(1,max(0,rt-XF/2)/(XF/2)) if J.get('xf_seq') else ease_io(rt/XF);pv=Image.new('RGBA',(W,H));keep=TOPL[0];TOPL[0]=Image.new('RGBA',(W,H));STG(n-1,t,pv);TOPL[0]=keep
        sc=1-(0 if J.get('xf_seq') else 0.25)*p;pv=pv.resize((int(W*sc),int(H*sc)),Image.BILINEAR);a=pv.split()[3].point(lambda v:int(v*(1-p)));pv.putalpha(a)
        tmp=Image.new('RGBA',(W,H));tmp.alpha_composite(pv,(int(SX-SX*sc),int(560-560*sc)));tmp.alpha_composite(st);st=tmp
    Z=J.get('stage_zoom',1.22);cx0,cy0=(SX,560);PJ=SJ.get(n-1)
    if PJ and rt<TZ:Zp=PJ.get('stage_zoom',1.22);Z=Zp+(Z-Zp)*ease_io(rt/TZ)
    for zp in J.get('punch',[]):
        if 0<=t-zp<0.35:Z*=1+0.07*math.sin((t-zp)/0.35*math.pi)
    if abs(Z-1)>1e-3:st=st.resize((int(W*Z),int(H*Z)),Image.BICUBIC);st=st.crop((int(cx0*Z-cx0),int(cy0*Z-cy0),int(cx0*Z-cx0)+W,int(cy0*Z-cy0)+H))
    c.alpha_composite(st)
    # fish (left)
    fc=cue_at(J['fish'],t) if J['fish'] else None;ex=0;P=SJ.get(n-1)
    if not fc and P and P['fish'] and rt<0.35:fc=P['fish'][-1];ex=ease_io(rt/0.35)
    if fc:
        fp=fc['pose'];lv=LVN[int(FLV[f])];bl=FBL.get(f,0)
        fi=fish_img(fp,lv,bl);hh=820;fi=fi.resize((int(fi.width*hh/1080),hh),Image.BILINEAR)
        enter=ease_out((t-SN[n]['s0'])/0.35) if not (P and P['fish']) else 1
        _tb=tbeat(t);bob=-10*FENS[min(N-1,max(0,int(_tb*FPS)))]-4*math.sin(_tb*2.2)
        if fc.get('jump'):u=t-fc['t'];bob-=60*max(0,math.sin(min(1,u/0.45)*math.pi)) if u<0.45 else 0
        x=260-int((1-enter)*600)-int(ex*700);c.alpha_composite(fi,(x-fi.width//2+30,H-hh+40+int(bob)))
    # O (right)
    oc=cue_at(J['o'],t);L=dict(J.get('o_layout',{}));PL=(P or {}).get('o_layout',{})
    if P and rt<TZ:
        q=ease_io(rt/TZ);L={'scale':PL.get('scale',1.0)+(L.get('scale',1.0)-PL.get('scale',1.0))*q,'dx':PL.get('dx',0)+(L.get('dx',0)-PL.get('dx',0))*q}
    oh=int(880*L.get('scale',1.0))
    fq=min(N-1,int(tq(t)*FPS));o=hostO(oc['pose'],LVN[int(OLV[f])],OBL.get(f,0),ODX[fq],ODY[fq],oh)
    c.alpha_composite(o,(int(W-o.width+60+L.get('dx',0)),H-o.height+60))
    c.alpha_composite(TOPL[0])
    tab=tab_at(n)
    if tab:
        u=1 if (P and P.get('tab')==tab) else ease_out((rt-0.1)/0.4)
        tb=card(tab,32,(64,64,80),(255,255,255),20,14,3);paste(c,tb,W-tb.width//2-30+int((1-u)*400),56)
    cv=counter_val(t)
    if cv>0:
        last=max([x['t'] for x in G['counter'] if x['t']<=t]);s=over((t-last)/0.3) if t-last<0.3 else 1
        paste(c,card(f'翻车计数  {cv}',40,(255,120,100),(255,255,255)),210,90,s)
    z=1.0
    if n==1 and rt<0.4:z+=0.06*math.sin(rt/0.4*math.pi)
    if abs(z-1)>1e-4:
        cw,ch=int(W/z),int(H/z);c=c.crop(((W-cw)//2,(H-ch)//2,(W-cw)//2+cw,(H-ch)//2+ch)).resize((W,H),Image.BILINEAR)
    return c.convert('RGB')
if __name__=='__main__':
    if sys.argv[1]=='-1':
        for t in map(float,sys.argv[2:]):draw(int(t*FPS)).save(f'/tmp/full_chk_{t}.jpg')
        sys.exit()
    f0,f1=int(sys.argv[1]),min(int(sys.argv[2]),N)
    p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','17','-preset','fast','-pix_fmt','yuv420p',f'part_{f0:05d}.mp4'],stdin=subprocess.PIPE)
    for f in range(f0,f1):p.stdin.write(draw(f).tobytes())
    p.stdin.close();p.wait()
