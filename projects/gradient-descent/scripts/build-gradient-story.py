"""Build narration-driven events; check the one regression model used everywhere."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    source=json.loads((ROOT/'output/fish-gradient-story-alignment.json').read_text(encoding='utf8'))
    chars=[];mapping=[]
    for b in source['boundaries']:
        for ch in b['text']:
            if ch.isalnum():chars.append(ch);mapping.append(b)
    text=''.join(chars)
    assert text==''.join(c for c in source['text'] if c.isalnum()),'Alignment text mismatch'
    assert all(a['offset']<=b['offset'] for a,b in zip(mapping,mapping[1:])),'Non-monotonic alignment'
    def phrase(s):
        clean=''.join(c for c in s if c.isalnum());i=text.find(clean)
        if i<0:raise ValueError(f'Missing aligned phrase {s}')
        first=mapping[i];last=mapping[i+len(clean)-1]
        return {'frame':round(first['offset']*30),'end':round((last['offset']+last['duration'])*30),'text':s}
    keys={'knobs':'转动两只旋钮','slopeKnob':'一个改斜率','interceptKnob':'一个改截距','result':'线变了','map':'把每一组旋钮位置','mapHere':'放到这张地图上','rise':'误差越大','height':'地形越高','local':'现在只看脚下这一小块','components':'分别看两个参数方向的坡度','combine':'合成一个下降方向','move':'移动一点','smaller':'误差变小','recalculate':'重新看坡度','again':'再走一步','term':'这就是梯度下降','small':'步长太小','large':'太大可能跨过头','compare':'用同样的三步','suitable':'合适的步长','stable':'能更稳地降低误差','return':'回到刚才的直线','closer':'它已经更贴近数据','finish':'AI学习就是这样不断调整参数'}
    events={k:phrase(v) for k,v in keys.items()}
    updates=[]
    for k in ['move','again']:
        e=events[k];updates.append({'start':e['frame'],'end':max(e['frame']+12,e['end'])})
    start=events['compare']['frame']+8;end=events['suitable']['frame']-5
    spacing=(end-start)/3
    assert spacing>=12,'Comparison narration too short'
    compare=[{'start':round(start+i*spacing),'end':round(start+i*spacing+min(14,spacing*.65))} for i in range(3)]
    remaining=events['return']['frame']-events['suitable']['frame']-20
    spacing2=remaining/6
    assert spacing2>=7,'Not enough time to finish convergence'
    settle=[{'start':round(events['suitable']['frame']+5+i*spacing2),'end':round(events['suitable']['frame']+5+i*spacing2+min(9,spacing2*.7))} for i in range(6)]
    sentences=[p.strip() for p in source['text'].replace('；','。').split('。') if p.strip()]
    captions=[]
    for sentence in sentences:
        # Split long clauses, retaining exact words and their aligned start.
        parts=sentence.split('，');acc=''
        for part in parts:
            if len(acc)+len(part)>19 and acc:captions.append({'frame':phrase(acc)['frame'],'text':acc});acc=part
            else:acc=acc+'，'+part if acc else part
        if acc:captions.append({'frame':phrase(acc)['frame'],'text':acc})
    sfx=[{'frame':events['map']['frame'],'audio':'sync-paper.wav','volume':.12},{'frame':events['rise']['frame'],'audio':'sync-paper.wav','volume':.12},{'frame':events['combine']['frame'],'audio':'sync-arrow.wav','volume':.13}]
    for i,item in enumerate(updates+compare+settle):sfx.append({'frame':item['end'],'audio':'sync-tap.wav','volume':.13 if i==0 else .05})
    # Independent sample MSE and numerical-gradient checks.
    X=[-1,-.5,0,.5,1]
    def loss(p):return .5*p[0]**2+p[1]**2
    for p in [[1.2,1.2],[.5,-.9],[-.6,.7]]:
        actual=sum((((.8+p[0])*x+.5+p[1])-(.8*x+.5))**2 for x in X)/len(X)
        assert abs(actual-loss(p))<1e-12
        for j,analytic in enumerate([p[0],2*p[1]]):
            a=p.copy();b=p.copy();a[j]+=1e-5;b[j]-=1e-5
            assert abs((loss(a)-loss(b))/2e-5-analytic)<1e-8
    for rate in [.35,.06,1.05]:
        p=[1.2,1.2]
        for _ in range(3):p=[p[0]*(1-rate),p[1]*(1-2*rate)]
        assert abs(p[0])<=2.1 and abs(p[1])<=2.3
        print(rate,p,loss(p))
    result={'audio':source['audio'],'duration':source['duration'],'frames':source['frames'],'boundaries':source['boundaries'],'events':events,'updates':updates,'compareUpdates':compare,'settleUpdates':settle,'captions':captions,'sfx':sfx}
    (ROOT/'src/gradient-story/timing.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'frames':result['frames'],'events':events,'compareUpdates':compare,'settleUpdates':settle},ensure_ascii=True))
if __name__=='__main__':main()
