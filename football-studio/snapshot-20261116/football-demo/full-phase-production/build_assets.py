from pathlib import Path
import json,csv,math,html
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).parent;A=R/'assets';FONT='/workspace/football-demo/manutd-tactics/src/fonts/NotoSansSC-700.ttf'
club='https://www.arsenal.com/news/arsenal-3-1-leicester-how-it-happened-a2WhY2x57PnL';lineup='https://www.skysports.com/football/arsenal-vs-leicester-city/teams/390837';article='https://www.independent.co.uk/sport/football/premier-league/arsenal-news-mesut-ozil-goal-assist-vs-leicester-watch-video-highlights-unai-emery-tactics-a8596881.html'
players=[('A19',19,'莱诺','门将起点','83.2–84.6','官方赛报/阵容+连续出球', 'A'),('A16',16,'霍尔丁','门将之后的后场接点','84.2–85.8','Independent直接描述传递次序；连续实帧','A'),('A34',34,'扎卡','左侧接球后带进内侧','86.2–89.6','86.6背号34、88.6带球连续；61分钟后移左后卫','A'),('A11',11,'托雷拉','前内侧接应并向中圈输送','88.6–91.0','90.2背号11+报道传递次序','A'),('A10',10,'厄齐尔','中场中转及后段前插','91.6–92.2 / 97.6–101.8','连续实帧+报道；98.4背号10清楚','A'),('A29',29,'贡多齐','另一侧中转向右路出球','92.2–95.0','独立报道明确接球者；阵容61分钟替补入场','A'),('A2',2,'贝莱林','右侧推进与回传','94.8–98.8','连续镜头+官方及独立报道','A'),('A17',17,'伊沃比','中路/内侧向前接应语境','91.6–98.4','中场17号连续镜头；附近3号可见','A'),('A9',9,'拉卡泽特','接来球并回做给前插者','98.4–101.2','背号9+官方战报明确dummy/return sequence','A'),('A14',14,'奥巴梅扬','门前另一侧已到位的终结接应','100.04–103.6','终结背号14、官方报道','A'),('A20',20,'穆斯塔菲','未参与本稿核心传递的后场语境','83.2–89.6','阵容确定在场；不凭模糊远端单帧给精确跟踪','B_仅人员清单，不上核心板'),('L14',14,'里卡多·佩雷拉','从边线逼近34，之后回追；最后在A14身后','86.6–90.2 / 100.8–102.2','88.6背号14清楚，与末端14连续回追及在场名单对应','A'),('L10',10,'麦迪逊','托雷拉拿球时的前方接近者','89.4–91.0','90.2近身蓝衣背号10+阵容；脚本不扩展其意图','A-'),('L24',24,'门迪','贡多齐附近、右侧回追语境','93.0–98.4','93.6背号24及连续位置；不误作奇尔韦尔盯贝莱林','A'),('L25',25,'恩迪迪','厄齐尔附近的中路回追','90.2–100.8','90.2/97.6背号25清楚','A'),('L3',3,'奇尔韦尔','伊沃比附近回撤','93.4–100.8','97.6背号3清楚','A'),('L6',6,'埃文斯','较深蓝衣、伊沃比前侧语境','93.6–101.0','97.6背号6，阵容对应；不说被9号吸走','A'),('L15',15,'马奎尔','10号身前到身后相对关系','97.6–101.2','98.4背号15；99.2–100.8连续同一人','A'),('L18',18,'阿马泰','9号/球门前的另一名蓝衣语境','97.6–102.2','97.6及100.8背号18','A'),('L1',1,'舒梅切尔','门前向持球一侧出击','100.04–102.2','对方门将+名单；不是读心/被吸引','A'),('F1',None,'最近的第一线蓝衣','后场第一线靠向球侧','83.2–86.6','号码模糊：可能对应11号，但未确认，不用于旁白定名','UNCONFIRMED'),('F2',None,'另一名较前蓝衣','门将与持球侧之间的前压语境','83.2–86.6','报道提瓦尔迪施压，但不把该文一句强映射某一模糊帧','UNCONFIRMED')]
with (R/'script/PLAYER_MAP.csv').open('w',newline='',encoding='utf-8-sig') as f:w=csv.writer(f);w.writerow(['team_qualified_id','shirt_number','identity','visible_role_only','source_times_s','evidence','confidence']);w.writerows(players)
(R/'script/IDENTITY_EVIDENCE.json').write_text(json.dumps({'sources':[club,lineup,article],'phase_clock':'约65:01–65:21，不能拿首发名单直接代替当时场上人员','important_substitution_check':['A14/A29已于61分钟上场，A12利希施泰纳与A7姆希塔良不应出现在本阶段核心板','莱斯特8号伊希纳乔61分钟已被11号奥尔布赖顿换下，不把模糊第一线蓝衣随手叫8号'],'named_players':[dict(zip(['id','number','identity','role','source_s','evidence','confidence'],p)) for p in players]},ensure_ascii=False,indent=2))
# Coordinates are relative relationship sketches, NOT measured pitch positions or tracking.
def node(k,u,v):return {'id':k,'uv':[u,v]}
boards=[
{'id':'B1','title':'后场：相邻接应点','source_frames':[83.2,84.6,86.6],'view':{'xmin_m':30,'ymin_m':17,'scale_px_per_m':8.2},'nodes':[node('A19',94,50),node('A16',83,77),node('A34',72,94),node('A11',67,58),node('F1',78,74),node('F2',88,40),node('L14',65,93)],'passes':[['A19','A16'],['A16','A34']],'runs':[],'defense':[['F1',[80,70],[77,76]]],'cue_order':['19控球','16接应','第一线蓝衣靠向球侧','34边线接应','19→16→34球路']},
{'id':'B2','title':'内切后，下一站仍有防守','source_frames':[86.6,88.6,90.2],'view':{'xmin_m':30,'ymin_m':20,'scale_px_per_m':9.0},'nodes':[node('A34',66,76),node('A11',59,55),node('L14',72,85),node('L10',53,57)],'passes':[['A34','A11']],'runs':[['A34',[72,94],[66,76]]],'defense':[['L14',[65,93],[72,85]],['L10',[49,66],[53,57]]],'cue_order':['34与对方14旧位置','34由边线带内侧','对方14变追赶','11前内侧接应','新接近者10，不同防守人']},
{'id':'B3','title':'中转：把球接到外线','source_frames':[90.6,91.6,93.6,95.2],'view':{'xmin_m':2,'ymin_m':-2,'scale_px_per_m':8.7},'nodes':[node('A11',61,62),node('A10',49,52),node('A29',55,25),node('A2',42,4),node('A17',40,29),node('L24',49,31),node('L25',52,70),node('L6',39,44)],'passes':[['A11','A10'],['A10','A29'],['A29','A2']],'runs':[['A10',[49,52],[39,52]],['A17',[40,29],[32,29]]],'defense':[['L24',[49,31],[43,24]],['L25',[52,70],[43,63]]],'cue_order':['11→10','10→29','29→2','中间中转/外侧前送','两名内侧接应者继续跟进']},
{'id':'B4','title':'外侧推进，内侧跟进','source_frames':[95.2,97.6,98.4],'view':{'xmin_m':-7,'ymin_m':-1,'scale_px_per_m':12.1},'nodes':[node('A2',23,8),node('A17',18,28),node('A10',25,54),node('L3',24,29),node('L24',29,15),node('L25',32,61),node('L15',17,54),node('L6',14,39)],'passes':[],'runs':[['A2',[34,8],[23,8]],['A17',[30,28],[18,28]],['A10',[39,54],[25,54]]],'defense':[['L3',[34,29],[24,29]],['L24',[42,15],[29,15]],['L25',[45,61],[32,61]]],'cue_order':['2外侧持球','17/10内侧','3在17附近回撤','25在10附近回撤','24在2一侧追赶；不把3误标成24']},
{'id':'B5','title':'回做：接原位，还是接前插','source_frames':[98.4,99.2,100.8],'view':{'xmin_m':-4,'ymin_m':5,'scale_px_per_m':9.4},'nodes':[node('A2',24,10),node('A10',23,56),node('A9',20,83),node('L15',18,56),node('L25',29,60),node('L18',15,83)],'passes':[['A2','A10','A9'],['A9','A10_next']],'extra_points':{'A10_next':[10,42]},'runs':[['A10',[23,56],[10,42]]],'defense':[['L15',[18,56],[15,45]]],'cue_order':['10→15→9定位','来球路线必须通过10原位','球越过原位后10再进禁区','9回做至新点','同一15从身前到身后']},
{'id':'B6','title':'门前：另一侧的接应','source_frames':[100.52,100.8,101.24,102.2],'view':{'xmin_m':-5,'ymin_m':20,'scale_px_per_m':14.2},'nodes':[node('A10',8,40),node('A14',4,64),node('A9',17,57),node('L1',5,45),node('L14',10,73),node('L18',8,54),node('L15',13,42)],'passes':[['A10','A14']],'runs':[],'defense':[['L1',[1.5,50],[5,45]],['L14',[14,81],[10,73]]],'cue_order':['10控球与1出击','A14已在另一侧，不追溯画外跑动','L14回追','最后横传连接两个门前点']}]
model={'coordinate_system':'u0–100攻击向左、v0–100远侧到近侧；手工关系示意，不是测绘米数。渲染球场用105×68的正俯视等比几何，玩家相对位置待逐帧覆核，不宣称精确跟踪。','pitch_projection':'orthographic; no rotation/shear; uniform scale in x/y','boards':boards};(A/'BOARD_RELATIONS.json').write_text(json.dumps(model,ensure_ascii=False,indent=2))
# Self-contained staged SVG geometry, plus a contact-sheet preview made with same coordinate mapping.
C={'bg':'#0b151b','pitch':'#6c7a79','att':'#c0dd3d','def':'#f16a53','ball':'#f1db46','run':'#b9e858','text':'#f2f3e9'}
previews=[]
for b in boards:
 v=b['view'];sc=v['scale_px_per_m'];X=lambda u:42+(u*1.05-v['xmin_m'])*sc;Y=lambda z:80+(z*.68-v['ymin_m'])*sc
 im=Image.new('RGB',(2560,1440),C['bg']);d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype(FONT,n*2)
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720"><defs><clipPath id="local"><rect x="38" y="70" width="942" height="540"/></clipPath><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#f1db46"/></marker></defs><rect width="1280" height="720" fill="#0b151b"/>']
 def line(ps,color,width=1.2,dash=None):
  pts=[(X(u),Y(vv)) for u,vv in ps];d.line([(round(x*2),round(y*2)) for x,y in pts],fill=color,width=max(1,round(width*2)));pa=' '.join(f'{x:.2f},{y:.2f}' for x,y in pts);svg.append(f'<polyline points="{pa}" fill="none" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
  if dash and len(pts)>1:
   aa,bb=pts[-2:];ang=math.atan2(bb[1]-aa[1],bb[0]-aa[0]);head=[bb,(bb[0]-8*math.cos(ang-.43),bb[1]-8*math.sin(ang-.43)),(bb[0]-8*math.cos(ang+.43),bb[1]-8*math.sin(ang+.43))];d.polygon([(round(x*2),round(y*2)) for x,y in head],fill=color);svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in head)+f'" fill="{color}"/>')
 def label(x,y,s,size=23,col=C['text']):d.text((x*2,y*2),s,font=font(size),fill=col);svg.append(f'<text x="{x}" y="{y+size}" font-family="Noto Sans SC,sans-serif" font-size="{size}" font-weight="600" fill="{col}">{html.escape(s)}</text>')
 svg.append('<g id="phase_context" clip-path="url(#local)">')
 for ps in [[(0,0),(100,0),(100,100),(0,100),(0,0)],[(50,0),(50,100)],[(0,20.35),(15.714,20.35),(15.714,79.65),(0,79.65)],[(0,36.53),(5.238,36.53),(5.238,63.47),(0,63.47)],[(100,20.35),(84.286,20.35),(84.286,79.65),(100,79.65)],[(100,36.53),(94.762,36.53),(94.762,63.47),(100,63.47)]]:line(ps,C['pitch'],1.05)
 # Metric center circle and goal mouths, same uniform scale as field lines.
 cx,cy=X(50),Y(50);rad=9.15*sc;d.ellipse(((cx-rad)*2,(cy-rad)*2,(cx+rad)*2,(cy+rad)*2),outline=C['pitch'],width=2);svg.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="{C["pitch"]}" stroke-width="1.05"/>')
 for ps in [[(0,44.6),(-2,44.6),(-2,55.4),(0,55.4)],[(100,44.6),(102,44.6),(102,55.4),(100,55.4)]]:line(ps,C['pitch'],1.05)
 # Main field clips are SVG-native; PIL preview is cropped back to local area below.
 coords={n['id']:n['uv'] for n in b['nodes']};coords.update(b.get('extra_points',{}))
 svg.append('</g><g id="phase_ball_routes" clip-path="url(#local)">')
 for ps in b['passes']:
  nodes=[coords[k] for k in ps];line(nodes,C['ball'],2.3,'5 5')
 svg.append('</g><g id="phase_player_runs" clip-path="url(#local)">')
 for k,aa,bb in b['runs']:line([aa,bb],C['run'],2.5,'7 5')
 svg.append('</g><g id="phase_defensive_changes" clip-path="url(#local)">')
 for k,aa,bb in b['defense']:line([aa,bb],C['def'],1.65,'3 5')
 svg.append('</g><g id="phase_people" clip-path="url(#local)">')
 for n in b['nodes']:
  k=n['id'];u,vv=n['uv'];x,y=X(u),Y(vv)
  if not (35<x<980 and 65<y<615):continue
  color=C['att'] if k.startswith('A') else C['def'];r=18 if k.startswith('A') else 16;fill='#24301b' if k.startswith('A') else '#66352e';d.ellipse(((x-r)*2,(y-r)*2,(x+r)*2,(y+r)*2),fill=fill,outline=color,width=4);svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="2"/>');num=k[1:] if k[0] in 'AL' else '·';bbox=d.textbbox((0,0),num,font=font(20));d.text((x*2-(bbox[2]-bbox[0])/2,y*2-24),num,font=font(20),fill=C['text']);svg.append(f'<text x="{x:.2f}" y="{y+7:.2f}" text-anchor="middle" fill="#f2f3e9" font-family="Noto Sans SC,sans-serif" font-size="20" font-weight="700">{num}</text>')
 svg.append('</g>')
 for key,q in b.get('extra_points',{}).items():
  xx,yy=X(q[0]),Y(q[1]);d.ellipse(((xx-25)*2,(yy-25)*2,(xx+25)*2,(yy+25)*2),outline=C['run'],width=3);svg.append(f'<circle cx="{xx}" cy="{yy}" r="25" fill="none" stroke="{C["run"]}" stroke-width="1.5" stroke-dasharray="4 4"/>');label(xx-45,yy-58,'下一接点',23,C['run'])
 # Apply the same local clip to the PIL diagnostic preview, not just SVG.
 local=im.crop((76,140,1960,1220));clean=Image.new('RGB',im.size,C['bg']);clean.paste(local,(76,140));im=clean;d=ImageDraw.Draw(im)
 # Invariant full-pitch minimap with observed role points only; no invented full 22.
 mx,my,mw,mh=1013,80,225,146
 d.rectangle((mx*2,my*2,(mx+mw)*2,(my+mh)*2),outline=C['pitch'],width=2);d.line(((mx+mw/2)*2,my*2,(mx+mw/2)*2,(my+mh)*2),fill=C['pitch'],width=2);svg.append(f'<g id="phase_minimap"><rect x="{mx}" y="{my}" width="{mw}" height="{mh}" fill="none" stroke="#6c7a79" stroke-width="1"/><path d="M{mx+mw/2} {my}V{my+mh}" stroke="#6c7a79"/>')
 for n in b['nodes']:
  k=n['id'];u,vv=n['uv'];x,y=mx+u/100*mw,my+vv/100*mh;cc=C['att'] if k.startswith('A') else C['def'];d.ellipse((x*2-5,y*2-5,x*2+5,y*2+5),fill=cc);svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.5" fill="{cc}"/>')
 ux=max(0,v['xmin_m']/105);vy=max(0,v['ymin_m']/68);uw=min(1,(v['xmin_m']+942/sc)/105)-ux;vh=min(1,(v['ymin_m']+540/sc)/68)-vy
 if uw>0 and vh>0:
  bx,by,bw,bh=mx+ux*mw,my+vy*mh,uw*mw,vh*mh;d.rectangle((bx*2,by*2,(bx+bw)*2,(by+bh)*2),outline=C['att'],width=2);svg.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="none" stroke="{C["att"]}" stroke-width="1"/>')
 svg.append('</g>');label(42,24,b['title'],28);label(1040,34,'← 进攻方向',19);label(1010,240,'总览仅标本段已见对象',17,'#a0adaa');label(42,625,'局部关系示意 · 不补画外站位',18,'#a0adaa');svg.append('</svg>');(A/f"{b['id']}_STAGED.svg").write_text(''.join(svg));im=im.resize((1280,720),Image.Resampling.LANCZOS);im.save(A/f"{b['id']}_preview.png");previews.append(im)
