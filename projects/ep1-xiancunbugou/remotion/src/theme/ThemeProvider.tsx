/**
 * ThemeProvider
 * ------------------------------------------------------------------
 * 两套通道：
 *   1) CSS 自定义属性 --t-<key>：给颜色用。绘制时求值，所以模块作用域创建的小部件也能跟着换皮。
 *   2) React context：给数值/时长/easing/字体规格用。组件里 useTheme() 直接拿。
 *
 * 帧率归一：context 暴露 f30() 和 msToFrames()，把所有「帧」参数换算到当前 fps。
 * 设计基准是 30fps；60fps 时同一秒对应两倍帧数，所以所有硬编码帧数都要过 f30()。
 */
import React from 'react';
import {staticFile, useVideoConfig} from 'remotion';
import type {Theme} from './types';
import {SKINS, SkinId} from './skins';
import {alpha} from './color';
import {materialVars} from './materials';

export type ThemeCtx = {
  theme: Theme;
  /** 设计稿帧数（30fps 基准）→ 当前 fps 帧数 */
  f30: (frames: number) => number;
  /** 毫秒 → 当前 fps 帧数（只给真正的 Sequence 用） */
  msToFrames: (ms: number) => number;
  /**
   * 入场时长，单位 = 设计帧（30fps 坐标）。
   * 因为所有动画都在 useDesignFrame() 的坐标系里跑，
   * 时长必须同单位，否则 60fps 下动画会变成两倍长。
   */
  enterFrames: number;
  /** 错帧间隔，单位 = 设计帧 */
  staggerFrames: number;
  /** 解析后的入场 easing 函数 */
  easeEnter: (t: number) => number;
  /** 解析后的强调 easing 函数 */
  easeEmphasis: (t: number) => number;
  /** 皮肤是否像素风（决定 imageRendering / shapeRendering） */
  pixel: boolean;
};

export const ThemeContext = React.createContext<ThemeCtx | null>(null);

/** 把 cubic-bezier(x1,y1,x2,y2) 解析成 f(t) */
export const parseCubicBezier = (css: string): ((t: number) => number) => {
  const m = /cubic-bezier\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)/.exec(css);
  if (!m) return (t) => t;
  const [x1, y1, x2, y2] = m.slice(1).map(Number);
  // 牛顿迭代求 x(t)=p 的 t，再取 y
  const bx = (t: number) => 3 * (1 - t) * (1 - t) * t * x1 + 3 * (1 - t) * t * t * x2 + t * t * t;
  const by = (t: number) => 3 * (1 - t) * (1 - t) * t * y1 + 3 * (1 - t) * t * t * y2 + t * t * t;
  const dbx = (t: number) => 3 * (1 - t) * (1 - t) * x1 + 6 * (1 - t) * t * (x2 - x1) + 3 * t * t * (1 - x2);
  return (p: number) => {
    if (p <= 0) return 0;
    if (p >= 1) return 1;
    let t = p;
    for (let i = 0; i < 8; i++) {
      const x = bx(t) - p;
      if (Math.abs(x) < 1e-6) break;
      const d = dbx(t);
      if (Math.abs(d) < 1e-6) break;
      t -= x / d;
      t = Math.max(0, Math.min(1, t));
    }
    return by(t);
  };
};

