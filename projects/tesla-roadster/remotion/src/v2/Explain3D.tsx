import React from 'react';
import * as THREE from 'three';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import {Arrow} from '../Car2';
import car from '../car.json';
import fitA from '../hfitA.json';
import fitB from '../hfitB.json';
import {C, Callout, Chip, Credit, F, NumberPop, e, lin, usePop, FPS} from './theme';

type V = 'A' | 'B';
type V3 = [number, number, number];
/** All times are ABSOLUTE seconds on the master timeline. */
export const CFG = {
  A: {freeze: 'hA.png', cut: 'hcutA.png', fit: fitA as any, az0: -0.5, az1: 0.25, el: 0.32, npos: [0, -0.45, -12.5] as V3,
    t0: 17.1, three: [17.75, 18.1], settle: [18.3, 21.3], xray: [17.95, 18.5], end: 27.9},
  B: {freeze: 'hB.png', cut: 'hcutB.png', fit: fitB as any, az0: Math.PI + 0.5, az1: Math.PI - 0.2, el: 0.3, npos: [-0.6, -0.35, -13] as V3,
    t0: 30.4, three: [30.95, 31.3], settle: [31.4, 34.6], xray: [31.1, 31.6], end: 46.9},
};

export function pose(v: V, t: number) {
  const c = CFG[v];
  const tN = e(t, c.settle[0], c.settle[1]);
  const orbit = e(t, c.settle[1], c.end);
  let az = c.az0 + (c.az1 - c.az0) * orbit;
  if (v === 'B') az += 0.55 * e(t, 42.3, 44.0) - 0.55 * e(t, 44.6, 46.6);
  const qN = new THREE.Quaternion().setFromEuler(new THREE.Euler(c.el, az, 0, 'XYZ'));
  const q = new THREE.Quaternion(...(c.fit.q as [number, number, number, number])).slerp(qN, tN);
  const pos = (c.fit.pos as number[]).map((p, i) => p + (c.npos[i] - p) * tN) as V3;
  // gentle push-ins / nudge
  let push = 0;
  if (v === 'A') push = 1.6 * e(t, 23.6, 24.4) - 1.0 * e(t, 25.0, 26.2);
  if (v === 'B') { pos[0] += 0.5 * e(t, 36.6, 37.6) - 0.5 * e(t, 38.0, 39.2); pos[1] += 0.25 * e(t, 36.6, 37.6) - 0.25 * e(t, 38.0, 39.2); push = 2.0 * e(t, 44.2, 46.2); }
  const fov = c.fit.fov + (30 - c.fit.fov) * tN + push;
  const sc = (c.fit.scale as number[]).map((s) => s + (1 - s) * tN) as V3;
  return {q, pos, fov, sc, tN};
}
export function project(v: V, t: number, local: V3) {
  const {q, pos, fov, sc} = pose(v, t);
  const p = new THREE.Vector3(local[0] * sc[0], local[1] * sc[1], local[2] * sc[2]).applyQuaternion(q).add(new THREE.Vector3(...pos));
  const th = Math.tan((fov * Math.PI) / 360);
  const x = p.x / -p.z / (th * (16 / 9)), y = p.y / -p.z / th;
  return {x: ((x + 1) / 2) * 1920, y: ((1 - y) / 2) * 1080};
}

/** visibility states */
function st(v: V, t: number) {
  const c = CFG[v];
  if (v === 'A') return {xray: e(t, c.xray[0], c.xray[1]), fanO: e(t, 17.95, 18.4), flow: e(t, 19.1, 19.9), low: e(t, 21.1, 21.7), press: e(t, 22.7, 23.4), pulse: e(t, 23.7, 24.0) - e(t, 24.0, 24.6),
    tank: 0, valve: 0, jet: 0, back: 0, fwd: 0, side: 0};
  return {xray: e(t, c.xray[0], c.xray[1]), fanO: 0, flow: 0, low: 0, press: 0, pulse: 0,
    tank: e(t, 31.2, 31.8), valve: e(t, 32.55, 32.8) * (1 - 0.6 * e(t, 34.5, 35.5)), jet: e(t, 33.4, 33.9) * (1 - e(t, 40.6, 41.2)) + e(t, 44.6, 45.4) * 0.6,
    back: e(t, 35.8, 36.3) * (1 - e(t, 40.8, 41.2)), fwd: e(t, 36.7, 37.2) * (1 - e(t, 40.8, 41.2)), side: e(t, 41.9, 42.3) * (1 - e(t, 44.4, 45.0))};
}

