/** 颜色工具：hex ↔ HSL，以及跨皮肤的整体配色重映射 */

export type RGB = {r: number; g: number; b: number};
export type HSL = {h: number; s: number; l: number};

export const parseHex = (hex: string): RGB => {
  let h = hex.trim().replace('#', '');
  if (h.length === 3) h = h.split('').map((c) => c + c).join('');
  if (h.length === 8) h = h.slice(0, 6);
  const n = parseInt(h, 16);
  return {r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255};
};

export const toHex = ({r, g, b}: RGB) => {
  const f = (v: number) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0');
  return `#${f(r)}${f(g)}${f(b)}`;
};

export const rgbToHsl = ({r, g, b}: RGB): HSL => {
  const R = r / 255, G = g / 255, B = b / 255;
  const max = Math.max(R, G, B), min = Math.min(R, G, B);
  const l = (max + min) / 2;
  let h = 0, s = 0;
  const d = max - min;
  if (d !== 0) {
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    if (max === R) h = ((G - B) / d + (G < B ? 6 : 0)) / 6;
    else if (max === G) h = ((B - R) / d + 2) / 6;
    else h = ((R - G) / d + 4) / 6;
  }
  return {h: h * 360, s, l};
};

export const hslToRgb = ({h, s, l}: HSL): RGB => {
  const H = ((h % 360) + 360) % 360 / 360;
  if (s === 0) { const v = l * 255; return {r: v, g: v, b: v}; }
  const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
  const p = 2 * l - q;
  const hue = (t: number) => {
    let T = t; if (T < 0) T += 1; if (T > 1) T -= 1;
    if (T < 1 / 6) return p + (q - p) * 6 * T;
    if (T < 1 / 2) return q;
    if (T < 2 / 3) return p + (q - p) * (2 / 3 - T) * 6;
    return p;
  };
  return {r: hue(H + 1 / 3) * 255, g: hue(H) * 255, b: hue(H - 1 / 3) * 255};
};

export const hexToHsl = (hex: string) => rgbToHsl(parseHex(hex));
export const hslToHex = (hsl: HSL) => toHex(hslToRgb(hsl));

export const mixHex = (a: string, b: string, t: number) => {
  const A = parseHex(a), B = parseHex(b);
  return toHex({r: A.r + (B.r - A.r) * t, g: A.g + (B.g - A.g) * t, b: A.b + (B.b - A.b) * t});
};

export const alpha = (hex: string, a: number) => {
  const {r, g, b} = parseHex(hex);
  return `rgba(${r},${g},${b},${a})`;
};

/** 相对亮度（WCAG） */
export const luminance = (hex: string) => {
  const {r, g, b} = parseHex(hex);
  const f = (v: number) => { const s = v / 255; return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4); };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
};

/** 把任意基准色搬到一个新皮肤里：先做明暗曲线，再做色相归拢，最后收饱和度 */
export type RemapSpec = {
  /** 明暗映射：入 0..1 出 0..1（把纸色压成深底、把墨色提成浅字） */
  light: (l: number) => number;
  /** 有彩色元素的色相偏移（度）。null = 保持原色相 */
  hueShift?: number | null;
  /** 色相向目标色收拢的比例 0..1 */
  huePull?: number;
  /** 目标色相（收拢时用） */
  hueTarget?: number;
  /** 饱和度曲线 */
  sat: (s: number) => number;
  /** 低饱和判定阈值：低于它的当作无彩色，只走明暗 */
  greyBelow?: number;
  /** 是否对无彩色也染色（冷调深底） */
  tintGreys?: {h: number; s: number};
  /** 明度下限/上限保护 */
  clamp?: [number, number];
};

export const remap = (hex: string, spec: RemapSpec): string => {
  if (hex === 'transparent' || hex.startsWith('var(') || hex.startsWith('rgba')) return hex;
  const {h, s, l} = hexToHsl(hex);
  const grey = s < (spec.greyBelow ?? 0.12);
  let outH = h, outS = spec.sat(s);
  if (grey) {
    outS = spec.tintGreys ? spec.tintGreys.s : Math.min(outS, 0.06);
    if (spec.tintGreys) outH = spec.tintGreys.h;
  } else {
    if (spec.hueShift != null) outH = h + spec.hueShift;
    if (spec.huePull && spec.hueTarget != null) {
      // 沿最短弧收拢
      let d = ((spec.hueTarget - outH + 540) % 360) - 180;
      outH = outH + d * spec.huePull;
    }
  }
  let outL = spec.light(l);
  if (spec.clamp) outL = Math.max(spec.clamp[0], Math.min(spec.clamp[1], outL));
  return hslToHex({h: outH, s: Math.max(0, Math.min(1, outS)), l: Math.max(0, Math.min(1, outL))});
};
