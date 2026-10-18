import React, {createContext, useContext} from 'react';
import {Sequence, useCurrentFrame} from 'remotion';
import {FPS} from './theme';
type A = [number, number][];
const Ctx = createContext<{from: number; anchors: A}>({from: 0, anchors: []});
const fr = (s: number) => Math.round(s * FPS);
/** v3-absolute seconds */
export const useT3 = () => { const {from} = useContext(Ctx); return (from + useCurrentFrame()) / FPS; };
/** map v3 time -> v2 time via anchors [t3,t2] (slope 1 outside) */
export const warp = (t: number, a: A) => {
  if (!a.length) return t;
  if (t <= a[0][0]) return a[0][1] + (t - a[0][0]);
  for (let i = 0; i < a.length - 1; i++) { const [x0, y0] = a[i], [x1, y1] = a[i + 1]; if (t <= x1) return y0 + ((t - x0) / (x1 - x0)) * (y1 - y0); }
  const l = a[a.length - 1]; return l[1] + (t - l[0]);
};
export const useWarpT = () => { const {anchors} = useContext(Ctx); return warp(useT3(), anchors); };
export const Seq: React.FC<{a: number; b: number; anchors?: A; children: React.ReactNode}> = ({a, b, anchors = [], children}) =>
  <Sequence from={fr(a)} durationInFrames={Math.max(1, fr(b) - fr(a))} premountFor={20}><Ctx.Provider value={{from: fr(a), anchors}}>{children}</Ctx.Provider></Sequence>;
