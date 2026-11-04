/**
 * 主题契约（Theme Contract）
 * ------------------------------------------------------------------
 * 一套分镜、一套时间轴，只换 theme 文件就换整套视觉皮肤。
 *
 * 颜色走 CSS 自定义属性（--t-*），因为：
 *   1) SVG 呈现属性（fill="var(--t-ink)"）需要字符串，不能塞 React context 对象；
 *   2) W.tsx / Chapters.tsx 里大量小部件工厂是在模块作用域调用的
 *      （例如 W.label('x', P.teal, 60) 写在数据表里），如果用 context 取色，
 *      颜色会在 import 那一刻被冻结，换皮肤失效。CSS 变量在绘制时才求值，天然跟着换。
 * 时长 / easing / 圆角数值 / 噪点强度这些「算出来的数」走 useTheme() context。
 */

export type FontSpec = {
  family: string;
  size: number;
  lineHeight: number;
  weight: number;
  letterSpacing: number;
};

export type ThemeColors = {
  // 语义色
  bg: string;
  bgAlt: string;
  grid: string;
  surface: string;
  surfaceAlt: string;
  border: string;
  /** 描边（图形轮廓，可不同于 border） */
  stroke: string;
  textPrimary: string;
  textSecondary: string;
  textInverse: string;
  accent: string;
  accent2: string;
  accent3: string;
  warn: string;
  success: string;
  /** 深色底板（标题条、反色块）底色 */
  plate: string;
  /** 底板上的字 */
  onPlate: string;
  /** 字幕条 / 终端底色 */
  overlay: string;
  /** 遮罩层（章节卡压暗） */
  scrim: string;
  /** 气泡底色 */
  bubble: string;
  /** 气泡上的字 */
  bubbleText: string;

  /** 兼容层：像素画材。像素道具是逐格画的，颜色是画材不是语义色 */
  legacy: Record<string, string>;
};

export type ThemeTexture = {
  /** 噪点强度 0–1 */
  grainAmount: number;
  /** 暗角 0–1 */
  vignette: number;
  /** 背景模糊 px（毛玻璃） */
  blurGlass: number;
  /** 扫描线 0–1 */
  scanlines: number;
  /** 背景光晕强度 0–1（霓虹渐变用） */
  glow: number;
};

export type ThemeShape = {
  radiusSm: number;
  radiusMd: number;
  radiusLg: number;
  borderWidth: number;
  /**
   * 阴影生成器：只要给一个偏移量，皮肤决定怎么画。
   *   像素  -> `${n}px ${n}px 0 rgba(30,27,37,.18)`  （硬边、无模糊）
   *   霓虹  -> `0 ${n*2}px ${n*7}px rgba(0,0,0,.5)`   （大扩散柔光）
   *   纸本  -> `${n}px ${n}px 0 #17140F`              （印刷硬投影）
   * 之所以要参数化而不是给一个固定字符串：像素皮肤不同组件用 4/5/6/8/10 五档偏移，
   * 压成一个值会让边缘错开 1px，像素 diff 就归不了零。
   */
  shadow: (n: number, alpha?: number) => string;
  /** 深色场景里的黑影（原设计用 rgba(0,0,0,.35)） */
  shadowDeep: (n: number, alpha?: number) => string;
  /** 强调阴影（发光/彩色投影） */
  shadowAccent: (n: number) => string;
  pixelated: boolean;
};

export type ThemeMotion = {
  /** cubic-bezier 字符串（给 CSS transition 用） */
  easeEnter: string;
  easeEmphasis: string;
  /** 入场时长（毫秒，引擎按 fps 换算成帧） */
  enterMs: number;
  bounce: boolean;
  /** 错帧间隔（毫秒） */
  staggerMs: number;
  /** 常驻微动幅度倍数 */
  idleAmp: number;
  /**
   * 可选的解析式 easing 覆盖。像素皮肤用它锁死和改造前完全一致的 easeOutBack，
   * 保证像素 diff 为 0；其他皮肤走 easeEnter 字符串解析出来的三次贝塞尔。
   */
  easeEnterFn?: (t: number) => number;
  easeEmphasisFn?: (t: number) => number;
};

export type ThemeType = {
  fontDisplay: FontSpec;
  fontBody: FontSpec;
  fontMono: FontSpec;
  fontFaces: {family: string; file: string}[];
};

export type Theme = {
  id: string;
  label: string;
  colors: ThemeColors;
  texture: ThemeTexture;
  shape: ThemeShape;
  motion: ThemeMotion;
  type: ThemeType;
  /** 亮场背景画法 */
  bgMode: 'paper' | 'grid' | 'glass' | 'flat';
  /** 暗场背景画法 */
  bgModeDark: 'paper' | 'grid' | 'glass' | 'flat';
  /** 章节卡星空底画法 */
  bgModeStar: 'stars' | 'aurora' | 'rules';
  /** 画材色板：109 个像素道具用色在当前皮肤下的取值 */
  materials: Record<string, string>;
  /**
   * 卡点强度 0–1。0 = 完全不吃拍（像素皮肤就是 0，
   * 因为它的验收标准是和改造前逐像素一致；任何脉动都会破坏 diff=0）。
   * 霓虹/纸本给 0.6–1，字幕条呼吸、进度条光晕、HUD 心跳都跟着 BGM 走。
   */
  rhythm: number;
};
