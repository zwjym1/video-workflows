"""Build frame events and quiet deterministic SFX from absolute Fish timestamps.

No network calls or credentials. Run after the alignment JSON is available.
"""
import json, math, wave
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
FPS=30

def main():
    source=json.loads((ROOT/'output/fish-gradient-full-alignment.json').read_text(encoding='utf8'))
    text=''; mapping=[]
    for boundary in source['boundaries']:
        clean=''.join(ch for ch in boundary['text'] if ch.isalnum())
        for ch in clean:
            text+=ch;mapping.append(boundary)
    expected=''.join(ch for ch in source['text'] if ch.isalnum())
    if text!=expected:raise ValueError('Alignment text does not match narration text')
    offsets=[b['offset'] for b in source['boundaries']]
    if offsets!=sorted(offsets):raise ValueError('Alignment offsets are not monotonic')
    def phrase(value):
        value=''.join(ch for ch in value if ch.isalnum())
        at=text.find(value)
        if at<0:raise ValueError(f'Missing aligned phrase: {value}')
        first=mapping[at];last=mapping[at+len(value)-1]
        return {'frame':round(first['offset']*FPS),'end':round((last['offset']+last['duration'])*FPS),'text':value}
    terms={'axis':'两个参数','grid':'画成','rise':'高度','slope':'坡度','direction':'朝误差减小的方向','update':'调整一步','recalculate':'再计算','readjust':'再调整','term':'梯度下降','steps':'步子也有讲究','small':'太小','big':'太大','normal':'换回合适的步长','steady':'更稳地降低误差','caveat':'这是两参数示意','ball':'球表示参数位置'}
    events={key:phrase(value) for key,value in terms.items()}
    def movement(event):
        end=event['end'];return {'start':max(event['frame'],end-14),'end':end,'arrow':event['frame']-7}
    first=[movement(events['update']),movement(events['readjust'])]
    # The first two updates align to spoken verbs. Faster repetition follows.
    after=first[-1]['end']+5
    if after+12<events['term']['end']:first.append({'start':after,'end':after+12,'arrow':after-5})
    modes={}
    for name,nextname in [('small','big'),('big','normal'),('normal','caveat')]:
        start=events[name]['frame']+3;end=events[nextname]['frame']-3
        spacing=(end-start)/3
        if spacing<9:raise ValueError(f'Insufficient time for three updates: {name}')
        modes[name]=[{'start':round(start+i*spacing),'end':round(start+i*spacing+min(12,spacing*.65)),'arrow':round(start+i*spacing-5)} for i in range(3)]
    continue_start=events['caveat']['frame']+6
    continues=[{'start':continue_start+i*12,'end':continue_start+i*12+8,'arrow':continue_start+i*12-4} for i in range(6)]
    if continues[-1]['end']>source['frames']:raise ValueError('Continuation exceeds audio timeline')
    timeline={'audio':source['audio'],'duration':source['duration'],'frames':source['frames'],'boundaries':source['boundaries'],'events':events,'updates':{'first':first,**modes,'continue':continues},'captions':[],'sfx':[]}
    captions=[('AI学习','AI 学习，到底在改什么？'),('把两个参数','把两个参数，画成一张地图'),('位置代表','位置代表参数，高度代表误差'),('根据当前位置','根据当前位置的坡度'),('朝误差','朝误差减小的方向，调整一步'),('再计算','再计算，再调整'),('这就是','这就是梯度下降'),('步子','步子也有讲究'),('太小','太小，走得慢'),('太大','太大，可能来回跳'),('换回','换回合适的步长'),('更稳','更稳地降低误差'),('这是两参数','这是两参数示意，真实模型维度更高'),('球表示','球表示参数位置，不是自己滚下山')]
    timeline['captions']=[{'frame':phrase(key)['frame'],'text':value} for key,value in captions]
    sr=48000;rng=np.random.default_rng(20261015)
    def sound(kind):
        duration={'paper':.34,'arrow':.14,'tap':.16,'sweep':.25}[kind]
        t=np.arange(round(sr*duration))/sr;noise=rng.normal(0,1,len(t))
        if kind=='tap':data=np.sin(2*np.pi*145*t)*np.exp(-t*35)+noise*.08*np.exp(-t*65)
        elif kind=='paper':data=np.convolve(noise,np.ones(13)/13,mode='same')*np.sin(np.pi*t/duration)**2
        elif kind=='arrow':data=np.sin(2*np.pi*(700*t+1300*t*t))*np.sin(np.pi*t/duration)**2*.5+noise*.04
        else:data=np.convolve(noise,np.ones(5)/5,mode='same')*np.sin(np.pi*t/duration)**2
        data=data/max(1,np.max(np.abs(data)))*.30
        with wave.open(str(ROOT/f'public/sync-{kind}.wav'),'wb') as wav:
            wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(sr);wav.writeframes((data*32767).astype('<i2').tobytes())
    for kind in ['paper','arrow','tap','sweep']:sound(kind)
    def sfx(frame,kind,volume):timeline['sfx'].append({'frame':frame,'audio':f'sync-{kind}.wav','volume':volume})
    sfx(events['grid']['frame'],'paper',.16);sfx(events['rise']['frame'],'paper',.14)
    sfx(events['direction']['frame'],'arrow',.18);sfx(events['recalculate']['frame'],'arrow',.12)
    for mode,updates in timeline['updates'].items():
        for i,update in enumerate(updates):
            if mode!='first':sfx(update['arrow'],'sweep' if mode=='big' else 'arrow',.12 if mode=='big' else .055)
            elif i>0:sfx(update['arrow'],'arrow',.08)
            sfx(update['end'],'tap',.15 if mode=='first' and i==0 else .065)
    target=ROOT/'src/gradient-sync/timing.json';target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'frames':timeline['frames'],'events':events,'updates':timeline['updates']},ensure_ascii=True))

if __name__=='__main__':main()
