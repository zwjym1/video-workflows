// ①–⑨ + 结尾：逐镜定制构图（自由坐标，插图为主，小人走位/指向/搬运），时间轴跟配音逐字时间戳
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {useDesignFrame, Sfx} from './timeline/fps';
import {Frame, FontFace, P, PaperBg, DarkGridBg, m, useEnter, BgSweep} from './kit';
import {Sprite, SpriteBg} from './Sprite';
import {Dust, Cell} from './sprites';
import {prog, easeInOut} from './lib/anim';
import {gridSegs} from './timeline/grid';
import {useSnapToBeat} from './components/BeatSync';
import {makeCues, Cue, CueSub, Kid, idleStyle, Idle, ProgCtx, useProg, Card, Timeline, Seg, S1, S2, S4, D1, D2, D4, NAME} from './Motion';
import * as W from './W';
import {CARD_BURST, BurstWall, BurstKind, BigCard, DataPanel, ChapterTab, BlockStrip} from './Dense';

/** v3：每镜内的全屏爆点（镜内本地帧），由下方 FINAL_SEGS 排程 */
export const BURSTS: Record<string, {at: number; kind: BurstKind; cap: string}[]> = {};
const BURST_DUR = 54;


type F = (t: number) => React.ReactNode;
type It = {k: string; x: number; y: number; f: F; s?: number; until?: string; idle?: Idle; off?: number};
type Act = {k: string; x: number; pose: 'think' | 'point'; flip?: boolean; carry?: string};
type Shot = {lines: string[]; dark?: boolean; strip?: boolean; keys?: string[]; its: It[]; kid: Act[]};
const KG = m('green');
const I = (k: string, x: number, y: number, f: F, o: Partial<It> = {}): It => ({k, x, y, f, ...o});
const A = (k: string, x: number, pose: 'think' | 'point', flip = false, carry?: string): Act => ({k, x, pose, flip, carry});

const startOf = (cues: Cue[], k: string) => { const c = cues.find((x) => x.text.includes(k)); if (!c) throw new Error('key not found: ' + k); return c.from; };

const ItView: React.FC<{it: It; at: number; end: number; seed: number; snap?: boolean}> = ({it, at, end, seed, snap}) => {
  const f = useDesignFrame();
  // 卡点：每镜第一个元素（语义主体）入场吸到拍点，容差 3 帧 = 100ms。超出容差原样不动。
  // 必须无条件调用 hook（不能写在三元里），否则同一组件在不同帧的 hook 顺序会变。
  const snapped = useSnapToBeat(at, 3);
  const atS = snap ? snapped : at;
  const enter = useEnter();
  const p = prog(f, atS, enter.frames, enter.ease); const out = f >= end ? (f - end) / 8 : 0;
  return (<>
    <Sfx at={atS} dur={6} file="sfx/pop.wav" volume={0.12} />
    {f >= atS && out < 1 && <div style={{position: 'absolute', left: it.x, top: it.y, opacity: Math.min(1, p * 2) * (1 - out), transform: `translateY(${(1 - p) * 40}px) scale(${(0.6 + 0.4 * p) * (it.s ?? 1) * ZOOM})`, transformOrigin: 'top left'}}>
      <div style={idleStyle(f, seed, it.idle, 3)}>{it.f(f - atS)}</div>
    </div>}
  </>);
};

/** 小人走位：到点后 16 帧走到新 x（快跳步），然后摆姿势；carry 时头顶扛一个色块 */
const Actor: React.FC<{acts: (Act & {at: number})[]; seed: number}> = ({acts, seed}) => {
  const f = useDesignFrame();
  let cur = acts[0], prevX = acts[0].x, since = 0;
  for (let i = 0; i < acts.length; i++) if (f >= acts[i].at) { cur = acts[i]; prevX = i > 0 ? acts[i - 1].x : acts[i].x; since = acts[i].at; }
  const w = prog(f, since, 16, easeInOut); const x = prevX + (cur.x - prevX) * w; const walking = w > 0 && w < 1 && prevX !== cur.x;
  const flip = walking ? cur.x < prevX : !!cur.flip;
  const poses: [number, 'think' | 'point'][] = [[0, walking ? 'think' : cur.pose]];
  return (
    <div style={{position: 'absolute', left: x, top: 600 - (walking ? Math.abs(Math.sin(f * 0.6)) * 14 : 0)}}>
      {cur.carry && <div style={{position: 'absolute', left: 30, top: -50}}><Cell c={cur.carry} s={56} /></div>}
      <Kid h={280} poses={poses} flip={flip} seed={seed} />
    </div>
  );
};