const FALLBACK: Record<string, (s: number) => string> = {};
/** 生成 --t-* 变量表 */
export const themeVars = (theme: Theme): React.CSSProperties => {
  const vars: Record<string, string> = {};
  const push = (k: string, v: string) => { vars[`--t-${k}`] = v; };
  const c = theme.colors;
  push('bg', c.bg); push('bg-alt', c.bgAlt); push('grid', c.grid);
  push('surface', c.surface); push('surface-alt', c.surfaceAlt);
  push('border', c.border); push('stroke', c.stroke);
  push('text', c.textPrimary); push('text-2', c.textSecondary); push('text-inv', c.textInverse);
  push('accent', c.accent); push('accent2', c.accent2); push('accent3', c.accent3);
  push('warn', c.warn); push('success', c.success);
  push('plate', c.plate); push('on-plate', c.onPlate);
  push('overlay', c.overlay); push('scrim', c.scrim);
  push('bubble', c.bubble); push('bubble-text', c.bubbleText);
  // 阴影按偏移档位导出：模块作用域的小部件工厂靠这些变量取阴影
  [4, 5, 6, 8, 10].forEach((n) => push(`shadow-${n}`, theme.shape.shadow(n)));
  push('shadow-6-a20', theme.shape.shadow(6, 0.2));
  push('shadow-8-a20', theme.shape.shadow(8, 0.2));
  push('shadow-deep-10', theme.shape.shadowDeep(10));
  push('shadow-accent-8', theme.shape.shadowAccent(8));
  push('shadow', theme.shape.shadow(6));
  push('shadow-lg', theme.shape.shadow(10));
  push('shadow-accent', theme.shape.shadowAccent(6));
  // 画材（legacy）全部导出
  Object.entries(c.legacy).forEach(([k, v]) => push(k, v));
  // 常用衍生：描边色的半透明版本、墨色的半透明版本
  push('ink-a18', alphaSafe(c.legacy.ink, 0.18));
  push('ink-a20', alphaSafe(c.legacy.ink, 0.2));
  push('ink-a22', alphaSafe(c.legacy.ink, 0.22));
  push('ink-a92', alphaSafe(c.legacy.ink, 0.92));
  push('paper-a55', alphaSafe(theme.colors.bgAlt, 0.55));
  // 画材（109 个像素道具用色）
  Object.assign(vars, materialVars(theme.materials));
  // 字体（组件里读 var(--t-font-display) 而不是写死字体名）
  push('font-display', theme.type.fontDisplay.family);
  push('font-body', theme.type.fontBody.family);
  push('font-mono', theme.type.fontMono.family);
  return vars as React.CSSProperties;
};

/** 生成 @font-face 声明 */
export const fontFaceCss = (theme: Theme) => theme.type.fontFaces
  .map((f) => `@font-face{font-family:"${f.family}";src:url("${staticFile(f.file)}");font-display:block;}`)
  .join('');

const alphaSafe = (hex: string, a: number) => {
  if (!hex.startsWith('#') || (hex.length !== 4 && hex.length !== 7)) return hex;
  try { return alpha(hex, a); } catch { return hex; }
};

export const ThemeProvider: React.FC<{skin?: SkinId | Theme; children: React.ReactNode}> = ({skin = 'pixel', children}) => {
  const {fps} = useVideoConfig();
  const theme: Theme = typeof skin === 'string' ? SKINS[skin] : skin;
  const f30 = React.useCallback((frames: number) => Math.round((frames * fps) / 30), [fps]);
  const msToFrames = React.useCallback((ms: number) => Math.round((ms / 1000) * fps), [fps]);
  const easeEnter = React.useMemo(() => theme.motion.easeEnterFn ?? parseCubicBezier(theme.motion.easeEnter), [theme]);
  const easeEmphasis = React.useMemo(() => theme.motion.easeEmphasisFn ?? parseCubicBezier(theme.motion.easeEmphasis), [theme]);
  // 毫秒 → 设计帧（固定 30fps 基准，与 useDesignFrame 同单位）
  const msToDesignFrames = (ms: number) => Math.max(1, Math.round((ms / 1000) * 30));
  const ctx: ThemeCtx = {
    theme, f30, msToFrames,
    enterFrames: msToDesignFrames(theme.motion.enterMs),
    staggerFrames: msToDesignFrames(theme.motion.staggerMs),
    easeEnter, easeEmphasis,
    pixel: theme.shape.pixelated,
  };
  return (
    <ThemeContext.Provider value={ctx}>
      <style>{fontFaceCss(theme)}</style>
      <div style={{...themeVars(theme), width: '100%', height: '100%'}}>{children}</div>
    </ThemeContext.Provider>
  );
};

/** 无 Provider 时回落到像素皮肤：方便老组件单独渲染、也方便 still 对比 */
const defaultCtx = (fps = 30): ThemeCtx => {
  const theme = SKINS.pixel;
  return {
    theme,
    f30: (frames) => Math.round((frames * fps) / 30),
    msToFrames: (ms) => Math.round((ms / 1000) * fps),
    enterFrames: 8, staggerFrames: 6,
    easeEnter: theme.motion.easeEnterFn!,
    easeEmphasis: parseCubicBezier(theme.motion.easeEmphasis),
    pixel: true,
  };
};

export const useTheme = (): ThemeCtx => React.useContext(ThemeContext) ?? defaultCtx();

/** 直接取当前皮肤（常用） */
export const useSkin = () => useTheme().theme;
/** 帧率归一：把 30fps 设计帧换算到当前 fps */
export const useF30 = () => useTheme().f30;
