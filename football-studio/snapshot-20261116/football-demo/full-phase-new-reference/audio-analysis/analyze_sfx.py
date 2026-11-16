#!/usr/bin/env python3
"""Local mixed-track SFX evidence: flux at visual anchors + transients, spectrum, CLAP zero-shot.
Does not claim listening. Model scores are not facts. Mixed clips are study-only, not clean SFX.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import stft

ROOT = Path("/workspace/football-demo/full-phase-new-reference")
WAV = ROOT / "audio/reference_original.wav"
OUT = ROOT / "audio-analysis"
CLIP_DIR = OUT / "clips_mixed_study"
CLIP_DIR.mkdir(parents=True, exist_ok=True)
SPEC_DIR = OUT / "spectra"
SPEC_DIR.mkdir(parents=True, exist_ok=True)

audio, sr = sf.read(str(WAV), always_2d=True)
mono = audio.mean(axis=1).astype(np.float32)
n = len(mono)
dur = n / sr

# --- spectral flux on 1024 hop 256 (~5.8ms) ---
nper = 1024
hop = 256
f, t_stft, Z = stft(mono, fs=sr, nperseg=nper, noverlap=nper - hop, boundary=None)
mag = np.abs(Z)
# positive log flux
logm = np.log1p(mag)
dlog = np.diff(logm, axis=1)
flux = np.maximum(dlog, 0).sum(axis=0)
# times of flux bins: mid of second frame of each diff
# stft times t_stft are center of each frame; flux[i] corresponds to transition t_stft[i] -> t_stft[i+1]
flux_t = 0.5 * (t_stft[:-1] + t_stft[1:])

# also high-frequency flux (>3kHz) and mid (1-6k)
hi_idx = f >= 3000
mid_idx = (f >= 800) & (f <= 6000)
lo_idx = f < 250
flux_hi = np.maximum(dlog[hi_idx], 0).sum(axis=0)
flux_mid = np.maximum(dlog[mid_idx], 0).sum(axis=0)
flux_lo = np.maximum(dlog[lo_idx], 0).sum(axis=0)


def rms_db(x):
    r = np.sqrt(np.mean(np.square(x)) + 1e-20)
    return 20 * math.log10(r)


def peak_db(x):
    p = np.max(np.abs(x)) + 1e-20
    return 20 * math.log10(p)


def band_energy_frac(x, lo, hi):
    # rfft energy fraction
    X = np.fft.rfft(x * np.hanning(len(x)))
    p = np.abs(X) ** 2
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    tot = p.sum() + 1e-20
    return float(p[(freqs >= lo) & (freqs < hi)].sum() / tot)


def centroid_hz(x):
    X = np.fft.rfft(x * np.hanning(len(x)))
    p = np.abs(X) ** 2
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    return float((freqs * p).sum() / (p.sum() + 1e-20))


def flux_in_window(t0, t1):
    m = (flux_t >= t0) & (flux_t < t1)
    if not np.any(m):
        return 0.0, 0.0, 0.0, 0.0
    return float(flux[m].max()), float(flux_hi[m].max()), float(flux_mid[m].max()), float(flux_lo[m].max())


def local_peak(center, radius=0.40):
    m = (flux_t >= center - radius) & (flux_t <= center + radius)
    if not np.any(m):
        return None
    i = np.argmax(flux[m])
    ts = flux_t[m][i]
    return {
        "t_s": float(ts),
        "flux": float(flux[m][i]),
        "flux_hi": float(flux_hi[m][i]),
        "flux_mid": float(flux_mid[m][i]),
        "flux_lo": float(flux_lo[m][i]),
        "offset_from_probe_s": float(ts - center),
    }


def envelope_duration(x, sr, rel_start=0.2, rel_end=0.2):
    env = np.abs(x)
    # 2ms smooth
    k = max(1, int(0.002 * sr))
    kernel = np.ones(k) / k
    env = np.convolve(env, kernel, mode="same")
    peak = env.max() + 1e-20
    above = np.where(env >= rel_start * peak)[0]
    if len(above) == 0:
        return 0.0
    start = above[0]
    after = env[start:]
    below = np.where(after < rel_end * peak)[0]
    end = start + (below[0] if len(below) else len(after) - 1)
    return (end - start) / sr


# load ASR words (machine, review needed)
asr_path = ROOT / "analysis/local_asr.json"
words = []
with open(asr_path) as f:
    asr = json.load(f)
# flexible schema
if isinstance(asr, dict):
    segs = asr.get("segments") or asr.get("chunks") or asr.get("words") or []
    if "text" in asr and not segs and "segments" not in asr:
        segs = []
    for s in segs:
        if "words" in s and isinstance(s["words"], list):
            for w in s["words"]:
                words.append({
                    "word": w.get("word") or w.get("text") or "",
                    "start": float(w.get("start", s.get("start", 0))),
                    "end": float(w.get("end", s.get("end", 0))),
                })
        else:
            words.append({
                "word": s.get("word") or s.get("text") or s.get("word", ""),
                "start": float(s.get("start", 0)),
                "end": float(s.get("end", 0) or s.get("start", 0)),
            })
elif isinstance(asr, list):
    for s in asr:
        words.append({
            "word": s.get("word") or s.get("text") or "",
            "start": float(s.get("start", 0)),
            "end": float(s.get("end", 0)),
        })


def asr_around(t, pad=0.25):
    hit = [w for w in words if w["start"] - pad <= t <= w["end"] + pad]
    mid = [w for w in hit if w["start"] < t < w["end"]]
    return {
        "mid_word": mid[0]["word"] if mid else None,
        "mid_word_interval": [mid[0]["start"], mid[0]["end"]] if mid else None,
        "nearby": [{"word": w["word"], "start": w["start"], "end": w["end"]} for w in hit[:8]],
        "in_speech_span": bool(mid),
    }


# probes
probes = [
    ("V_title", 1.00, "视觉锚：约1s标题弹出（时码可能近似）"),
    ("V_cut_5", 5.00, "视觉锚：约5s实拍/板切换（时码可能近似）"),
    ("V_label_6", 6.00, "视觉锚：约6s落点标签"),
    ("V_label_6.1", 6.10, "模式切换：约6.1s入板"),
    ("V_cut_13", 13.00, "视觉锚：约13s实拍/板切换（时码可能近似）"),
    ("V_circle_14", 14.00, "视觉锚：约14s定格圈注"),
    ("V_circle_14.1", 14.10, "模式切换：约14.1s板→实拍"),
    ("V_cut_21", 21.00, "视觉锚：约21s切换"),
    ("V_cut_21.6", 21.60, "模式切换：约21.6s入板"),
    ("V_redzone_25", 25.00, "视觉锚：约25s红防守区域"),
    ("V_passline_27", 27.00, "视觉锚：约27s传球线画出"),
    ("T01", 7.536, "既有通谱通量峰 T01"),
    ("T02", 17.616, "既有通谱通量峰 T02"),
    ("T03", 22.886, "既有通谱通量峰 T03"),
    ("T04", 27.726, "既有通谱通量峰 T04"),
    ("V_cut_30", 30.00, "视觉锚：约30s切换"),
    ("V_cut_31.6", 31.60, "模式切换：约31.6s板→实拍"),
    ("T05", 42.276, "既有通谱通量峰 T05"),
    ("V_cut_46", 46.00, "视觉锚：约46s切换"),
    ("V_cut_47.3", 47.30, "模式切换：约47.3s入板"),
    ("V_encircle_51", 51.00, "视觉锚：约51s包围连线"),
    ("T06", 52.786, "既有通谱通量峰 T06"),
    ("T07", 56.826, "既有通谱通量峰 T07"),
    ("T08", 65.506, "既有通谱通量峰 T08"),
    ("T09", 72.176, "既有通谱通量峰 T09"),
    ("T10", 76.416, "既有通谱通量峰 T10"),
    ("T11", 95.006, "既有通谱通量峰 T11"),
    ("T12", 100.036, "既有通谱通量峰 T12"),
    ("V_summary_105", 105.00, "视觉锚：总结段连续路线 105s"),
    ("V_summary_107", 107.00, "视觉锚：总结段 107s"),
    ("V_summary_109", 109.00, "视觉锚：总结段 109s"),
    ("V_summary_111", 111.00, "视觉锚：总结段 111s"),
    ("V_summary_113", 113.00, "视觉锚：总结段 113s（近结尾）"),
    ("M_80.0", 80.00, "模式切换：约80s实拍/板叠化"),
    ("M_87.2", 87.20, "模式切换：约87.2s入板"),
    ("M_98.2", 98.20, "模式切换：约98.2s入实拍"),
    ("M_104.7", 104.70, "模式切换：约104.7s入总结板"),
]

# baseline flux stats
flux_p50 = float(np.percentile(flux, 50))
flux_p80 = float(np.percentile(flux, 80))
flux_p90 = float(np.percentile(flux, 90))
flux_p95 = float(np.percentile(flux, 95))
flux_p99 = float(np.percentile(flux, 99))
flux_hi_p90 = float(np.percentile(flux_hi, 90))
flux_hi_p95 = float(np.percentile(flux_hi, 95))

records = []
clip_paths = {}
for name, t, note in probes:
    t = float(t)
    lp = local_peak(t, 0.40)
    peak_t = lp["t_s"] if lp else t
    # tight 120ms around local peak, 400ms study, 800ms clap
    def slice_at(center, pre, post):
        a = max(0, int((center - pre) * sr))
        b = min(n, int((center + post) * sr))
        return mono[a:b], a / sr, b / sr

    tight, ts, te = slice_at(peak_t, 0.040, 0.160)
    midw, ms, me = slice_at(peak_t, 0.080, 0.320)
    clapw, cs, ce = slice_at(peak_t, 0.120, 0.480)
    pre_bed, _, _ = slice_at(peak_t, 0.900, -0.050)  # 850ms ending 50ms before peak

    # also window locked to probe (visual time), not flux peak
    vis_tight, _, _ = slice_at(t, 0.040, 0.160)

    rec = {
        "id": name,
        "probe_s": t,
        "note": note,
        "local_peak": lp,
        "flux_at_probe_max_pm40ms": flux_in_window(t - 0.04, t + 0.04),
        "flux_percentiles_ref": {"p50": flux_p50, "p80": flux_p80, "p90": flux_p90, "p95": flux_p95, "p99": flux_p99},
        "tight_window_s": [ts, te],
        "peak_dbfs_200ms": peak_db(tight) if len(tight) else None,
        "rms_dbfs_200ms": rms_db(tight) if len(tight) else None,
        "rms_dbfs_pre_bed_850ms": rms_db(pre_bed) if len(pre_bed) else None,
        "sfx_minus_bed_db": (rms_db(tight) - rms_db(pre_bed)) if (len(tight) and len(pre_bed)) else None,
        "centroid_hz_200ms": centroid_hz(tight) if len(tight) else None,
        "e_frac_lt250": band_energy_frac(tight, 0, 250) if len(tight) else None,
        "e_frac_800_6k": band_energy_frac(tight, 800, 6000) if len(tight) else None,
        "e_frac_gt3k": band_energy_frac(tight, 3000, sr / 2) if len(tight) else None,
        "e_frac_gt8k": band_energy_frac(tight, 8000, sr / 2) if len(tight) else None,
        "env_dur_20pct_s": envelope_duration(tight, sr, 0.2, 0.2) if len(tight) else None,
        "vis_locked_rms_dbfs_200ms": rms_db(vis_tight) if len(vis_tight) else None,
        "vis_locked_centroid_hz": centroid_hz(vis_tight) if len(vis_tight) else None,
        "asr": asr_around(peak_t, 0.25),
        "asr_at_visual": asr_around(t, 0.15),
    }
    # flux percentile of local peak
    if lp:
        rec["local_peak_flux_percentile"] = float((flux <= lp["flux"]).mean() * 100)
        rec["local_peak_flux_hi_percentile"] = float((flux_hi <= lp["flux_hi"]).mean() * 100)
    # export mixed study clip (400ms around peak) — NOT a clean SFX
    clip_path = CLIP_DIR / f"{name}_peak{peak_t:.3f}_400ms_mixed_study.wav"
    a = max(0, int((peak_t - 0.080) * sr))
    b = min(n, int((peak_t + 0.320) * sr))
    sf.write(str(clip_path), audio[a:b], sr, subtype="PCM_16")
    rec["mixed_study_clip"] = str(clip_path)
    rec["mixed_study_clip_disclaimer"] = "混音短窗，仅供频谱/模型交叉，不是可发布独立音效"
    clip_paths[name] = (clip_path, peak_t)
    # also export visual-locked 400ms
    clip_v = CLIP_DIR / f"{name}_visual{t:.3f}_400ms_mixed_study.wav"
    a = max(0, int((t - 0.080) * sr))
    b = min(n, int((t + 0.320) * sr))
    sf.write(str(clip_v), audio[a:b], sr, subtype="PCM_16")
    rec["mixed_study_clip_visual_locked"] = str(clip_v)
    records.append(rec)

# rolling flux over summary 105-113 to see continuous transients
sum_m = (flux_t >= 104.5) & (flux_t <= 113.7)
summary_peaks = []
if np.any(sum_m):
    ft = flux_t[sum_m]
    fv = flux[sum_m]
    fhi = flux_hi[sum_m]
    # peaks above p80, min 0.25s apart
    last = -10
    order = np.argsort(fv)[::-1]
    for i in order:
        if fv[i] < flux_p80:
            break
        if ft[i] - last < 0.25 and abs(ft[i] - last) < 0.25:
            continue
        # spacing vs already accepted
        if any(abs(ft[i] - p["t_s"]) < 0.25 for p in summary_peaks):
            continue
        last = ft[i]
        summary_peaks.append({
            "t_s": float(ft[i]),
            "flux": float(fv[i]),
            "flux_hi": float(fhi[i]),
            "flux_percentile": float((flux <= fv[i]).mean() * 100),
        })
    summary_peaks.sort(key=lambda x: x["t_s"])

# 0.8-1.6s title window extra
title_m = (flux_t >= 0.6) & (flux_t <= 1.8)
title_peaks = []
if np.any(title_m):
    ft, fv, fhi = flux_t[title_m], flux[title_m], flux_hi[title_m]
    i = int(np.argmax(fv))
    title_peaks.append({
        "t_s": float(ft[i]), "flux": float(fv[i]), "flux_hi": float(fhi[i]),
        "flux_percentile": float((flux <= fv[i]).mean() * 100),
        "flux_hi_percentile": float((flux_hi <= fhi[i]).mean() * 100),
    })

# CLAP zero-shot
print("loading CLAP laion/clap-htsat-unfused ...", flush=True)
from transformers import pipeline

candidate_labels = [
    "spoken narration or human speech",
    "spoken consonant or plosive burst",
    "background music",
    "electronic kick drum or music beat",
    "short user-interface click or button click",
    "whoosh or swoosh transition sound",
    "short impact or hit sound effect",
    "football kick or ball kick",
    "crowd cheering in a stadium",
    "silence or very soft noise floor",
]
# hypothesis is implicit in pipeline
clf = pipeline(
    "zero-shot-audio-classification",
    model="laion/clap-htsat-unfused",
    device=-1,
)

clap_results = {}
for name, (path, peak_t) in clip_paths.items():
    # also classify visual-locked clip? do peak-locked first, and visual if different >80ms
    try:
        out = clf(str(path), candidate_labels=candidate_labels)
        # normalize schema
        if isinstance(out, dict) and "labels" in out:
            pairs = list(zip(out["labels"], out["scores"]))
        elif isinstance(out, list):
            # list of {label, score} or [[{}]]
            if out and isinstance(out[0], list):
                out = out[0]
            if out and isinstance(out[0], dict):
                pairs = [(d.get("label") or d.get("sequence"), float(d.get("score") or d.get("prob") or 0)) for d in out]
            else:
                pairs = []
        else:
            pairs = []
        pairs = sorted(pairs, key=lambda x: -x[1])
        clap_results[name] = [{"label": a, "score": float(b)} for a, b in pairs]
        print(f"CLAP {name} top={pairs[0] if pairs else None}", flush=True)
    except Exception as e:
        clap_results[name] = {"error": repr(e)}
        print(f"CLAP {name} ERROR {e!r}", flush=True)

# attach clap
for rec in records:
    rec["clap_peak_locked_400ms"] = clap_results.get(rec["id"])
    rec["clap_note"] = "模型分数不是事实；需与通量/频谱/画面/ASR交叉。高 speech 分不排除同窗混有短音效。"

# decisions later in a second pass file; this is measurements
out_json = {
    "source_wav": str(WAV),
    "duration_s": dur,
    "sr": sr,
    "method": {
        "flux": "positive log-magnitude STFT flux, nperseg=1024, hop=256",
        "classifier": "transformers pipeline zero-shot-audio-classification, laion/clap-htsat-unfused, CPU, local weights",
        "limits": [
            "分析对象是已混音轨，旁白、BGM、现场声与可能的音效叠加",
            "未进行人工听感判断",
            "CLAP 分数是文本-音频相似度，不能单独定名",
            "既有 T01–T12 当时用 4s 间隔筛选，短间隔视觉事件可能被漏检，本脚本已在锚点±0.4s 重测",
        ],
    },
    "flux_percentiles": {
        "p50": flux_p50, "p80": flux_p80, "p90": flux_p90, "p95": flux_p95, "p99": flux_p99,
        "hi_p90": flux_hi_p90, "hi_p95": flux_hi_p95,
    },
    "title_window_0.6_1.8_max": title_peaks,
    "summary_105_113_local_peaks_above_p80": summary_peaks,
    "probes": records,
}
out_path = OUT / "PROBE_MEASUREMENTS.json"
out_path.write_text(json.dumps(out_json, ensure_ascii=False, indent=2), encoding="utf-8")
print("WROTE", out_path, "probes", len(records), "summary_peaks", len(summary_peaks))