const Rig: React.FC<{fov: number}> = ({fov}) => { const {camera} = useThree(); const c = camera as THREE.PerspectiveCamera;
  c.position.set(0, 0, 0); c.up.set(0, 1, 0); c.lookAt(0, 0, -1); c.fov = fov; c.near = 0.1; c.far = 200; c.updateProjectionMatrix(); return null; };

const useGeo = () => React.useMemo(() => { const pos = new THREE.Float32BufferAttribute(car.pos as number[], 3);
  const mk = (idx: number[]) => { const g = new THREE.BufferGeometry(); g.setAttribute('position', pos); g.setIndex(idx); g.computeVertexNormals(); return g; };
  return {body: mk(car.body as number[]), glass: mk(car.glass as number[]), all: mk([...(car.body as number[]), ...(car.glass as number[])])}; }, []);

const Scene: React.FC<{v: V; t: number; f: number}> = ({v, t, f}) => {
  const g = useGeo(); const {q, pos, fov, sc, tN} = pose(v, t); const s = st(v, t);
  const op = 1 - 0.8 * s.xray; const glow = 0.4 + 0.8 * s.pulse;
  const parts: React.ReactNode[] = [];
  if (s.flow > 0) for (let i = 0; i < 40; i++) { const k = ((i / 40) + f * 0.016) % 1; const ang = i * 2.399;
    const a = new THREE.Vector3(Math.cos(ang) * 1.9, 0.06, Math.sin(ang) * 1.0), m = new THREE.Vector3(-0.1, 0.13, 0), b = new THREE.Vector3(-3.0, 0.3, i % 2 ? 0.45 : -0.45);
    const p = k < 0.6 ? a.lerp(m, k / 0.6) : m.clone().lerp(b, (k - 0.6) / 0.4);
    parts.push(<mesh key={'a' + i} position={p}><sphereGeometry args={[0.045, 8, 8]} /><meshBasicMaterial color="#9fe6ff" transparent opacity={0.85 * s.flow} toneMapped={false} /></mesh>); }
  if (s.jet > 0) for (let i = 0; i < 36; i++) { const k = ((i / 36) + f * 0.03) % 1; const ang = i * 2.399; const z = i % 2 ? 0.4 : -0.4;
    parts.push(<mesh key={'b' + i} position={[-2.3 - k * 2.2, 0.58 + Math.sin(ang) * 0.12 * k, z + Math.cos(ang) * 0.14 * k]}><sphereGeometry args={[0.05 + 0.06 * k, 8, 8]} /><meshBasicMaterial color="#e8f6ff" transparent opacity={0.75 * (1 - k) * s.jet} toneMapped={false} /></mesh>); }
  const sidePts: [number, number, number, number][] = [[1.75, 0.62, 0.78, 1], [1.75, 0.62, -0.78, 1], [-1.85, 0.82, 0.85, -1], [-1.85, 0.82, -0.85, -1]];
  return <>
    <Rig fov={fov} />
    <ambientLight intensity={0.3 + 0.15 * tN} />
    <hemisphereLight args={['#cfe0ff', '#151010', 0.6]} />
    <directionalLight position={[3, 10, 4]} intensity={1.4 + 1.0 * tN} />
    <pointLight position={[-6, 3, -12]} intensity={40} color="#5fb8ff" />
    <pointLight position={[6, 2, -12]} intensity={25} color="#ff6b7a" />
    <group position={pos} quaternion={q} scale={sc}>
      <mesh geometry={g.body}><meshPhysicalMaterial color="#e6e9ec" metalness={0.25} roughness={0.32} clearcoat={1} transparent={s.xray > 0} opacity={op} depthWrite={s.xray < 0.3} /></mesh>
      <mesh geometry={g.glass}><meshPhysicalMaterial color="#05070a" metalness={0.5} roughness={0.05} transparent={s.xray > 0} opacity={Math.max(op, 0.25)} depthWrite={s.xray < 0.3} /></mesh>
      {s.xray > 0.02 && <mesh geometry={g.all}><meshBasicMaterial color="#7fdcff" wireframe transparent opacity={0.07 * s.xray} /></mesh>}
      {(car.wheels as number[][]).map(([x, y, z], i) => <group key={i} position={[x, y, z]} rotation={[Math.PI / 2, 0, 0]}><mesh><cylinderGeometry args={[car.wr, car.wr, car.ww, 40]} /><meshStandardMaterial color="#121418" roughness={0.85} /></mesh></group>)}
      {s.fanO > 0.01 && <group position={[-0.1, 0.13, 0]}>
        <mesh rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[0.5, 0.045, 16, 64]} /><meshStandardMaterial color="#ffb347" emissive="#ff8a00" emissiveIntensity={glow} transparent opacity={s.fanO} toneMapped={false} /></mesh>
        <group rotation={[0, f * (0.25 + 0.5 * s.flow), 0]}>{Array.from({length: 7}).map((_, i) => <mesh key={i} rotation={[0, (i * Math.PI * 2) / 7, 0.35]}><boxGeometry args={[0.9, 0.02, 0.13]} /><meshStandardMaterial color="#ffd08a" emissive="#ff9a1f" emissiveIntensity={glow} transparent opacity={s.fanO} toneMapped={false} /></mesh>)}</group>
      </group>}
      {s.low > 0 && <mesh position={[-0.1, 0.09, 0]}><cylinderGeometry args={[1.7, 1.7, 0.08, 48]} /><meshBasicMaterial color="#ff3b52" transparent opacity={(0.22 + 0.12 * Math.sin(f * 0.25)) * s.low} depthWrite={false} /></mesh>}
      {s.press > 0 && [-1.3, 0, 1.3].map((x, i) => <Arrow key={i} from={[x, 2.7 - 0.12 * Math.sin(f * 0.2 + i) - 0.3 * s.pulse, 0]} dir={[0, -1, 0]} len={1.0 * s.press} color="#4aa8ff" r={0.07 + 0.02 * s.pulse} opacity={s.press} />)}
      {s.tank > 0.01 && <group>
        <mesh position={[-0.75, 0.62, 0]} rotation={[Math.PI / 2, 0, 0]}><capsuleGeometry args={[0.2, 0.85, 8, 24]} /><meshStandardMaterial color="#5ad1ff" emissive="#1aa6ff" emissiveIntensity={0.5 + 0.5 * s.tank} transparent opacity={s.tank} toneMapped={false} /></mesh>
        <mesh position={[-1.12, 0.62, 0]} rotation={[0, 0, Math.PI / 2]} scale={1 + 0.6 * s.valve}><cylinderGeometry args={[0.09, 0.09, 0.16, 20]} /><meshStandardMaterial color="#ff4d5e" emissive="#ff2040" emissiveIntensity={0.4 + 2.0 * s.valve} transparent opacity={s.tank} toneMapped={false} /></mesh>
        {[0.4, -0.4].map((z) => <group key={z}>
          <mesh position={[-1.62, 0.6, z / 2]} rotation={[0, Math.atan2(z / 2, 0.9), Math.PI / 2]}><cylinderGeometry args={[0.035, 0.035, 0.95, 10]} /><meshStandardMaterial color="#cfe9ff" emissive="#79c8ff" emissiveIntensity={0.5 + s.jet} transparent opacity={s.tank} toneMapped={false} /></mesh>
          <mesh position={[-2.18, 0.58, z]} rotation={[0, 0, Math.PI / 2]}><coneGeometry args={[0.13, 0.26, 24, 1, true]} /><meshStandardMaterial color="#c0c6cc" metalness={0.9} roughness={0.2} side={THREE.DoubleSide} transparent opacity={s.tank} /></mesh>
          {s.jet > 0 && <mesh position={[-2.3 - 0.75 * s.jet, 0.58, z]} rotation={[0, 0, -Math.PI / 2]}><coneGeometry args={[0.28, 1.5 * s.jet, 24, 1, true]} /><meshBasicMaterial color="#cfeaff" transparent opacity={0.32} blending={THREE.AdditiveBlending} depthWrite={false} side={THREE.DoubleSide} /></mesh>}
        </group>)}
        {sidePts.map((p, i) => <group key={i}>
          <mesh position={[p[0], p[1], p[2]]}><sphereGeometry args={[0.07, 16, 16]} /><meshStandardMaterial color="#ffe36b" emissive="#ffc400" emissiveIntensity={0.6 + 1.5 * s.side} transparent opacity={s.tank} toneMapped={false} /></mesh>
          {s.side > 0 && <mesh position={[p[0], p[1] + p[3] * 0.32 * s.side, p[2]]} rotation={[p[3] > 0 ? 0 : Math.PI, 0, 0]}><coneGeometry args={[0.12, 0.6 * s.side * (0.8 + 0.2 * Math.sin(f * 0.9 + i)), 16, 1, true]} /><meshBasicMaterial color="#fff2a8" transparent opacity={0.55} blending={THREE.AdditiveBlending} depthWrite={false} /></mesh>}
        </group>)}
      </group>}
      {s.back > 0 && <Arrow from={[-2.6, 1.25, 0]} dir={[-1, 0, 0]} len={1.4 * s.back} color="#4fd1ff" r={0.08} />}
      {s.fwd > 0 && <Arrow from={[0.4, 1.35, 0]} dir={[1, 0.55, 0]} len={1.7 * s.fwd} color="#ff9a2e" r={0.09} />}
      {parts}
    </group>
  </>;
};

