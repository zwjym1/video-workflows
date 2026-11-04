// 通用像素信息图小部件（全部代码道具 + 已有 codex 素材），t = 元素出现后的帧数
import React from 'react';
import {P, FONT, Label, Token} from './kit';
import {m as mat} from './theme/mat';
import {Sprite} from './Sprite';
import {Cell, ClockSprite, BoltSprite} from './sprites';
import {GpuCard} from './Motion';
import {prog, easeOut, easeOutBack} from './lib/anim';

const KG = mat('green');
const QKV = [P.orange, KG, P.gold];
const sh = 'var(--t-shadow-6-a20)';
const txt = (size: number, color: string = P.text): React.CSSProperties => ({fontFamily: FONT, fontSize: size, color, lineHeight: 1.15, whiteSpace: 'nowrap'});
type F = (t: number) => React.ReactNode;

export const title = (text: string, sub?: string, dark?: boolean): F => () => (
  <div style={{background: dark ? P.onGold : P.plate, padding: '14px 40px', boxShadow: sh, textAlign: 'center'}}>
    <div style={txt(68, dark ? P.amber : P.gold)}>{text}</div>
    {sub && <div style={txt(32, dark ? P.amber : P.onPlate)}>{sub}</div>}
  </div>
);
export const label = (text: string, bg: string = P.plate, size = 44, color: string = P.onPlate): F => () => <Label text={text} bg={bg} size={size} color={color} />;

/** Token 方块 + 挂 QKV 三色小格；Q 依次点亮（扫描） */
export const tokens = (words = ['猫', '爱', '吃', '鱼'], qkv = true, scan = false): F => (t) => (
  <div style={{display: 'flex', gap: 28}}>
    {words.map((w, i) => { const hot = scan && Math.floor(t / 18) % words.length === i; return (
      <div key={i} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, transform: hot ? 'translateY(-8px)' : undefined}}>
        <Token ch={w} size={124} hot={hot} />
        {qkv && <div style={{display: 'flex', gap: 4}}>{QKV.map((c, k) => <div key={k} style={{opacity: t > 6 + i * 4 + k * 3 ? 1 : 0}}><Cell c={c} s={38} /></div>)}</div>}
        {qkv && <div style={txt(24)}>Q K V</div>}
      </div>); })}
  </div>
);

/** N×N 表：scan 行扫描 / softmax 行着色 / grow 翻倍膨胀 / dashed 虚线不落显存 */
export const grid = (n: number, mode: 'scan' | 'softmax' | 'grow' | 'dashed' | 'tiles' | 'fill', size = 300, cap?: string): F => (t) => {
  const N = mode === 'grow' && t > 50 ? n * 2 : n;
  const S = mode === 'grow' ? Math.min(size * (t > 50 ? 1 + prog(t, 50, 14, easeOutBack) : 1), size * 2) : size;
  const s = S / N; const row = Math.floor(t / 10) % N; const shown = mode === 'fill' ? Math.min(N * N, Math.floor(t * 1.2)) : N * N;
  const r = (i: number) => { const v = Math.sin(i * 12.9) * 4375.5; return v - Math.floor(v); };
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10}}>
      <svg width={S} height={S} shapeRendering="crispEdges" style={{display: 'block', boxShadow: mode === 'dashed' ? undefined : sh}}>
        {Array.from({length: N * N}).map((_, i) => { const x = i % N, y = Math.floor(i / N); if (i >= shown) return null;
          let c = mat('cell-pale');
          if (mode === 'scan' && y === row) c = P.orange; else if (mode === 'scan' && y < row) c = mat('cell-warm');
          if (mode === 'softmax') { const w = r(i); c = y === row ? `rgba(46,143,130,${0.25 + 0.75 * w})` : `rgba(46,143,130,${0.1 + 0.3 * w})`; }
          if (mode === 'tiles') { const tile = Math.floor(t / 20) % 4; c = Math.floor(y / (N / 2)) * 2 + Math.floor(x / (N / 2)) === tile ? P.orange : mat('cream-dark'); }
          if (mode === 'dashed') return <rect key={i} x={x * s + 3} y={y * s + 3} width={s - 6} height={s - 6} fill="none" stroke="var(--m-grey-light)" strokeWidth={3} strokeDasharray="6 5" />;
          return <rect key={i} x={x * s + 1} y={y * s + 1} width={s - 2} height={s - 2} fill={c} stroke={P.stroke} strokeWidth={2} />; })}
      </svg>
      {(cap || mode === 'grow') && <div style={txt(34, mode === 'dashed' ? mat('ghost-text') : P.text)}>{mode === 'grow' ? (t > 50 ? `N×2 → 表 ×4` : `N = ${n}`) : cap}</div>}
    </div>
  );
};

