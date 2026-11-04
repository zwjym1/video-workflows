/**
 * 帧率归一
 * ------------------------------------------------------------------
 * 设计基准是 30fps：全片时间轴、字幕 cue、动效帧数都是按 30fps 写的。
 * 60fps 版本不重写时间轴，只在渲染时把「时间」统一换算：
 *
 *   design(frame, fps) = frame * 30 / fps      // 当前帧 → 设计帧
 *   toFps(designFrames, fps) = designFrames * fps / 30
 *
 * 所有 useCurrentFrame() 的读取都经过 useDesignFrame()，
 * 拿到的是「设计帧」，于是 30 和 60 下同一秒看到的画面一致。
 * useVideoConfig().durationInFrames 也同步翻倍。
 */
import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';

export const DESIGN_FPS = 30;

/** 当前帧 → 设计帧（30fps 坐标系） */
export const toDesignFrame = (frame: number, fps: number) => (frame * DESIGN_FPS) / fps;
/** 设计帧 → 当前 fps 帧 */
export const fromDesignFrame = (designFrames: number, fps: number) => (designFrames * fps) / DESIGN_FPS;
/** 毫秒 → 当前 fps 帧（取整） */
export const msToFrames = (ms: number, fps: number) => Math.round((ms / 1000) * fps);

/** 组件里统一用这个，替代 useCurrentFrame() */
export const useDesignFrame = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return toDesignFrame(f, fps);
};

/** 设计帧 → 当前 fps 帧，给 <Sequence from=… durationInFrames=…> 用 */
export const useSeq = () => {
  const {fps} = useVideoConfig();
  return {
    from: (designFrames: number) => Math.round(fromDesignFrame(designFrames, fps)),
    dur: (designFrames: number) => Math.max(1, Math.round(fromDesignFrame(designFrames, fps))),
    fps,
  };
};

/**
 * 段落起点（设计帧）
 * ------------------------------------------------------------------
 * Remotion 的 useCurrentFrame() 在 <Sequence> 里返回的是「相对段首」的帧。
 * 但拍点是整片时间轴上的绝对位置，所以脉动/吸附都需要知道自己在整片里的偏移。
 * Timeline 会给每个 Sequence 包一层 SegStartCtx。
 */
export const SegStartCtx = React.createContext(0);

/** 当前段在整片里的起始设计帧 */
export const useSegStart = () => React.useContext(SegStartCtx);

/** 整片绝对值的设计帧（= 段内帧 + 段首）—— 和拍点表同一坐标系的帧 */
export const useGlobalDesignFrame = () => useDesignFrame() + useSegStart();

/** 音效：设计帧 + 设计时长 → 当前 fps 的 Sequence。所有 sfx 都走这个，
 *  这样 60fps 下音效不会提前一半播完。 */
import {Audio, Sequence, staticFile} from 'remotion';

export const Sfx: React.FC<{at: number; dur?: number; file: string; volume?: number}> = ({at, dur = 6, file, volume = 0.2}) => {
  const {fps} = useVideoConfig();
  return (
    <Sequence from={Math.round(fromDesignFrame(at, fps))} durationInFrames={Math.max(1, Math.round(fromDesignFrame(dur, fps)))} layout="none">
      <Audio src={staticFile(file)} volume={volume} />
    </Sequence>
  );
};
