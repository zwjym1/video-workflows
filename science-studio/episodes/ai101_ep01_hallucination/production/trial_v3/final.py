# 混音 + 字幕（字幕最后一步单独叠最上层）— v2
import json,re,subprocess,numpy as np,soundfile as sf,os
EP='/workspace/science-studio/episodes/ai101_ep01_hallucination'
TL=json.load(open('timeline.json'));LN=TL['lines'];DUR=TL['dur'];SN={int(k):v for k,v in TL['shots'].items()}
S={l['n']:l for l in json.load(open('timeline_v1.json'))['lines']}
SFXR='/workspace/science-studio/assets/audio_lib/sfx/'
def T(n,dt,frm='t0'):return S[n][frm]+dt
def mapt(t):
    # v1 absolute time -> v2 absolute time (per-shot piecewise linear)
    n=max(k for k in S if S[k]['s0']<=t+1e-6) if t>=0 else 1
    o=S[n];a=SN[n];lo=o['t0']-o['s0'];ln=a['t0']-a['s0'];do=o['t1']-o['t0'];dn=a['t1']-a['t0'];r=t-o['s0']
    rn=r*ln/lo if r<lo and lo>0 else ln+(r-lo)*dn/do
    return a['s0']+rn
EV=[(0.0,'impact_punch/slam_a',-6),(T(1,1.85),'pop_ui/pop_switch_hard',-8),(T(1,3.8),'pop_ui/pop_switch_hard',-8),(T(1,3.8),'impact_punch/hit_a',-12),
 (S[2]['s0'],'whoosh_trans/whoosh_synth',-12),(S[2]['s0']+0.25,'pop_ui/pop_plop',-10),(S[2]['s0']+0.4,'ding_success/sparkle_synth',-12),
 (T(3,0.35),'pop_ui/pop_click_b',-12),(T(3,0.75),'pop_ui/pop_click_b',-12),(T(3,1.15),'pop_ui/pop_click_b',-12),(T(3,1.6),'tech_digital/pep_blip',-10),
 (T(4,0.1),'pop_ui/pop_ui' if False else 'pop_ui/pop_plop2',-10),(T(5,0.1),'pop_ui/pop_rollover',-14),(T(5,2.2),'tech_digital/machine_hum',-18),(T(5,3.0),'impact_punch/thunk_synth',-8),
 (S[6]['s0']+0.05,'pop_ui/pop_click_a',-12),(T(6,0.55),'impact_punch/bonk_synth',-8),(T(7,2.3),'whoosh_trans/paper_swipe',-8),(T(7,2.75),'comedy_fail/fail_wah_down',-14),
 (T(8,0.15),'impact_punch/slam_a',-8),(T(8,1.2),'pop_ui/pop_synth',-12),(T(8,2.0),'pop_ui/pop_synth',-12),
 (T(9,2.3),'impact_punch/thunk_synth',-6),(T(9,2.3),'whoosh_trans/rise_highup',-16),(T(10,0.3),'comedy_fail/weird_wobble',-14),
 (T(11,1.5),'ding_success/ding_bell',-10),(T(11,1.85),'pop_ui/pop_plop',-12),(S[12]['s0'],'whoosh_trans/whoosh_synth',-12),(T(12,0.05),'pop_ui/pop_plop',-10),
 (T(13,0.25),'pop_ui/pop_click_b',-10),(T(13,0.85),'comedy_fail/fail_retro_die',-18),(T(13,1.4),'impact_punch/thunk_synth',-8),(T(13,1.7),'ding_success/ding_coin',-12),
 (S[15]['s0']+0.05,'impact_punch/gong',-18),(T(15,1.9),'pop_ui/boop_synth',-12)]
tv=0.6
while tv<7.5:EV.append((T(14,tv),'pop_ui/pop_click_a',-22));tv+=0.32
EV=[(mapt(t) if t>0 else 0.0,p,g) for t,p,g in EV]
N4=[l for l in LN if l['shot']==4]
def sn(k,dt):L=SN[k];return L['t0']+dt
EV+=[(N4[1]['t0']-0.05,'pop_ui/pop_plop',-12),(N4[2]['t0'],'impact_punch/thunk_synth',-10),
 (sn(16,0.3),'pop_ui/pop_plop2',-12),(sn(16,0.9),'ding_success/ding_coin',-14),
 (sn(17,1.0),'whoosh_trans/whoosh_synth',-14),(sn(17,1.6),'impact_punch/bonk_synth',-12),
 (sn(18,0.6),'whoosh_trans/paper_swipe',-12),(sn(18,1.05),'whoosh_trans/paper_swipe',-12),(sn(18,1.5),'whoosh_trans/paper_swipe',-12),(sn(18,2.4),'pop_ui/pop_plop',-12),
 (sn(19,0.1),'pop_ui/pop_click_b',-12),(sn(19,0.35),'pop_ui/pop_click_b',-12),(sn(19,0.65),'pop_ui/pop_click_b',-12),(sn(19,0.95),'ding_success/sparkle_synth',-12),
 (sn(20,0.6),'comedy_fail/fail_wah_down',-14),(sn(20,0.65),'impact_punch/thunk_synth',-10)]
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
VAD=json.load(open('vad.json'))
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
BGM='/workspace/science-studio/knowledge/aning_rhythm/bgm_sep_7702426566919212315.mp3'
def lufs(f,extra=[]):
    r=subprocess.run(['ffmpeg','-nostats',*extra,'-i',f,'-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',r)[-1])
LV=lufs('vo_all.wav');LB=lufs(BGM,['-t',str(DUR)]);G=round(LV-14-LB,2);print('VO',LV,'BGM',LB,'gain',G)
fc=(f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo[vo];"
    f"[3:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{DUR},volume={G}dB,afade=t=in:d=0.2,afade=t=out:st={DUR-1.2}:d=1.2[bg];"
    f"[vo][2:a][bg]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a];[0:v]ass=subs.ass[v]")
OUT=EP+'/production/trial_open_v3.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i','picture.mp4','-i','vo_all.wav','-i','sfx.wav','-i',BGM,'-filter_complex',fc,'-map','[v]','-map','[a]',
 '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(DUR),'-movflags','+faststart',OUT],check=True)
print(OUT)
