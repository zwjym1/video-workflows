// 通用信息图组件库。颜色全部走主题变量（--m-* 画材 / --t-* 语义色），
// 所以同一个组件在三套皮肤下自动换色，不需要复制三份。
import React from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {useDesignFrame, Sfx} from './timeline/fps';
import {useBeatPulse} from './components/BeatSync';
import {prog, rand, enterSpec} from './lib/anim';
import {useTheme} from './theme/ThemeProvider';

/** 画材引用：P.ink -> 'var(--m-ink)' */
export {m, sv} from './theme/mat';
import {m, sv} from './theme/mat';
const s = sv;

/**
 * P = 画材（像素道具原色）+ 语义别名。
 * 像素皮肤下 text/plate/stroke 和 ink 是同一个值（diff 必须为 0）；
 * 深色皮肤下它们分开：正文是浅字、底板是深块、描边是灰蓝线。
 */
export const P = {
  // —— 画材 ——
  paper: m('paper'), dot: m('dot'), tokenBg: m('token-bg'), corner: m('corner'),
  ink: m('ink'), ink2: m('ink-2'), white: m('white'), black: m('black'),
  green: m('green'), heart: m('heart'), orange: m('orange'), orangeBar: m('orange-bar'),
  gold: m('gold'), goldDark: m('gold-dark'), teal: m('teal'), tealBright: m('teal-bright'),
  slate: m('slate'), grey: m('grey'), greyLight: m('grey-light'),
  darkBg: m('dark-bg'), darkGrid: m('dark-grid'), darkSurface: m('dark-surface'),
  panel: m('panel'), darkText: m('dark-text'), metal: m('metal'),
  cream: m('cream'), creamDark: m('cream-dark'), muted: m('muted'),
  wood: m('wood'), woodDark: m('wood-dark'), rail: m('rail'),
  hbmDark: m('hbm-dark'), hbmLight: m('hbm-light'),
  cellPale: m('cell-pale'), cellWarm: m('cell-warm'),
  termBg: m('term-bg'), hudBg: m('hud-bg'),
  dust1: m('dust-1'), dust2: m('dust-2'), dust3: m('dust-3'),
  // —— 语义别名（皮肤相关的角色） ——
  /** 正文/标题字色 */
  text: s('text'),
  /** 次级文字 */
  text2: s('text-2'),
  /** 实心底板（标题条、反色标签） */
  plate: s('plate'),
  /** 底板上的字 */
  onPlate: s('on-plate'),
  /** 图形轮廓线 */
  stroke: s('stroke'),
  /** 气泡底 / 气泡字 */
  bubble: s('bubble'),
  bubbleText: s('bubble-text'),
  /** 金色底上的字（像素皮肤下是墨色） */
  onGold: m('ink'),
  amber: m('ink'),
  /** 强调色 */
  accent: s('accent'), accent2: s('accent2'), accent3: s('accent3'),
  warn: s('warn'), success: s('success'),
  surface: s('surface'), surfaceAlt: s('surface-alt'), border: s('border'),
  bg: s('bg'), bgAlt: s('bg-alt'), grid: s('grid'),
  scrim: s('scrim'), overlay: s('overlay'),
};

/** 兼容旧引用：FONT 现在是变量引用（CSS 里 font-family 支持 var()） */
export const FONT = 'var(--t-font-display)';
export const FONT_BODY = 'var(--t-font-body)';
export const FONT_MONO = 'var(--t-font-mono)';

export const FontFace: React.FC = () => null; // 字体由 ThemeProvider 统一注入

/** 像素块投影：从皮肤读；像素皮肤下就是硬边 6px 投影 */
/** 皮肤阴影：n 是偏移档位（原像素设计里用 4/5/6/8/10 五档） */
export const useShadow = (n = 6) => {
  const {theme} = useTheme();
  return theme.shape.shadow(n);
};
/** 入场参数（设计帧 + easing）：按皮肤取，pixel 走 lib/anim 的覆盖表。
 *  改入场只改这一处，ElView / ItView / Pop 三处自动一致。 */
export const useEnter = () => {
  const {theme, enterFrames, easeEnter} = useTheme();
  return enterSpec(theme.id, enterFrames, easeEnter);
};

/** 组件外也能算（模块作用域的小部件工厂用） */
export const shadowOf = (theme: {shape: {shadow: (n: number) => string}}, n = 6) => theme.shape.shadow(n);

