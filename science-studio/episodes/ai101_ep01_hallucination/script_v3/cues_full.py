# 全片逐镜时间轴源数据（机读）。时间：('v',x)=本镜第1句人声起点+x；('s',x)=本镜起点+x；('l2',x)=本镜第2句起点+x。
# build_full.py 解析成绝对秒 -> shots_v3.json（picture.py / final.py 直接读取）+ script_tzs_v3.md（审核）。
import json,os
EPD='/workspace/science-studio/episodes/ai101_ep01_hallucination'
VOICE={'O':'ebea2d0931f54cd69ec7d5e88db6b084','F':'9510b59280f74ad197f10b61eaa5abba'}
RT=EPD+'/test/retest_2026-11-03/'
def rd(p,n=None):
    s=open(p).read().replace('**','').replace('#','').strip()
    return s if n is None else s[:n]
def E(_b,_at,k,**kw):return dict(t=(_b,_at),k=k,**kw)
def V(x):return ('v',x)
def S(x):return ('s',x)
Y,R,B,GR,WH=(255,214,64),(255,120,100),(120,200,255),(120,220,140),(255,255,255)
X=820
SH={}
# ---------------- 镜 1–20（沿用 trial_v4 样板） ----------------
HK=dict(anim='none',nosnap=1,until=('s',0.95),anim_out='fade',fo=0.3)
SH[1]=dict(o=[('s',0,'pose_talk_point','严肃微吃惊')],f=[],react='鱼不在场',stage_zoom=1.0,el=[
 # v4 第0帧钩子：打叉截图 + 问句大字，0–1.0s 在画面，随后淡出
 E('s',0,'browser',src='01d_xiangshan_cableway_bjd_20261016.png',crop=[260,90,1020,260],w=420,title='news.bjd.com.cn · 2026-10-16',x=300,y=330,rot=-4,**HK),
 E('s',0,'big',text='×',size=220,col=(230,40,40),x=300,y=340,**HK),
 E('s',0,'stamp',text='不是餐厅',size=190,x=1080,y=480,rot=-8,**HK),
 E('s',0,'stamp',text='人均 ¥120–200',size=96,x=1060,y=730,rot=-5,**HK),
 E('s',0,'card',text='AI 推荐：双清别墅',size=40,x=320,y=560,rot=2,**HK),
 E('s',0,'stamp',text='索道已停运',size=56,x=320,y=690,rot=-10,**HK),
 E('s',0,'big',text='AI 推荐的餐馆，居然不存在？',size=92,col=Y,x=960,y=140,**HK),
 E('s',1.02,'browser',src='01_cctv_bjd_20261101.png',crop=[0,0,1280,1600],w=720,title='news.bjd.com.cn · 2026-11-01',x=640,y=545,rot=-2,anim='fade',fd=0.35,nosnap=1,
   push=1,tp0=('s',3.576),tp1=('s',4.0),pz=2.2,rel=(-126.4,-257.4),fx=780,fy=470,box=[300,304,508,336],tbox=('s',4.087)),
 E('v',1.85,'fx',name='impact_star',x=330,y=330,s=0.8),E('v',1.85,'big',text='推荐的餐馆：不存在',size=84,col=WH,x=700,y=420,rot=-4,until=('s',3.576),anim_out='fade',fo=0.25),
 E('s',4.087,'fx',name='impact_star',x=1300,y=800,s=0.8),E('s',4.087,'hlbig',text='建议乘坐的索道已停运两年',size=80,dt=0.12,x=760,y=800,rot=2),E('s',4.598,'card',text='央视',size=34,bg=R,fg=WH,x=1260,y=710,rot=6)])
SH[2]=dict(o=[('s',0,'pose_talk_idle','看鱼，微惊'),('v',0.3,'pose_react_surprise','被抢话吃惊')],f=[('s',0,'fish_f09_point_self','拍胸脯'),('s',0.51,'fish_f01_brag_scroll','得意举卷轴')],react='O 吃惊后仰',el=[
 E('s',0.25,'img',src='p01_scroll.png',h=640,x=980,y=520,rot=6,sway=1.0),E('s',0.35,'fx',name='sparkle_burst',x=980,y=380,s=1.4),
 E('s',1.0,'fx',name='twinkle',x=1180,y=300,s=1.2),
 E('s',0.51,'fx',name='sparkle_burst',x=1000,y=330,s=1.0),E('v',0.45,'card',text='餐馆 ✓',size=48,bg=GR,x=960,y=430,rot=-4),E('v',0.95,'card',text='索道 ✓',size=48,bg=GR,x=990,y=600,rot=3)])
# v4：镜2/3 合并成同一画面（鱼留在场、卷轴同位置、无切点）；「越要查」放大镜+红叉，O 摇头
SH[3]=dict(o=[('s',0,'pose_deadpan','冷脸半眼'),('l2',-0.1,'pose_talk_idle','摇头否决')],o_shake=[(('l2',0.7),('l2',1.18))],f=[('s',0,'fish_f01_brag_scroll','举卷轴'),('l2',0,'fish_f03_head_hold','被否抱头')],react='鱼留在场',xf=0.0,el=[
 E('s',0,'img',src='p01_scroll.png',h=640,x=980,y=520,rot=6,sway=1.0,anim='none'),
 E('s',0,'card',text='餐馆 ✓',size=48,bg=GR,x=960,y=430,rot=-4,anim='none'),E('s',0,'card',text='索道 ✓',size=48,bg=GR,x=990,y=600,rot=3,anim='none'),
 E('v',0.0,'fx',name='slash',x=960,y=430,s=1.2),E('v',0.0,'fx',name='slash',x=990,y=600,s=1.2),
 E('v',0.0,'mag',size=200,x=1060,y=500,rot=-12),E('v',0.0,'fx',name='cross_draw',x=980,y=540,s=1.6,ease=None),
 E('l2',0.75,'stamp',text='越肯定 越要查',size=56,x=980,y=800,rot=-6,anim='stamp')])
