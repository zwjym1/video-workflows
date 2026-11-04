# 音效来源

三个音效都是本项目自己用 Python + numpy 合成的，没有用任何第三方采样，版权归项目所有，可以商用。
生成脚本就是下面这段（44.1kHz、单声道、16bit），重新运行即可复现。

| 文件 | 用途 | 合成方法 |
|---|---|---|
| pop.wav | 元素弹入 | 90ms，方波和正弦混合，频率 520→1250Hz 上扫，指数衰减（8-bit 风格的“啵”） |
| flash.wav | 章节卡闪白 | 450ms，高通白噪声加上 800→2600Hz 上扫正弦，10ms 起音，指数衰减 |
| cut.wav | 硬切 | 120ms，150→55Hz 下扫正弦重击，叠一段极短噪声作为咔嗒 |

音量：pop 0.22，flash 0.4，cut 0.5。不用 BGM，因为对标视频没有 BGM。

```python
import numpy as np, wave
R=44100
def save(n,x):
  x=np.clip(x/np.max(np.abs(x))*0.8,-1,1);w=wave.open(n,'wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(R);w.writeframes((x*32767).astype('<i2').tobytes());w.close()
t=np.arange(int(R*.09))/R
f=np.linspace(520,1250,len(t));ph=2*np.pi*np.cumsum(f)/R
save('pop.wav',np.sign(np.sin(ph))*0.5*np.exp(-t*38)+np.sin(ph)*0.5*np.exp(-t*30))
t=np.arange(int(R*.45))/R;rng=np.random.default_rng(1)
n=rng.standard_normal(len(t));hp=np.diff(n,prepend=0)
f=np.linspace(800,2600,len(t));sh=np.sin(2*np.pi*np.cumsum(f)/R)
save('flash.wav',(hp*0.6+sh*0.4)*np.minimum(1,t/0.01)*np.exp(-t*7))
t=np.arange(int(R*.12))/R;f=np.linspace(150,55,len(t))
save('cut.wav',np.sin(2*np.pi*np.cumsum(f)/R)*np.exp(-t*30)+rng.standard_normal(len(t))*0.25*np.exp(-t*160))
```
