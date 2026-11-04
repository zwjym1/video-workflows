// 无声动效小样：K1–K4 硬切串联。节奏参数来自对标 vLLM 片段实测（见 ../MOTION_DATA.md）
import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig} from 'remotion';
import {useDesignFrame, Sfx, SegStartCtx} from './timeline/fps';
import {Frame, FontFace, Label, P, PaperBg, Pop, Sub, FONT, DarkGridBg, StarBg, m} from './kit';
import {Sprite, SpriteBg} from './Sprite';
import {BoltSprite, ClockSprite, Cell, NeuralNet, Dust} from './sprites';
import {prog, easeOut, easeOutBack} from './lib/anim';
import {useBeatPulse} from './components/BeatSync';

const FPS = 30, CPS = 7.25; // 字/秒
export const NAME = '显存不够';
export const K_GREEN = m('green');

export const vis = (t: string) => [...t.replace(/[|。，：？！]$/g, '')].reduce((a, ch) => a + (/[\x00-\x7f]/.test(ch) ? 0.55 : 1), 0);
export type Cue = {text: string; from: number; dur: number; vo?: string};
import VO from './vo_t.json';
import {ChapterTab, BlockStrip} from './Dense';
const norm = (t: string) => t.replace(/[^0-9A-Za-z\u4e00-\u9fff%]/g, '');
const voOf = (line: string) => (VO as {text: string; file: string; dur: number; ct: number[]}[]).find((v) => v.text === line.replace(/\|/g, ''));
export const LINE_GAP = 8; // 句间停顿 8 帧
/** 一句一条：按 。？！： 断句；显示宽度 >16 先按逗号拆，再按手标的 | 拆。
 *  有配音时：每条字幕从它第一个字真正被念出的时刻开始（Fish 逐字时间戳），一句话的总长 = 音频时长 + 8 帧停顿 */
const chunksOf = (line: string) => {
  const out: string[] = [];
  for (let s of line.split(/(?<=[。？！：])/)) {
    s = s.trim(); if (!s) continue;
    const parts = (vis(s) > 16 ? s.split(/(?<=，)/) : [s]).flatMap((p) => vis(p) > 16 ? p.split('|') : [p.replace(/\|/g, '')]);
    for (const p of parts) { const q = p.replace(/[。，：、]$/, ''); if (q) out.push(q); }
  }
  return out;
};
export const makeCues = (lines: string[]): Cue[] => {
  const out: Cue[] = []; let t = 0;
  for (const line of lines) {
    const ch = chunksOf(line); const v = voOf(line);
    if (v) {
      const L = Math.ceil(v.dur * FPS) + LINE_GAP; let o = 0;
      const starts = ch.map((c) => { const st = Math.round((v.ct[Math.min(o, v.ct.length - 1)] ?? 0) * FPS); o += norm(c).length; return st; });
      ch.forEach((c, i) => { const from = i === 0 ? 0 : starts[i]; const to = i + 1 < ch.length ? starts[i + 1] : L; out.push({text: c, from: t + from, dur: Math.max(1, to - from), vo: i === 0 ? v.file : undefined}); });
      t += L;
    } else {
      for (const c of ch) { const dur = Math.max(30, Math.round((c.length / CPS) * FPS)); out.push({text: c, from: t, dur}); t += dur; }
    }
  }
  return out;
};
export const total = (c: Cue[]) => c[c.length - 1].from + c[c.length - 1].dur;
export const CueSub: React.FC<{cues: Cue[]; keys: string[]}> = ({cues, keys}) => {
  const f = useDesignFrame();
  const {fps} = useVideoConfig();
  // 注意：cue 的 from/dur 是设计帧（30fps 坐标）。
  // <Sequence> 要的是当前 fps 的帧，必须换算，否则 60fps 下人声会提前一倍、
  // 一整段 6 分钟的片子在半小时位置就没声音了。
  const toF = (df: number) => Math.round((df * fps) / 30);
  const c = cues.find((x) => f >= x.from && f < x.from + x.dur);
  return <>
    {cues.filter((x) => x.vo).map((x, i) => <Sequence key={i} from={toF(x.from)} layout="none"><Audio src={staticFile(x.vo!)} volume={1} /></Sequence>)}
    {c ? <Sub text={c.text} keys={keys} /> : null}
  </>;
};
/** 强调：8 帧 1→1.12→1 */
export const Pulse: React.FC<{at: number; children: React.ReactNode}> = ({at, children}) => {
  const f = useDesignFrame();
  const t = (f - at) / 8; const s = t >= 0 && t <= 1 ? 1 + 0.12 * Math.sin(Math.PI * t) : 1;
  return <div style={{transform: `scale(${s})`, transformOrigin: 'center'}}>{children}</div>;
};

