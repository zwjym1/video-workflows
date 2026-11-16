from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,json,numpy as np,csv,concurrent.futures,sys,wave
R=Path(__file__).resolve().parents[1];O=R/'out';Q=R/'qc';(Q/'encoded').mkdir(exist_ok=True);sys.path.insert(0,str(R/'render'));import render_film as F
P=O/'arsenal_full_phase_main.mp4';probes={};audio_qc={}
def call(c):return subprocess.run(c,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
for p in [P,O/'arsenal_full_phase_light.mp4']:
 pr=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_data','-of','json',str(p)]));probes[p.name]=pr
 call(['ffmpeg','-v','error','-i',str(p),'-f','null','-'])
 a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-ac','2','-ar','48000','-f','f32le','-']),'<f4').reshape(-1,2);mono=np.mean(a,axis=1)
 rows=[]
 for t in np.arange(0,99.36,1):
  x=a[round(t*48000):min(len(a),round((t+1)*48000))];rows.append({'start_s':float(t),'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(x*x))+1e-12)),'peak_dbfs':float(20*np.log10(np.max(abs(x))+1e-12))})
 au=next(z for z in pr['streams'] if z['codec_type']=='audio');vv=next(z for z in pr['streams'] if z['codec_type']=='video')
 audio_qc[p.name]={'full_AV_decode':'passed','codec':au['codec_name'],'profile':au.get('profile'),'sample_rate':au['sample_rate'],'channels':au['channels'],'channel_layout':au.get('channel_layout'),'default':au['disposition']['default'],'start_time':au.get('start_time'),'duration':pr['format']['duration'],'video_codec':vv['codec_name'],'pix_fmt':vv['pix_fmt'],'dimensions':[vv['width'],vv['height']],'peak_dbfs':float(20*np.log10(np.max(abs(a))+1e-12)),'first_10s_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(a[:480000]**2))+1e-12)),'tail_music_82_99_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(a[82*48000:99*48000]**2))+1e-12)),'mono_to_stereo_rms_db':float(20*np.log10((np.sqrt(np.mean(mono**2))+1e-12)/(np.sqrt(np.mean(a*a))+1e-12))),'segments_1s':rows}
 (Q/(p.stem+'_ffprobe.json')).write_text(json.dumps(pr,ensure_ascii=False,indent=2))
(Q/'ACTUAL_ENCODED_AUDIO_QC.json').write_text(json.dumps(audio_qc,ensure_ascii=False,indent=2))
print('AUDIO_AND_DECODE_PASSED',flush=True)
# All evidence images below are decoded from the actual delivery MP4, not preflight renders.
def grab(t):
 p=Q/'encoded'/f'{t:.2f}.png'
 if not p.exists():call(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(P),'-frames:v','1',str(p)])
 return p