/* ------------------------------------------------------------------ *
 * 背景：按皮肤的 bgMode 分派
 * 像素 = 米白点阵 + 彩色像素屑；霓虹 = 深底 + 青紫光晕；纸本 = 米白 + 纸纹
 * ------------------------------------------------------------------ */
export const PaperBg: React.FC = () => {
  const {width, height} = useVideoConfig();
  const {theme, pixel} = useTheme();
  const f = useDesignFrame();
  const mode = theme.bgMode;
  if (mode === 'glass') return <GlassBg />;
  // 底纹极慢漂移：像素皮肤下按 2px 取整（像素块整数倍，不出中间色）。
  // 点阵周期 48，取模后完全无缝，四边不会露底——这是唯一既能整幅动、
  // 又不用 overscan、还不会糊像素的做法。
  const step = pixel ? 2 : 1;
  const ox = Math.round((f * 1.20) / step) * step % 48;
  const oy = Math.round((f * 0.68) / step) * step % 48;
  return (
    <AbsoluteFill style={{background: P.paper}}>
      <svg width={width} height={height} shapeRendering={pixel ? 'crispEdges' : 'auto'}>
        <defs><pattern id="dots" width="48" height="48" patternUnits="userSpaceOnUse"
          patternTransform={`translate(${ox} ${oy})`}><rect x="22" y="22" width="4" height="4" fill={P.dot} /></pattern></defs>
        <rect width={width} height={height} fill="url(#dots)" />
        {[0,1,2,3,4,5].map((i) => <rect key={i} x={rand(i)*width} y={rand(i+9)*height} width={12} height={12} fill={[P.dust1, P.dust2, P.dust3][i%3]} opacity={0.7} />)}
      </svg>
    </AbsoluteFill>
  );
};

/** 数据流扫光 —— 镜头内的「大面积、离散、可辨识」的运动
 * ------------------------------------------------------------------
 * 这里有一条实测出来的、反直觉的结论，必须写下来：
 *
 *   质检口径数的是「帧差曲线的局部极大值」，不是帧差总量。
 *   所以**匀速平移反而拿不到分**——一条光带匀速扫过时，
 *   每 0.125s 的帧差几乎是同一个常数（实测稳定在 0.8–0.9），
 *   一个峰都没有。观众看着是「有东西在动」，指标却是 0 事件。
 *   反过来，光带**一格一格跳**，每次跳都产生一个尖峰，事件立刻就数得出来。
 *
 * 这也正是「动作事件」这个词的本意：可辨识的一次动作，而不是持续流动。
 * 于是这里做成 CRT 式**逐格扫描**：
 *   - 横带每 15 帧（一拍）向下跳一格，跳 6 格为一轮，然后从顶部重来
 *   - 竖带每 22 帧向右跳一格，跳 7 格一轮（周期与横带互质，不同步）
 *   - 跳变时宽度同时收一下再展开，让「跳」这个动作看得见
 *   - 透明度封顶 0.07，只做「数据在走」的暗示，不抢主体
 *   - 整 8px 对齐，像素皮肤下边缘不会出现半像素
 * ------------------------------------------------------------------ */