SH[4]=dict(o=[('s',0,'pose_talk_idle','口语摊手'),('l2',0,'pose_deadpan','听鱼嘴硬，冷眼'),('l3',0,'pose_talk_idle','摇头否决')],f=[('s',0,'fish_f05_akimbo_proud','叉腰嘴硬')],react='鱼说话时 O 冷眼；O 否决时鱼闭嘴眨眼',el=[
 E('s',0,'img',src='p02b_local_map.png',h=620,x=X,y=560,anim='none',zoom=0.02),E('s',0,'card',text='北京',size=44,x=X-200,y=330),
 E('v',0.1,'img',src='p02c_map_pin.png',h=170,x=X+180,y=460),E('v',0.15,'fx',name='shockwave',x=X+180,y=540),E('v',0.25,'card',text='济南',size=54,bg=Y,x=X+180,y=330)])
SH[5]=dict(o=[('s',0,'pose_talk_point','讲故事')],f=[],react='鱼滑出画',punch=[V(3.0)],el=[
 E('s',0,'img',src='p03_stopwatch.png',h=560,x=X-60,y=600,anim='none'),
 E('v',0.0,'roll',a='AI：8 分钟',b='实际：37 分钟',fmt='实际：{} 分钟',va=8,vb=37,r0=V(2.2),r1=V(3.0),x=X-60,y=250,anim='none'),
 E('v',3.0,'fx',name='impact_star',x=X+170,y=230,s=0.7),E('s',0.4,'src_tag',src='02_jinan_qlwb.png',crop=[80,0,1200,700],label='齐鲁晚报')])
SH[6]=dict(o=[('s',0,'pose_think','歪头轻嘲')],f=[],react='—',el=[
 E('s',0,'card',text='地铁 · 直达站',size=52,bg=(40,120,220),fg=WH,x=X,y=300),E('v',0.5,'img',src='p04_construction.png',h=540,x=X,y=620,anim='slide_up'),
 E('v',0.85,'fx',name='dust_poof',x=X,y=860,s=1.6)])
SH[7]=dict(o=[('s',0,'pose_talk_idle','平叙')],f=[],react='—',el=[
 E('s',0,'flip',src='p05_boarding_pass.png',w=900,tf=V(2.3),x=X,y=560),E('s',0,'card',text='直飞',size=60,bg=Y,x=X,y=330,anim='none',until=V(2.3)),
 E('v',2.5,'card',text='这个航班号 → 另一条航线',size=50,bg=R,fg=WH,x=X,y=330),E('v',2.75,'fx',name='cross_draw',x=X+300,y=560,s=1.3),
 E('s',0.4,'src_tag',src='03_jinan_flight_dzplus.png',crop=[0,0,1280,900],label='大众新闻')])
SH[8]=dict(o=[('s',0,'pose_talk_point','一字一顿加重')],f=[('s',0,'fish_f02_sunglasses_slam','墨镜拍桌（不说话）')],react='鱼墨镜拍桌入画，闭嘴',el=[
 E('v',0.15,'fx',name='impact_star',x=620,y=700,s=1.3),E('v',0.2,'card',text='！！！',size=90,fg=(240,60,60),x=900,y=300,rot=-6),
 E('v',1.2,'fx',name='pop_exclaim',x=1040,y=520,s=1.2),E('v',2.0,'fx',name='pop_exclaim',x=780,y=560,s=1.0),E('v',2.7,'card',text='从不说“我猜”',size=50,bg=Y,x=900,y=820)])
SH[9]=dict(o=[('s',0,'pose_peace','解释腔，指术语卡')],f=[],react='鱼滑出画',punch=[V(1.0)],el=[
 E('v',0.05,'fx',name='pop_question',x=X,y=420,s=1.6),E('v',0.1,'card',text='这个毛病叫……',size=56,bg=Y,x=X,y=300,rot=-3),
 E('v',1.2,'fx',name='marker_highlight',x=X,y=580,s=2.0,ease=None),E('v',1.0,'card',text='幻觉 ＝ 一本正经地胡说',size=84,bg=(255,255,250),x=X,y=540),
 E('v',1.5,'card',text='定义参考：OpenAI《Why language models hallucinate》',size=26,bg=(235,235,240),x=X,y=690),
 E('v',1.6,'src_tag',src='05_openai_blog.png',crop=[0,0,1280,900],label='OpenAI 博客')])
SH[10]=dict(o=[('s',0,'pose_deadpan','听鱼辩解，冷眼')],f=[('s',0,'fish_f03_head_hold','抱头委屈')],react='O 冷眼不动',el=[
 E('v',0.3,'fx',name='sweat_drop',x=620,y=250,s=1.2),E('v',1.6,'fx',name='sweat_drop',x=560,y=240,s=1.0),E('v',1.8,'card',text='记性不好？',size=54,x=980,y=330,rot=4)])
SH[11]=dict(o=[('s',0,'pose_peace','比 2，预告')],f=[],react='鱼滑出画',tab='两个毛病',el=[
 E('v',1.5,'card',text='①  ？？？',size=64,bg=Y,x=X+90,y=420),E('v',1.85,'card',text='②  ？？？',size=64,bg=B,x=X+90,y=620),E('v',1.5,'fx',name='sparkle_burst',x=X,y=420)])
SH[12]=dict(o=[('s',0,'pose_think','听鱼提问，歪头')],f=[('s',0,'fish_f04_shrug','摊手好奇')],react='O 歪头听',tab='① 从哪冒出来',el=[
 E('v',0.05,'card',text='① 这些话从哪来？',size=56,bg=Y,x=980,y=360,rot=-3),E('v',1.6,'fx',name='pop_question',x=1180,y=560,s=1.3)])