const ZOOM = 1.15;
const ShotView: React.FC<{s: Shot; seed: number; id: string; stage: number}> = ({s, seed, id, stage}) => {
  const f = useDesignFrame(); const ctx = React.useContext(ProgCtx);
  const cues = makeCues(s.lines);
  const st = s.its.map((it) => startOf(cues, it.k) + (it.off ?? 0));
  const en = s.its.map((it) => (it.until ? startOf(cues, it.until) : 1e9));
  const acts = s.kid.map((a) => ({...a, at: startOf(cues, a.k)}));
  if (acts.length) acts[0].at = 0;
  return (
    <AbsoluteFill><FontFace />
      {s.dark ? <SpriteBg name="bg_dark_grid" fallback={<DarkGridBg />} /> : <SpriteBg name="bg_paper" fallback={<PaperBg />} />}
      <Dust n={10} dark={s.dark} seed={seed} />
      {/* 2026-11-04 背景扫光带去掉：整屏横竖两条亮带一直在跳，属于无意义装饰 */}
      {/* 布景层：机房地台 + 两侧机柜 + 底部显卡排，压暗做背景，提高画面密度 */}
      <div style={{position: 'absolute', left: 0, top: 878, width: 1920, height: 10, background: s.dark ? m('panel') : m('dot')}} />
      <div style={{position: 'absolute', left: 30, top: 720, opacity: s.dark ? 0.35 : 0.45}}><Sprite name="rack" w={88} mute /></div>
      <div style={{position: 'absolute', left: 1810, top: 700, opacity: s.dark ? 0.35 : 0.45}}><Sprite name="rack" w={92} mute /></div>
      <div style={{position: 'absolute', left: 700, top: 830, opacity: s.dark ? 0.16 : 0.2}}><Sprite name="gpu_row" w={520} mute /></div>
      {s.its.map((it, i) => <ItView key={i} it={it} at={st[i]} end={en[i]} seed={seed * 7 + i * 3.3} snap={i === 0} />)}
      {s.strip && <BlockStrip f={f} total={cues[cues.length - 1].from + cues[cues.length - 1].dur} stage={stage} />}
      {acts.length > 0 && <Actor acts={acts} seed={seed} />}
      <ChapterTab stage={Math.max(1, stage)} prog={useProg(f)} />
      <DataPanel stage={Math.max(1, stage)} cue={Math.max(0, cues.findIndex((c) => f >= c.from && f < c.from + c.dur))} cues={cues.length} prog={useProg(f)} dark={s.dark} />
      {(BURSTS[id] ?? []).map((b, i) => f >= b.at && f < b.at + BURST_DUR ? <BurstWall key={i} kind={b.kind} t={f - b.at} dur={BURST_DUR} stage={Math.max(1, stage)} caption={b.cap} seed={seed * 5 + i} /> : null)}
      <Frame progress={useProg(f)} count={ctx.count} name={NAME} dark={s.dark} />
      <CueSub cues={cues} keys={s.keys ?? []} />
    </AbsoluteFill>
  );
};

const HOOK3: Shot = {lines: ['而且不是近似，算出来的结果和原来一模一样。', '那么问题就来了，数据到底搬到哪去了？为什么搬得慢？FlashAttention|又是怎么做到少搬的？'], keys: ['一模一样', '少搬'], its: [
  I('不是近似', 200, 150, W.label('不是近似', P.teal, 60), {until: '问题就来了'}),
  I('一模一样', 200, 280, W.same('原版', 'Flash 版'), {s: 1.3, until: '问题就来了'}),
  I('问题就来了', 260, 200, W.qblocks(['搬到哪？', '为什么慢？', '怎么少搬？']), {s: 1.5}),
], kid: [A('不是近似', 1250, 'think'), A('一模一样', 1250, 'point', true), A('问题就来了', 1300, 'point', true)]};

