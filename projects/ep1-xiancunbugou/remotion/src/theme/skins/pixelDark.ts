/**
 * pixelDark —— 基准皮肤。
 * 所有数值都是从改造前的代码里原样搬过来的，一个都没改色。
 * 验收标准：frame 600 与改造前逐像素对比，平均绝对误差必须接近 0。
 */
import type {Theme} from '../types';
import {easeOutBack} from '../../lib/anim';
import {BASE_MATERIALS} from '../tokens';

const L = {
  // 纸面
  paper: '#F6F0E2', dot: '#E4DCCB', tokenBg: '#FBF7EA', corner: '#D0BDA2',
  // 墨
  ink: '#1E1B25', ink2: '#2B2735', white: '#FFFFFF',
  // 强调
  green: '#65BF62', heart: '#F8574C', orange: '#E07A3A', orangeBar: '#FF8236',
  teal: '#2E8F82', gold: '#F2C14E', slate: '#9A94AA',
  // 深场
  darkBg: '#2A2733', darkGrid: '#34303F', darkSurface: '#25222D', darkBorder: '#3A3546',
  darkText: '#D8D2E6', darkMuted: '#9A94AA', darkCell: '#4A4458', darkCellLit: '#8FD3C7',
  // 道具画材
  panel: '#3A3546', panelDark: '#2E2A37', panelLine: '#5C566C', metal: '#4A4458',
  metalLight: '#7D7792', goldDark: '#B88A2A', cream: '#F3EAD3', creamDark: '#D3C9B6',
  muted: '#7A6E5C', grey: '#5A5468', greyLight: '#8A84A0',
};

export const pixelDark: Theme = {
  id: 'pixel',
  label: '像素暗房',
  colors: {
    bg: L.paper, bgAlt: L.darkBg, grid: L.darkGrid,
    surface: L.tokenBg, surfaceAlt: L.darkSurface,
    border: L.ink, stroke: L.ink,
    textPrimary: L.ink, textSecondary: L.muted, textInverse: L.white,
    accent: L.orange, accent2: L.gold, accent3: L.teal,
    warn: L.heart, success: L.green,
    plate: L.ink, onPlate: L.white,
    overlay: L.ink, scrim: 'rgba(30,27,37,.92)',
    bubble: L.white, bubbleText: L.ink,
    legacy: L,
  },
  texture: {grainAmount: 0, vignette: 0, blurGlass: 0, scanlines: 0, glow: 0},
  shape: {
    radiusSm: 0, radiusMd: 0, radiusLg: 0, borderWidth: 5,
    shadow: (n: number, a?: number) => `${n}px ${n}px 0 rgba(30,27,37,${a ?? 0.18})`,
    shadowDeep: (n: number, a?: number) => `${n}px ${n}px 0 rgba(0,0,0,${a ?? 0.35})`,
    shadowAccent: (n: number) => `${n}px ${n}px 0 rgba(30,27,37,.22)`,
    pixelated: true,
  },
  motion: {
    easeEnter: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
    easeEmphasis: 'cubic-bezier(0.22, 1, 0.36, 1)',
    enterMs: 267,     // 8 帧 @30fps
    bounce: true,
    staggerMs: 200,
    idleAmp: 1,
    // 像素皮肤锁死原曲线，保证 diff = 0（easeOutBack, c1=1.70158）
    easeEnterFn: easeOutBack,
  },
  type: {
    fontDisplay: {family: 'FusionPixel', size: 68, lineHeight: 1.15, weight: 400, letterSpacing: 0},
    fontBody: {family: 'FusionPixel', size: 40, lineHeight: 1.3, weight: 400, letterSpacing: 0},
    fontMono: {family: 'FusionPixel', size: 32, lineHeight: 1.3, weight: 400, letterSpacing: 0},
    fontFaces: [{family: 'FusionPixel', file: 'fonts/fusion-pixel-12px-zh_hans.otf'}],
  },
  bgMode: 'paper',
  bgModeDark: 'grid',
  bgModeStar: 'stars',
  // 基准皮肤直接用原始画材，不做任何换算——这是像素 diff 必须为 0 的前提
  rhythm: 0,
  materials: {...BASE_MATERIALS},
};