const C1 = makeCues(['FlashAttention是什么？为什么加一行参数，大模型的注意力就能快好几倍？', '你是一个程序员，想在自己的显卡上|微调一个开源大模型。', '模型加载进来，一跑，显存爆了。把上下文改短，能跑了，但慢得像在挤牙膏。']);
const C2 = makeCues(['这时候你很容易想到，是不是算力不够，得换卡？', '其实不一定。计算机有个老毛病，很多时候不是算得慢，是搬得慢。', 'FlashAttention干的就是一件事：少搬。', '论文里，它在GPT-2上|把注意力这一步算快了最多7.6倍，整个GPT-2训练快了3倍。']);
const C3 = makeCues(['分块是什么？']);
const C4 = makeCues(['既然搬一整张大表太贵，那就别搬整张。', 'FlashAttention把Q、K、V|切成一个个小块，小到能整个放进工作台。', '一次只从显存|拿一小块Q和一小块K、V，在SRAM里|把打分、softmax、乘V一口气做完。', '做完这一块，只把这一小块的输出写回去，那张N乘N的大表，从头到尾都不落到显存里。', '而且这几步|被合并成了同一个GPU算子，中间结果一直留在片上。', '这种把大矩阵切小块、|在片上一次算完的做法，就是所谓的分块。']);
export const at = (c: Cue[], i: number, off = 0) => c[Math.min(i, c.length - 1)].from + off;
export const atT = (c: Cue[], key: string, off = 0) => (c.find((x) => x.text.includes(key)) ?? c[c.length - 1]).from + off;
/** 常驻微动 v4 —— 动作密度提速版
 * ------------------------------------------------------------------
 * 旧版（v3）每个元素只跑一条正弦：周期 40–80 帧、幅度 3px、相位打散。
 * 实测下来整片动作事件只有 0.61–1.11 次/秒，而且有大段 0 帧差（挂机）。
 *
 * v4 拆成两层：
 *
 *  A. 连续通道（永远在动，保证任何一帧都不会是「死图」）
 *     a) 上下浮动  3–6px，正弦，周期 1.6–2.2s（48–66 设计帧）
 *     b) 极慢旋转  ±0.8°，周期 3–4s（90–120 设计帧）
 *     c) 呼吸缩放  1.000 ↔ 1.015，周期 2.4s（72 设计帧）
 *     三者的周期与相位都由元素 seed 打散，绝不整屏同步。
 *
 *  B. 离散事件（每 0.70–0.85s 一个，5 种轮换）
 *     tick 周期 period = 21–25.5 设计帧，相位按 seed 偏移，
 *     每个 tick 从 5 种里取一种（起点类型也由 seed 决定，所以同一镜里
 *     不同元素同时跑的是不同事件）：
 *       0 上浮     3px，12 帧
 *       1 旋转脉冲 ±0.6°，14 帧
 *       2 呼吸脉冲 +1.2%，10 帧
 *       3 闪一下   不透明度 0.92，4 帧
 *       4 小跳     向上 6px 再落回，10 帧
 *
 * 为什么要有 A：只有 B 的话事件之间是静止的，帧差会掉到 0，观感是「抽搐」而不是「丝滑」。
 * 为什么要有 B：只有 A 的话动作太平缓，8fps 采样的帧差峰值过不了 1.2 的检测门限，
 *              肉眼也只会觉得「好像有点飘」，不会有「画面一直在动」的节奏感。
 * 两者叠加 = 底座在流、上面有节拍。
 * ------------------------------------------------------------------ */
export type Idle = 'float' | 'wobble' | 'breathe' | 'flash' | 'hop' | 'jitter' | 'none';

/** 确定性哈希，0..1（同一 seed + 通道号永远同一个值，保证可重复渲染） */
const h01 = (seed: number, k: number) => {
  const v = Math.sin(seed * 127.1 + k * 311.7 + 0.5) * 43758.5453;
  return v - Math.floor(v);
};

/** 每个元素多久来一个离散事件（设计帧）。0.70–0.85s @30fps = 21–25.5 帧 */
export const IDLE_TICK_MIN = 21;
export const IDLE_TICK_MAX = 25.5;
/** 全局节奏倍率：1 = 每 0.70–0.85s 一个事件。调大 = 更慢更稳 */
export const IDLE_RATE = 1;
/** 事件幅度全局倍率 */
export const IDLE_AMP = 2.0;
/** 事件幅度全局倍率（调试用） */


/**
 * 2026-11-04 用户反馈「为什么画面元素要晃来晃去」——全部装饰性微动效下线。
 * 现在只有显式指定 kind 的元素才会动（给"显存爆了"这种语义故障用），
 * 其余元素一律静止，画面里的运动只允许来自"信息本身在变"
 * （数字滚动、格子点亮、进度条推进、元素入场）。
 */
