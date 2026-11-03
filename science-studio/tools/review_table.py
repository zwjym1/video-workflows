#!/usr/bin/env python3
"""为任意一期生成审核表：review_table.xlsx + review_table_N.jpg
用法: python3 review_table.py <episode_dir> [--hook "..."] [--risk 关键词1,关键词2] [--rows-per-img 20]
读取 <ep>/shotlist.md 中的分镜表 (| # | 时间 | 章 | 口播 | 主持/版式 | 画面元素 | 大字 | SFX | 梗 | ⚡ |)
以及其中的 Flow 小动画表 (| ID | 镜 | 首帧 | 中文 | ...)；若存在 facts.md，🟡/❌ 行计入"待核事实"。"""
import re,sys,argparse,os
from openpyxl import Workbook
from openpyxl.styles import Alignment,Font,PatternFill,Border,Side
from PIL import Image,ImageDraw,ImageFont
ap=argparse.ArgumentParser();ap.add_argument('ep');ap.add_argument('--hook',default='');ap.add_argument('--risk',default='')
ap.add_argument('--rows-per-img',type=int,default=20);ap.add_argument('--max-cps',type=float,default=7.0)
a=ap.parse_args();ep=a.ep.rstrip('/')
md=open(f'{ep}/shotlist.md').read()
shots=[];gags={}
for l in md.splitlines():
    c=[x.strip() for x in l.strip().split('|')[1:-1]]
    if l.startswith('|') and len(c)>=10 and c[0].isdigit(): shots.append(c[:10])
    elif l.startswith('| G') and len(c)>=4: gags[c[0]]=c[3]
def sec(t):
    m=re.match(r'(\d+):([\d.]+)',t);return int(m[1])*60+float(m[2])
def short(s,n=34):
    s=re.sub(r'\s+',' ',s);return s if len(s)<=n else s[:n-1]+'…'
def nch(s): return len(re.sub(r'[（）()…，。？！、：—“”\s【】]','',s))
risk_kw=[k for k in a.risk.split(',') if k]
unver=[]
if os.path.exists(f'{ep}/facts.md'):
    for l in open(f'{ep}/facts.md'):
        if l.startswith('|') and ('🟡' in l):
            c=[x.strip() for x in l.strip('|\n').split('|')];unver.append(short(c[1],22))
chmap={}
if os.path.exists(f'{ep}/script.md'):
    for l in open(f'{ep}/script.md'):
        m=re.match(r'## 第 (\d+) 章 (.+)',l)
        if m: chmap[m[1]]=f'第{m[1]}章 '+m[2].strip()
        elif l.startswith('## 结尾'): chmap['结尾']='结尾'
EMO=re.compile('[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]')
recmap={}
if os.path.exists(f'{ep}/screen_record_plan.md'):
    for l in open(f'{ep}/screen_record_plan.md'):
        cc=[x.strip() for x in l.strip().split('|')[1:-1]]
        if len(cc)>=3 and re.match(r'R\d',cc[0]) and cc[2] in('A','B'):
            opt='(可选)' in cc[0] or '可选' in cc[0]
            for s in re.findall(r'\d+',cc[1]):
                tag=cc[0].split('（')[0]+':'+cc[2]+('?' if opt else '')
                recmap[int(s)]=(recmap[int(s)]+' '+tag) if int(s) in recmap else tag
rows=[]
for c in shots:
    zp=bool(c[9]);c=[EMO.sub('',x) for x in c]
    i,tm,ch,vo,lay,el,big,sfx,g,pz=c
    t0,t1=[sec(x) for x in tm.split('–')];d=t1-t0
    r=[]
    if any(k in vo for k in risk_kw): r.append('事实待核')
    if nch(vo)/max(d,0.1)>a.max_cps: r.append('语速快')
    pops=len(re.findall(r'\(\d|@|×\d|；',el))
    if d>4 and pops<=1: r.append('无画面变化')
    fx=short(sfx.replace('comedy_fail/','').replace('ding_success/','').replace('impact_punch/','').replace('pop_ui/','').replace('tech_digital/','').replace('whoosh_trans/',''),26)
    if zp: fx='【放大】'+fx
    pic=short(el,30)+(f'｜「{big}」' if big else '')
    rows.append([int(i),f'{t0:.1f}–{t1:.1f}s',chmap.get(ch,ch),short(vo,40),pic,fx,(g+' '+short(gags.get(g,''),18)).strip(),'、'.join(r),recmap.get(int(i),'—'),''])
