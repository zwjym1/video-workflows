# 全片混音 + 字幕（字幕最后单独叠最上层）；音效时点全部读 script_v3/shots_v3.json
import json,re,subprocess,numpy as np,soundfile as sf,os
EP='/workspace/science-studio/episodes/ai101_ep01_hallucination'
TL=json.load(open('timeline.json'));LN=TL['lines'];DUR=TL['dur'];SN={int(k):v for k,v in TL['shots'].items()}
SFXR='/workspace/science-studio/assets/audio_lib/sfx/'
SJ=json.load(open(EP+'/script_v3/shots_v3.json'))
EV=[(x['t'],x['f'],x['db']) for x in SJ['global']['sfx']]
EV=[e for e in EV if 0<=e[0]<DUR]
SR=48000;n=int(DUR*SR);mix=np.zeros((n,2),np.float32)
def load(p):
    a,sr=sf.read(p,dtype='float32',always_2d=True)
    if sr!=SR:
        raw=subprocess.run(['ffmpeg','-v','error','-i',p,'-ar',str(SR),'-ac','2','-f','f32le','-'],capture_output=True).stdout;a=np.frombuffer(raw,np.float32).reshape(-1,2)
    if a.shape[1]==1:a=np.repeat(a,2,1)
    return a
for t,p,g in EV:
    a=load(SFXR+p+'.wav')*10**(g/20);i=int(t*SR);j=min(n,i+len(a));mix[i:j]+=a[:j-i]
sf.write('sfx.wav',mix,SR);json.dump(EV,open('sfx_events.json','w'))
# subs
def ts(t):return f'{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}'
A=['[Script Info]','ScriptType: v4.00+','PlayResX: 1920','PlayResY: 1080','','[V4+ Styles]',
'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
'Style: O,Noto Sans CJK SC,60,&H00FFFFFF,&H00FFFFFF,&H00302230,&H80000000,-1,0,0,0,100,100,1,0,1,6,2,2,60,60,50,1',
'Style: F,Noto Sans CJK SC,60,&H00FFD27A,&H00FFFFFF,&H00302230,&H80000000,-1,0,0,0,100,100,1,0,1,6,2,2,60,60,50,1',
'','[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
def dec(p,sr=16000):return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True).stdout,np.float32)
def vadf(a,sr=16000,hop=0.005):
    h=int(sr*hop);n=len(a)//h;r=np.sqrt((a[:n*h].reshape(n,h)**2).mean(1));db=20*np.log10(r+1e-9);return db>(db.max()-38)
AV={w:vadf(dec(f'vo_{w}.wav')) for w in 'OF'};VAD=[]
for i,l in enumerate(LN):
    act=AV[l['who']];hop=0.005;lo=max(0,l['t0']-0.4);hi=l['t1']+0.4
    if i>0:lo=max(lo,(LN[i-1]['t1']+l['t0'])/2)
    if i+1<len(LN):hi=min(hi,(l['t1']+LN[i+1]['t0'])/2)
    idx=np.where(act[int(lo/hop):int(hi/hop)])[0];VAD.append([lo+idx[0]*hop,lo+(idx[-1]+1)*hop])
json.dump(VAD,open('vad.json','w'))
for li,l in enumerate(LN):
    txt=l['text'].replace('——','，').replace('……','…')
    ph=[p for p in re.split(r'(?<=[，。！？；：,!?…])',txt) if p.strip()];m=[]
    for p in ph:
        if m and len(m[-1])+len(p)<=12:m[-1]+=p
        else:m.append(p)
    # char position -> time from aligned tokens
    pos=[None]*len(txt);ptr=0
    for w in l.get('words',[]):
        k=txt.find(w['c'],ptr)
        if k<0:continue
        for q in range(k,k+len(w['c'])):pos[q]=w['t0']
        ptr=k+len(w['c'])
    starts=[];c0=0
    for p in m:
        ts_=[pos[q] for q in range(c0,c0+len(p)) if pos[q] is not None];starts.append(ts_[0] if ts_ else None);c0+=len(p)
    starts[0]=VAD[li][0]
    for q in range(1,len(starts)):
        if starts[q] is None or starts[q]<=starts[q-1]:starts[q]=starts[q-1]+(l['t1']-l['t0'])*len(m[q-1])/len(txt)
    for q,p in enumerate(m):
        e=starts[q+1] if q+1<len(m) else VAD[li][1]+0.06
        A.append(f"Dialogue: 0,{ts(starts[q])},{ts(e)},{l['who']},,0,0,0,,{p.rstrip('，。；：,')}")
open('subs.ass','w').write('\n'.join(A)+'\n')
# voice guard: every line must carry the right reference_id and pass the f0 gate
VID={'O':'ebea2d0931f54cd69ec7d5e88db6b084','F':'9510b59280f74ad197f10b61eaa5abba'}
for l in LN:
    assert l.get('reference_id')==VID[l['who']],('WRONG VOICE',l['idx'],l['who'],l.get('reference_id'))
    assert l.get('voice_ok'),('VOICE GATE FAIL',l['idx'])
print('voice check OK',len(LN))
BGM0='/workspace/science-studio/knowledge/aning_rhythm/bgm_sep_7702426566919212315.mp3'
# BGM 只有 120s：按小节(4拍=2.0426s)拼接循环，接缝 1s 交叉淡化
bg=load(BGM0);BAR=4*60/117.5;P=int(57*BAR*SR);O=int(8*BAR*SR);XF=SR
out=bg[:P].copy()
while len(out)<int((DUR+2)*SR):
    seg=bg[O:P];w=np.linspace(0,1,XF)[:,None];out[-XF:]=out[-XF:]*(1-w)+seg[:XF]*w;out=np.concatenate([out,seg[XF:]])
sf.write('bgm_loop.wav',out,SR);BGM='bgm_loop.wav' 
def lufs(f,extra=[]):
    r=subprocess.run(['ffmpeg','-nostats',*extra,'-i',f,'-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',r)[-1])
LV=lufs('vo_all.wav');LB=lufs(BGM,['-t',str(DUR)]);G=round(LV-14-LB,2);print('VO',LV,'BGM',LB,'gain',G)
fc=(f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo[vo];"
    f"[3:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{DUR},volume={G}dB,afade=t=in:d=0.2,afade=t=out:st={DUR-1.2}:d=1.2[bg];"
    f"[vo][2:a][bg]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a];[0:v]ass=subs.ass[v]")
OUT=EP+'/production/full_v1.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i','picture.mp4','-i','vo_all.wav','-i','sfx.wav','-i',BGM,'-filter_complex',fc,'-map','[v]','-map','[a]',
 '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(DUR),'-movflags','+faststart',OUT],check=True)
print(OUT)
