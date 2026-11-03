"""同步自检：每句 实际人声起止(VAD，最终混音所用分轨) vs 嘴动起止(渲染所用嘴型序列) vs 字幕起止(subs.ass)。
用法: python3 sync_check.py <trial_dir> [mouth_npz]"""
import sys,json,re,numpy as np,subprocess
D=sys.argv[1];FPS=30
TL=json.load(open(D+'/timeline.json'));LN=TL['lines'];DUR=TL['dur']
def dec(p,sr=16000):return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True).stdout,np.float32)
def vad(a,sr=16000,hop=0.005):
    h=int(sr*hop);n=len(a)//h;r=np.sqrt((a[:n*h].reshape(n,h)**2).mean(1));db=20*np.log10(r+1e-9);return db>(db.max()-38),hop
A={w:vad(dec(f'{D}/vo_{w}.wav')) for w in 'OF'}
M=np.load(sys.argv[2] if len(sys.argv)>2 else D+'/mouth.npz')
ev=[]
for l in open(D+'/subs.ass'):
    m=re.match(r'Dialogue: \d+,(\d+):(\d+):([\d.]+),(\d+):(\d+):([\d.]+),(\w+),,0,0,0,,(.*)',l)
    if m:g=m.groups();ev.append((int(g[0])*3600+int(g[1])*60+float(g[2]),int(g[3])*3600+int(g[4])*60+float(g[5]),g[6],g[7].strip()))
rows=[];CH=[]
for i,l in enumerate(LN):
    w=l['who'];act,hop=A[w];lo=max(0,l['t0']-0.4);hi=l['t1']+0.4
    if i>0:lo=max(lo,(LN[i-1]['t1']+l['t0'])/2)
    if i+1<len(LN):hi=min(hi,(l['t1']+LN[i+1]['t0'])/2)
    idx=np.where(act[int(lo/hop):int(hi/hop)])[0]
    a0=lo+idx[0]*hop;a1=lo+(idx[-1]+1)*hop
    mv=M[w];fr=np.where(mv[int(lo*FPS):int(hi*FPS)]>0)[0]
    m0=lo+fr[0]/FPS if len(fr) else np.nan;m1=lo+(fr[-1]+1)/FPS if len(fr) else np.nan
    other=M['F' if w=='O' else 'O'][int(a0*FPS):int(a1*FPS)];wrong=float((other>0).mean())
    se=[e for e in ev if e[2]==w and lo-0.2<=e[0]<hi]
    s0=se[0][0] if se else np.nan;s1=se[-1][1] if se else np.nan
    ch=[]
    for e in se[1:]:
        c=re.sub(r'[^\w]','',e[3])[:1]
        cand=[x['t0'] for x in l.get('words',[]) if x['c'][:1]==c and x['t0']>=e[0]-0.4]
        if cand:ch.append(e[0]-cand[0])
    CH.extend(ch)
    rows.append(dict(i=i+1,who=w,audio=(round(a0,3),round(a1,3)),mouth_on=round(m0-a0,3),mouth_off=round(m1-a1,3),sub_on=round(s0-a0,3),sub_off=round(s1-a1,3),other_mouth=round(wrong,2)))
def st(k):v=np.abs([r[k] for r in rows]);return dict(max=round(float(np.nanmax(v)),3),mean=round(float(np.nanmean(v)),3))
S={k:st(k) for k in ['mouth_on','mouth_off','sub_on','sub_off']};S['sub_chunk_on']=dict(n=len(CH),max=round(float(np.max(np.abs(CH))),3) if CH else None,mean=round(float(np.mean(np.abs(CH))),3) if CH else None);S['other_mouth_max']=max(r['other_mouth'] for r in rows)
S['fail']=[r['i'] for r in rows if abs(r['mouth_on'])>0.08 or abs(r['mouth_off'])>0.08 or abs(r['sub_on'])>0.1 or r['other_mouth']>0.05]
for r in rows:print(r)
print(json.dumps(S,ensure_ascii=False))
json.dump(dict(rows=rows,summary=S),open(D+'/sync_report.json','w'),ensure_ascii=False,indent=1)