total=sec(shots[-1][1].split('–')[1]);ng=len({r[6].split()[0] for r in rows if r[6]})
hook=a.hook or rows[0][3]
nrec=sum(1 for r in rows if r[8]!='—')
summary=f'录屏镜 {nrec}（A/B 见「录屏?」）｜总长 {int(total//60)}:{total%60:04.1f}｜镜头 {len(rows)}｜小动画 {ng}｜放大冲击 {sum(1 for r in rows if "【放大】" in r[5])}｜钩子：{hook}｜待核事实：{"；".join(unver) or "无"}'
H=['序号','时间','段落','口播文案','画面/大字','音效·动效','小动画','自检风险','录屏?','过关?']
# xlsx
wb=Workbook();ws=wb.active;ws.title='审核'
ws.append([summary]);ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=10)
ws['A1'].font=Font(bold=True,size=12);ws['A1'].alignment=Alignment(wrap_text=True,vertical='center');ws.row_dimensions[1].height=48
ws.append(H);thin=Side(style='thin',color='BBBBBB')
for j in range(1,11):
    x=ws.cell(2,j);x.font=Font(bold=True,color='FFFFFF');x.fill=PatternFill('solid',fgColor='333344')
cur=None;fills=['F4F6FB','FFFFFF']
for r in rows:
    if r[2]!=cur:
        cur=r[2];ws.append([cur]+['']*9);rr=ws.max_row;ws.merge_cells(start_row=rr,start_column=1,end_row=rr,end_column=10)
        ws.cell(rr,1).font=Font(bold=True,color='7A4A00');ws.cell(rr,1).fill=PatternFill('solid',fgColor='FFE9A8')
    ws.append(r);rr=ws.max_row
    for j in range(1,11):
        x=ws.cell(rr,j);x.alignment=Alignment(wrap_text=True,vertical='top');x.border=Border(top=thin,bottom=thin,left=thin,right=thin)
    if r[7]: ws.cell(rr,8).font=Font(color='C00000',bold=True)
    ws.cell(rr,10).fill=PatternFill('solid',fgColor='E8F7EC')
for j,w in enumerate([6,12,18,42,40,28,24,16,10,10],1): ws.column_dimensions[chr(64+j)].width=w
ws.freeze_panes='A3';wb.save(f'{ep}/review_table.xlsx')
# jpg
FB='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';FR='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
f=ImageFont.truetype(FR,22,index=2);fb=ImageFont.truetype(FB,22,index=2);fs=ImageFont.truetype(FB,24,index=2)
CW=[60,165,175,500,450,300,260,150,110,80];W=sum(CW)+40
def wrap(d,s,w,font):
    out=[];line=''
    for ch in s:
        if d.textlength(line+ch,font=font)>w-14: out.append(line);line=ch
        else: line+=ch
    out.append(line);return out[:2]
items=[];cur=None
for r in rows:
    if r[2]!=cur: cur=r[2];items.append(('sec',cur))
    items.append(('row',r))
pages=[];pg=[];n=0
for it in items:
    pg.append(it);n+=it[0]=='row'
    if n>=a.rows_per_img and it[0]=='row': pages.append(pg);pg=[];n=0
if pg: pages.append(pg)
tmp=Image.new('RGB',(10,10));td=ImageDraw.Draw(tmp)
for pi,pg in enumerate(pages,1):
    hts=[]
    for k,v in pg: hts.append(40 if k=='sec' else 16+30*max(len(wrap(td,str(x),w,f)) for x,w in zip(v,CW)))
    sl=wrap(td,summary,W-40,fs) if pi==1 else [f'（续 {pi}/{len(pages)}）']
    Ht=20+36*len(sl)+20+44+sum(hts)+20
    im=Image.new('RGB',(W,Ht),'white');d=ImageDraw.Draw(im);y=20
    for s in sl: d.text((20,y),s,font=fs,fill=(20,20,30));y+=36
    y+=20;x=20
    for h,w in zip(H,CW): d.rectangle([x,y,x+w,y+44],fill=(51,51,68));d.text((x+7,y+9),h,font=fb,fill='white');x+=w
    y+=44
    for (k,v),h in zip(pg,hts):
        if k=='sec': d.rectangle([20,y,W-20,y+h],fill=(255,233,168));d.text((28,y+6),v,font=fb,fill=(122,74,0))
        else:
            x=20
            for j,(val,w) in enumerate(zip(v,CW)):
                bg=(232,247,236) if j==9 else ((225,238,255) if j==8 and val!='—' else (255,255,255))
                d.rectangle([x,y,x+w,y+h],fill=bg,outline=(190,190,200))
                col=(192,0,0) if j==7 else (30,30,40)
                for li,s in enumerate(wrap(d,str(val),w,f)): d.text((x+7,y+8+li*30),s,font=fb if j==7 else f,fill=col)
                x+=w
        y+=h
    im.save(f'{ep}/review_table_{pi}.jpg',quality=92)
print(summary);print('pages',len(pages))