export const idleStyle = (f: number, seed: number, kind?: Idle, amp = 3): React.CSSProperties => {
  if (!kind || kind === 'none') return {};
  const r = (k: number) => h01(seed, k);
  const k = (amp / 3) * IDLE_AMP;

  /* ---------- A. 连续通道 ---------- */
  const perF = 48 + r(11) * 18;                     // 1.6–2.2s
  const ampF = (3 + r(12) * 3) * k;                 // 3–6px
  const phF = r(13) * Math.PI * 2;
  const perR = 90 + r(14) * 30;                     // 3–4s
  const phR = r(15) * Math.PI * 2;
  const perB = 72;                                  // 2.4s
  const phB = r(16) * Math.PI * 2;

  let ty = Math.sin((f * 2 * Math.PI) / perF + phF) * ampF;
  let rot = Math.sin((f * 2 * Math.PI) / perR + phR) * 0.8;
  let sc = 1 + Math.sin((f * 2 * Math.PI) / perB + phB) * 0.015;
  let op = 1;

  /* ---------- B. 离散事件 ---------- */
  // 显式指定 kind 时，事件类型锁死为该种；节奏不变，否则该元素就掉队了
  const explicit = kind && kind !== 'float' ? kind : undefined;
  const per = (IDLE_TICK_MIN + r(21) * (IDLE_TICK_MAX - IDLE_TICK_MIN)) * IDLE_RATE;
  const ph = r(22) * per;
  const t = f + ph;
  const step = Math.floor(t / per);
  const local = t - step * per;
  // 类型按 step 轮转：同一元素相邻两次一定不是同一种，5 种齐全
  const type = explicit
    ? (explicit === 'jitter' ? 4 : explicit === 'wobble' ? 1 : explicit === 'breathe' ? 2 : explicit === 'flash' ? 3 : 0)
    : (Math.floor(r(23) * 5) + step) % 5;

  if (type === 0) {
    // 上浮 6px 再落回，12 帧
    ty -= Math.sin(Math.PI * Math.min(1, local / 12)) * 6 * k;
  } else if (type === 1) {
    // 旋转脉冲 1.0°，14 帧
    rot += Math.sin(Math.PI * Math.min(1, local / 14)) * 1.0;
  } else if (type === 2) {
    // 呼吸脉冲 +1.5%，10 帧
    sc += Math.sin(Math.PI * Math.min(1, local / 10)) * 0.015;
  } else if (type === 3) {
    // 闪一下：8% 透明度变化，4 帧
    op = local < 4 ? 0.92 : 1;
  } else {
    // 小跳：向上 10px 再落回，10 帧
    ty -= Math.sin(Math.PI * Math.min(1, local / 10)) * 10 * k;
  }

  const parts = [`translateY(${ty.toFixed(2)}px)`];
  if (Math.abs(rot) > 0.01) parts.push(`rotate(${rot.toFixed(3)}deg)`);
  if (Math.abs(sc - 1) > 0.0005) parts.push(`scale(${sc.toFixed(4)})`);
  return {transform: parts.join(' '), transformOrigin: 'center center', opacity: op};
};

export const Bob: React.FC<{seed?: number; amp?: number; kind?: Idle; children: React.ReactNode}> = ({seed = 0, amp = 3, kind, children}) => {
  const f = useDesignFrame();
  return <div style={idleStyle(f, seed, kind, amp)}>{children}</div>;
};

/** 闪烁 */
export const Blink: React.FC<{period?: number; children: React.ReactNode}> = ({period = 30, children}) => {
  const f = useDesignFrame();
  return <div style={{display: 'inline-block', opacity: f % period < period * 0.7 ? 1 : 0.25}}>{children}</div>;
};
/** 小人：每 ~1s 轻弹、每 2.5s 眨眼、按 poses 时间表在思考/指向间切换（切换时 6 帧挤压） */
const EYES = {think: [[98, 138, 30, 20], [153, 142, 36, 18]], point: [[128, 143, 24, 22], [168, 146, 28, 20]]};
/** 眨眼时间表：间隔 2–5s 随机，约 1/5 概率连眨两下；每次 4 帧：半闭→闭→闭→半闭 */
const blinkState = (f: number, seed = 1) => {
  let t = 20 + seed * 7; let i = 0;
  while (t <= f + 4) {
    const v = Math.sin((i + 1) * 12.99 + seed * 7.1) * 43758.5; const r = v - Math.floor(v);
    const marks = r < 0.2 ? [t, t + 7] : [t];
    for (const m of marks) { const d = f - m; if (d >= 0 && d < 4) return d === 0 || d === 3 ? 0.5 : 1; }
    t += 60 + Math.floor(r * 90); i++;
  }
  return 0;
};
export const Kid: React.FC<{h: number; poses: [number, 'think' | 'point'][]; flip?: boolean; seed?: number}> = ({h, poses, flip, seed = 1}) => {
  const f = useDesignFrame();
  let pose: 'think' | 'point' = poses[0][1]; let since = 0;
  for (const [t, p] of poses) if (f >= t) { pose = p; since = t; }
  const nat = pose === 'think' ? 248 : 392; const k = h / 640; const w = nat * k;
  // 2026-11-04 用户反馈「为什么画面元素要晃来晃去」：小人的持续轻弹已去掉。
  // 只保留入场/换姿势时的挤压（sq），那是有语义的、一次性的。
  const hop = 0;
  const sq = f - since < 6 ? 1 - 0.08 * Math.sin(Math.PI * (f - since) / 6) : 1;
  const b = blinkState(f, seed);
  return (
    <div style={{position: 'relative', width: w, transform: `translateY(${-hop}px) scaleY(${sq})`, transformOrigin: 'bottom center'}}>
      <Sprite name={pose === 'think' ? 'kid_think' : 'kid_point'} w={w} flip={flip} />
      {b > 0 && EYES[pose].map(([x, y, ew, eh], i) => <div key={i} style={{position: 'absolute', left: (flip ? nat - x - ew : x) * k, top: y * k, width: ew * k, height: eh * k * b, background: m('skin'), borderBottom: `${Math.max(2, 3 * k)}px solid var(--m-ink)`}} />)}
    </div>
  );
};