export const BgSweep: React.FC<{seed?: number; dark?: boolean}> = ({seed = 0, dark}) => {
  const f = useDesignFrame();
  const {theme} = useTheme();
  const r = (k: number) => { const v = Math.sin(seed * 53.1 + k * 91.7) * 43758.5; return v - Math.floor(v); };
  const BEAT = 15;
  // 横带：每拍下一格，6 格一轮
  const hy = Math.floor((f + r(1) * BEAT) / BEAT) % 6;
  const hp = ((f + r(1) * BEAT) % BEAT) / BEAT;            // 0→1 格内进度
  const y = Math.round((hy * 190 + 40) / 8) * 8;
  const bandH = Math.round((64 + 26 * (1 - hp)) / 8) * 8;   // 落下时收窄，再展开
  // 竖带：每 22 帧一格，7 格一轮
  const vx = Math.floor((f + r(2) * 22) / 22) % 7;
  const vp = ((f + r(2) * 22) % 22) / 22;
  const x = Math.round((vx * 290 + 30) / 8) * 8;
  const bandW = Math.round((84 + 30 * (1 - vp)) / 8) * 8;
  // 颜色必须跟底色反着来：亮底（米白纸面）上用墨色，暗底上用冷白。
  // 之前亮底用金色 242,193,78 扫过 #F6F0E2 的纸面，几乎看不见（实测帧差 0.5），
  // 这是「同一套参数在两种底色上效果差 3 倍」的典型坑。
  const c = dark ? '200,225,255' : '30,27,37';
  const on = theme.shape.pixelated ? 1 : 1;
  return (
    <div style={{position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden', opacity: on}}>
      <div style={{position: 'absolute', left: 0, top: y - bandH / 2, width: 1920, height: bandH,
        background: `linear-gradient(180deg, rgba(${c},0) 0%, rgba(${c},.085) 35%, rgba(${c},.125) 50%, rgba(${c},.085) 65%, rgba(${c},0) 100%)`}} />
      <div style={{position: 'absolute', left: x - bandW / 2, top: 0, width: bandW, height: 1080,
        background: `linear-gradient(90deg, rgba(${c},0) 0%, rgba(${c},.07) 35%, rgba(${c},.10) 50%, rgba(${c},.07) 65%, rgba(${c},0) 100%)`}} />
    </div>
  );
};

/** 深色网格底（计算类场景） */
export const DarkGridBg: React.FC = () => {
  const {width, height} = useVideoConfig();
  const {theme, pixel} = useTheme();
  if (theme.bgModeDark === 'glass') return <GlassBg dark />;
  if (theme.bgModeDark === 'paper') return <PaperGridLight />;
  const f = useDesignFrame();
  const g = 82;
  // 网格整体极慢漂移，按 2px 取整，按 g 取模 → 无缝、不露边、不糊像素
  const step = pixel ? 2 : 1;
  // 2026-11-04 去掉网格持续漂移（原来 1.05px/帧 ≈ 31px/s，整块背景永远在爬）
  const ox = 0;
  const oy = 0;
  return (
    <AbsoluteFill style={{background: P.darkBg}}>
      <svg width={width} height={height} shapeRendering={pixel ? 'crispEdges' : 'auto'}>
        {Array.from({length: Math.ceil(width / g) + 1}).map((_, i) => <rect key={`v${i}`} x={i * g + ox - g} y={0} width={2} height={height} fill={P.darkGrid} />)}
        {Array.from({length: Math.ceil(height / g) + 1}).map((_, i) => <rect key={`h${i}`} x={0} y={i * g + oy - g} width={width} height={2} fill={P.darkGrid} />)}
      </svg>
    </AbsoluteFill>
  );
};

/** 纸本皮肤的「暗场」：仍然是纸，只是网格线更深 */
const PaperGridLight: React.FC = () => {
  const {width, height} = useVideoConfig();
  const g = 82;
  return (
    <AbsoluteFill style={{background: P.bgAlt}}>
      <svg width={width} height={height}>
        {Array.from({length: Math.ceil(width / g)}).map((_, i) => <rect key={`v${i}`} x={i * g} y={0} width={1.5} height={height} fill={P.darkGrid} />)}
        {Array.from({length: Math.ceil(height / g)}).map((_, i) => <rect key={`h${i}`} x={0} y={i * g} width={width} height={1.5} fill={P.darkGrid} />)}
      </svg>
    </AbsoluteFill>
  );
};

/** 霓虹/玻璃背景：深蓝黑 + 青紫双光晕 + 细网格 */
export const GlassBg: React.FC<{dark?: boolean}> = ({dark}) => {
  const {width, height} = useVideoConfig();
  const {theme} = useTheme();
  const f = useDesignFrame();
  const t = theme.colors;
  const drift = 0; // 2026-11-04 光晕缓慢位移去掉
  return (
    <AbsoluteFill style={{background: dark ? t.bgAlt : t.bg}}>
      <div style={{position: 'absolute', inset: 0,
        background: `radial-gradient(900px 700px at ${26 + drift / 20}% 22%, ${t.accent}33, transparent 62%),
                     radial-gradient(800px 680px at ${76 - drift / 24}% 74%, ${t.accent2}2e, transparent 60%),
                     radial-gradient(600px 500px at 50% 105%, ${t.accent3}22, transparent 70%)`}} />
      <svg width={width} height={height}>
        <defs><pattern id="gg" width="64" height="64" patternUnits="userSpaceOnUse">
          <path d="M64 0H0V64" fill="none" stroke={t.grid} strokeWidth="1" opacity={0.5} />
        </pattern></defs>
        <rect width={width} height={height} fill="url(#gg)" opacity={0.55} />
      </svg>
    </AbsoluteFill>
  );
};

/** 章节卡底：星空 → 极光 → 印刷横线 */
export const StarBg: React.FC = () => {
  const {width, height} = useVideoConfig();
  const f = useDesignFrame();
  const {theme, pixel} = useTheme();
  const mode = theme.bgModeStar;
  if (mode === 'aurora') {
    const t = theme.colors;
    return (
      <AbsoluteFill style={{background: t.bgAlt}}>
        <div style={{position: 'absolute', inset: 0, background:
          `radial-gradient(1100px 760px at 22% 12%, ${t.accent}3d, transparent 60%),
           radial-gradient(900px 700px at 84% 84%, ${t.accent2}33, transparent 62%),
           linear-gradient(160deg, ${t.bg} 0%, ${t.bgAlt} 100%)`}} />
        <svg width={width} height={height}>
          {Array.from({length: 60}).map((_, i) => {
            const x = rand(i) * width, y = rand(i + 100) * height;
            const tw = 0.6;
            return <circle key={i} cx={x} cy={y} r={i % 9 === 0 ? 2.6 : 1.4} fill={i % 7 === 0 ? t.accent2 : t.accent} opacity={tw} />;
          })}
        </svg>
      </AbsoluteFill>
    );
  }
  if (mode === 'rules') {
    return <AbsoluteFill style={{background: P.paper}}>
      <svg width={width} height={height}>
        {Array.from({length: 22}).map((_, i) => <rect key={i} x={0} y={i * 52 + 30} width={width} height={1} fill={P.dot} opacity={0.85} />)}
      </svg>
    </AbsoluteFill>;
  }
  return (
    <AbsoluteFill style={{background: `linear-gradient(${P.ink2}, ${P.stroke})`}}>
      <svg width={width} height={height} shapeRendering={pixel ? 'crispEdges' : 'auto'}>
        {Array.from({length: 70}).map((_, i) => {
          const sz = rand(i * 3) > 0.85 ? 6 : 3;
          const tw = 0.7;
          return <rect key={i} x={rand(i) * width} y={rand(i + 100) * height} width={sz} height={sz} fill={i % 7 === 0 ? P.gold : m('star-dim')} opacity={tw} />;
        })}
      </svg>
    </AbsoluteFill>
  );
};

/** 全局质感层：噪点 + 暗角 + 扫描线。像素皮肤下全为 0，不产生任何像素 */
export const Texture: React.FC = () => {
  const {theme} = useTheme();
  const f = useDesignFrame();
  const {grainAmount, vignette, scanlines} = theme.texture;
  if (!grainAmount && !vignette && !scanlines) return null;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {vignette > 0 && <div style={{position: 'absolute', inset: 0, background: `radial-gradient(ellipse at center, transparent 42%, rgba(0,0,0,${0.55 * vignette}) 100%)`}} />}
      {scanlines > 0 && <div style={{position: 'absolute', inset: 0, backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,.35) 0px, rgba(0,0,0,.35) 1px, transparent 1px, transparent 3px)', opacity: scanlines}} />}
      {grainAmount > 0 && <div style={{position: 'absolute', inset: -40, opacity: grainAmount, mixBlendMode: 'overlay',
        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' seed='${Math.floor(f / 3) % 7}'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)'/%3E%3C/svg%3E")`,
        backgroundSize: '160px 160px'}} />}
    </AbsoluteFill>
  );
};

/** 四角取景框 + 顶部进度条 + 右上 HUD */
export const Frame: React.FC<{progress: number; count: number; name: string; dark?: boolean}> = ({progress, count, name, dark}) => {
  const {width, height} = useVideoConfig();
  const {theme} = useTheme();
  const beat = useBeatPulse(1, 6, true);
  const rp = beat * theme.rhythm;
  const arm = 0.03 * width, mm = 0.022 * width, t = theme.shape.pixelated ? 6 : 3;
  const c = dark ? m('corner-dark') : P.corner;
  const L = (x: number, y: number, sx: number, sy: number) => (
    <g key={`${x}${y}`}><rect x={sx > 0 ? x : x - arm} y={sy > 0 ? y : y - t} width={arm} height={t} fill={c} /><rect x={sx > 0 ? x : x - t} y={sy > 0 ? y : y - arm} width={t} height={arm} fill={c} /></g>
  );
  return (
    <AbsoluteFill>
      <svg width={width} height={height} shapeRendering={theme.shape.pixelated ? 'crispEdges' : 'auto'}>
        {L(mm, mm + 20, 1, 1)}{L(width - mm, mm + 20, -1, 1)}{L(mm, height - mm, 1, -1)}{L(width - mm, height - mm, -1, -1)}
        <rect x={0} y={0} width={width} height={height * 0.008} fill={P.plate} />
        <rect x={0} y={0} width={width * progress} height={height * 0.008} fill={P.green} />
        {rp > 0.02 && <>
          <rect x={0} y={0} width={width * progress} height={height * 0.008 + rp * 14} fill={P.accent} opacity={rp * 0.55} />
          <rect x={0} y={height * 0.008} width={width * progress} height={rp * 26} fill={P.accent} opacity={rp * 0.18} />
        </>}
      </svg>
      <div style={{position: 'absolute', right: width * 0.021, top: height * 0.012, background: P.hudBg, color: P.onPlate, fontFamily: FONT, fontSize: height * 0.036, padding: `${height*0.008}px ${height*0.016}px`, display: 'flex', gap: 14, alignItems: 'center', boxShadow: theme.shape.shadow(4), borderRadius: theme.shape.radiusSm, border: theme.shape.pixelated ? undefined : `1px solid ${P.border}`, backdropFilter: theme.texture.blurGlass ? `blur(${theme.texture.blurGlass}px)` : undefined}}>
        <span style={{color: P.heart, letterSpacing: 2, transform: `scale(${1 + rp * 0.22})`, display: 'inline-block', textShadow: rp > 0.01 ? `0 0 ${rp * 16}px ${P.heart}` : undefined}}>♥♥♥</span>
        <span style={{color: P.gold}}>■×{String(count).padStart(2, '0')}</span>
        <span>{name}</span>
      </div>
    </AbsoluteFill>
  );
};

/** 底部字幕：深底、两端强调竖条，keys 内的词变色 */
export const Sub: React.FC<{text: string; keys?: string[]}> = ({text, keys = []}) => {
  const {height} = useVideoConfig();
  const {theme} = useTheme();
  // 卡点：字幕条的强调竖条随拍跳一下。theme.rhythm=0（像素皮肤）时 p 恒为 0，画面零变化。
  const beat = useBeatPulse(1, 6);
  const rp = beat * theme.rhythm;
  const parts: {s: string; k: boolean}[] = [];
  let rest = text;
  while (rest.length) {
    let hit = -1, key = '';
    keys.forEach((k) => { const i = rest.indexOf(k); if (i >= 0 && (hit < 0 || i < hit)) { hit = i; key = k; } });
    if (hit < 0) { parts.push({s: rest, k: false}); break; }
    if (hit > 0) parts.push({s: rest.slice(0, hit), k: false});
    parts.push({s: key, k: true}); rest = rest.slice(hit + key.length);
  }
  // 卡点竖条：每拍从 1.0 弹到 2.1 倍高，并带一段外发光
  const barH = height * 0.03 * (1 + rp * 1.1);
  const bar = <span style={{display: 'inline-block', width: 8, height: barH, background: P.orangeBar, borderRadius: theme.shape.pixelated ? 0 : 4, boxShadow: rp > 0.02 ? `0 0 ${rp * 26}px ${P.orangeBar}, 0 0 ${rp * 56}px ${P.accent}88` : undefined, transform: `scaleY(${1 + rp * 0.2})`}} />;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: height * 0.889, display: 'flex', justifyContent: 'center'}}>
      <div style={{background: P.overlay, color: P.onPlate, fontFamily: FONT, fontSize: height * 0.04, height: height * 0.075, display: 'flex', alignItems: 'center', gap: 22, padding: '0 22px', transform: `translateY(${-rp * 5}px) scale(${1 + rp * 0.012})`,
        boxShadow: rp > 0.02 ? `${theme.shape.shadow(5)}, 0 0 ${rp * 44}px ${P.accent}77` : theme.shape.shadow(5), borderRadius: theme.shape.radiusMd, border: theme.shape.pixelated ? undefined : `1px solid ${P.border}`, backdropFilter: theme.texture.blurGlass ? `blur(${theme.texture.blurGlass}px)` : undefined}}>
        {bar}<span>{parts.map((p, i) => <span key={i} style={{color: p.k ? P.gold : P.onPlate}}>{p.s}</span>)}</span>{bar}
      </div>
    </div>
  );
};

