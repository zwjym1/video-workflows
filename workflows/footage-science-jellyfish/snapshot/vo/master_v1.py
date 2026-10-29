# -*- coding: utf-8 -*-
"""take_v1.mp3 → 句间加呼吸停顿（只在句间能量最低处插静音，不拉伸）→ 去齿音（5–8 kHz 动态压，最大 6 dB）→ loudnorm −16 → vo_v1.wav + cards_master.json"""
import json, subprocess
from pathlib import Path
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
ROOT=Path(__file__).resolve().parent; SR=48000
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'take_v1.mp3'),'-ar',str(SR),'-ac','1',str(ROOT/'take_v1.wav')],check=True)
y,_=sf.read(str(ROOT/'take_v1.wav'))
cards=json.load(open(ROOT/'cards_timed.json'))
PAD={0:0.18,3:0.22,4:0.28,7:0.32,8:0.15,10:0.12,13:0.32,16:0.38}
LEAD=0.12
win=int(0.01*SR); env=np.sqrt(np.convolve(y**2,np.ones(win)/win,'same'))
pieces=[]; cur=0; ins=[]  # (orig_time, added)
for i,p in PAD.items():
    b=cards[i]['b']; a2=cards[i+1]['a']; lo=int((b-0.04)*SR); hi=int((a2+0.06)*SR)
    k=lo+int(np.argmin(env[lo:hi])); pieces+= [y[cur:k], np.zeros(int(p*SR))]; cur=k; ins.append((k/SR,p))
pieces.append(y[cur:]); yy=np.concatenate([np.zeros(int(LEAD*SR))]+pieces+[np.zeros(int(0.5*SR))])
def remap(t): return t+LEAD+sum(p for k,p in ins if t>=k)
# de-ess: 5–8 kHz band envelope above threshold → gain reduction up to 6 dB (applied to band only)
sos=butter(4,[5000,8000],btype='band',fs=SR,output='sos'); band=sosfiltfilt(sos,yy)
w=int(0.005*SR); be=np.sqrt(np.convolve(band**2,np.ones(w)/w,'same'))+1e-9
thr=np.percentile(be[be>1e-4],80); over=20*np.log10(np.maximum(be/thr,1)); gr_db=np.minimum(over*0.6,6.0)
gr_db=np.convolve(gr_db,np.ones(w*2)/(w*2),'same'); g=10**(-gr_db/20)
ds=yy-band+band*g
pre=ROOT/'vo_v1_pre_norm.wav'; sf.write(str(pre),ds,SR)
def meas(p):
    r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True)
    return json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}')+1])
m1=meas(pre)
flt=(f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m1['input_i']}:measured_TP={m1['input_tp']}:measured_LRA={m1['input_lra']}:measured_thresh={m1['input_thresh']}:offset={m1['target_offset']}:linear=true")
out=ROOT/'vo_v1.wav'; subprocess.run(['ffmpeg','-v','error','-y','-i',str(pre),'-af',flt,'-ar',str(SR),str(out)],check=True)
m2=meas(out)
for c in cards:
    c['a']=round(remap(c['a']),3); c['b']=round(remap(c['b']),3); c['chars']=[(ch,round(remap(a),3),round(remap(e),3)) for ch,a,e in c['chars']]
json.dump(cards,open(ROOT/'cards_master.json','w'),ensure_ascii=False,indent=1)
json.dump(dict(total_s=round(len(yy)/SR,3),pads=PAD,lead=LEAD,deess=dict(band='5-8kHz',max_db=6,mean_gr_db=float(gr_db.mean()),p95_gr_db=float(np.percentile(gr_db,95))),loud=m2,voice='906524668b6d4afe84736962e005cd09',model='s2.1-pro-free'),open(ROOT/'vo_v1.meta.json','w'),ensure_ascii=False,indent=1)
print('dur',round(len(yy)/SR,2),'LUFS',m2['input_i'],'TP',m2['input_tp'],'GR p95',round(float(np.percentile(gr_db,95)),2),'max',round(float(gr_db.max()),2))