/** Pure 3D canvas (used by panels too). */
export const Car3DLayer: React.FC<{v: V; t: number}> = ({v, t}) => { const f = useCurrentFrame();
  return <ThreeCanvas width={1920} height={1080} gl={{antialias: true, toneMapping: THREE.ACESFilmicToneMapping}}><Scene v={v} t={t} f={f} /></ThreeCanvas>; };

/** Balloon analogy inset (2D) */
const Balloon: React.FC<{t: number}> = ({t}) => {
  const o = e(t, 38.2, 38.6) * (1 - e(t, 40.5, 40.9)); if (o <= 0) return null;
  const k = e(t, 38.5, 40.2, (x) => x);
  const bx = 330 - 200 * k, by = 190 - 30 * Math.sin(k * 3);
  return <div style={{position: 'absolute', left: 1240, top: 250, width: 560, height: 400, opacity: o, transform: `translateY(${(1 - o) * 20}px)`, borderRadius: 18, background: C.glass, border: '1px solid rgba(255,255,255,0.14)', zIndex: 44, overflow: 'hidden'}}>
    <svg width={560} height={330}>
      {Array.from({length: 9}).map((_, i) => { const kk = ((i / 9) + t * 1.6) % 1; return <circle key={i} cx={bx + 70 + kk * 170} cy={by + (i % 3 - 1) * 12 * kk} r={4 + 8 * kk} fill="#cfeaff" opacity={(1 - kk) * 0.8 * e(t, 38.5, 38.7)} />; })}
      <ellipse cx={bx} cy={by} rx={62} ry={50} fill="#ff3b4f" />
      <ellipse cx={bx - 18} cy={by - 18} rx={14} ry={9} fill="#ffffff" opacity={0.35} />
      <polygon points={`${bx + 60},${by} ${bx + 76},${by - 9} ${bx + 76},${by + 9}`} fill="#d92a3e" />
      <line x1={bx + 90} y1={by + 70} x2={bx + 200} y2={by + 70} stroke={C.cyan} strokeWidth={4} markerEnd="url(#ah)" />
      <line x1={bx - 40} y1={by + 70} x2={bx - 140} y2={by + 70} stroke={C.amber} strokeWidth={4} markerEnd="url(#ah2)" />
      <defs><marker id="ah" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill={C.cyan} /></marker>
        <marker id="ah2" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill={C.amber} /></marker></defs>
    </svg>
    <div style={{position: 'absolute', bottom: 22, left: 0, right: 0, textAlign: 'center', fontFamily: F, fontWeight: 800, fontSize: 30, color: C.white}}>
      <span style={{color: C.cyan}}>气往后</span>　<span style={{color: C.amber}}>球往前</span></div>
  </div>;
};

