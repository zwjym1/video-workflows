from pathlib import Path
import json,re,csv,subprocess,wave,numpy as np
R=Path(__file__).parent;P=json.loads((R/'script/ORIGINAL_SCRIPT.json').read_text());V=json.loads((R/'script/VOICE_TIMESTAMPS.json').read_text());VD={x['id']:x for x in V};starts={};cur=.04
for v in V:
 starts[v['id']]=cur
 if v['id']!='S11':cur+=v['core_end']+.1
VERIFY=round(cur*25)/25;starts['S11']=VERIFY;END=VERIFY+20.4

def chars(v):
 out=[]
 for w in v['words']:
  for i,ch in enumerate(w['text']):out.append({'ch':ch,'start':w['offset']+i*w['duration']/len(w['text']),'duration':w['duration']/len(w['text'])})
 return out
CH={k:chars(v) for k,v in VD.items()}
def wt(k,s):
 x=CH[k];full=''.join(z['ch'] for z in x);i=full.find(s)
 if i<0:raise ValueError((k,s,full))
 return starts[k]+x[i]['start']
def q(t):return round(t*25)/25
captions=[]
for sc in P['scenes']:
 k=sc['id'];full=''.join(x['ch'] for x in CH[k]);pos=0
 for s in re.split('[，。；：]',sc['voiceover']):
  if not s:continue
  ix=full.find(s,pos)
  if ix<0:raise ValueError(s)
  cc=CH[k][ix:ix+len(s)];captions.append({'start_s':starts[k]+cc[0]['start'],'end_s':starts[k]+cc[-1]['start']+cc[-1]['duration'],'text':s,'scene':k});pos=ix+len(s)
for i,sc in enumerate(P['scenes']):sc.update(output_start_s=starts[sc['id']],output_end_s=starts[P['scenes'][i+1]['id']] if i+1<len(P['scenes']) else END,actual_voice_end_s=starts[sc['id']]+VD[sc['id']]['core_end'])
(R/'script/ACTUAL_TIMELINE.json').write_text(json.dumps({'duration_s':END,'fps':25,'verify_start_s':VERIFY,'verify_source_s':[83.2,103.6],'status':'actual_narration_timing_and_assets_ready_no_final_render','scenes':P['scenes'],'captions':captions},ensure_ascii=False,indent=2))
# Sentence-level source evidence, not merely whole-scene broad ranges.
source_sets={
'S00':[[83.2,86.6],[83.2]],'S01':[[83.2,84.6,86.6],[84.6,85.4,86.6]],'S02':[[86.6,88.6],[86.6,88.6,89.4],[88.6,90.2]],'S03':[[89.4,90.2,90.6],[88.6,90.2]],'S04':[[90.6,91.6],[91.6,93.0,94.6,95.6],[91.6,93.6,97.6]],'S05':[[93.6,97.6],[95.2,97.6],[93.6,97.6,98.4]],'S06':[[97.6,98.4],[98.4]],'S07':[[98.6,98.84,99.08,99.56],[99.56,100.04,100.52,100.8]],'S08':[[98.4,100.8],[98.4,99.2,100.8]],'S09':[[100.52,100.8],[100.8,101.24],[100.04,101.24,102.2]],'S10':[[83.2,86.6,88.6,91.6,93.6,97.6,98.4,100.8],[83.2,103.6]],'S11':[[83.2,103.6]]}
rows=[]
for sc in P['scenes']:
 ss=[x for x in re.split('[。；]',sc['voiceover']) if x];evidence=source_sets[sc['id']]
 if len(ss)!=len(evidence):raise ValueError((sc['id'],ss,evidence))
 for j,s in enumerate(ss):
  t=wt(sc['id'],re.split('[，：]',s)[0]);src=evidence[j];rows.append({'scene':sc['id'],'sentence':s,'output_voice_start_s':round(t,3),'source_evidence_s':json.dumps(src),'board':sc['board'],'relationship':sc['purpose'],'evidence_files_or_extract':'从原官方源按所列时码抽帧；已有evidence/source_*.jpg；具体门前98.4/100.8亦在旧源证据中，不用上一进球82.6帧。'})