type Ch = {stage: number; title: string; card: string; shots: Shot[]};
export const CH: Ch[] = [
  {stage: 1, title: '注意力', card: '注意力是什么？', shots: [
    {lines: ['我们知道，大模型读一句话，会把每个Token算成三组数，叫Q、K、V。', '每个Token都要拿自己的Q，去和所有Token的K比一遍，算出该重点关注谁。'], keys: ['Q、K、V', '重点关注'], its: [
      I('大模型读', 300, 170, W.tokens(undefined, false), {s: 1.5, until: '三组数'}),
      I('三组数', 300, 170, W.tokens(), {s: 1.5, until: '每个Token都要'}),
      I('Q、K、V', 300, 560, W.label('Q 查询 · K 键 · V 值', P.plate, 44), {until: '每个Token都要'}),
      I('每个Token都要', 200, 170, W.tokens(undefined, true, true), {s: 1.3}),
      I('去和所有', 1050, 150, W.grid(4, 'scan', 300, 'Q × 所有 K'), {s: 1.1}),
      I('重点关注', 200, 560, W.label('该重点关注谁？', P.orange, 56)),
    ], kid: [A('大模型读', 1150, 'think'), A('三组数', 1150, 'point', true), A('去和所有', 1560, 'point', true)]},
    {lines: ['这一步得到的打分表，就是一张N乘N的大矩阵，N是句子长度。', '然后对每一行做一次softmax，把打分变成加起来等于1的权重。', '最后拿这份权重，把所有Token的V加权求和，得到输出。'], keys: ['N乘N', 'softmax', '加权求和'], its: [
      I('打分表', 220, 120, W.grid(6, 'fill', 360, '打分表 N×N')),
      I('N是', 220, 590, W.label('N = 句子长度', P.plate, 48), {until: '最后拿'}),
      I('softmax', 720, 120, W.grid(6, 'softmax', 360, '每行做 softmax')),
      I('等于1', 720, 590, W.label('每行加起来 = 1', P.teal, 48), {until: '最后拿'}),
      I('最后拿', 220, 590, W.label('权重 × V → 加权求和', P.gold, 48, P.onGold)),
      I('得到输出', 220, 700, W.check('得到输出')),
    ], kid: [A('打分表', 1250, 'think'), A('softmax', 1200, 'point', true), A('得到输出', 1000, 'point', true)]},
    {lines: ['这种每个Token都去看一遍|所有Token的计算，就是所谓的注意力。', '麻烦在于，句子长度翻一倍，这张表就要变成四倍大。'], keys: ['注意力', '四倍'], its: [
      I('这种每个', 200, 150, W.tokens(undefined, true, true), {s: 1.2}),
      I('所谓的注意力', 200, 470, W.title('注意力', '每个 Token 看一遍所有 Token'), {s: 1.1}),
      I('翻一倍', 1000, 120, W.grid(4, 'grow', 170), {s: 1.1}),
      I('四倍', 1000, 600, W.label('长度 ×2 → 表 ×4', P.heart, 52)),
    ], kid: [A('这种每个', 870, 'point', true), A('翻一倍', 1620, 'point', true)]},
  ]},
  {stage: 2, title: '存储层级', card: 'HBM和SRAM是什么？', shots: [
    {lines: ['显卡里不止一种存储。', '一种是我们常说的显存，容量大，A100上有40到80GB，带宽每秒1.5到2TB，它的名字叫HBM，高带宽显存。'], keys: ['显存', 'HBM'], its: [
      I('显卡里', 200, 170, W.gpu('A100', 560), {until: '常说的显存'}),
      I('常说的显存', 160, 140, W.store('40–80GB', '1.5–2TB/s', 640)),
      I('40到80', 900, 130, W.num(80, ' GB', 'A100 显存容量（最高）', 0, P.text)),
      I('带宽', 900, 360, W.num(2, ' TB/s', 'HBM 带宽（最高）', 0, P.teal)),
      I('HBM', 200, 600, W.title('HBM', '高带宽显存')),
    ], kid: [A('显卡里', 900, 'think'), A('常说的显存', 1480, 'point', true)]},
    {lines: ['另一种藏在计算核心旁边，叫片上SRAM。A100有108个计算单元，每个只有192KB，可带宽估计能到每秒19TB左右。', '一个像仓库，大，但远。一个像工作台，快，但小得可怜。'], keys: ['SRAM', '192KB', '19TB'], its: [
      I('计算核心旁边', 160, 150, W.bench('片上 SRAM', 440), {until: '一个像仓库'}),
      I('108个', 700, 140, W.sms(), {s: 1.25, until: '一个像仓库'}),
      I('192KB', 160, 560, W.label('每个只有 192KB', P.orange, 52), {until: '一个像仓库'}),
      I('19TB', 760, 540, W.num(19, ' TB/s', 'SRAM 带宽（估计）', 0, P.teal), {until: '一个像仓库'}),
      I('一个像仓库', 160, 160, W.sprite('warehouse', 600, 'HBM：大，但远'), {s: 1}),
      I('一个像工作台', 860, 180, W.bench('SRAM：快，但小', 440)),
    ], kid: [A('计算核心旁边', 1450, 'think'), A('108个', 1500, 'point', true), A('一个像仓库', 1450, 'point', true)]},
    {lines: ['GPU真正干活，数据都得先从仓库搬到工作台上。', '这种大而慢、小而快|分层摆放的存储结构，就是所谓的GPU显存层级。'], keys: ['显存层级'], its: [
      I('真正干活', 160, 110, W.cart([], 1500)),
      I('分层摆放', 220, 470, W.tiers()),
      I('显存层级', 1150, 500, W.label('GPU 显存层级', P.plate, 52)),
    ], kid: [A('真正干活', 300, 'point'), A('搬到工作台', 1350, 'think', false, P.orange), A('显存层级', 1500, 'point', true)]},
  ]},
  {stage: 3, title: '访存瓶颈', card: '标准注意力为什么慢？', shots: [
    {lines: ['按教科书的写法，注意力是一步一步算的。', '先算出N乘N的打分表，写回显存。', '再从显存读出来做softmax，结果再写回显存。', '最后再读一遍，去乘V。'], keys: ['写回显存'], its: [
      I('教科书', 200, 150, W.title('教科书写法', '一步一步算'), {s: 1.2, until: '先算出'}),
      I('先算出', 160, 110, W.cart(['写', '读', '写', '读'], 1500)),
      I('先算出', 160, 460, W.label('① 算出 N×N → 写回显存', P.orange, 44), {off: 6}),
      I('再从显存', 160, 560, W.label('② 读回 → softmax → 写回', P.teal, 44)),
      I('最后再读', 160, 660, W.label('③ 再读一遍 → 乘 V', P.gold, 44, P.onGold)),
    ], kid: [A('教科书', 1300, 'think'), A('先算出', 1050, 'point', true), A('最后再读', 1100, 'think')]},
    {dark: true, lines: ['那张最大的表，在仓库和工作台之间|来来回回搬了好几趟。', '可真正的计算，其实没几下。', '结果就是，计算核心大部分时间在等数据。', '这种瓶颈不在算力、|而在读写显存的问题，就是所谓的访存瓶颈。'], keys: ['来来回回', '等数据', '访存瓶颈'], its: [
      I('那张最大的表', 160, 110, W.cart(['写', '读', '写', '读', '读'], 1500), {until: '结果就是'}),
      I('没几下', 300, 480, W.row(W.num(4, ' 趟', '搬运', 0, P.heart, true), W.num(3, ' 步', '计算', 0, P.teal, true)), {until: '结果就是'}),
      I('结果就是', 200, 160, W.gpu('计算核心：等数据…', 560, true)),
      I('大部分时间', 860, 170, W.util()),
      I('访存瓶颈', 860, 480, W.title('访存瓶颈', '不在算 · 在搬', true), {s: 1.1}),
    ], kid: [A('那张最大的表', 1450, 'think'), A('没几下', 1450, 'point', true), A('访存瓶颈', 1520, 'point', true)]},
  ]},
  {stage: 5, title: '在线softmax', card: '在线softmax是什么？', shots: [
    {dark: true, strip: true, lines: ['不过这里有个坑。', 'softmax要除以一整行的总和，可分块之后，你一次只看到这一行的一小段，总和还不知道。', 'FlashAttention的办法是，边算边记账。', '每处理一块，就记下到目前为止的最大值，和到目前为止的累加和。'], keys: ['总和', '记账', '最大值', '累加和'], its: [
      I('有个坑', 200, 150, W.label('有个坑！', P.heart, 64), {until: 'FlashAttention的办法'}),
      I('一整行', 640, 160, W.label('softmax = eˣ ÷ 整行总和', m('panel'), 44), {until: 'FlashAttention的办法'}),
      I('一小段', 200, 330, W.rowChunks(), {s: 1.3, until: '每处理一块'}),
      I('边算边记账', 200, 140, W.title('边算边记账', undefined, true)),
      I('每处理一块', 200, 330, W.ledger(), {s: 1.1}),
      I('累加和', 860, 420, W.label('max m · sum ℓ', m('panel'), 52)),
    ], kid: [A('有个坑', 1300, 'think'), A('一小段', 1450, 'point', true), A('每处理一块', 1450, 'point', true)]},
    {dark: true, strip: true, lines: ['新的一块进来，如果出现了更大的值，就把之前的结果按比例缩放一下，再接着累加。', '等这一行所有块都过完，账也就对上了，结果和一次性算整行完全一样。', '这种不用看完整行、|边读边修正的softmax算法，就是所谓的在线softmax。'], keys: ['缩放', '完全一样', '在线softmax'], its: [
      I('新的一块', 200, 140, W.ledger([1.2, 2.8, 2.0, 3.5]), {s: 1.1, until: '所谓的在线'}),
      I('缩放', 860, 170, W.label('旧结果 × e^(m旧−m新)', P.orange, 44), {until: '等这一行'}),
      I('等这一行', 860, 160, W.same('分块在线', '整行一次'), {s: 1.1}),
      I('所谓的在线', 200, 170, W.title('在线 softmax', '边读边修正', true), {s: 1.1}),
    ], kid: [A('新的一块', 1450, 'think'), A('完全一样', 1580, 'point', true)]},
  ]},
  {stage: 6, title: '重算', card: '重算是什么？', shots: [
    {lines: ['训练的时候还有反向传播，按理说要用到|前向时那张N乘N的大表。', '存下来吧，显存又爆了。', 'FlashAttention的选择是，不存。', '它只存最终输出，和每一行的那两个记账数字。'], keys: ['反向传播', '不存'], its: [
      I('反向传播', 200, 130, W.back('反向传播')),
      I('N乘N', 200, 300, W.grid(6, 'fill', 260, '要存这张表？'), {until: '它只存'}),
      I('显存又爆了', 600, 320, W.gpu(undefined, 420, false), {until: '它只存'}),
      I('显存又爆了', 1100, 280, W.num(100, '%', '显存', 0), {idle: 'jitter', until: '它只存'}),
      I('不存', 1100, 520, W.check('不存', false), {until: '它只存'}),
      I('它只存', 200, 400, W.keep(), {s: 1.4}),
    ], kid: [A('反向传播', 1500, 'think'), A('显存又爆了', 1500, 'point', true), A('它只存', 1300, 'point', true)]},
    {lines: ['反向传播需要的时候，再按块在片上重新算一遍。', '算的次数是变多了，但比从显存里把大表读回来还要快。', '这种拿多算一遍换少读显存的做法，就是所谓的重算。'], keys: ['重新算', '重算'], its: [
      I('反向传播需要', 200, 130, W.grid(4, 'tiles', 280, '按块在片上重算')),
      I('片上', 640, 150, W.bench('片上 SRAM', 380)),
      I('次数是变多', 200, 530, W.race()),
      I('所谓的重算', 1100, 150, W.title('重算', '多算一遍 换 少读显存')),
    ], kid: [A('反向传播需要', 1150, 'point', true), A('所谓的重算', 1500, 'point', true)]},
  ]},
  {stage: 7, title: '总装', card: '好啦，到这里我们捋一下。', shots: [
    {lines: ['注意力会产生|一张随长度平方增长的大表。', 'GPU的瓶颈常常不在算，而在显存和片上之间的搬运。', '分块让大表不落显存。', '在线softmax让|分块后的结果依然精确。', '重算让训练时也不用存大表。'], keys: ['平方', '搬运'], its: [
      I('平方', 160, 120, W.grid(4, 'grow', 150)),
      I('瓶颈', 620, 110, W.cart([], 960)),
      I('分块让', 160, 500, W.check('分块：大表不落显存')),
      I('在线softmax让', 160, 610, W.check('在线 softmax：依然精确')),
      I('重算让', 160, 720, W.check('重算：训练也不存大表')),
    ], kid: [A('平方', 1600, 'think'), A('分块让', 1250, 'point', true), A('重算让', 1250, 'think')]},
    {lines: ['这一整套，加上把所有步骤融合进一个算子，就是FlashAttention。', '论文里，它的显存占用只随序列长度线性增长，不再是平方。', 'BERT-large训练|比当时的MLPerf 1.1纪录|快了15%，GPT-2快了3倍。'], keys: ['FlashAttention', '线性', '15%', '3倍'], its: [
      I('这一整套', 160, 110, W.machine(['注意力', '显存层级', '分块', '在线softmax', '重算']), {until: 'BERT'}),
      I('线性增长', 160, 480, W.curve(), {until: 'BERT'}),
      I('BERT', 200, 150, W.num(15, '%', 'BERT-large 训练提速', 0), {s: 1.2}),
      I('MLPerf', 200, 420, W.label('对比 MLPerf 1.1 纪录', m('slate'), 40)),
      I('GPT-2快了', 760, 150, W.num(3, '×', 'GPT-2 训练', 0), {s: 1.2}),
    ], kid: [A('这一整套', 1500, 'think'), A('线性增长', 1200, 'point', true), A('GPT-2快了', 1300, 'point', true)]},
    {lines: ['在长序列评测|Long-Range Arena上快了2.4倍。', '显存省下来，能塞进更长的上下文。论文里它第一次让Transformer|在长度16K的Path-X任务上|做到了比瞎猜更好，准确率61.4%。'], keys: ['2.4倍', '16K', '61.4%'], its: [
      I('Long-Range', 200, 150, W.num(2.4, '×', 'Long-Range Arena', 1), {s: 1.2, until: '16K'}),
      I('塞进', 760, 190, W.label('更长的上下文 →', P.teal, 52), {until: '16K'}),
      I('塞进', 200, 470, W.tokens(['长', '长', '长', '的', '上', '下', '文'], false), {s: 0.9, off: 10, until: '16K'}),
      I('16K', 200, 150, W.num(16, 'K', 'Path-X 序列长度', 0, P.text), {s: 1.2}),
      I('瞎猜', 760, 160, W.label('瞎猜 = 50%', m('slate'), 48)),
      I('61.4', 760, 300, W.num(61.4, '%', 'Path-X 准确率', 1, KG), {s: 1.2}),
    ], kid: [A('Long-Range', 1450, 'think'), A('塞进', 1500, 'point', true), A('61.4', 1500, 'point', true)]},
  ]},
  {stage: 8, title: '怎么用', card: '怎么用？', shots: [
    {dark: true, lines: ['如果你用的是|Hugging Face的transformers，加载模型时传一个参数，attn_implementation|等于flash_attention_2，就能切过去。', '前提是先装好flash-attn这个包，官方README给的命令是|pip install flash-attn，加上no-build-isolation。'], keys: ['flash_attention_2', 'flash-attn'], its: [
      I('Hugging Face', 200, 140, W.label('Hugging Face · transformers', P.gold, 48, P.onGold)),
      I('传一个参数', 200, 260, W.code('attn_implementation="flash_attention_2"', 1250)),
      I('切过去', 200, 420, W.check('一行切换', true, true), {until: '前提是'}),
      I('前提是', 200, 410, W.term([['$ pip install flash-attn \\'], ['    --no-build-isolation'], ['Successfully installed flash-attn', KG]], 1000)),
      I('README', 1250, 430, W.label('来源：官方 README', m('panel'), 40)),
    ], kid: [A('Hugging Face', 1550, 'think'), A('传一个参数', 1550, 'point', true), A('no-build', 1550, 'think')]},
    {lines: ['硬件上，FlashAttention-2|支持Ampere、Ada和Hopper|架构的卡，比如A100、RTX 3090、|RTX 4090、H100。数据类型要用fp16或bf16。'], keys: ['fp16', 'bf16'], its: [
      I('硬件上', 160, 130, W.archs(), {s: 1.15}),
      I('A100', 160, 430, W.gpu(undefined, 420)),
      I('4090', 640, 470, W.sprite('gpu_row', 520)),
      I('数据类型', 1220, 440, W.row(W.label('fp16', P.teal, 60), W.label('bf16', P.teal, 60))),
    ], kid: [A('硬件上', 1450, 'think'), A('A100', 1500, 'point', true), A('数据类型', 1620, 'point', true)]},
    {dark: true, lines: ['不想装的话，transformers里还有一个sdpa选项，用的是PyTorch|自带的缩放点积注意力。', '而专门给H100优化的|FlashAttention-3，目前在仓库里还是beta。'], keys: ['sdpa', 'beta'], its: [
      I('sdpa', 200, 150, W.code('attn_implementation="sdpa"', 780)),
      I('PyTorch', 200, 290, W.label('PyTorch 自带 · 缩放点积注意力', m('panel'), 44)),
      I('专门给H100', 200, 420, W.gpu('H100', 480)),
      I('beta', 780, 500, W.label('FlashAttention-3 · beta', P.orange, 52)),
    ], kid: [A('sdpa', 1400, 'point', true), A('beta', 1520, 'point', true)]},
  ]},
  {stage: 9, title: '完整流程', card: '最后，我们用一次完整的计算|把这些串起来。', shots: [
    {lines: ['一句话进来，被切成Token，算出Q、K、V，放在显存里。', 'FlashAttention拿出第一块Q，送上片上SRAM。', '再一块一块地拿K和V上来。'], keys: ['SRAM'], its: [
      I('一句话进来', 200, 150, W.tokens(), {s: 1.2, until: '第一块Q'}),
      I('放在显存里', 980, 140, W.store('Q K V', 'HBM', 440), {until: '第一块Q'}),
      I('第一块Q', 160, 150, W.pipeline()),
      I('一块一块', 200, 560, W.label('K、V 一块一块上', KG, 52, P.onGold)),
    ], kid: [A('一句话进来', 1550, 'think'), A('一块一块', 1000, 'point', true, KG)]},
    {lines: ['每来一块，在片上算打分，更新这一行的最大值和累加和，把之前的结果缩放一下，加上这一块的贡献。', '所有K、V块过完，这块Q的输出就算好了，写回显存。'], keys: ['最大值', '累加和', '写回显存'], its: [
      I('每来一块', 160, 130, W.pipeline()),
      I('最大值', 200, 520, W.label('m ← max(m, 新块)', m('panel'), 48)),
      I('缩放', 200, 620, W.label('旧结果 × 缩放 + 这块贡献', P.orange, 48)),
      I('写回显存', 200, 730, W.check('这块 Q 的输出 → 写回显存')),
    ], kid: [A('每来一块', 1350, 'think'), A('写回显存', 1350, 'point', true, m('dark-cell-lit'))]},
    {dark: true, lines: ['接着换下一块Q，重复一遍。', '整个过程，那张N乘N的大表|一次都没出现在显存里。', '训练反向的时候，再按块把它在片上重新算出来。'], keys: ['一次都没'], its: [
      I('下一块Q', 200, 140, W.label('下一块 Q → 重复', P.plate, 56)),
      I('一次都没', 200, 270, W.grid(6, 'dashed', 300, 'N×N：0 次落显存')),
      I('训练反向', 640, 420, W.back('反向：片上重算')),
    ], kid: [A('下一块Q', 1450, 'think'), A('训练反向', 1580, 'point', true)]},
  ]},
];
const END: Shot[] = [
  {lines: ['现在，搬得慢比算得慢更要命，这句话是不是好理解多了？', '留个思考题：分块越大，搬的次数越少，那为什么块不能无限大？', '答案就在那192KB里。'], keys: ['搬得慢', '192KB'], its: [
    I('搬得慢比', 200, 130, W.scale(), {s: 1.2, until: '思考题'}),
    I('思考题', 200, 170, W.quiz(), {s: 1.3}),
    I('192KB', 1180, 200, W.bench('192KB', 360)),
  ], kid: [A('搬得慢比', 1150, 'point', true), A('思考题', 1500, 'think'), A('192KB', 1560, 'point', true)]},
  {lines: ['我是显存不够，一个显卡永远在爆显存的穷学生，买不起更大的卡，就只能把省显存的招一个个拆明白，我们下期见。'], keys: ['显存不够'], its: [
    I('我是显存不够', 200, 140, W.title('显存不够', '常年爆显存的穷学生'), {s: 1.2}),
    I('爆显存', 940, 140, W.num(100, '%', '我的显存', 0), {idle: 'jitter'}),
    I('买不起', 200, 450, W.gpu('买不起更大的卡', 420)),
    I('拆明白', 720, 520, W.label('省显存的招，一个个拆明白', P.teal, 44)),
    I('下期见', 900, 660, W.label('下期见！', P.orange, 64)),
  ], kid: [A('我是显存不够', 1500, 'point', true), A('下期见', 1450, 'point')]},
];

