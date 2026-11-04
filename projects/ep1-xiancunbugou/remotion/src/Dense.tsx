// v3 填充度：全屏爆点墙 / 全屏章节卡 / 常驻数据面板 / 左侧章节签
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {useDesignFrame} from './timeline/fps';
import {FONT, FontFace, Frame, P, StarBg} from './kit';
import {Cue, CueSub, useProg, NAME} from './Motion';

export const STAGES = ['注意力', '存储层级', '访存瓶颈', '分块', '在线softmax', '重算', '总装', '怎么用', '完整流程'];
const rnd = (i: number) => { const v = Math.sin(i * 12.9898 + 78.233) * 43758.5453; return v - Math.floor(v); };
// 亮度铺满 15%–85%：内容墙本身要有层次，不是一块纯色
const HUES = [205, 168, 32, 48, 280, 350, 120, 18, 190];
export const heat = (v: number, hue: number) => `hsl(${hue + (v - 0.5) * 40}, ${55 + 30 * v}%, ${14 + 72 * v}%)`;

export const CARD_BURST = new Set<string>();
export type BurstKind = 'matrix' | 'numbers' | 'gpus';
/** 全屏信息墙：N×N 打分矩阵（每行 softmax）/ 满屏数字墙 / GPU 阵列利用率 */
export const BurstWall: React.FC<{kind: BurstKind; t: number; dur: number; stage: number; caption?: string; seed?: number}> = ({kind, t, dur, stage, caption, seed = 1}) => {
  const C = 32, R = 18, cw = 1920 / C, ch = 1080 / R;
  const hue = HUES[(stage - 1 + 9) % 9];
  const wipe = Math.min(1, t / 8); const out = t > dur - 6 ? Math.max(0, (dur - t) / 6) : 1;
  const row = Math.floor(t / 3) % R;
  // matrix：每行原始分数做 softmax，归一到 0–1 显示
  const vals: number[] = [];
  for (let y = 0; y < R; y++) {
    const raw = Array.from({length: C}, (_, x) => 3 * rnd(seed * 997 + y * C + x) - Math.abs(x - y * C / R) * 0.08);
    const mx = Math.max(...raw); const e = raw.map((r) => Math.exp(r - mx)); const s = e.reduce((a, b) => a + b, 0);
    const p = e.map((v) => v / s); const pm = Math.max(...p);
    p.forEach((v) => vals.push(kind === 'gpus' ? rnd(seed * 31 + y * C + v * 1e3) * 0.9 + 0.08 : Math.pow(v / pm, 0.45)));
  }
  return (
    <AbsoluteFill style={{opacity: out}}>
      <svg width={1920} height={1080} shapeRendering="crispEdges" style={{position: 'absolute'}}>
        {vals.map((v, i) => { const x = i % C, y = Math.floor(i / C); if ((x + y) / (C + R) > wipe * 1.05) return null;
          const hot = kind !== 'gpus' && y === row; const g = kind === 'gpus' ? 6 : 5;
          const vv = kind === 'gpus' ? Math.min(1, v * (0.82 + 0.18 * Math.min(1, wipe * 1.4))) : v;
          return <g key={i}>
            <rect x={x * cw + g / 2} y={y * ch + g / 2} width={cw - g} height={ch - g} fill={hot ? P.white : heat(vv, hue)} />
            {kind === 'gpus' && <rect x={x * cw + 8} y={y * ch + ch - 14} width={(cw - 16) * vv} height={6} fill={P.black} />}
            {kind === 'numbers' && <text x={x * cw + cw / 2} y={y * ch + ch * 0.68} fontSize={22} textAnchor="middle" fontFamily="monospace" fill={vv > 0.5 ? '#111' : '#eee'}>{(v * 0.99).toFixed(2).slice(1)}</text>}
          </g>; })}
      </svg>
      {caption && <div style={{position: 'absolute', left: 0, right: 0, top: 390, textAlign: 'center'}}>
        <span style={{display: 'inline-block', fontFamily: FONT, fontSize: 120, color: P.white, background: '#0d0c12', padding: '10px 50px', transform: `scale(${0.85 + 0.15 * wipe})`}}>{caption}</span>
      </div>}
    </AbsoluteFill>
  );
};

/** 全屏章节卡：矩阵墙铺满 + 巨型序号 + ≥300px 标题 */
export const BigCard: React.FC<{stage: number; title: string; cues: Cue[]; keys?: string[]; burst?: boolean}> = ({stage, title, cues, keys = [], burst}) => {
  const f = useDesignFrame();
  const wall = (burst ?? CARD_BURST.has('card' + stage)) && f < 60;
  const wlen = [...title].reduce((a, c) => a + (/[\x00-\x7f]/.test(c) ? 0.6 : 1), 0); const fs = Math.min(300, 1150 / wlen);
  return (
    <AbsoluteFill><FontFace /><StarBg />
      {wall && <BurstWall kind={stage % 2 ? 'matrix' : 'numbers'} t={f * 1.5} dur={90} stage={stage} seed={stage * 13} />}
      <div style={{position: 'absolute', left: 120, right: 120, top: 200, height: 560, background: wall ? '#0d0c12' : heat(0.45, HUES[(stage + 8) % 9]), display: 'flex', alignItems: 'center', gap: 50, padding: '0 60px',
        transform: `scale(${0.9 + 0.1 * Math.min(1, f / 10)})`}}>
        <div style={{fontFamily: FONT, fontSize: 380, lineHeight: 1, color: P.gold}}>{String(stage).padStart(2, '0')}</div>
        <div>
          <div style={{fontFamily: FONT, fontSize: 56, color: P.orange}}>STAGE {stage} / 9</div>
          <div style={{fontFamily: FONT, fontSize: fs, lineHeight: 1.05, color: P.white, whiteSpace: 'nowrap'}}>{title}</div>
        </div>
      </div>
      <Frame progress={useProg(f)} count={stage} name={NAME} dark />
      <CueSub cues={cues} keys={keys} />
    </AbsoluteFill>
  );
};

