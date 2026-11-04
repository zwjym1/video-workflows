/**
 * neonGlass —— 深色玻璃拟态 / 霓虹科技风。
 * 深蓝黑底 + 青紫渐变光晕 + 半透明毛玻璃卡片 + 细描边 + 大圆角 + 大字号 + 极简。
 *
 * 像素道具的「画材色」不是手调第二套，而是从 pixelDark 的画材按一条明暗+色相曲线推出来的：
 * 把纸面压到深底、把墨线提成描边、把暖橙金换成霓虹青紫，这样显卡/仓库/机柜不用重画也能换皮。
 */
import type {Theme} from '../types';
import {remap} from '../color';
import {deriveMaterials} from '../materials';

const light = (l: number) => {
  // 深色皮肤：把中性明暗整体映射到 0.06–0.86，暗的留暗、亮的变发光体
  const t = Math.max(0, Math.min(1, l));
  return 0.055 + Math.pow(t, 0.72) * 0.80;
};
const spec = {
  light,
  hueShift: null as number | null,
  huePull: 0.62,
  hueTarget: 194,     // 青
  sat: (s: number) => Math.min(1, s * 1.28 + 0.06),
  greyBelow: 0.16,
  tintGreys: {h: 222, s: 0.30},
  clamp: [0.05, 0.92] as [number, number],
};
/** 暖色（橙/金/红）单独拉到紫，避免整屏只剩青 */
const warm = (hex: string) => remap(hex, {...spec, huePull: 0.80, hueTarget: 286, hueShift: null});

const L = {
  paper: '#070B18',
  dot: '#141C33',
  tokenBg: '#101830',
  corner: '#2A3A5C',
  ink: '#04070F',
  ink2: '#0A1226',
  white: '#EAF2FF',
  green: '#3DE0C0',
  heart: '#FF5F7E',
  orange: warm('#E07A3A'),
  orangeBar: '#39E6FF',
  teal: '#39E6FF',
  gold: '#B98CFF',
  slate: '#6A7A9E',
  darkBg: '#060A15',
  darkGrid: '#101a30',
  darkSurface: '#0C1424',
  darkBorder: '#1E2C48',
  darkText: '#CFE0FF',
  darkMuted: '#7C8DB0',
  darkCell: '#16223C',
  darkCellLit: '#4CF0D8',
  panel: '#132038',
  panelDark: '#0A1120',
  panelLine: '#26385C',
  metal: '#1B2A48',
  metalLight: '#4A6690',
  goldDark: '#7A5AC0',
  cream: '#DCE9FF',
  creamDark: '#1B2A44',
  muted: '#9FB2D4',
  grey: '#223354',
  greyLight: '#5B7099',
};

export const neonGlass: Theme = {
  id: 'neon',
  label: '霓虹玻璃',
  colors: {
    bg: L.paper, bgAlt: L.darkBg, grid: L.darkGrid,
    surface: 'rgba(20,32,58,0.55)', surfaceAlt: 'rgba(12,20,40,0.72)',
    border: 'rgba(120,200,255,0.22)', stroke: 'rgba(140,215,255,0.38)',
    textPrimary: '#EAF2FF', textSecondary: '#8FA2C4', textInverse: '#04070F',
    accent: '#39E6FF', accent2: '#B98CFF', accent3: '#3DE0C0',
    warn: '#FF5F7E', success: '#3DE0C0',
    plate: 'rgba(10,18,36,0.82)', onPlate: '#EAF2FF',
    overlay: 'rgba(6,10,21,0.80)', scrim: 'rgba(8,14,30,0.55)',
    bubble: 'rgba(22,36,64,0.78)', bubbleText: '#EAF2FF',
    legacy: L,
  },
  texture: {grainAmount: 0.05, vignette: 0.55, blurGlass: 18, scanlines: 0, glow: 1},
  shape: {
    radiusSm: 10, radiusMd: 22, radiusLg: 34, borderWidth: 1.5,
    shadow: (n: number) => `0 ${n * 2.4}px ${n * 8}px rgba(0,0,0,0.55)`,
    shadowDeep: (n: number) => `0 ${n * 2.4}px ${n * 10}px rgba(0,0,0,0.68)`,
    shadowAccent: (n: number) => `0 0 ${n * 6}px rgba(57,230,255,0.45), 0 0 ${n * 15}px rgba(185,140,255,0.26)`,
    pixelated: false,
  },
  motion: {
    easeEnter: 'cubic-bezier(0.16, 1, 0.3, 1)',
    easeEmphasis: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
    enterMs: 467,      // 14 帧 @30fps，比像素风舒展
    bounce: true,
    staggerMs: 267,
    idleAmp: 1.25,
  },
  type: {
    fontDisplay: {family: '"Inter", "Noto Sans SC", system-ui, sans-serif', size: 76, lineHeight: 1.04, weight: 700, letterSpacing: -1.5},
    fontBody: {family: '"Inter", "Noto Sans SC", system-ui, sans-serif', size: 42, lineHeight: 1.35, weight: 600, letterSpacing: 0},
    fontMono: {family: '"IBM Plex Mono", ui-monospace, monospace', size: 34, lineHeight: 1.4, weight: 400, letterSpacing: 0},
    fontFaces: [
      {family: 'Inter', file: 'fonts/Inter-Regular-Subset.woff'},
      {family: 'Inter', file: 'fonts/Inter-SemiBold-Subset.woff'},
      {family: 'Inter', file: 'fonts/Inter-Bold-Subset.woff'},
      {family: 'Noto Sans SC', file: 'fonts/NotoSansSC-Subset.otf'},
      {family: 'Noto Sans SC', file: 'fonts/NotoSansSC-Bold-Subset.otf'},
      {family: 'IBM Plex Mono', file: 'fonts/IBMPlexMono-Regular-Subset.woff'},
      {family: 'IBM Plex Mono', file: 'fonts/IBMPlexMono-SemiBold-Subset.woff'},
    ],
  },
  bgMode: 'glass',
  bgModeDark: 'glass',
  bgModeStar: 'aurora',
  rhythm: 0.85,
  materials: deriveMaterials(spec, {
    // 霓虹皮肤里「纸/白」要变成发光体而不是砖块
    paper: '#0A1024', white: '#EAF2FF', black: '#02040A',
    ink: '#04070F', 'ink-2': '#0A1226',
    gold: '#B98CFF', 'gold-dark': '#7A5AC0',
    orange: '#FF7AC6', heart: '#FF5F7E',
    green: '#3DE0C0', teal: '#39E6FF', 'teal-bright': '#39E6FF',
    panel: '#132038', 'dark-surface': '#0C1424', 'dark-bg': '#060A15',
    'dark-text': '#CFE0FF', cream: '#DCE9FF', 'cream-dark': '#1B2A44',
    term: '#050912', 'term-bg': '#050912', 'hud-bg': '#0A1430',
    'token-bg': '#101830', dot: '#141C33',
    'muted': '#9FB2D4',
  }),
};