/** 数字卡：20 帧滚动到目标值 */
export const num = (v: number, suffix: string, cap: string, dec = 0, color: string = P.heart, dark?: boolean): F => (t) => (
  <div style={{background: dark ? mat('dark-bg') : P.tokenBg, border: `5px solid ${P.stroke}`, padding: '10px 26px', boxShadow: sh, textAlign: 'center'}}>
    <div style={txt(30, dark ? mat('dark-text') : mat('muted'))}>{cap}</div>
    <div style={txt(88, color)}>{(v * prog(t, 0, 20, easeOut)).toFixed(dec)}{suffix}</div>
  </div>
);

/** 终端：逐字打出，光标闪 */
export const term = (lines: [string, string?][], w = 720): F => (t) => {
  let left = Math.floor(t * 1.6);
  return (
    <div style={{width: w, background: mat('term-bg'), border: `5px solid ${P.stroke}`, boxShadow: sh}}>
      <div style={{background: mat('panel'), padding: '6px 14px', display: 'flex', gap: 10}}>{[P.heart, P.gold, KG].map((c) => <div key={c} style={{width: 16, height: 16, background: c}} />)}</div>
      <div style={{padding: '14px 20px', minHeight: 120}}>
        {lines.map(([l, c], i) => { const n = Math.max(0, Math.min(l.length, left)); left -= l.length; if (n <= 0 && i > 0) return null;
          return <div key={i} style={txt(32, c ?? mat('dark-text'))}>{l.slice(0, n)}{n < l.length && t % 16 < 8 ? '▌' : ''}</div>; })}
      </div>
    </div>
  );
};

/** 天平：右边「搬得慢」压下去 */
export const scale = (): F => (t) => {
  const a = -9 * prog(t, 20, 18, easeOutBack); // 2026-11-04 去掉落地后持续 ±0.8° 摆动
  return (
    <div style={{position: 'relative', width: 640, height: 300}}>
      <div style={{position: 'absolute', left: 310, top: 70, width: 20, height: 200, background: P.plate}} />
      <div style={{position: 'absolute', left: 230, top: 260, width: 180, height: 24, background: P.plate}} />
      <div style={{position: 'absolute', left: 20, top: 60, width: 600, transform: `rotate(${-a}deg)`, transformOrigin: 'center'}}>
        <div style={{height: 14, background: mat('grey'), border: `3px solid ${P.stroke}`}} />
        <div style={{position: 'absolute', left: -10, top: 14}}><Label text="算得慢" size={38} bg="var(--m-slate)" /></div>
        <div style={{position: 'absolute', right: -10, top: 14}}><Label text="搬得慢" size={38} bg={P.orange} /></div>
      </div>
    </div>
  );
};