contact=Image.new('RGB',(1920,1080),C['bg'])
for j,im in enumerate(previews):contact.paste(im.resize((640,360)),((j%3)*640,(j//3)*360))
contact.crop((0,0,1920,720)).save(A/'SIX_RELATION_BOARDS_PREVIEW.jpg',quality=96)
(R/'script/VISUAL_SPEC.md').write_text('''# 新片可执行视觉规范（阶段资产，不是已完成动画）

1. 主板正常正俯视、固定向左；不旋斜。球场线按105×68等比绘制；局部平移/等比缩放，右上固定同向总览，只标本阶段已见对象，禁止为了好看补满22人。
2. 1280×720、25fps原生；图形2×超采样。主场区域x38–980/y70–610，小地图x1013/y80/225×146。字幕基准33px NotoSansSC-700，最多两短信息单位，绝不细黄小字堆满屏；节点r16–18/数字20，核心关键词24。角色名只在首次必要位置出现。
3. 我方黄绿描边#c0dd3d，对方珊瑚红#f16a53；球路暖黄#f1db46，跑线更绿#b9e858；防守相对变化红虚线。颜色与队服不相同，开头简短图例明确；A14与L14内部ID永不混用，必要叫名字。
4. 每板先人后路线后下一接点；后面同板是解释回顾态则保留旧点虚影并注明原位，不使球路绕过原位。B5来球必须穿过10号旧点，球经过后人再移动；9号回做是另一条路线。
5. SVG的phase_*组是分层几何，全显态仅供核对，禁止整张直接淡入充当动画。真实Fish关键词落点触发描线0.25–0.55秒为初值；防守尾线只画源中已见的相对变化，绝不推断“被吸引/被骗/故意清路”。
6. 每个关系都回实拍验证，不只一张板讲完全部；源83.2–103.6完整原速最终复看。源82.6仍是上一进球回放，不用。奥巴在前段画外，不画他沿边线跑；看得到的终结站位才讲。
7. 源实拍叠圈仅定格；没有逐帧真实脚点及鞋部遮挡就不动态跟踪，恢复运动先撤。后场第一线未认准名字只称蓝衣，不画臆测号码。新88.6/90.2脚点与鞋mask需正式渲染前实图裁片复核，不因资产有字段就宣称遮罩已完工。
8. SFX使用audio/sfx_original独立原创近似；仅少数强切低顿点，最多一条关键球路弱whoosh，不给每传每圈铺音。已读父SFX_CUES：原片部分切点的低顿点仍可能BGM踩点，不谎称抽到了干净原音效；参考混音片禁止进入成片。
''')
print('IDENTITIES_AND_SIX_STAGED_ASSETS_READY')