with (R/'script/SENTENCE_SOURCE_MAP.csv').open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
# Cue anchors are tied to generated word timestamps. The compositor must select matching live/freeze/board states.
cues=[]
def add(board,scene,token,event):cues.append({'board':board,'scene':scene,'word':token,'output_s':q(wt(scene,token)),'event':event,'status':'execution_anchor_not_claim_already_rendered'})
for b,k,t,e in [
('B1','S01','莱诺','context_A19'),('B1','S01','霍尔丁','show_A16_pass_19_16'),('B1','S01','扎卡','show_A34_pass_16_34'),('B1','S01','蓝衣','show_F1_unidentified_pressure'),
('B2','S02','扎卡','state_before_A34_L14'),('B2','S02','内侧','run_A34_inward'),('B2','S02','身后追赶','L14_after_relative_position'),('B2','S02','托雷拉','show_A11_outlet'),('B2','S03','麦迪逊','show_L10_new_pressure'),
('B3','S04','中圈','show_A11_A10'),('B3','S04','贡多齐','pass_A10_A29'),('B3','S04','贡多齐再','board_entry_and_relay'),('B3','S04','右路','pass_A29_A2_once'),
('B4','S05','贝莱林','show_outside_carrier_A2'),('B4','S05','伊沃比','show_inside_A17'),('B4','S05','厄齐尔','show_inside_A10'),('B4','S05','奇尔韦尔','show_L3_near_A17'),('B4','S05','恩迪迪','show_L25_near_A10'),
('B5','S06','十号','show_A10_before'),('B5','S06','马奎尔','show_L15_in_front'),('B5','S06','拉卡泽特','show_A9_other_side'),('B5','S07','继续给九号','incoming_ball_crosses_A10_old_point'),('B5','S07','进入禁区','A10_run_after_ball_passed'),('B5','S07','回做','A9_return_to_A10_new_point'),('B5','S08','身后追赶','compare_same_L15_after'),
('B6','S09','奥巴梅扬','show_A14_already_other_side'),('B6','S09','佩雷拉','show_L14_trailing_not_A14'),('B6','S09','门将','show_L1_moves_toward_ball_side'),('B6','S09','横传','pass_A10_A14'),
('SUMMARY','S10','后场','highlight_first_outlets'),('SUMMARY','S10','内切','highlight_A34_A11'),('SUMMARY','S10','中转','highlight_A10_A29'),('SUMMARY','S10','外侧','highlight_A2'),('SUMMARY','S10','回做','highlight_A9_A10')]:add(b,k,t,e)
(R/'script/ANIMATION_CUES.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2))
sfx=[{'scene':'S02','token':'原来','file':'cut_hit_low_muted.wav','kind':'sparse_board_cut','relative_rms_below_voice_db':10},{'scene':'S04','token':'贡多齐再','file':'cut_hit_low_muted.wav','kind':'sparse_board_cut','relative_rms_below_voice_db':10},{'scene':'S06','token':'十号','file':'cut_hit_low_muted.wav','kind':'sparse_board_cut','relative_rms_below_voice_db':10},{'scene':'S04','token':'右路','file':'whoosh_line_short.wav','kind':'single_key_route_optional_original_approx','relative_rms_below_voice_db':15}]
for s in sfx:s['output_s']=q(wt(s['scene'],s['token']));s['provenance']='父交独立原创近似SFX，不是参考混音截取';s['bind_rule']='必须在该时点真实出现对应硬切/描线；后续若镜头切点调整，本事件同步移或删除，不跟BGM找拍。'
# Real aligned VO+SFX timing preview, no BGM and no final film claim.
sr=48000;n=round(END*sr);vo=np.zeros((n,2),np.float32);fx=np.zeros_like(vo)
def dec(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ac','2','-ar','48000','-f','f32le','-']),np.float32).reshape(-1,2)
for v in V:
 a=dec(v['file'])[:round((v['core_end']+.035)*sr)].copy();gain=min(1.55,max(.72,.135/(np.sqrt(np.mean(a*a))+1e-9)));a*=gain;j=round(starts[v['id']]*sr);vo[j:j+len(a)]+=a
for s in sfx:
 a=dec(R/'audio/sfx_original'/s['file']);target=.135*10**(-s['relative_rms_below_voice_db']/20);gain=target/(np.sqrt(np.mean(a*a))+1e-12);a=a*gain;j=round(s['output_s']*sr);fx[j:j+len(a)]+=a;s['preview_gain_linear']=float(gain);s['preview_placed_rms_dbfs']=float(20*np.log10(np.sqrt(np.mean(a*a))+1e-12))
peak=float(np.max(np.abs(vo+fx)));scale=min(1,.84/(peak+1e-9));vo*=scale;fx*=scale
for name,a in [('VOICE_ONLY_TIMED.wav',vo),('SFX_ONLY_TIMED.wav',fx),('VO_SFX_TIMING_PREVIEW.wav',vo+fx)]:
 with wave.open(str(R/'audio'/name),'w') as f:f.setparams((2,2,sr,0,'NONE','not compressed'));f.writeframes((a*32767).clip(-32768,32767).astype('<i2').tobytes())
(R/'script/SFX_EVENTS.json').write_text(json.dumps({'status':'actually_mixed_in_timing_preview_not_final_video','events':sfx,'preview_master_scale':scale,'no_bgm_yet':True,'no_reference_narration_used':True},ensure_ascii=False,indent=2));print('ACTUAL_TIMELINE',END,'verify',VERIFY,'sentences',len(rows),'animation_cues',len(cues),'SFX_EVENTS',[(s['output_s'],s['file']) for s in sfx],flush=True)
