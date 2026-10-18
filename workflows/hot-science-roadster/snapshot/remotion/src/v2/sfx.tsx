import React from 'react';
import {Audio, Sequence, staticFile} from 'remotion';
const fr = (s: number) => Math.round(s * 30);
/** [file, startSec, volume, durSec?] */
export const CUES: [string, number, number, number?][] = [
  ['bed.wav', 0, 0.07],
  ['boom.wav', 0.0, 0.55], ['whoosh.wav', 1.0, 0.3], ['ding.wav', 1.9, 0.18],
  ['thump.wav', 3.27, 0.4], ['thump.wav', 4.61, 0.4],
  ['whoosh.wav', 6.2, 0.28], ['ding.wav', 8.42, 0.2],
  ['whoosh.wav', 10.1, 0.28], ['ding.wav', 11.42, 0.2], ['ding.wav', 11.66, 0.2],
  ['whoosh.wav', 13.0, 0.3], ['ding.wav', 13.2, 0.15], ['ding.wav', 15.39, 0.18],
  ['shutter.wav', 17.1, 0.5], ['whoosh.wav', 17.7, 0.22], ['ding.wav', 18.15, 0.2],
  ['fanhum.wav', 18.0, 0.22, 9.9], ['ding.wav', 21.25, 0.2], ['whoosh.wav', 22.6, 0.18], ['thump.wav', 23.78, 0.3], ['ding.wav', 26.45, 0.22], ['boom.wav', 26.45, 0.25],
  ['whoosh.wav', 27.8, 0.3], ['whoosh.wav', 29.0, 0.25],
  ['shutter.wav', 30.4, 0.5], ['whoosh.wav', 30.9, 0.22], ['ding.wav', 31.4, 0.2],
  ['click.wav', 32.6, 0.5], ['ding.wav', 32.7, 0.15], ['jet.wav', 33.4, 0.3, 4.2], ['ding.wav', 34.0, 0.15], ['ding.wav', 36.0, 0.15], ['whoosh.wav', 36.7, 0.22],
  ['hiss.wav', 38.5, 0.22], ['puff.wav', 42.0, 0.3], ['puff.wav', 42.45, 0.28], ['puff.wav', 42.9, 0.28], ['ding.wav', 42.0, 0.12], ['ding.wav', 44.8, 0.2],
  ['whoosh.wav', 46.8, 0.28], ['ding.wav', 48.44, 0.22], ['ding.wav', 49.40, 0.22],
  ['whoosh.wav', 51.1, 0.25], ['boom.wav', 53.1, 0.35], ['ding.wav', 56.8, 0.2], ['whoosh.wav', 58.0, 0.25], ['ding.wav', 58.3, 0.15], ['ding.wav', 59.55, 0.25], ['boom.wav', 59.55, 0.25],
  ['whoosh.wav', 61.2, 0.25], ['boom.wav', 62.1, 0.5],
];
export const SFX: React.FC = () => <>{CUES.map(([f, s, v, d], i) => <Sequence key={i} from={fr(s)} durationInFrames={fr(d ?? 64)}><Audio src={staticFile('sfx/' + f)} volume={v} /></Sequence>)}</>;
