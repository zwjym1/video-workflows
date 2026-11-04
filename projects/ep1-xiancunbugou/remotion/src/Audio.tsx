/**
 * 整片音频轨
 * ------------------------------------------------------------------
 * 三层：
 *   1) BGM：<Bgm/> 支持「只在指定帧区间播放」，音量可配
 *   2) 人声：各分镜里的 CueSub 自己挂（按逐字时间戳对齐）
 *   3) 音效：Sfx 组件（见 timeline/fps.tsx）
 *
 * BGM 的区间用设计帧（30fps 基准）写，内部按 fps 换算，
 * 所以 30/60fps 版本听到的是同一段音乐、同一个起点。
 */
import React from 'react';
import {Audio as RAudio, Sequence, staticFile, useVideoConfig} from 'remotion';
import {loadBeats, BgmSpec} from './timeline/beats';
import {fromDesignFrame} from './timeline/fps';
import {BGM_PHASE_SEC} from './timeline/grid';

/**
 * 默认 BGM 配置。换曲子只需要改这里 + 跑一次 scripts/bpm.py
 * we_never_120：We Never (Hi Noise remix)，已拉伸成精确 120 BPM，
 * 1 拍 = 0.5s = 15 设计帧，1 小节 = 2.0s = 60 设计帧（见 timeline/grid.ts）。
 * 音频 400s = 12000 设计帧，比整片长，不会循环到第二遍。
 */
export const DEFAULT_BGM: BgmSpec = {
  name: 'we_never_120',
  file: 'bgm/bgm_we_never_120.mp3',
  volume: 0.12,
  fromFrame: 0,
  // 400s = 12000 设计帧。比整片长，所以整片都会被覆盖到，不会循环回开头
  toFrame: 12000,
  offsetSec: 0,
};

export const Bgm: React.FC<{
  spec?: BgmSpec;
  /** 相对默认值的音量倍率（不同章节想要不同情绪时用） */
  gain?: number;
}> = ({spec = DEFAULT_BGM, gain = 1}) => {
  const {fps, durationInFrames} = useVideoConfig();
  const from = Math.round(fromDesignFrame(spec.fromFrame ?? 0, fps));
  const to = Math.min(durationInFrames, Math.round(fromDesignFrame(spec.toFrame ?? 1e9, fps)));
  const dur = Math.max(1, to - from);
  // 只播指定区间：Sequence 的长度就是这段区间，区间外不渲染 Audio
  if (dur <= 0) return null;
  // 相位补偿：裁掉音频开头的 0.03s，让拍点落在整 15/60 帧上（见 timeline/grid.ts）
  // 30fps → 1 帧；60fps → 2 帧，换算成秒相同，所以两档帧率听到的是同一相位
  const trim = Math.round(((spec.offsetSec ?? 0) + BGM_PHASE_SEC) * fps);
  return (
    <Sequence from={from} durationInFrames={dur} layout="none" name="BGM">
      <RAudio src={staticFile(spec.file)} volume={spec.volume * gain} trimBefore={trim} loop />
    </Sequence>
  );
};

/** 只在某段帧区间内响的 BGM（章节化配乐用） */
export const BgmRange: React.FC<{fromFrame: number; toFrame: number; file: string; volume?: number; loop?: boolean}> = ({
  fromFrame, toFrame, file, volume = 0.12, loop = true,
}) => {
  const {fps} = useVideoConfig();
  const from = Math.round(fromDesignFrame(fromFrame, fps));
  const dur = Math.max(1, Math.round(fromDesignFrame(toFrame - fromFrame, fps)));
  return (
    <Sequence from={from} durationInFrames={dur} layout="none">
      <RAudio src={staticFile(file)} volume={volume} loop={loop} />
    </Sequence>
  );
};

/** 拍点数据 + BGM 一起用的便捷：返回 BeatProvider 需要的 props。
 *  phaseSec 必须和 Bgm 实际裁掉的音频长度一致，否则脉动会比音乐晚 30ms。 */
export const bgmBeatProps = (spec: BgmSpec) => ({
  name: spec.name,
  startFrame: spec.fromFrame ?? 0,
  phaseSec: (spec.offsetSec ?? 0) + BGM_PHASE_SEC,
  data: loadBeats(spec.name),
});