export const Explain3D: React.FC<{v: V; start: number}> = ({v, start}) => {
  const f = useCurrentFrame(); const t = start + f / FPS; const c = CFG[v];
  const dim = e(t, c.t0, c.t0 + 0.45); const flash = lin(t, [c.t0, c.t0 + 0.05, c.t0 + 0.3], [0, 0.55, 0]);
  const glow = e(t, c.t0 + 0.2, c.t0 + 0.5) * (1 - e(t, c.three[0], c.three[1]));
  const cutO = 1 - e(t, c.three[0], c.three[1] + 0.1); const three = e(t, c.three[0], c.three[1]);
  const shift = v === 'B' ? -230 * (e(t, 38.1, 38.7) - e(t, 40.4, 41.0)) : 0;
  const P = (local: V3) => { const p = project(v, t, local); return {x: p.x + shift, y: p.y}; };
  const pop = (at: number) => usePop(t, at);
  const out = (a: number) => 1 - e(t, a, a + 0.4);
  const callouts = v === 'A' ? [
    {at: 18.15, end: 21.0, local: [-0.1, 0.13, 0] as V3, label: '车底风扇', color: C.amber, dx: 200, dy: 150},
    {at: 21.25, end: 25.5, local: [0.9, 0.09, 0.9] as V3, label: '车底低压区', color: C.red, dx: 220, dy: 150},
    {at: 22.7, end: 25.5, local: [-1.3, 3.2, 0] as V3, label: '外面的大气压', color: C.cyan, dx: -200, dy: -60},
  ] : [
    {at: 31.4, end: 32.5, local: [-0.75, 0.62, 0] as V3, label: '高压气罐', color: C.cyan, dx: 200, dy: -170},
    {at: 32.6, end: 35.3, local: [-1.12, 0.62, 0] as V3, label: '阀门 打开', color: C.red, dx: 210, dy: -170},
    {at: 34.0, end: 35.3, local: [-2.25, 0.58, 0] as V3, label: '尾部喷口', color: C.white, dx: -220, dy: 150},
    {at: 42.0, end: 44.2, local: [1.75, 0.62, 0.78] as V3, label: '姿态小喷口', color: C.amber, dx: 200, dy: -160},
  ];
  return <AbsoluteFill style={{background: '#05070b'}}>
    <Img src={staticFile(c.freeze)} style={{position: 'absolute', width: 1920, height: 1080, filter: `brightness(${1 - 0.75 * dim}) blur(${dim * 9}px) saturate(${1 - 0.4 * dim})`}} />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, rgba(30,60,110,0.25) 0%, rgba(0,0,0,0.8) 75%)', opacity: dim}} />
    <Img src={staticFile(c.cut)} style={{position: 'absolute', width: 1920, height: 1080, opacity: cutO * Math.min(1, dim * 3), filter: `drop-shadow(0 0 ${4 + 14 * glow}px rgba(111,214,255,${0.95 * glow}))`}} />
    <AbsoluteFill style={{opacity: three, transform: `translateX(${shift}px)`}}><Car3DLayer v={v} t={t} /></AbsoluteFill>
    <AbsoluteFill style={{background: '#fff', opacity: flash}} />
    <Chip text={v === 'A' ? '拆解一 · 风扇吸地' : '拆解二 · 冷气推进'} sub={three > 0.05 ? '示意模型 非官方' : undefined} accent={v === 'A' ? C.cyan : C.amber} o={e(t, c.t0 + 0.1, c.t0 + 0.5)} />
    {callouts.map((k, i) => { const p = P(k.local); return <Callout key={i} x={p.x} y={p.y} label={k.label} color={k.color} p={pop(k.at)} out={out(k.end)} dx={k.dx} dy={k.dy} />; })}
    {v === 'A' && <NumberPop x={1300} y={250} big="2倍" label="车重的吸附力" color={C.cyan} p={pop(26.45)} />}
    {v === 'B' && <>
      <Balloon t={t} />
      {(() => { const o = pop(44.8) * (1 - e(t, 46.5, 46.9)); return o > 0 ? <div style={{position: 'absolute', right: 120, top: 300, opacity: Math.min(1, o), transform: `translateX(${(1 - o) * 30}px)`, zIndex: 44, padding: '18px 28px', borderRadius: 14, background: C.glass, borderLeft: `5px solid ${C.white}`}}>
        <div style={{fontFamily: F, fontSize: 26, color: C.dim, letterSpacing: 3}}>技术来源</div>
        <div style={{fontFamily: F, fontWeight: 900, fontSize: 56, color: C.white, letterSpacing: 2}}>SpaceX 冷气推进器</div></div> : null; })()}
      {(() => { const o = pop(36.0) * (1 - e(t, 37.9, 38.2)); return o > 0 ? <div style={{position: 'absolute', left: 1330, top: 260, zIndex: 44, opacity: Math.min(1, o), fontFamily: F, fontWeight: 900, fontSize: 44, lineHeight: 1.5}}>
        <div style={{color: C.cyan}}>气往后喷</div><div style={{color: C.amber, opacity: e(t, 36.8, 37.1)}}>车往前 往上冲</div></div> : null; })()}
    </>}
    <Credit text={three > 0.5 ? '示意动画 · 背景画面来源：Tesla' : '画面来源：Tesla'} />
  </AbsoluteFill>;
};