SH[13]=dict(o=[('s',0,'pose_talk_point','先夸后反转')],f=[],react='鱼滑出画',tab='① 从哪冒出来',punch=[V(1.4)],el=[
 E('v',0.25,'card',text='查资料',size=60,x=X-260,y=520),E('v',0.85,'fx',name='cross_draw',x=X-260,y=520,s=1.3,ease=None),
 E('v',1.4,'card',text='接龙',size=60,bg=Y,x=X+260,y=520),E('v',1.7,'fx',name='check_draw',x=X+260,y=520,s=1.3,ease=None)])
SH[14]=dict(o=[('s',0,'pose_talk_idle','机制段，快')],f=[],react='—',tab='① 从哪冒出来',el=[
 E('v',0.2,'card',text='猜下一个字',size=40,bg=B,x=X,y=140),E('v',0.6,'typing',text='香山脚下有家百年老店，招牌菜是……',dt=0.32,x=X,y=720),
 E('s',0,'card',text='演示 · 非真实数据',size=26,bg=(235,235,240),x=X+420,y=840,anim='none')])
SH[15]=dict(o=[('s',0,'pose_think','压低')],f=[],react='—',tab='① 从哪冒出来',el=[
 E('s',0.05,'img',src='p18_brain_section.png',h=620,x=X,y=560),E('v',1.3,'fx',name='circle_draw',x=X,y=560,s=1.3,ease=None),E('v',1.9,'fx',name='pop_question',x=X+260,y=300,s=1.0)])
SH[16]=dict(o=[('s',0,'pose_talk_idle','轻快')],f=[],react='—',tab='① 从哪冒出来',el=[
 E('s',0,'img',src='p07_puzzle.png',h=560,x=X,y=560),E('v',0.3,'card',text='资料多 → 又准又顺',size=46,bg=GR,x=X,y=180),E('v',0.9,'fx',name='check_draw',x=X+250,y=330,s=1.2,ease=None)])
SH[17]=dict(o=[('s',0,'pose_deadpan','略讽刺')],f=[],react='—',tab='① 从哪冒出来',el=[
 E('s',0,'img',src='p07_puzzle.png',h=560,x=X,y=560,anim='none'),E('v',0.2,'card',text='资料空着 → 照样接',size=46,bg=R,fg=WH,x=X,y=180),
 E('v',1.0,'card',text='听起来很像',size=50,bg=Y,x=X,y=560,anim='slide_r',rot=4),E('v',2.4,'fx',name='wavy_underline',x=X,y=640,s=1.4,ease=None)])
SH[18]=dict(o=[('s',0,'pose_talk_point','平叙')],f=[],react='—',tab='① 从哪冒出来',el=[
 E('s',0,'img',src='p02b_local_map.png',h=600,x=X,y=600,anim='none')]+
 sum([[E('v',0.4+i*0.45,'card',text=w,size=44,x=X-300+i*300,y=300,rot=(-1)**i*5),E('v',0.6+i*0.45,'fx',name='slash',x=X-300+i*300,y=300,s=0.9)] for i,w in enumerate(['湖景','网红咖啡','人均 68'])],[])+
 [E('v',2.4,'img',src='p02c_map_pin.png',h=150,x=X,y=600),E('v',2.6,'card',text='拼出来的“新地点”',size=42,bg=Y,x=X,y=760)])
SH[19]=dict(o=[('s',0,'pose_think','看鱼显摆')],f=[('s',0,'fish_f05_akimbo_proud','自鸣得意')],react='O 歪头看，不动嘴',tab='① 从哪冒出来',el=[
 E('v',0.05,'merge',words=['网红咖啡馆','湖景','人均68'],xs=[720,980,1240],y=260,tx=980,ty=520,dt=0.3,fly=0.35),
 E('v',0.9,'img',src='p08_cafe_sign.png',h=480,x=980,y=520),E('v',0.95,'fx',name='sparkle_burst',x=980,y=420,s=1.2)])
SH[20]=dict(o=[('s',0,'pose_deadpan','两拍冷砸')],f=[],react='鱼滑出画',tab='① 从哪冒出来',el=[
 E('s',0,'img',src='p08_cafe_sign.png',h=480,x=X,y=520,anim='none',until=V(0.4),anim_out='fade',fo=0.9),E('v',0.2,'card',text='像，但不在',size=56,bg=R,fg=WH,x=X,y=200,rot=-3),
 E('v',0.6,'fx',name='smoke_puff',x=X,y=520,s=1.6),E('v',0.7,'img',src='p09b_reservoir_dry.png',h=640,x=X,y=560,anim='fade',fd=0.9),
 E('v',1.4,'src_tag',src='04_xiamen_xmnn.png',crop=[0,0,1280,900],label='厦门网')])
# ---------------- 镜 21–50（新） ----------------
T2='② 为什么硬撑'
SH[21]=dict(o=[('s',0,'pose_think','听鱼吐槽')],f=[('s',0,'fish_f05_akimbo_proud','叉腰吐槽')],react='O 歪头听',tab=T2,el=[
 E('v',0.1,'card',text='不会就说不会？',size=56,bg=Y,x=980,y=330,rot=-3,sfx=[('pop_ui/pop_plop',-10,0)]),E('v',1.3,'fx',name='pop_question',x=1180,y=520,s=1.2)],
 sfx=[('s',0,'whoosh_trans/whoosh_synth',-12)])
SH[22]=dict(o=[('s',0,'pose_talk_point','笃定')],f=[],react='鱼滑出画',tab=T2,el=[
 E('v',0.0,'img',src='p10_exam_paper.png',h=600,x=X,y=580,anim='drop',rot=-4,sfx=[('whoosh_trans/paper_swipe',-8,0.1)]),E('v',0.6,'card',text='考试就是这么教的',size=52,bg=Y,x=X,y=220,sfx=[('pop_ui/pop_click_b',-12,0)])])
