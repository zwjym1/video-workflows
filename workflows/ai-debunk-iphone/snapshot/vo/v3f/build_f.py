"""v3f 拼轨（= v3d；另把 04/09/18-19/28-29/30/31 换成 v3f 去品牌版 take）
v3d 拼轨（= v3c 规则；只把 01 句换成去地名版 01_d1，其余单元沿用 v3c 选定 take）
原 v3c 拼轨：选定候选 → 整单元保留（拆句对不切）→ 句内静音 >0.27s 压到 0.25s（静音中点 20ms 交叉淡化）
→ 单元首 15ms 淡入、尾 40ms 淡出（末句 80ms） → 单元间 0.25–0.32s（两处段落换气 0.40s）→ 结尾留约 0.63s 尾音
→ 可选 atempo（WSOLA，≤1.03）→ 两遍 loudnorm −16 LUFS / TP −1.7 → vo_master_v3c.wav/mp3 + words_v3c.json
用法: build_c.py [tempo]"""
import json, re, sys, subprocess, difflib
sys.path.insert(0, "/workspace/iphone-fake/v2/vo/v3c"); sys.path.insert(0, "/workspace/iphone-fake/v2/vo"); import os; os.chdir("/workspace/iphone-fake/v2/vo/v3c")
import numpy as np, soundfile as sf
from pypinyin import lazy_pinyin
from common_c import *
import common_c
NEW01 = "一整片海面，漂满了免费 iPhone？"
TXT["01"] = NEW01
import post
SR = 48000; VO = "/workspace/iphone-fake/v2/vo"
TEMPO = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
F = json.load(open("feats_c.json")); SEL = json.load(open("select_c.json")); PICK = dict(SEL["pick"]); PICK.update(json.load(open("override_c.json")))
FD = json.load(open("../v3d/feats_d.json")); PICK["01"] = "../v3d/takes/01_d1.wav"; F["../v3d/takes/01_d1.wav"] = FD["takes/01_d1.wav"]
sys.path.insert(0, "/workspace/iphone-fake/v2/vo/v3f"); from gen_f import NEW as NEWF
TXT.update(NEWF)
FF = json.load(open("../v3f/feats_f.json"))
for u_, k_ in {"04": "04_f3", "09": "09_f3", "18-19": "18-19_f1", "28-29": "28-29_f1", "30": "30_f2", "31": "31_f3"}.items():
    PICK[u_] = f"../v3f/takes/{k_}.wav"; F[PICK[u_]] = FF[f"takes/{k_}.wav"]
GAP_DEFAULT = 0.25
GAP_AFTER = {"03": 0.32, "13": 0.40, "31": 0.40, "05": 0.28, "07": 0.28, "12": 0.28, "21": 0.28, "24": 0.28, "29": 0.28, "30": 0.28, "37": 0.30, "39": 0.30}
TAIL = 0.71; INNER_MAX, INNER_TO = 0.27, 0.25
U = {"iphone": 2, "ai": 2, "bbc": 3, "openai": 4, "hive": 1, "grok": 2, "verify": 3}
def units(s): return len(re.findall(r"[\u4e00-\u9fff]", s)) + sum(U.get(w.lower(), 1) for w in re.findall(r"[A-Za-z]+", s))
def env_db(x):
    hop = SR // 100; n = len(x) // hop
    return 20 * np.log10(np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)]) + 1e-9)
def key(t): return t.lower().lstrip("@") if re.match(r"[@A-Za-z]", t) else lazy_pinyin(t)[0]
def hyp_tokens(words):
    out = []
    for w, s, e in words:
        w2 = re.sub(r"\d", lambda m: "零一二三四五六七八九"[int(m.group())], w.strip()).replace("x", "成")
        toks = re.findall(r"[A-Za-z]+|[\u4e00-\u9fff]", w2)
        for i, t in enumerate(toks): out.append((t, s + (e - s) * i / len(toks), s + (e - s) * (i + 1) / len(toks)))
    return out
