import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import data from './data/v3d.json';
import {BrandBadge} from '../Brand';
import {Overlay, O, WORLD_KINDS} from '../v3/Overlays';
import {useV3Font} from '../v3/Fonts';
import {BGM_DUCK_DB, BGM_FADE_OUT, BGM_GAIN_DB, DUCK_ATTACK, DUCK_RELEASE, FONT, INK, VO_GAIN_DB, YELLOW, clamp, db} from '../v3/theme';

export type V3dProps = {hideSubs: boolean; hideExtras: boolean};
type Kf = {t: number; s: number; x: number; y: number};
type Shot = {id: string; t0: number; t1: number; world: {type: string; src: string; k?: number}; cam: Kf[]; ov: O[]; src: string | null; enter: string; grayAt: number | null};
const SHOTS = data.shots as unknown as Shot[];
const FPS = data.fps;
const F = `${FONT}, "Noto Sans CJK SC", sans-serif`;
const easeIO = (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

const camAt = (cam: Kf[], t: number, sh: Shot): Kf => {
  const kf = cam.length ? cam : [{t: sh.t0, s: 1, x: 960, y: 540}, {t: sh.t1, s: 1.05, x: 960, y: 540}];
  if (t <= kf[0].t) return kf[0];
  for (let i = 0; i < kf.length - 1; i++) {
    const a = kf[i], b = kf[i + 1];
    if (t < b.t) {
      const dt = b.t - a.t;
      let k = (t - a.t) / Math.max(1e-6, dt);
      const fast = Math.abs(b.s - a.s) / Math.max(dt, 1e-3) > 0.12 || Math.hypot(b.x - a.x, b.y - a.y) / Math.max(dt, 1e-3) > 80;
      if (fast) k = easeIO(k);
      return {t, s: a.s + (b.s - a.s) * k, x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k};
    }
  }
  return kf[kf.length - 1];
};
// 摄像机不许露出 world 边（s≥1 时把中心夹在可视范围内）
const clampCam = (c: Kf): Kf => {
  const s = Math.max(1, c.s);
  const hx = 960 / s, hy = 540 / s;
  return {...c, s, x: Math.min(1920 - hx, Math.max(hx, c.x)), y: Math.min(1080 - hy, Math.max(hy, c.y))};
};

const ShotView: React.FC<{sh: Shot; hideExtras: boolean}> = ({sh, hideExtras}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = sh.t0 + frame / fps;
  const c = clampCam(camAt(sh.cam, t, sh));
  // 切入的一下「顿」：4 帧内 1.035→1
  const settle = sh.enter === 'none' ? 1 : interpolate(frame, [0, 4], [1.035, 1], clamp);
  // 震屏 / 闪白
  let shx = 0, shy = 0, flash = 0;
  for (const o of sh.ov) {
    const lf = (t - o.t) * fps;
    if (o.k === 'shake' && lf >= 0 && lf < 9) { const a = (1 - lf / 9) * 14; shx += Math.sin(lf * 2.9) * a; shy += Math.cos(lf * 3.7) * a * 0.6; }
    if (o.k === 'flash' && lf >= 0 && lf < 5) flash = Math.max(flash, interpolate(lf, [0, 1, 5], [0.45, 0.3, 0], clamp));
  }
  const gray = sh.grayAt != null ? interpolate(t, [sh.grayAt, sh.grayAt + 0.12], [0, 1], clamp) : 0;
  const s = c.s * settle;
  const tf = `translate(${960 - c.x * s + shx}px, ${540 - c.y * s + shy}px) scale(${s})`;
  const ctx = {t, fps, shotEnd: sh.t1};
  const vis = (o: O) => t >= o.t && (o.t1 === undefined || o.k === 'cursor' || o.k === 'dash' || o.k === 'qmark' || t < o.t1);
  const world = sh.ov.filter((o) => WORLD_KINDS.has(o.k) && !o.screen && vis(o));
  const screen = sh.ov.filter((o) => (!WORLD_KINDS.has(o.k) || o.screen) && o.k !== 'shake' && o.k !== 'flash' && vis(o));
  const extrasHidden = (o: O) => hideExtras && (o.k === 'danmaku');
  return (
    <AbsoluteFill style={{background: INK, overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transformOrigin: '0 0', transform: tf}}>
        <div style={{position: 'absolute', inset: 0, filter: gray ? `grayscale(${gray})` : undefined}}>
          {sh.world.type === 'video' ? (
            <OffthreadVideo src={staticFile(sh.world.src)} muted style={{width: 1920, height: 1080}} />
          ) : (
            <Img src={staticFile(sh.world.src)} style={{width: 1920, height: 1080}} />
          )}
          {world.filter((o) => o.k === 'img' || o.k === 'stamp').map((o, i) => <Overlay key={`wi${i}`} o={o} c={ctx} />)}
        </div>
        {world.filter((o) => o.k !== 'img' && o.k !== 'stamp').map((o, i) => <Overlay key={`w${i}`} o={o} c={ctx} />)}
      </div>
      {screen.filter((o) => !extrasHidden(o)).map((o, i) => <Overlay key={`s${i}`} o={o} c={ctx} />)}
      {!hideExtras && sh.ov.some((o) => o.k === 'danmaku') ? (
        <div style={{position: 'absolute', left: 40, top: 848, padding: '3px 12px', borderRadius: 6, background: 'rgba(0,0,0,.66)', color: '#FF9F43', fontFamily: F, fontWeight: 700, fontSize: 22}}>示意弹幕</div>
      ) : null}
      {sh.src ? (
        <div data-layer="source" style={{position: 'absolute', right: 40, top: 852, padding: '3px 12px 5px', borderRadius: 6, background: 'rgba(0,0,0,.5)', color: 'rgba(255,255,255,.82)', fontFamily: F, fontWeight: 700, fontSize: 21, whiteSpace: 'nowrap'}}>{sh.src}</div>
      ) : null}
      {flash > 0 ? <AbsoluteFill style={{background: '#fff', opacity: flash}} /> : null}
    </AbsoluteFill>
  );
};

// 片内标题条：y 42–120
const TitleBar: React.FC = () => {
  const f = useCurrentFrame();
  const k = interpolate(f, [0, 6], [0, 1], {...clamp, easing: (x) => 1 - Math.pow(1 - x, 3)});
  const [a, b] = ['满海漂着', '免费 iPhone？'];
  return (
    <div data-layer="title" style={{position: 'absolute', left: 0, right: 0, top: 42, height: 78, display: 'flex', justifyContent: 'center', transform: `translateY(${(1 - k) * -90}px)`}}>
      <div style={{height: 78, boxSizing: 'border-box', padding: '0 34px', display: 'flex', alignItems: 'center', borderRadius: 14, background: 'rgba(14,14,16,.84)', borderBottom: `5px solid ${YELLOW}`,
        fontFamily: F, fontWeight: 700, fontSize: 44, color: '#fff', whiteSpace: 'nowrap', boxShadow: '0 8px 20px rgba(0,0,0,.35)'}}>
        {a}<span style={{color: YELLOW}}>{b}</span><span style={{marginLeft: 14}}>真相拆给你看</span>
      </div>
    </div>
  );
};

type Cue = {sid: string; start: number; end: number; text: string; segs: (string | null)[][]};
const CUES = data.subs as unknown as Cue[];
const SubLine: React.FC<{segs: (string | null)[][]; stroke: boolean}> = ({segs, stroke}) => (
  <div style={{position: 'absolute', left: 0, right: 0, top: 0, textAlign: 'center', whiteSpace: 'nowrap', fontFamily: F, fontWeight: 700, fontSize: 66, lineHeight: '96px', letterSpacing: 2,
    color: stroke ? 'transparent' : '#FFFFFF', WebkitTextStroke: stroke ? '12px #000' : undefined}}>
    {segs.map(([tx, col], i) => <span key={i} style={{color: stroke ? 'transparent' : (col ?? '#FFFFFF')}}>{tx}</span>)}
  </div>
);
const Subs: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const cue = CUES.find((c) => t >= c.start && t < c.end);
  if (!cue) return null;
  const pop = Math.min(1, (t - cue.start) / 0.1);
  return (
    <div data-layer="subs" style={{position: 'absolute', left: 0, right: 0, top: 940, height: 96, transform: `scale(${0.94 + 0.06 * pop})`, transformOrigin: 'center center'}}>
      <SubLine segs={cue.segs} stroke />
      <SubLine segs={cue.segs} stroke={false} />
    </div>
  );
};

