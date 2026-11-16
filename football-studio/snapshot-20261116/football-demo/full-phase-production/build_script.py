from pathlib import Path
import json,csv,re,shutil
R=Path(__file__).parent
raw=[
('S00','开题','从门将到门前，阿森纳这次进攻，靠的是接应职责一站站交接。先从后场看起。',[83.2,86.2],'实拍起手，不先放射门；按门将→后场接点→边线接点给空间承诺。',None),
('S01','后场相邻接点','莱诺交给霍尔丁，球再到边线附近的扎卡。蓝衣向球侧靠近，阿森纳先用相邻的接点，把球送出后场。',[83.2,86.6],'实拍83.2–86.6→B1：先19再16再34；最近蓝衣只编号内部F1，不硬认名字。','B1'),
('S02','边线接球者带进内侧','扎卡接球后带向内侧。原来逼近他的十四号佩雷拉，随后变成从身后追赶；前内侧的托雷拉，是新的出球方向。',[86.6,89.8],'先原速86.6–88.6，88.6短定格标34/对方14，再B2前后状态。不能说整条防线被过。','B2'),
('S03','下一接点也面对新压力','托雷拉接球时，麦迪逊已经靠近。下一名接球人面对的防守，和扎卡刚才面对的，并不是同一个。',[88.6,91.0],'B2显示34→11白球路；保留14在34身后，新增10向11接近的相对位置；随后89.6–91.0实拍验证。','B2'),
('S04','中场一脚中转到外侧','球送到中圈。厄齐尔一脚转给贡多齐，贡多齐再向右路出球。中间负责中转，外侧负责接着向前送。',[90.6,95.6],'实拍90.6–93.6→B3按11→10→29→2逐段；人路另起，不把后脚跟的技术动作讲成全队读心。','B3'),
('S05','内外两条通道与回撤','看没有持球的人。贝莱林在外侧推进，伊沃比和厄齐尔沿内侧跟进；奇尔韦尔和恩迪迪，也在他们附近回撤。',[94.8,98.4],'95.2–97.6原速→97.6定格只解释17/3、10/25两组→B4局部板；24号追2号一侧作为语境，不说是3号盯2号。','B4'),
('S06','禁区前不是无人防守','所以禁区前不是一片空地。贝莱林回传时，十号身前有马奎尔，另一侧还有拉卡泽特。',[97.6,99.2],'98.4实拍定格依次显示10→15→9，再B5上下文；白来球穿过10号原位，不向旁边绕。','B5'),
('S07','9号回做接前插者','来球继续给九号，十号从马奎尔身侧进入禁区。拉卡泽特马上回做，把球送回前插者。',[98.4,100.8],'先98.4–100.8真实连续动作，必要99.2短停；B5先让白球越原位后才动10号，回做路线独立。','B5'),
('S08','同一防守者前后关系','这时再对比：马奎尔由身前变成身后追赶。进攻没有在第一次接应处停住，而是把接点往门里续了一步。',[98.4,100.8],'98.4/100.8同一蓝15前后对照；不把跨帧像素差当真实跑距；只用一次旧点/新点，不再复述三遍动画。','B5'),
('S09','门前不同接应位置','最后看门前另一侧。奥巴梅扬已经到位，佩雷拉还在回追；门将正向持球侧出击，横传把两处接应连到了一起。',[100.04,103.6],'B6以100.8/101.0确认10、A14、L14、门将1。只说14已在另一侧，不虚构他从边线开始的跑动；实拍兑现完整到103.6。','B6'),
('S10','职责链收束','后场留接点，内切后有人接，中间一脚中转，外侧继续推进，门前再接上回做。每一站，都把球交给了位置不同的队友。',[83.2,103.6],'正俯视总览按旁白逐段增亮实际经过的路线；不补未见球员或画假整队阵型。','SUMMARY'),
('S11','完整原速验证','去掉标注，完整看一遍。',[83.2,103.6],'完整20.4秒原速，旁白只在开始，随后纯原生运动+BGM；无静帧片尾。',None)]
scenes=[]
for sid,purpose,vo,src,vis,board in raw:scenes.append({'id':sid,'purpose':purpose,'voiceover':vo,'source_s':src,'visual':vis,'board':board,'narration_characters':len(re.findall('[\u4e00-\u9fffA-Za-z0-9]',vo))})
plan={'status':'ORIGINAL_SCRIPT_AND_ASSET_PREPARATION_NO_FINAL_RENDER','source':'/workspace/football-demo/new-source-candidates/arsenal-leicester-2018.mp4','clean_continuous_source_s':[83.2,103.6],'new_main_reference':'/workspace/football-demo/full-phase-new-reference/reference/watch_reference_h264.mp4','source_limits':['82.6秒仍是上一进球回放，绝不拿作本回合起因；83.2起为新的后场组织。','原镜头只显示本回合球附近的人，不复原未见22人站位或宣称整条防线都如何。','奥巴早段一度在画外，不复制新参考迪马利亚沿边线保持宽度的具体跑法。','只认已核号码；最近第一线蓝衣F1保留未定名，不把61分钟前首发名单硬套65分钟。'],'scenes':scenes,'timing_rule':'Fish真实逐字时码完成后定剪；本文件不填假预算时码。','sfx_rule':'使用父已给原创独立SFX，后续必须实混并交独立stem；候选混音片禁用。'}
(R/'script/ORIGINAL_SCRIPT.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2));(R/'script/VOICEOVER.txt').write_text('\n\n'.join(x['voiceover'] for x in scenes))
with (R/'script/SHOT_SCRIPT.csv').open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=scenes[0]);w.writeheader();w.writerows(scenes)
D=Path('/workspace/football-demo/full-phase-new-reference/audio-analysis/sfx_original_approx');(R/'audio/sfx_original').mkdir(exist_ok=True)
for name in ['cut_hit_low_muted.wav','ui_tick_soft.wav','whoosh_line_short.wav','circle_lock_soft.wav','MANIFEST.json']:
 if (D/name).exists():shutil.copy2(D/name,R/'audio/sfx_original'/name)
print('ORIGINAL_SCRIPT',sum(x['narration_characters'] for x in scenes),'characters',len(scenes),'scenes')
