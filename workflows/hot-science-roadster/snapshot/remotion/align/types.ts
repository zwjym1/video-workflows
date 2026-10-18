import type React from 'react';
export type Shot = {id: string; label?: string; src: string; start: number; end: number; in: number; rate: number};
export type Timeline = {version: number; composition?: string; fps?: number; shots: Shot[]; audio?: any};
export type Word = {text: string; start: number; end: number};
export type AlignProject = {
  title: string; composition: string; component: React.ComponentType<any>;
  fps: number; width: number; height: number; durationInFrames: number;
  audio: string; // narration file, relative to publicDir
  sentences: {i: number; text: string; start: number; end: number; words: Word[]}[];
  defaultShots: () => Shot[];
  mergeShots: (tl?: Partial<Timeline> | null) => Shot[];
  graphicSegments: () => {id: string; label: string; start: number; end: number}[];
  // optional audio mixer (saved as "audio" in the timeline JSON)
  defaultAudio?: () => AudioMix; mergeAudio?: (tl: any) => AudioMix; bgmGain?: (t: number, mix: AudioMix) => number;
  inputProps: (timeline: Timeline) => Record<string, unknown>;
};
export type AudioMix = {voiceDb: number; sfxDb: number; bgmDb: number; duckDb: number; bgmEnv: {t: number; db: number}[]; lufs: number};
