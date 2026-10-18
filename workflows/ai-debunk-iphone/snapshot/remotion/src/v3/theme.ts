export const INK = '#111214', PAPER = '#EFE8DA', RED = '#E0392A', YELLOW = '#FFD84A', GREEN = '#1FA35B', WHITE = '#FFFFFF';
export const FONT = 'NotoSubV3';
export const SUB_TOP = 900; // 字幕区 y≥900
export const TITLE_BAND = [42, 120] as const; // 标题带
export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
// ---- 声音常量（dB）
export const VO_GAIN_DB = 0;           // 口播主轨 vo_master_v3c 已 −15.98 LUFS
export const BGM_GAIN_DB = 0;         // BGM 文件已做到 −22 LUFS（未闪避时）
export const BGM_DUCK_DB = -9;        // 口播时压低 9 dB
export const DUCK_ATTACK = 0.08;      // s
export const DUCK_RELEASE = 0.25;     // s
export const BGM_FADE_OUT = 1.6;      // 末 1.6s 余弦淡出到 0（最后一字约在结束前 0.63s），与片尾同步
export const db = (x: number) => Math.pow(10, x / 20);