let sd = 1;
const shot = (id: string, s: Shot, count: number): Seg => { const c = makeCues(s.lines); const n = sd++; return {id, dur: c[c.length - 1].from + c[c.length - 1].dur, node: <ShotView s={s} seed={n} id={id} stage={count} />, count}; };
// 章节卡：旁白长度只做下限参考，最终时长由 timeline/grid.ts 抬到整小节（≥2 小节）
const card = (stage: number, title: string, line: string): Seg => { const c = makeCues([line]); return {id: 'card' + stage, dur: c[c.length - 1].from + c[c.length - 1].dur + 10, node: <BigCard stage={stage} title={title} cues={c} keys={[title]} />, count: stage, cut: false}; };

export const RAW_SEGS: Seg[] = [
  {id: 'K1', dur: D1, node: <S1 />, count: 0},
  {id: 'K2', dur: D2, node: <S2 />, count: 0},
  shot('hook3', HOOK3, 0),
];
CH.forEach((ch) => {
  if (ch.stage === 5) { RAW_SEGS.push(card(4, '分块', '分块是什么？')); RAW_SEGS.push({id: 'K4', dur: D4, node: <S4 />, count: 4}); }
  RAW_SEGS.push(card(ch.stage, ch.title, ch.card));
  ch.shots.forEach((s, i) => RAW_SEGS.push(shot(`c${ch.stage}s${i}`, s, ch.stage)));
});
END.forEach((s, i) => RAW_SEGS.push(shot('end' + i, s, 9)));