/** codex v2 显卡 + 代码画的风扇转动层（风扇中心实测 (186,140)/(420,140)，半径约 92，原图 576×312） */
export const FanLayer: React.FC<{r: number; speed?: number}> = ({r, speed = 1}) => {
  const f = useDesignFrame(); const n = 23, px = (2 * r) / n, c = (n - 1) / 2;
  const cells: React.ReactNode[] = [];
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    const dx = x - c, dy = y - c, d = Math.hypot(dx, dy);
    if (d > c) continue;
    let col = m('dark-bg');
    if (d > c - 1) col = m('ink');
    else if (d < 2.2) col = m('metal');
    else { // 2026-11-04 扇叶从 0.35rad/帧（约 0.6s 一圈，视觉上就是频闪）放慢到 0.05rad/帧（4.2s 一圈，看得出是风扇在转）
    const a = Math.atan2(dy, dx) + d * 0.12 + f * 0.05 * speed; const sec = ((a % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2) / (Math.PI * 2 / 7); if (sec % 1 < 0.55) col = sec % 1 < 0.15 ? m('fan-hot') : m('orange'); }
    cells.push(<rect key={x + '-' + y} x={x * px} y={y * px} width={px + 0.4} height={px + 0.4} fill={col} />);
  }
  return <svg width={2 * r} height={2 * r} shapeRendering="crispEdges" style={{display: 'block'}}>{cells}</svg>;
};
export const GpuCard: React.FC<{w: number; mute?: boolean; speed?: number}> = ({w, mute, speed = 1}) => {
  const k = w / 576, r = 90 * k;
  return (
    <div style={{position: 'relative', width: w, filter: mute ? 'saturate(0.25) sepia(0.2)' : undefined}}>
      <Sprite name="gpu" w={w} />
      {[186, 420].map((cx) => <div key={cx} style={{position: 'absolute', left: cx * k - r, top: 140 * k - r}}><FanLayer r={r} speed={speed} /></div>)}
    </div>
  );
};

/** 全片进度：嵌进整片时由外层告诉自己的起点和总长 */
export const ProgCtx = React.createContext<{start: number; total: number; count: number}>({start: 0, total: 1, count: 0});
export const useProg = (f: number) => { const c = React.useContext(ProgCtx); return (c.start + f) / c.total; };

export const D1 = total(C1), D2 = total(C2), D3 = Math.max(84, total(C3)), D4 = total(C4);
export const MOTION_TOTAL = D1 + D2 + D3 + D4;

export const MPop: React.FC<React.ComponentProps<typeof Pop> & {idle?: Idle}> = (p) => <Pop {...p}><Bob seed={p.x * 0.37 + p.y * 0.11 + p.at * 0.013} kind={p.idle}>{p.children}</Bob></Pop>;
export const S1: React.FC = () => {
  const f = useDesignFrame();
  const mem0 = Math.round(40 + 58 * prog(f, at(C1, 4), 45, easeOut)); const mem = mem0 >= 98 ? 97 + (Math.floor(f / 7) % 3) : mem0;
  return (
    <AbsoluteFill><FontFace /><SpriteBg name="bg_paper" fallback={<PaperBg />} /><Dust n={8} />
      <MPop at={0} x={500} y={100}><Pulse at={at(C1, 1)}><div style={{display: 'flex', gap: 24, alignItems: 'center', background: P.plate, padding: '16px 40px', boxShadow: 'var(--t-shadow-8-a20)'}}><BoltSprite px={8} /><span style={{fontFamily: FONT, fontSize: 100, color: P.gold}}>FlashAttention</span></div></Pulse></MPop>
      <MPop at={10} x={1340} y={110}><Sprite name="qblock" w={128} /></MPop>
      <MPop at={at(C1, 1)} x={620} y={300}><div style={{position: 'relative'}}><NeuralNet cols={[4, 6, 6, 6, 4]} w={680} h={400} />{Array.from({length: 6}).map((_, i) => <div key={i} style={{position: 'absolute', left: ((f * 6 + i * 113) % 640), top: 40 + ((i * 67) % 320), width: 12, height: 12, background: [P.orange, K_GREEN, P.gold][i % 3]}} />)}</div></MPop>
      <MPop at={at(C1, 1, 20)} x={440} y={380}><div style={{display: 'flex', flexDirection: 'column', gap: 16}}>{['token_q', 'token_k', 'token_v'].map((n, i) => <div key={i} style={{display: 'flex', alignItems: 'center', gap: 10, }}><span style={{fontFamily: FONT, fontSize: 32, color: P.text}}>{'QKV'[i]}</span><Sprite name={n} w={64} /></div>)}</div></MPop>
      <Pop at={at(C1, 2)} x={190} y={660}><Kid h={320} poses={[[0, 'think'], [atT(C1, '显存爆了'), 'point'], [atT(C1, '挤牙膏'), 'think']]} /></Pop>
      <MPop at={at(C1, 3)} x={1360} y={640}><GpuCard w={300} mute speed={1.3} /></MPop>
      <MPop at={at(C1, 3, 10)} x={1700} y={680}><div style={{display: 'flex', gap: 6}}>{[0, 1].map((i) => <Sprite key={i} name="rack" w={54} mute />)}</div></MPop>
      <MPop at={at(C1, 4)} x={1340} y={380} idle="jitter"><Pulse at={at(C1, 4, 45)}><div style={{background: P.tokenBg, border: `5px solid ${P.stroke}`, padding: '14px 20px', boxShadow: 'var(--t-shadow-6)'}}>
        <div style={{fontFamily: FONT, fontSize: 32, color: P.text}}>显存 <Blink period={20}><span style={{color: P.heart}}>{mem > 90 ? '!' : ''}</span></Blink></div>
        <div style={{fontFamily: FONT, fontSize: 80, color: mem > 90 ? P.heart : P.text, lineHeight: 1}}>{mem}%</div>
        <div style={{width: 220, height: 22, background: m('panel'), marginTop: 8}}><div style={{width: 2.2 * mem, height: 22, background: P.heart}} /></div>
      </div></Pulse></MPop>
      <MPop at={at(C1, 4, 20)} x={110} y={610}><div style={{background: P.bubble, border: `4px solid ${P.stroke}`, padding: '4px 12px', fontFamily: FONT, fontSize: 24}}>又爆显存了？</div></MPop>
      <MPop at={at(C1, 6)} x={1640} y={560}><div style={{display: 'flex', alignItems: 'center', gap: 8}}><ClockSprite px={5} /><span style={{fontFamily: FONT, fontSize: 28, color: P.text}}>挤牙膏…</span></div></MPop>
      <Frame progress={useProg(f)} count={0} name={NAME} />
      <CueSub cues={C1} keys={['FlashAttention', '显存爆了', '挤牙膏']} />
    </AbsoluteFill>
  );
};

