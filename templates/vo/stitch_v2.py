"""开头 0–15s（卡1–7）新配音拼接 → 接回旧整轨「更离谱的是」 → vo_master_v2.wav + chars_v2/cards_v2.json"""
import json,subprocess,re
import numpy as np, soundfile as sf
SR=48000; han=lambda s: re.findall(r'[\u4e00-\u9fff]',s)
# 选版 + 处理参数：take, atempo, 小句增益(dB, 相对), 加重字(+dB)
PICK=[('s1',0,1.07,-3.0,{}),           # 耳语
      ('s2',0,1.00, 0.0,{'瞬':3,'间':3}),
      ('s3',2,1.15, 0.5,{}),
      ('s4',0,1.00, 1.5,{}),
      ('s5',2,1.00, 2.5,{}),
      ('s6',1,1.08, 1.0,{'诺':3.5,'贝':3.5,'尔':3.5})]
LEAD=0.30; GAPS=[0.25,0.30,0.22,0.40,0.18]; TAIL_GAP=0.45
OLD_SPLICE=14.858-0.06   # 旧整轨「更」前 60ms
def lufs(y):
    sf.write('/tmp/_l.wav',y,SR)
    r=subprocess.run(['ffmpeg','-hide_banner','-i','/tmp/_l.wav','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
    I=float(re.findall(r'I:\s+(-?[\d.]+) LUFS',r)[-1]); tp=float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS',r)[-1]); return I,tp
out=[np.zeros(int(LEAD*SR))]; t=LEAD; chars=[]; info=[]
for k,(cid,take,tempo,gdb,emph) in enumerate(PICK):
    src=f'hook2/{cid}-{take}.mp3'; w=f'hook2/_{cid}.wav'
    subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-ar',str(SR),'-ac','1','-af',f'atempo={tempo}',w],check=True)
    y,_=sf.read(w)
    al=[(x['text'].strip(),x['offset']/tempo,(x['offset']+x['duration'])/tempo) for x in json.load(open(src+'.json')) if han(x['text'])]
    env=np.ones(len(y))
    for ch,a,b in al:
        if ch in emph:
            i0=int(max(0,a-0.03)*SR); i1=min(len(y),int((b+0.05)*SR)); g=10**(emph[ch]/20)
            r=np.ones(i1-i0)*g; n=min(int(0.03*SR),len(r)//3); r[:n]=np.linspace(1,g,n); r[-n:]=np.linspace(g,1,n); env[i0:i1]=np.maximum(env[i0:i1],r)
    y=y*env
    a=np.abs(y); idx=np.where(a>0.03*a.max())[0]; i0=max(0,idx[0]-int(0.015*SR)); i1=min(len(y),idx[-1]+int(0.03*SR)); y=y[i0:i1]
    rms=np.sqrt(np.mean(y[np.abs(y)>0.01*np.abs(y).max()]**2)); y=y/rms*10**((-20+gdb)/20)
    off=i0/SR
    for ch,a,b in al: chars.append(dict(u=0,ch=ch,a=round(t+max(0,a-off),3),b=round(t+b-off,3)))
    dur=len(y)/SR; n=len([c for c in al]); info.append(dict(clause=cid,take=f'{cid}-{take}',start=round(t,3),end=round(t+dur,3),dur=round(dur,3),chars=n,cps=round(n/dur,2),atempo=tempo,gain_db=gdb,emph=emph))
    out.append(y); t+=dur
    if k<len(GAPS): out.append(np.zeros(int(GAPS[k]*SR))); t+=GAPS[k]; info[-1]['gap_after']=GAPS[k]
head=np.concatenate(out)
old,_=sf.read('vo_master.wav'); rest=old[int(OLD_SPLICE*SR):]
Ir,_=lufs(rest[:int(60*SR)]); Ih,tph=lufs(head)
head*=10**((Ir-Ih)/20); Ih2,tph2=lufs(head)
# 头段峰值控制（线性增益后若 TP>-1.5 用 alimiter）
if tph2>-1.5:
    sf.write('/tmp/_h.wav',head,SR); subprocess.run(['ffmpeg','-v','error','-y','-i','/tmp/_h.wav','-af','alimiter=limit=0.84:attack=2:release=60:level=false','/tmp/_h2.wav'],check=True); head,_=sf.read('/tmp/_h2.wav')
gap=np.zeros(int(TAIL_GAP*SR)); new_utt1=len(head)/SR+TAIL_GAP+0.06
y=np.concatenate([head,gap,rest]); sf.write('vo_master_v2.wav',y,SR)
delta=new_utt1-14.858
oldch=json.load(open('chars.json'))
allch=chars+[dict(x,a=round(x['a']+delta,3),b=round(x['b']+delta,3)) for x in oldch if x['u']>=1]
assert len(allch)==len(oldch),(len(allch),len(oldch))
json.dump(allch,open('chars_v2.json','w'),ensure_ascii=False)
Iall,tpall=lufs(y); Ih3,tph3=lufs(head)
D=json.load(open('cards.json'))
json.dump(dict(total=round(len(y)/SR,3),delta_after_card7=round(delta,3),utts=[[0,LEAD,round(len(head)/SR,3)]]+[[u[0],round(u[1]+delta,3),round(u[2]+delta,3)] for u in D['utts'][1:]]),open('cards_v2_meta.json','w'),indent=1)
json.dump(dict(clauses=info,head_lufs=Ih3,head_tp=tph3,rest_lufs=Ir,all_lufs=Iall,all_tp=tpall,total=round(len(y)/SR,3),delta=round(delta,3)),open('hook2/stitch_v2.json','w'),ensure_ascii=False,indent=1)
for i in info: print(i)
print('head LUFS',Ih3,'TP',tph3,'| rest',Ir,'| all',Iall,'TP',tpall,'| total',round(len(y)/SR,2),'delta',round(delta,3))
