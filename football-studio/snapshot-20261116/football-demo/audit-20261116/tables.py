import json,csv
from pathlib import Path
R=Path(__file__).parent;P=Path('/workspace/football-demo/manutd-tactics');tl=json.loads((P/'src/timeline.json').read_text());vo=json.loads((R/'sample_voice_detail.json').read_text())
def write(name,rows):
 with (R/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
notes={
'open':('实拍拉慢+两行问题','0–8整段标题；仅1–3.142有中文VO；无逐字显现','来源n2..131，约0.65x；不是定格'),
'first_watch':('实拍完整连续回放','8–9.8显示先看这一回；8.15–9.090中文VO；其余含低音量原解说','n0..181第一次整段；起始夹带源转场残帧'),
'play1':('实拍连续重启','15.267再次从n0开始；直到17.5无中文VO','开头再次夹带源转场残帧'),
'freeze1':('实拍定格','双正圆+球圈+11标签同时出现；无路径绘制','原帧n56；字幕17.5起整句s1'),
'board1':('静态战术板','点/圈0.05–0.45仅透明度渐入；不移动；字幕0.3后整句复现至板尾','20.815后无中文VO；无对应防守动作变化'),
'play2':('实拍拉慢约0.8x','无中文VO；无持久在线跟踪','n57..77'),
'freeze2':('实拍定格','双正圆+直虚线箭头+标签共用0.25s渐显；字幕27.7起整句s2','原帧n78；无先人物后传球的顺序'),
'board2':('静态战术板','0.05–0.45点渐入；0.35–0.85整条虚线透明渐入；点不移动；字幕0.3后至末尾','30.698后无中文VO；后续9.152s直至s3均无中文VO'),
'play3':('实拍拉慢约0.7x','无中文VO；无持久在线跟踪','n79..131'),
'freeze3':('实拍定格','球员正圆/空当圈/3个对手圆/远角直虚线同时显现；21汉字整句字幕','原帧n132；标记无语义分步'),
'slow_shot':('实拍拉慢约0.5x','前n133..140用相同坐标圈，后淡出；不是位置插值；字幕s3至44.7','n133..161'),
'board_recap':('静态总结板','0.45点出现；0.85传球箭头齐；1.5远角箭头齐；没有球/人运动','47.451后至51.333仅底乐；字幕45.267后至板尾'),
'replay':('实拍完整连续重复','无中文VO/新增标注，原场解说与人群混入','n0..181再次整段；源转场残帧第三次出现'),
'endcard':('纯黑落版','学习样片/来源文字固定；无中文VO','静止2.5s')}
rows=[];s=0
for j,seg in enumerate(tl['segments']):
 a=s/30;b=(s+seg['n_out'])/30;s+=seg['n_out'];ty,event,note=notes[seg['id']]
 overlaps=[f"{v['id']}:{max(a,v['placement']):.3f}–{min(b,v['file_end']):.3f}" for v in vo if max(a,v['placement'])<min(b,v['file_end'])]
 rows.append(dict(unit=j+1,id=seg['id'],start_s=f'{a:.6f}',end_s=f'{b:.6f}',duration_s=f'{b-a:.6f}',visual_type=ty,caption_annotation_sequence=event,vo_file_overlap=';'.join(overlaps) or '无中文VO文件',source_or_limit=note,basis='timeline精确帧数+render.py+人工候选/关键帧复核'))
write('sample_shots.csv',rows)
# Boundaries are human-reviewed editing-unit anchors; dissolve anchors are not hard camera cuts.
data=[
(0,'人物抠图/标题','激光眼+问题标题；字幕随两句引入变化；非实拍运动'),
(127,'实拍全景','组织进攻；长句指明布斯克茨接球；连续场面'),
(228,'战术板','17.133s内依次球员关系→德容相对安全→身前空当→穆勒位置→传球线路；局部推近；不是17s同一板'),
(742,'实拍带脚圈','回到底片；横扁黄/红脚圈区分人物；说明穆勒置于德容身后'),
(808,'同源实拍冻结→慢推进','闪白/冻结标志；脚圈+宽带传球线；30s后转身传球；33–38侧移缩短距离；38–41抢断；非单一绝对静帧'),
(1239,'实拍重构/跳接','同回合格纳布里得球；此处为构图跳变锚点，不断言独立摄影机'),
(1304,'实拍近景','持球推进；叠化换景锚点；43.767为叠化尾不另算镜头'),
(1394,'实拍近景换角度','斜向叠化至腿部持球近景'),
(1425,'实拍全景','反击分左路；连续传跑'),
(1523,'战术板','高后卫线→身后空间→回防禁区；区域带/箭头/镜面位置变化；斜擦转入'),
(1869,'实拍带跟随圈','佩里西奇接球前穆勒放慢→回头观察→举手；圈随人位移，不只图形微动'),
(2150,'战术板','全防线面向边路；扇形视线/弧顶空区/传球路线分层；斜擦'),
(2373,'实拍全景','挑传弧顶；球运动与落点'),
(2525,'实拍另一角度','接球前后，白闪换角度；黄圈跟随/局部推近；不推断精确倍速'),
(2689,'实拍冻结→连续推进','假射姿势→吸引封堵→垫给莱万；冻结后恢复球/人运动'),
(3034,'战术板','先外跑牵动阿尔巴→突然内切；位置/线路/空区分步'),
(3310,'实拍近景慢推进','莱万背身回做→穆勒停球→射门；中途大帧差多为球与摄影机快动，不分成多个镜头'),
(3591,'实拍门后','门将扑救与入网；120s附近多候选为运动而非换镜'),
(3679,'总结战术板','编号四步骤依次出现；串联断球/推进分边/压回防线/撞墙终结；非重复同一条说明'),
(4240,'实拍回扣','抢断镜段；闪白/叠化回扣'),
(4280,'实拍回扣','同回合另一阶段；白闪锚点，是否独立机位未判定'),
(4297,'实拍近景回扣','撞墙/终结近景'),
(4317,'实拍全景回扣','回扣空间选择；叠化锚点'),
(4405,'人物标题','这就是空间阅读者；中文解释至ASR148.06s'),
(4472,'未加战术标记实拍','原回合连续全景回放；无新中文解说证据'),
(4612,'未加标记近景','持球推进镜头；154.267为同镜头快动'),
(4657,'未加标记全景','分边进攻'),
(4732,'未加标记近景','传中/接应；159.6/160.0为运动候选'),
(4809,'未加标记全景','门前配合及射门；165.7为摄像机/球运动'),
(5010,'庆祝近景→淡黑','球员庆祝；167.467/168.833/169.833不是新镜头；170.667后渐黑')]
rows=[]
for j,(f,ty,nt) in enumerate(data):
 e=data[j+1][0] if j+1<len(data) else 5131
 rows.append(dict(unit=j+1,start_frame=f,end_frame_exclusive=e,start_s=f'{f/30:.6f}',end_s=f'{e/30:.6f}',duration_s=f'{(e-f)/30:.6f}',visual_type=ty,caption_annotation_sequence=nt,boundary_basis='候选F-2/F/F+2人工复核；叠化取最大变化锚点而非声称首帧；全景内未逐一精分所有速度变化'))
write('reference_shots.csv',rows)
# More granular semantic events in the first 45 seconds. Approximate boundaries are explicitly flagged.
ev=[(0,1.9,'标题','为什么全场都在追着球跑的时候','ASR+可见字幕'),(1.9,4.233333,'标题','只有他在看球会落到哪里；问题标题完成','ASR0–3.92；结束镜段锚点'),(4.233333,7.6,'实拍连续','布斯克茨中场接横传；场景建立','可见字幕+精确镜段'),(7.6,10.3,'战术板','穆勒/德容关系与圈注引入','结束约值，1fps联系表±0.5s'),(10.3,13,'战术板','注意看→此时巴萨正在中场组织进攻','两端约值±0.5s；13s精确图已核'),(13,15,'战术板','盯人关系；局部推近并轮换人物焦点','边界约值±0.5s'),(15,17,'战术板','德容相对安全：红色标签与圈','边界约值±0.5s；16s字幕逐字可见'),(17,20,'战术板','出现身前空当；揭示骗局；增加黄色空区','边界约值±0.5s；19s精确图已核'),(20,22,'战术板','穆勒早已贴在德容身边；黄圈重焦','边界约值±0.5s；21s精确图已核'),(22,24.733333,'战术板','白虚线传球线路及小标签出现','开始约值±0.5s；23s精确图已核'),(24.733333,26.933333,'实拍带脚圈','位置藏于德容身后；区分红黄角色','精确镜段锚点；语句为机转写交叉图像'),(26.933333,30.066667,'冻结/闪白引导','黄宽带+虚线说明线路看似畅通；30s增加小标签','边界为镜段锚点与ASR；仍有少量装饰微动，不算新增战术命题'),(30.066667,33.133333,'实拍慢推进','布斯克茨转身准备传球，位置随画面更新','ASR词句区间约值；30s仍有FREEZE，32s已释放，精确释放首帧未标'),(33.133333,35.1,'实拍慢推进','穆勒侧移；黄圈跟人；加入方向曲线/标签','ASR区间+35s精确图'),(35.1,38,'实拍慢推进','解释侧移使球与穆勒距离更近','ASR+37s精确图；图形为动作证据而非只旋转'),(38,41.3,'实拍慢推进','抢在触球前铲断','ASR+40s精确图'),(41.3,43.466667,'实拍全景','球到格纳布里，反击启动','切换锚点+ASR'),(43.466667,45,'实拍近景','推进甩开回追者；45s处截断本附表','切换锚点+ASR')]
write('reference_first45_events.csv',[dict(start_s=a,end_s=b,duration_s=round(b-a,6),visual_type=t,event=n,time_evidence=q) for a,b,t,n,q in ev])
# All scan candidates are reviewed, not automatically called cuts.
true={f:ty for f,ty,nt in data[1:]}
reject={817:'冻结闪白/曝光恢复尾，不是新镜头',1313:'叠化恢复尾，不重复计镜头',2698:'闪白恢复尾，不是新镜头',3325:'同近景球员/摄影机位移',3539:'同近景射门动作/摄影机位移',3548:'同近景球运动/摄影机位移',3567:'同近景镜头追球',3576:'同近景镜头追球',3600:'新机位后的亮度变化/运动',3613:'门后摄像机/门网运动',3626:'门后摄像机/门网运动',4628:'近景跟拍/腿部运动',4788:'同镜头跟拍/球员运动',4800:'同镜头跟拍/球员运动',4971:'同镜头追射门',5024:'庆祝动作',5065:'庆祝动作/球员进入画面',5095:'庆祝动作',5120:'尾部淡出',5130:'尾部淡出'}
for name in ['reference','sample']:
 sc=json.loads((R/f'{name}_scan_summary.json').read_text());rs=[]
 for c in sc['candidate_transitions']:
  f=c['frame'];good=(f in true) if name=='reference' else True
  rs.append(dict(frame=f,time_s=c['time'],algorithm_mad=c['mad'],algorithm_hist_tv=c['hist_tv'],manual_disposition=('编辑镜段锚点（非必然摄影机切换）' if good else '不另算镜头'),manual_evidence_note=(true.get(f,reject.get(f,'同场景变化')) if name=='reference' else 'timeline边界已核；8/15.267/51.333包含源残帧'),review_image=f'{name}_candidate_review_{list(sc["candidate_transitions"]).index(c)//10:02d}.jpg'))
 write(f'{name}_candidate_classification.csv',rs)
# VO-free intervals, explicitly distinct from silence / absence of any human voice.
gaps=[];last=0
for v in vo:
 if v['placement']>last:gaps.append((last,v['placement']))
 last=v['file_end']
if last<61.1:gaps.append((last,61.1))
sourceaudio=[(8,17.5003),(51.333,58.5997)]
grs=[]
for a,b in gaps:
 src=sum(max(0,min(b,y)-max(a,x)) for x,y in sourceaudio)
 grs.append(dict(start_s=a,end_s=b,duration_s=b-a,cn_vo_file='无',source_commentary_overlap_s=src,background='含源英文解说/人群混音，不能称无人声' if src else '按mix.py只有背景底乐；不是静音'))
write('sample_no_cn_vo_gaps.csv',grs)
static={}
for name in ['reference','sample']:
 sc=json.loads((R/f'{name}_scan_summary.json').read_text());dur=sc['decoded_duration'];rr=sc['runs']['near_static_full']
 static[name]={'video_duration_s':dur,'frame_count':sc['frames'],'full_near_static_total_s':sum(x['duration'] for x in rr),'full_near_static_pct':100*sum(x['duration'] for x in rr)/dur,'longest_near_static_s':max(x['duration'] for x in rr),'first45_near_static_s':sum(max(0,min(45,x['end'])-x['start']) for x in rr),'candidate_count':len(sc['candidate_transitions'])}
static['sample_voice']={'file_window_s':sum(v['file_duration'] for v in vo),'file_window_pct':100*sum(v['file_duration'] for v in vo)/61.1,'vad_candidate_sum_s':sum(x['end']-x['start'] for v in vo for x in v['vad_local']),'han_char_count':sum(v['han_char_count'] for v in vo),'largest_no_cn_vo_gap_s':max(b-a for a,b in gaps)}
static['board_vo_free_tails']=[{'start':vo[2]['file_end'],'end':26.6},{'start':vo[3]['file_end'],'end':36.766666666666666},{'start':vo[5]['file_end'],'end':51.333333333333336}]
static['board_vo_free_tail_total_s']=sum(x['end']-x['start'] for x in static['board_vo_free_tails'])
(R/'audit_stats.json').write_text(json.dumps(static,ensure_ascii=False,indent=2));print(json.dumps(static,ensure_ascii=False,indent=2))
