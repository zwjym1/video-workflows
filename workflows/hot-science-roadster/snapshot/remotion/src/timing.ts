/** Global timing from voice/alignment.json (fps=30). */
export const FPS = 30;
export const DURATION_FRAMES = 1915; // ~63.66s

/** Shot boundaries in frames (from sentence starts). */
export const SHOTS = {
  S01: {from: 0, to: 96}, // → 3.193s
  S02: {from: 96, to: 191}, // → 6.35s
  S03: {from: 191, to: 307}, // → 10.219s
  S04: {from: 307, to: 393}, // → 13.114s
  // Transition A: sentences 6–12 (13.114–28.486)
  TA: {from: 393, to: 855},
  // Transition B: sentences 13–19 (28.486–46.944)
  TB: {from: 855, to: 1408},
  S08: {from: 1408, to: 1537}, // → 51.222s
  S09: {from: 1537, to: 1836}, // → 61.192s
  S10: {from: 1836, to: 1915},
} as const;

export const TA_FRAMES = SHOTS.TA.to - SHOTS.TA.from; // 462
export const TB_FRAMES = SHOTS.TB.to - SHOTS.TB.from; // 553
