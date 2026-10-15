import math,random
from PIL import Image,ImageDraw,ImageFont,ImageFilter
W,H=1920,1080
BG='#FFF8EC';INK='#2B2D42';BLUE='#3A86FF';ORANGE='#FF8C42';YEL='#FFD23F';TEAL='#2EC4B6';PINK='#FF5D8F';GRID='#EDE4D3';WOOD='#C98B4F'
import os
B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
if not os.path.exists(B): B='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def F(s,b=True): return ImageFont.truetype(B if b else R,s,index=2)
def canvas(bg=BG,grid=True):
  im=Image.new('RGB',(W,H),bg);d=ImageDraw.Draw(im)
  if grid:
    for x in range(0,W,60): d.line([(x,0),(x,H)],fill=GRID,width=2)
    for y in range(0,H,60): d.line([(0,y),(W,y)],fill=GRID,width=2)
  return im,d
def sub(d,text):
  f=F(64);w=d.textlength(text,font=f);x=(W-w)/2;y=920
  d.text((x,y),text,font=f,fill='white',stroke_width=8,stroke_fill=INK)
def chapter(d,t):
  f=F(34);w=d.textlength(t,font=f)
  d.rounded_rectangle([40,36,40+w+48,36+64],radius=32,fill=BLUE);d.text((64,44),t,font=f,fill='white')
def poly(n,cx,cy,r,rot=-math.pi/2): return [(cx+r*math.cos(rot+2*math.pi*i/n),cy+r*math.sin(rot+2*math.pi*i/n)) for i in range(n)]

# 1 opening wheel (to scale: rolled line = pi*D, bars = D, extra = 0.1416*D)
im,d=canvas();chapter(d,'开场')
gy=700;d.rectangle([0,gy,W,H],fill='#CDEAC0');d.line([(0,gy),(W,gy)],fill=INK,width=6)
D=360;r=D/2;x0=300;xe=x0+math.pi*D
# ghost wheel at start
d.ellipse([x0-r,gy-D,x0+r,gy],outline='#B8B8C8',width=6);d.line([(x0,gy-12),(x0,gy+12)],fill=INK,width=4)
d.line([(x0,gy-6),(xe,gy-6)],fill=ORANGE,width=14)
cx=xe;cy=gy-r
d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=INK);d.ellipse([cx-r+28,cy-r+28,cx+r-28,cy+r-28],fill='#8D99AE')
for a_ in range(0,360,45):
  th=math.radians(a_+20);d.line([(cx,cy),(cx+(r-28)*math.cos(th),cy+(r-28)*math.sin(th))],fill=INK,width=8)
d.ellipse([cx-20,cy-20,cx+20,cy+20],fill=YEL)
cols=[BLUE,TEAL,PINK]
for i in range(3):
  d.rounded_rectangle([x0+i*D+3,gy+40,x0+(i+1)*D-3,gy+70],radius=12,fill=cols[i])
  d.text((x0+i*D+D/2-30,gy+80),'直径',font=F(30),fill=INK)
d.rectangle([x0+3*D,gy+40,xe,gy+70],fill=YEL,outline=ORANGE,width=3)
d.text((x0+3*D-150,gy+130),'还多一小截（约0.14个直径）',font=F(34),fill=ORANGE)
d.polygon([(x0+3*D+5,gy+125),(xe-5,gy+125),(x0+3*D+(xe-x0-3*D)/2,gy+78)],fill=ORANGE)
d.text((80,140),'车轮滚一圈，到底走了多远？',font=F(72),fill=INK)
sub(d,'还多出一小截');im.save('style-frames/sf1-opening-wheel.png')

# 2 measuring
im,d=canvas();chapter(d,'第1章 量一量')
items=[('杯盖',180,'3.14',BLUE),('硬币',100,'3.13',ORANGE),('碗口',220,'3.15',TEAL)]
x=330
for name,r,v,c in items:
  cy=470;d.ellipse([x-r,cy-r,x+r,cy+r],outline=c,width=14,fill='white');d.line([(x-r,cy),(x+r,cy)],fill=INK,width=6)
  d.text((x-40,cy+r+20),name,font=F(44),fill=INK)
  d.rounded_rectangle([x-110,cy+r+90,x+110,cy+r+170],radius=20,fill=c);d.text((x-75,cy+r+95),v,font=F(60),fill='white')
  x+= r+ (items[items.index((name,r,v,c))+1][1] if name!='碗口' else 0)+220
d.text((640,110),'周长 ÷ 直径  ≈ 3.1…',font=F(72),fill=PINK)
sub(d,'结果却差不多');im.save('style-frames/sf2-measure.png')

# 3 割圆术
im,d=canvas();chapter(d,'第3章 割圆术')
cx,cy,r=560,520,360
d.ellipse([cx-r,cy-r,cx+r,cy+r],fill='#FFE7C2')
for n,c,w in [(6,BLUE,6),(12,TEAL,6),(24,PINK,7)]:
  d.polygon(poly(n,cx,cy,r),outline=c,width=w)
