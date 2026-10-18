// Align-tool project adapter for RoadsterShortV3.
// For a new video: copy this file, point it at your composition / alignment / defaults,
// then set "entry" + "timeline" in align/project.config.json.
import {RoadsterShortV3} from '../../src/v3/Short';
import {V3_FRAMES, defaultShots, graphicSegments, mergeShots, sentences, defaultAudio, mergeAudio, bgmGain} from '../../src/v3/shots';
import type {AlignProject} from '../types';

export const project: AlignProject = {
  title: 'Tesla Roadster 短视频 v3',
  composition: 'RoadsterShortV3',
  component: RoadsterShortV3 as any,
  fps: 30, width: 1920, height: 1080, durationInFrames: V3_FRAMES,
  audio: 'v3/voice-v3.wav',
  sentences: sentences.map((s) => ({i: s.i, text: s.text, start: s.start, end: s.end, words: s.words})),
  defaultShots, mergeShots, graphicSegments, defaultAudio, mergeAudio, bgmGain,
  inputProps: (timeline) => ({withVoice: true, timeline}),
};