/**
 * 120 BPM 硬卡点：所有段落时长套到网格上。
 * 章节卡 → 整小节（≥120 帧）；普通镜头 → 整拍，且每串镜头总长补到整小节。
 * 画面内容、字幕、配音一个字都没动，只是每段多留了几帧静止。
 */
export const FINAL_SEGS: Seg[] = gridSegs(RAW_SEGS, (s) => s.id.startsWith('card'));
// 爆点排程 v3.1：5 次，间隔 ≥80s。章节卡只留 card1 铺墙；card4/7/9 降级为只放大字。其余 4 次插在镜头内的结论句上（镜内本地帧）
{
  CARD_BURST.add('card1');
  BURSTS.c3s0 = [{at: 86, kind: 'matrix', cap: 'N×N 打分表 → 写回显存'}];   // 129.4s「先算出N乘N的打分表，写回显存」
  BURSTS.c5s1 = [{at: 90, kind: 'matrix', cap: '旧结果 × 缩放 + 新块'}];     // 211.0s「就把之前的结果按比例缩放一下」
  BURSTS.c7s2 = [{at: 135, kind: 'gpus', cap: '显存省下 → 更长上下文'}];     // 292.5s「显存省下来，能塞进更长的上下文」
  BURSTS.c9s2 = [{at: 123, kind: 'matrix', cap: 'N×N 大表：0 次落显存'}];    // 374.1s「那张N乘N的大表 一次都没出现在显存里」
}
/** 未上网格的原始时间轴：只用于「换皮不换画面」的回归对比，不进成片。 */
export const UNGRIDDED_SEGS: Seg[] = RAW_SEGS;
export const UNGRIDDED_TOTAL = RAW_SEGS.reduce((a, s) => a + s.dur, 0);
export const FinalUngridded: React.FC = () => <Timeline segs={RAW_SEGS} />;
export const FINAL_TOTAL = FINAL_SEGS.reduce((a, s) => a + s.dur, 0);
export const Final: React.FC = () => <Timeline segs={FINAL_SEGS} />;