// BGM 闪避：口播句内压低 BGM_DUCK_DB（起 DUCK_ATTACK，收 DUCK_RELEASE），末尾淡出
const SPEECH = data.speech as number[][];
const duckGate = (t: number) => {
  let g = 0;
  for (const [s, e] of SPEECH) {
    if (t < s - DUCK_ATTACK || t > e + DUCK_RELEASE) continue;
    const v = t < s ? (t - (s - DUCK_ATTACK)) / DUCK_ATTACK : t <= e ? 1 : 1 - (t - e) / DUCK_RELEASE;
    g = Math.max(g, v);
  }
  return g;
};
const bgmVolume = (f: number) => {
  const t = f / FPS;
  const k = interpolate(t, [data.total - BGM_FADE_OUT, data.total], [0, 1], clamp);
  const fade = 0.5 + 0.5 * Math.cos(Math.PI * k);
  return Math.min(1, db(BGM_GAIN_DB + BGM_DUCK_DB * duckGate(t)) * fade);
};

export const IphoneFakeV3d: React.FC<V3dProps> = ({hideSubs, hideExtras}) => {
  useV3Font();
  return (
    <AbsoluteFill style={{background: INK}}>
      {SHOTS.map((sh) => {
        const from = Math.round(sh.t0 * FPS);
        const to = Math.round(sh.t1 * FPS);
        return (
          <Sequence key={sh.id} from={from} durationInFrames={Math.max(1, to - from)} name={sh.id}>
            <ShotView sh={sh} hideExtras={hideExtras} />
          </Sequence>
        );
      })}
      <TitleBar />
      {!hideExtras ? <BrandBadge /> : null}
      {!hideSubs ? <Subs /> : null}
      <Audio src={staticFile(data.vo)} volume={db(VO_GAIN_DB)} />
      <Audio src={staticFile(data.bgm)} volume={bgmVolume} />
      {data.sfx.map((x, i) => (
        <Sequence key={`sfx${i}`} from={Math.max(0, Math.round(x.t * FPS))} name={`sfx ${x.kind}`} layout="none">
          <Audio src={staticFile(x.file)} volume={x.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