SH[23]=dict(o=[('s',0,'pose_think','讲比方'),('v',2.2,'pose_talk_idle','数字清楚')],f=[],react='—',tab=T2,el=[
 E('v',0.2,'img',src='p11_calendar_wheel.png',h=520,x=X,y=580,anim='spin',sfx=[('pop_ui/pop_rollover',-12,0)]),
 E('v',2.2,'card',text='猜：9 月 10 日',size=54,x=X,y=240,sfx=[('tech_digital/pep_blip',-12,0)]),
 E('v',3.6,'card',text='蒙对机会 1/365',size=58,bg=Y,x=X,y=880,sfx=[('ding_success/ding_bell',-12,0)]),
 E('s',0.4,'src_tag',src='05_openai_blog.png',crop=[0,0,1280,900],label='OpenAI 博客')])
SH[24]=dict(o=[('s',0,'pose_stop_hand','重砸')],f=[],react='—',tab=T2,punch=[V(1.0)],el=[
 E('v',0.0,'card',text='说“不知道”',size=56,x=X,y=260),E('v',1.0,'stamp',text='0 分',size=150,x=X,y=580,rot=-8,anim='stamp',sfx=[('impact_punch/slam_a',-6,0)])])
SH[25]=dict(o=[('s',0,'pose_talk_idle','快')],f=[],react='—',tab=T2,el=[
 E('v',0.1,'card',text='AI 考试：只看答对多少',size=50,bg=B,x=X,y=240,sfx=[('pop_ui/pop_synth',-12,0)]),
 E('v',1.0,'card',text='答对  ✓  得分',size=54,bg=GR,x=X-230,y=520),E('v',1.4,'card',text='不知道  =  白卷',size=54,bg=(200,200,205),x=X+230,y=520,sfx=[('pop_ui/pop_synth',-12,0)]),
 E('v',3.0,'fx',name='box_draw',x=X+230,y=520,s=1.3,ease=None)])
SH[26]=dict(o=[('s',0,'pose_peace','生活化，轻笑')],f=[],react='—',tab=T2,el=[
 E('v',0.0,'card',text='不会也要蒙',size=54,bg=Y,x=X,y=220)]+
 [E('v',0.4+i*0.18,'card',text=c,size=72,x=X-330+i*220,y=540,sfx=[('pop_ui/pop_click_a',-14,0)]) for i,c in enumerate('ABCD')]+
 [E('v',1.4,'fx',name='check_draw',x=X-110,y=540,s=1.0,ease=None),E('v',1.9,'card',text='空着 = 一定没分',size=46,bg=(200,200,205),x=X,y=820)])
SH[27]=dict(o=[('s',0,'pose_talk_point','轻讽刺')],f=[('s',0,'fish_f06_gradcap_proud','戴学士帽得意（不说话）')],react='鱼戴学士帽挺胸，闭嘴',tab=T2,el=[
 E('v',0.2,'img',src='p10_exam_paper.png',h=560,x=980,y=560,rot=5),E('v',0.3,'card',text='特别会考试',size=52,bg=Y,x=980,y=230,sfx=[('ding_success/ding_coin',-12,0)]),
 E('v',2.4,'card',text='没把握，也照样写满',size=50,bg=R,fg=WH,x=980,y=860,sfx=[('pop_ui/pop_plop',-12,0)]),E('v',2.4,'fx',name='sparkle_burst',x=980,y=560,s=1.2)])
SH[28]=dict(o=[('s',0,'pose_deadpan','看鱼，忍笑')],f=[('s',0,'fish_f07_gradcap_off_blank','摘帽发呆')],react='O 平静看鱼，不动嘴',tab=T2,el=[
 E('v',0.2,'fx',name='sweat_drop',x=600,y=250,s=1.2,sfx=[('comedy_fail/weird_wobble',-14,0)]),E('v',0.9,'card',text='被考成这样？',size=54,x=1000,y=330,rot=4)])
SH[29]=dict(o=[('s',0,'pose_talk_point','收束，句尾下沉')],f=[],react='鱼滑出画',tab=T2,el=[
 E('v',0.1,'card',text='OpenAI 建议',size=44,bg=B,x=X,y=180,sfx=[('pop_ui/pop_plop',-12,0)]),
 E('v',1.2,'card',text='答错：扣更多分',size=56,bg=R,fg=WH,x=X,y=380,sfx=[('pop_ui/pop_synth',-12,0)]),
 E('v',2.1,'card',text='说“不知道”：扣得少',size=56,bg=(200,200,205),x=X,y=540,sfx=[('pop_ui/pop_synth',-12,0)]),
 E('v',3.6,'card',text='规矩改了 → 学生才会改',size=56,bg=GR,x=X,y=740,sfx=[('ding_success/ding_bell',-12,0)]),
 E('s',0.4,'src_tag',src='05_openai_blog.png',crop=[0,0,1280,900],label='OpenAI 博客')])
SH[30]=dict(o=[('s',0,'pose_talk_idle','缓冲，眨眼')],f=[],react='—',tab='③ 实测',el=[
 E('s',0.1,'big',text='③ 我们实测了一下',size=96,col=Y,x=X,y=520,sfx=[('whoosh_trans/whoosh_synth',-12,0)])])
SH[31]=dict(o=[('s',0,'pose_think','看鱼')],f=[('s',0,'fish_f08_phone_raise','举手机'),('s',0.8,'fish_f09_point_self','指自己心虚')],react='O 歪头看',tab='③ 实测',el=[
 E('v',0.6,'card',text='我也会编吗？',size=56,bg=Y,x=1000,y=330,rot=-3,sfx=[('pop_ui/pop_plop',-10,0)])],sfx=[('s',0,'whoosh_trans/whoosh_synth',-12)])
