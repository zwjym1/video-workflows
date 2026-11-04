// EP1 整片（无配音，只带音效）：K1/K2/K4 用定制镜头，其余章节用通用「槽位」引擎
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {useDesignFrame, Sfx} from './timeline/fps';
import {Frame, FontFace, P, PaperBg, DarkGridBg, m, useEnter, BgSweep} from './kit';
import {SpriteBg} from './Sprite';
import {Dust} from './sprites';
import {prog} from './lib/anim';
import {gridSegs} from './timeline/grid';
import {useSnapToBeat} from './components/BeatSync';
import {makeCues, Cue, CueSub, Kid, idleStyle, Idle, ProgCtx, useProg, Card, Timeline, Seg, S1, S2, S4, D1, D2, D4, NAME} from './Motion';
import * as W from './W';

type F = (t: number) => React.ReactNode;
type El = [string, number, F, Idle?];
type Shot = {lines: string[]; els: El[]; dark?: boolean; keys?: string[]};
type Ch = {stage?: number; title?: string; card?: string[]; shots: Shot[]};

/** 槽位：0 左上 1 右上 2 左下 3 右下 4 上通栏 5 下通栏 6 全幅；右下角 1700+ 留给小人 */
const SLOTS = [[130, 140, 800, 380], [990, 140, 700, 380], [130, 545, 800, 335], [990, 545, 700, 335], [130, 140, 1560, 380], [130, 545, 1560, 335], [130, 140, 1560, 740]];
const CELLS = [[0], [1], [2], [3], [0, 1], [2, 3], [0, 1, 2, 3]];

const cuesOf = (lines: string[]) => {
  const out: (Cue & {li: number})[] = []; let t = 0;
  lines.forEach((l, li) => { for (const c of makeCues([l])) { out.push({...c, from: c.from + t, li}); } t = out[out.length - 1].from + out[out.length - 1].dur; });
  return out;
};
const startOf = (cues: (Cue & {li: number})[], lines: string[], k: string) => {
  const c = cues.find((x) => x.text.includes(k)); if (c) return c.from;
  const li = lines.findIndex((l) => l.replace(/\|/g, '').includes(k));
  const c2 = cues.find((x) => x.li === li); return c2 ? c2.from : 0;
};

const ElView: React.FC<{at: number; end: number; slot: number; f: F; idle?: Idle; seed: number; snap?: boolean}> = ({at, end, slot, f: render, idle, seed, snap}) => {
  const f = useDesignFrame();
  const [x, y, w, h] = SLOTS[slot];
  // 卡点：只有「语义关键元素」（每镜第一个 + 通栏/全幅槽位）入场吸到拍点，
  // 容差 3 帧 = 100ms。超出容差不吸，宁可错过拍子也不能把入场拽离字幕。
  const at2 = useSnapToBeat(at, 3);
  const atS = snap ? at2 : at;
  const enter = useEnter();
  const p = prog(f, atS, enter.frames, enter.ease);
  const out = f >= end ? (f - end) / 8 : 0;
  // 自动放大到槽位的 ~88%（最多 1.7 倍），避免小部件在大画面里显得空
  const ref = React.useRef<HTMLDivElement>(null); const [k, setK] = React.useState(1);
  React.useLayoutEffect(() => { const el = ref.current; if (!el) return; const ow = el.offsetWidth, oh = el.offsetHeight; if (!ow || !oh) return;
    const nk = Math.min(1.7, (0.88 * w) / ow, (0.88 * h) / oh); if (Math.abs(nk - k) > 0.01) setK(nk); });
  return (
    <>
      <Sfx at={atS} dur={6} file="sfx/pop.wav" volume={0.22} />
      {f >= atS && out < 1 && <div style={{position: 'absolute', left: x, top: y, width: w, height: h, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: Math.min(1, p * 2) * (1 - out)}}>
        <div style={{transform: `translateY(${(1 - p) * 40}px) scale(${(0.6 + 0.4 * p) * k})`, transformOrigin: 'center center'}}>
          <div ref={ref} style={idleStyle(f, seed, idle, 3)}>{render(f - atS)}</div>
        </div>
      </div>}
    </>
  );
};

