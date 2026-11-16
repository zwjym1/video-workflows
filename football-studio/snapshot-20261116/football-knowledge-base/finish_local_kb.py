from pathlib import Path
import json,shutil,csv,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
R=Path('/workspace/football-knowledge-base');C=[json.loads(l) for l in (R/'concepts.jsonl').read_text().splitlines()];S=[json.loads(l) for l in (R/'sources/source_registry.jsonl').read_text().splitlines()];now=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
(R/'analysis_checklist.md').write_text('''# 从“播报传球”到有证据的战术解释

## 一条主问题贯穿，不给每个人强塞一个术语
1. 先提出对手造成的具体阻碍：接点被盖住？背后有人？边路施压但中路仍有跑者？别以“精彩配合”当问题。
2. 标明阶段、攻向、当时人数/比分与镜头边界。当前阿森纳素材83.2起门将已控球，回收球权过程不见；不称抢断反击。比分牌显示领先，不编扳平压力。
3. 只锁定决定这一问的3–6人，不必全22人。缺全景限制结论，不把专业分析砍成谁传谁。
4. 比较动作前—中—后：原来哪条路难走？做了什么？哪个防守者怎样反应？新的可用动作/风险是什么？
5. 允许有依据的功能解释：“这一接点提供…选择”“该跑动与…一致”“若防守跟出，可能…”。不必每句堆“可能”，只在关键推断层说明边界。
6. 证据达到A移动→D跟走→B利用时，可解释牵制；只有A跑或D随球横移时不够。无需证明脑内意图，但不可把结果倒推为赛前设计。
7. 写一个能推翻自己的反例：补位其实已到？接球者只能回传？球路本就畅通？裁切掉一名补位者？
8. 每板回答一个具体疑问，先对象/防守，再动作/球路，再变化后的选择，回实拍验证。术语放在白话之后。
9. 一口气说四个姓名却没解释阻碍/反应/收益，删顺序播报，补关系；只写“空间被拉开”却不指哪两人之间，重写。
10. 有威胁不等于必进，传球成功不等于推进成功，第一解围不等于防守结束；也不从最后进球倒推之前每一步都最优。

## 三层证据不是“只许讲事实”
- L0可见：A接球、D靠近、B沿内侧跑、球最终到哪里。
- L1功能推断：A-D-B的前后变化支持“此动作提供/限制了什么选择”。这是专业分析核心，必须保留；给相关反应和反例，不读心。
- L2真实意图/计划：他“早知道”“故意骗过”“教练赛前安排每一步”。需要当事人可靠说明或额外材料；单镜头通常不能支持。

## 术语落地门槛
- 破压：标出哪条线被越过及接后下一脚；不是球过线就完。
- 第三人：明确A/B/C及直达为何受限；A-B-A先叫两人回做。
- 牵制：明确谁被带到哪、谁因此受益，以及补位是否存在。
- 人数优势：数及时能参与的人，不能只数裁切后画内人。
- 线间：两条防线需可见；半空间通道不等于线间层。
- 压迫触发：有启动前参照和至少两人配合；一人追球不能证明整队陷阱。
- 剩余防守：需要球后/对方出口视野；看不到不补标准3+2。

## 拒绝门槛与可继续路径
仅关键姓名模糊→称角色/号码；少一个画外人→只讲本地关系；缺整条前因→改阶段起点。只有“核心因果无法观察且无替代证据”才换选题，不能把谨慎变成只播报或无休止找镜头。
''')
(R/'audience_translation.md').write_text('''# 双层表达：普通人先懂问题，老球迷能核查机制

不是把术语替换成形容词，而是保留“对手问题→行动→防守反应→收益/代价”。

## 口播骨架（原创编辑法，不是机构官方课程）
- 问题：为什么边上拿球，中间的人还要继续跑？
- 观察：17和10在内侧，3和25仍在附近回撤。
- 机制：外侧推进时，内侧接点也需要被照顾；内外分工保留回传/中路接应，不必只冲底线。
- 术语后置：这就是内外通道的接应分工；只有真从同伴内侧超越，才进一步叫内套。
- 兑现：回原速，核对球怎样接到下一站。不是在板上讲完后让实拍硬等。

## 双层示例
|普通话先说|给老球迷的第二层|不好的堆词|
|---|---|---|
|直着找不到他，就借队友转一手接上他的跑位。|三人间接连接，检查A-C被封、B改变角度、C时机。|第三人轮转解锁自由人。|
|前面去抢，后面得留住被过以后的那条路。|压迫与斜后保护的距离/角度联动。|压迫覆盖平衡闭环。|
|球后那几人让球队丢了还能接着防。|rest defence与对方出口的可达关系，非机械数3+2。|剩余防守保证绝对安全。|
|让防守顾两条真能用的路，而不是在图上多一个圆点。|局部人数和位置优势需在同一动作时限内兑现。|2v1必破。|

## 观众喜欢：只能做编辑假设，不是留存承诺
一条主问题；前几秒给真实矛盾/动作；每次停画增加一个发现；同一问题按职责递进；只引入当下有用的术语；每个关键解释回原速能验证。反常识用“为什么回传反而能向前？”之类可检验问题，不写“99%球迷不懂”。
没有该账号实际完播/留存/评论理解数据，本库不预测必火，也不能说“观众都喜欢战术板”。未来在相同比较窗口记录开场问题、术语密度、解释节点与真实观众反馈；不能把播放量变化单因果归给知识库。
''')
(R/'clip_selection.md').write_text('''# 选片：先有值得回答的问题，再找进球

## 必过的证据门
有完整的“阻碍—选择—防守反应—结果”局部链；攻防关系可复查；能用一个问题概括；关键画外未知不决定结论。可选守成/逼回/丢球，不以进球作硬门槛。

## 四组成对反例（是编辑情境，不冒充新核实比赛）
1. 普通横传：无人压、阵型未变、下一脚无变化，只能说A给B→低分析值。相似横传若跨过球侧压力，对手横移来不及、另一侧接球能推进→值得讲“换边改变处理时间”。
2. 普通回传：只是维持球权，缺前压与后续镜头→不硬称诱敌。相似回传若把背压交给队友处理，再找到跑出压力的第三点→高值，即使最后射偏。
3. 美丽世界波：只有球飞进门/慢放脚法→娱乐强但完整战术分析弱；可做诚实技术短讲，不编前因。一段守住禁区、协防补位后逼对方回传→虽无进球，若职责变化清晰，可高值。
4. 丢球回合：单纯停球失误特写→难支撑整套体系崩溃。若有压迫触发、封下一脚、接应被切断并最终丢球的完整证据→高值；同样也可讲进攻怎样避免此局面。

## 编辑启发评分，非平台留存预测
按0/1/2记录：问题清晰、预期落差、可见防守反应、前中后连续、机制可证伪、白话可解释、板能增益、原速可验证。总分只帮助同类候选比较，无统计训练或保证流量的意义。核心反应/连续性为0先补镜头或换问题，不能靠名气/进球把分补回来。不要为了反常识强找“所有人都错了”。

## 当前阿森纳素材的真正可用主问题
不是“这20秒里谁传给谁”，而是“外侧推进时，内侧接应怎样连续接上，最后把原位接球改成防线另一侧接球？”后场至中场只能解释已见接点和压力变化；不要因为终结漂亮给每次普通传递都编一层神机妙算。
''')
EX=[
{'id':'E01','scene':'S04','output_s':[27.8,35.66],'source_s':[91.6,93.6,95.6],'old_text':'球送到中圈。厄齐尔一脚转给贡多齐，贡多齐再向右路出球。中间负责中转，外侧负责接着向前送。','diagnosis':['主要是传球顺序＋抽象职责，缺“为何需要这一中转”的问题。','防守证据并非没有：91.6接球附近蓝衣、93.6的24号与后续外侧回追可见，原稿没将其转成选择解释。'],'visible':['91.6厄齐尔接球附近有蓝衣；中场传递连续。','93.6贡多齐附近24号、贝莱林在外侧；97.6外侧持球/回追关系可复核。'],'rewrite':'中间这一下的价值，不是多传一次。厄齐尔附近已经有蓝衣；他借贡多齐把球送到外侧，贝莱林继续往前。这样，中间的人不必自己连续带球，也能把推进交到另一条通道，再无球跟上。','reasoning':'一脚中转提供从中央接点到外侧推进的办法；附近压力与转边后动作支持此功能解释，但不证明原先直带必定失败。','cannot_add':['不能说贡多齐把整条防线吸到中路。','不能说贝莱林完全无人防守，24号在该侧回追。','不声称厄齐尔当时看见全部选项、故意骗谁。'],'cards':['K04','K06','K08'],'board_question':'这一手中转，让哪条继续推进的路线接上了？','board_group':'A11/A10/A29/A2及附近L24/L25，分先后状态，不把所有人固定在一帧。'},
{'id':'E02','scene':'S05','output_s':[35.66,42.96],'source_s':[93.6,97.6,98.4],'old_text':'看没有持球的人。贝莱林在外侧推进，伊沃比和厄齐尔沿内侧跟进；奇尔韦尔和恩迪迪，也在他们附近回撤。','diagnosis':['比纯播报进了一步，但仅罗列球走/人走与附近回撤。','缺少“球在外侧时，内侧人为什么不能停”的具体防守问题。'],'visible':['93.6到97.6，17号与10号沿内侧跟进，3号/25号在附近回撤。','97.6持球者在外侧，24号在其一侧回追；6/15等较深防守仍存在。','98.4回传时10号已跟到禁区前接应位置。'],'rewrite':'球在边上，里面的人为什么还要跑？因为外侧有人推进，内侧也得有下一脚可接。17号和10号继续跟，3号和25号也在附近回撤；这让蓝衣不能只处理边上的球，内侧跑动也要有人接住。等边路回传，下一站已经接上。','reasoning':'这里可解释“内外同时形成推进与接应职责”，防守须兼顾两类威胁；并不等于内侧无人保护或确证谁被故意牵走。','cannot_add':['不称17/10必定做了内套：平行内侧跟进未必从同伴内侧超越。','不写拉卡泽特吸引中卫清空中路：缺完整跟出—空位利用链。','不写明确2v1；6/15等补位者可见。'],'cards':['K11','K12','K13','K14'],'board_question':'边上带球时，里面两条跑线让防守多了什么任务？','board_group':'A2、A17/L3、A10/L25，保留L24与较深可见保护作语境，不删除防守者造空当。'},
{'id':'E03','scene':'S09','output_s':[62.7,70.48],'source_s':[100.8,101.24,102.2],'old_text':'最后看门前另一侧。奥巴梅扬已经到位，佩雷拉还在回追；门将正向持球侧出击，横传把两处接应连到了一起。','diagnosis':['姓名/位置真实、已有门将证据，但末句“连起来”只复述横传的几何结果。','缺“横传比继续在同侧处理多提供了什么终结办法”。'],'visible':['100.8门将已朝持球一侧出来；A14在另一侧、L14回追。','101.24厄齐尔触球/传球时门将出击，奥巴在佩雷拉前侧。','随后原速见横传到另一侧终结，不只是一个静帧。'],'rewrite':'门将已经向厄齐尔这一侧出来，另一侧的奥巴还跑在佩雷拉前面。横传不是为了再多倒一脚，而是把最后一下交到门将移动的另一侧。这就提供了一个不必正面硬过门将的终结办法。','reasoning':'门将/两接点/追防相对位置与实际球路支持功能解释；不需要证明球员脑内意图。','cannot_add':['不能倒推奥巴从早先边线一路包抄，前段不在画面。','不称横传必进、唯一正确或门将被故意骗出。','不是所有低平横传都叫倒三角，本次先按实际相对门线方向叫横传。'],'cards':['K16','K17','K24'],'board_question':'门将来到这一侧以后，另一侧的接点为什么更有用？','board_group':'A10、A14、L1、L14及最近能干预者；画实际传球方向，不把对手当不存在。'}]
for ex in EX:ex['actual_evidence_files']=[f'/workspace/football-demo/full-phase-production/evidence/source_{x:.2f}.jpg' for x in ex['source_s']];ex['application_status']='仅知识库应用样例，未改原稿/未重渲；新对白长度不是现有秒数预算。'
(R/'worked_examples/arsenal_application.json').write_text(json.dumps({'source_script':'/workspace/football-demo/full-phase-production/out/FINAL_SCRIPT.txt','actual_film':'/workspace/football-demo/full-phase-production/out/arsenal_full_phase_main.mp4','original_source':'/workspace/football-demo/new-source-candidates/arsenal-leicester-2018.mp4','method':'实际读取交付稿与本轮原尺寸源帧；结合已有连续源帧和逐帧映射；不把新理论当旧回合实证。','examples':EX},ensure_ascii=False,indent=2))
(R/'worked_examples/README.md').write_text('# 当前99.36秒片的三段检验\n\n实际文件是FINAL_SCRIPT.txt，不是不存在的FINAL_SCRIPT.md；场景与时间取FINAL_TIMELINE.json。没有改原片/原稿或自动再渲。改写为应用样例，如重制须按新真实配音另排，不强塞原时轴。\n\n'+'\n\n'.join(f'## {e["id"]} {e["scene"]}\n\n原句：{e["old_text"]}\n\n诊断：'+ '；'.join(e['diagnosis'])+'\n\n可见依据：'+'；'.join(e['visible'])+'\n\n普通话改写：'+e['rewrite']+'\n\n允许的专业解释：'+e['reasoning']+'\n\n不能补写：'+'；'.join(e['cannot_add'])+'\n\n卡片：'+','.join(e['cards'])+'\n源时点：'+str(e['source_s'])+'\n板问题：'+e['board_question'] for e in EX))
(R/'README.md').write_text('''# 足球战术解读知识库 v1

用户访问入口为本轮知识库Page（真实URL写入PAGE_LINK.md后使用）；本目录是以后制作可检索的结构化资料，不是新软件产品，也不替代教练资格课程。

- concepts.jsonl：36张深入卡，按比赛问题与阶段组织；每卡有条件、前中后观察、最低镜头、事实/推断/未知、反例、白话/坏句、板上关系与具体来源章节。
- taxonomy.json：9个阶段入口，另标尚未覆盖领域。
- sources/source_registry.jsonl + notes/：20篇实际阅读公开专业正文，13 FIFA、3 UEFA、4 Coaches’ Voice。公开可读≠开源；不复制整书/课件/原图/视频。
- analysis_checklist.md：先找防守问题，再解释选择与反应；允许有依据的战术功能推断，避免过度谨慎退回传球播报。
- audience_translation.md：新手白话＋老球迷可检验机制；术语后置，观众偏好仅是编辑假设。
- clip_selection.md：4组成对筛片反例及编辑评分，不预测流量。
- worked_examples/：实际99.36秒阿森纳片S04/S05/S09的诊断、证据、改写及不能补写的论断；未重渲或改制作系统。
- resources/：父交已核8项GitHub资源及统一许可决定；仅指针/规范与模型边界，不导入商业受限原始数据。

## 查询协议
先用阶段找卡，再按当前“对手造成的问题”检索opponent_problem与minimum_evidence；写稿时同时读取counterexample和source_refs，不只抽plain_one_sentence。模型数据不足时不调用模型名制造权威。更新要记录来源、定义变化与适用场景，不以新增术语数衡量进步。

## 边界
v1覆盖常见组织/推进/最后三区/无球支援/压迫/防线/转换/低位/定位球/阵型观察问题，不声称穷尽足球。尚未系统覆盖界外球、点球、间接任意球专项、女子/青少年/成年差异、体能与长期训练。嵌入源视频未逐一观看；读过的是公开正文。尚无该账号真实留存/完播实验，不能承诺观众喜欢或必火。
''')
(R/'CHANGELOG.md').write_text(f'''# CHANGELOG\n\n## v1.0｜{now}（Asia/Shanghai）\n- 实际阅读20篇专业公开正文，形成36张问题驱动的卡，不收全文。\n- 增加L0事实/L1功能推断/L2真实意图分层，修复“太谨慎只播报”的旧机制。\n- 增加双层表达、反例与完整回合选片门槛；编辑评分非留存预测。\n- 以实际阿森纳稿3段作应用检验，未重渲。\n- 合并8项GitHub资源指针，纠正“全GitHub没有教材”的绝对说法，限定本轮8项目；不引入原始数据/书/视频。\n- 明确第三人宽窄定义、half-space/线间、角球分类口径与xG分母风险，不把流派当定理。\n''')
# Validate field completeness, source integrity and real worked-example evidence.
required=['concept_zh','concept_en','phase','opponent_problem','preconditions','observe','minimum_evidence','visible_facts','reasoned_interpretation','unknown_intent','counterexample','plain_one_sentence','jargon_bad','board_relations','source_refs','dual_layer']
for c in C:
 assert all(c.get(k) for k in required),c['id'];assert set(c['observe'])=={'before','during','after'},c['id']
 for ref in c['source_refs']:assert ref['id'] in {s['id'] for s in S} and ref['section']
for e in EX:
 for p in e['actual_evidence_files']:assert Path(p).exists(),p
with (R/'sources/card_source_crosswalk.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['card','concept','source','section','url'])
 for c in C:
  for ref in c['source_refs']:w.writerow([c['id'],c['concept_zh'],ref['id'],ref['section'],ref['url']])
(R/'VALIDATION.json').write_text(json.dumps({'at':now,'card_count':len(C),'professional_source_count':len(S),'source_card_links':sum(len(c['source_refs']) for c in C),'github_resources_count':8,'all_cards_required_fields_complete':True,'all_36_cards_have_before_during_after':True,'worked_examples':3,'actual_evidence_paths_exist':True,'no_original_raw_data_imported':True,'no_original_video_modified':True,'page_status':'pending_actual_WriteCanvas'},ensure_ascii=False,indent=2))
print('LOCAL_KB_VALIDATED',len(C),'cards',len(S),'sources',sum(len(c['source_refs']) for c in C),'card-source links; worked examples evidence present')
