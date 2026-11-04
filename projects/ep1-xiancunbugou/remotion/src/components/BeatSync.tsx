/**
 * 卡点组件
 * ------------------------------------------------------------------
 * useBeatPulse(strength, decayFrames)
 *   每一拍触发一个 1 → 0 的衰减值，用于强调色闪烁、缩放脉冲、光晕扩散。
 *   decayFrames 是「衰减到 0 需要多少设计帧」——短促（4–6 帧）像心跳，长（12–20）像呼吸。
 *
 * <OnBeat at=…> 把一个任意组件对齐到最近的拍子再入场。
 *
 * 两者都从 BeatProvider 拿当前 BGM 的拍点，不需要一层层传 props。
 */
import React from 'react';
import {BeatData, onBeatIndex, nearestBeat, isDownBeat, BEATS_PER_BAR, loadBeats} from '../timeline/beats';
import {useGlobalDesignFrame, useSegStart, useDesignFrame, DESIGN_FPS} from '../timeline/fps';

type BeatCtxValue = {
  data: BeatData;
  /** 音频起点在整片里对应的设计帧（BGM 不是从 0 帧起播时） */
  offsetSec: number;
  enabled: boolean;
};

const BeatContext = React.createContext<BeatCtxValue | null>(null);

/** 没有 Provider 时给一份空的，组件不会崩，只是不脉动 */
const EMPTY: BeatCtxValue = {data: {bpm: 0, beats: []}, offsetSec: 0, enabled: false};

export const BeatProvider: React.FC<{
  /** 节拍数据名（src/data/beat_<name>.json 的 <name>） */
  name?: string;
  /** 数据直接传入（外部已 loadBeats 时） */
  data?: BeatData;
  /** BGM 起播的设计帧：用来把音频内时间和整片时间对齐 */
  startFrame?: number;
  /**
   * BGM 音频被裁掉的开头秒数（Audio.tsx 的相位补偿）。
   * 裁掉之后音频内时间比视频时间快这么多，所以拍点在视频轴上整体提前。
   */
  phaseSec?: number;
  enabled?: boolean;
  children: React.ReactNode;
}> = ({name, data, startFrame = 0, phaseSec = 0, enabled = true, children}) => {
  const value = React.useMemo<BeatCtxValue>(() => {
    const d = data ?? (name ? loadBeats(name) : EMPTY.data);
    // 约定：视频时间 t_v ↔ 音频内时间 t_a = t_v - offsetSec
    //   BGM 从第 startFrame 帧起播  → t_a = t_v - startFrame/30
    //   音频开头被裁掉 phaseSec 秒  → t_a = t_v - startFrame/30 + phaseSec
    return {data: d, offsetSec: startFrame / DESIGN_FPS - phaseSec, enabled};
  }, [name, data, startFrame, phaseSec, enabled]);
  return <BeatContext.Provider value={value}>{children}</BeatContext.Provider>;
};

export const useBeatData = () => React.useContext(BeatContext) ?? EMPTY;

/**
 * 每一拍返回一个 1 → 0 的衰减值。
 * @param strength  峰值倍数（1 = 不额外放大，只给 0..1 的值用）
 * @param decayFrames 衰减时长（设计帧）
 * @param accentOnly 只在每小节首拍（重音）触发
 */
export const useBeatPulse = (strength = 1, decayFrames = 8, accentOnly = false): number => {
  // 用整片绝对帧：段内 Sequence 的 useCurrentFrame 是相对值，拍点是绝对时间
  const f = useGlobalDesignFrame();
  const {data, offsetSec, enabled} = useBeatData();
  if (!enabled || !data.beats.length) return 0;
  // 用「刚过去的那一拍」算衰减：t = 当前帧距该拍的帧数
  const {index, phaseSec} = onBeatIndex(f, DESIGN_FPS, data.beats, offsetSec);
  if (index < 0) return 0;
  if (accentOnly && !isDownBeat(index)) return 0;
  const sinceFrames = phaseSec * DESIGN_FPS;
  if (sinceFrames >= decayFrames) return 0;
  // 指数衰减，尾巴收得干净
  const k = 1 - sinceFrames / decayFrames;
  return Math.pow(k, 2) * strength;
};

/** 当前是第几拍、第几小节 —— 给需要「按拍换画面」的地方用 */
export const useBeatClock = () => {
  const f = useGlobalDesignFrame();
  const {data, offsetSec, enabled} = useBeatData();
  if (!enabled || !data.beats.length) return {beat: -1, bar: -1, beatInBar: -1, downBeat: false};
  const {index} = onBeatIndex(f, DESIGN_FPS, data.beats, offsetSec);
  return {
    beat: index,
    bar: index < 0 ? -1 : Math.floor(index / BEATS_PER_BAR),
    beatInBar: index < 0 ? -1 : index % BEATS_PER_BAR,
    downBeat: isDownBeat(index),
  };
};

/**
 * 把子组件的入场对齐到最近的拍子。
 * at 是「期望入场的设计帧」，最终入场帧会被吸附到 tolerance 帧内最近的拍。
 */
export const OnBeat: React.FC<{
  at: number;
  tolerance?: number;
  children: React.ReactNode;
  /** 对齐后额外提前/延后几帧（负数=提前） */
  nudge?: number;
}> = ({at, tolerance = 6, nudge = 0, children}) => {
  const snapped = useSnapToBeat(at, tolerance) + nudge;
  return <BeatSnap from={snapped}>{children}</BeatSnap>;
};

/**
 * 把「段内设计帧」吸附到最近拍点，返回吸附后的段内帧。
 * 容差以外原样返回 —— 宁可错过拍子，也不要把入场硬拽到离字幕太远的地方。
 */
export const useSnapToBeat = (localFrame: number, tolerance = 3): number => {
  const {data, offsetSec, enabled} = useBeatData();
  const segStart = useSegStart();
  if (!enabled || !data.beats.length) return localFrame;
  const abs = segStart + localFrame;
  const snappedAbs = nearestBeat(abs, DESIGN_FPS, data.beats, tolerance, offsetSec);
  return snappedAbs === abs ? localFrame : snappedAbs - segStart;
};

/** 内部：到帧才渲染 */
const BeatSnap: React.FC<{from: number; children: React.ReactNode}> = ({from, children}) => {
  const f = useDesignFrame();
  if (f < from) return null;
  return <>{children}</>;
};

/** 便捷：把数值按拍量化（1.2 表示 1.2 拍一循环） */
export const useBeatPhase = (beatsPerCycle = 1): number => {
  const f = useGlobalDesignFrame();
  const {data, offsetSec, enabled} = useBeatData();
  if (!enabled || !data.beats.length) return 0;
  const {index, progress} = onBeatIndex(f, DESIGN_FPS, data.beats, offsetSec);
  if (index < 0) return 0;
  return ((index % beatsPerCycle) + progress) / beatsPerCycle;
};

/** 脉冲式强调包装：每拍把子组件弹一下（scale 1 → 1+amount → 1） */
export const BeatPulse: React.FC<{amount?: number; decayFrames?: number; accentOnly?: boolean; children: React.ReactNode}> = ({
  amount = 0.06, decayFrames = 8, accentOnly = false, children,
}) => {
  const p = useBeatPulse(1, decayFrames, accentOnly);
  return <div style={{transform: `scale(${1 + p * amount})`, transformOrigin: 'center'}}>{children}</div>;
};
