import React from 'react';
import {interpolate, Easing, useCurrentFrame, useVideoConfig, spring} from 'remotion';
export const FPS = 30;
export const F = '"Noto Sans CJK SC","Noto Sans SC",sans-serif';
export const C = {cyan: '#4fd1ff', red: '#ff3b4f', amber: '#ffb347', white: '#f5f7fa', glass: 'rgba(10,14,20,0.74)', dim: 'rgba(255,255,255,0.62)'};
const cl = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
export const io = Easing.inOut(Easing.cubic);
/** eased 0..1 between absolute seconds a..b */
export const e = (t: number, a: number, b: number, ease = io) => interpolate(t, [a, b], [0, 1], {...cl, easing: ease});
export const lin = (t: number, a: number[], b: number[]) => interpolate(t, a, b, cl);
export const useT = (offset = 0) => { const f = useCurrentFrame(); return offset + f / FPS; };
/** spring pop (0..~1.05..1) starting at absolute time `at` */
export const usePop = (t: number, at: number) => {
  const fr = Math.round((t - at) * FPS);
  return fr < 0 ? 0 : spring({frame: fr, fps: FPS, config: {damping: 13, stiffness: 160, mass: 0.7}});
};

export const Credit: React.FC<{text?: string}> = ({text = '画面来源：Tesla'}) => (
  <div style={{position: 'absolute', top: 34, left: 44, fontFamily: F, fontSize: 24, color: C.dim, letterSpacing: 1, textShadow: '0 2px 6px #000', zIndex: 50}}>{text}</div>
);

export const Chip: React.FC<{text: string; sub?: string; accent?: string; o: number}> = ({text, sub, accent = C.red, o}) => (
  <div style={{position: 'absolute', top: 34, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: o, transform: `translateY(${(1 - o) * -14}px)`, zIndex: 45}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '10px 26px 10px 18px', borderRadius: 10, background: C.glass, border: '1px solid rgba(255,255,255,0.14)', backdropFilter: 'blur(6px)'}}>
      <span style={{width: 6, height: 30, borderRadius: 3, background: accent}} />
      <span style={{fontFamily: F, fontWeight: 900, fontSize: 36, color: C.white, letterSpacing: 2}}>{text}</span>
    </div>
    {sub ? <div style={{marginTop: 8, fontFamily: F, fontSize: 22, color: C.dim, letterSpacing: 2}}>{sub}</div> : null}
  </div>
);

/** ring + leader line + label anchored at (x,y) */
export const Callout: React.FC<{x: number; y: number; label: string; color?: string; p: number; dx?: number; dy?: number; r?: number; out?: number}> = ({x, y, label, color = C.cyan, p, dx = 160, dy = -110, r = 46, out = 1}) => {
  if (p <= 0.001 || out <= 0.001) return null;
  const lx = x + dx, ly = y + dy;
  const lineP = Math.min(1, p * 1.3);
  const lab = Math.max(0, Math.min(1, (p - 0.35) / 0.65));
  const left = dx < 0;
  return (
    <div style={{position: 'absolute', inset: 0, opacity: out, zIndex: 40, pointerEvents: 'none'}}>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <circle cx={x} cy={y} r={r * (0.6 + 0.4 * p)} fill="none" stroke={color} strokeWidth={3} opacity={Math.min(1, p)} />
        <circle cx={x} cy={y} r={r * (1 + 0.6 * (1 - p))} fill="none" stroke={color} strokeWidth={1.5} opacity={0.5 * (1 - Math.min(1, p))} />
        <circle cx={x} cy={y} r={5} fill={color} />
        <line x1={x + (dx / Math.hypot(dx, dy)) * r} y1={y + (dy / Math.hypot(dx, dy)) * r} x2={x + (dx / Math.hypot(dx, dy)) * r + (lx - x - (dx / Math.hypot(dx, dy)) * r) * lineP} y2={y + (dy / Math.hypot(dx, dy)) * r + (ly - y - (dy / Math.hypot(dx, dy)) * r) * lineP} stroke={color} strokeWidth={2} />
      </svg>
      <div style={{position: 'absolute', top: ly - 28, left: left ? undefined : lx, right: left ? 1920 - lx : undefined, opacity: lab, transform: `translateX(${(1 - lab) * (left ? 16 : -16)}px)`,
        padding: '8px 20px', borderRadius: 8, background: C.glass, borderLeft: left ? undefined : `4px solid ${color}`, borderRight: left ? `4px solid ${color}` : undefined,
        fontFamily: F, fontWeight: 800, fontSize: 34, color: C.white, whiteSpace: 'nowrap', boxShadow: '0 6px 24px rgba(0,0,0,0.4)'}}>{label}</div>
    </div>
  );
};

export const NumberPop: React.FC<{x: number; y: number; big: string; label?: string; color?: string; p: number; align?: 'left' | 'center'}> = ({x, y, big, label, color = C.amber, p, align = 'left'}) => {
  if (p <= 0.001) return null;
  return (
    <div style={{position: 'absolute', left: align === 'center' ? x - 600 : x, width: align === 'center' ? 1200 : undefined, top: y, textAlign: align, opacity: Math.min(1, p * 1.5), transform: `scale(${0.7 + 0.3 * p})`, transformOrigin: align === 'center' ? 'center' : 'left center', zIndex: 42}}>
      <div style={{fontFamily: F, fontWeight: 900, fontSize: 150, lineHeight: 1, color, textShadow: `0 0 30px ${color}66, 0 6px 0 rgba(0,0,0,0.5)`, letterSpacing: -2}}>{big}</div>
      {label ? <div style={{marginTop: 10, fontFamily: F, fontWeight: 700, fontSize: 36, color: C.white, letterSpacing: 2, textShadow: '0 2px 8px #000'}}>{label}</div> : null}
    </div>
  );
};

export const SpeedLines: React.FC<{o: number; t: number; dir?: 1 | -1}> = ({o, t, dir = -1}) => {
  if (o <= 0.01) return null;
  const lines = Array.from({length: 18}, (_, i) => {
    const y = 80 + ((i * 397) % 920); const len = 220 + ((i * 131) % 380); const sp = 2600 + ((i * 53) % 1400);
    const x = ((((i * 733) + t * sp) % 2600) - 340);
    return <line key={i} x1={dir < 0 ? 1920 - x : x} y1={y} x2={dir < 0 ? 1920 - x + len : x - len} y2={y} stroke="white" strokeWidth={i % 3 ? 2 : 3} opacity={0.18 + (i % 4) * 0.06} strokeLinecap="round" />;
  });
  return <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, opacity: o, zIndex: 20, mixBlendMode: 'screen'}}>{lines}</svg>;
};

export const Vignette: React.FC<{o?: number}> = ({o = 1}) => (
  <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.55) 100%)', opacity: o, zIndex: 15}} />
);