const ShotView: React.FC<{s: Shot; seed: number}> = ({s, seed}) => {
  const f = useDesignFrame(); const ctx = React.useContext(ProgCtx);
  const cues = cuesOf(s.lines);
  const st = s.els.map((e) => startOf(cues, s.lines, e[0]));
  const end = s.els.map((e, i) => Math.min(1e9, ...s.els.map((e2, j) => (j !== i && (st[j] > st[i] || (st[j] === st[i] && j > i)) && CELLS[e2[1]].some((c) => CELLS[e[1]].includes(c)) ? st[j] : 1e9))));
  const poses = cues.map((c, i) => [c.from, i % 2 ? 'point' : 'think'] as [number, 'think' | 'point']);
  return (
    <AbsoluteFill><FontFace />
      {s.dark ? <SpriteBg name="bg_dark_grid" fallback={<DarkGridBg />} /> : <SpriteBg name="bg_paper" fallback={<PaperBg />} />}
      <Dust n={8} dark={s.dark} seed={seed} />
      {/* 2026-11-04 背景扫光带去掉：整屏横竖两条亮带一直在跳，属于无意义装饰 */}
      {s.els.map((e, i) => <ElView key={i} at={st[i]} end={end[i]} slot={e[1]} f={e[2]} idle={e[3]} seed={seed * 7 + i * 3.3} snap={i === 0 && (e[1] === 4 || e[1] === 5 || e[1] === 6)} />)}
      <div style={{position: 'absolute', left: 1715, top: 600}}><Kid h={260} poses={poses} flip={seed % 2 === 1} seed={seed} /></div>
      <Frame progress={useProg(f)} count={ctx.count} name={NAME} dark={s.dark} />
      <CueSub cues={cues} keys={s.keys ?? []} />
    </AbsoluteFill>
  );
};

const KG = m('green');
const HOOK_REST: Shot = {lines: ['而且不是近似，算出来的结果和原来一模一样。', '那么问题就来了，数据到底搬到哪去了？为什么搬得慢？FlashAttention|又是怎么做到少搬的？'], keys: ['一模一样', '少搬'], els: [
  ['不是近似', 0, W.label('不是近似', P.teal, 52)], ['算出来', 1, W.check('一模一样')], ['问题就来了', 5, W.qblocks(['搬到哪？', '为什么慢？', '怎么少搬？'])]]};