export const S2: React.FC = () => {
  const f = useDesignFrame();
  const n = (7.6 * prog(f, at(C2, 6), 30, easeOut)).toFixed(1);
  const L = 820, R = 1250, Y = 600;
  const flowOn = f > at(C2, 3);
  return (
    <AbsoluteFill><FontFace /><SpriteBg name="bg_paper" fallback={<PaperBg />} /><Dust n={8} seed={3} />
      <MPop at={0} x={110} y={340}><Sprite name="warehouse" w={720} mute /></MPop>
      <MPop at={at(C2, 1)} x={1250} y={470}><Sprite name="bench" w={460} clipTop={0.3} mute /></MPop>
      <MPop at={at(C2, 1, 12)} x={620} y={100}><Label text="算得慢？" size={44} bg="var(--m-slate)" /></MPop>
      <MPop at={at(C2, 3)} x={880} y={100}><div style={{display: 'flex', gap: 16, alignItems: 'center'}}><span style={{fontFamily: FONT, fontSize: 48, color: P.heart}}>✕</span><Pulse at={at(C2, 3, 12)}><Label text="搬得慢！" size={44} bg={P.orange} /></Pulse></div></MPop>
      <MPop at={at(C2, 2)} x={200} y={720}><Label text="HBM 显存 · 40–80GB · 大但远" size={30} /></MPop>
      <MPop at={at(C2, 2, 15)} x={1270} y={720}><Label text="SRAM 片上 · 192KB · 快但小" size={30} bg={P.teal} /></MPop>
      {flowOn && <svg style={{position: 'absolute', left: L, top: Y}} width={R - L} height={40} shapeRendering="crispEdges">
        <rect x={0} y={4} width={(R - L) * prog(f, at(C2, 3), 12, easeOut)} height={32} fill="var(--m-rail)" /><rect x={0} y={0} width={R - L} height={4} fill={P.stroke} /><rect x={0} y={36} width={R - L} height={4} fill={P.stroke} />
        {Array.from({length: 14}).map((_, i) => <rect key={i} x={((i * 34 + f * 4) % (R - L))} y={18} width={16} height={4} fill="var(--m-wood-dark)" />)}
      </svg>}
      {flowOn && Array.from({length: 5}).map((_, i) => { const t = ((f - at(C2, 3)) / 70 + i / 5) % 1; return <div key={i} style={{position: 'absolute', left: L + t * (R - L - 52), top: Y - 44}}><Sprite name={['token_q', 'token_k', 'token_v'][i % 3]} w={52} /></div>; })}
      <MPop at={at(C2, 4)} x={900} y={660}><Blink period={24}><Label text="少搬" size={40} bg={P.plate} color={P.gold} /></Blink></MPop>
      <MPop at={at(C2, 6)} x={1560} y={140}><Pulse at={at(C2, 6, 30)}><div style={{background: P.tokenBg, border: `4px solid ${P.stroke}`, padding: '8px 16px', boxShadow: 'var(--t-shadow-6)'}}>
        <div style={{fontFamily: FONT, fontSize: 20, color: m('muted')}}>注意力 · GPT-2</div>
        <div style={{fontFamily: FONT, fontSize: 64, color: P.heart, lineHeight: 1}}>{n}×</div>
        <div style={{fontFamily: FONT, fontSize: 16, color: m('muted')}}>arXiv:2205.14135</div>
      </div></Pulse></MPop>
      <MPop at={at(C2, 7)} x={1580} y={330}><Label text="训练 3×" size={34} bg={P.heart} /></MPop>
      <Pop at={at(C2, 0, 10)} x={1480} y={740}><Kid h={320} flip poses={[[0, 'think'], [atT(C2, '其实不一定'), 'point'], [atT(C2, '论文里'), 'think'], [atT(C2, '训练快了'), 'point']]} /></Pop>
      <Frame progress={useProg(f)} count={0} name={NAME} />
      <CueSub cues={C2} keys={['算得慢', '搬得慢', '少搬', '7.6倍', '3倍']} />
    </AbsoluteFill>
  );
};

/** 章节卡：星空 + 星座点到第 N 颗 + STAGE N + 闪白（2.8s）
 *  卡点：标题框在每小节首拍轻弹一下（1.0 → 1.04），和 BGM 的重音同一帧。 */