d.polygon(poly(24,cx,cy,r),fill=None)
d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=INK,width=6)
d.ellipse([cx-10,cy-10,cx+10,cy+10],fill=INK)
rows=[(6,'3.0000'),(12,'3.1058'),(24,'3.1326'),(48,'3.1394'),(96,'3.1410'),(192,'≈3.1415')]
tx,ty=1080,150
d.rounded_rectangle([tx,ty,tx+760,ty+90+6*100],radius=28,fill='white',outline=INK,width=4)
d.text((tx+40,ty+18),'边数',font=F(44),fill=INK);d.text((tx+330,ty+18),'周长 ÷ 直径',font=F(44),fill=INK)
cl=[BLUE,TEAL,PINK,ORANGE,'#8338EC',INK]
for i,(n,v) in enumerate(rows):
  y=ty+100+i*100
  if i<3: d.rounded_rectangle([tx+16,y-6,tx+744,y+82],radius=18,fill='#F3F7FF')
  col=cl[i] if i<3 else '#B8B8C8'
  d.text((tx+50,y),f'{n}',font=F(60),fill=col);d.text((tx+330,y),v,font=F(60),fill=col)
d.text((tx+40,ty+90+6*100+20),'π = 3.14159…  边越多，越接近',font=F(40),fill=PINK)
sub(d,'边越多 越贴着圆');im.save('style-frames/sf3-gekuanshu-table.png')

# 4 祖冲之 算筹桌
im,d=canvas('#F4E3C3',False);chapter(d,'第4章 祖冲之')
d.rounded_rectangle([120,420,1800,1000],radius=40,fill=WOOD)
for i in range(0,1680,90): d.line([(120+i,430),(160+i,990)],fill='#B97A42',width=3)
random.seed(3)
def rods(x,y,k,horiz=False):
  for j in range(k):
    if horiz: d.rounded_rectangle([x,y+j*22,x+90,y+j*22+12],radius=6,fill='#F2D8A7',outline='#7A4E24',width=2)
    else: d.rounded_rectangle([x+j*22,y,x+j*22+12,y+110],radius=6,fill='#F2D8A7',outline='#7A4E24',width=2)
digs='31415926'
x=230
for i,ch in enumerate(digs):
  v=int(ch);horiz=i%2==1
  if v>=6:
    d.rounded_rectangle([x,560 if not horiz else 500,x+(90 if horiz else 100),(572 if not horiz else 600)] if not horiz else [x+40,500,x+52,600],radius=6,fill='#F2D8A7',outline='#7A4E24',width=2)
    rods(x,600 if not horiz else 610,v-5,horiz)
  else: rods(x,580,v,horiz)
  x+=190
d.text((200,140),'3.1415926 < π < 3.1415927',font=F(84),fill=INK)
d.text((200,260),'小数点后 7 位 · 约1500年前',font=F(48),fill=ORANGE)
try:
  p=Image.open('assets/zu-chongzhi-bronze.jpg');p.thumbnail((300,420));
  m=Image.new('L',p.size,0);ImageDraw.Draw(m).rounded_rectangle([0,0,*p.size],radius=30,fill=255)
  im.paste(p,(1560,60),m);d.text((1560,60+p.size[1]+6),'祖冲之（后人塑像）',font=F(26,False),fill=INK)
except Exception as e: print(e)
sub(d,'他用的是算筹');im.save('style-frames/sf4-zuchongzhi-rods.png')

# 5 digit waterfall
im=Image.new('RGB',(W,H),'#1B2A4A');d=ImageDraw.Draw(im);chapter(d,'第5章 计算机时代')
pi='31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679'*3
random.seed(1);fs=F(34,False)
for col in range(0,W,46):
  off=random.randint(0,200);sp=random.randint(10,30)
  for k in range(26):
    y=(k*42+off)%H; a=max(40,255-k*9)
    c=random.choice([TEAL,YEL,'#9BD1FF','#FFFFFF'])
    d.text((col+6,y),pi[(col//46*7+k)%len(pi)],font=fs,fill=c)
ov=Image.new('RGBA',(W,H),(0,0,0,0));od=ImageDraw.Draw(ov);od.rounded_rectangle([360,330,1560,690],radius=40,fill=(27,42,74,235))
im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB');d=ImageDraw.Draw(im)
t='314万亿位小数';f=F(130);w=d.textlength(t,font=f);d.text(((W-w)/2,380),t,font=f,fill=YEL)
t='截至2026年 · 一台计算机连续算了约110天';f=F(40,False);w=d.textlength(t,font=f);d.text(((W-w)/2,580),t,font=f,fill='white')
sub(d,'π还是没写完');im.save('style-frames/sf5-digit-waterfall.png')

# 6 π日
im,d=canvas();chapter(d,'第6章 π日')
d.rounded_rectangle([200,220,760,800],radius=36,fill='white',outline=INK,width=6)
d.rounded_rectangle([200,220,760,360],radius=36,fill=PINK);d.rectangle([200,320,760,360],fill=PINK)
d.text((380,240),'3 月',font=F(80),fill='white');d.text((330,420),'14',font=F(260),fill=INK)
cx,cy=1300,560;d.ellipse([cx-330,cy-200,cx+330,cy+200],fill=WOOD);d.ellipse([cx-290,cy-180,cx+290,cy+150],fill='#E9A23B')
d.text((cx-80,cy-190),'π',font=F(260),fill='white',stroke_width=6,stroke_fill=INK)
d.text((1000,180),'国际数学日',font=F(64),fill=BLUE)
sub(d,'永远写不完的数');im.save('style-frames/sf6-piday.png')
