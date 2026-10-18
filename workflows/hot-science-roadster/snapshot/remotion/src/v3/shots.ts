import AL from './align.json';
import TL from './footage-timeline.json';
import type {Shot, Timeline} from './shotctx';
const FPS = 30;
type Wd = {text: string; start: number; end: number};
const SS = (AL as any).sentences as {i: number; text: string; start: number; end: number; words: Wd[]}[];
export const s = (i: number) => SS[i];
/** start time of substring (first alt that matches) in sentence i */
export const W = (i: number, sub: string | string[], end = false): number => {
  const ws = SS[i].words; let joined = ''; const idx: number[] = [];
  ws.forEach((w, k) => { for (const _ of w.text) { joined += _; idx.push(k); } });
  for (const q of Array.isArray(sub) ? sub : [sub]) { const p = joined.indexOf(q); if (p >= 0) return end ? ws[idx[p + q.length - 1]].end : ws[idx[p]].start; }
  throw new Error(`W miss ${i} ${sub}`);
};
const LAST = SS[SS.length - 1];
export const V3_END = LAST.end + 1.6;
export const V3_FRAMES = Math.round(V3_END * FPS);
const nx = (i: number) => (i + 1 < SS.length ? SS[i + 1].start : V3_END);

/* ---------- T: key times ---------- */
export const T = {
  cut: W(0, '是这') - 0.05, fly: W(0, '飞'), semi: W(1, 'Semi'),
  cm: s(2).start - 0.15, c1: W(2, '特效'), c2: W(2, ['AI', 'A I']), c3: W(2, '画饼'),
  me: s(3).start - 0.1, con: s(4).start - 0.1, real: W(4, '真不是'), but: W(4, '但'),
  src: s(5).start - 0.1, two: W(5, '说白'), xi: W(5, '吸'), pen: W(5, '喷'),
  climb: s(6).start - 0.1, A: W(7, '大') - 0.35, feng: W(7, '风'), chou: W(7, '抽'), qiya: W(8, '气压'), wai: W(8, '外'), si: W(8, '死'),
  musk: s(9).start - 0.05, zui: W(9, '最'), bei: W(9, '倍'),
  inv: s(10).start - 0.1, ding: W(10, '顶'), dao: W(10, '倒'), bushi: W(10, '不是'),
  q: s(11).start - 0.1, spx: W(12, 'SpaceX'),
  B: W(13, '座'), gao: W(13, '高'), fa: W(13, '阀'), pen2: W(13, '喷'), qwh: W(14, '气往后'), qian: W(14, '前'), gen: W(14, '跟'), qq: W(14, '气球'),
  dh: W(15, '点火'), sy: W(15, '烧油'), ys: W(15, '压缩'), cs: W(16, '车身'), pk: W(16, '喷口'), zt: W(16, '姿态'), hj: W(16, '火箭'),
  sum: s(17).start - 0.1, fs: W(17, '风扇'), pq: W(17, '喷气'),
  buy: s(18).start - 0.1, y28: W(19, ['二零二八', '2028']), hf: W(19, '会飞'), fb: W(19, '封闭'), price: s(20).start - 0.1, w25: W(20, ['二十五', '25']),
  end: s(21).start - 0.1, gan: W(21, '敢'),
};