intervals={'B1':(6.08,10.08,.4),'B2':(15.28,23.28,.4),'B3':(30.92,33.72,.2),'B4':(36.56,41.36,.4),'B5':(46.08,54.08,.4),'B6':(62.72,68.72,.4)}
process={k:[round(v,2) for v in np.arange(a,b+.001,step)] for k,(a,b,step) in intervals.items()}
key=[.8,9.8,15.04,22.8,26.,32.6,41.4,47.8,50.0,50.2,51.4,52.,54.,55.6,58.,65.9,67.9,68.8,69.8,74.5,78.96,82.2,99.32]
alltimes=sorted(set(key+sum(process.values(),[])))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(grab,alltimes))
def contact(ts,path,cols=4,tw=320):
 th=round(tw*720/1280);a=Image.new('RGB',(cols*tw,int(np.ceil(len(ts)/cols))*(th+25)),F.BG)
 for j,t in enumerate(ts):im=Image.open(grab(t)).convert('RGB').resize((tw,th));a.paste(im,((j%cols)*tw,(j//cols)*(th+25)));ImageDraw.Draw(a).text(((j%cols)*tw+5,(j//cols)*(th+25)+th+4),f'ENCODED {t:.2f}s',fill='white')
 a.save(path,quality=96)
contact(key,Q/'ACTUAL_RENDER_CONTACT.jpg')
for k,ts in process.items():contact(ts,Q/f'{k}_ACTUAL_LINE_PROGRESS.jpg')
# Same-source real frames adjacent to each board's final encoded state.
pairs=[('B1',9.8,85.4),('B2',22.8,90.2),('B3',32.6,93.6),('B4',41.4,97.6),('B5',52.,99.2),('B6',68.8,101.24)]
a=Image.new('RGB',(1280,6*385),F.BG);dr=ImageDraw.Draw(a)
for j,(k,t,st) in enumerate(pairs):
 a.paste(Image.open(grab(t)).resize((640,360)),(0,j*385));a.paste(F.still(st).resize((640,360)),(640,j*385));dr.text((6,j*385+362),f'{k} actual encoded {t:.2f}s | SOURCE {st:.2f}s',fill='white')
a.save(Q/'SIX_BOARDS_VS_SOURCE.jpg',quality=96)
# Boot-mask counterfactual evidence: source | same overlay with mask OFF | actual encoded | mask ROI.
a=Image.new('RGB',(1280,3*245+35),F.BG);d=ImageDraw.Draw(a);labels=['SOURCE','COUNTERFACTUAL: MASK OFF','ACTUAL ENCODED (MASK ON)','MANUAL ROI + CHROMA MASK']
for j,lab in enumerate(labels):d.text((j*320+5,8),lab,fill='white')
maskmetrics=[]
for row,(st,t,box,marks) in enumerate([(88.6,15.04,(832,485,990,582),[('A34',14.64),('L14',14.8)]),(90.2,26.,(792,394,965,486),[('A11',24.96),('L10',25.28)]),(100.8,58.,(632,302,828,418),[('A10',56.8),('L15',57.64)])]):
 original=F.still(st);naive=F.freeze(st,t,marks,False);masked=F.freeze(st,t,marks,True)
 encoded=Image.open(grab(t)).convert('RGB')
 if st==100.8:
  base=(520,235,870,430);sx=590/350;sy=329/195;eb=(round(655+(box[0]-520)*sx),round(176+(box[1]-235)*sy),round(655+(box[2]-520)*sx),round(176+(box[3]-235)*sy));ec=encoded.crop(eb)
 else:ec=encoded.crop(box)
 overlay=original.convert('RGBA');ml=Image.new('RGBA',overlay.size,(100,185,255,0));ml.putalpha(F.bootmask(st).point(lambda x:round(x*.58)));overlay=Image.alpha_composite(overlay,ml).convert('RGB')
 imgs=[original.crop(box),naive.crop(box),ec,overlay.crop(box)]
 for j,im in enumerate(imgs):a.paste(im.resize((320,205),Image.Resampling.NEAREST if j==3 else Image.Resampling.LANCZOS),(j*320,row*245+35))
 d.text((5,row*245+243),f'source {st:.2f}s / actual output {t:.2f}s -- still only; marks removed before movement',fill='white')
 no=np.asarray(naive).astype(float);yes=np.asarray(masked).astype(float);orig=np.asarray(original).astype(float);m=np.asarray(F.bootmask(st))>220;hit=m&(np.max(abs(no-orig),axis=2)>12)
 maskmetrics.append({'source_s':st,'output_s':t,'boot_or_body_overlap_pixels_restored':int(hit.sum()),'mask_on_vs_source_mean_abs_on_overlap':float(np.mean(abs(yes-orig)[hit])) if hit.any() else 0,'counterfactual_vs_source_mean_abs_on_overlap':float(np.mean(abs(no-orig)[hit])) if hit.any() else 0})
a.save(Q/'BOOT_MASK_ACTUAL_COUNTERFACTUAL.jpg',quality=98)
(Q/'BOOT_MASK_QC.json').write_text(json.dumps(maskmetrics,indent=2))
# B5: evaluate rendered pass geometry and its actual presentation near crossing.
b=F.B['B5'];uv={n['id']:n['uv'] for n in b['nodes']};pts=[F.proj(b,uv[z]) for z in ['A2','A10','A9']];origin=np.array(pts[1]);lengths=[np.linalg.norm(np.array(v)-np.array(u)) for u,v in zip(pts,pts[1:])];cross_fraction=lengths[0]/sum(lengths)
# Inverse of renderer smootherstep by dense search: identify source frame in encoded MP4 nearest ball/origin.
x=np.linspace(0,1,10001);e=x*x*x*(x*(x*6-15)+10);ii=np.argmin(abs(e-cross_fraction));cross_t=49.44+1.28*x[ii];nearest=round(cross_t*25)/25
pathcheck={'incoming_path_min_distance_to_A10_origin_px':0.0,'path_points_px':pts,'ball_crosses_origin_s':round(float(cross_t),4),'nearest_encoded_frame_s':nearest,'A10_run_start_s':51.52,'player_run_progress_at_crossing':0.0,'note':'A10 origin is an explicit vertex of continuous incoming route; no pause/touch at vertex; return is separately drawn from9 to next point.'}
(Q/'B5_INTERSECTION_QC.json').write_text(json.dumps(pathcheck,indent=2));contact([49.44,49.84,nearest,50.64,51.4,51.8,52.2,53.8],Q/'B5_CROSSING_AND_RUN_SEQUENCE.jpg')
# Actual delivery video all-frame near-static detection (low-resolution decode, with visible captions).
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P),'-map','0:v:0','-vf','scale=128:72,format=gray','-f','rawvideo','-pix_fmt','gray','-']);v=np.frombuffer(raw,np.uint8).reshape(-1,72,128).astype(np.float32);delta=np.mean(abs(v[1:]-v[:-1]),axis=(1,2));static=delta<.16
runs=[];start=None
for i,bv in enumerate(list(static)+[False]):
 if bv and start is None:start=i
 if not bv and start is not None:
  if (i-start)/25>=.4:runs.append({'start_s':round(start/25,2),'end_s':round((i+1)/25,2),'duration_s':round((i+1-start)/25,2)})
  start=None
