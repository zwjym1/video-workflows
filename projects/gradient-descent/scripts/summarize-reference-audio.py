"""Summarize local transcript and measured energy; no listening claims."""
import json,re
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/reference-analysis';REPORT=ROOT/'参考研究'
def main():
    transcript=json.loads((REPORT/'reference-transcript.json').read_text(encoding='utf8'))
    signal=json.loads((OUT/'signal-analysis.json').read_text(encoding='utf8'))
    segments=transcript['segments'];words=[w for s in segments for w in s['words']]
    gaps=[]
    for a,b in zip(words,words[1:]):
        if b['start']-a['end']>=.25:gaps.append({'start':a['end'],'end':b['start'],'duration':b['start']-a['end'],'before':a['text'],'after':b['text']})
    chars=sum(len(re.findall(r'[\u3400-\u9fff]',s['text'])) for s in segments)
    sr,raw=wavfile.read(OUT/'audio-16k.wav');audio=raw.astype(float)/32768
    loud=np.loadtxt(OUT/'loudness-20ms.csv',delimiter=',',skiprows=1)
    # Candidate accents are energetic 100-ms syllabic regions, not linguistic proof.
    n=1600;blocks=audio[:len(audio)//n*n].reshape(-1,n)
    energy=20*np.log10(np.maximum(np.sqrt(np.mean(blocks**2,axis=1)),1e-8));times=(np.arange(len(energy))+.5)*.1
    candidates=[]
    for i in range(1,len(energy)-1):
        lo=max(0,i-15);hi=min(len(energy),i+16)
        contrast=energy[i]-np.median(energy[lo:hi])
        if energy[i]>energy[i-1] and energy[i]>=energy[i+1] and contrast>4 and energy[i]>-19:
            at=times[i];near=min(segments,key=lambda s:0 if s['start']<=at<=s['end'] else min(abs(s['start']-at),abs(s['end']-at)))
            candidates.append({'time':round(float(at),2),'rms_100ms_dbfs':round(float(energy[i]),2),'local_contrast_db':round(float(contrast),2),'nearby_asr':near['text']})
    chapters=[(0,38.8,'图像向量与流形假设'),(38.8,85.3,'纸团类比与分布损失/梯度困境'),(85.3,119.7,'扩散模型与正向加噪'),(119.7,158.2,'反向扩散与score向量场'),(158.2,195.1,'噪声标签与监督训练'),(195.1,226.35,'生成采样与文本条件控制')]
    chapter_data=[]
    for start,end,title in chapters:
        selected=[s for s in segments if start<=s['start']<end]
        count=sum(len(re.findall(r'[\u3400-\u9fff]',s['text'])) for s in selected)
        chapter_data.append({'start':start,'end':end,'title':title,'asr_han_chars':count,'chars_per_second':count/(end-start),'pause_candidates':[g for g in gaps if start<=g['start']<end],'energy_accent_candidates':[v for v in candidates if start<=v['time']<end]})
    result={'asr_segments':len(segments),'han_characters':chars,'asr_chars_per_second':chars/signal['duration'],'word_gap_candidates':gaps,'energy_accent_candidates':candidates,'chapters':chapter_data,'limitations':['ASR has domain-term substitutions; no manual audio verification.','VAD returned speech for 99% of duration; do not treat this as precise voice occupancy.','Energy peaks and transients may be speech consonants, music or edits, not identified sound effects.']}
    (OUT/'rhythm-analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    plt.rcParams['font.family']='Microsoft YaHei'
    fig,axes=plt.subplots(3,1,figsize=(16,9),layout='constrained')
    stride=160;times_wave=np.arange(0,len(audio),stride)/sr
    axes[0].plot(times_wave,audio[::stride],lw=.35,color='#34746a');axes[0].set_title('全片波形；橙色为 ASR 词间隔 ≥ 0.25s（候选停顿，非人工确认）')
    for gap in gaps:axes[0].axvspan(gap['start'],gap['end'],color='#d6a052',alpha=.25)
    axes[1].plot(loud[:,0],loud[:,1],lw=.55,color='#82714e');axes[1].set_ylim(-65,-5);axes[1].set_ylabel('20ms RMS / dBFS');axes[1].set_title('音量包络；竖线为章节候选边界')
    for start,_,_ in chapters[1:]:axes[1].axvline(start,color='#a64531',alpha=.45)
    # Explicitly visualize VAD non-speech, mostly end tail in this dense narration.
    axes[2].plot(times_wave,audio[::stride],lw=.3,color='#999999')
    for gap in signal['pauses']:axes[2].axvspan(gap['start'],gap['end'],color='#a64531',alpha=.4)
    axes[2].set_title('VAD非语音候选区（红）；本例VAD几乎连续命中，不能据此断言无停顿/无音乐')
    for ax in axes:ax.set_xlim(0,signal['duration']);ax.set_xlabel('秒');ax.grid(alpha=.15)
    fig.savefig(OUT/'waveform-rhythm.png',dpi=150);plt.close(fig)
    print(json.dumps({'segments':len(segments),'characters':chars,'chars_per_second':chars/signal['duration'],'gaps':len(gaps),'top_gaps':sorted(gaps,key=lambda g:g['duration'],reverse=True)[:15],'accent_candidates':candidates[:14]},ensure_ascii=False))
if __name__=='__main__':main()