/** 右上常驻数据面板：章节进度、当前句序号、片内进度格（全部从镜头数据算） */
export const DataPanel: React.FC<{stage: number; cue: number; cues: number; prog: number; dark?: boolean}> = ({stage, cue, cues, prog, dark}) => {
  const hue = HUES[(stage - 1 + 9) % 9]; const lit = Math.round(prog * 60);
  const tx = {fontFamily: FONT, color: P.white, fontSize: 30};
  return (
    <div style={{position: 'absolute', left: 1500, top: 96, width: 380, background: dark ? '#23263a' : '#2b2838', padding: 18, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 10}}>
      <div style={{...tx, color: P.gold}}>STAGE {stage}/9 · {STAGES[stage - 1] ?? '收尾'}</div>
      <div style={tx}>句 {cue + 1} / {cues}</div>
      <svg width={344} height={150} shapeRendering="crispEdges">
        {Array.from({length: 60}).map((_, i) => <rect key={i} x={(i % 12) * 29} y={Math.floor(i / 12) * 30} width={26} height={27} fill={i < lit ? heat(0.35 + 0.6 * rnd(i + stage * 60), hue) : '#3d3a4e'} />)}
      </svg>
      <div style={{...tx, fontSize: 24}}>全片进度 {Math.round(prog * 100)}%</div>
      <div style={{display: 'flex', gap: 4}}>{STAGES.map((_, i) => <div key={i} style={{flex: 1, height: 22, background: i < stage ? heat(0.7, HUES[i]) : '#3d3a4e'}} />)}</div>
    </div>
  );
};

/** 左侧章节签 + 进度刻度 */
export const ChapterTab: React.FC<{stage: number; prog: number}> = ({stage, prog}) => (
  <div style={{position: 'absolute', left: 36, top: 120, width: 96, height: 700, background: '#2b2838', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '14px 0', boxSizing: 'border-box', gap: 8}}>
    <div style={{fontFamily: FONT, fontSize: 48, color: P.gold}}>{String(stage).padStart(2, '0')}</div>
    {STAGES.map((s, i) => <div key={i} style={{width: 64, height: 50, background: i + 1 === stage ? heat(0.75, HUES[i]) : i + 1 < stage ? heat(0.4, HUES[i]) : '#3d3a4e', fontFamily: FONT, fontSize: 22, color: P.white, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{i + 1}</div>)}
    <div style={{width: 64, height: 100, background: '#3d3a4e', position: 'relative'}}><div style={{position: 'absolute', bottom: 0, width: 64, height: 100 * prog, background: P.green}} /></div>
  </div>
);

/** v3.1 分块章填充：一整行打分被切成 8 块，逐块"上片→记账"，当前块高亮（实心面板，不透明） */
export const BlockStrip: React.FC<{f: number; total: number; stage: number; x?: number; y?: number; w?: number; h?: number; title?: string}> = ({f, total, stage, x = 190, y = 680, w = 1200, h = 190, title}) => {
  const hue = HUES[(stage - 1 + 9) % 9]; const B = 8, R = 3, per = 4;
  const cur = Math.min(B - 1, Math.floor((f / Math.max(1, total)) * B * 1.15));
  const cw = (w - 40) / (B * per), rh = (h - 70) / R;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, background: '#2b2838', boxSizing: 'border-box', padding: '10px 20px'}}>
      <div style={{fontFamily: FONT, fontSize: 30, color: P.gold, height: 44}}>{title ?? `一整行打分 → 切成 ${B} 块 · 第 ${cur + 1}/${B} 块在片上`}</div>
      <svg width={w - 40} height={h - 70} shapeRendering="crispEdges">
        {Array.from({length: B * per * R}).map((_, i) => { const c = i % (B * per), r = Math.floor(i / (B * per)), b = Math.floor(c / per);
          const v = 0.25 + 0.7 * rnd(i + stage * 101 + Math.floor(f / 20) * (b === cur ? 1 : 0));
          return <rect key={i} x={c * cw + (b * 6) / per} y={r * rh} width={cw - 4} height={rh - 4} fill={b === cur ? (Math.floor(f / 8) % 2 ? P.white : heat(0.9, hue)) : b < cur ? heat(v, hue) : '#4a4660'} />; })}
      </svg>
    </div>
  );
};
