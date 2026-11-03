"""规则 v2 硬指标测量 → out/<id>/measure_v2.json（用 .venv-dy 跑：librosa / faster_whisper / numpy，不依赖 cv2）。
python lib/measure_v2.py --id X --video 成片.mp4 [--srt 字幕.srt] [--trial-dir 含 timeline.json/vo_O.wav/vo_F.wav/sync_report.json 的目录]
   [--beat-period 0.51064 --beat-offset 0.0015] [--top-layer yes|no --top-note ..] [--design-cuts json]
每项失败都只记「未测」，不报错退出。"""
import argparse, json, os, re, subprocess, sys, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
for k in ('id', 'video', 'srt', 'trial-dir', 'top-note', 'design-cuts', 'top-layer'): ap.add_argument('--' + k)
ap.add_argument('--beat-period', type=float); ap.add_argument('--beat-offset', type=float, default=None)
a = ap.parse_args(); OD = os.path.join(ROOT, 'out', a.id); M = {}
def sh(c): return subprocess.run(c, capture_output=True, text=True).stdout
def dec(p, sr=16000): return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
def tryit(name, f):
    try: M[name] = f()
    except Exception as e: print(f'!! {name} 未测：{e}', file=sys.stderr)
pr = json.loads(sh(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate', '-of', 'json', a.video]))['streams'][0]
W, H = pr['width'], pr['height']; n, d = pr['r_frame_rate'].split('/'); FPS = float(n) / float(d)
M['orientation'] = 'landscape' if W > H else 'portrait'
def lufs():
    t = subprocess.run(['ffmpeg', '-nostats', '-i', a.video, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', t)[-1])
tryit('lufs', lufs)
def beats():
    w, h = 192, int(192 * H / W) // 2 * 2; raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', a.video, '-vf', f'scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    V = np.frombuffer(raw, np.uint8).reshape(-1, h, w)[:, :int(h * 0.86)].astype(np.float32)   # 去掉底部字幕带
    dd = np.abs(np.diff(V, axis=0)).mean((1, 2)); Y = V.mean((1, 2)); j = np.abs(Y[2:] - Y[:-2])
    per, off = a.beat_period, a.beat_offset
    if per is None:
        import librosa; y = dec(a.video, 22050); tm, bt = librosa.beat.beat_track(y=y, sr=22050, units='time'); per = float(np.median(np.diff(bt))); off = float(np.median(bt % per))
    off = off or 0.0; ons = []; q = 0
    for i, x in enumerate(dd):
        if x < 0.2: q += 1
        else:
            if x > 0.4 and q >= 6: ons.append((i + 1) / FPS)
            q = 0
    hit = lambda t: abs(t - (off + round((t - off) / per) * per)) <= 2 / FPS + 1e-6
    rng = np.random.default_rng(0); dur = len(V) / FPS
    return dict(onsets=len(ons), hits=sum(map(hit, ons)), rate=round(sum(map(hit, ons)) / max(1, len(ons)), 3), chance=round(float(np.mean([hit(x) for x in rng.uniform(0, dur, 5000)])), 3),
                miss=[round(t, 2) for t in ons if not hit(t)], period=round(per, 5), offset=round(off, 4), still=round(float((dd < 0.5).mean()), 3), n2f_gt10=int((j > 10).sum()), per_min_2f_gt10=round(float((j > 10).sum()) / dur * 60, 1), dur=round(dur, 2))
tryit('beats', beats)
TD = a.trial_dir
def voice():
    import librosa; TL = json.load(open(f'{TD}/timeline.json'))['lines']; sr = 16000; st = {w: dec(f'{TD}/vo_{w}.wav') for w in sorted(set(l['who'] for l in TL))}; R = []
    for l in TL:
        x = st[l['who']][int(l['t0'] * sr):int(l['t1'] * sr)]
        if len(x) < sr * 0.3 or np.abs(x).max() < 1e-3: continue
        f0, vf, _ = librosa.pyin(x, fmin=70, fmax=600, sr=sr, frame_length=1024, hop_length=320)
        R.append(dict(i=l.get('idx'), who=l['who'], t0=l['t0'], seed=l.get('seed'), f0=float(np.nanmedian(f0)) if np.any(vf) else float('nan'), mf=librosa.feature.mfcc(y=x, sr=sr, n_mfcc=20)[1:].mean(1), text=l.get('text', '')[:18]))
    res = {}
    for w in st:
        S = [r for r in R if r['who'] == w]; F = np.array([r['f0'] for r in S]); Mf = np.array([r['mf'] for r in S]); c = Mf.mean(0)
        cos = [float(np.dot(m, c) / np.linalg.norm(m) / np.linalg.norm(c)) for m in Mf]; med = float(np.nanmedian(F)); mad = float(np.nanmedian(np.abs(F - med)))
        res[w] = dict(n=len(S), f0_median=round(med, 1), cos_min=round(min(cos), 3), cos_median=round(float(np.median(cos)), 3),
                      outliers=[dict(i=r['i'], t0=r['t0'], f0=round(r['f0'], 1), cos=round(cs, 3), text=r['text']) for r, cs in zip(S, cos) if abs(r['f0'] - med) / (1.4826 * mad + 1e-6) > 2.5 or cs < 0.93])
    return res
if TD: tryit('voice', voice)
def lips():
    s = json.load(open(f'{TD}/sync_report.json'))['summary']
    return dict(max_err=max(s['mouth_on']['max'], s['mouth_off']['max']), mean_on=s['mouth_on']['mean'], mean_off=s['mouth_off']['mean'], other_mouth_max=s.get('other_mouth_max'), source='sync_report.json（渲染用嘴型序列 vs 分轨人声 VAD，非画面像素实测）')
if TD and os.path.exists(f'{TD}/sync_report.json'): tryit('lipsync', lips)
def cards():
    C = []
    for b in re.split(r'\n\s*\n', open(a.srt, encoding='utf-8-sig').read().strip()):
        L = b.strip().splitlines(); m = re.match(r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)', L[1] if len(L) > 1 else '')
        if m: g = list(map(int, m.groups())); C.append((g[0]*3600+g[1]*60+g[2]+g[3]/1000, g[4]*3600+g[5]*60+g[6]+g[7]/1000, ''.join(L[2:])))
    return C
if a.srt:
    C = cards(); txt = lambda t: re.sub(r'\s', '', t)
    def subs():
        ln = [len(txt(c[2])) for c in C]; o = dict(n=len(C), maxlen=max(ln), over16=sum(x > 16 for x in ln), top_layer=None if a.top_layer is None else a.top_layer == 'yes', top_note=a.top_note or '')
        return o
    tryit('subs', subs)
    def plus1():
        from faster_whisper import WhisperModel; y = dec(a.video); md = WhisperModel('small', device='cpu', compute_type='int8'); R = []
        for t0, t1, s in C:
            if '+1' in s or '＋1' in s:
                seg = y[int(max(0, t0 - 0.3) * 16000):int((t1 + 0.3) * 16000)]; heard = ''.join(x.text for x in md.transcribe(seg, language='zh')[0])
                R.append(dict(t=round(t0, 2), text=s, heard=heard, ok=('加一' in heard or '加1' in heard or '家一' in heard or '家衣' in heard)))
        return R
    tryit('plus1', plus1)
    def rhythm():
        sp = sum(c[1] - c[0] for c in C); ch = sum(len(re.sub(r'[\s，。！？、,.!?：:；;“”"「」…—\-]', '', c[2])) for c in C)
        o = dict(cps=round(ch / sp, 2), chars=ch, speech_s=round(sp, 2))
        if a.design_cuts:
            cu = json.load(open(a.design_cuts)); cu = cu['cuts'] if isinstance(cu, dict) else cu; o['unit_s'] = round(M.get('beats', {}).get('dur', C[-1][1]) / (len(cu) + 1), 2); o['unit_src'] = f'设计镜头 {len(cu)+1} 个'
        return o
    tryit('rhythm', rhythm)
json.dump(M, open(os.path.join(OD, 'measure_v2.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print(json.dumps({k: (v if k not in ('voice',) else {w: {kk: x[kk] for kk in ('f0_median', 'cos_min')} for w, x in v.items()}) for k, v in M.items()}, ensure_ascii=False, default=float)[:2500])
