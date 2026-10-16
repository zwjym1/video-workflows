import type React from 'react';
export type Shot = {id: string; label?: string; src: string; start: number; end: number; in: number; rate: number};
export type Timeline = {version: number; composition?: string; fps?: number; shots: Shot[]};
export type Word = {text: string; start: number; end: number};
export type AlignProject = {
  title: string; composition: string; component: React.ComponentType<any>;
  fps: number; width: number; height: number; durationInFrames: number;
  audio: string; // narration file, relative to publicDir
  sentences: {i: number; text: string; start: number; end: number; words: Word[]}[];
  defaultShots: () => Shot[];
  mergeShots: (tl?: Partial<Timeline> | null) => Shot[];
  graphicSegments: () => {id: string; label: string; start: number; end: number}[];
  inputProps: (timeline: Timeline) => Record<string, unknown>;
};