export const CHAPTERS: Ch[] = [
  {stage: 1, title: '注意力', card: ['注意力是什么？'], shots: [
    {lines: ['我们知道，大模型读一句话，会把每个Token算成三组数，叫Q、K、V。', '每个Token都要拿自己的Q，去和所有Token的K比一遍，算出该重点关注谁。'], keys: ['Q、K、V', '重点关注'], els: [
      ['大模型读', 4, W.tokens(undefined, false)], ['三组数', 4, W.tokens()], ['去和所有', 2, W.grid(4, 'scan', 250, 'Q 扫过所有 K')], ['重点关注', 3, W.label('该关注谁？', P.orange, 52)]]},
    {lines: ['这一步得到的打分表，就是一张N乘N的大矩阵，N是句子长度。', '然后对每一行做一次softmax，把打分变成加起来等于1的权重。'], keys: ['N乘N', 'softmax'], els: [
      ['打分表', 0, W.grid(6, 'fill', 280, '打分表 N×N')], ['N是', 1, W.label('N = 句子长度', P.plate, 48)], ['softmax', 2, W.grid(6, 'softmax', 250, '每行 softmax')], ['等于1', 3, W.label('每行加起来 = 1', P.teal, 44)]]},
    {lines: ['最后拿这份权重，把所有Token的V加权求和，得到输出。', '这种每个Token都去看一遍|所有Token的计算，就是所谓的注意力。', '麻烦在于，句子长度翻一倍，这张表就要变成四倍大。'], keys: ['注意力', '四倍'], els: [
      ['加权求和', 4, W.label('权重 × V → 求和 → 输出', P.gold, 52, P.onGold)], ['就是所谓', 2, W.title('注意力', '每个 Token 看一遍所有 Token')], ['翻一倍', 1, W.grid(4, 'grow', 140)], ['四倍', 3, W.label('长度 ×2 → 表 ×4', P.heart, 48)]]},
  ]},
  {stage: 2, title: '存储层级', card: ['HBM和SRAM是什么？'], shots: [
    {lines: ['显卡里不止一种存储。', '一种是我们常说的显存，容量大，A100上有40到80GB，带宽每秒1.5到2TB，它的名字叫HBM，高带宽显存。'], keys: ['显存', 'HBM'], els: [
      ['不止一种', 1, W.gpu('A100', 380)], ['常说的显存', 0, W.store('40–80GB', '1.5–2TB/s', 440)], ['带宽', 2, W.num(2, ' TB/s', 'HBM 带宽（最高）', 0, P.text)], ['HBM', 3, W.label('HBM 高带宽显存', P.plate, 44)]]},
    {lines: ['另一种藏在计算核心旁边，叫片上SRAM。A100有108个计算单元，每个只有192KB，可带宽估计能到每秒19TB左右。', '一个像仓库，大，但远。一个像工作台，快，但小得可怜。'], keys: ['SRAM', '192KB', '19TB'], els: [
      ['片上SRAM', 0, W.bench('片上 SRAM', 330)], ['108个', 1, W.sms()], ['19TB', 2, W.num(19, ' TB/s', 'SRAM 带宽（估计）', 0, P.teal)], ['仓库', 3, W.row(W.label('仓库：大但远', m('slate'), 34), W.label('工作台：快但小', P.teal, 34))]]},
    {lines: ['GPU真正干活，数据都得先从仓库搬到工作台上。', '这种大而慢、小而快|分层摆放的存储结构，就是所谓的GPU显存层级。'], keys: ['显存层级'], els: [
      ['真正干活', 4, W.cart([])], ['分层', 2, W.title('GPU 显存层级', '大而慢 ⇄ 小而快')], ['存储结构', 3, W.label('仓库 → 工作台', P.orange, 44)]]},
  ]},
  {stage: 3, title: '访存瓶颈', card: ['标准注意力为什么慢？'], shots: [
    {lines: ['按教科书的写法，注意力是一步一步算的。', '先算出N乘N的打分表，写回显存。', '再从显存读出来做softmax，结果再写回显存。'], keys: ['写回显存'], els: [
      ['教科书', 0, W.title('标准注意力', '一步一步算')], ['先算出', 1, W.grid(5, 'fill', 230, '① 算完 → 写回')], ['再从显存', 5, W.cart(['写', '读', '写', '读'])]]},
    {lines: ['最后再读一遍，去乘V。', '那张最大的表，在仓库和工作台之间|来来回回搬了好几趟。', '可真正的计算，其实没几下。'], keys: ['来来回回'], els: [
      ['最后再读', 0, W.label('③ 再读一遍 × V', P.orange, 48)], ['来来回回', 5, W.cart(['写', '读', '写', '读', '读'])], ['没几下', 1, W.num(3, ' 步', '真正的计算', 0, P.teal)]]},
    {dark: true, lines: ['结果就是，计算核心大部分时间在等数据。', '这种瓶颈不在算力|而在读写显存的问题，就是所谓的访存瓶颈。'], keys: ['等数据', '访存瓶颈'], els: [
      ['等数据', 0, W.gpu('计算核心：等数据…', 380, true)], ['不在算力', 3, W.label('算力 ≠ 瓶颈', m('panel'), 44)], ['访存瓶颈', 1, W.title('访存瓶颈', '不在算 · 在搬', true)]]},
  ]},
  {stage: 5, title: '在线softmax', card: ['在线softmax是什么？'], shots: [
    {dark: true, lines: ['不过这里有个坑。', 'softmax要除以一整行的总和，可分块之后，你一次只看到这一行的一小段，总和还不知道。'], keys: ['总和'], els: [
      ['有个坑', 0, W.label('有个坑！', P.heart, 56)], ['一整行', 1, W.label('softmax = eˣ ÷ 整行总和', m('panel'), 36)], ['一小段', 5, W.rowChunks()]]},
    {dark: true, lines: ['FlashAttention的办法是，边算边记账。', '每处理一块，就记下到目前为止的最大值，和到目前为止的累加和。'], keys: ['记账', '最大值', '累加和'], els: [
      ['边算边记账', 0, W.title('边算边记账', undefined, true)], ['最大值', 1, W.ledger()], ['累加和', 2, W.label('max m · sum ℓ', m('panel'), 48)]]},
    {dark: true, lines: ['新的一块进来，如果出现了更大的值，就把之前的结果按比例缩放一下，再接着累加。', '等这一行所有块都过完，账也就对上了，结果和一次性算整行完全一样。', '这种不用看完整行|边读边修正的softmax算法，就是所谓的在线softmax。'], keys: ['缩放', '完全一样', '在线softmax'], els: [
      ['新的一块', 1, W.ledger([1.2, 2.8, 2.0, 3.5])], ['缩放', 0, W.label('旧结果 × e^(m旧−m新)', P.orange, 40)], ['所有块', 2, W.same('分块在线', '整行一次')], ['在线softmax', 3, W.title('在线 softmax', undefined, true)]]},
  ]},
  {stage: 6, title: '重算', card: ['重算是什么？'], shots: [
    {lines: ['训练的时候还有反向传播，按理说要用到|前向时那张N乘N的大表。', '存下来吧，显存又爆了。', 'FlashAttention的选择是，不存。'], keys: ['反向传播', '不存'], els: [
      ['反向传播', 4, W.back('反向传播')], ['N乘N', 2, W.grid(6, 'fill', 220, '要存这张表？')], ['显存又爆了', 3, W.num(100, '%', '显存', 0), 'jitter'], ['不存', 1, W.check('不存', false)]]},
    {lines: ['它只存最终输出，和每一行的那两个记账数字。', '反向传播需要的时候，再按块在片上重新算一遍。', '算的次数是变多了，但比从显存里把大表读回来还要快。', '这种拿多算一遍换少读显存的做法，就是所谓的重算。'], keys: ['重新算', '重算'], els: [
      ['只存', 4, W.keep()], ['重新算', 2, W.grid(4, 'tiles', 200, '按块在片上重算')], ['还要快', 5, W.race()], ['所谓的重算', 4, W.title('重算', '多算一遍 换 少读显存')]]},
  ]},
  {stage: 7, title: '总装', card: ['好啦，到这里我们捋一下。'], shots: [
    {lines: ['注意力会产生|一张随长度平方增长的大表。', 'GPU的瓶颈常常不在算，而在显存和片上之间的搬运。', '分块让大表不落显存。', '在线softmax让|分块后的结果依然精确。', '重算让训练时也不用存大表。'], keys: ['平方', '搬运'], els: [
      ['平方', 0, W.grid(4, 'grow', 130)], ['瓶颈', 1, W.label('搬运 > 计算', P.orange, 52)], ['分块让', 2, W.check('分块：不落显存')], ['在线softmax让', 3, W.check('在线softmax：精确')], ['重算让', 2, W.check('重算：不存大表')]]},
    {lines: ['这一整套，加上把所有步骤融合进一个算子，就是FlashAttention。', '论文里，它的显存占用只随序列长度线性增长，不再是平方。'], keys: ['FlashAttention', '线性'], els: [
      ['这一整套', 4, W.machine(['注意力', '显存层级', '分块', '在线softmax', '重算'])], ['线性增长', 5, W.curve()]]},
    {lines: ['BERT-large训练|比当时的MLPerf 1.1纪录|快了15%，GPT-2快了3倍。', '在长序列评测|Long-Range Arena上快了2.4倍。'], keys: ['15%', '3倍', '2.4倍'], els: [
      ['BERT', 0, W.num(15, '%', 'BERT-large 训练提速', 0)], ['MLPerf', 2, W.label('对比 MLPerf 1.1 纪录', m('slate'), 36)], ['GPT-2快了', 1, W.num(3, '×', 'GPT-2 训练', 0)], ['Long-Range', 3, W.num(2.4, '×', 'Long-Range Arena', 1)]]},
    {lines: ['显存省下来，能塞进更长的上下文。论文里它第一次让Transformer|在长度16K的Path-X任务上|做到了比瞎猜更好，准确率61.4%。'], keys: ['16K', '61.4%'], els: [
      ['塞进', 0, W.label('更长的上下文', P.teal, 52)], ['16K', 1, W.num(16, 'K', 'Path-X 序列长度', 0, P.text)], ['瞎猜', 3, W.label('> 瞎猜 50%', P.orange, 44)], ['61.4', 2, W.num(61.4, '%', 'Path-X 准确率', 1, KG)]]},
  ]},
  {stage: 8, title: '怎么用', card: ['怎么用？'], shots: [
    {dark: true, lines: ['如果你用的是|Hugging Face的transformers，加载模型时传一个参数，attn_implementation|等于flash_attention_2，就能切过去。'], keys: ['flash_attention_2'], els: [
      ['Hugging Face', 0, W.label('Hugging Face transformers', P.gold, 40, P.onGold)], ['传一个参数', 5, W.code('attn_implementation="flash_attention_2"')], ['切过去', 1, W.check('一行切换', true, true)]]},
    {dark: true, lines: ['前提是先装好flash-attn这个包，官方README给的命令是|pip install flash-attn，加上no-build-isolation。'], keys: ['flash-attn'], els: [
      ['flash-attn这个包', 4, W.term([['$ pip install flash-attn \\'], ['    --no-build-isolation'], ['Successfully installed flash-attn', KG]], 900)], ['README', 2, W.label('来源：官方 README', m('panel'), 40)], ['no-build', 3, W.label('别漏这个参数', P.orange, 44)]]},
    {lines: ['硬件上，FlashAttention-2|支持Ampere、Ada和Hopper|架构的卡，比如A100、RTX 3090|RTX 4090、H100。数据类型要用fp16或bf16。'], keys: ['fp16', 'bf16'], els: [
      ['硬件上', 4, W.archs()], ['A100', 3, W.gpu(undefined, 300)], ['fp16', 2, W.row(W.label('fp16', P.teal, 52), W.label('bf16', P.teal, 52))]]},
    {dark: true, lines: ['不想装的话，transformers里还有一个sdpa选项，用的是PyTorch|自带的缩放点积注意力。', '而专门给H100优化的|FlashAttention-3，目前在仓库里还是beta。'], keys: ['sdpa', 'beta'], els: [
      ['sdpa', 0, W.code('attn_implementation="sdpa"', 720)], ['PyTorch', 1, W.label('PyTorch 自带 · 缩放点积注意力', m('panel'), 32)], ['FlashAttention-3', 5, W.row(W.gpu(undefined, 300), W.label('FA3 · H100 · beta', P.orange, 48))]]},
  ]},
  {stage: 9, title: '完整流程', card: ['最后，我们用一次完整的计算|把这些串起来。'], shots: [
    {lines: ['一句话进来，被切成Token，算出Q、K、V，放在显存里。', 'FlashAttention拿出第一块Q，送上片上SRAM。', '再一块一块地拿K和V上来。'], keys: ['SRAM'], els: [
      ['一句话', 0, W.tokens()], ['放在显存里', 1, W.label('全部放在 HBM 显存', P.plate, 40)], ['第一块Q', 5, W.pipeline()], ['一块一块', 1, W.label('K、V 一块一块上', KG, 44, P.onGold)]]},
    {lines: ['每来一块，在片上算打分，更新这一行的最大值和累加和，把之前的结果缩放一下，加上这一块的贡献。', '所有K、V块过完，这块Q的输出就算好了，写回显存。'], keys: ['最大值', '累加和', '写回显存'], els: [
      ['每来一块', 5, W.pipeline()], ['最大值', 1, W.ledger([2.1, 1.4, 3.6, 2.9], true)], ['缩放', 0, W.label('缩放旧结果 + 加上这块', P.orange, 40)], ['写回显存', 0, W.check('写回显存')]]},
    {lines: ['接着换下一块Q，重复一遍。', '整个过程，那张N乘N的大表|一次都没出现在显存里。', '训练反向的时候，再按块把它在片上重新算出来。'], keys: ['一次都没'], els: [
      ['下一块Q', 0, W.label('下一块 Q → 重复', P.plate, 48)], ['一次都没', 1, W.grid(5, 'dashed', 220, 'N×N：0 次落显存')], ['训练反向', 5, W.back('反向：片上重算')]]},
  ]},
  {shots: [
    {lines: ['现在，搬得慢比算得慢更要命，这句话是不是好理解多了？', '留个思考题：分块越大，搬的次数越少，那为什么块不能无限大？', '答案就在那192KB里。'], keys: ['搬得慢', '192KB'], els: [
      ['搬得慢比', 4, W.scale()], ['思考题', 5, W.quiz()]]},
    {lines: ['我是显存不够，一个显卡永远在爆显存的穷学生，买不起更大的卡，就只能把省显存的招一个个拆明白，我们下期见。'], keys: ['显存不够'], els: [
      ['我是', 0, W.title('显存不够', '常年爆显存的穷学生')], ['买不起', 1, W.gpu('买不起更大的卡', 340)], ['拆明白', 2, W.label('省显存的招，一个个拆明白', P.teal, 38)], ['下期见', 3, W.label('下期见！', P.orange, 56)]]},
  ]},
];