/** 问号方块依次落下 */
export const qblocks = (caps: string[]): F => (t) => (
  <div style={{display: 'flex', gap: 70}}>
    {caps.map((c, i) => { const p = prog(t, i * 14, 12, easeOutBack); return (
      <div key={i} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14, opacity: p > 0 ? 1 : 0, transform: `translateY(${(1 - p) * -160}px)`}}>
        <Sprite name="qblock" w={120} /><div style={txt(34)}>{c}</div>
      </div>); })}
  </div>
);
export const check = (text: string, ok = true, dark?: boolean): F => (t) => (
  <div style={{display: 'flex', alignItems: 'center', gap: 22}}>
    <div style={{width: 96, height: 96, background: ok ? KG : P.heart, border: `5px solid ${P.stroke}`, ...txt(72, P.white), display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${1 + 0.3 * (1 - prog(t, 2, 10, easeOutBack))})`, boxShadow: sh}}>{ok ? '✓' : '✕'}</div>
    <div style={txt(48, dark ? P.onPlate : P.text)}>{text}</div>
  </div>
);

/** 仓库 / 工作台 / 显卡 */
export const store = (cap1: string, cap2: string, w = 460): F => () => (
  <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10}}>
    <Sprite name="warehouse" w={w} mute />
    <div style={{display: 'flex', gap: 12}}><Label text={cap1} size={32} /><Label text={cap2} size={32} bg={P.teal} /></div>
  </div>
);
export const bench = (cap: string, w = 360): F => () => (
  <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10}}>
    <Sprite name="bench" w={w} clipTop={0.3} mute />
    <Label text={cap} size={32} bg={P.teal} />
  </div>
);
export const gpu = (cap?: string, w = 420, zzz = false): F => (t) => (
  <div style={{position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8}}>
    <GpuCard w={w} mute speed={zzz ? 0.15 : 1} />
    {cap && <Label text={cap} size={32} />}
    {zzz && ['Z', 'z', 'z'].map((z, i) => { const k = ((t + i * 20) % 60) / 60; return <div key={i} style={{position: 'absolute', left: w * 0.8 + k * 50, top: -10 - k * 90, ...txt(44 - i * 8, mat('muted')), opacity: 1 - k}}>{z}</div>; })}
  </div>
);
/** 108 个小工作台依次点亮 */
export const sms = (): F => (t) => (
  <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12}}>
    <div style={{display: 'grid', gridTemplateColumns: 'repeat(18, 30px)', gap: 5}}>{Array.from({length: 108}).map((_, i) => <Cell key={i} c={i < t * 3 ? (Math.floor(t / 6 + i) % 11 === 0 ? P.gold : P.teal) : mat('cream-dark')} s={30} />)}</div>
    <div style={{display: 'flex', gap: 12}}><Label text="108 个计算单元" size={32} /><Label text="每个 192KB · ~19TB/s" size={32} bg={P.teal} /></div>
  </div>
);
/** 小车在仓库和工作台之间往返，标出第几趟 */
export const cart = (trips: string[] = [], w = 1400): F => (t) => {
  const per = 40; const k = Math.floor(t / per); const ph = (t % per) / per; const dir = k % 2 === 0 ? 1 : -1; const x = dir > 0 ? ph : 1 - ph;
  const L = 330, R = w - 300;
  return (
    <div style={{position: 'relative', width: w, height: 300}}>
      <div style={{position: 'absolute', left: 0, top: 30}}><Sprite name="warehouse" w={300} mute /></div>
      <div style={{position: 'absolute', right: 0, top: 110}}><Sprite name="bench" w={260} clipTop={0.3} mute /></div>
      <div style={{position: 'absolute', left: L, top: 230, width: R - L, height: 12, background: mat('wood-dark'), borderTop: `4px solid ${P.stroke}`, borderBottom: `4px solid ${P.stroke}`}} />
      <div style={{position: 'absolute', left: L + x * (R - L - 110), top: 160}}>
        <div style={{width: 110, height: 60, background: P.orange, border: `5px solid ${P.stroke}`, ...txt(28, P.white), display: 'flex', alignItems: 'center', justifyContent: 'center'}}>N×N</div>
        <div style={{display: 'flex', justifyContent: 'space-between', padding: '0 12px'}}><div style={{width: 18, height: 18, background: P.plate}} /><div style={{width: 18, height: 18, background: P.plate}} /></div>
      </div>
      {trips.length > 0 && <div style={{position: 'absolute', left: L + 40, top: 20, display: 'flex', gap: 12}}>{trips.map((s, i) => <div key={i} style={{...txt(34, P.white), background: i <= k ? (i % 2 ? P.teal : P.orange) : mat('chip-off'), padding: '4px 14px'}}>{s}</div>)}</div>}
    </div>
  );
};
/** 账本：每 30 帧来一块，记 max / sum；出现更大值时闪「缩放」 */
export const ledger = (vals = [2.1, 1.4, 3.6, 2.9], dark = true): F => (t) => {
  const k = Math.min(vals.length, Math.floor(t / 30) + 1); let m = -1, l = 0, rescale = false;
  for (let i = 0; i < k; i++) { const nm = Math.max(m, vals[i]); if (i > 0 && nm > m) rescale = i === k - 1; l = l * Math.exp(m - nm) + Math.exp(vals[i] - nm) * 2; m = nm; }
  const fresh = t % 30 < 14;
  return (
    <div style={{background: dark ? mat('dark-surface') : P.tokenBg, border: `5px solid ${P.stroke}`, padding: '16px 26px', boxShadow: sh, width: 520}}>
      <div style={txt(32, P.gold)}>账本 · 第 {k}/{vals.length} 块</div>
      <div style={{...txt(56, dark ? P.onPlate : P.text), marginTop: 6}}>max m = {m.toFixed(1)}</div>
      <div style={txt(56, dark ? P.onPlate : P.text)}>sum ℓ = {l.toFixed(2)}</div>
      <div style={{...txt(34, P.heart), opacity: rescale && fresh ? 1 : 0}}>新最大值 → 旧结果整体缩放</div>
    </div>
  );
};
/** 一行分数分段进来：已见彩色，未见「?」 */
export const rowChunks = (n = 8, per = 2): F => (t) => {
  const seen = Math.min(n, (Math.floor(t / 30) + 1) * per);
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12}}>
      <div style={{display: 'flex', gap: 8}}>{Array.from({length: n}).map((_, i) => <div key={i} style={{width: 76, height: 76, background: i < seen ? (Math.floor(i / per) === Math.floor((seen - 1) / per) ? P.orange : mat('cell-warm')) : mat('metal'), border: `5px solid ${P.stroke}`, ...txt(40, P.white), display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{i < seen ? '' : '?'}</div>)}</div>
      <div style={txt(34, mat('dark-text'))}>这一行的总和？还不知道</div>
    </div>
  );
};
/** 两条结果对比：长度一致 + ✓ */
export const same = (a: string, b: string): F => (t) => (
  <div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
    {[a, b].map((s, i) => <div key={i} style={{display: 'flex', alignItems: 'center', gap: 16}}><div style={{...txt(34, P.white), width: 220}}>{s}</div><div style={{width: 380 * prog(t, i * 10, 24, easeOut), height: 40, background: i ? P.gold : P.teal, border: `4px solid ${P.stroke}`}} /></div>)}
    <div style={{...txt(44, KG), opacity: t > 40 ? 1 : 0}}>✓ 结果完全一样</div>
  </div>
);
/** 两条计时：从显存读 vs 片上重算 */
export const race = (): F => (t) => (
  <div style={{display: 'flex', flexDirection: 'column', gap: 22}}>
    {[['从显存读大表', 0.6, P.heart], ['片上重算一遍', 1.6, KG]].map(([s, v, c], i) => { const p = Math.min(1, (t * (v as number)) / 90); return (
      <div key={i} style={{display: 'flex', alignItems: 'center', gap: 16}}><ClockSprite px={5} /><div style={{...txt(36, P.text), width: 250}}>{s as string}</div>
        <div style={{width: 360, height: 44, background: mat('cream'), border: `4px solid ${P.stroke}`}}><div style={{width: 352 * p, height: 36, background: c as string}} /></div>
        <div style={{...txt(34, c as string), width: 90}}>{p >= 1 ? '完成' : ''}</div></div>); })}
  </div>
);
/** 反向箭头：箭头组从右往左流 */
export const back = (text: string): F => (t) => (
  <div style={{display: 'flex', alignItems: 'center', gap: 20}}>
    <div style={{display: 'flex', gap: 6}}>{Array.from({length: 6}).map((_, i) => <div key={i} style={{...txt(64, (Math.floor(t / 5) + i) % 6 === 0 ? P.orange : mat('slate'))}}>◀</div>)}</div>
    <Label text={text} size={48} bg={P.plate} color={P.gold} />
  </div>
);
/** 只存 O + (m, ℓ) */
export const keep = (): F => (t) => (
  <div style={{display: 'flex', gap: 24, alignItems: 'center'}}>
    <div style={txt(36)}>只存：</div>
    {['O', '(m, ℓ)'].map((s, i) => <div key={i} style={{...txt(52, P.text), background: i ? P.gold : mat('dark-cell-lit'), border: `5px solid ${P.stroke}`, padding: '8px 24px', boxShadow: sh, opacity: t > i * 12 ? 1 : 0}}>{s}</div>)}
  </div>
);
/** 总装：5 个零件飞进机器 */
export const machine = (parts: string[]): F => (t) => (
  <div style={{position: 'relative', width: 1400, height: 340}}>
    {parts.map((s, i) => { const p = prog(t, 10 + i * 10, 22, easeOut); return (
      <div key={i} style={{position: 'absolute', left: 30 + i * 150 + p * (560 - i * 150), top: 30 + (i % 2) * 120 + p * (130 - (i % 2) * 120), opacity: 1 - prog(t, 30 + i * 10, 6), ...txt(30, P.white), background: [P.orange, P.teal, KG, P.gold, mat('slate')][i], padding: '8px 14px', border: `4px solid ${P.stroke}`}}>{s}</div>); })}
    <div style={{position: 'absolute', left: 820, top: 50, width: 520, height: 240, background: mat('panel'), border: `6px solid ${P.stroke}`, boxShadow: sh, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14}}>
      <div style={{display: 'flex', gap: 10}}>{Array.from({length: 5}).map((_, i) => <div key={i} style={{width: 26, height: 26, background: t > 30 + i * 10 ? [P.orange, P.teal, KG, P.gold, mat('slate')][i] : mat('dark-surface'), border: `3px solid ${P.stroke}`}} />)}</div>
      <div style={{background: P.gold, padding: '8px 22px', display: 'flex', gap: 10, alignItems: 'center', transform: t > 80 && t < 90 ? 'scale(1.08)' : undefined}}><BoltSprite px={5} /><span style={txt(52)}>FlashAttention</span></div>
    </div>
  </div>
);
/** 线性 vs 平方 曲线 */
export const curve = (): F => (t) => {
  const p = prog(t, 0, 40, easeOut); const W = 560, H = 280;
  const pts = (fn: (x: number) => number) => Array.from({length: 20}).map((_, i) => { const x = (i / 19) * p; return `${30 + x * W},${H - fn(x) * (H - 20)}`; }).join(' ');
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 20}}>
      <svg width={W + 40} height={H + 10} style={{background: P.tokenBg, border: `5px solid ${P.stroke}`}}>
        <polyline points={pts((x) => x * x)} fill="none" stroke={P.heart} strokeWidth={8} />
        <polyline points={pts((x) => x * 0.35)} fill="none" stroke={P.teal} strokeWidth={8} />
      </svg>
      <div style={{display: 'flex', flexDirection: 'column', gap: 12}}><Label text="标准：平方" size={32} bg={P.heart} /><Label text="FA：线性" size={32} bg={P.teal} /></div>
    </div>
  );
};
/** 支持卡表，3080 一行亮起 */
export const archs = (): F => (t) => (
  <div style={{display: 'flex', flexDirection: 'column', gap: 10}}>
    {[['Ampere', 'A100 · RTX 3090 · 3080'], ['Ada', 'RTX 4090'], ['Hopper', 'H100']].map(([a, b], i) => { const hot = i === 0 && t > 40 && Math.floor(t / 10) % 2 === 0; return (
      <div key={i} style={{display: 'flex', gap: 14, alignItems: 'center', opacity: t > i * 10 ? 1 : 0}}>
        <div style={{...txt(38, P.white), background: hot ? P.orange : P.plate, width: 200, padding: '6px 14px'}}>{a}</div><div style={txt(36)}>{b}</div>{i === 0 && t > 40 && <div style={txt(34, P.orange)}>← 我的卡</div>}</div>); })}
  </div>
);
/** ⑨ 完整流程：Q 块上片、K/V 块轮流进来、账本走、输出写回 */
export const pipeline = (blocks = 4): F => (t) => {
  const k = Math.floor(t / 30) % (blocks + 1); const done = k === blocks;
  return (
    <div style={{position: 'relative', width: 1500, height: 330}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: 360, height: 320, background: mat('panel'), border: `5px solid ${P.stroke}`, padding: 14, boxSizing: 'border-box'}}>
        <div style={txt(32, mat('dark-text'))}>HBM 显存</div>
        <div style={{display: 'flex', gap: 8, marginTop: 10}}>{Array.from({length: 4}).map((_, i) => <Cell key={i} c={i === 0 ? mat('grey') : P.orange} s={54} />)}</div>
        <div style={{display: 'flex', gap: 8, marginTop: 10}}>{Array.from({length: blocks}).map((_, i) => <Cell key={i} c={i < k ? mat('grey') : KG} s={54} />)}</div>
        <div style={{display: 'flex', gap: 8, marginTop: 10}}>{Array.from({length: 4}).map((_, i) => <Cell key={i} c={i === 0 && done ? mat('dark-cell-lit') : mat('grey')} s={54} />)}</div>
      </div>
      <div style={{position: 'absolute', left: 380 + ((t % 30) / 30) * 260, top: 120, opacity: done ? 0 : 1}}><Cell c={KG} s={60} /></div>
      <div style={{position: 'absolute', left: 700, top: 0, width: 420, height: 320, background: mat('dark-surface'), border: `5px solid ${P.gold}`, padding: 16, boxSizing: 'border-box'}}>
        <div style={txt(32, P.gold)}>SRAM 片上</div>
        <div style={{display: 'flex', gap: 14, marginTop: 14}}><Cell c={P.orange} s={90} /><Cell c={done ? mat('metal') : KG} s={90} /><Cell c={done ? mat('dark-cell-lit') : mat('metal')} s={90} /></div>
        <div style={{...txt(34, P.white), marginTop: 18}}>{done ? '这块 Q 算完 → 写回' : `第 ${k + 1} 块 K、V`}</div>
      </div>
      <div style={{position: 'absolute', left: 1150, top: 30, ...txt(40, P.white)}}>m = {(2 + k * 0.4).toFixed(1)}</div>
      <div style={{position: 'absolute', left: 1150, top: 90, ...txt(40, P.white)}}>ℓ = {(1 + k * 1.7).toFixed(1)}</div>
      <div style={{position: 'absolute', left: 1150, top: 170}}><Label text="N×N 表：0 次落显存" size={30} bg="var(--m-panel)" /></div>
    </div>
  );
};
/** 结尾：思考题 / 口号卡 */
export const quiz = (): F => (t) => (
  <div style={{background: P.tokenBg, border: `6px solid ${P.stroke}`, padding: '20px 40px', boxShadow: sh, textAlign: 'center'}}>
    <div style={txt(40, P.orange)}>思考题</div>
    <div style={txt(60)}>块为什么不能无限大？</div>
    <div style={{...txt(40, P.teal), opacity: t > 60 ? 1 : 0}}>提示：192KB</div>
  </div>
);
export const code = (text: string, w = 1300): F => (t) => (
  <div style={{width: w, background: mat('term-bg'), border: `5px solid ${P.stroke}`, padding: '20px 26px', boxShadow: sh}}>
    <span style={txt(40, mat('dark-text'))}>{text.slice(0, Math.floor(t * 1.4))}</span><span style={{...txt(40, P.gold), opacity: t % 16 < 8 ? 1 : 0}}>▌</span>
  </div>
);
export const sprite = (name: string, w: number, cap?: string): F => () => (
  <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10}}><Sprite name={name} w={w} />{cap && <Label text={cap} size={32} />}</div>
);
export const row = (...fs: F[]): F => (t) => <div style={{display: 'flex', gap: 30, alignItems: 'center'}}>{fs.map((f, i) => <div key={i}>{f(t)}</div>)}</div>;

/** 存储层级金字塔：上窄下宽 */
export const tiers = (): F => (t) => (
  <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10}}>
    {[['SRAM 片上 · 192KB · ~19TB/s', 380, P.teal], ['HBM 显存 · 40–80GB · 1.5–2TB/s', 820, mat('tier-mid')]].map(([s, w, c], i) => (
      <div key={i} style={{width: (w as number) * prog(t, i * 10, 14, easeOut), height: 92, background: c as string, border: `5px solid ${P.stroke}`, boxShadow: sh, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', ...txt(38, P.white)}}>{s as string}</div>))}
    <div style={txt(34)}>↑ 小而快 · 大而慢 ↓</div>
  </div>
);
/** 计算核心的时间占比：等数据 vs 计算 */
export const util = (dark = true): F => (t) => (
  <div style={{display: 'flex', flexDirection: 'column', gap: 16}}>
    {[['等数据', 0.85, P.heart], ['真正计算', 0.15, KG]].map(([s, v, c], i) => (
      <div key={i} style={{display: 'flex', alignItems: 'center', gap: 16}}>
        <div style={{...txt(40, dark ? P.onPlate : P.text), width: 190}}>{s as string}</div>
        <div style={{width: 460, height: 48, background: mat('panel'), border: `4px solid ${P.stroke}`}}><div style={{width: 452 * (v as number) * prog(t, 0, 30, easeOut), height: 40, background: c as string}} /></div>
      </div>))}
    <div style={txt(28, mat('slate'))}>（示意，非实测比例）</div>
  </div>
);
