"""V3 音频素材：VO 拷贝、BGM 截段+响度到 −22 LUFS、SFX 裁短/去头静音/统一电平，并记录每个样本的峰值偏移（whoosh 峰值对切点）"""
import json, subprocess, os, numpy as np, soundfile as sf, librosa, shutil
V2 = "/workspace/iphone-fake/v2"; PUB = f"{V2}/remotion/public/v3"
RAW = f"{V2}/assets/sfx_v3/raw"
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
shutil.copy(f"{V2}/vo/vo_master_v3c.wav", f"{PUB}/audio/vo_v3c.wav")
# ---- BGM：Mixkit 281 Complicated（Arulo），从 24.0s 附近的强拍起，取 80s（覆盖 v3c 口播 78s）
y, sr = librosa.load(f"{V2}/vo/bgm/cand_v3/mk_281.mp3", sr=48000, mono=False)
y = np.atleast_2d(y)
_, beats = librosa.beat.beat_track(y=librosa.to_mono(y), sr=sr)
bt = librosa.frames_to_time(beats, sr=sr)
start = float(bt[np.argmin(abs(bt - 24.0))])
DUR = 80.0
seg = y[:, int(start * sr): int((start + DUR) * sr)].T
tmp = "/tmp/bgm_seg.wav"; sf.write(tmp, seg, sr)
# 两遍 loudnorm 到 −22 LUFS（线性增益，不压缩）
out = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", "loudnorm=I=-22:TP=-3:LRA=20:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(out[out.rfind("{"):out.rfind("}") + 1])
gain = -22 - float(j["input_i"])
ff("-i", tmp, "-af", f"volume={gain:.2f}dB", "-ar", "48000", "-c:a", "pcm_s16le", f"{PUB}/audio/bgm_281.wav")
print("bgm start", round(start, 3), "input_i", j["input_i"], "gain", round(gain, 2))
# ---- SFX
SFX = {  # 名称: (源文件, 最长秒数, 目标峰值 dBFS)
    "whoosh_c": ("whoosh_c.mp3", 0.55, -9), "whoosh_d": ("whoosh_d.mp3", 0.55, -9), "whoosh_e": ("whoosh_e.mp3", 0.55, -9),
    "whoosh_b": ("whoosh_b.mp3", 0.6, -9), "whoosh_f": ("whoosh_f.mp3", 0.6, -10),
    "pop_a": ("pop_a.mp3", 0.25, -8), "pop_b": ("pop_b.mp3", 0.3, -8), "pop_c": ("pop_c.mp3", 0.3, -8),
    "click_b": ("click_b.mp3", 0.25, -10), "click_c": ("click_c.mp3", 0.3, -10),
    "hit_d": ("hit_d.mp3", 1.2, -4), "hit_c": ("hit_c.mp3", 1.2, -4),
}
meta = {}
for name, (src, mx, pk) in SFX.items():
    a, _ = librosa.load(f"{RAW}/{src}", sr=48000, mono=True)
    env = np.abs(a)
    thr = env.max() * 0.06
    on = int(np.argmax(env > thr))                      # 去掉头部静音
    a = a[max(0, on - int(0.004 * 48000)):]
    a = a[: int(mx * 48000)]
    fade = int(0.04 * 48000); a[-fade:] *= np.linspace(1, 0, fade)
    a *= 10 ** (pk / 20) / (np.abs(a).max() + 1e-9)
    # 峰值时间（用 10ms RMS 包络），whoosh 用它对齐切点
    hop = 480; rms = np.sqrt(np.convolve(a ** 2, np.ones(hop) / hop, mode="same"))
    peak = float(np.argmax(rms) / 48000)
    sf.write(f"{PUB}/sfx/{name}.wav", a, 48000, subtype="PCM_16")
    meta[name] = {"src": src, "dur": round(len(a) / 48000, 3), "peak": round(peak, 3)}
json.dump({"bgm": {"file": "v3/audio/bgm_281.wav", "track_start": round(start, 3), "gain_db": round(gain, 2)}, "sfx": meta},
          open(f"{V2}/remotion/scripts/v3/audio_meta.json", "w"), indent=1)
for k, v in meta.items(): print(k, v)