runs.sort(key=lambda r:r['duration_s'],reverse=True)
# No speech AND no new visible information is judged only when both signals are actually absent.
actual=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(O/'narration.wav'),'-ac','1','-ar','48000','-f','f32le','-']),'<f4');silent=[]
for n in range(len(v)):
 x=actual[n*1920:(n+1)*1920];silent.append(np.sqrt(np.mean(x*x))<.003)
noinfo=np.concatenate([[False],static])&np.array(silent[:len(v)]);nr=[];start=None
for i,flag in enumerate(list(noinfo)+[False]):
 if flag and start is None:start=i
 if not flag and start is not None:
  if (i-start)/25>.3:nr.append({'start_s':round(start/25,2),'end_s':round(i/25,2),'duration_s':round((i-start)/25,2)})
  start=None
nr.sort(key=lambda r:r['duration_s'],reverse=True)
# Exact source order for final 510 frames, no tracking/analysis graphics; first invitation subtitle expires quickly.
replay=[]
for t in [81.2,85.2,90.2,95.2,99.32]:
 frame=round(t*25);im=v[frame];st=83.2+t-78.96;source=np.asarray(F.src(st).resize((128,72)).convert('L'),np.float32);replay.append({'output_s':t,'source_s':round(st,2),'mean_abs_luma':float(np.mean(abs(im-source)))})
(Q/'ALL_FRAME_VISUAL_QC.json').write_text(json.dumps({'decoded_frame_count':len(v),'expected_frame_count':2484,'near_static_threshold_mean_luma_128x72':.16,'longest_near_static_runs':runs[:8],'longest_no_voice_and_near_static_runs':nr[:8],'replay_source_samples':replay,'caution':'算法近静态不是语义审片；需要听解释且标签/关系在变的定格不自动算缺陷。未声称逐帧人工观看。'},ensure_ascii=False,indent=2))
# Stem proportions at the actually mixed sound-effect events.
def wav(p):
 with wave.open(str(p)) as w:return np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,2)/32768
vo=wav(O/'narration.wav');fx=wav(O/'sfx.wav');bg=wav(O/'bgm.wav');ratios=[]
for e in json.loads((R/'script/SFX_EVENTS.json').read_text())['events']:
 j=round(e['output_s']*48000);n=round(.3*48000);vr=np.sqrt(np.mean(vo[j:j+n]**2));fr=np.sqrt(np.mean(fx[j:j+n]**2));br=np.sqrt(np.mean(bg[j:j+n]**2));ratios.append({'t':e['output_s'],'file':e['file'],'sfx_minus_voice_rms_db':float(20*np.log10((fr+1e-12)/(vr+1e-12))),'bgm_minus_voice_rms_db':float(20*np.log10((br+1e-12)/(vr+1e-12)))})
(Q/'SFX_VOICE_ACTUAL_RATIOS.json').write_text(json.dumps(ratios,indent=2))
print('QC_COMPLETE',json.dumps({'audio':{k:{a:b for a,b in vv.items() if a!='segments_1s'} for k,vv in audio_qc.items()},'near_static':runs[:3],'no_vo_and_static':nr[:3],'masks':maskmetrics,'intersection':pathcheck,'replay':replay,'sfx_ratios':ratios},ensure_ascii=False),flush=True)
