import React from 'react';
import {AbsoluteFill, Audio, interpolate, Easing, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import captions from '../captions.json';
import {C, Callout, Credit, F, FPS, NumberPop, SpeedLines, Vignette, e, lin, usePop, Chip} from './theme';
import {Car3DLayer, Explain3D} from './Explain3D';
import {useWarpT} from './warp';
import {useShot} from './shotctx';


const fr = (s: number) => Math.round(s * FPS);
export const V2_FRAMES = fr(63.85);

/** Absolute-time hook within a Sequence that starts at `start` */
const useAbs = (_start: number) => useWarpT();

const Clip: React.FC<{id?: string; src: string; at: number; rate?: number; start: number; zoom?: [number, number, number, number]; origin?: string; dark?: number; blur?: number}> = ({id, src: src0, at: at0, rate: rate0 = 1, start, zoom, origin = '50% 50%', dark = 0, blur = 0}) => {
  const t = useAbs(start); const sh = useShot(id); const src = sh?.src ?? src0, at = sh?.in ?? at0, rate = sh?.rate ?? rate0;
  const s = zoom ? interpolate(t, [zoom[2], zoom[3]], [zoom[0], zoom[1]], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.quad)}) : 1;
  return <AbsoluteFill style={{overflow: 'hidden', background: '#000'}}>
    <OffthreadVideo muted src={staticFile(src)} startFrom={Math.round(at * 30)} playbackRate={rate}
      style={{width: 1920, height: 1080, objectFit: 'cover', transform: `scale(${s})`, transformOrigin: origin, filter: `brightness(${1 - dark}) blur(${blur}px)`}} />
  </AbsoluteFill>;
};
const Seq: React.FC<{a: number; b: number; children: React.ReactNode}> = ({a, b, children}) => <Sequence from={fr(a)} durationInFrames={fr(b) - fr(a)}>{children}</Sequence>;

const Tag: React.FC<{text: string; o: number; x: number; y: number; color?: string; size?: number}> = ({text, o, x, y, color = C.cyan, size = 32}) => o <= 0 ? null :
  <div style={{position: 'absolute', left: x, top: y, opacity: Math.min(1, o), transform: `translateY(${(1 - Math.min(1, o)) * 14}px)`, padding: '8px 18px', borderRadius: 8, background: C.glass, borderLeft: `4px solid ${color}`, fontFamily: F, fontWeight: 800, fontSize: size, color: C.white, zIndex: 40, whiteSpace: 'nowrap'}}>{text}</div>;

/* ---------- S01 + S02 ---------- */
export const Hook: React.FC = () => { const t = useAbs(0);
  const dark = 0.35 * e(t, 3.05, 3.4);
  const hl = (at: number, color: string, txt: string, y: number) => { const p = usePop(t, at); return p <= 0 ? null : <div style={{position: 'absolute', left: 140, top: y, opacity: Math.min(1, p), transform: `translateX(${(1 - Math.min(1, p)) * -40}px)`, zIndex: 41}}>
    <div style={{fontFamily: F, fontWeight: 900, fontSize: 124, color: C.white, letterSpacing: 4, lineHeight: 1.05, textShadow: '0 8px 30px rgba(0,0,0,0.6)'}}>{txt}</div>
    <div style={{height: 8, width: `${Math.min(1, p) * 100}%`, maxWidth: 520, borderRadius: 4, background: color, boxShadow: `0 0 18px ${color}`, marginTop: 8}} /></div>; };
  return <AbsoluteFill>
    <Clip src="clip-fly.mp4" at={41.3} start={0} zoom={[1.0, 1.14, 0, 3.2]} origin="55% 45%" />
    <AbsoluteFill style={{background: '#000', opacity: dark}} />
    <SpeedLines t={t} o={e(t, 0.9, 1.2) * (1 - e(t, 2.3, 2.7))} />
    <Vignette />
    <Tag text="飞越 Tesla Semi 卡车" o={usePop(t, 1.9) * (1 - e(t, 3.0, 3.2))} x={140} y={200} color={C.red} />
    {t > 3.05 && <div style={{position: 'absolute', left: 144, top: 300, zIndex: 41, opacity: e(t, 3.1, 3.3), fontFamily: F, fontSize: 26, letterSpacing: 6, color: C.dim}}>● 现场实拍  LIVE</div>}
    {hl(3.27, C.red, '不是特效', 360)}
    {hl(4.61, C.cyan, '也不是 AI', 530)}
    <Credit />
  </AbsoluteFill>; };

