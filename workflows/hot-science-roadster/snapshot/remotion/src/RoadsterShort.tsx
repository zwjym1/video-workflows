import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import captions from './captions.json';
import {SyncedSubs} from './ui';
import {
  ShotDanmaku,
  ShotEnding,
  ShotHook,
  ShotInfo,
  ShotNotVfx,
  ShotSummary,
  ShotTransitionA,
  ShotTransitionB,
  ShotTwoSystems,
} from './Shots';
import {DURATION_FRAMES, FPS, SHOTS, TA_FRAMES, TB_FRAMES} from './timing';

export {DURATION_FRAMES, FPS};

export const RoadsterShort: React.FC = () => {
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <Audio src={staticFile('voice.mp3')} />

      <Sequence from={SHOTS.S01.from} durationInFrames={SHOTS.S01.to - SHOTS.S01.from}>
        <ShotHook />
      </Sequence>
      <Sequence from={SHOTS.S02.from} durationInFrames={SHOTS.S02.to - SHOTS.S02.from}>
        <ShotNotVfx />
      </Sequence>
      <Sequence from={SHOTS.S03.from} durationInFrames={SHOTS.S03.to - SHOTS.S03.from}>
        <ShotDanmaku />
      </Sequence>
      <Sequence from={SHOTS.S04.from} durationInFrames={SHOTS.S04.to - SHOTS.S04.from}>
        <ShotTwoSystems />
      </Sequence>
      <Sequence from={SHOTS.TA.from} durationInFrames={TA_FRAMES}>
        <ShotTransitionA durationInFrames={TA_FRAMES} />
      </Sequence>
      <Sequence from={SHOTS.TB.from} durationInFrames={TB_FRAMES}>
        <ShotTransitionB durationInFrames={TB_FRAMES} />
      </Sequence>
      <Sequence from={SHOTS.S08.from} durationInFrames={SHOTS.S08.to - SHOTS.S08.from}>
        <ShotSummary />
      </Sequence>
      <Sequence from={SHOTS.S09.from} durationInFrames={SHOTS.S09.to - SHOTS.S09.from}>
        <ShotInfo durationInFrames={SHOTS.S09.to - SHOTS.S09.from} />
      </Sequence>
      <Sequence from={SHOTS.S10.from} durationInFrames={SHOTS.S10.to - SHOTS.S10.from}>
        <ShotEnding />
      </Sequence>

      {/* Global word-synced subs — above all shots, bottom-safe */}
      <SyncedSubs cues={captions.cues} fps={FPS} />
    </AbsoluteFill>
  );
};
