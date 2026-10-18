"""实测 V3 预览：切镜（ffmpeg scene 0.30，0.4s 内合并）、音效数/对齐、结尾静音、整片响度、BGM 响度、每句画面变化覆盖率"""
import json, subprocess, re, sys, numpy as np, soundfile as sf
R = "/workspace/iphone-fake/v2/remotion"
MP4 = sys.argv[1] if len(sys.argv) > 1 else "/workspace/iphone-fake/v2/preview/v3_preview_540p.mp4"
d = json.load(open(f"{R}/src/v3/data/v3.json")); FPS = d["fps"]
W = json.load(open("/workspace/iphone-fake/v2/vo/" + (sys.argv[2] if len(sys.argv) > 2 else "words_v3c.json")))
out = {}
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", MP4], capture_output=True, text=True).stdout)
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", MP4, "-vf", "select='gt(scene,0.30)',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
raw = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", log)]
cuts = []
for t in raw:
    if not cuts or t - cuts[-1] > 0.4: cuts.append(t)
plan = [s["t0"] for s in d["shots"][1:]]
iv = np.diff([0] + cuts + [dur])
win = lambda a: sum(1 for c in cuts if a <= c < a + 8)
wins = [win(a) for a in np.arange(0, dur - 8, 0.25)]
match = []
for p in plan:
    near = min(cuts, key=lambda c: abs(c - p)) if cuts else None
    match.append(round((near - p) * FPS, 1) if near is not None and abs(near - p) < 0.3 else None)
out["cuts"] = dict(n=len(cuts), times=[round(c, 2) for c in cuts], mean_interval=round(dur / len(cuts), 2), mean_shot=round(float(np.mean(iv)), 2),
                   first_cut=round(cuts[0], 2), first10=sum(1 for c in cuts if c < 10), max_shot=round(float(iv.max()), 2),
                   longest_at=round(float(([0] + cuts)[int(np.argmax(iv))]), 2), fastest8=max(wins), slowest8=min(wins),
                   planned=len(plan), planned_detected=sum(1 for m in match if m is not None), planned_offset_frames=[m for m in match],
                   extra_detected=[round(c, 2) for c in cuts if min(abs(c - p) for p in plan) > 0.3],
                   section={"0-13.8": sum(1 for c in cuts if c < 13.8), "13.8-25.4": sum(1 for c in cuts if 13.8 <= c < 25.4), "25.4-57.4(揭穿)": sum(1 for c in cuts if 25.4 <= c < 57.4), "57.4-65.9(解释)": sum(1 for c in cuts if 57.4 <= c < 65.9), "65.9-end(收尾)": sum(1 for c in cuts if c >= 65.9)})
# 音效
sx = d["sfx"]
out["sfx"] = dict(n=len(sx), by_kind={k: sum(1 for x in sx if x["kind"] == k) for k in ("whoosh", "pop", "hit", "click")})
err = []
for x in sx:
    start_f = round(x["t"] * FPS); real_at = start_f / FPS + (x["at"] - x["t"])
    err.append(abs(real_at - x["at"]) * FPS)