/* ---------- S03 danmaku ---------- */
const DM = [
  {t: '怎么飞的？？', lane: 0, s: 6.2, v: 330}, {t: '假的吧 这是CG', lane: 1, s: 6.3, v: 260}, {t: '推进器原理求科普', lane: 2, s: 6.5, v: 300},
  {t: '是不是AI做的', lane: 3, s: 6.25, v: 280}, {t: '风扇吸地？', lane: 4, s: 6.7, v: 350}, {t: '能上路吗', lane: 5, s: 6.9, v: 240},
  {t: '物理学不存在了', lane: 0, s: 7.6, v: 300}, {t: '这车怎么挂在墙上的', lane: 2, s: 7.9, v: 280}, {t: '前方高能', lane: 4, s: 8.1, v: 320},
  {t: '马斯克又整活', lane: 1, s: 8.4, v: 300}, {t: '喷的是什么气', lane: 5, s: 8.6, v: 270}, {t: '？？？', lane: 3, s: 9.0, v: 360},
];
const HL = {t: '它到底怎么飞起来的？', lane: 3, s: 5.52, v: 420};
export const Danmaku: React.FC = () => { const t = useAbs(6.35);
  const lanes = (l: number) => 130 + l * 74;
  const x = (d: {s: number; v: number}) => 1920 - (t - d.s) * d.v;
  const hx = x(HL); const hp = usePop(t, 8.42);
  return <AbsoluteFill>
    <Clip id="comments-bg" src="clip-ramp.mp4" at={72.5} start={6.35} dark={0.45} blur={3} zoom={[1.05, 1.12, 6.35, 10.2]} />
    <Vignette />
    <Chip text="评论区问得最多" accent={C.amber} o={e(t, 6.4, 6.7)} />
    {DM.map((d, i) => { const xx = x(d); return t < d.s ? null : <div key={i} style={{position: 'absolute', left: xx, top: lanes(d.lane), fontFamily: F, fontWeight: 700, fontSize: 38, color: i % 5 === 2 ? '#ffd25a' : i % 5 === 4 ? '#8fd8ff' : '#fff', whiteSpace: 'nowrap', textShadow: '1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000', opacity: 0.92 - 0.35 * hp, zIndex: 30}}>{d.t}</div>; })}
    {t >= HL.s && <div style={{position: 'absolute', left: hx, top: lanes(HL.lane) - 8, zIndex: 31, fontFamily: F, fontWeight: 900, fontSize: 38 + 10 * Math.min(1, hp), color: '#ffd25a', whiteSpace: 'nowrap', padding: '4px 14px', borderRadius: 8,
      border: `2px solid rgba(255,210,90,${Math.min(1, hp)})`, background: `rgba(10,14,20,${0.6 * Math.min(1, hp)})`, textShadow: '1px 1px 0 #000,-1px -1px 0 #000'}}>{HL.t}</div>}
    <Credit />
  </AbsoluteFill>; };

/* ---------- S04 two systems ---------- */
export const Two: React.FC = () => { const t = useAbs(10.22);
  const card = (at: number, n: string, a: string, b: string, color: string, x: number) => { const p = usePop(t, at); return p <= 0 ? null :
    <div style={{position: 'absolute', left: x, top: 330, width: 560, opacity: Math.min(1, p), transform: `translateY(${(1 - Math.min(1, p)) * 30}px)`, padding: '26px 32px', borderRadius: 16, background: C.glass, borderTop: `5px solid ${color}`, zIndex: 40}}>
      <div style={{fontFamily: F, fontWeight: 900, fontSize: 30, color, letterSpacing: 3}}>{n}</div>
      <div style={{fontFamily: F, fontWeight: 900, fontSize: 60, color: C.white, marginTop: 6}}>{a}</div>
      <div style={{fontFamily: F, fontSize: 30, color: C.dim, marginTop: 4}}>{b}</div></div>; };
  return <AbsoluteFill>
    <Clip id="two-bg" src="clip-ramp.mp4" at={40.0} start={10.22} zoom={[1.0, 1.1, 10.22, 13.1]} dark={0.15 + 0.3 * e(t, 11.2, 11.5)} />
    <Vignette />
    {card(11.42, '系统 ①', '车底风扇', '负责 吸', C.cyan, 330)}
    {card(11.66, '系统 ②', '冷气推进器', '负责 飞', C.amber, 1030)}
    <Credit />
  </AbsoluteFill>; };