const shotDur = (s: Shot) => { const c = cuesOf(s.lines); return c[c.length - 1].from + c[c.length - 1].dur; };
let seedN = 1;
const shotSeg = (id: string, s: Shot, count: number): Seg => { const sd = seedN++; return {id, dur: shotDur(s), node: <ShotView s={s} seed={sd} />, count}; };
const cardSeg = (stage: number, title: string, lines: string[]): Seg => { const c = makeCues(lines); return {id: 'card' + stage, dur: c[c.length - 1].from + c[c.length - 1].dur, node: <Card stage={stage} title={title} cues={c} keys={[title]} />, count: stage, cut: false}; };

const RAW_SEGS: Seg[] = [
  {id: 'K1', dur: D1, node: <S1 />, count: 0},
  {id: 'K2', dur: D2, node: <S2 />, count: 0},
  shotSeg('hook3', HOOK_REST, 0),
];
CHAPTERS.forEach((ch) => {
  if (ch.stage === 5) { // ④ 分块：定制 K3/K4 插在 ③ 之后
    RAW_SEGS.push(cardSeg(4, '分块', ['分块是什么？']));
    RAW_SEGS.push({id: 'K4', dur: D4, node: <S4 />, count: 4});
  }
  if (ch.stage) RAW_SEGS.push(cardSeg(ch.stage, ch.title!, ch.card!));
  ch.shots.forEach((s, i) => RAW_SEGS.push(shotSeg(`c${ch.stage ?? 'end'}s${i}`, s, ch.stage ?? 9)));
});
/** 120 BPM 硬卡点（同 Chapters.tsx）：卡对整小节、镜头对整拍 */
export const EP_SEGS: Seg[] = gridSegs(RAW_SEGS, (s) => s.id.startsWith('card'));
export const EP_TOTAL = EP_SEGS.reduce((a, s) => a + s.dur, 0);
export const Episode: React.FC = () => <Timeline segs={EP_SEGS} />;