MODELS=['DeepSeek-Flash','GLM-5.3-Flash','Kimi-K2.8-Preview','MiniMax-M3.1-Flash','Qwen3.8-Flash']
POS=[(330,345),(820,345),(1310,345),(575,730),(1065,730)]
def keyl(m):
    L=[x.strip() for x in open(RT+f'ans_b_{m}.md').read().replace('**','').replace('#','').split('\n') if x.strip()]
    return '……\n'+'\n'.join([x for x in L if '索道' in x][:2])+'\n……'
def panes(cps,hl_t,big=None):
    out=[]
    for i,m in enumerate(MODELS):
        x,y=POS[i];out.append(E('s',0.1,'term',title=m,text=keyl(m),w=470,h=380,fs=22,cps=cps,x=x,y=y,anim='fade',fd=1.0,
            hl=[dict(s='索道',t=hl_t)],top=False))
    return out
SH[32]=dict(o=[('s',0,'pose_talk_idle','交代，平稳')],o_layout=dict(scale=0.45,dx=40),f=[],react='O 缩到右下角',tab='③ 实测',stage_zoom=1.0,el=
 panes(70,V(3.0))+[E('s',0.2,'card',text='2026-11-03 实测 · qodercn CLI · 5 个模型 · 未联网 · 原文',size=24,bg=(222,222,230),x=820,y=125,anim='fade'),
 E('v',0.0,'card',text='香山附近吃什么？怎么坐索道？',size=40,bg=Y,x=820,y=60,sfx=[('tech_digital/typewriter_ding_synth',-14,0)])],
 sfx=[('v',0.2+i*0.25,'pop_ui/pop_click_a',-22) for i in range(10)]+[('v',3.0+i*0.15,'pop_ui/pop_click_b',-14) for i in range(5)])
SH[33]=dict(o=[('s',0,'pose_react_surprise','「全」重'),('l2',0,'pose_deadpan','干讽')],o_layout=dict(scale=0.6,dx=20),f=[],react='—',tab='③ 实测',stage_zoom=1.0,el=
 [dict(e,t=('s',0),cps=0,anim='none',anim_out='fade',fo=1.5,until=('l2',-1.03)) for e in panes(0,S(0))]+
 [E('v',0.4+i*0.13,'stamp',text='已停运',size=46,x=POS[i][0],y=POS[i][1]+60,rot=-10,anim='stamp',until=('l2',-1.03),anim_out='fade',fo=1.5,sfx=[('impact_punch/thunk_synth',-12,0)]) for i in range(5)]+
 [E('v',1.2,'browser',src='01d_xiangshan_cableway_bjd_20261016.png',crop=[260,90,1020,700],w=560,title='北京日报客户端（北京晚报）· 2026-10-16',x=1250,y=560,rot=2,until=('l2',-1.03),anim_out='fade',fo=1.5),
  E('l2',-0.79,'stamp',text='2024 年 3 月起停运',size=48,x=1500,y=340,rot=-6,anim='stamp',sfx=[('impact_punch/slam_a',-8,0)]),
  E('l2',-0.1,'term',title='MiniMax-M3.1-Flash · 原文',text=rd(RT+'ans_b_MiniMax-M3.1-Flash.md'),w=900,h=560,fs=22,cps=0,scroll=False,x=640,y=540,anim='fade',fd=1.5,hl=[dict(s='双清别墅（香山公园·静宜园内）',t=('l2',0.6)),dict(s='人均 ¥120–200',t=('l2',2.6),col=(255,120,100))]),
  E('l2',2.9,'stamp',text='旧居 ≠ 餐厅',size=70,x=1300,y=420,rot=-8,anim='stamp',sfx=[('impact_punch/slam_a',-8,0)]),
  E('l2',3.1,'card',text='双清别墅：毛主席旧居，参观点',size=36,bg=Y,x=1300,y=600)],
 punch=[])
SH[34]=dict(o=[('s',0,'pose_deadpan','看鱼')],o_layout={},f=[('s',0,'fish_f10_guilty_oldmap','抱旧地图心虚')],react='O 冷眼',tab='③ 实测',el=[
 E('v',0.2,'img',src='p17_old_map_book.png',h=420,x=1000,y=560,rot=-6),E('v',0.5,'fx',name='sweat_drop',x=600,y=250,s=1.2,sfx=[('comedy_fail/weird_wobble',-14,0)]),
 E('v',1.0,'card',text='老黄历',size=54,bg=(230,200,140),x=1000,y=300,rot=4)])
SH[35]=dict(o=[('s',0,'pose_stop_hand','「可」转折')],f=[],react='鱼滑出画',tab='③ 实测',el=[
 E('v',0.0,'card',text='换个小地方：福建屏南 · 双溪镇',size=46,bg=Y,x=X,y=200,sfx=[('whoosh_trans/whoosh_synth',-12,0)]),
 E('s',0,'term',title='第 1 次问',text='双溪镇一日游怎么安排？',w=520,h=420,fs=20,x=X-290,y=580,anim='fade',fd=0.45,nosnap=1),E('s',0,'term',title='第 2 次问',text='双溪镇一日游怎么安排？',w=520,h=420,fs=20,x=X+290,y=580,anim='fade',nosnap=1,fd=0.45),
 E('v',1.6,'card',text='不编店名了，细节照样露馅',size=44,bg=R,fg=WH,x=X,y=880,sfx=[('pop_ui/pop_plop',-12,0)])])