/* ---------- TA live: climb slow-mo + top-down ---------- */
export const ClimbLive: React.FC = () => { const t = useAbs(13.1);
  const ar = usePop(t, 15.39);
  return <AbsoluteFill>
    {t < 16.1 ? <Clip src="clip-ramp.mp4" at={68.0} rate={0.55} start={13.1} zoom={[1.0, 1.18, 13.1, 16.1]} origin="50% 40%" />
      : <AbsoluteFill><OffthreadVideo muted src={staticFile('hliveA.mp4')} style={{width: 1920, height: 1080}} /></AbsoluteFill>}
    <Vignette />
    <Tag text="0.5× 慢放" o={e(t, 13.2, 13.5) * (1 - e(t, 15.9, 16.1))} x={1600} y={34} color={C.white} size={26} />
    <Callout x={960} y={560} label="先看这里" color={C.amber} p={usePop(t, 13.2)} out={1 - e(t, 14.2, 14.5)} dx={240} dy={-140} r={70} />
    {ar > 0 && t < 16.1 && <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, zIndex: 39}}>
      <line x1={1180} y1={760} x2={1180} y2={760 - 420 * Math.min(1, ar)} stroke={C.cyan} strokeWidth={6} strokeLinecap="round" />
      <polygon points={`1180,${740 - 420 * Math.min(1, ar)} 1162,${770 - 420 * Math.min(1, ar)} 1198,${770 - 420 * Math.min(1, ar)}`} fill={C.cyan} /></svg>}
    <Tag text="垂直墙面 90°" o={ar * (1 - e(t, 15.95, 16.1))} x={1220} y={420} color={C.cyan} />
    <Tag text="车头朝天" o={usePop(t, 14.45) * (1 - e(t, 15.3, 15.5))} x={1220} y={420} color={C.amber} />
    <Credit />
  </AbsoluteFill>; };

export const FlyLive: React.FC = () => { const t = useAbs(27.9);
  return <AbsoluteFill>
    <Clip src="clip-fly.mp4" at={40.68} start={27.9} zoom={[1.0, 1.16, 27.9, 30.4]} origin="60% 40%" />
    <SpeedLines t={t} o={e(t, 29.0, 29.4) * (1 - e(t, 30.1, 30.4))} />
    <Vignette />
    <Tag text="慢镜头之前 · 原速回放" o={e(t, 28.0, 28.3) * (1 - e(t, 30.0, 30.3))} x={1500} y={34} color={C.white} size={24} />
    <Credit />
  </AbsoluteFill>; };

/* ---------- S08 summary ---------- */
export const Summary: React.FC = () => { const t = useAbs(46.9);
  const panel = (v: 'A' | 'B', x: number, color: string, label: string, at: number, st: number) => { const p = usePop(t, at); const show = e(t, 46.95, 47.4);
    return <div style={{position: 'absolute', left: x, top: 210, width: 860, height: 484, opacity: show, transform: `translateY(${(1 - show) * 24}px)`, borderRadius: 18, overflow: 'hidden', background: '#070a10', border: `2px solid ${p > 0 ? color : 'rgba(255,255,255,0.15)'}`, boxShadow: p > 0 ? `0 0 40px ${color}44` : undefined}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transform: 'scale(0.448)', transformOrigin: 'top left'}}><Car3DLayer v={v} t={st} /></div>
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 26, textAlign: 'center', opacity: Math.min(1, p), transform: `scale(${0.85 + 0.15 * Math.min(1, p)})`, fontFamily: F, fontWeight: 900, fontSize: 64, color, textShadow: '0 4px 16px #000'}}>{label}</div>
    </div>; };
  return <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, #0d1522 0%, #04060a 70%)'}}>
    <Chip text="一句话记住" accent={C.white} o={e(t, 47.0, 47.4)} sub="示意模型 非官方" />
    {panel('A', 80, C.cyan, '风扇负责吸', 48.44, 27.0)}
    {panel('B', 980, C.amber, '喷气负责飞', 49.40, 37.4)}
    <Credit text="示意动画" />
  </AbsoluteFill>; };

/* ---------- S09 can you buy ---------- */
const Tracker: React.FC<{t: number}> = ({t}) => { const items = [['2028 量产', 53.3, C.cyan], ['会飞版仅限封闭场地', 56.8, C.amber], ['订金最高 25万美元', 59.5, C.red]] as const;
  return <div style={{position: 'absolute', top: 34, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 12, zIndex: 46, opacity: e(t, 52.9, 53.2)}}>
    {items.map(([l, at, col]) => { const on = e(t, at, at + 0.25); return <div key={l} style={{padding: '8px 18px', borderRadius: 8, background: C.glass, border: `1px solid ${on > 0.5 ? col : 'rgba(255,255,255,0.12)'}`, fontFamily: F, fontWeight: 800, fontSize: 26, color: on > 0.5 ? C.white : 'rgba(255,255,255,0.35)', transform: `scale(${1 + 0.06 * (on - e(t, at + 0.25, at + 0.5))})`}}>
      <span style={{display: 'inline-block', width: 10, height: 10, borderRadius: 5, background: on > 0.5 ? col : '#555', marginRight: 10}} />{l}</div>; })}
  </div>; };
