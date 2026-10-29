# v3 = take_v1（v5 用的整条口播）里只把第 16 句换成 take_v2（同声音同参数整条重生成）的第 16 句；
# 接缝放在句间静音能量最低处，15 ms 等功率交叉淡化，替换句按 RMS 对齐到 v1 前后句。
import json,numpy as np,soundfile as sf
SR=48000
a=json.load(open('../backup_v5/vo/cards_timed.json'));b=json.load(open('cards_timed_v2.json'))
y1,_=sf.read('take_v1.wav'); y2,_=sf.read('take_v2.wav')
def env(y): w=int(0.01*SR); return np.sqrt(np.convolve(y**2,np.ones(w)/w,'same'))
e1,e2=env(y1),env(y2)
def cut(e,c,i):  # boundary between sentence i and i+1
    lo=int((c[i]['b']-0.04)*SR); hi=int((c[i+1]['a']+0.06)*SR); return lo+int(np.argmin(e[lo:hi]))
p1,q1=cut(e1,a,15),cut(e1,a,16); p2,q2=cut(e2,b,15),cut(e2,b,16)
rms=lambda s: np.sqrt(np.mean(s**2))
ref=np.mean([rms(y1[int(a[i]['a']*SR):int(a[i]['b']*SR)]) for i in (15,17)])
mid=y2[p2:q2]; g=ref/rms(y2[int(b[16]['a']*SR):int(b[16]['b']*SR)]); mid=mid*g
X=int(0.015*SR); r=np.linspace(0,1,X); fi=np.sin(r*np.pi/2); fo=np.cos(r*np.pi/2)
head=y1[:p1+X].copy(); tail=y1[q1-X:].copy()
out=np.concatenate([head[:-X], head[-X:]*fo+mid[:X]*fi, mid[X:-X], mid[-X:]*fo+tail[:X]*fi, tail[X:]])
sf.write('take_v3.wav',out,SR,subtype='FLOAT')
d=(q2-p2)-(q1-p1); s1=p1/SR; s2=q1/SR; off=(p1-p2)/SR
cards=json.load(open('../backup_v5/vo/cards_timed.json'))
cards[16]=dict(b[16]); 
def sh(c,o):
    c=dict(c); c['a']=round(c['a']+o,3); c['b']=round(c['b']+o,3); c['chars']=[(ch,round(x+o,3),round(z+o,3)) for ch,x,z in c['chars']]; return c
cards[16]=sh(b[16],off)
for i in range(17,len(cards)): cards[i]=sh(cards[i],d/SR)
json.dump(cards,open('cards_timed_v3.json','w'),ensure_ascii=False,indent=1)
print('seam1',round(s1,3),'seam2',round(s2,3),'gain dB',round(20*np.log10(g),2),'len change',round(d/SR,3),'dur',round(len(out)/SR,3))
print('seam env dB v1',round(20*np.log10(e1[p1]+1e-9),1),round(20*np.log10(e1[q1]+1e-9),1),'v2',round(20*np.log10(e2[p2]+1e-9),1),round(20*np.log10(e2[q2]+1e-9),1))