wh = [x for x in sx if x["kind"] == "whoosh"]
cut_err = [abs(round(s["t0"] * FPS) / FPS - x["at"]) * FPS for s, x in zip(d["shots"][1:], wh)]
out["sfx"]["max_align_err_frames"] = round(max(err + cut_err), 2)
# 整片响度 / 结尾
ld = subprocess.run(["ffmpeg", "-hide_banner", "-i", MP4, "-af", "loudnorm=I=-16:TP=-1.5:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(ld[ld.rfind("{"):ld.rfind("}") + 1])
out["loudness"] = dict(I=float(j["input_i"]), TP=float(j["input_tp"]), LRA=float(j["input_lra"]))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", MP4, "-ac", "1", "-ar", "48000", "/tmp/v3mix.wav"], check=True)
a, sr = sf.read("/tmp/v3mix.wav")
def rms_db(x): return round(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12), 1)
hop = int(0.05 * sr); env = np.array([rms_db(a[i:i + hop]) for i in range(0, len(a) - hop, hop)])
sil = 0; best = 0
for v in env:
    sil = sil + 1 if v < -40 else 0; best = max(best, sil)
out["silence"] = dict(last_0p3s_db=rms_db(a[-int(0.3 * sr):]), last_word_end=W["sentences"][-1]["end"], video_end=round(dur, 3),
                      tail_after_last_word=round(dur - W["sentences"][-1]["end"], 3), longest_below_m40db_s=round(best * 0.05, 2))
# BGM（按 Remotion 同一闪避曲线离线算）
b, bsr = sf.read(f"{R}/public/{d['bgm']}")   # 保留立体声，LUFS 按声道功率相加
n = int(d["total"] * bsr); b = b[:n]
tt = np.arange(len(b)) / bsr
g = np.zeros_like(tt)
for s0, e0 in d["speech"]:
    up = np.clip((tt - (s0 - 0.08)) / 0.08, 0, 1); dn = np.clip(1 - (tt - e0) / 0.25, 0, 1)
    g = np.maximum(g, np.where(tt < s0, up, np.where(tt <= e0, 1, dn)) * ((tt >= s0 - 0.08) & (tt <= e0 + 0.25)))
fade = np.clip(np.interp(tt, [d["total"] - 0.35, d["total"]], [1, 0.25]), 0.25, 1)
k = 10 ** (-9 * g / 20) * fade
bd = b * (k[:, None] if b.ndim == 2 else k)
sf.write("/tmp/bgm_ducked.wav", bd, bsr); sf.write("/tmp/bgm_raw.wav", b, bsr)
def lufs(p):
    s = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(json.loads(s[s.rfind("{"):s.rfind("}") + 1])["input_i"])
out["bgm"] = dict(unducked_LUFS=lufs("/tmp/bgm_raw.wav"), ducked_LUFS=lufs("/tmp/bgm_ducked.wav"), duck_db=-9, speech_frac=round(float((g > 0.99).mean()), 2))
# 每句画面变化覆盖：句子时间窗 [start-0.12, end] 内有切镜 / 叠加层出现 / 推镜关键帧
ev = [s["t0"] for s in d["shots"]]
for s in d["shots"]:
    ev += [o["t"] for o in s["ov"]] + [k["t"] for k in s["cam"][1:-1]]
cov = []
for s in W["sentences"]:
    hit = [e for e in ev if s["start"] - 0.12 <= e <= s["end"]]
    cov.append((s["id"], len(hit)))
miss = [i for i, n in cov if n == 0]
out["coverage"] = dict(sentences=len(cov), covered=len(cov) - len(miss), ratio=round((len(cov) - len(miss)) / len(cov), 3), missing=miss)
# 判定套件次数
out["kit"] = sum(1 for s in d["shots"] for o in s["ov"] if o.get("kit") or (o["k"] == "stamp" and not o.get("still")))
out["split_screens"] = [(s["id"], round(s["t1"] - s["t0"], 2)) for s in d["shots"] if any(o["k"] == "split" for o in s["ov"])]
out["duration"] = round(dur, 3)
# 破绽圈：单镜内停留时长（circle/dash/penring 从出现到镜头结束或 t1）
circ = []
for s_ in d["shots"]:
    for o in s_["ov"]:
        c = o.get("circle") if o["k"] == "cursor" else (o if o["k"] in ("dash", "penring", "ring") else None)
        if c is None: continue
        t0 = max(c["t"], s_["t0"]); t1 = min(c.get("t1") or s_["t1"], s_["t1"])
        circ.append((s_["id"], o["k"], round(t1 - t0, 2)))
out["circles"] = circ
# 结尾 2 秒包络（50ms RMS，dBFS）
out["end_env_db"] = [rms_db(a[i:i + int(0.05 * sr)]) for i in range(len(a) - 2 * sr, len(a) - int(0.05 * sr) + 1, int(0.1 * sr))]
json.dump(out, open(MP4.replace(".mp4", "_measure.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