export const Card: React.FC<{stage: number; title: string; cues: Cue[]; keys?: string[]}> = ({stage, title, cues, keys = []}) => {
  const f = useDesignFrame();
  const p = prog(f, 0, 12, easeOutBack);
  // 小节首拍脉动：6 帧衰减，峰值 1.04 倍，只弹不发散
  const beat = useBeatPulse(1, 6, true);
  const stars = [[160, 620], [330, 470], [520, 540], [700, 380], [900, 300], [1110, 340], [1300, 230], [1500, 300], [1700, 200]];
  const lit = Math.min(stage, 9); const draw = prog(f, 4, 16, easeOut);
  // 静置段的三条动作源（章节卡是 4s 静场，不加这些整段帧差只有 0.1，会把全片密度拖死）：
  //   1) 星座节点按拍依次「点名」——每拍点亮一颗，依次弹到 1.7 倍再落回
  //   2) 一道扫描光带横穿星空（1.6s 一趟），照亮它经过的那一列星星
  //   3) 标题框上下浮 4px（周期 2s）
  const beatPhase = (f % 15) / 15;
  // 扫光带按拍跳格（不是匀速滑过）：匀速滑动在帧差曲线上是一条平台，
  // 没有局部极大值，质检数不出事件；跳格每跳一次就是一个可辨识的动作。
  const sweepStep = Math.floor(f / 15) % 9;
  const sweepX = sweepStep * 225 - 160;
  return (
    <AbsoluteFill><FontFace />
      <StarBg />
      <Sfx at={0} dur={6} file="sfx/cut.wav" volume={0.3} />
      <Sfx at={20} dur={14} file="sfx/flash.wav" volume={0.25} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 760, height: 320, background: 'rgba(40,44,80,.55)'}} />
      {/* 扫描光带：竖向渐变亮带，横穿画面，本身也是「画面在动」的强信号 */}
      <div style={{position: 'absolute', left: sweepX, top: 0, width: 160, height: 1080, pointerEvents: 'none',
        background: `linear-gradient(90deg, rgba(242,193,78,0) 0%, rgba(242,193,78,.10) 45%, rgba(255,255,255,.16) 50%, rgba(242,193,78,.10) 55%, rgba(242,193,78,0) 100%)`}} />
      <svg style={{position: 'absolute', left: 0, top: 0}} width={1920} height={1080} shapeRendering="crispEdges">
        {stars.slice(0, lit - 1).map(([x, y], i) => { const [x2, y2] = stars[i + 1]; const n = i < lit - 2 ? 12 : Math.round(12 * draw);
          // 扫描带经过这一段时，点变白变粗
          const midx = (x + x2) / 2, hot = Math.abs(midx - (sweepX + 80)) < 130;
          const sz = hot ? 9 : 6;
          return Array.from({length: n}).map((_, k) => <rect key={`${i}-${k}`} x={x + (x2 - x) * k / 12} y={y + (y2 - y) * k / 12} width={sz} height={sz} fill={hot ? P.white : P.gold} />); })}
        {stars.map(([x, y], i) => { const on = i < lit - 1 || (i === lit - 1 && draw >= 1);
          // 已点亮节点：按拍序依次点名，弹 1.7 倍（每颗错开 0.19 拍）
          const k = 1;
          const tw = on ? 1 : 0.6;
          const wv = 48 * k, hv = 16 * k;
          return <g key={i} opacity={tw}><rect x={x - wv / 2} y={y - hv / 4} width={wv} height={hv / 2} fill={on ? P.gold : m('night')} /><rect x={x - hv / 4} y={y - wv / 2} width={hv / 2} height={wv} fill={on ? P.gold : m('night')} /></g>; })}
        <circle cx={stars[lit - 1][0]} cy={stars[lit - 1][1]} r={34} fill={P.gold} opacity={0.20} />
      </svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: 620, textAlign: 'center', opacity: Math.min(1, p * 2)}}>
        <div style={{display: 'inline-block', padding: '14px 70px 18px', border: `4px solid ${P.gold}`, background: 'rgba(30,27,37,.92)', fontFamily: FONT,
          transform: `scale(${0.8 + 0.2 * p})`}}>
          <div style={{fontSize: 40, color: P.orange}}>STAGE {stage}</div>
          <div style={{fontSize: 96, color: P.white, lineHeight: 1.05, display: 'inline-block', transformOrigin: 'center center'}}>{title}</div>
        </div>
      </div>
      <Frame progress={useProg(f)} count={stage} name={NAME} dark />
      <AbsoluteFill style={{background: m('white'), opacity: f < 20 ? 0 : f < 22 ? 0.85 : Math.max(0, 0.85 - (f - 22) * 0.14), pointerEvents: 'none'}} />
      <CueSub cues={cues} keys={keys} />
    </AbsoluteFill>
  );
};
const S3: React.FC = () => <Card stage={4} title="分块" cues={C3} keys={['分块']} />;

