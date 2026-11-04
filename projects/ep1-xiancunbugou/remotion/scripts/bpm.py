#!/usr/bin/env python3
"""
BPM + 拍点检测
------------------------------------------------------------------
输入一个音频文件，输出：
  1) BPM（整数 + 两位小数）
  2) 每一拍的时间戳（秒）
存成 src/data/beat_<name>.json，格式 {"bpm": 112.35, "beats": [0.0, 0.534, ...]}

为什么不用 librosa.beat.beat_track 直接出拍点：
  librosa 的 beat_track 给的是「估计的拍位置」，对 click 轨偶尔会吞拍/多拍。
  这里用「librosa 估计 BPM → 用起音包络做相位对齐 → 按时值等间隔铺拍点」的两步法，
  拍点密度严格等于估计 BPM，且首拍对齐到第一个真实起音，误差不会累积。

用法：
  python3 scripts/bpm.py <audio> [--name NAME] [--out-dir DIR]
  python3 scripts/bpm.py public/bgm/placeholder_112.wav --name placeholder_112
"""
import argparse, json, os, sys, pathlib

import numpy as np
import librosa
from librosa.feature.rhythm import tempo as _tempo


def _transients(y, sr):
    """样本级「起音起点」检测。返回秒数组，精度 ~0.5ms。

    要点：不是找能量峰值，而是找「越过门限的第一刻」（rising edge）。
    峰值检测会系统性地晚 40–60ms（包络爬升时间），相位一偏整条拍点就全歪。
    """
    import numpy as _np
    if len(y) == 0:
        return []
    win = max(4, int(0.001 * sr))                  # 1ms 平滑，压掉单样本噪声
    env = _np.convolve(_np.abs(y), _np.ones(win) / win, "same")
    thr = float(env.max()) * 0.02
    above = env > thr
    idx = _np.where(~above[:-1] & above[1:])[0] + 1   # 上升沿
    if len(idx) == 0:
        return []
    times = idx / sr
    out = [float(times[0])]
    for t in times[1:]:
        if t - out[-1] >= 0.05:                     # 50ms 内合并（click 间隔最短 535ms）
            out.append(float(t))
    return out


def detect(path: str, name: str | None = None):
    y, sr = librosa.load(path, sr=22050, mono=True)
    dur = len(y) / sr

    # 1) 全局 BPM：起音包络 + 自相关（比 onset-tempo 更稳），并用 librosa 交叉校验
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512)
    tempo_est = _tempo(onset_envelope=onset_env, sr=sr, hop_length=512, aggregate=np.median)
    bpm_lib = float(np.atleast_1d(tempo_est)[0])

    # 自相关法：在 60–200 BPM 内找最强周期
    ac = librosa.autocorrelate(onset_env - onset_env.mean(), max_size=len(onset_env))
    fps_env = sr / 512
    lo, hi = int(fps_env * 60 / 200), int(fps_env * 60 / 60)
    lag = lo + int(np.argmax(ac[lo:hi]))
    bpm_ac = 60.0 * fps_env / lag

    # 两者接近就用自相关（分辨率更高），否则取 librosa
    bpm = bpm_ac if abs(bpm_ac - bpm_lib) < 4 else bpm_lib

    # 2) 用原始波形上的起音起点，同时精确拟合 BPM 和相位
    #    为什么不能直接用 librosa 的 tempo：
    #      tempo 是从节拍直方图里选的 bin，分辨率约 0.1–0.3 BPM，
    #      112.35 对应真值 112.00 时，64 拍会累积 0.1s 的偏移。
    #    真拍点之间是等距的，所以对 (t_i, i) 做最小二乘拟合即可得到
    #    亚毫秒级的周期 —— 前提是先把每个起音分配到一个整数拍号 i。
    transients = _transients(y, sr)
    period0 = 60.0 / bpm

    if len(transients) >= 4:
        # 用粗 BPM 给每个起音分配拍号，然后迭代拟合（2 轮足够收敛）
        phase, period = 0.0, period0
        for _ in range(3):
            ts = np.asarray(transients)
            idx = np.round((ts - phase) / period)
            # 只用落在网格附近的点参与拟合，避免漏检/多检把斜率带偏
            resid = np.abs(ts - (phase + idx * period))
            keep = resid < period * 0.25
            if keep.sum() < 4:
                break
            A = np.vstack([np.ones(keep.sum()), idx[keep]]).T
            sol, *_ = np.linalg.lstsq(A, ts[keep], rcond=None)
            phase, period = float(sol[0]), float(sol[1])
        bpm = 60.0 / period
    else:
        phase, period = 0.0, period0

    # 相位归一到 [0, period)
    phase = phase % period

    # 只铺到最后一个真实起音之后半拍，不外推到整段音频末尾
    last = transients[-1] if transients else dur
    end_t = min(dur, last + period * 0.5)
    # 从 i = -2 开始生成再裁剪：[0, period) 归一化后 phase 可能比真实首拍大一个周期
    # （音频正好从一拍开始、第 0 个起音没有上升沿时就会这样），
    # 往前多铺两拍再过滤，才能把 t≈0 那一拍捡回来。
    i0 = -2
    i1 = int(np.ceil((end_t - phase) / period)) + 1
    raw = [phase + i * period for i in range(i0, i1)]
    # 允许极小负值（首拍就在 0 附近，拟合相位有 ±1ms 抖动）并夹到 0
    beats = [round(max(0.0, b), 4) for b in raw if -0.02 <= b <= dur + 1e-6]


    return {
        'bpm': round(float(bpm), 2),
        'beats': beats,
        '_debug': {
            'bpm_librosa': round(bpm_lib, 2),
            'bpm_autocorr': round(bpm_ac, 2),
            'phase': round(phase, 4),
            'duration': round(dur, 3),
            'onsets_found': int(len(transients)),
            'source': os.path.basename(path),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audio')
    ap.add_argument('--name', default=None)
    ap.add_argument('--out-dir', default='src/data')
    args = ap.parse_args()

    name = args.name or pathlib.Path(args.audio).stem
    res = detect(args.audio, name)
    os.makedirs(args.out_dir, exist_ok=True)
    out = os.path.join(args.out_dir, f'beat_{name}.json')
    # 正式字段只保留 bpm / beats；调试信息放 _debug，渲染时忽略
    pathlib.Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=0))
    print(f"BPM = {res['bpm']}  (librosa {res['_debug']['bpm_librosa']}, autocorr {res['_debug']['bpm_autocorr']})")
    print(f"beats = {len(res['beats'])}  first 8 = {res['beats'][:8]}")
    print(f"-> {out}")


if __name__ == '__main__':
    main()
