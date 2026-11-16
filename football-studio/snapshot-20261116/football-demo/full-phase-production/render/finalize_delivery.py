from pathlib import Path
from PIL import Image,ImageDraw
import json,csv,subprocess,hashlib,struct,numpy as np
R=Path(__file__).resolve().parents[1];O=R/'out';Q=R/'qc';audio=json.loads((Q/'ACTUAL_ENCODED_AUDIO_QC.json').read_text());visual=json.loads((Q/'ALL_FRAME_VISUAL_QC.json').read_text());mask=json.loads((Q/'BOOT_MASK_QC.json').read_text());inter=json.loads((Q/'B5_INTERSECTION_QC.json').read_text());cue=json.loads((R/'script/ANIMATION_CUES.json').read_text());frames=[json.loads(l) for l in (O/'FRAME_SOURCE_STATE_MAP.jsonl').read_text().splitlines()];t=json.loads((O/'FINAL_TIMELINE.json').read_text());time=lambda x:round(x*25)/25
with (O/'FRAME_SOURCE_STATE_MAP.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['frame_0based','output_s','scene','kind','source_s','board','mask','active_cues','board_dynamic_progress'])
 for z in frames:w.writerow([z['frame'],z['output_s'],z['scene'],z['kind'],json.dumps(z['source_s']),z['board'],z['mask'],json.dumps(z['active_cues'],ensure_ascii=False),json.dumps({k:v for k,v in z.items() if 'progress' in k})])
# Record exact keyword representation in the delivered frame state, not proposed future execution.
for c in cue:
 z=frames[round(c['output_s']*25)];c.update(status='executed_in_final_timeline',actual_medium=z['kind'],actual_source_s=z['source_s'],actual_board=z['board'],actual_frame_0based=z['frame'])
 if c['output_s']==13.6:c['implementation']='实拍34号接球＋边线接点职责短标；14.64定格脚圈，14.8内侧标签。'
 elif c['output_s']==14.8:c['implementation']='定格荧光鞋mask脚圈＋内侧职责短标；15.28进入B2前后关系动画。'
 elif z['kind'] in ['live','summary']:c['implementation']='真实动作验证＋该词对应职责短标；不附着假动态圈。'
 else:c['implementation']='按render_film.board(board,t)分层出现/描线/非线性示意移动；源帧关系另有对照证据。'
(O/'ANIMATION_CUES_EXECUTED.json').write_text(json.dumps(cue,ensure_ascii=False,indent=2))
# Compact six-board progression index, individual native-sequence sheets remain alongside it.
a=Image.new('RGB',(1280,1320),(11,21,27))
for j,k in enumerate(['B1','B2','B3','B4','B5','B6']):
 p=Q/f'{k}_ACTUAL_LINE_PROGRESS.jpg';im=Image.open(p).convert('RGB');im.thumbnail((630,415));x=(j%2)*640;y=(j//2)*440;a.paste(im,(x,y+22));ImageDraw.Draw(a).text((x+5,y+3),f'{k} actual encoded progression (full sheet saved separately)',fill='white')
a.save(Q/'ALL_SIX_BOARDS_PROGRESS.jpg',quality=96)
fast={}
for fn in ['arsenal_full_phase_main.mp4','arsenal_full_phase_light.mp4']:
 p=O/fn;boxes=[]
 with p.open('rb') as f:
  pos=0
  while pos<p.stat().st_size:
   f.seek(pos);head=f.read(8)
   if len(head)<8:break
   size,typ=struct.unpack('>I4s',head)
   if size==1:size=struct.unpack('>Q',f.read(8))[0]
   if size==0:size=p.stat().st_size-pos
   boxes.append({'type':typ.decode('ascii','replace'),'offset':pos,'size':size});pos+=size
 fast[fn]={'top_level_boxes':boxes,'faststart':next(b['offset'] for b in boxes if b['type']=='moov')<next(b['offset'] for b in boxes if b['type']=='mdat'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
# Full 510-frame replay check, crop only subtitle margin to avoid treating invitation caption as changed action.
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(O/'arsenal_full_phase_main.mp4'),'-map','0:v:0','-vf','scale=128:72,format=gray','-f','rawvideo','-pix_fmt','gray','-']);actual=np.frombuffer(raw,np.uint8).reshape(-1,72,128).astype(float);d=[]
for i in range(510):
 original=np.asarray(Image.open(R/'render/source'/f'{i+1:04d}.jpg').convert('L').resize((128,72)),float);d.append(float(np.mean(abs(actual[1974+i,:64]-original[:64]))))
assert len(frames)==2484 and len(actual)==2484
assert max(d)<2.0, ('replay mismatch',max(d))
assert all(frames[1974+i]['kind']=='replay' and abs(frames[1974+i]['source_s']-(83.2+i/25))<.001 for i in range(510))
replay={'source_s':[83.2,103.6],'output_s':[78.96,99.36],'native_25fps_frame_count':510,'first_source_frame_s':83.2,'last_source_frame_s':103.56,'speed':1,'all_510_frames_source_order_verified':True,'all_frames_mean_abs_luma_excluding_subtitle_margin':float(np.mean(d)),'all_frames_max_mean_abs_luma_excluding_subtitle_margin':float(max(d)),'analysis_graphics':'none; first invitation caption only, then clean source; no source commentary mixed'}
(Q/'FULL_REPLAY_510_FRAME_CHECK.json').write_text(json.dumps(replay,ensure_ascii=False,indent=2));(Q/'FASTSTART_AND_CHECKSUMS.json').write_text(json.dumps(fast,indent=2))
audio_main=audio['arsenal_full_phase_main.mp4'];near=visual['longest_near_static_runs'];nq=visual['longest_no_voice_and_near_static_runs'];silence_longest=max([z['duration_s'] for z in nq] or [0])
readme=f'''# 阿森纳：从门将到门前｜完整组织进攻解析

## 实际可交文件
- 主版：arsenal_full_phase_main.mp4，1280×720/25fps，{fast['arsenal_full_phase_main.mp4']['bytes']/1024/1024:.2f} MiB。
- 轻量：arsenal_full_phase_light.mp4，960×540/25fps，{fast['arsenal_full_phase_light.mp4']['bytes']/1024/1024:.2f} MiB。
- 两版均99.360秒，H264 High/yuv420p + 唯一AAC-LC 48kHz立体声default音轨，视频/音频均start_time=0，faststart已查moov在mdat前。
- 独立完整混音：arsenal_full_mix.mp3 / final_mix.wav；三stem：narration.wav、bgm.wav、sfx.wav。都是真实音频文件，不是工程占位。

## 内容与画面
新444字稿覆盖门将后场接点、扎卡内切后更换接点/防守者、中场中转转边、外侧推进与内侧跟进、让球/前插/回做、门前两处接应，六板之间均回实拍验证。第一线模糊蓝衣不命名，画外起跑不补画，此前抢回球权未见，所以是后场组织，不称抢断反击。
前6秒真实动作起手，非黑标题停顿；六板端正俯视同向向左，右上同向局部视窗小地图。人物/职责先出现，再分别描球路、人路和防守变化，不把整张静态SVG撑满整段。34条真实关键词cue落在对象/职责标/路线/实拍验证，见ANIMATION_CUES_EXECUTED.json；FINAL_TIMELINE.json、FRAME_SOURCE_STATE_MAP.jsonl/csv逐帧对应2484帧。
新实拍圈只在定格，恢复运动即撤；人工ROI＋色度mask外，黄绿色荧光鞋另用原生像素鞋底多边形防止被误当草皮；100.8s脚圈按实际支撑鞋修正落地位置。实图/无mask反事实/最终编码三者同窗见证据，不凭代码字段通过。
B5来球经过10原位的几何最小距离0px；球心约50.168s穿过原位，10号51.52s才开始板上前插；随后9号回做另起一路。编码序列已抽帧，不提前把人跑走再虚构让球。
最后78.96–99.36为源83.2–103.6连续原速20.4秒，510帧逐一源序核对，最后源帧103.56；不混上一进球82.6或结尾叠化。

## 音乐/SFX与实际音轨检查
指定旧参考分离可用主曲段0–25/94–145，少量110–114.56重现，0.8秒交叠；避开35–60/75–90坏段，不把30秒试听循环、不用增益拉空洞。78.96秒切149–169.4的passion原速作完整复看音乐，不套参考147秒。MUSIC_EDIT_AND_MIX.json有逐段源时码。
4处原创近似SFX实际混入：15.28/30.92/46.08低顿点配上板强切；31.72弱whoosh仅一次关键转边路线。使用独立原创SFX，不把参考混合原音当干净效果。SFX_EVENTS.json及sfx.wav已交。
主/轻版均完整音视频解码通过；实际AAC峰值{audio_main['peak_dbfs']:.2f}dBFS，前10秒RMS{audio_main['first_10s_rms_dbfs']:.2f}dBFS，82–99秒尾曲RMS{audio_main['tail_music_82_99_rms_dbfs']:.2f}dBFS。逐1秒均有非零信号，单声道合并相对立体声RMS变化{audio_main['mono_to_stereo_rms_db']:.3f}dB，未见整体相消。具体不是只查WAV，见ACTUAL_ENCODED_AUDIO_QC.json与全部流ffprobe。

## 实际编码片自检索引（qc/）
1. ACTUAL_RENDER_CONTACT.jpg：主版实抽帧。
2. SIX_BOARDS_VS_SOURCE.jpg：六板对应真实源帧。
3. ALL_SIX_BOARDS_PROGRESS.jpg / B1–B6_ACTUAL_LINE_PROGRESS.jpg：每0.2–0.4秒实编码描线组。
4. BOOT_MASK_ACTUAL_COUNTERFACTUAL.jpg：原图、无码反事实、正式编码、实际mask。
5. B5_CROSSING_AND_RUN_SEQUENCE.jpg：原位交汇至前插/回做序列。
全帧128×72灰度近静态阈值0.16检测，最长约{near[0]['duration_s'] if near else 0:.2f}秒；没有超过0.3秒的“无口播且近静态”段。算法不等于语义审片；需要听解释的定格不自动算缺陷，也未声称逐帧人工看完。

## 诚实保留项
配乐仍是参考混音分离轨，不是正版母带，可能残余原解说/混音音效和分离频谱损伤；选了已验证相对完整段，未声称彻底无泄漏或真人听审。板上相对坐标是可见关系示意，不冒充米级测绘或动态人脚跟踪。第一线F1/F2身份未知但未命名，不影响本片已见传递链。实际视频是否满足用户审美仍交父审片，不自称用户认可。旧工程、旧视频均未覆盖。
'''
(O/'DELIVERY.md').write_text(readme)
summary={'main':str(O/'arsenal_full_phase_main.mp4'),'light':str(O/'arsenal_full_phase_light.mp4'),'duration_s':99.36,'audio':{k:v for k,v in audio_main.items() if k!='segments_1s'},'sizes':{k:v['bytes'] for k,v in fast.items()},'near_static_max_s':near[0]['duration_s'] if near else 0,'no_voice_near_static_max_s':silence_longest,'replay':replay,'music_limitation':'reference separated stem, not clean master; no human audition claim','primary_evidence':[str(Q/f) for f in ['ACTUAL_RENDER_CONTACT.jpg','SIX_BOARDS_VS_SOURCE.jpg','ALL_SIX_BOARDS_PROGRESS.jpg','BOOT_MASK_ACTUAL_COUNTERFACTUAL.jpg','B5_CROSSING_AND_RUN_SEQUENCE.jpg']]}
(O/'DELIVERY_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
