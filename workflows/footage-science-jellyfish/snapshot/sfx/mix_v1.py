"""EP-20261029-01 混音 v1：vo_v1.wav（已去齿音）+ BGM「一切都在变好（生命力BGM）」从曲内 0.5 s 起（与 sfx/snap_v1.py 同一偏移）
+ 低频 pop/thud（−14 dB rel 人声，无高频 glitch）+ 两遍 loudnorm −16 LUFS / TP −1.5。
BGM 压缩沿用 EP-20261028-02 mix_v3：基线按源响度补偿，人声处 −8 dB，前 3 s 不压。
最后检查 4 kHz 以上峰值（目标 ≤ −14 dBFS），超了对全混做 4 kHz 以上动态压。"""
import json, subprocess, re, os, numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SR = 48000; CJ = json.load(open('cuts_v1.json')); TOTAL = CJ['total']; N = int(TOTAL * SR); BGM_OFF = CJ['bgm_off']
BGM = os.path.abspath('../audio/bgm/02_一切都在变好（生命力BGM）.mp3')
KT = json.loads(re.search(r'export const KT = (\{.*?\})', open('../remotion/src/data/kt.ts').read()).group(1))
CT = dict((n, t) for n, t in CJ['cuts'])
def load(path, ss=0.0, dur=None, ch=1):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(ss), '-i', path] + (['-t', str(dur)] if dur else []) + ['-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32).copy()
    return a.reshape(-1, ch) if ch > 1 else a
db = lambda x: 20 * np.log10(max(x, 1e-12)); rms = lambda a: float(np.sqrt(np.mean(np.square(a)) + 1e-20))
v = load('../vo/vo_v1.wav'); v = np.pad(v, (0, max(0, N - len(v))))[:N]
hop = SR // 100; fr = N // hop
vr = np.sqrt(np.mean(v[:fr * hop].reshape(fr, hop) ** 2, 1) + 1e-12); act = (20 * np.log10(vr) > -40)
Rv = db(rms(v[:fr * hop][np.repeat(act, hop)]))
EV = []
EV.append((KT['ufo'] + 0.27, 'pop', -14, 'UFO 打叉'))
for k, f in (('huojian', 'pop_up1'), ('cz6', 'pop'), ('gaodu', 'pop'), ('why', 'pop_up1'), ('bwfz', 'thud')):
    EV.append((KT[k] - 0.08 if k != 'gaodu' else KT[k] - 0.38, f, -14, f'名词戳 {k}'))
for k in ('c07_cc_bj', 'c08_tl_sx', 'c09_jn_sd'): EV.append((CT[k], 'pop', -15, f'地名戳 {k}'))
EV.append((KT['zhang'] - 0.5, 'thud', -13, '尾气猛地胀开'))
for k in ('k1', 'k2', 'k3'): EV.append((KT[k], 'pop_up1', -15, f'清单打勾 {k}'))
EV.append((KT['shao1'], 'thud', -14, '少一样 打叉'))
sfx = np.zeros(N, np.float32); table = []; cache = {}
for t, f, rel, note in sorted(EV):
    if f not in cache: cache[f] = load(f'lib/{f}.wav')
    a = cache[f]; g = Rv + rel - db(rms(a)); a = a * 10 ** (g / 20); i = int(t * SR); j = min(N, i + len(a)); sfx[i:j] += a[:j - i]
    table.append(dict(t=round(t, 3), sfx=f, rel_Rv_dB=rel, note=note))
b = load(BGM, ss=BGM_OFF, dur=TOTAL + 0.5, ch=2); b = np.pad(b, ((0, max(0, N - len(b))), (0, 0)))[:N]
r = subprocess.run(['ffmpeg', '-hide_banner', '-ss', str(BGM_OFF), '-t', str(TOTAL), '-i', BGM, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
SRC_LUFS = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])
GB0, DUCK = -17.5 + (-8.4 - SRC_LUFS), -8.0
a2 = act.astype(float).copy(); k = 15
for i in range(fr):
    if not act[i] and act[max(0, i - k):i].any() and act[i:i + k].any(): a2[i] = 1
t = np.arange(fr) / 100; duck = np.where(a2 > 0, DUCK, 0.0); duck[t < 3.0] = 0
g = np.zeros(fr); cur = 0.0
for i in range(fr):
    if t[i] < 3.0: cur = duck[i]
    else: cur += (duck[i] - cur) * ((1 - np.exp(-1 / 6)) if duck[i] < cur else (1 - np.exp(-1 / 30)))
    g[i] = cur
gs = np.interp(np.arange(N) / SR, t, g); fade = np.clip((TOTAL - np.arange(N) / SR) / 1.5, 0, 1)
bg = b * (10 ** ((GB0 + gs) / 20) * fade)[:, None]
def hf_peak(x):
    sos = butter(6, 4000, btype='high', fs=SR, output='sos'); h = sosfiltfilt(sos, x, axis=0); return db(float(np.max(np.abs(h))))
def hf_tame(x, lim_db):
    """4 kHz 以上分频峰值限制：零相位分频（lo = x − hf，可完全重建），高频段用 3 ms 最大值包络算增益，
    最小值保持 + 平滑（不留尖峰），只压超出 lim 的高频瞬态（齿音/爆破），中低频不动"""
    from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d
    sos = butter(4, 4000, btype='high', fs=SR, output='sos'); h = sosfiltfilt(sos, x, axis=0); lo = x - h
    e = np.abs(h) if h.ndim == 1 else np.max(np.abs(h), 1); w = int(0.003 * SR)
    e = maximum_filter1d(e, w * 2 + 1) + 1e-9; gr = np.minimum(1.0, 10 ** (lim_db / 20) / e)
    gr = uniform_filter1d(minimum_filter1d(gr, w * 2 + 1), w * 2 + 1)
    return lo + (h * gr if h.ndim == 1 else h * gr[:, None])
def master(x, name):
    x = x.copy(); f = int(0.4 * SR); x[-f:] *= np.linspace(1, 0, f)[:, None]
    sf.write('_pre.wav', x, SR, subtype='FLOAT')
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', '_pre.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
    af = f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample={SR}"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', '_pre.wav', '-af', af, '-ar', str(SR), '-ac', '2', '-c:a', 'pcm_s16le', '-t', str(TOTAL), name], check=True)
    return measure(name)
def measure(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]); TP = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1]); LRA = float(re.findall(r'LRA:\s+(-?[\d.]+) LU', r)[-1])
    if p.endswith('.m4a'):
        y = np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True,check=True).stdout,np.float32).reshape(-1,2).astype(float)
    else: y, _ = sf.read(p)
    return dict(I=I, TP=TP, LRA=LRA, hf4k_peak_dBFS=round(hf_peak(y), 2))
