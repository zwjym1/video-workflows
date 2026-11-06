# v4：按角色逐句响度对齐 —— 每句（O 和鱼）都拉到鱼的逐句中位响度，重建 vo_O/vo_F/vo_all
import json,numpy as np,soundfile as sf,pyloudnorm as pl
EPD='/workspace/science-studio/episodes/ai101_ep01_hallucination/';SR=48000
T=json.load(open('timeline.json'));m=pl.Meter(SR,block_size=0.2)
def lu(a):
    b=np.r_[a,np.zeros(max(0,int(0.45*SR)-len(a)),np.float32)];return m.integrated_loudness(b)
A={};Lu={}
for l in T['lines']:
    a,sr=sf.read(EPD+l['wav'],dtype='float32');a=a.mean(1) if a.ndim>1 else a;assert sr==SR;A[l['idx']]=a;Lu[l['idx']]=lu(a)
tgt=float(np.median([Lu[l['idx']] for l in T['lines'] if l['who']=='F']))
N=int(T['dur']*SR);V={'O':np.zeros(N,np.float32),'F':np.zeros(N,np.float32)};rep=[]
for l in T['lines']:
    a=A[l['idx']]*10**((tgt-Lu[l['idx']])/20);i=int(round(l['t0']*SR));V[l['who']][i:i+len(a)]+=a[:N-i];rep.append((l['idx'],l['who'],round(Lu[l['idx']],1),round(lu(a),2)))
pk=max(np.abs(V['O']+V['F']).max(),1e-6)
if pk>0.97:V={k:v*0.97/pk for k,v in V.items()}
for k in 'OF':sf.write(f'vo_{k}.wav',V[k],SR)
sf.write('vo_all.wav',V['O']+V['F'],SR)
role={k:round(m.integrated_loudness(V[k]),2) for k in 'OF'}
after={w:[r[3] for r in rep if r[1]==w] for w in 'OF'}
J=dict(target_line_lufs=round(tgt,2),role_integrated=role,role_diff=round(role['O']-role['F'],2),
  before_median={w:round(float(np.median([r[2] for r in rep if r[1]==w])),2) for w in 'OF'},
  after_line_range={w:[min(after[w]),max(after[w])] for w in 'OF'},lines=rep)
json.dump(J,open('loudness_roles.json','w'),ensure_ascii=False,indent=1)
print({k:v for k,v in J.items() if k!='lines'})
