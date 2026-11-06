// EP-20261029-01 火箭水母云 v1：实拍（预裁 1080×1920，footage/clips.py）+ 两段 Remotion 示意动画。无 AI 生成画面。
import React from 'react';
import {AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {CINNABAR, CornerLabel, GOLD, INK, PAPER, SMILEY, W, H, c01, easeOut, lerp} from './common/theme';
import {CUTS, NAMES, TOTAL} from './data/cuts_v1';
import {KT} from './data/kt';
export {CUTS, NAMES, TOTAL};
const sg = (t: number, a: number, b: number) => c01((t - a) / Math.max(1e-3, b - a));
const useT = (i: number) => { const f = useCurrentFrame(); const {fps} = useVideoConfig(); return CUTS[i] + f / fps; };
export const SHOT_END = (i: number) => (i < CUTS.length - 1 ? CUTS[i + 1] : TOTAL);
const CREDIT: Record<string, string> = {
  jn: '画面：AlphaStar · 济南千佛山', am: '画面：Atumu · 山西忻州', ws: '画面：Windsky', tl: '画面：玻纤轻木 · 太原理工大学',
  cc: '画面：央视 CCTV-13', cc_bj: '画面：央视 CCTV-13（北京网友拍摄）', cc_ty: '画面：央视 CCTV-13（太原网友拍摄）', d: '示意图（高度已夸大）',
};
const credit = (n: string) => n.startsWith('d') ? CREDIT.d : n === 'c07_cc_bj' ? CREDIT.cc_bj : n === 'c06b_cc_ty' ? CREDIT.cc_ty : CREDIT[n.split('_')[1]];

// ---------- 通用标注（大字号） ----------
const STROKE = {WebkitTextStroke: '10px #000', paintOrder: 'stroke fill'} as React.CSSProperties;
export const Chip: React.FC<{x: number; y: number; text: string; p: number; size?: number; color?: string; bg?: string; anchor?: 'left' | 'center' | 'right'}> = ({x, y, text, p, size = 64, color = PAPER, bg = 'rgba(8,8,12,.72)', anchor = 'center'}) => {
  if (p <= 0) return null; const e = easeOut(sg(p, 0, 1)); const tx = anchor === 'center' ? '-50%' : anchor === 'right' ? '-100%' : '0';
  return <div style={{position: 'absolute', left: x, top: y, transform: `translate(${tx},-50%) scale(${0.8 + 0.2 * e})`, opacity: e, fontFamily: SMILEY, fontWeight: 700, fontSize: size, color, whiteSpace: 'pre', ...(text.includes('\n') ? {lineHeight: 1.12, textAlign: 'left' as const} : {}), background: bg, padding: `${size * 0.14}px ${size * 0.36}px`, borderRadius: size * 0.22, border: '2px solid rgba(239,232,218,.3)', zIndex: 45, boxShadow: '0 8px 24px rgba(0,0,0,.45)'}}>{text}</div>;
};
/** 朱印戳：p = (t-出现)/0.25 */
const Stamp: React.FC<{text: string; p: number; x?: number; y?: number; size?: number; rot?: number}> = ({text, p, x = W / 2, y = 430, size = 130, rot = -4}) => {
  if (p <= 0) return null; const s = lerp(1.7, 1, easeOut(sg(p, 0, 1)));
  return <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) scale(${s}) rotate(${rot}deg)`, opacity: c01(p * 3), zIndex: 50, background: PAPER, border: `${Math.round(size / 13)}px solid ${CINNABAR}`, borderRadius: 16, padding: `${size / 9}px ${size / 2.6}px`, boxShadow: '0 12px 30px rgba(0,0,0,.6)'}}>
    <div style={{fontFamily: SMILEY, fontWeight: 700, fontSize: size, color: CINNABAR, lineHeight: 1.05, whiteSpace: 'nowrap'}}>{text}</div></div>;
};
const CrossOut: React.FC<{text: string; p: number; q: number; y?: number}> = ({text, p, q, y = 430}) => p <= 0 ? null : <div style={{position: 'absolute', left: W / 2, top: y, transform: `translate(-50%,-50%) scale(${0.8 + 0.2 * easeOut(c01(p))})`, opacity: easeOut(c01(p)), zIndex: 50}}>
  <div style={{fontFamily: SMILEY, fontWeight: 700, fontSize: 150, color: PAPER, ...STROKE}}>{text}</div>
  {q > 0 && <svg width={420} height={240} style={{position: 'absolute', left: '50%', top: '50%', transform: `translate(-50%,-50%) scale(${lerp(1.5, 1, easeOut(c01(q)))})`, opacity: c01(q * 4)}}><path d="M50 40 L370 200 M370 40 L50 200" stroke={CINNABAR} strokeWidth={26} strokeLinecap="round" /></svg>}
</div>;
const Leader: React.FC<{x1: number; y1: number; x2: number; y2: number; p: number; text: string; size?: number}> = ({x1, y1, x2, y2, p, text, size = 76}) => {
  if (p <= 0) return null; const e = easeOut(c01(p)); const xe = lerp(x1, x2, e), ye = lerp(y1, y2, e);
  return <>
    <svg width={W} height={H} style={{position: 'absolute', inset: 0, zIndex: 44}}><line x1={x1} y1={y1} x2={xe} y2={ye} stroke="#000" strokeWidth={12} strokeLinecap="round" /><line x1={x1} y1={y1} x2={xe} y2={ye} stroke={GOLD} strokeWidth={6} strokeLinecap="round" /><circle cx={x2} cy={y2} r={14 * e} fill={GOLD} stroke="#000" strokeWidth={4} /></svg>
    <Chip x={x1} y={y1} text={text} p={p * 1.5} size={size} color="#ffe9c4" />
  </>;
};

// ---------- 实拍镜头：预裁视频 + 单向慢推（不摆动） ----------
const PUSH: Record<string, [number, number, number, number]> = { // [s1, originX, originY, 起始缩放]
  c01_am_open: [1.08, 320, 1050, 1], c09_jn_sd: [1.09, 540, 900, 1], c06b_cc_ty: [1.08, 540, 800, 1], c05_cc_lift: [1.12, 540, 600, 1], c04_am_rocket: [1.18, 540, 960, 1],
  c15_am_jelly: [1.14, 380, 640, 1], c18_ws_empty: [1.08, 540, 900, 1], c19_jn_end: [1.07, 540, 1100, 1], c14_ws_ice: [1.1, 660, 760, 1], c08_tl_sx: [1.25, 340, 275, 1], /* v6h：尾迹头部局部 100→125% 缓推 */
};
const Real: React.FC<{i: number}> = ({i}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig(); const n = NAMES[i]; const dur = SHOT_END(i) - CUTS[i];
  const [s1, ox, oy, s0] = PUSH[n] || [1.055, 540, 860, 1];
  const s = lerp(s0, s1, c01(f / fps / dur));
  return <AbsoluteFill style={{overflow: 'hidden', background: INK}}>
    <AbsoluteFill style={{transform: `scale(${s})`, transformOrigin: `${ox}px ${oy}px`, ...(n === 'c05_cc_lift' ? {filter: `brightness(${lerp(0.85, 1, c01(f / fps / 0.2)).toFixed(3)})`} : {})}}>  {/* v6d：c05 开头 0.2 s 亮度 85%→100% */}
      <OffthreadVideo src={staticFile(`footage/${n}.mp4`)} muted style={{width: W, height: H}} />
    </AbsoluteFill>
  </AbsoluteFill>;
};

// ---------- 三条件清单（c16–c19 连续） ----------
const CONDS = ['清晨或傍晚发射', '高空没大风', '头顶没厚云'];
const Checklist: React.FC<{t: number}> = ({t}) => {
  const show = sg(t, KT.san3 - 0.1, KT.san3 + 0.25); if (show <= 0) return null;
  const on = [KT.k1, KT.k2, KT.k3]; const fail = t >= KT.shao1 && t < CUTS[NAMES.indexOf('c19_jn_end')];
  const allOn = t >= KT.quan - 0.05;
  return <div style={{position: 'absolute', left: 90, top: 380, zIndex: 46}}>
    {CONDS.map((c, k) => { const p = sg(t, KT.san3 - 0.1 + k * 0.12, KT.san3 + 0.2 + k * 0.12); const ok = t >= on[k] - 0.05; const bad = fail && k === 1;
      const glow = allOn ? 0.5 + 0.5 * Math.sin((t - KT.quan) * 9 + k) : 0;
      const dim = fail && !bad ? 0.55 : 1;
      return <div key={k} style={{display: 'flex', alignItems: 'center', marginBottom: 34, opacity: easeOut(p) * dim, transform: `translateX(${lerp(-80, 0, easeOut(p))}px)`}}>
        <div style={{width: 104, height: 104, borderRadius: 18, border: `6px solid ${bad ? CINNABAR : ok ? GOLD : PAPER}`, background: 'rgba(8,8,12,.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: allOn ? `0 0 ${30 * glow + 10}px ${GOLD}` : 'none'}}>
          {bad ? <svg width={70} height={70}><path d="M12 12 L58 58 M58 12 L12 58" stroke={CINNABAR} strokeWidth={12} strokeLinecap="round" /></svg>
            : ok ? <svg width={74} height={74}><path d={`M10 38 L30 58 L66 14`} stroke={GOLD} strokeWidth={12} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={100} strokeDashoffset={100 * (1 - easeOut(sg(t, on[k] - 0.05, on[k] + 0.2)))} /></svg> : null}
        </div>
        <div style={{marginLeft: 30, fontFamily: SMILEY, fontWeight: 700, fontSize: 84, color: bad ? '#ff9a90' : ok ? '#ffe9c4' : PAPER, ...STROKE, textDecoration: bad ? 'line-through' : 'none', textDecorationColor: CINNABAR}}>{c}</div>
      </div>; })}
  </div>;
};

// ---------- 示意 1：地球影子（高度夸大） ----------
const D1: React.FC = () => {
  const i = NAMES.indexOf('d1_shadow'); const t = useT(i); const t0 = CUTS[i], t1 = SHOT_END(i);
  const C = {x: 540, y: 3330}, R = 1900; const P = {x: 540, y: C.y - R};
  const d = (lerp(4, 24, easeOut(sg(t, t0, KT.dimian + 0.3))) * Math.PI) / 180;
  const u = {x: -Math.cos(d), y: -Math.sin(d)}; const n = {x: Math.sin(d), y: -Math.cos(d)};
  const T = {x: C.x + R * n.x, y: C.y + R * n.y}; const B = {x: C.x - R * n.x, y: C.y - R * n.y}; const L = 5000;
  const shadow = `M${T.x},${T.y} L${T.x + L * u.x},${T.y + L * u.y} L${B.x + L * u.x},${B.y + L * u.y} L${B.x},${B.y} Z`;
  const hLine = C.y - R / Math.cos(d); // 观测者正上方影子边界 y
  const sun = {x: 1000, y: P.y - 40 + 520 * Math.tan(d)};
  const push = lerp(1, 1.07, sg(t, t0, t1));
  const flow = (t - t0) * 260;
  const rays = Array.from({length: 26}, (_, k) => -500 + k * 80);
  // 火箭：从地面升起，在 KT.shai 前后冲出影子
  const rk = sg(t, KT.gaokong + 0.3, t1 + 0.4); const ry = lerp(P.y - 6, hLine - 330, Math.pow(rk, 1.25));
  const lit = ry < hLine;
  const pSun = sg(t, KT.luoshan - 0.1, KT.luoshan + 0.25), pGround = sg(t, KT.dimian - 0.1, KT.dimian + 0.25), pShadow = sg(t, KT.yingzi - 0.1, KT.yingzi + 0.25), pHigh = sg(t, KT.gaokong - 0.1, KT.gaokong + 0.25);
  return <AbsoluteFill style={{background: INK, overflow: 'hidden'}}>
    <AbsoluteFill style={{transform: `scale(${push})`, transformOrigin: `540px ${P.y - 200}px`}}>
      <svg width={W} height={H}>
        <defs>
          <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#0b1430" /><stop offset="0.7" stopColor="#24366a" /><stop offset="1" stopColor="#3c4f86" /></linearGradient>
          <radialGradient id="sunG"><stop offset="0" stopColor="#fff4d0" /><stop offset="0.35" stopColor="#ffc35a" /><stop offset="1" stopColor="#ff8a2a" stopOpacity={0} /></radialGradient>
          <mask id="lightM"><rect width={W} height={H} fill="#fff" /><path d={shadow} fill="#000" /></mask>
          <linearGradient id="ray" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stopColor="#ffd27a" stopOpacity={0.9} /><stop offset="1" stopColor="#ffd27a" stopOpacity={0.35} /></linearGradient>
        </defs>
        <rect width={W} height={H} fill="url(#sky)" />
        <g mask="url(#lightM)">
          <rect width={W} height={H} fill="#ffb347" opacity={0.18} />
          {rays.map((o, k) => { const sx = 1200, sy = sun.y + o; return <line key={k} x1={sx} y1={sy} x2={sx + 2600 * u.x} y2={sy + 2600 * u.y} stroke="url(#ray)" strokeWidth={5} strokeDasharray="60 40" strokeDashoffset={-flow} opacity={0.75} />; })}
        </g>
        <path d={shadow} fill="#050814" opacity={0.55} />
        <circle cx={sun.x} cy={sun.y} r={150} fill="url(#sunG)" />
        <circle cx={sun.x} cy={sun.y} r={52} fill="#ffe7a8" />
        <circle cx={C.x} cy={C.y} r={R} fill="#101a2e" stroke="#4d6aa8" strokeWidth={6} />
        {Array.from({length: 40}, (_, k) => { const a = -Math.PI / 2 + (k - 20) * 0.012; return <circle key={k} cx={C.x + (R - 14 - (k % 3) * 8) * Math.cos(a)} cy={C.y + (R - 14 - (k % 3) * 8) * Math.sin(a)} r={4 + (k % 2) * 2} fill="#ffcf6b" opacity={0.6 + 0.4 * Math.sin(k * 7 + t * 6)} />; })}
        {/* 影子边界（观测者头顶） */}
        <line x1={0} y1={hLine} x2={W} y2={hLine} stroke={GOLD} strokeWidth={4} strokeDasharray="18 14" opacity={pHigh} />
        {/* 火箭与尾迹 */}
        {rk > 0 && <g>
          <path d={`M${P.x},${P.y - 4} L${P.x},${Math.max(ry, hLine)}`} stroke="#8d97ad" strokeWidth={10} opacity={0.8} />
          {lit && <path d={`M${P.x},${hLine} L${P.x},${ry}`} stroke="#fff3cf" strokeWidth={16} style={{filter: 'drop-shadow(0 0 18px #ffd27a)'}} />}
          {lit && <circle cx={P.x} cy={ry} r={16 + 16 * sg(hLine - ry, 0, 300)} fill="#fff3cf" opacity={0.85} style={{filter: 'blur(6px)'}} />}
          <path d={`M${P.x - 12},${ry + 20} L${P.x},${ry - 26} L${P.x + 12},${ry + 20} Z`} fill="#fff" />
        </g>}
        {/* 观测者 */}
        <circle cx={P.x} cy={P.y - 6} r={16} fill={CINNABAR} stroke="#fff" strokeWidth={4} opacity={pGround} />
      </svg>
    </AbsoluteFill>
    <Chip x={1040} y={1220} anchor="right" text="太阳已落山 30 多分钟" p={pSun} size={58} bg="rgba(0,0,0,.88)" />  {/* v6c：底加深 */}
    <Chip x={540} y={1530} text="地面：天黑了" p={pGround} size={72} />
    <Chip x={190} y={hLine * 1.0 + 160} anchor="left" text="地球的影子" p={pShadow} size={66} color="#a9c1ff" />
    <Chip x={540} y={hLine - 420} text="几十～上百公里：还有阳光" p={pHigh} size={66} color="#ffe2a0" />
  </AbsoluteFill>;
};

// ---------- 示意 2：尾焰随高度胀开 ----------
const rand = (k: number) => { const x = Math.sin(k * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const DOTS = Array.from({length: 520}, (_, k) => ({x: rand(k) * W, a: -7 * Math.log(1 - rand(k + 999) * 0.999), v: 0.4 + rand(k + 77)}));
const D2: React.FC = () => {
  const i = NAMES.indexOf('d2_plume'); const t = useT(i); const t0 = CUTS[i], t1 = SHOT_END(i);
  const Y0 = 1480, Y100 = 300; const yA = (a: number) => lerp(Y0, Y100, a / 100);
  const climb = easeOut(sg(t, t0 + 0.2, KT.yibai + 0.2)) * 0.15 + sg(t, t0 + 0.2, KT.yibai + 0.2) * 0.85;
  const alt = lerp(2, 100, Math.pow(climb, 1.6));
  const ry = yA(alt); const X = 610;
  const wOf = (a: number) => 9 + 300 * Math.pow(a / 100, 2.6) + (t > KT.bwfz ? 0 : 0);
  const bloom = sg(t, t1 - 0.9, t1);
  const PA: [number, number][] = [[0, 101325], [10, 26500], [20, 5529], [30, 1197], [40, 287.1], [50, 79.78], [60, 21.96], [70, 5.221], [80, 1.052], [90, 0.1836], [100, 0.03201]]; // US Std Atmosphere 1976
  const k10 = Math.min(9, Math.floor(alt / 10)); const fr10 = (alt - PA[k10][0]) / 10; const pa = Math.exp(lerp(Math.log(PA[k10][1]), Math.log(PA[k10 + 1][1]), fr10)); const N = 101325 / pa;
  const fmtN = N < 10 ? N.toFixed(1) : N < 10000 ? Math.round(N).toLocaleString('en-US') : `${Math.round(N / 10000)}万`;
  const trail: string[] = []; for (let a = 0; a <= alt; a += 1) trail.push(`${X + wOf(a) * 0.55},${yA(a)}`);
  const trailL: string[] = []; for (let a = alt; a >= 0; a -= 1) trailL.push(`${X - wOf(a) * 0.55},${yA(a)}`);
  const headR = wOf(alt) * (1 + 1.6 * easeOut(bloom));
  const pChou = sg(t, KT.chou - 0.1, KT.chou + 0.25), pXi = sg(t, KT.shao - 0.1, KT.shao + 0.25), pBw = sg(t, KT.bwfz - 0.1, KT.bwfz + 0.25);
  return <AbsoluteFill style={{overflow: 'hidden', background: INK}}>
    <AbsoluteFill style={{transform: `scale(${lerp(1, 1.05, sg(t, t0, t1))})`, transformOrigin: '540px 900px'}}>
      <svg width={W} height={H}>
        <defs>
          <linearGradient id="atm" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stopColor="#3b5a9a" /><stop offset="0.45" stopColor="#1d2c58" /><stop offset="1" stopColor="#0a0f22" /></linearGradient>
          <radialGradient id="head"><stop offset="0" stopColor="#fff8e6" stopOpacity={0.95} /><stop offset="0.6" stopColor="#ffe2a8" stopOpacity={0.55} /><stop offset="1" stopColor="#ffd27a" stopOpacity={0} /></radialGradient>
        </defs>
        <rect width={W} height={H} fill="url(#atm)" />
        {DOTS.map((p, k) => { const y = yA(p.a); if (y < Y100 - 40 || y > Y0 + 80) return null; const x = (p.x + (t - t0) * 40 * p.v) % W; return <circle key={k} cx={x} cy={y} r={4} fill="#cfe0ff" opacity={0.55} />; })}
        {/* 高度轴 */}
        <line x1={120} y1={Y0} x2={120} y2={Y100} stroke={PAPER} strokeWidth={4} opacity={0.8} />
        {[0, 20, 40, 60, 80, 100].map((a) => <g key={a}><line x1={108} y1={yA(a)} x2={132} y2={yA(a)} stroke={PAPER} strokeWidth={4} /><text x={146} y={yA(a) + 14} fill={PAPER} fontSize={40} fontFamily={SMILEY} fontWeight={700}>{a}{a === 100 ? ' km' : ''}</text></g>)}
        <polygon points={[...trail, ...trailL].join(' ')} fill="#e9eef8" opacity={0.85} />
        <ellipse cx={X} cy={ry - headR * 0.15} rx={headR} ry={headR * 0.75} fill="url(#head)" />
        <path d={`M${X - 14},${ry + 10} L${X},${ry - 40} L${X + 14},${ry + 10} Z`} fill="#fff" />
        <circle cx={X} cy={ry + 14} r={12} fill="#ffb347" />
      </svg>
    </AbsoluteFill>
    <div style={{position: 'absolute', right: 40, top: 300, textAlign: 'right', fontFamily: SMILEY, fontWeight: 700, color: PAPER, ...STROKE, zIndex: 46}}>
      <div style={{fontSize: 60}}>高度 <span style={{color: '#ffe2a0', fontSize: 96}}>{Math.round(alt)}</span> km</div>
      <div style={{fontSize: 56, marginTop: 6}}>气压 = 地面的 <span style={{color: '#9fd0ff', fontSize: 84}}>1/{fmtN}</span></div>
    </div>
    <Chip x={X + 40} y={1290} anchor="left" text={"空气稠：\n尾焰被压细"} p={pChou} size={60} />  {/* v6c：两行，右缘 ≈ 990，留 ≥60 px */}
    <Chip x={X - 40} y={yA(55)} anchor="right" text="越往上越稀" p={pXi} size={60} color="#9fd0ff" />
    <Stamp text="不到百万分之一" p={pBw * 1.6} y={660} size={96} />
  </AbsoluteFill>;
};

// ---------- 镜头叠加 ----------
/** v6c：地名戳统一位置（北京/山西/山东/太原同一锚点，左下空天，避开尾迹与字幕） */
const PlaceStamp: React.FC<{text: string; t: number; a: number}> = ({text, t, a}) => <Stamp text={text} p={sg(t, a, a + 0.2)} x={300} y={1350} size={150} />;
/** v6f：太原镜 6.2–7.4 s 沿弧形尾迹描一遍，7.4–7.6 定住。坐标取自 c06b 素材本身（推镜前），按时间插值后套同一缓推变换，始终贴在尾迹上 */
const TY_X = [860, 780, 700, 620, 540, 460, 380, 300, 220, 140, 60];
const TY_K: [number, number[]][] = [
  [6.2, [870, 795, 726, 661, 601, 546, 496, 450, 410, 359, 313]],
  [6.5, [909, 836, 768, 704, 644, 589, 538, 492, 451, 401, 360]],
  [6.8, [953, 881, 813, 750, 692, 638, 589, 544, 504, 450, 415]],
  [7.1, [981, 912, 846, 785, 728, 675, 626, 582, 542, 488, 471]],
  [7.4, [1014, 946, 883, 823, 767, 715, 667, 623, 583, 545, 537]],
  [7.6, [1034, 969, 907, 849, 794, 743, 695, 651, 611, 590, 583]],
];
const TyTrace: React.FC<{t: number; i: number}> = ({t, i}) => {
  const A = 6.2, B = 7.4; if (t < A) return null;
  const [s1, ox, oy, s0] = PUSH.c06b_cc_ty; const ps = lerp(s0, s1, c01((t - CUTS[i]) / (SHOT_END(i) - CUTS[i])));
  let k = 0; while (k < TY_K.length - 2 && t > TY_K[k + 1][0]) k++;
  const [ta, ya] = TY_K[k], [tb, yb] = TY_K[k + 1]; const u = c01((t - ta) / (tb - ta));
  const pts = TY_X.map((x, j) => [ox + (x - ox) * ps, oy + (lerp(ya[j], yb[j], u) - oy) * ps] as const);
  const d = pts.map(([x, y], j) => `${j ? 'L' : 'M'}${x} ${y.toFixed(1)}`).join(' ');
  const len = pts.slice(1).reduce((s, [x, y], j) => s + Math.hypot(x - pts[j][0], y - pts[j][1]), 0);
  const e = easeOut(c01((t - A) / (B - A))); const op = 1;
  const hd = Math.min(pts.length - 1, e * (pts.length - 1)); const j0 = Math.floor(hd), fj = hd - j0; const j1 = Math.min(pts.length - 1, j0 + 1);
  const hx = lerp(pts[j0][0], pts[j1][0], fj), hy = lerp(pts[j0][1], pts[j1][1], fj);
  return <svg width={W} height={H} style={{position: 'absolute', inset: 0, zIndex: 44, opacity: op}}>
    <path d={d} fill="none" stroke="#000" strokeOpacity={0.55} strokeWidth={34} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={`${len * e} ${len}`} />
    <path d={d} fill="none" stroke={GOLD} strokeWidth={22} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={`${len * e} ${len}`} />
    <defs><radialGradient id="tyHead"><stop offset="0" stopColor="#fff" stopOpacity={1} /><stop offset="0.35" stopColor="#ffe9a8" stopOpacity={0.9} /><stop offset="1" stopColor="#ffb347" stopOpacity={0} /></radialGradient></defs>
    {e < 1 && <><circle cx={hx} cy={hy} r={58 + 6 * Math.sin(t * 40)} fill="url(#tyHead)" /><circle cx={hx} cy={hy} r={13} fill="#fff" /></>}
  </svg>;
};
const Overlay: React.FC<{i: number}> = ({i}) => {
  const t = useT(i); const n = NAMES[i]; const p = (k: number, d = 0.25) => sg(t, k - 0.08, k - 0.08 + d);
  switch (n) {
    case 'c03_jn_ufo': return <CrossOut text="UFO？" p={p(KT.ufo - 0.1)} q={p(KT.ufo + 0.35, 0.2)} y={520} />;
    case 'c04_am_rocket': return <Stamp text="是火箭" p={p(KT.huojian - 0.25)} y={520} />;  // v5：提前到切点后约 0.12 s
    case 'c05_cc_lift': return <><Chip x={540} y={420} text="10月23日 18:15 · 太原" p={sg(t, CUTS[i], CUTS[i] + 0.2)} size={66} /></>;  // v6：去掉与字幕重字的「长征六号改」贴纸；镜头压到 ~0.93 s，日期条切入即出
    case 'c06_am_rise': return null; // v4：去掉与 c05/字幕重复的「太原卫星发射中心」标签，画面本身是升空尾迹
    case 'c06b_cc_ty': return <><TyTrace t={t} i={i} /><Stamp text="太原·起飞" p={sg(t, CUTS[i], CUTS[i] + 0.2)} x={540} y={1350} size={120} /></>;  // v6d：发射地戳 6.8 弹入（对齐「太」6.82），文字/尺寸/位置与三个目击地戳区分
    case 'c07_cc_bj': return <PlaceStamp text="北京" t={t} a={CUTS[i]} />;  // v6c：四个地名戳统一位置（左下空天）
    case 'c08_tl_sx': return <PlaceStamp text="山西" t={t} a={CUTS[i]} />;
    case 'c09_jn_sd': return <PlaceStamp text="山东" t={t} a={CUTS[i]} />;
    case 'c10_tl_climb': return <><Chip x={540} y={420} text="↑ 越飞越高" p={sg(t, CUTS[i], CUTS[i] + 0.2)} size={80} color="#ffe2a0" /><Stamp text="高度" p={p(KT.gaodu - 0.3)} y={640} size={140} /></>;
    case 'c11_ws_lit': return <><Chip x={540} y={420} text="冲出地影" p={p(KT.chong)} size={84} color="#ffe2a0" /><Chip x={540} y={560} text="被阳光照亮" p={p(KT.zhuiguang)} size={84} color="#ffe2a0" /></>;
    case 'c12_ws_why': return <Stamp text="水母形？" p={p(KT.why)} y={480} size={130} />;
    case 'c13_am_burst': return <Chip x={540} y={420} text="稀薄空气里 猛地胀开" p={p(KT.zhang - 0.5)} size={76} color="#ffe2a0" />;
    case 'c14_ws_ice': return <><Chip x={540} y={420} text="−80 °C" p={p(KT.ling)} size={120} color="#9fd0ff" /><Chip x={540} y={600} text="水汽 → 冰晶" p={p(KT.bing)} size={84} /></>;
    case 'c15_am_jelly': return <><Chip x={540} y={330} text="冰晶散射阳光" p={p(KT.sanshe)} size={72} color="#ffe2a0" /><Leader x1={300} y1={1050} x2={330} y2={760} p={p(KT.gai, 0.35)} text="伞盖" /><Leader x1={820} y1={1100} x2={790} y2={720} p={p(KT.chu, 0.35)} text="触须" /></>;
    default: return null;
  }
};
export const ShotHost: React.FC<{i: number}> = ({i}) => {
  const n = NAMES[i]; const t = useT(i);
  const body = n === 'd1_shadow' ? <D1 /> : n === 'd2_plume' ? <D2 /> : <Real i={i} />;
  return <AbsoluteFill>{body}<Overlay i={i} />{i >= NAMES.indexOf('c16_tl_campus') && <Checklist t={t} />}<CornerLabel text={credit(n)} /></AbsoluteFill>;
};
