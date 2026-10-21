"""v1p: same as film_mix.py but VO = vo_master_v1p.wav (4 sentences Fish retake, 2026-10-21)."""
"""全片音频 film_mix_v1：
- VO：vo_master.wav 整条直取（不再逐段 10ms 淡入，接缝处人声 100% 连续）
- bed / sfx：各段已出的分轨（hook2d v3 + seg2..seg6）按母带绝对时间首尾相接；各段 bed 首末样本本身≈0，无断点
- duck：同配方（-9dB，attack .25 / release .02，阈 0.01）全片一次计算，避免每段从 0 重启造成床电平跳
- alimiter 同参数（limit .76），最后整片线性增益到 -16 LUFS（不再压缩），尾部补静音到 OptoFilm 时长 5246f。"""
import numpy as np, soundfile as sf, subprocess, json, sys
SR=48000; NF=5246; N=int(round(NF/30*SR))
D='/workspace/optogenetics/audio/'
def rd(p):
    x,sr=sf.read(p); assert sr==SR,p; return x if x.ndim==1 else x[:,0]
from scipy.signal import butter, sosfilt
def lpf(x,fc,order=2): return sosfilt(butter(order,fc,fs=SR,output='sos'),x)
db=lambda v:10**(v/20)
segs=[(0.0,14.80,'hook2d',True),(14.80,47.70,'seg2',False),(47.70,75.15,'seg3',False),
      (75.15,115.25,'seg4',False),(115.25,144.25,'seg5',False),(144.30,None,'seg6',False)]
# ⑥段音频按 seg6_mix.py 自 144.30 起（与画面动作起点一致），144.25–144.30 床留 50ms 空；人声连续，此处本是气口
bed=np.zeros(N); sfx=np.zeros(N)
for a,b,n,raw in segs:
    i0=int(round(a*SR)); bb=rd(D+n+'_bed.wav'); ss=rd(D+n+'_sfx.wav')*(db(-6) if raw else 1)
    L=(len(bb) if b is None else int(round((b-a)*SR))); L=min(L,N-i0)
    bed[i0:i0+L]+=np.pad(bb,(0,max(0,L-len(bb))))[:L]; sfx[i0:i0+L]+=np.pad(ss,(0,max(0,L-len(ss))))[:L]
vo=rd('/workspace/optogenetics/vo/vo_master_v1p.wav'); vo=np.pad(vo,(0,max(0,N-len(vo))))[:N]
e=np.sqrt(np.maximum(0,lpf(vo**2,8))); act=(e>0.01).astype(float)
g=np.zeros(N); s=0.
for i in range(0,N,48):
    a=act[i]; s=s+(a-s)*(0.25 if a>s else 0.02); g[i:i+48]=s
mix=vo+bed*10**((-9*g)/20)+sfx
sf.write(D+'film/film_mix_v1p_pre.wav',mix.astype(np.float32),SR)
subprocess.run(['ffmpeg','-v','error','-y','-i',D+'film/film_mix_v1p_pre.wav','-af','alimiter=limit=0.76:attack=2:release=60:level=disabled','-ar',str(SR),'-c:a','pcm_f32le',D+'film/film_mix_v1p_lim.wav'],check=True)
m=rd(D+'film/film_mix_v1p_lim.wav'); m=np.pad(m,(0,max(0,N-len(m))))[:N]
def meas(p):
    r=subprocess.run(['ffmpeg','-hide_banner','-i',p,'-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True).stderr
    return json.loads(r[r.rfind('{'):r.rfind('}')+1])
I=float(meas(D+'film/film_mix_v1p_lim.wav')['input_i'])
m=m*db(-16-I)
print('gain',round(-16-I,2),'peak dBFS',round(20*np.log10(np.abs(m).max()),2))
sf.write(D+'film_mix_v1p.wav',m.astype(np.float32),SR,subtype='PCM_24')
sf.write(D+'film/film_bed_full_v1p.wav',bed.astype(np.float32),SR); sf.write(D+'film/film_sfx_full_v1p.wav',sfx.astype(np.float32),SR)
print(json.dumps({k:v for k,v in meas(D+'film_mix_v1p.wav').items() if k in('input_i','input_tp','input_lra')}))