/** 弹入：从下方 40px + 缩放回弹。时长/easing 从皮肤读 */
export const Pop: React.FC<{at: number; x: number; y: number; children: React.ReactNode; dur?: number; sfx?: boolean}> = ({at, x, y, children, dur, sfx = true}) => {
  const f = useDesignFrame();
  const enter = useEnter();
  const d = dur ?? enter.frames;
  const p = prog(f, at, d, enter.ease);
  return (
    <>
      {sfx && <Sfx at={at} dur={6} file="sfx/pop.wav" volume={0.12} />}
      {f >= at && <div style={{position: 'absolute', left: x, top: y, transform: `translateY(${(1 - p) * 40}px) scale(${0.6 + 0.4 * p})`, opacity: Math.min(1, p * 2), transformOrigin: 'center bottom'}}>{children}</div>}
    </>
  );
};

export const Label: React.FC<{text: string; size?: number; bg?: string; color?: string}> = ({text, size = 40, bg = P.plate, color = P.onPlate}) => {
  const {theme} = useTheme();
  return (
    <div style={{background: bg, color, fontFamily: FONT, fontSize: size, padding: `${size * 0.18}px ${size * 0.4}px`, boxShadow: theme.shape.shadow(5), whiteSpace: 'nowrap', borderRadius: theme.shape.radiusSm, border: theme.shape.pixelated ? undefined : `1px solid ${P.border}`}}>{text}</div>
  );
};