def align(ref, hyp):
    rk = [key(t) for t in ref]; hk = [key(t[0]) for t in hyp]
    sm = difflib.SequenceMatcher(a=rk, b=hk, autojunk=False); T = [None] * len(ref)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1): T[i1 + k] = hyp[j1 + k][1:]
        elif op == "replace" and j2 > j1:
            s, e = hyp[j1][1], hyp[j2 - 1][2]; n = i2 - i1
            for k in range(n): T[i1 + k] = (s + (e - s) * k / n, s + (e - s) * (k + 1) / n)
    for i in range(len(T)):
        if T[i] is None:
            j = i
            while j < len(T) and T[j] is None: j += 1
            s = T[i - 1][1] if i > 0 else max(0, T[j][0] - 0.18 * (j - i))
            e = T[j][0] if j < len(T) else s + 0.18 * (j - i)
            for k in range(i, j): T[k] = (s + (e - s) * (k - i) / (j - i), s + (e - s) * (k - i + 1) / (j - i))
    return T
parts = []; t = 0.0; rows = []; words = []; info = {}
fi = int(0.015 * SR); fo = int(0.040 * SR); xf = int(0.020 * SR)
for gi, g in enumerate(GC):
    k = gid(g); name = PICK[k]; v = F[name]
    x, sr = sf.read(name); assert sr == SR; x = x.mean(1) if x.ndim > 1 else x
    ref = [tk for s in g for tk in ref_tokens(TXT[s])]
    T = align(ref, hyp_tokens(v["words"]))
    db = env_db(x); vv = np.where(db > -45)[0]
    a0 = max(0.0, vv[0] / 100 - 0.03); b0 = min(len(x) / SR, (vv[-1] + 1) / 100 + 0.08)
    y = x[int(a0 * SR):int(b0 * SR)].copy()
    T = [(max(0, s - a0), max(0, e - a0)) for s, e in T]
    # ASR 词尾常早于真实尾音：最后一个字的结束对齐到能量尾
    T[-1] = (T[-1][0], max(T[-1][1], (vv[-1] + 1) / 100 - a0))
    # 句内长静音压缩
    d2 = env_db(y); sil = d2 < -42; runs = []; i = 0
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]: j += 1
            if (j - i) / 100 > INNER_MAX and i > 3 and j < len(sil) - 3: runs.append((i / 100, j / 100))
            i = j
        else: i += 1
    cuts = [((a + b) / 2 - ((b - a) - INNER_TO) / 2, (a + b) / 2 + ((b - a) - INNER_TO) / 2) for a, b in runs]
    fade = np.linspace(1, 0, xf)
    for c0, c1 in sorted(cuts, reverse=True):
        i0, i1 = int(c0 * SR), int(c1 * SR)
        y = np.concatenate([y[:i0 - xf], y[i0 - xf:i0] * fade + y[i1 - xf:i1] * (1 - fade), y[i1:]])
    def mp(tt):
        sh = 0.0
        for c0, c1 in cuts:
            if tt >= c1: sh += c1 - c0
            elif tt > c0: sh += tt - c0
        return tt - sh
    T = [(mp(s), mp(e)) for s, e in T]
    # 单元内句界：按能量找静音段定边界；问号/句号句界的天然停顿 <0.25s 时在静音中点补到 0.28s（只插零，不切声音）
    bounds = {}; idx = 0
    for kk in range(len(g) - 1):
        idx += len(ref_tokens(TXT[g[kk]])); e_, s_ = T[idx - 1][1], T[idx][0]
        d3 = env_db(y); lo, hi = int(max(0, min(e_, s_) - 0.2) * 100), int(min(len(d3), (max(e_, s_) + 0.2) * 100))
        sil = d3[lo:hi] < -40; best = (0, 0); i = 0
        while i < len(sil):
            if sil[i]:
                j = i
                while j < len(sil) and sil[j]: j += 1
                if j - i > best[1] - best[0]: best = (i, j)
                i = j
            else: i += 1
        if best[1] - best[0] >= 2: sa, sb = (lo + best[0]) / 100, (lo + best[1]) / 100
        else: m_ = int(np.argmin(d3[lo:hi])) + lo; sa = sb = m_ / 100
        if TXT[g[kk]][-1] in "？。" and sb - sa < 0.25:
            add = 0.28 - (sb - sa); mid = int((sa + sb) / 2 * SR); f10 = int(0.01 * SR)
            y = np.concatenate([y[:mid - f10], y[mid - f10:mid] * np.linspace(1, 0, f10), np.zeros(int(add * SR)), y[mid:mid + f10] * np.linspace(0, 1, f10), y[mid + f10:]])
            T = [(a_ + add if a_ >= (sa + sb) / 2 else a_, b_ + add if b_ >= (sa + sb) / 2 else b_) for a_, b_ in T]; sb += add
        bounds[kk] = (sa + 0.02, sb - 0.02) if sb - sa >= 0.06 else ((sa + sb) / 2, (sa + sb) / 2)
    y[:fi] *= np.linspace(0, 1, fi)
    fo_ = int(0.08 * SR) if gi == len(GC) - 1 else fo   # 末句尾音：80ms 余弦释放，避免模型截断的硬停
    y[-fo_:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo_)))
    d = len(y) / SR
    idx = 0
    for s in g:
        n = len(ref_tokens(TXT[s])); tt = T[idx:idx + n]; toks = ref[idx:idx + n]; idx += n
        j_ = g.index(s); st_ = bounds[j_ - 1][1] if j_ > 0 else tt[0][0]; en_ = bounds[j_][0] if j_ < len(g) - 1 else min(d, tt[-1][1] + 0.04)
        tt = [(min(max(a_, st_), en_), min(max(b_, st_), en_)) for a_, b_ in tt]
        rows.append({"id": s, "text": TXT[s], "start": t + st_, "end": t + en_, "unit": k, "take": name,
                     "inner_cut": round(sum(c1 - c0 for c0, c1 in cuts), 3) if s == g[0] else 0})
        for tok, (s0, e0) in zip(toks, tt): words.append({"id": s, "text": tok, "start": t + s0, "end": t + min(e0, d)})
    parts.append(y); t += d
    if gi < len(GC) - 1:
        gap = GAP_AFTER.get(g[-1], GAP_DEFAULT); parts.append(np.zeros(int(gap * SR))); t += gap
    else:
        parts.append(np.zeros(int(max(0, TAIL - 0.08) * SR))); t += max(0, TAIL - 0.08)
