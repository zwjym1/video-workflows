# r7 统一音效：一套「轻科幻+卡通」音色家族（A 大调五声音阶，同一 EQ/同一短房间），按类别固定电平
import numpy as np, subprocess, json, sys, os
from scipy.signal import butter, sosfilt, fftconvolve
R=48000; END=116.9; rng=np.random.default_rng(527)
# 用法: python mix_v4.py <纯人声wav> <mixkit目录> <输出目录>（box 与 PC 同一脚本）
VO,MK,OUT=(sys.argv[1:4] if len(sys.argv)>3 else ['/workspace/blackhole527/remotion/audio/film_mix_v1.wav','/workspace/blackhole527/sfx/mk','/workspace/blackhole527/sfx/v4'])
MK=MK.rstrip('/\\')+os.sep
def dec(f,rate=1.0):
    af=[] if rate==1 else ['-af',f'asetrate={int(R*rate)},aresample={R}']
    return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f,*af,'-ac','1','-ar',str(R),'-f','f32le','-'],capture_output=True).stdout,dtype=np.float32).astype(np.float64)
def tt(d): return np.arange(int(d*R))/R
def env(d,a,tau): t=tt(d); return np.minimum(1,t/max(a,1e-4))*np.exp(-t/tau)
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=R,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=R,output='sos'),x)
def bp(x,lo,hi): return sosfilt(butter(2,[lo,hi],'band',fs=R,output='sos'),x)
def glide(f0,f1,d,k=40):  # 指数滑音相位
    t=tt(d); f=f1+(f0-f1)*np.exp(-t*k); return np.sin(2*np.pi*np.cumsum(f)/R)