Q1=rd(EPD+'/test/answer_qwen.md');Q2=rd(EPD+'/test/answer_qwen2.md')
i1=Q1.index('白水洋景区');i2=Q2.index('上午 · 白水洋')
SH[36]=dict(o=[('s',0,'pose_talk_point','左右指，对比')],f=[],react='—',tab='③ 实测',stage_zoom=1.0,el=[
 E('s',0,'term',title='Qwen · 第 1 次（原文）',text=Q1[i1:i1+190],w=760,h=520,fs=24,scroll=False,x=470,y=520,anim='fade',fd=0.45,nosnap=1,hl=[dict(s='是否算双溪镇境内我不确定',t=V(1.2))]),
 E('s',0,'term',title='Qwen · 第 2 次（原文）',text=Q2[i2:i2+120],w=760,h=520,fs=24,scroll=False,x=1290,y=520,anim='fade',fd=0.45,nosnap=1,hl=[dict(s='双溪镇境内',t=V(3.4),col=(255,120,100))]),
 E('v',3.5,'fx',name='spark_spray',x=880,y=420,s=1.2,sfx=[('tech_digital/zap',-10,0)]),E('v',3.7,'card',text='前后矛盾',size=50,bg=R,fg=WH,x=880,y=900)])
OSM=EPD+'/rec/r9/'
_p=open(OSM+'osm_pts.txt').read().split();PTS=[float(v) for v in _p[:4]]
SH[37]=dict(o=[('s',0,'pose_deadpan','前平后重砸')],o_layout=dict(scale=0.8),f=[],react='—',tab='③ 实测',stage_zoom=1.0,punch=[V(2.6)],el=[
 E('s',0,'term',title='Qwen · 第 2 次（原文）',text='万安桥（长桥村，离镇上约 10 分钟车程）',w=760,h=130,fs=26,x=700,y=230,anim='fade',fd=0.45,nosnap=1,hl=[dict(s='约 10 分钟车程',t=V(0.6))]),
 E('v',1.4,'ruler_map',map=OSM+'osm_map.png',pts=PTS,w=700,a='双溪镇',b='万安桥',label='直线约 29 公里',t_draw=V(1.7),dur=0.9,x=640,y=620,anim='pop',sfx=[('whoosh_trans/rise_highup',-14,0.3)]),
 E('v',2.6,'fx',name='impact_star',x=1000,y=600,s=1.0,sfx=[('impact_punch/thunk_synth',-6,0)])])
SH[38]=dict(o=[('s',0,'pose_talk_idle','调侃')],f=[('s',0,'fish_f11_slip_fall','从标尺滑倒（不说话）')],react='鱼滑倒，闭嘴',tab='③ 实测',el=[
 E('s',0,'img',src='p19_ruler_km.png',w=700,x=1000,y=420,rot=-12),E('v',0.1,'fx',name='impact_star',x=520,y=720,s=1.0,sfx=[('comedy_fail/boing_spring',-10,0)]),
 E('v',1.0,'card',text='距离、时间：照样瞎估',size=50,bg=R,fg=WH,x=1000,y=820)],counter=[('v',0.0,2)],sfx=[('v',0.0,'tech_digital/pep_blip',-10)])
SH[39]=dict(o=[('s',0,'pose_talk_idle','缓冲')],f=[],react='—',tab='④ 赔钱？',el=[E('s',0.1,'big',text='④ AI 说“我赔你”',size=96,col=Y,x=X,y=520,sfx=[('whoosh_trans/whoosh_synth',-12,0)])])
SH[40]=dict(o=[('s',0,'pose_think','看鱼夸张')],f=[('s',0,'fish_f12_cheque_wave','挥支票')],react='O 歪头看',tab='④ 赔钱？',el=[
 E('v',0.2,'img',src='p14_cheque.png',w=560,x=1000,y=480,rot=-6,sway=1.0,sfx=[('ding_success/ding_coin2',-10,0)]),E('v',1.2,'big',text='赔十万！',size=110,col=Y,x=1000,y=760,rot=-4)])
SH[41]=dict(o=[('s',0,'pose_deadpan','冷砸')],f=[],react='鱼滑出画',tab='④ 赔钱？',el=[
 E('s',0,'img',src='p14_cheque.png',w=560,x=X,y=520,rot=-6,anim='none'),E('v',0.1,'stamp',text='无效',size=120,x=X,y=520,rot=-10,anim='stamp',sfx=[('impact_punch/slam_a',-6,0)]),
 E('v',0.9,'card',text='还真有人信了',size=50,x=X,y=820)])
SH[42]=dict(o=[('s',0,'pose_talk_idle','讲案')],f=[],react='—',tab='④ 赔钱？',el=[
 E('v',0.2,'card',text='① AI 答错高校校区信息',size=42,x=X,y=300,sfx=[('pop_ui/pop_synth',-12,0)]),
 E('v',2.0,'card',text='② AI：“答错赔你十万”',size=42,bg=Y,x=X,y=480,sfx=[('pop_ui/pop_synth',-12,0)]),
 E('v',3.8,'card',text='③ 用户起诉',size=42,bg=R,fg=WH,x=X,y=660,sfx=[('pop_ui/pop_synth',-12,0)]),
 E('s',0.4,'src_tag',src='08_hangzhou_xinhua.png',crop=[0,0,1280,900],label='新华网')])
SH[43]=dict(o=[('s',0,'pose_stop_hand','宣读')],f=[],react='—',tab='④ 赔钱？',punch=[V(4.2)],el=[
 E('v',0.0,'img',src='p21_judgment.png',h=560,x=X-80,y=580),E('v',0.4,'card',text='AI 的承诺 ≠ 平台的承诺',size=48,bg=Y,x=X,y=200),
 E('v',2.2,'card',text='已提示风险 · 无过错',size=42,x=X,y=780),
 E('v',4.1,'img',src='p13_gavel.png',h=300,x=X+300,y=480,anim='drop',sfx=[('impact_punch/gong',-14,0.15),('impact_punch/thunk_synth',-6,0.15)]),
 E('v',4.2,'stamp',text='驳回',size=110,x=X-80,y=580,rot=-8,anim='stamp')])
