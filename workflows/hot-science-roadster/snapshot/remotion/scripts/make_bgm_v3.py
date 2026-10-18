# Synthesized (original, royalty-free) tech BGM: section A (light) and B (drums). Am-F-C-G @112bpm
import numpy as np,soundfile as sf
SR=44100;BPM=112;beat=60/BPM;rng=np.random.default_rng(1)
def kick():
    n=int(.35*SR);t=np.arange(n)/SR;f=45+90*np.exp(-t*30);return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def snare():
    n=int(.25*SR);t=np.arange(n)/SR;return (rng.standard_normal(n)*.7+np.sin(2*np.pi*190*t)*.5)*np.exp(-t*18)
def hat(o=False):
    n=int((.18 if o else .05)*SR);x=np.diff(np.concatenate([[0],rng.standard_normal(n)]));return x*np.exp(-np.arange(n)/SR*(14 if o else 60))*.35
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]
hz=lambda m:440*2**((m-69)/12)
def add(out,s,x): out[s:s+len(x)]+=x
def render(dur,full):
    bar=4*beat;N=int(dur*SR);out=np.zeros(N+int(3*bar*SR));t=np.arange(int(bar*SR))/SR
    for b in range(int(dur/bar)+1):
        s=int(b*bar*SR);ch=chords[b%4]
        pad=sum(np.sin(2*np.pi*hz(m)*t)+.3*np.sin(2*np.pi*hz(m)*2.003*t) for m in ch)/3
        add(out,s,pad*np.minimum(1,t/.3)*np.minimum(1,(bar-t)/.3)*(.10 if full else .14))
        for k in range(8):
            n=int(beat/2*SR);tt=np.arange(n)/SR
            add(out,s+int(k*beat/2*SR),np.sign(np.sin(2*np.pi*hz(ch[k%3]+12)*tt))*np.exp(-tt*10)*.033)
        for k in range(4):
            bs=s+int(k*beat*SR)
            if full or k%2==0: add(out,bs,kick()*(.55 if full else .28))
            if full and k%2==1: add(out,bs,snare()*.3)
            if full:
                add(out,bs,hat());add(out,bs+int(beat/2*SR),hat(True))
                n=int(beat*SR);tt=np.arange(n)/SR;add(out,bs,np.sin(2*np.pi*hz(ch[0]-24)*tt)*np.exp(-tt*3)*.22)
            else: add(out,bs+int(beat/2*SR),hat()*.6)
    out=out[:N];return out/(np.abs(out).max()*1.12)
sf.write('bgm_A.wav',render(70,False),SR);sf.write('bgm_B.wav',render(70,True),SR)
n=int(.9*SR);t=np.arange(n)/SR
sf.write('sting.wav',np.sin(2*np.pi*(600+900*t)*t)*np.exp(-t*4)*.4+np.sin(2*np.pi*1568*t)*np.exp(-np.maximum(0,t-.35)*6)*(t>.35)*.4,SR)
print('ok')