/* ---------- real-footage shots: word-anchored defaults; footage-timeline.json overrides by id ---------- */
const sh = (id: string, label: string, src: string, start: number, end: number, inn: number, rate = 1): Shot => ({id, label, src, start: +start.toFixed(3), end: +end.toFixed(3), in: +inn.toFixed(3), rate});
export const defaultShots = (): Shot[] => {
  const suckDur = T.A - T.climb; const climbEnd = T.ding;
  const flyDur = T.B - T.q, flyRate = Math.min(1, 4.2 / flyDur);
  return [
    sh('hook-launch', '开场·起步加速', 'clip-launch.mp4', 0, T.cut, 5.0),
    sh('hook-fly', '开场·飞越Semi', 'clip-fly.mp4', T.cut, T.cm, 42.5 - (T.fly - T.cut)),
    sh('comments-bg', '评论区背景', 'clip-ramp.mp4', T.cm, T.me, 72.5),
    sh('me-bg', '自我介绍背景', 'clip-ramp-official.mp4', T.me, T.con, 10),
    sh('concl', '结论', 'clip-fly.mp4', T.con, T.src, 42.0, 0.5),
    sh('two-bg', '两套系统背景', 'clip-ramp.mp4', T.two, T.climb, 40.0),
    sh('suck-live', '先说吸·俯视实拍→定格', 'hliveA.mp4', T.climb, T.A, Math.max(0, 1 - suckDur), suckDur > 1 ? +(1 / suckDur).toFixed(3) : 1),
    sh('musk-downforce', '马斯克说·下压力读数', 'clip-ramp.mp4', T.musk, T.zui - 0.05, 4.4),
    sh('climb', '冲上弯墙·爬坡过程', 'clip-ramp.mp4', T.inv, climbEnd, 11.4 - (climbEnd - T.inv)),
    sh('top-inverted', '顶上倒过来一下', 'clip-ramp.mp4', climbEnd, T.q, 20.9, 0.6),
    sh('fly-q', '设问·飞行实拍', 'clip-fly.mp4', T.q, T.B, 43.15 - flyDur * flyRate, +flyRate.toFixed(3)),
    sh('buy-promo', '能开上吗·官方片', 'promo-garage.mp4', T.buy, T.y28 - 0.14, 0),
    sh('buy-musk', '2028量产·马斯克', 'musk2028.mp4', T.y28 - 0.14, T.hf, 0),
    sh('buy-closed', '封闭场地', 'clip-ramp.mp4', T.hf, T.price, 82),
    sh('end', '结尾', 'clip-ramp-official.mp4', T.end, V3_END, 24.3),
  ];
};
/** non-footage segments, shown locked in the align tool */
export const graphicSegments = () => [
  {id: 'me-card', label: '频道卡', start: T.me, end: T.con}, {id: 'sources', label: '报道截图', start: T.src, end: T.two},
  {id: 'explainA', label: '3D 拆解一', start: T.A, end: T.inv}, {id: 'explainB', label: '3D 拆解二', start: T.B, end: T.sum},
  {id: 'summary', label: '一句话总结', start: T.sum, end: T.buy}, {id: 'price', label: '售价截图', start: T.price, end: T.end},
];
export const mergeShots = (tl?: Partial<Timeline> | null): Shot[] => { const o = Object.fromEntries(((tl?.shots ?? []) as Shot[]).map((x) => [x.id, x]));
  return defaultShots().map((d) => ({...d, ...(o[d.id] ?? {})})); };
export const fileTimeline = TL as Timeline;
export const sentences = SS;

/* ---------- audio mix (saved in footage-timeline.json under "audio") ---------- */
export type AudioMix = {voiceDb: number; sfxDb: number; bgmDb: number; duckDb: number; bgmEnv: {t: number; db: number}[]; lufs: number};
// bgmDb 0 = previous v3 level (+3 dB vs v3.1, as requested)
export const defaultAudio = (): AudioMix => ({voiceDb: 0, sfxDb: 0, bgmDb: 0, duckDb: 10, bgmEnv: [], lufs: -16});
export const mergeAudio = (tl?: any): AudioMix => ({...defaultAudio(), ...((tl && tl.audio) || {})});
export const BGM_BASE = 0.238; // calibrated: overall BGM level = v3.1 + 3 dB (with duckDb 10)
export const BGM_SWITCH = () => T.q; // A → B at "那真正把它送上天的"
const db = (x: number) => Math.pow(10, x / 20);
const envDb = (t: number, env: {t: number; db: number}[]) => { if (!env.length) return 0; const e = [...env].sort((a, b) => a.t - b.t);
  if (t <= e[0].t) return e[0].db; for (let i = 0; i < e.length - 1; i++) if (t <= e[i + 1].t) return e[i].db + ((t - e[i].t) / (e[i + 1].t - e[i].t)) * (e[i + 1].db - e[i].db); return e[e.length - 1].db; };
/** 0..1, how much the voice is speaking (attack 0.08 s, release 0.35 s) */
export const speechAmt = (t: number) => { let m = 0; for (const s of SS) { const a = s.start - 0.08, b = s.end + 0.35;
  if (t >= a && t <= b) m = Math.max(m, Math.min(1, (t - a) / 0.08, t <= s.end ? 1 : (b - t) / 0.35)); } return m; };
export const bgmGain = (t: number, mix: AudioMix) => BGM_BASE * db(mix.bgmDb + envDb(t, mix.bgmEnv) - mix.duckDb * speechAmt(t));
export const linDb = db;