raw = np.concatenate(parts); sf.write("/tmp/v3f_raw.wav", raw, SR)
src = "/tmp/v3f_raw.wav"
if abs(TEMPO - 1) > 1e-3:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"atempo={TEMPO}", "-ar", "48000", "/tmp/v3f_tempo.wav"], check=True); src = "/tmp/v3f_tempo.wav"
# 只削极少数尖峰（真峰 −2.5 dBFS 软限幅），好让线性 loudnorm 能到 −16 LUFS 而 TP ≤ −1.5
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", "volume=1.5dB,alimiter=limit=0.75:attack=1:release=40:level=false:asc=1", "-ar", "48000", "/tmp/v3f_lim.wav"], check=True); src = "/tmp/v3f_lim.wav"
post.main(src, f"{VO}/vo_master_v3f", room=False, chain=False)
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{VO}/vo_master_v3f.wav"]))
for r in rows:
    for kk in ("start", "end"): r[kk] = round(r[kk] / TEMPO, 3)
for w in words:
    for kk in ("start", "end"): w[kk] = round(w[kk] / TEMPO, 3)
for i, r in enumerate(rows): r["gap_after"] = round(rows[i + 1]["start"] - r["end"], 3) if i + 1 < len(rows) else round(dur - r["end"], 3)
tot = sum(units(TXT[s]) for s in SID); speech = sum(r["end"] - r["start"] for r in rows)
L = json.load(open(f"{VO}/vo_master_v3f.loudness.json"))
out = {"total_sec": round(dur, 3), "voice": "cfd828bdf120410c923fac0056c687c2", "model": "s2.1-pro-free", "speed": 1.25, "temperature": 0.65,
       "emotion_tags": "none", "tempo_post": TEMPO, "tempo_method": "none" if TEMPO == 1 else "ffmpeg atempo (WSOLA)", "inner_pause_max": INNER_TO,
       "script": "script_v3.md + v3d 01 句 + v3f 去品牌/平台词（04 09 18 19 28 29 30 31）", "units": tot, "speech_sec": round(speech, 3), "units_per_sec_speech": round(tot / speech, 2), "units_per_sec_overall": round(tot / dur, 2),
       "tail_after_last_word": round(dur - rows[-1]["end"], 3), "loudness": L, "sentences": rows, "words": words}
json.dump(out, open(f"{VO}/words_v3f.json", "w"), ensure_ascii=False, indent=1)
print("tempo", TEMPO, "dur", round(dur, 2), "speech", round(speech, 2), "u/s speech", out["units_per_sec_speech"], "overall", out["units_per_sec_overall"], "tail", out["tail_after_last_word"], L)