A=[440,493.88,554.37,659.26,739.99]   # A 大调五声：与氛围底 55/82.5 Hz（A/E）同调
def note(i,oct=0): return A[i%5]*2**(i//5+oct)
# ---------- 音色家族 ----------
def SUB(f0=55,tau=0.28,d=0.9):        # 柔和低频冲击（替代 vine boom/bong/shocking/金属管/悬疑）
    x=glide(f0*2.2,f0,d,30)*env(d,0.004,tau)+0.25*glide(f0*4.4,f0*2,d,30)*env(d,0.002,tau*0.5)
    n=lp(rng.standard_normal(int(d*R)),900)*env(d,0.001,0.012)*0.6
    return np.tanh(1.6*(x+n))
def THOCK(f=220,d=0.35):              # 中频软击（替代 slap/punch）
    x=glide(f*1.6,f,d,60)*env(d,0.002,0.07)+0.4*bp(rng.standard_normal(int(d*R)),900,3500)*env(d,0.001,0.01)
    return np.tanh(1.3*x)
def POP(f=554.37,d=0.22):             # 卡通 pop：上滑短音（替代 boing/啵）
    t=tt(d); fr=f*(0.55+0.45*(1-np.exp(-t*90))); x=np.sin(2*np.pi*np.cumsum(fr)/R)*env(d,0.002,0.045)
    return x+0.15*bp(rng.standard_normal(len(t)),2000,6000)*env(d,0.0005,0.004)
def TICK(f=1760,d=0.08):              # UI 轻点（替代打字/订书机/相机/鼓点）
    t=tt(d); return np.sin(2*np.pi*f*t)*env(d,0.0005,0.012)+0.5*hp(rng.standard_normal(len(t)),3000)*env(d,0.0003,0.003)
def CHIME(f=880,d=1.3,two=True):      # 玻璃铃（替代 ding/sparkle/wow/bong）
    def b(f): return sum(a*np.sin(2*np.pi*f*m*tt(d))*env(d,0.003,tau) for m,a,tau in [(1,1,.55),(2,.35,.3),(3,.15,.15),(4.2,.06,.08)])
    x=b(f)
    if two: s=int(0.07*R); y=np.zeros_like(x); y[s:]=b(f*1.5)[:len(x)-s]*0.8; x=x+y
    return x
def RISE(d=1.6,f0=220,f1=440):        # 上扬（替代 cinematic riser/悬疑 riser）
    t=tt(d); a=(t/d)**2; n=rng.standard_normal(len(t)); out=np.zeros_like(t); seg=int(0.05*R)
    for i in range(0,len(t),seg):     # 分段带通扫频
        c=600*2**(3*i/len(t)); out[i:i+seg]=bp(n[max(0,i-seg):i+seg],c*0.7,min(c*1.4,20000))[-len(out[i:i+seg]):]
    tone=np.sin(2*np.pi*np.cumsum(f0*(f1/f0)**(t/d))/R)
    x=(0.6*out+0.5*tone)*a; x[-int(0.03*R):]*=np.linspace(1,0,int(0.03*R)); return x
def WH(kind='S',rate=1.0):            # 同一套 whoosh（Mixkit #166 短 / #1490 长）
    return dec(MK+('166.mp3' if kind=='S' else '1490.mp3'),rate)
def BITE(i):                           # 开头咬合：SUB + 下滑 chomp + 牙齿 tick；5 口逐级升调
    s=SUB(55,0.16,0.6); c=glide(note(i,-1)*1.2,note(i,-1)*0.5,0.6,25)*env(0.6,0.002,0.06); k=np.pad(TICK(note(i,2),0.08),(0,len(s)-int(0.08*R)))
    return np.tanh(1.2*(s+0.8*c+0.35*k))
# ---------- 统一处理：同 EQ + 同一短房间 ----------
IR=lp(rng.standard_normal(int(0.35*R)),6000)*np.exp(-tt(0.35)/0.07); IR/=np.sqrt(np.sum(IR**2))
def unify(x,cat):
    x=hp(x,30 if cat in('SUB','BITE') else 70); x=lp(x,9000,4)
    x=x-0.25*bp(x,2500,5000)             # 去刺耳 2.5–5k（约 -2.5 dB）
    if cat not in('SUB',): x=hp(x,140) if cat in('TICK','CHIME','POP') else x   # 去浑浊
    wet=fftconvolve(x,IR)[:len(x)+int(0.3*R)]; x=np.pad(x,(0,len(wet)-len(x)))+0.18*wet
    return x
# K 加权 150 ms 窗峰值电平（短音效用此替代 loudnorm：BS.1770 的门限对 <400 ms 片段不可靠）
from scipy.signal import lfilter
def kw(x):   # ITU-R BS.1770 K 加权（48 kHz 系数）
    y=lfilter([1.53512485958697,-2.69169618940638,1.19839281085285],[1,-1.69065929318241,0.73248077421585],x)
    return lfilter([1.0,-2.0,1.0],[1,-1.99004745483398,0.99007225036621],y)
class _M:
    def integrated_loudness(self,x):  # BS.1770-4 门限积分响度
        y=kw(x); b=int(0.4*R); h=int(0.1*R); z=np.array([np.mean(y[i:i+b]**2) for i in range(0,len(y)-b+1,h)])
        l=-0.691+10*np.log10(z+1e-15); z=z[l>-70]; rel=-0.691+10*np.log10(z.mean())-10
        return -0.691+10*np.log10(z[-0.691+10*np.log10(z)>rel].mean())
meter=_M()
def lvl(x,w=int(0.15*R)):
    y=kw(x); c=np.convolve(y**2,np.ones(w)/w,'valid') if len(y)>w else np.array([np.mean(y**2)]); return 10*np.log10(c.max()+1e-12)
# 类别目标电平（相对人声参考 Rv，单位 dB；同类事件同电平）
TGT={'BITE':-3,'SUB':-6,'THOCK':-8,'POP':-9,'WH':-10,'RISE':-11,'CHIME':-11,'TICK':-13}
# ---------- 事件表：时间/密度与 r5 v3 完全一致，只换音色 ----------
def ticks(t0,n,dt,base=10): return [(t0+i*dt,'TICK',dict(f=note(base+(i%3))),f'打字 tick{i+1}') for i in range(n)]
E=[(0.0,'SUB',{},'首帧低频冲击'),(0.0,'WH',dict(kind='L'),'首帧快推'),
 *[(b,'BITE',dict(i=i),f'第{i+1}口 啊呜') for i,b in enumerate([0.03,1.42,2.2,2.9,3.6])],
 (2.84,'SUB',{},'「每527天咬一口」大字落下'),(4.35,'WH',dict(kind='L'),'拉远成轨道'),
 *ticks(5.28,6,0.13),(8.8,'CHIME',dict(f=880),'「咬了五口」'),(11.14,'SUB',{},'「到现在还活着」'),
 (12.87,'SUB',dict(f0=55,tau=0.5,d=1.4),'「为什么不一口吞掉」'),(18.6,'WH',dict(kind='S'),'推向近点'),
 (21.4,'RISE',dict(d=2.3),'引力差拉伸'),(23.45,'WH',dict(kind='L'),'切入超算模拟'),(25.7,'THOCK',{},'外层被扯成面条'),
 (29.25,'WH',dict(kind='S'),'拉回全轨道'),(32.56,'WH',dict(kind='S',rate=0.9),'核心逃逸'),(37.04,'THOCK',{},'「再挨下一口」'),
 (38.3,'WH',dict(kind='S'),'轨道折成饭卡'),*[(x,'TICK',dict(f=note(10+i)),f'打孔{i+1}') for i,x in enumerate([39.45,39.7,39.95,40.2])],
 (40.09,'POP',dict(f=note(2)),'「分期饭卡」'),(40.78,'THOCK',{},'第5孔'),(41.8,'WH',dict(kind='L'),'饭卡碎裂'),(41.81,'SUB',{},'「更反常的是」'),
 *[(x,'POP',dict(f=note(i)),f'脉冲柱{i+1}') for i,x in enumerate([50.0,51.85,52.65,53.45,55.0])],
 (54.7,'CHIME',dict(f=440),'「一口比一口狠」'),(56.74,'CHIME',dict(f=660),'「以前没见过」'),(58.8,'WH',dict(kind='S'),'推入剖面'),(58.82,'SUB',{},'「为什么会这样」'),
 (63.0,'POP',dict(f=note(-2)),'恒星膨胀'),(64.2,'WH',dict(kind='S'),'转潮汐撕裂'),(66.6,'RISE',dict(d=1.6),'潮汐撕裂'),(67.7,'SUB',{},'撕裂闪光'),
 *ticks(68.75,4,0.13),(68.85,'CHIME',dict(f=1318.5,two=False),'1/10 太阳'),(72.34,'THOCK',{},'「越挨揍」'),(73.82,'POP',dict(f=note(1)),'「掉肉更多」'),
 (75.53,'POP',dict(f=note(2)),'评论气泡1'),(76.28,'POP',dict(f=note(3)),'评论气泡2'),(78.4,'SUB',{},'「没错」'),(81.4,'WH',dict(kind='L'),'光束网格'),
 (83.5,'WH',dict(kind='L',rate=0.8),'极速拉远'),(84.88,'CHIME',dict(f=880),'缩成像素'),(85.82,'TICK',dict(f=note(10)),'测光孔径'),(85.9,'SUB',dict(f0=55,tau=0.5,d=1.4),'「怎么看到的」'),
 (94.0,'SUB',dict(f0=55,tau=0.15,d=0.5),'双峰心跳1a'),(94.2,'SUB',dict(f0=55,tau=0.15,d=0.5),'双峰心跳1b'),(95.65,'SUB',dict(f0=55,tau=0.15,d=0.5),'双峰心跳2a'),(95.85,'SUB',dict(f0=55,tau=0.15,d=0.5),'双峰心跳2b'),
 *[(98.95+0.3*i,'TICK',dict(f=note(10+i)),f'时间轴{i+1}') for i in range(5)],(100.85,'CHIME',dict(f=880),'第5口按时出现'),
 (102.3,'WH',dict(kind='S'),'平移到2026'),(103.5,'SUB',{},'问号'),(104.95,'TICK',dict(f=note(10)),'望远镜对准'),(106.91,'THOCK',{},'「结果待公布」盖章'),
 (108.45,'WH',dict(kind='L'),'回到残骸轨道'),(110.9,'POP',dict(f=note(2)),'「最多再撑」框'),(112.96,'SUB',dict(f0=55,tau=0.5,d=1.4),'「你觉得今年这一口」'),(115.78,'POP',dict(f=note(3)),'评论气泡'),
]
GEN={'SUB':SUB,'THOCK':THOCK,'POP':POP,'TICK':TICK,'CHIME':CHIME,'RISE':RISE,'WH':WH,'BITE':BITE}
if __name__=='__main__':
    v=dec(VO)[:int(END*R)]; N=len(v)
    yk=kw(v); w=int(0.15*R); c=10*np.log10(np.convolve(yk**2,np.ones(w)/w,'same')+1e-12)
    Rv=np.percentile(c[c>-45],90); vo_lufs=meter.integrated_loudness(v)
    print(f'人声 integrated {vo_lufs:.1f} LUFS, 150ms 参考 Rv {Rv:.1f} dB')
    sfx=np.zeros(N+R*3); rows=[]; cache={}
    for (t,cat,kw_,lab) in E:
        key=(cat,tuple(sorted(kw_.items())))
        if key not in cache: x=unify(GEN[cat](**kw_),cat); cache[key]=x*10**((Rv+TGT[cat]-lvl(x))/20)
        x=cache[key]; a=int(t*R); sfx[a:a+len(x)]+=x[:len(sfx)-a]; rows.append((t,cat,TGT[cat],lab,a,key))
    sfx=sfx[:N]
    # 人声自动闪避：语音包络 → SFX -4 dB（攻 30 ms / 释 250 ms）
    e=np.sqrt(np.convolve(v**2,np.ones(int(0.05*R))/int(0.05*R),'same')); act=(20*np.log10(e+1e-9)>-40).astype(float)
    g=np.zeros(N); s=0
    for i in range(0,N,48):
        tgt=act[i]; s+= (tgt-s)*(0.8 if tgt>s else 0.0192); g[i:i+48]=s
    sfx*=10**(-4*g/20)
    bed=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i',f'anoisesrc=color=brown:amplitude=0.6:d={END}:r={R}:seed=7','-f','lavfi','-i',f'sine=f=55:r={R}:d={END}','-f','lavfi','-i',f'sine=f=82.5:r={R}:d={END}',
     '-filter_complex','[0]lowpass=f=180,lowpass=f=180,volume=0.5[n];[1]volume=0.25,tremolo=f=0.15:d=0.6[a];[2]volume=0.12,tremolo=f=0.11:d=0.7[b];[n][a][b]amix=3:normalize=0,afade=t=in:d=1.5,afade=t=out:st=115.4:d=1.5[o]',
     '-map','[o]','-ac','1','-f','f32le','-'],capture_output=True).stdout,dtype=np.float32).astype(np.float64)[:N]; bed=np.pad(bed,(0,N-len(bed)))   # 氛围底（A1+E2，与 v2/v3 同配方）
    bed*=10**((vo_lufs-20-meter.integrated_loudness(bed))/20)
    mix=v+sfx+bed; tt_=np.arange(N)/R; fade=np.clip((END-tt_)/0.4,0,1); mix*=fade; sfx_out=(sfx+bed)*fade
    gain=-16.0-meter.integrated_loudness(mix); mix*=10**(gain/20); sfx_out*=10**(gain/20)
    from scipy.io import wavfile
    P=lambda n: os.path.join(OUT,n)
    wavfile.write(P('pre_mix.wav'),R,mix.astype(np.float32)); wavfile.write(P('sfx_only_pre.wav'),R,sfx_out.astype(np.float32))
    # 母带：+0.2 dB 后 4× 过采样限幅（真峰 ≤ -1.5 dBTP 余量），24-bit
    for a,b,v in [('pre_mix.wav','film_mix_v4.wav','0.2dB'),('sfx_only_pre.wav','sfx_only.wav','0.2dB')]:
        subprocess.run(['ffmpeg','-y','-v','error','-i',P(a),'-af',f'volume={v},aresample=192000,alimiter=limit=0.8:level=disabled:attack=1:release=60,aresample=48000','-c:a','pcm_s24le',P(b)],check=True)
    # SFX 类别内/类别间实测（在混音里、闪避后）
    meas={}
    gg=10**(-4*g/20)
    for (t,cat,tg,lab,a,key) in rows:
        x=cache[key]; n=min(len(x),N-a); meas.setdefault(cat,[]).append(lvl(x[:n]*gg[a:a+n])-Rv)
    rows=[r[:4] for r in rows]
    json.dump({'Rv':Rv,'vo_lufs':vo_lufs,'gain':gain,'events':rows,'meas':{k:[round(min(v),1),round(max(v),1)] for k,v in meas.items()}},open(os.path.join(OUT,'mix_meta_v4.json'),'w'),ensure_ascii=False,indent=1)
    print('events',len(rows),'cats',{k:len(v) for k,v in meas.items()}); print({k:[round(min(v),1),round(max(v),1)] for k,v in meas.items()})
