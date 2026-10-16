import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, staticFile} from 'remotion';
import AL from './align.json';
import {C, Credit, F, FPS, NumberPop, SpeedLines, Vignette, e, lin, usePop, Chip} from './theme';
import {Explain3D} from './Explain3D';
import {Seq, useT3} from './warp';
import {Danmaku, Two, ClimbLive, Summary, Buy, End, Clip, Tag} from './v2shots';

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
  inv: s(10).start - 0.1, dao: W(10, '倒'), bushi: W(10, '不是'),
  q: s(11).start - 0.1, spx: W(12, 'SpaceX'),
  B: W(13, '座'), gao: W(13, '高'), fa: W(13, '阀'), pen2: W(13, '喷'), qwh: W(14, '气往后'), qian: W(14, '前'), gen: W(14, '跟'), qq: W(14, '气球'),
  dh: W(15, '点火'), sy: W(15, '烧油'), ys: W(15, '压缩'), cs: W(16, '车身'), pk: W(16, '喷口'), zt: W(16, '姿态'), hj: W(16, '火箭'),
  sum: s(17).start - 0.1, fs: W(17, '风扇'), pq: W(17, '喷气'),
  buy: s(18).start - 0.1, y28: W(19, ['二零二八', '2028']), hf: W(19, '会飞'), fb: W(19, '封闭'), price: s(20).start - 0.1, w25: W(20, ['二十五', '25']),
  end: s(21).start - 0.1, gan: W(21, '敢'),
};

/* ---------- hook ---------- */
const Hook3: React.FC = () => { const t = useT3();
  const hl = (at: number, color: string, txt: string, y: number, size = 124) => { const p = usePop(t, at); return p <= 0 ? null : <div style={{position: 'absolute', left: 140, top: y, opacity: Math.min(1, p), transform: `translateX(${(1 - Math.min(1, p)) * -40}px)`, zIndex: 41}}>
    <div style={{fontFamily: F, fontWeight: 900, fontSize: size, color: C.white, letterSpacing: 4, lineHeight: 1.05, textShadow: '0 8px 30px rgba(0,0,0,0.6)'}}>{txt}</div>
    <div style={{height: 8, width: `${Math.min(1, p) * 100}%`, maxWidth: 520, borderRadius: 4, background: color, boxShadow: `0 0 18px ${color}`, marginTop: 8}} /></div>; };
  if (t < T.cut) { const pa = usePop(t, W(0, '加速'));
    return <AbsoluteFill><Clip src="clip-launch.mp4" at={7.9} start={0} zoom={[1.0, 1.12, 0, T.cut]} /><Vignette />
      <Tag text="Tesla 新 Roadster 发布会" o={e(t, 0.15, 0.45)} x={140} y={200} color={C.white} />
      {pa > 0 && <div style={{position: 'absolute', left: 140, top: 300, zIndex: 41, opacity: Math.min(1, pa), fontFamily: F, fontWeight: 900, fontSize: 96, color: 'rgba(255,255,255,0.75)'}}>
        <span style={{position: 'relative'}}>加速<span style={{position: 'absolute', left: -8, right: -8, top: '52%', height: 9, background: C.red, transform: `scaleX(${e(t, W(0, '加速') + 0.15, W(0, '加速') + 0.45)})`, transformOrigin: 'left'}} /></span>
        <span style={{fontSize: 40, marginLeft: 20, color: C.dim}}>不是重点</span></div>}
      <Credit /></AbsoluteFill>; }
  const at = 42.5 - (T.fly - T.cut);
  return <AbsoluteFill><Clip src="clip-fly.mp4" at={at} start={T.cut} zoom={[1.0, 1.14, T.cut, s(1).end]} origin="55% 45%" />
    <SpeedLines t={t} o={e(t, T.fly - 0.3, T.fly) * (1 - e(t, T.fly + 1.0, T.fly + 1.4))} />
    <Vignette />
    {hl(T.fly, C.red, '它飞起来了', 300)}
    <Tag text="飞越 Tesla Semi 卡车" o={usePop(t, T.semi) * 1} x={140} y={200} color={C.amber} />
    <div style={{position: 'absolute', left: 144, top: 160, zIndex: 41, opacity: e(t, T.cut, T.cut + 0.3), fontFamily: F, fontSize: 24, letterSpacing: 6, color: C.dim}}>● 现场实拍  LIVE</div>
    <Credit /></AbsoluteFill>; };

