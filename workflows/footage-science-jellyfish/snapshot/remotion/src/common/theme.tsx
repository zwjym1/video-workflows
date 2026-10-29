// EP-20261021-03 视觉常量与通用小组件（御前奏折 × 机密简报：墨黑底、宣纸白、朱砂红、鎏金）
import React from 'react';
import {Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
export const W = 1080, H = 1920, FPS = 30;
export const INK = '#0c0d12', PAPER = '#efe8da', CINNABAR = '#c8352b', GOLD = '#d9a441', CYAN = '#6fd3ff', GREEN = '#5fd38a', RED = '#ff5a4e', GREY = '#8a8f9c';
// 2026-10-22：中文字体统一为品牌字 Smiley Sans（得意黑），缺字回落 Noto
export const NOTO = "'Smiley', 'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif";
export const SMILEY = "'Smiley', 'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif";
export const fontCss = `@font-face{font-family:'Smiley';src:url(${staticFile('fonts/SmileySans-Oblique.ttf')}) format('truetype');}*{font-synthesis:none;}`;
export const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
export const c01 = (x: number) => Math.max(0, Math.min(1, x));
export const ease = (x: number) => { const t = c01(x); return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
export const easeOut = (x: number) => 1 - Math.pow(1 - c01(x), 3);
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
/** 区间进度：f 在 [a,b] 帧之间 0→1 */
export const win = (f: number, a: number, b: number) => c01((f - a) / Math.max(1, b - a));

/** 右上角「丞」朱印角标（与往期同一套：盖下后停在右上角） */
export const BrandBadge: React.FC<{startAt?: number}> = ({startAt = 4}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const st = spring({frame: f - startAt, fps, config: {damping: 10, stiffness: 210}});
  const scale = f < startAt ? 0 : interpolate(st, [0, 1], [2.4, 1]);
  const op = f < startAt ? 0 : interpolate(f, [startAt, startAt + 4, startAt + 22, startAt + 36], [0, 1, 1, 0.6], clamp);
  return <div data-layer="brand" style={{position: 'absolute', right: 40, top: 34, width: 78, height: 78, opacity: op, transform: `scale(${scale}) rotate(${interpolate(st, [0, 1], [-18, -6])}deg)`, zIndex: 70}}>
    <Img src={staticFile('brand/seal_t.png')} style={{width: 78, height: 78, filter: 'drop-shadow(0 3px 6px rgba(0,0,0,.5))'}} />
  </div>;
};

/** 左上角常驻小字：示意声明（内容随镜头切换） */
export const CornerLabel: React.FC<{text: string; opacity?: number}> = ({text, opacity = 1}) => (
  <div data-layer="corner" style={{position: 'absolute', left: 36, top: 172, maxWidth: 1008, whiteSpace: 'pre', opacity, zIndex: 60, fontFamily: NOTO, fontWeight: 700, fontSize: 36, lineHeight: 1.3, color: 'rgba(239,232,218,.82)', background: 'rgba(8,8,12,.55)', padding: '6px 14px', borderRadius: 8, borderLeft: `4px solid ${CINNABAR}`}}>{text}</div>
);

// v3：署名移到画面高 9–12%（y≈172–230），字高 36 px（返修单 P1）
/** 画面内标注胶囊（数值/来源），跟随出现 */
export const Tag: React.FC<{x: number; y: number; text: string; color?: string; size?: number; p?: number; anchor?: 'left' | 'center' | 'right'}> = ({x, y, text, color = PAPER, size = 34, p = 1, anchor = 'center'}) => {
  const tx = anchor === 'center' ? '-50%' : anchor === 'right' ? '-100%' : '0';
  return <div style={{position: 'absolute', left: x, top: y, transform: `translate(${tx},-50%) scale(${0.85 + 0.15 * easeOut(p)})`, opacity: easeOut(p), fontFamily: NOTO, fontWeight: 700, fontSize: size, color, whiteSpace: 'nowrap', background: 'rgba(8,8,12,.66)', padding: '6px 16px', borderRadius: 12, border: '1px solid rgba(239,232,218,.25)', zIndex: 40}}>{text}</div>;
};

/** 深色背景：微网格 + 暗角（机密简报感） */
export const BriefBg: React.FC<{tint?: string}> = ({tint = '#141826'}) => (
  <div style={{position: 'absolute', inset: 0, background: `radial-gradient(ellipse at 50% 42%, ${tint} 0%, ${INK} 72%)`}}>
    <svg width={W} height={H} style={{position: 'absolute', inset: 0, opacity: 0.08}}>
      {Array.from({length: 28}).map((_, i) => <line key={'v' + i} x1={i * 40} y1={0} x2={i * 40} y2={H} stroke={PAPER} strokeWidth={1} />)}
      {Array.from({length: 49}).map((_, i) => <line key={'h' + i} x1={0} y1={i * 40} x2={W} y2={i * 40} stroke={PAPER} strokeWidth={1} />)}
    </svg>
  </div>
);