SH[44]=dict(o=[('s',0,'pose_phone','真诚、稍慢')],f=[],react='—',tab='④ 赔钱？',el=[
 E('s',0,'img',src='p14_cheque.png',w=520,x=X,y=480,rot=-6,anim='none',until=V(0.8),anim_out='fly_up',sfx=[('whoosh_trans/whoosh_synth',-14,0.8)]),
 E('v',0.4,'card',text='AI 拍胸脯 → 别当真',size=50,bg=Y,x=X,y=260),E('v',2.6,'card',text='最后核对的：你自己',size=60,bg=GR,x=X,y=620,sfx=[('ding_success/ding_bell',-12,0)])])
SH[45]=dict(o=[('s',0,'pose_think','看鱼认怂')],f=[('s',0,'fish_f13_typing_focus','专心打字')],react='O 歪头看',tab='⑤ 你能做什么',el=[
 E('v',0.0,'term',title='大肥鱼 · 回答',text='这条……我不确定，你去地图上查一下。⚠️',w=700,h=150,fs=30,cps=6,x=1000,y=300,anim='pop',sfx=[('pop_ui/pop_click_a',-20,0.3*i) for i in range(10)]+[('ding_success/ding_synth',-12,3.4)])])
SIGN=lambda b,a:E(b,a,'card',text='不知道',size=64,bg=(255,255,255),x=320,y=905,rot=-2,anim='fade',top=True)
SH[46]=dict(o=[('s',0,'pose_peace','暖、带笑'),('l2',0,'pose_talk_point','金句')],f=[('s',0,'fish_f13_typing_focus','被夸害羞'),('l2',0,'fish_f14_sign_idk','举「不知道」牌')],react='O 夸鱼时鱼停手；金句时鱼举牌闭嘴',tab='⑤ 你能做什么',el=[
 E('v',0.2,'fx',name='emoji_ok',x=1000,y=300,s=1.2,sfx=[('ding_success/ding_bell',-10,0)]),
 E('l2',0.6,'card',text='说得再顺 → 也是在接龙',size=54,x=X,y=360,sfx=[('pop_ui/pop_plop',-12,0)]),
 E('l2',3.2,'card',text='敢说“不知道” → 才是真进步',size=60,bg=Y,x=X,y=560,sfx=[('ding_success/powerup_a',-12,0)]),E('l2',3.3,'fx',name='sparkle_burst',x=X,y=560,s=1.4)])
SH[47]=dict(o=[('s',0,'pose_peace','看鱼笑')],f=[('s',0,'fish_f14_sign_idk','举牌跳一下',)],fish_jump=True,react='O 比耶',tab='⑤ 你能做什么',el=[
 E('v',0.0,'card',text='技能 +1：会说“不知道”',size=54,bg=GR,x=1000,y=330,rot=-3,sfx=[('tech_digital/pep_blip',-10,0),('ding_success/ding_gem',-12,0.2)]),E('v',0.1,'fx',name='confetti',x=1000,y=300,s=1.2)])
SH[48]=dict(o=[('s',0,'pose_phone','对观众说')],f=[],react='—',tab='⑤ 你能做什么',el=[
 E('v',0.0,'phone',map=OSM+'osm_map.png',seq=[dict(q='双溪古镇',ok=True,t=V(0.8)),dict(q='白水湾网红咖啡馆',ok=False,t=V(2.4))],x=X-120,y=540,anim='slide_up',sfx=[('pop_ui/pop_click_a',-18,0.8+0.12*i) for i in range(4)]+[('ding_success/ding_synth',-12,1.6),('comedy_fail/fail_wah_down',-14,3.9)]),
 E('v',0.4,'card',text='每个地名，都搜一遍',size=46,bg=Y,x=X+330,y=260),E('v',3.9,'card',text='搜不到，先当它是编的',size=46,bg=R,fg=WH,x=1100,y=540)])
SH[49]=dict(o=[('s',0,'pose_peace','挥手')],f=[('s',0,'fish_f04_shrug','探头问观众')],react='O 挥手',tab=None,el=[
 E('v',0.1,'card',text='查证三步',size=40,bg=(64,64,80),fg=WH,x=980,y=420),
 E('v',0.3,'card',text='① 让它给出处',size=46,bg=Y,x=980,y=530,sfx=[('pop_ui/pop_plop',-10,0)]),
 E('v',1.1,'card',text='② 自己点开查',size=46,bg=GR,x=980,y=650,sfx=[('pop_ui/pop_plop',-10,0)]),
 E('v',1.9,'card',text='③ 地名去地图搜',size=46,bg=B,x=980,y=770,sfx=[('pop_ui/pop_plop',-10,0)])])
SH[50]=dict(o=[('s',0,'pose_peace','片尾')],f=[('s',0,'fish_f04_shrug','片尾')],react='双人片尾定格',tab=None,el=[
 E('s',0.1,'big',text='AI 扫盲 · 第 1 期',size=90,col=Y,x=980,y=420),E('s',0.5,'card',text='说得再顺，也要查一查',size=46,x=980,y=620,sfx=[('ding_success/ding_bell',-12,0)])])
COUNTER=[('v',3,1.6,1),('v',38,0.0,2)]
SFX120=json.load(open(EPD+'/script_v3/sfx_1_20.json'))
for k,v in SFX120.items():SH[int(k)].setdefault('sfx',[]).extend([(b,x,p,g) for b,x,p,g in v])