/** 窗口：b 之后 8 帧淡出再卸载 */
export const Fade: React.FC<{b: number; children: React.ReactNode}> = ({b, children}) => {
  const f = useDesignFrame(); if (f >= b + 8) return null;
  return <div style={{opacity: f < b ? 1 : 1 - (f - b) / 8}}>{children}</div>;
};
export const S4: React.FC = () => {
  const f = useDesignFrame();
  const B = atT(C4, '一次只从');
  const W = atT(C4, '做完这一块'), N = atT(C4, 'N乘N'), M = atT(C4, '而且这几步'), H = atT(C4, '中间结果'), Z = atT(C4, '这种把');
  const fly = prog(f, B, 18, easeOut);
  const hbm = Array.from({length: 24}).map((_, i) => (i * 7) % 3 === 0 ? m('hbm-dark') : m('cream-dark'));
  const tile = Math.floor(Math.max(0, f - at(C4, 1)) / 20) % 4;
  const step = Math.floor((f - atT(C4, '把打分')) / 12);
  const outN = Math.max(0, Math.min(4, Math.floor((f - W) / 20) + 1)) * (f >= W ? 1 : 0);
  const blockP = f < W ? prog(f, atT(C4, '把打分'), 60) : ((f - W) % 40) / 40; // 每块进度 0→100 循环
  const merge = prog(f, M + 10, 14, easeOut);
  const glow = f >= H && Math.floor(f / 8) % 2 === 0;
  const lit = (i: number) => i < 3 ? (f > B + 18 ? [P.orange, K_GREEN, P.gold][i] : m('metal')) : (f >= H ? m('lit-violet') : m('metal'));
  return (
    <AbsoluteFill><FontFace /><SpriteBg name="bg_dark_grid" fallback={<DarkGridBg />} /><Dust n={10} dark seed={5} />
      <MPop at={0} x={150} y={140}><span style={{fontFamily: FONT, fontSize: 60, color: m('dark-text')}}>GPU</span></MPop>
      {f < B && <>
        <MPop at={0} x={180} y={250}><div style={{display: 'grid', gridTemplateColumns: 'repeat(6, 112px)', gap: 12, background: '#2b2838', padding: 14}}>{hbm.map((c, i) => <Cell key={i} c={f > at(C4, 1) && Math.floor(i / 6) === tile ? [P.orange, K_GREEN, P.gold][i % 3] : c} s={112} />)}</div></MPop>
        <MPop at={at(C4, 1, 10)} x={280} y={780}><Label text="切成一个个小块" size={48} /></MPop>
        <MPop at={at(C4, 0, 15)} x={1000} y={220}><div style={{position: 'relative', background: '#2b2838', padding: 20}}><Sprite name="matrix" w={540} /><div style={{position: 'absolute', inset: -10, border: '6px dashed var(--m-grey-light)'}} /></div></MPop>
        <MPop at={at(C4, 0, 30)} x={1010} y={800}><Label text="整张 N×N 大表：不搬" size={48} bg="var(--m-panel)" /></MPop>
        <svg style={{position: 'absolute', left: 180, top: 230}} width={540} height={8}>{Array.from({length: 6}).map((_, i) => <rect key={i} x={(i * 90 + f * 3) % 540} y={0} width={30} height={6} fill="var(--m-track)" />)}</svg>
      </>}
      <Sfx at={B} dur={6} file="sfx/cut.wav" volume={0.3} />
      {f >= B && <>
        {/* v3.1 填充：右列实心底板 + 左下 HBM 分块图 */}
        <svg style={{position: 'absolute', left: 1380, top: 190}} width={500} height={640} shapeRendering="crispEdges"><rect width={500} height={640} fill="#2b2838" />
          {Array.from({length: 10 * 13}).map((_, i) => { const c = i % 10, r = Math.floor(i / 10); const on = ((c + r + Math.floor(f / 6)) % 7) === 0;
            return <rect key={i} x={8 + c * 49} y={8 + r * 48.5} width={43} height={42} fill={on ? '#6a5a9a' : (c + r) % 2 ? '#3a3650' : '#443f5e'} />; })}</svg>
        <BlockStrip f={f - B} total={D4 - B} stage={4} x={140} y={600} w={360} h={250} title="N×N 分块 · 逐块上片" />
        {/* 左：HBM 显存条，输出块一块块落回去 */}
        <Fade b={M}><MPop at={B} x={140} y={240}><div style={{width: 300, background: m('panel'), border: `5px solid ${P.stroke}`, padding: 16}}>
          <div style={{fontFamily: FONT, fontSize: 36, color: m('dark-text')}}>HBM 显存</div>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 56px)', gap: 10, marginTop: 14}}>{Array.from({length: 12}).map((_, i) => <Cell key={i} c={i < outN ? m('dark-cell-lit') : m('grey')} s={56} />)}</div>
          <svg width={260} height={10} style={{marginTop: 12}}>{Array.from({length: 4}).map((_, i) => <rect key={i} x={(i * 70 + f * 3) % 260} y={0} width={28} height={8} fill="var(--m-grey-light)" />)}</svg>
        </div></MPop></Fade>
        {/* 中：SRAM */}
        <MPop at={B} x={520} y={200}><div style={{width: 820, height: 520, background: m('dark-surface'), border: `6px solid ${glow ? P.gold : P.stroke}`, padding: 30, boxSizing: 'border-box', boxShadow: 'var(--t-shadow-deep-10)'}}>
          <div style={{fontFamily: FONT, fontSize: 40, color: P.gold}}>SRAM 片上 · 192KB</div>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 140px)', gap: 24, marginTop: 30}}>{Array.from({length: 8}).map((_, i) => <Cell key={i} c={lit(i)} s={140} />)}</div>
        </div></MPop>
        <div style={{position: 'absolute', left: 200 + fly * 400, top: 600 - fly * 260, display: 'flex', gap: 10, opacity: f > B + 18 ? 0 : 1}}>{['token_q', 'token_k', 'token_v'].map((n) => <Sprite key={n} name={n} w={72} />)}</div>
        {/* 写回：输出块从 SRAM 飞回 HBM */}
        {f >= W && f < N + 40 && (() => { const t = ((f - W) % 20) / 20; return <div style={{position: 'absolute', left: 560 - t * 260, top: 560 - t * 120, width: 56, height: 56, background: m('dark-cell-lit'), border: `4px solid ${P.stroke}`}} />; })()}
        {/* 底：三步 → 合并成一个算子 */}
        <Fade b={W}><MPop at={atT(C4, '把打分')} x={540} y={760}><div style={{display: 'flex', gap: 14}}>{['打分', 'softmax', '×V'].map((t, i) => <div key={i} style={{fontFamily: FONT, fontSize: 40, color: P.white, background: i <= step ? P.teal : m('panel'), padding: '8px 20px', border: `4px solid ${P.stroke}`}}>{t}</div>)}</div></MPop></Fade>
        {f >= M && <MPop at={M} x={540} y={760}><div style={{position: 'relative', width: 820, height: 80}}>
          {['打分', 'softmax', '×V'].map((t, i) => <div key={i} style={{position: 'absolute', top: 0, left: (1 - merge) * i * 200 + merge * 260, opacity: merge > 0.9 && i > 0 ? 0 : 1, fontFamily: FONT, fontSize: 40, color: P.white, background: P.teal, padding: '8px 20px', border: `4px solid ${P.stroke}`}}>{t}</div>)}
          {merge > 0.9 && <div style={{position: 'absolute', top: 0, left: 260}}><Pulse at={M + 24}><div style={{fontFamily: FONT, fontSize: 40, color: P.text, background: P.gold, padding: '8px 24px', border: `4px solid ${P.stroke}`}}>1 个 GPU 算子</div></Pulse></div>}
        </div></MPop>}
        {/* 右列 */}
        <Fade b={N}><MPop at={atT(C4, '把打分', 10)} x={1400} y={210}><div style={{fontFamily: FONT, fontSize: 36, color: m('cream')}}>本块进度 {Math.round(blockP * 100)}%</div><div style={{width: 420, height: 44, background: m('cream'), border: `5px solid ${P.stroke}`, marginTop: 8}}><div style={{width: 410 * blockP, height: 34, background: P.gold}} /></div></MPop></Fade>
        {f >= W && <Fade b={H}><MPop at={W} x={1400} y={350}><Label text={`输出写回 ×${outN}`} size={48} bg="var(--m-teal-bright)" /></MPop></Fade>}
        {f >= N && <Fade b={Z}><MPop at={N} x={1420} y={470}><div style={{position: 'relative', width: 200}}><div style={{opacity: 0.35, filter: 'grayscale(1)'}}><Sprite name="matrix" w={200} /></div>
          <div style={{position: 'absolute', left: 30, top: 10, fontFamily: FONT, fontSize: 150, lineHeight: 1, color: P.heart, transform: `scale(${1 + 0.3 * (1 - prog(f, N + 4, 8, easeOutBack))})`}}>✕</div></div>
          <div style={{fontFamily: FONT, fontSize: 34, color: m('cream'), marginTop: 8}}>N×N 不落显存</div></MPop></Fade>}
        {f >= H && <MPop at={H} x={1100} y={118}><Blink period={16}><Label text="中间结果留在片上" size={36} bg={P.plate} color={P.gold} /></Blink></MPop>}
        {f >= Z && <MPop at={Z} x={1620} y={720}><Pulse at={Z + 40}><Label text="分块" size={72} bg={P.plate} color={P.gold} /></Pulse></MPop>}
      </>}
      <ChapterTab stage={4} prog={useProg(f)} />
      <Frame progress={useProg(f)} count={4} name={NAME} dark />
      <CueSub cues={C4} keys={['小块', 'SRAM', '一口气做完', '不落到显存', 'GPU算子', '片上', '分块']} />
    </AbsoluteFill>
  );
};

