import json,subprocess,os
S=json.load(open('src/v3/align.json'))['sentences']
def W(i,q,d=0.0):
    ws=S[i]['words'];j='';ix=[]
    for k,w in enumerate(ws):
        for ch in w['text']: j+=ch;ix.append(k)
    for qq in (q if isinstance(q,list) else [q]):
        p=j.find(qq)
        if p>=0: return ws[ix[p]]['start']+d
    raise SystemExit(f'miss {i} {q}')
K=[('01-launch',W(0,'加速',.6)),('02-fly',W(0,'飞',.5)),('03-semi',W(1,'Semi',.5)),('04-comments',W(2,'画饼',.5)),('05-me',S[3]['start']+.8),
('06-concl',W(4,'但',.8)),('07-sources',W(5,'拆解',.6)),('08-two',W(5,'喷',.5)),('09-climb',S[6]['start']+.6),('10-fan3d',W(7,'抽',.3)),
('11-press',W(8,'外',.3)),('12-suction',W(8,'死',.6)),('13-rampcut',S[9]['start']+.5),('14-2x',W(9,'倍',.5)),('15-inv',W(10,'倒',.5)),('16-notinv',W(10,'不是',.6)),
('17-q',S[11]['start']+.8),('18-spacex',W(12,'SpaceX',.6)),('19-tank',W(13,'高',.5)),('20-valve',W(13,'喷',.4)),('21-react',W(14,'前',.3)),('22-balloon',W(14,'气球',.5)),
('23-nofire',W(15,'压缩',.5)),('24-rcs',W(16,'姿态',.2)),('25-rocket',W(16,'火箭',.6)),('26-summary',W(17,'喷气',.5)),('27-promo',S[18]['start']+.8),('28-2028',W(19,['二零二八'],.6)),
('29-closed',W(19,'封闭',.5)),('30-price',W(20,'二十五',.6)),('31-end',W(21,'敢',.6))]
os.makedirs('frames-v3',exist_ok=True)
json.dump(K,open('frames-v3/times.json','w'))
for n,t in K:
    subprocess.run(['npx','remotion','still','/tmp/b3','RoadsterShortV3',f'frames-v3/{n}.jpg',f'--frame={round(t*30)}','--gl=angle','--scale=0.5','--log=error'],check=True)
    print(n,round(t,2),flush=True)
