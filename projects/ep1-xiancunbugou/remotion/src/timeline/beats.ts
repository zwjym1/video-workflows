/**
 * 卡点引擎：把任意帧吸附到最近的拍子，并给动画提供「第几拍」。
 * ------------------------------------------------------------------
 * 数据来自 scripts/bpm.py 生成的 src/data/beat_<name>.json：
 *   {"bpm": 112.35, "beats": [0.0, 0.534, ...]}
 * 注意：beats 是「音频文件内的时间轴」，不是整片时间轴。
 * BGM 从某个设计帧开始播时，用 offsetSec 把两者对齐。
 */

export type BeatData = {bpm: number; beats: number[]};

/**
 * loadBeats(name) 读 json。
 * 用 require 静态引用而不是 fetch：Remotion 打包时需要把 json 一起打进去，
 * 运行时 fetch 在渲染器里不可靠，且 still 渲染没有网络。
 */
const REGISTRY: Record<string, BeatData> = {
  placeholder_112: require('../data/beat_placeholder_112.json'),
  // We Never (Hi Noise remix) 拉伸到精确 120 BPM：1 拍 = 0.5s，offset 0.03s
  // json 里多带 period / offset / dur / name 字段，BeatData 只取 bpm + beats
  we_never_120: require('../data/beats_we_never_120.json'),
};

/** 可用的节拍轨列表（给 Root 里配置 BGM 用） */
export const BEAT_NAMES = Object.keys(REGISTRY);

export const loadBeats = (name: string): BeatData => {
  const d = REGISTRY[name];
  if (!d) throw new Error(`beat data "${name}" not found. Available: ${BEAT_NAMES.join(', ')}. ` +
    `生成方法: python3 scripts/bpm.py public/bgm/<file> --name ${name}`);
  return d;
};

/** 已加载的 BGM 配置：哪条轨、从整片第几帧开始、音量多少、只播到第几帧 */
export type BgmSpec = {
  name: string;
  /** 音频文件名（public/bgm/ 下） */
  file: string;
  volume: number;
  /** 整片时间轴上的起播帧（设计帧，30fps 基准） */
  fromFrame?: number;
  /** 整片时间轴上的停止帧（设计帧，不含） */
  toFrame?: number;
  /** 音频文件内部的起始偏移秒（裁掉前奏时用） */
  offsetSec?: number;
};

/**
 * 把任意帧吸附到最近的拍子。
 * @param frame  设计帧（30fps 坐标）
 * @param fps    设计帧率（固定 DESIGN_FPS=30，保留参数以便和签名一致）
 * @param beats  拍点秒数组
 * @param toleranceFrames 容差（帧）。超出容差就不吸附，原样返回 ——
 *        避免「离拍子太远的入场被硬拽过去」而显得节奏错乱。
 * @param offsetSec 音频起点在整片里的时间偏移（BGM 不是从 0 帧开始时）
 */
export const nearestBeat = (
  frame: number,
  fps: number,
  beats: number[],
  toleranceFrames = 6,
  offsetSec = 0,
): number => {
  if (!beats.length) return frame;
  const t = frame / fps - offsetSec;
  // 二分找插入点
  let lo = 0, hi = beats.length - 1;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (beats[mid] < t) lo = mid + 1; else hi = mid;
  }
  const cands = [beats[lo]];
  if (lo > 0) cands.push(beats[lo - 1]);
  let best = cands[0];
  for (const c of cands) if (Math.abs(c - t) < Math.abs(best - t)) best = c;
  const targetFrame = (best + offsetSec) * fps;
  return Math.abs(targetFrame - frame) <= toleranceFrames ? targetFrame : frame;
};

/**
 * 当前处于第几拍（从 0 开始；在第一个拍点之前返回 -1）。
 * 返回值同时带上「这一拍内的进度」0..1，做脉动衰减用。
 */
export const onBeatIndex = (
  frame: number,
  fps: number,
  beats: number[],
  offsetSec = 0,
): {index: number; progress: number; phaseSec: number} => {
  if (!beats.length) return {index: -1, progress: 0, phaseSec: 0};
  const t = frame / fps - offsetSec;
  if (t < beats[0]) return {index: -1, progress: 0, phaseSec: t};
  let lo = 0, hi = beats.length - 1;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if (beats[mid] <= t) lo = mid; else hi = mid - 1;
  }
  const start = beats[lo];
  const period = beats.length > 1 ? beats[1] - beats[0] : 0.5;
  const end = lo + 1 < beats.length ? beats[lo + 1] : start + period;
  const progress = end > start ? Math.min(1, (t - start) / (end - start)) : 0;
  return {index: lo, progress, phaseSec: t - start};
};

/** 距下一拍还有多少帧（负数表示刚过拍）。用于「提前入场」的排版节奏 */
export const framesToNextBeat = (frame: number, fps: number, beats: number[], offsetSec = 0): number => {
  if (!beats.length) return Infinity;
  const t = frame / fps - offsetSec;
  for (const b of beats) if (b > t) return (b - t) * fps;
  return Infinity;
};

/** 拍号：每小节几拍（4/4） */
export const BEATS_PER_BAR = 4;
/** 这一拍是不是小节首拍（重音） */
export const isDownBeat = (index: number) => index >= 0 && index % BEATS_PER_BAR === 0;