/* ---------- comments ---------- */
const COMMENTS: [number, string, string, string][] = [
  [0, '我以为是AI恶搞，专门来搜了一下，没想到是真的[黑脸]', '@JiangJiang', '抖音'],
  [1, '吹的牛太多了不被信任是正常的，跑路多少次了', '网友评论', 'B站 BV1zcJS6sEXT'],
  [2, '上什么天？吹上天？', '网友评论', 'B站 BV1j9JQ6oEeE'],
];
const Comments: React.FC = () => { const t = useT3(); const ats = [T.c1, T.c2, T.c3];
  return <>{COMMENTS.map(([k, txt, who, src]) => { const p = usePop(t, ats[k] - 0.05); if (p <= 0) return null; const m = Math.min(1, p);
    return <div key={k} style={{position: 'absolute', left: 560 + k * 40, top: 300 + k * 150, width: 820, opacity: m, transform: `translateY(${(1 - m) * 30}px) rotate(${(k - 1) * 0.8}deg) scale(${0.92 + 0.08 * m})`, zIndex: 45,
      padding: '20px 26px', borderRadius: 16, background: 'rgba(250,250,252,0.96)', boxShadow: '0 20px 50px rgba(0,0,0,0.55)', display: 'flex', gap: 18}}>
      <div style={{width: 58, height: 58, borderRadius: 29, flex: 'none', background: ['#ffb347', '#4fd1ff', '#ff7aa8'][k], fontFamily: F, fontWeight: 900, fontSize: 28, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{who[1] ?? '网'}</div>
      <div><div style={{fontFamily: F, fontSize: 22, color: '#8a8f99'}}>{who} · 来自{src}</div>
        <div style={{fontFamily: F, fontWeight: 700, fontSize: 34, color: '#16181d', marginTop: 4, lineHeight: 1.3}}>{txt}</div></div></div>; })}
    <div style={{position: 'absolute', right: 40, bottom: 160, fontFamily: F, fontSize: 20, color: 'rgba(255,255,255,0.55)', zIndex: 46}}>评论来源：抖音 / B站 公开评论</div></>; };

/* ---------- channel card ---------- */
const Me: React.FC = () => { const t = useT3(); const p = usePop(t, T.me + 0.05); const m = Math.min(1, p);
  return <AbsoluteFill><Clip src="clip-ramp-official.mp4" at={10} start={T.me} dark={0.55} blur={8} />
    <div style={{position: 'absolute', left: 0, right: 0, top: 360, display: 'flex', justifyContent: 'center', zIndex: 41}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 34, padding: '30px 48px', borderRadius: 24, background: C.glass, border: '1px solid rgba(255,255,255,0.14)', opacity: m, transform: `scale(${0.85 + 0.15 * m})`}}>
        <div style={{width: 130, height: 130, borderRadius: 65, background: `conic-gradient(${C.cyan}, ${C.amber}, ${C.red}, ${C.cyan})`, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `rotate(${(t - T.me) * 40}deg)`}}>
          <div style={{width: 112, height: 112, borderRadius: 56, background: '#0b0f16', display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `rotate(${-(t - T.me) * 40}deg)`, fontFamily: F, fontWeight: 900, fontSize: 50, color: C.white}}>丞</div></div>
        <div><div style={{fontFamily: F, fontWeight: 900, fontSize: 84, color: C.white, letterSpacing: 6}}>秘书丞</div>
          <div style={{fontFamily: F, fontSize: 30, color: C.dim, marginTop: 4, opacity: e(t, T.me + 0.3, T.me + 0.6)}}>科技热点 · 一分钟讲明白</div></div></div></div>
  </AbsoluteFill>; };

/* ---------- conclusion ---------- */
const Concl: React.FC = () => { const t = useT3(); const p1 = usePop(t, T.real), p2 = usePop(t, T.but);
  return <AbsoluteFill><Clip src="clip-fly.mp4" at={42.0} rate={0.5} start={T.con} dark={0.4} zoom={[1.05, 1.15, T.con, T.src]} /><Vignette />
    <div style={{position: 'absolute', left: 140, top: 330, zIndex: 41}}>
      {p1 > 0 && <div style={{fontFamily: F, fontWeight: 900, fontSize: 116, color: C.white, opacity: Math.min(1, p1), transform: `translateX(${(1 - Math.min(1, p1)) * -40}px)`}}>真不是<span style={{color: C.cyan}}>特效</span></div>}
      {p2 > 0 && <div style={{fontFamily: F, fontWeight: 900, fontSize: 76, color: 'rgba(255,255,255,0.9)', marginTop: 24, opacity: Math.min(1, p2), transform: `translateX(${(1 - Math.min(1, p2)) * -40}px)`}}>但也不是你以为的<span style={{color: C.amber}}>「飞」</span></div>}
    </div><Credit /></AbsoluteFill>; };

/* ---------- sources ---------- */
const Sources: React.FC = () => { const t = useT3(); const shot = (img: string, at: number, x: number, y: number, w: number, rot: number) => { const p = usePop(t, at); const m = Math.min(1, p); return p <= 0 ? null :
  <Img src={staticFile(img)} style={{position: 'absolute', left: x, top: y, width: w, opacity: m, transform: `translateY(${(1 - m) * 40}px) rotate(${rot}deg) scale(${1 + 0.03 * e(t, at, T.two)})`, borderRadius: 12, boxShadow: '0 30px 80px rgba(0,0,0,0.6)'}} />; };
  return <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, #121a28 0%, #04060a 75%)'}}>
    <Chip text="我们翻了这些" accent={C.amber} o={e(t, T.src, T.src + 0.3)} />
    {shot('techcrunch.png', W(5, '原片') - 0.1, 160, 220, 1000, -2)}
    {shot('engadget.png', W(5, '拆解'), 1060, 240, 640, 2.5)}
    <Credit text="画面来源：TechCrunch / Engadget 报道截图" /></AbsoluteFill>; };

/* ---------- inverted live ---------- */
const Inv: React.FC = () => { const t = useT3();
  return <AbsoluteFill><Clip src="clip-ramp.mp4" at={18.6} rate={0.6} start={T.inv} zoom={[1.0, 1.12, T.inv, T.q]} origin="50% 35%" /><Vignette />
    <Tag text="0.6× 慢放" o={e(t, T.inv, T.inv + 0.3)} x={1600} y={34} color={C.white} size={26} />
    <Tag text="吸力最大 ≈ 车重 2 倍" o={e(t, T.inv, T.inv + 0.2) * (1 - e(t, T.dao - 0.3, T.dao))} x={140} y={240} color={C.amber} size={44} />
    <Tag text="在顶上 倒过来一下" o={usePop(t, T.dao)} x={140} y={240} color={C.cyan} size={44} />
    <Tag text="✕  不是倒挂一路开" o={usePop(t, T.bushi)} x={140} y={340} color={C.red} size={44} />
    <Credit /></AbsoluteFill>; };

const Fly3: React.FC = () => { const t = useT3(); const dur = T.B - T.q; const rate = Math.min(1, 4.2 / dur);
  return <AbsoluteFill><Clip src="clip-fly.mp4" at={43.15 - dur * rate} rate={rate} start={T.q} zoom={[1.0, 1.16, T.q, T.B]} origin="60% 40%" />
    <Vignette />
    {(() => { const p = usePop(t, s(11).start); return p <= 0 ? null : <div style={{position: 'absolute', left: 140, top: 300, zIndex: 41, opacity: Math.min(1, p) * (1 - e(t, T.spx - 0.3, T.spx)), fontFamily: F, fontWeight: 900, fontSize: 100, color: C.white}}>那它是怎么<span style={{color: C.amber}}>飞</span>的？</div>; })()}
    {(() => { const p = usePop(t, T.spx); return p <= 0 ? null : <div style={{position: 'absolute', left: 140, top: 320, zIndex: 41, opacity: Math.min(1, p), padding: '20px 30px', borderRadius: 14, background: C.glass, borderLeft: `6px solid ${C.amber}`}}>
      <div style={{fontFamily: F, fontSize: 30, color: C.dim}}>技术来自</div><div style={{fontFamily: F, fontWeight: 900, fontSize: 90, color: C.white, letterSpacing: 4}}>SpaceX</div><div style={{fontFamily: F, fontSize: 30, color: C.dim}}>冷气推进器（Cold-gas thrusters）</div></div>; })()}
    <Credit /></AbsoluteFill>; };

const B15: React.FC = () => { const t = useT3();
  return <>{([[T.dh, '不点火'], [T.sy, '不烧油'], [T.ys, '喷的是 压缩空气']] as const).map(([at, l], k) =>
    <Tag key={k} text={(k < 2 ? '✕  ' : '✓  ') + l} o={usePop(t, at) * (1 - e(t, T.cs - 0.1, T.cs + 0.2))} x={1330} y={260 + k * 92} color={k < 2 ? C.red : C.cyan} size={40} />)}</>; };

const RampCut: React.FC = () => { const t = useT3();
  return <AbsoluteFill style={{zIndex: 50}}><Clip src="clip-ramp.mp4" at={66.0} start={T.musk} zoom={[1.0, 1.1, T.musk, T.zui]} /><Vignette />
    <Tag text="实拍：吸住路面 贴墙爬坡" o={e(t, T.musk, T.musk + 0.25)} x={140} y={200} color={C.cyan} /><Credit /></AbsoluteFill>; };

/* ---------- subtitles ---------- */
const CUES = (() => { const out: {a: number; b: number; text: string}[] = [];
  SS.forEach((S, i) => { if (i === 2 || i === 21) return; let k = 0;
    for (const ch of S.text.split(/[，。？！：、,.?!:]/).filter(Boolean)) {
      const target = ch.replace(/2028/g, '二零二八').replace(/\s/g, ''); let acc = '', n = 0;
      while (k + n < S.words.length && acc.length < target.length) { acc += S.words[k + n].text.replace(/\s/g, ''); n++; }
      const seg = S.words.slice(k, k + n); k += n; if (!seg.length) continue;
      const push = (ws: Wd[], txt: string) => out.push({a: ws[0].start, b: ws[ws.length - 1].end, text: txt});
      if (ch.length > 17) { const h = Math.ceil(seg.length / 2), c = Math.ceil(ch.length / 2); push(seg.slice(0, h), ch.slice(0, c)); push(seg.slice(h), ch.slice(c)); } else push(seg, ch); } });
  for (let j = 0; j < out.length - 1; j++) if (out[j + 1].a - out[j].b < 0.4) out[j].b = out[j + 1].a;
  return out; })();
const Subs: React.FC = () => { const t = useT3() ;
  const c = CUES.find((q) => t >= q.a - 0.05 && t < q.b + 0.05); if (!c) return null;
  const o = lin(t, [c.a - 0.05, c.a + 0.03, c.b, c.b + 0.05], [0, 1, 1, 0]);
  return <div style={{position: 'absolute', left: 0, right: 0, bottom: 70, textAlign: 'center', zIndex: 60, opacity: o}}>
    <span style={{fontFamily: F, fontWeight: 900, fontSize: 54, color: '#fff', letterSpacing: 2, whiteSpace: 'nowrap', textShadow: '0 0 2px #000, 0 3px 0 #000, 0 0 18px rgba(0,0,0,0.85)', WebkitTextStroke: '1.5px rgba(0,0,0,0.6)'}}>{c.text}</span></div>; };

/* ---------- sfx ---------- */
const sf = (f: string, at: number, v: number, d = 6): [string, number, number, number] => [f, at, v, d];
export const SFX3 = () => [
  sf('boom.wav', 0, 0.4), sf('whoosh.wav', T.cut - 0.15, 0.28), sf('boom.wav', T.fly, 0.5),
  sf('whoosh.wav', T.cm - 0.1, 0.25), sf('click.wav', T.c1, 0.4), sf('click.wav', T.c2, 0.4), sf('click.wav', T.c3, 0.4),
  ['v3/sting.wav', T.me, 0.45, 2] as [string, number, number, number],
  sf('whoosh.wav', T.src - 0.1, 0.22),
  sf('shutter.wav', T.A, 0.45), sf('fanhum.wav', T.feng, 0.2, T.musk - T.feng), sf('ding.wav', T.bei, 0.22),
  sf('whoosh.wav', T.q - 0.1, 0.28), sf('shutter.wav', T.B, 0.45), sf('click.wav', T.fa, 0.45), sf('jet.wav', T.pen2 - 0.1, 0.28, 4.2),
  sf('hiss.wav', T.qq, 0.2, 2.5), sf('puff.wav', T.pk, 0.28), sf('puff.wav', T.pk + 0.45, 0.25), sf('puff.wav', T.pk + 0.9, 0.25),
  sf('whoosh.wav', T.sum - 0.1, 0.24), sf('ding.wav', T.y28, 0.24), sf('ding.wav', T.w25, 0.26),
];
const SFXL: React.FC = () => <>{SFX3().map(([f, a, v, d], i) => <Sequence key={i} from={Math.max(0, Math.round(a * FPS))} durationInFrames={Math.max(1, Math.round(d * FPS))}>
  <Audio src={staticFile(f.startsWith('v3/') ? f : 'sfx/' + f)} volume={v} /></Sequence>)}</>;

export const RoadsterShortV3: React.FC<{withVoice?: boolean}> = ({withVoice = true}) => <AbsoluteFill style={{background: '#000'}}>
  {withVoice && <Audio src={staticFile('v3/voice-v3.wav')} />}
  <SFXL />
  <Seq a={0} b={T.cut}><Hook3 /></Seq>
  <Seq a={T.cut} b={T.cm}><Hook3 /></Seq>
  <Seq a={T.cm} b={T.me} anchors={[[T.cm, 6.35], [s(2).end, 9.4]]}><Danmaku /><Comments /></Seq>
  <Seq a={T.me} b={T.con}><Me /></Seq>
  <Seq a={T.con} b={T.src}><Concl /></Seq>
  <Seq a={T.src} b={T.two}><Sources /></Seq>
  <Seq a={T.two} b={T.climb} anchors={[[T.two, 10.22], [T.xi, 11.42], [T.pen, 11.66], [T.climb, 13.1]]}><Two /></Seq>
  <Seq a={T.climb} b={T.A} anchors={[[T.climb, 13.1], [T.A, 17.1]]}><ClimbLive /></Seq>
  <Seq a={T.A} b={T.inv} anchors={[[T.A, 17.1], [T.feng, 18.15], [T.chou, 19.1], [T.qiya, 21.17], [T.wai, 22.66], [T.si, 23.78], [T.zui, 26.29], [T.bei, 27.41], [T.inv, 27.9]]}><Explain3D v="A" start={17.1} /></Seq>
  <Seq a={T.musk} b={T.zui - 0.05}><RampCut /></Seq>
  <Seq a={T.inv} b={T.q}><Inv /></Seq>
  <Seq a={T.q} b={T.B}><Fly3 /></Seq>
  <Seq a={T.B} b={T.sum} anchors={[[T.B, 30.4], [T.gao, 31.26], [T.fa, 32.58], [T.pen2, 34.5], [T.qwh, 35.56], [T.qian, 36.84], [T.gen, 38.11], [T.qq, 39.15], [s(15).start, 40.3], [s(15).end, 41.0], [T.cs, 41.12], [T.pk, 42.0], [T.zt, 43.12], [T.hj, 44.8], [T.sum, 46.9]]}><Explain3D v="B" start={30.4} /><B15 /></Seq>
  <Seq a={T.sum} b={T.buy} anchors={[[T.sum, 46.9], [T.fs, 48.44], [T.pq, 49.40], [T.buy, 51.22]]}><Summary /></Seq>
  <Seq a={T.buy} b={T.y28 - 0.14} anchors={[[T.buy, 51.22], [T.y28 - 0.14, 52.95]]}><Buy /></Seq>
  <Seq a={T.y28 - 0.14} b={T.hf} anchors={[[T.y28 - 0.14, 52.95], [T.y28, 53.09], [T.hf, 55.15]]}><Buy /></Seq>
  <Seq a={T.hf} b={T.price} anchors={[[T.hf, 55.15], [T.fb, 56.81], [T.price, 58.1]]}><Buy /></Seq>
  <Seq a={T.price} b={T.end} anchors={[[T.price, 58.1], [T.w25, 59.56], [T.end, 61.27]]}><Buy /></Seq>
  <Seq a={T.end} b={V3_END} anchors={[[T.end, 61.27], [T.gan, 62.23]]}><End /></Seq>
  <Subs />
</AbsoluteFill>;
