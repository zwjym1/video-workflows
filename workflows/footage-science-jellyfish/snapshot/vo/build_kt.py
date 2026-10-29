import json
from pathlib import Path
R=Path(__file__).resolve().parent.parent
c=json.load(open(R/'vo/cards_master.json'))
def at(ci,ch=None,n=1):
    if ch is None: return c[ci]['chars'][0][1]
    k=0
    for x in c[ci]['chars']:
        if x[0]==ch:
            k+=1
            if k==n: return x[1]
    raise KeyError((ci,ch,n))
A=dict(ufo=(1,'U'),huojian=(1,'火'),date=(2,None),cz6=(2,'长'),ty=(2,'太'),bj=(3,'北'),sx=(3,'山'),sd=(3,'山',2),gaodu=(4,'高'),
 luoshan=(5,'落'),dimian=(5,'地'),yingzi=(5,'影'),gaokong=(6,'几'),shai=(6,'晒'),chong=(7,'冲'),zhuiguang=(7,'追'),liang=(7,'亮'),
 why=(8,'水'),chou=(9,'稠'),xi=(9,'细'),shao=(10,'稀'),yibai=(10,'一'),qiya=(10,'气'),bwfz=(10,'百',2),zhang=(11,'胀'),san=(11,'伞'),
 ling=(12,'零'),bing=(12,'冰'),sanshe=(13,'散'),gai=(13,'盖'),chu=(13,'触'),san3=(14,'三'),k1=(15,'清'),k2=(15,'高'),k3=(15,'头'),
 shao1=(16,'少'),meiyou=(16,'完'),quan=(17,'全'))
kt={k:round(at(*v),3) for k,v in A.items()}
(R/'remotion/src/data/kt.ts').write_text('// 口播关键字起点（秒，vo_v1.wav 时间轴），由 vo/build_kt.py 生成\nexport const KT = '+json.dumps(kt)+' as const;\n')
print(kt)
