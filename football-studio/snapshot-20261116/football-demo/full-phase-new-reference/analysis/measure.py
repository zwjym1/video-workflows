from pathlib import Path
import subprocess,numpy as np,json,csv
from scipy.signal import stft,find_peaks
R=Path(__file__).resolve().parents[1];p=R/'reference/video.mp4';sr=16000;a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-ac','1','-ar',str(sr),'-f','f32le','-']),np.float32);freq,ts,z=stft(a,fs=sr,nperseg=512,noverlap=352,boundary=None);power=np.abs(z)**2;rms=np.sqrt(np.maximum(power.sum(0),1e-20));flux=np.maximum(np.diff(np.log1p(np.abs(z)*100),axis=1),0).mean(0);fi=ts[1:];inds,_=find_peaks(flux,distance=45,prominence=np.quantile(flux,.80)*.35);rank=sorted(inds,key=lambda i:flux[i],reverse=True);chosen=[]
for i in rank:
 t=float(fi[i])
 if t<1 or t>112:continue
 if all(abs(t-x)>4 for x in chosen):chosen.append(t)
 if len(chosen)==12:break
chosen.sort();records=[]
for j,t in enumerate(chosen,1):
 st=max(0,t-1.0);en=min(len(a)/sr,t+1.4);n=int(np.argmin(abs(ts-t)));tot=power[:,n].sum();b=a[int((t-.10)*sr):int((t+.15)*sr)];row={'id':f'T{j:02d}','reference_peak_s':round(t,3),'context_start_s':round(st,3),'context_end_s':round(en,3),'positive_log_spectral_flux':float(flux[np.argmin(abs(fi-t))]),'peak_dbfs_250ms':float(20*np.log10(np.max(abs(b))+1e-12)),'rms_dbfs_250ms':float(20*np.log10(np.sqrt(np.mean(b*b))+1e-12)),'energy_fraction_under_250Hz':float(power[freq<250,n].sum()/tot),'energy_fraction_over_3kHz':float(power[freq>3000,n].sum()/tot),'status':'混音瞬态候选，尚未认定为音效；可能来自语音或音乐，需与实画/识别交叉核查','semantic_timbre':'not_identified','visual_event_match':'pending_parent_watchVideo'};records.append(row);out=R/'sfx-candidates'/f"{row['id']}_{t:.2f}s_context.wav";subprocess.run(['ffmpeg','-v','error','-y','-ss',str(st),'-i',str(R/'audio/reference_original.wav'),'-t',str(en-st),'-c:a','pcm_s16le',str(out)],check=True)
(R/'analysis/TRANSIENT_CANDIDATES.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
with (R/'analysis/TRANSIENT_CANDIDATES.csv').open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
# Real-v-board type changes at .1s from actual video, classify visually distinct backgrounds.
b=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vf','fps=10,scale=160:120','-an','-f','rawvideo','-pix_fmt','rgb24','-']),np.uint8).reshape(-1,120,160,3);red=b[:,:,:,0].astype(np.int16);green=b[:,:,:,1].astype(np.int16);blue=b[:,:,:,2].astype(np.int16);ratio=((green>55)&(green>red*1.12)&(green>blue*1.08)).mean((1,2));types=np.where(ratio>.25,'live_or_live_freeze','board_or_black_title');runs=[]
for i,typ in enumerate(types):
 if not runs or runs[-1]['mode']!=typ:runs.append({'start_s':i/10,'end_s':(i+1)/10,'mode':str(typ)})
 else:runs[-1]['end_s']=(i+1)/10
(R/'analysis/SHOT_TYPE_RUNS.json').write_text(json.dumps({'method':'真实视频10fps草皮色占比；只区分实拍/板或黑底，不等于精确剪辑镜头检测；叠化需复看','runs':runs,'live_or_freeze_seconds_approx':float(np.sum(types=='live_or_live_freeze')/10),'board_or_title_seconds_approx':float(np.sum(types=='board_or_black_title')/10)},ensure_ascii=False,indent=2));print('SFX_CANDIDATES',[(r['id'],r['reference_peak_s']) for r in records],flush=True);print('SHOT_RUNS',runs,flush=True)