st = lambda m: np.stack([m, m], 1); O = '../remotion/assets/audio'
v_hf0 = hf_peak(v); v = hf_tame(v, -13.5).astype(np.float32); v_hf1 = hf_peak(v)
mix = bg + st(v + sfx); res = {}
res['mix'] = master(mix, f'{O}/mix.wav'); lim = -15.0
for it in range(4):
    if res['mix']['hf4k_peak_dBFS'] <= -14.2: break
    y, _ = sf.read(f'{O}/mix.wav'); y = hf_tame(y, lim - 1.0); res['mix'] = master(y, f'{O}/mix.wav'); res['mix']['hf_tame_iter'] = it + 1; lim -= 1.0
os.remove('_pre.wav'); sf.write('sfx_only.wav', sfx, SR, subtype='PCM_16')
sf.write('stem_bgm.wav', bg.astype(np.float32), SR, subtype='FLOAT'); sf.write('stem_vo.wav', v.astype(np.float32), SR, subtype='FLOAT')  # 同一相对电平，供 bgmfit --bgm-stem/--vo-stem
for gain in (0.0, -0.5, -1.0):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{O}/mix.wav', '-af', f'volume={gain}dB', '-c:a', 'aac', '-b:a', '192k', f'{O}/mix_aac.m4a'], check=True)
    m = measure(f'{O}/mix_aac.m4a'); m['pre_gain_dB'] = gain
    if m['TP'] <= -1.0: break
res['mix_aac'] = m
meta = dict(total_s=TOTAL, vo_hf4k_peak_before_after=[round(v_hf0, 2), round(v_hf1, 2)], Rv_dB=round(Rv, 2), bgm=dict(title='一切都在变好（生命力BGM）', author='Martins Garix', music_id='7552893524178733082', in_point_s=BGM_OFF, src_lufs=SRC_LUFS, base_dB=GB0, duck_dB=DUCK, tail_fade_s=1.5), results=res, events=table)
json.dump(meta, open('mix_meta.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False)); print('Rv', round(Rv, 2), 'events', len(table))