export const Token: React.FC<{ch: string; size?: number; hot?: boolean; fill?: string}> = ({ch, size = 76, hot, fill}) => {
  const {theme} = useTheme();
  return (
    <div style={{width: size, height: size, background: fill ?? (hot ? P.gold : P.tokenBg), border: `${theme.shape.borderWidth}px solid ${P.stroke}`, fontFamily: FONT, fontSize: size * 0.55, display: 'flex', alignItems: 'center', justifyContent: 'center', color: P.text, boxShadow: theme.shape.shadow(5), borderRadius: theme.shape.radiusSm}}>{ch}</div>
  );
};

/** 像素 GPU 卡（自绘） */
export const Gpu: React.FC<{w?: number; label?: string}> = ({w = 260, label}) => {
  const h = w * 0.42;
  return (
    <div style={{position: 'relative', width: w, height: h + 30}}>
      <svg width={w} height={h} shapeRendering="crispEdges">
        <rect x={0} y={0} width={w} height={h} fill={P.stroke} /><rect x={8} y={8} width={w - 16} height={h - 16} fill={P.panel} />
        {[0.28, 0.7].map((cx, i) => (<g key={i}><rect x={w * cx - h * 0.3} y={h * 0.2} width={h * 0.6} height={h * 0.6} fill={P.stroke} /><rect x={w * cx - h * 0.2} y={h * 0.3} width={h * 0.4} height={h * 0.4} fill={P.orange} /><rect x={w * cx - 4} y={h * 0.3} width={8} height={h * 0.4} fill={P.stroke} /></g>))}
        {Array.from({length: 10}).map((_, i) => <rect key={i} x={20 + i * (w - 40) / 10} y={h - 8} width={(w - 40) / 14} height={8} fill={P.gold} />)}
      </svg>
      {label && <div style={{position: 'absolute', top: h + 4, width: w, textAlign: 'center', fontFamily: FONT, fontSize: 28, color: P.text}}>{label}</div>}
    </div>
  );
};

/** 问号方块 */
export const QBlock: React.FC<{size?: number}> = ({size = 80}) => {
  const f = useDesignFrame();
  const {theme} = useTheme();
  return <div style={{width: size, height: size, background: P.gold, border: `${theme.shape.borderWidth}px solid ${P.stroke}`, fontFamily: FONT, fontSize: size * 0.6, display: 'flex', alignItems: 'center', justifyContent: 'center', color: m('qmark-ink'), boxShadow: theme.shape.shadow(5), borderRadius: theme.shape.radiusSm}}>?</div>;
};
