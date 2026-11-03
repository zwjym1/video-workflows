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
