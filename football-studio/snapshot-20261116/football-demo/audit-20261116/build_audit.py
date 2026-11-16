from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json,csv,io,math,numpy as np
R=Path(__file__).parent;P=Path('/workspace/football-demo/manutd-tactics')
F=P/'src/fonts/NotoSansSC-700.ttf'
font=ImageFont.truetype(str(F),30);small=ImageFont.truetype(str(F),24)
def frame(path,n):
 b=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf',f'select=eq(n\\,{n}),scale=1280:720','-frames:v','1','-f','image2pipe','-vcodec','png','-'])
 return Image.open(io.BytesIO(b)).convert('RGB')
def im(name,t):return Image.open(R/f'{name}_{t:06.2f}_1280.jpg').convert('RGB')
def pair(filename,left,right,labels,notes,crops=None):
 h=810 if not crops else 1210
 s=Image.new('RGB',(2560,h),(22,24,28));d=ImageDraw.Draw(s)
 for k,a in enumerate([left,right]):
  d.text((k*1280+24,8),labels[k],font=font,fill='white');s.paste(a,(k*1280,54))
  d.text((k*1280+24,778),notes[k],font=small,fill=(240,225,160))
  if crops:
   c=a.crop(crops[k]); c.thumbnail((1240,350)); s.paste(c,((k*1280)+(1280-c.width)//2,842));
 s.save(R/filename,quality=95)
pair('E01_live_same_scale.jpg',im('reference',28),im('sample',28),['参考 28.000s｜1080p统一缩到1280×720','样片 28.000s｜原生1280×720'],['脚底横扁圈；红黄区分角色；传球带与虚线两级','正圆双环；淡金色3px直虚线；角色几乎同色'],[(400,270,780,570),(460,180,820,420)])
pair('E02_board_same_scale.jpg',im('reference',19),im('sample',33),['参考战术板 19.000s｜统一1280×720','样片战术板 33.000s｜统一1280×720'],['局部构图放大关系；红/黄/白/蓝承担不同语义','整场横铺；6个点挤在右端；大块无关空场'])
pair('E03_subtitle_same_scale.jpg',im('reference',37),im('sample',42),['参考字幕 37.000s｜统一1280×720','样片字幕 42.000s｜统一1280×720'],['“穆勒”“距离更近”黄色；句子解释因果','21汉字整句白字；行动描述；统一3px黑描边'],[(180,620,1100,710),(100,620,1180,710)])
# Detail crops at identical 2x magnification, not a comparison of 1080p vs 720p pixels.
s=Image.new('RGB',(2560,600),(22,24,28));d=ImageDraw.Draw(s)
for k,(name,t,box,label) in enumerate([('reference',28,(410,285,910,535),'参考：脚圈/红黄分工/宽带+虚线'),('sample',42,(520,265,1020,515),'样片：正圆叠环/近色细线/直线箭头')]):
 d.text((1280*k+24,12),label,font=font,fill='white');a=im(name,t).crop(box).resize((1000,500));s.paste(a,(1280*k+140,70))
s.save(R/'E04_overlay_detail_2x.jpg',quality=96)
# Visible state progression, not mere detection of pixel motion.
s=Image.new('RGB',(1920,860),(22,24,28));d=ImageDraw.Draw(s)
for j,t in enumerate([16,19,23]):
 s.paste(im('reference',t).resize((640,360)),(640*j,50));d.text((640*j+12,12),f'参考 {t}s：关系/空当/线路分阶段',font=small,fill='white')
for j,t in enumerate([31.5,33,36]):
 s.paste(im('sample',t).resize((640,360)),(640*j,480));d.text((640*j+12,440),f'样片 {t}s：标记已齐，坐标不动',font=small,fill='white')
s.save(R/'E05_board_progression.jpg',quality=95)
# Exact transition frames, one decode for all selections.
ns=[239,240,242,457,458,460,1539,1540,1542]; dest=R/'transition_exact';dest.mkdir(exist_ok=True)
expr='+'.join(f'eq(n\\,{n})' for n in ns)
subprocess.run(['ffmpeg','-v','error','-i',str(P/'out/manutd-tactics-v2-light.mp4'),'-vf',f'select={expr},scale=640:360','-vsync','0','-q:v','2',str(dest/'%03d.jpg')],check=True)
s=Image.new('RGB',(1920,1200),(22,24,28));d=ImageDraw.Draw(s)
for j,n in enumerate(ns):
 x=j%3*640;y=j//3*400;s.paste(Image.open(dest/f'{j+1:03d}.jpg'),(x,y+40));d.text((x+12,y+5),f'样片 F{n} / {n/30:.3f}s',font=small,fill='white')
s.save(R/'E06_repeated_dissolve_flash.jpg',quality=95)
# Native-source vs encoded delivery: both are the very same underlying frame.
source=Image.open(P/'src/clips/wide/0079.jpg').convert('RGB');out=frame(P/'out/manutd-tactics-v2-light.mp4',840);master=frame(P/'out/manutd-tactics-v2.mp4',840)
pair('E07_same_frame_source_vs_delivery.jpg',source,out,['渲染输入JPEG n78｜底片原生720p','交付轻量版 F840 / 28.000s｜720p'],['源中草地/看台本已软；不是把1080p渲染丢成720p','后续编码有损，但正圆/位置/空白是绘图问题'],[(70,400,650,610),(70,400,650,610)])
# Measures restricted to an untouched 270x150 background ROI (x80:350, y450:600).
roi=(slice(450,600),slice(80,350))
def metric(a,b):
 a=np.asarray(a)[roi].astype(float);b=np.asarray(b)[roi].astype(float);mse=np.mean((a-b)**2)
 return {'rgb_mae':float(np.abs(a-b).mean()),'rgb_psnr_db':float(10*math.log10(255**2/mse)) if mse else None}
quality={'roi':'x80:350,y450:600; same original frame n78; no overlaid drawing in ROI','input_jpeg_vs_light':metric(source,out),'master_vs_light':metric(master,out)}
(R/'quality_roi_metrics.json').write_text(json.dumps(quality,indent=2))
print(json.dumps(quality))