for _n in (2,21,32,34,35,36,37,38):SH[_n]['xf']=0.45
SH[3]['xf']=0.0
SH[35]['xf']=0.0;SH[35].pop('xf_seq',None)   # v4：两处叠化改硬切（wtest 验证）
for _n in (34,36,37):SH[_n]['xf']=0.9
SH[33]['xf']=0.0
SH[7]['xf']=0.6;SH[35]['xf']=0.9;SH[36]['xf_seq']=1;SH[35]['xf_seq']=1;SH[37]['xf_seq']=1;SH[37]['xf']=1.6
# ---------------- 网感层（每个点都写进 shots_v3.json global.net，并逐条进「网感/卡点清单」） ----------------
# at: ('w',句号,'字') = 该句该字的发音起点；('s'/'v'/'l2',x) 同上。snap: 吸附拍点的最大位移（字锁定的点给小值，免得伤句意）
# kinds: shake(amp,dur) 震屏 / freeze(dur) 定格（只放在无人声的空隙）/ duck(pre) 梗前 BGM 收音再爆 / push 微推镜
#        sfx[(文件,dB,dt)] / sticker(text,bg,x,y,rot) 表情包贴纸 / accent(词) 重音字幕放大弹跳
STK=lambda text,bg,x,y,rot=-8:dict(text=text,bg=bg,x=x,y=y,rot=rot)
NET=[
 dict(shot=1,at=('w',1,'存'),snap=0.2,desc='开场爆点「不存在」',kinds=dict(accent='不存在',shake=(14,0.25),sfx=[('impact_punch/hit_a',-10,0)])),
 dict(shot=5,at=('v',3.0),snap=0.26,desc='「37 分钟」数字滚完',kinds=dict(accent='37',shake=(12,0.25),sticker=STK('迟到 29 分钟',(255,120,100),X+330,560,8))),
 dict(shot=9,at=('v',1.0),snap=0.26,desc='术语「幻觉」大字卡',kinds=dict(duck=0.3,accent='幻觉',push=True)),
 dict(shot=24,at=('v',1.0),snap=0.26,desc='「0 分」盖章',kinds=dict(duck=0.3,shake=(18,0.3),accent='0 分')),
 dict(shot=33,at=('v',0.4),snap=0.2,desc='5 个全让坐索道',kinds=dict(accent='全',sfx=[('pop_ui/pop_switch_hard',-10,0)])),
 dict(shot=33,at=('v',1.6),snap=0.26,desc='「2024 年起停运」盖章（翻车 1）',kinds=dict(shake=(16,0.3),sticker=STK('翻车现场',(255,214,64),1300,200,-6),sfx=[('comedy_fail/fail_wah_down',-12,0.1)])),
 dict(shot=33,at=('l2',2.9),snap=0.26,desc='「旧居 ≠ 餐厅」',kinds=dict(duck=0.3,push=True)),
 dict(shot=39,at=('s',0.0),snap=0.0,desc='翻车 2 之后定格 1 拍（0.51s）再进第④段',kinds=dict(freeze=0.51,sfx=[('comedy_fail/record_scratch_synth',-10,0)])),
 dict(shot=37,at=('v',2.6),snap=0.26,desc='「直线约 29 公里」量完（翻车 2）',kinds=dict(duck=0.3,shake=(16,0.3),accent='29')),
 dict(shot=38,at=('v',0.0),snap=0.26,desc='翻车加一：计数器翻牌 + 弹簧',kinds=dict(accent='+1',sfx=[('comedy_fail/boing_spring',-10,0)],sticker=STK('又翻了',(255,120,100),1150,300,6))),
 dict(shot=40,at=('w',42,'十'),snap=0.12,desc='「赔十万」甩支票',kinds=dict(accent='十万',sfx=[('ding_success/ding_coin2',-8,0),('ding_success/ding_coin',-12,0.12)])),
 dict(shot=41,at=('v',0.1),snap=0.26,desc='「无效」盖章',kinds=dict(duck=0.3,shake=(14,0.25))),
 dict(shot=43,at=('v',4.2),snap=0.26,desc='法院「驳回」落槌',kinds=dict(duck=0.3,shake=(18,0.3),accent='驳回')),
 dict(shot=45,at=('v',0.0),snap=0.26,desc='鱼打字：老年机按键音',kinds=dict(sfx=[('tech_digital/beep_synth',-20,0.3*i) for i in range(8)])),
 dict(shot=46,at=('l2',3.2),snap=0.26,desc='金句「敢说不知道」',kinds=dict(duck=0.3,push=True,accent='不知道')),
 dict(shot=47,at=('v',0.0),snap=0.26,desc='技能加一',kinds=dict(accent='+1',sticker=STK('学会了',(120,220,140),1300,560,-6))),
 dict(shot=48,at=('v',3.9),snap=0.26,desc='「搜不到 = 编的」',kinds=dict(shake=(10,0.2),accent='编的')),
]
# v4 闪白修正：镜32 终端窗随 O 缩小同时淡入；镜48 手机随切镜立即上滑；镜34 旧地图随切镜出现
for _e in SH[32]['el']:
    if _e['k']=='term':_e['t']=('s',0.0);_e['nosnap']=1
for _e in SH[48]['el']:
    if _e['k']=='phone':_e['t']=('s',0.0);_e['nosnap']=1
for _e in SH[34]['el']:
    if _e['k']=='img':_e['t']=('s',0.0);_e['nosnap']=1
for _e in SH[33]['el']:
    if _e['k']=='browser':_e['fo']=0.5
SH[33]['el'].append(E('l2',-1.29,'card',text='2024 年 3 月起暂停运营（香山公园通告 2024-03-13）',size=30,bg=WH,x=1180,y=240,rot=0,anim='fade',fd=0.3,nosnap=1))
for _e in SH[33]['el']:
    if _e.get('until')==('l2',-1.03):_e['until']=('l2',-1.29)
