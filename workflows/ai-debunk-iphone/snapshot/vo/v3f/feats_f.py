import json, re, sys, glob, difflib, numpy as np, soundfile as sf, librosa
from faster_whisper import WhisperModel
sys.path.insert(0, "."); from gen_f import NEW, UNITS
m = WhisperModel("large-v3", device="cpu", compute_type="int8"); F = {}
for p in sorted(glob.glob("takes/*_f*.wav")):
    u = p.split("/")[-1].rsplit("_f", 1)[0]; ref = re.sub(r"[^\w]", "", "".join(NEW[s] for s in UNITS[u]).lower())
    x, sr = sf.read(p); x = x.mean(1) if x.ndim > 1 else x
    segs, _ = m.transcribe(librosa.resample(x.astype(np.float32), orig_sr=sr, target_sr=16000), language="zh", beam_size=5, word_timestamps=True, initial_prompt="以下是普通话句子。")
    words = [(w.word.strip(), round(w.start, 3), round(w.end, 3)) for s in segs for w in s.words]
    asr = "".join(w for w, _, _ in words); hyp = re.sub(r"[^\w]", "", asr.lower()).replace("a.i.", "ai")
    cer = 1 - difflib.SequenceMatcher(a=ref, b=hyp).ratio()
    f, _, _ = librosa.pyin(x.astype(np.float32), fmin=70, fmax=400, sr=sr, frame_length=2048, hop_length=480); f = f[~np.isnan(f)]; st = 12 * np.log2(f / 100); q = int(len(st) * .75)
    F[p] = dict(asr=asr, cer=round(cer, 3), dur=round(len(x) / sr, 2), f0=round(float(st.mean()), 2), endrel=round(float(np.median(st[q:]) - st.mean()), 2), words=words)
    print(p, {k: v for k, v in F[p].items() if k != "words"}, flush=True)
json.dump(F, open("feats_f.json", "w"), ensure_ascii=False, indent=1)
