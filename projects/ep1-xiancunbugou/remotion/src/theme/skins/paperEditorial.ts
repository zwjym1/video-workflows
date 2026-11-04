/**
 * paperEditorial —— 浅色纸质杂志风。
 * 米白底 + 纸上噪点 + 细黑描边 + 硬阴影（无模糊投影）+ 大衬线标题 + 高对比黑色正文 + 朱红强调。
 *
 * 画材重映射：把像素皮肤的暖米白纸、墨黑线原样留下，把橙金绿全部收敛到「墨 + 朱红」，
 * 只允许朱红这一个彩色出口，符合杂志印刷的少色原则。
 */
import type {Theme} from '../types';
import {remap} from '../color';
import {deriveMaterials} from '../materials';

const light = (l: number) => {
  // 浅色皮肤：暗的留在 0.10 以上当墨，亮的推到 0.98 当纸
  const t = Math.max(0, Math.min(1, l));
  return 0.09 + Math.pow(t, 0.86) * 0.89;
};
/** 有彩色 → 朱红/赭石一支，色相收拢到 8–20 度，饱和度压到印刷墨的水平 */
const ink = (hex: string) => remap(hex, {
  light, hueShift: null, huePull: 0.88, hueTarget: 12,
  sat: (s: number) => Math.min(0.72, s * 0.72 + 0.05),
  greyBelow: 0.14, clamp: [0.08, 0.95],
});

const L = {
  paper: '#F4EFE4',
  dot: '#DED5C4',
  tokenBg: '#FBF7EE',
  corner: '#B9AE99',
  ink: '#17140F',
  ink2: '#2A241C',
  white: '#FFFFFF',
  green: '#2F5D46',
  heart: '#C0341E',
  orange: ink('#E07A3A'),
  orangeBar: '#C0341E',
  teal: '#2F5D46',
  gold: '#C08A2E',
  slate: '#6E675C',
  darkBg: '#F4EFE4',
  darkGrid: '#E2D9C8',
  darkSurface: '#EFE8DA',
  darkBorder: '#C9BFA8',
  darkText: '#17140F',
  darkMuted: '#6E675C',
  darkCell: '#D9CFBC',
  darkCellLit: '#2F5D46',
  panel: '#EDE5D6',
  panelDark: '#E4DACA',
  panelLine: '#B9AE99',
  metal: '#D8CEBB',
  metalLight: '#A99D86',
  goldDark: '#8A6A22',
  cream: '#FBF7EE',
  creamDark: '#D8CEBB',
  muted: '#6E675C',
  grey: '#C9BFA8',
  greyLight: '#8C8474',
};

export const paperEditorial: Theme = {
  id: 'paper',
  label: '纸本杂志',
  colors: {
    bg: L.paper, bgAlt: '#EDE6D8', grid: L.dot,
    surface: '#FBF7EE', surfaceAlt: '#EFE8DA',
    border: '#17140F', stroke: '#17140F',
    textPrimary: '#17140F', textSecondary: '#5C554A', textInverse: '#FBF7EE',
    accent: '#C0341E', accent2: '#C08A2E', accent3: '#2F5D46',
    warn: '#C0341E', success: '#2F5D46',
    plate: '#17140F', onPlate: '#FBF7EE',
    overlay: '#17140F', scrim: 'rgba(23,20,15,0.90)',
    bubble: '#FBF7EE', bubbleText: '#17140F',
    legacy: L,
  },
  texture: {grainAmount: 0.16, vignette: 0.12, blurGlass: 0, scanlines: 0, glow: 0},
  shape: {
    radiusSm: 0, radiusMd: 2, radiusLg: 3, borderWidth: 2.5,
    // 硬阴影：0 blur，符合「无模糊投影」
    shadow: (n: number) => `${n}px ${n}px 0 #17140F`,
    shadowDeep: (n: number) => `${n}px ${n}px 0 #17140F`,
    shadowAccent: (n: number) => `${n}px ${n}px 0 #C0341E`,
    pixelated: false,
  },
  motion: {
    easeEnter: 'cubic-bezier(0.2, 0.9, 0.24, 1)',
    easeEmphasis: 'cubic-bezier(0.3, 1.4, 0.5, 1)',
    enterMs: 333,      // 10 帧 @30fps
    bounce: true,
    staggerMs: 233,
    idleAmp: 0.7,
  },
  type: {
    fontDisplay: {family: '"Noto Serif SC", "Songti SC", serif', size: 74, lineHeight: 1.16, weight: 700, letterSpacing: 1},
    fontBody: {family: '"Noto Sans SC", "Inter", system-ui, sans-serif', size: 40, lineHeight: 1.45, weight: 400, letterSpacing: 0},
    fontMono: {family: '"IBM Plex Mono", ui-monospace, monospace', size: 32, lineHeight: 1.45, weight: 400, letterSpacing: 0},
    fontFaces: [
      {family: 'Noto Serif SC', file: 'fonts/NotoSerifSC-Bold-Subset.otf'},
      {family: 'Noto Serif SC', file: 'fonts/NotoSerifSC-SemiBold-Subset.otf'},
      {family: 'Noto Sans SC', file: 'fonts/NotoSansSC-Subset.otf'},
      {family: 'Noto Sans SC', file: 'fonts/NotoSansSC-Bold-Subset.otf'},
      {family: 'Inter', file: 'fonts/Inter-Regular-Subset.woff'},
      {family: 'IBM Plex Mono', file: 'fonts/IBMPlexMono-Regular-Subset.woff'},
    ],
  },
  bgMode: 'paper',
  bgModeDark: 'paper',
  bgModeStar: 'rules',
  rhythm: 0.6,
  materials: deriveMaterials({
    light, hueShift: null, huePull: 0.88, hueTarget: 12,
    sat: (x: number) => Math.min(0.72, x * 0.72 + 0.05),
    greyBelow: 0.14, clamp: [0.08, 0.97],
  }, {
    // 纸本皮肤：纸就是纸，墨就是墨；暗场不改底色（杂志不印黑底），只压暗一档
    paper: '#F4EFE4', white: '#FFFFFF', black: '#17140F',
    ink: '#17140F', 'ink-2': '#2A241C',
    'dark-bg': '#EDE6D8', 'dark-grid': '#DDD3C0', 'dark-surface': '#EFE8DA',
    'dark-text': '#17140F', panel: '#EDE5D6', dot: '#DED5C4',
    'token-bg': '#FBF7EE', cream: '#17140F', 'cream-dark': '#C9BFA8',
    heart: '#C0341E', 'orange-bar': '#C0341E',
  }),
};
