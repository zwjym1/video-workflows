# v4 = take_v3 + 地名间各加一段停顿（「北京 | 山西 | 山东」），让北京/山西镜头各 ≥0.9 s 且仍与口播同步；只在原有自然停顿（≈−57 dB）处插静音
import json,numpy as np,soundfile as sf
y,SR=sf.read('take_v3.wav'); cards=json.load(open('cards_timed_v3.json'))
INS=[(7.844,0.36,3,2),(8.392,0.38,3,4)]  # (原时刻, 插入秒, 卡号, 从第几个字起后移)
out=[];cur=0
for t,p,_,_ in INS: k=int(t*SR); out+=[y[cur:k],np.zeros(int(p*SR))]; cur=k
out.append(y[cur:]); sf.write('take_v4.wav',np.concatenate(out),SR,subtype='FLOAT')
sh=lambda c,o: (c[0],round(c[1]+o,3),round(c[2]+o,3))
for t,p,ci,j in INS:
    c=cards[ci]; c['chars']=[sh(x,p) if n>=j else x for n,x in enumerate(c['chars'])]; c['b']=round(c['b']+p,3)
    for k in range(ci+1,len(cards)):
        d=cards[k]; d['a']=round(d['a']+p,3); d['b']=round(d['b']+p,3); d['chars']=[sh(x,p) for x in d['chars']]
json.dump(cards,open('cards_timed_v4.json','w'),ensure_ascii=False,indent=1)
print(cards[3]['chars'][:6])
