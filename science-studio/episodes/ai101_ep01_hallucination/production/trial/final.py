# 混音 + 字幕（字幕最后一步单独叠最上层）
import json,re,subprocess,numpy as np,soundfile as sf,os
EP='/workspace/science-studio/episodes/ai101_ep01_hallucination'
TL=json.load(open('timeline.json'));LN=TL['lines'];DUR=TL['dur'];S={l['n']:l for l in LN}
SFXR='/workspace/science-studio/assets/audio_lib/sfx/'
def T(n,dt,frm='t0'):return S[n][frm]+dt
lead=lambda n:S[n]['t0']-S[n]['s0']
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
al={}
for l in LN:
    j=EP+'/vo/'+l['wav'].replace('vo/','').replace('cut/','takes/').replace('.wav','.mp3')+'.json'
    txt=l['text'].replace('——','，').replace('……','…')
    ph=[p for p in re.split(r'(?<=[，。！？；：,!?])',txt) if p.strip()];m=[]
    for p in ph:
        if m and len(m[-1])+len(p)<=12:m[-1]+=p
        else:m.append(p)
    tot=sum(len(p) for p in m);t=l['t0'];span=l['t1']-l['t0']
    for i,p in enumerate(m):
        d=span*len(p)/tot;e=t+d if i<len(m)-1 else l['t1']+0.2
        A.append(f"Dialogue: 0,{ts(t)},{ts(e)},{l['who']},,0,0,0,,{p.rstrip('，。；：,')}");t+=d
open('subs.ass','w').write('\n'.join(A)+'\n')
BGM='/workspace/science-studio/assets/audio_lib/bgm/happy_arcade_tune.mp3'
fc=(f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[vo][vok];"
    f"[3:a]aformat=sample_rates=48000:channel_layouts=stereo,aloop=loop=-1:size=2e9,atrim=0:{DUR},volume=-17dB,afade=t=in:d=0.3,afade=t=out:st={DUR-1.5}:d=1.5[bg];"
    f"[bg][vok]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[bgd];"
    f"[vo][2:a][bgd]amix=inputs=3:normalize=0,alimiter=limit=0.9[a];[0:v]ass=subs.ass[v]")
OUT=EP+'/production/trial_open_v1.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i','picture.mp4','-i','vo_all.wav','-i','sfx.wav','-i',BGM,'-filter_complex',fc,'-map','[v]','-map','[a]',
 '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(DUR),'-movflags','+faststart',OUT],check=True)
print(OUT)
