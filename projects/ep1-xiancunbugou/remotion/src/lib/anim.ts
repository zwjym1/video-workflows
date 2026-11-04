export type Ease = (t: number) => number;

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const linear: Ease = (t) => t;
export const easeInOut: Ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
export const easeOut: Ease = (t) => 1 - Math.pow(1 - t, 3);
export const easeIn: Ease = (t) => t * t * t;
export const easeOutBack: Ease = (t) => {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
};
/** 过冲回弹，适合「啪」地弹出 */
export const easeOutElastic: Ease = (t) =>
  t === 0 || t === 1 ? t : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * ((2 * Math.PI) / 3)) + 1;

/** frame 在 [start, start+dur] 内的进度，套上 ease */
export const prog = (frame: number, start: number, dur: number, ease: Ease = linear) =>
  ease(clamp01((frame - start) / dur));

/** 分段关键帧插值，两端保持首尾值 */
export const keyframes = (frame: number, ks: [number, number][], ease: Ease = easeInOut) => {
  if (frame <= ks[0][0]) return ks[0][1];
  for (let i = 1; i < ks.length; i++) {
    const [f1, v1] = ks[i];
    if (frame <= f1) {
      const [f0, v0] = ks[i - 1];
      return lerp(v0, v1, ease((frame - f0) / (f1 - f0)));
    }
  }
  return ks[ks.length - 1][1];
};

/** 确定性伪随机，0..1 */
export const rand = (seed: number) => {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
};

/** 手绘感的轻微抖动，按 4fps 跳变（像逐格动画） */
export const boil = (frame: number, seed: number, amp = 1) => {
  const step = Math.floor(frame / 7.5);
  return (rand(step * 31 + seed) - 0.5) * 2 * amp;
};

/** 伸手动画的伸出程度：a 帧开始伸出，b 帧开始收回，各 8 帧 */
export const reach = (f: number, a: number, b: number) => keyframes(f, [[a, 0], [a + 8, 1], [b, 1], [b + 8, 0]]);

/* ------------------------------------------------------------------ *
 * 入场曲线 v4（动作密度提速版）
 * ------------------------------------------------------------------
 * 设计要求：总时长 400ms（12 设计帧 @30fps），保留回弹但更收敛。
 * c1 从 1.70158 降到 1.2 → 过冲 5.3%（原 10.0%），首次回到最终位在 182ms，
 * 过冲峰值 254ms，400ms 完全静止。比原来 8 帧 / 1.7 的「啪一下」更舒展，
 * 但仍然是像素风该有的弹，不是高级感那种 600ms 缓入。
 *
 * 注意：旧的 easeOutBack（c1=1.7）保留不动 —— W.tsx 里的数字滚动、
 * 勾选回弹这些小部件还在用它的形状，改了会连带改掉组件内部动画。
 * ------------------------------------------------------------------ */
export const ENTER_FRAMES = 12;
export const ENTER_MS = 400;

/** easeOutBack，c1 = 1.2：过冲 5.3%，落定 182ms（首次到位） */
export const easeOutBackSoft: Ease = (t) => {
  const c1 = 1.2;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
};

/**
 * 入场时长按皮肤覆盖 —— 放在这里而不是改 src/theme/，
 * 因为皮肤目录另一条线在并行改，动它会冲突。
 * 只覆盖 pixel；neon / paper 仍走各自的 theme.motion 配置，一点没变。
 *
 * 像素皮肤原本是 8 帧 / c1=1.7（落定 130ms，「啪」的一下）。
 * 现在 12 帧 / c1=1.2 → 首次到位 182ms，完全静止 400ms，过冲 5.3%。
 * 正好落在对标「像素/信息图类 125–250ms 入场」的上沿，还保留弹的感觉。
 */
export const ENTER_OVERRIDE: Record<string, {frames: number; ease: Ease}> = {
  pixel: {frames: ENTER_FRAMES, ease: easeOutBackSoft},
};

/** 取某皮肤的实际入场参数：有覆盖用覆盖，否则用主题里的 */
export const enterSpec = (skinId: string, themeFrames: number, themeEase: Ease) =>
  ENTER_OVERRIDE[skinId] ?? {frames: themeFrames, ease: themeEase};