export type Seg = {id: string; dur: number; node: React.ReactNode; count: number; cut?: boolean};
/** 硬切串联：每段一个 Sequence，段首配切镜音（章节卡自带） */
export const Timeline: React.FC<{segs: Seg[]}> = ({segs}) => {
  const {fps} = useVideoConfig();
  const tot = segs.reduce((a, s) => a + s.dur, 0); let t = 0;
  return (
    <AbsoluteFill style={{background: m('black')}}>
      {segs.map((s, i) => { const from = t; t += s.dur; return (
        <Sequence key={s.id + i} from={Math.round((from * fps) / 30)} durationInFrames={Math.round((s.dur * fps) / 30)}>
          <ProgCtx.Provider value={{start: from, total: tot, count: s.count}}>
            {/* 段首设计帧：拍点脉动/吸附要用整片绝对坐标，见 timeline/fps.tsx */}
            <SegStartCtx.Provider value={from}>
              {s.cut !== false && i > 0 && <Sfx at={0} dur={6} file="sfx/cut.wav" volume={0.3} />}
              {s.node}
            </SegStartCtx.Provider>
          </ProgCtx.Provider>
        </Sequence>
      ); })}
    </AbsoluteFill>
  );
};
export const MOTION_SEGS: Seg[] = [
  {id: 'K1', dur: D1, node: <S1 />, count: 0},
  {id: 'K2', dur: D2, node: <S2 />, count: 0},
  {id: 'K3', dur: D3, node: <S3 />, count: 4, cut: false},
  {id: 'K4', dur: D4, node: <S4 />, count: 4},
];
export const MotionPreview: React.FC = () => <Timeline segs={MOTION_SEGS} />;
