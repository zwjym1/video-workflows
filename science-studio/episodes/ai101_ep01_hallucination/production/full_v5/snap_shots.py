# 镜头起点吸附到最近拍（只在上一句结束与本句开始之间的空隙里移动，≤0.3s）
import json
P='timeline.json';T=json.load(open(P));G=json.load(open('beat_grid.json'))
off,per=G['offset'],G['period']
def nb(t):return off+round((t-off)/per)*per
LN=T['lines'];S={int(k):v for k,v in T['shots'].items()};mv=0
for n in sorted(S):
    if n==1:continue
    lo=max([l['t1'] for l in LN if l['shot']<n] or [0])+0.03
    fl=[l['t0'] for l in LN if l['shot']==n];hi=(fl[0] if fl else S[n]['s0']+0.3)-0.02
    b=nb(S[n]['s0']);c=[x for x in (b,b-per,b+per) if lo<=x<=hi]
    if c:
        x=min(c,key=lambda x:abs(x-S[n]['s0']))
        if abs(x-S[n]['s0'])<=0.3:S[n]['s0']=round(x,3);mv+=1
for n in sorted(S):
    if n+1 in S:S[n]['s1']=S[n+1]['s0']
T['shots']={str(k):v for k,v in S.items()};json.dump(T,open(P,'w'),ensure_ascii=False)
print('snapped',mv)