export const Buy: React.FC = () => { const t = useAbs(51.22);
  const S = 0.82, ox = 190, oy = 130; const hb = usePop(t, 59.5);
  const engZoom = 1 + 0.07 * e(t, 58.1, 60.8);
  return <AbsoluteFill style={{background: '#05070b'}}>
    {t < 52.95 && <><Clip id="buy-promo" src="promo-garage.mp4" at={0} start={51.22} zoom={[1.0, 1.1, 51.22, 52.95]} /><Credit /></>}
    {t >= 52.95 && t < 55.15 && <><Clip id="buy-musk" src="musk2028.mp4" at={0} start={52.95} zoom={[1.0, 1.08, 52.95, 55.15]} origin="50% 35%" />
      <Vignette /><NumberPop x={140} y={560} big="2028" label="年 才量产" color={C.cyan} p={usePop(t, 53.1)} />
      <div style={{position: 'absolute', left: 144, top: 500, opacity: e(t, 53.4, 53.8), fontFamily: F, fontStyle: 'italic', fontSize: 28, color: C.dim, zIndex: 41}}>“We enter production in 2028.” — Elon Musk</div><Credit text="画面来源：Tesla 发布会" /></>}
    {t >= 55.15 && t < 58.1 && <><Clip id="buy-closed" src="clip-ramp.mp4" at={82} start={55.15} zoom={[1.0, 1.1, 55.15, 58.1]} dark={0.2} /><Vignette />
      {(() => { const p = usePop(t, 56.8); return p <= 0 ? null : <div style={{position: 'absolute', left: 140, top: 520, opacity: Math.min(1, p), transform: `translateX(${(1 - Math.min(1, p)) * -30}px)`, zIndex: 41, padding: '22px 30px', borderRadius: 14, background: C.glass, borderLeft: `6px solid ${C.amber}`}}>
        <div style={{height: 14, width: 260, marginBottom: 14, background: `repeating-linear-gradient(45deg, ${C.amber} 0 18px, #111 18px 36px)`, borderRadius: 3}} />
        <div style={{fontFamily: F, fontWeight: 900, fontSize: 58, color: C.white}}>会飞版 仅限封闭场地</div>
        <div style={{fontFamily: F, fontSize: 28, color: C.dim, marginTop: 6}}>目前只在封闭场地演示，不能上公路</div></div>; })()}
      <Credit /></>}
    {t >= 58.1 && <>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 40% 50%, #121a28 0%, #04060a 75%)'}} />
      <div style={{position: 'absolute', left: ox, top: oy, width: 840 * S, height: 790 * S, transform: `scale(${engZoom}) translateY(${(1 - e(t, 58.1, 58.5)) * 30}px)`, transformOrigin: '30% 25%', opacity: e(t, 58.1, 58.45), borderRadius: 14, overflow: 'hidden', boxShadow: '0 30px 80px rgba(0,0,0,0.6)'}}>
        <Img src={staticFile('engadget.png')} style={{width: '100%', height: '100%'}} />
        {hb > 0 && <div style={{position: 'absolute', left: 146 * S, top: 158 * S, width: (240 * S) * Math.min(1, hb), height: 58 * S, border: `4px solid ${C.red}`, borderRadius: 8, background: 'rgba(255,59,79,0.12)', boxShadow: `0 0 24px ${C.red}`}} />}
      </div>
      <Tag text="售价  未公布" o={usePop(t, 58.3)} x={1180} y={300} color={C.white} size={44} />
      <NumberPop x={1180} y={420} big="25万美元" label="订金最高（Thrust 版）" color={C.red} p={usePop(t, 59.55)} />
      <Credit text="画面来源：Engadget 报道截图" />
    </>}
    <Tracker t={t} />
  </AbsoluteFill>; };

/* ---------- S10 ending ---------- */
export const End: React.FC = () => { const t = useAbs(61.27); const p = usePop(t, 62.1);
  return <AbsoluteFill>
    <Clip id="end" src="clip-ramp-official.mp4" at={24.3} start={61.27} zoom={[1.0, 1.12, 61.27, 63.85]} dark={0.25 * e(t, 61.3, 61.8)} />
    <Vignette />
    <div style={{position: 'absolute', left: 140, top: 380, zIndex: 41}}>
      <div style={{fontFamily: F, fontWeight: 700, fontSize: 48, color: C.dim, opacity: e(t, 61.3, 61.6)}}>如果真能买</div>
      {p > 0 && <><div style={{fontFamily: F, fontWeight: 900, fontSize: 140, color: C.white, opacity: Math.min(1, p), transform: `translateX(${(1 - Math.min(1, p)) * -40}px)`, textShadow: '0 8px 30px rgba(0,0,0,0.6)'}}>你敢坐吗？</div>
        <div style={{height: 8, width: 560 * Math.min(1, p), background: C.red, borderRadius: 4, boxShadow: `0 0 18px ${C.red}`}} /></>}
    </div>
    <Credit />
  </AbsoluteFill>; };


export {Clip, Tag};
