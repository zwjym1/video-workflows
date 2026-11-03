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
    x=W-th.width//2-150+int((1-p)*500);y=110
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
