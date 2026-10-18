import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import subs from './data/subs.json';
import {SUB_FONT} from './theme';

type Cue = {sid: string; start: number; end: number; text: string; segs: (string | null)[][]};
const CUES = subs as Cue[];

const Line: React.FC<{segs: (string | null)[][]; stroke: boolean}> = ({segs, stroke}) => (
  <div
    style={{
      position: 'absolute', left: 0, right: 0, top: 0, textAlign: 'center', whiteSpace: 'nowrap',
      fontFamily: `${SUB_FONT}, "Noto Sans CJK SC", sans-serif`, fontWeight: 700, fontSize: 66, lineHeight: '96px', letterSpacing: 2,
      color: stroke ? 'transparent' : '#FFFFFF',
      WebkitTextStroke: stroke ? '12px #000' : undefined,
    }}
  >
    {segs.map(([t, c], i) => (
      <span key={i} style={{color: stroke ? 'transparent' : (c ?? '#FFFFFF')}}>{t}</span>
    ))}
  </div>
);

export const Subtitles: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  const cue = CUES.find((c) => t >= c.start && t < c.end);
  if (!cue) return null;
  const local = t - cue.start;
  const pop = Math.min(1, local / 0.12);
  return (
    <div data-layer="subs" style={{position: 'absolute', left: 0, right: 0, top: 940, height: 96, transform: `scale(${0.94 + 0.06 * pop})`, transformOrigin: 'center center'}}>
      <Line segs={cue.segs} stroke />
      <Line segs={cue.segs} stroke={false} />
    </div>
  );
};
