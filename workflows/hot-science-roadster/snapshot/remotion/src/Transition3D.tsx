import React from 'react';
import * as THREE from 'three';
import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  interpolate,
  Easing,
} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import {Car2, Arrow} from './Car2';
import fitA from './hfitA.json';
import fitB from './hfitB.json';
import {Chip, ModelDisclaimer, Pill, SourceCredit, cl} from './ui';

const ease = Easing.bezier(0.45, 0, 0.2, 1);
const iv = (f: number, a: number[], b: number[]) =>
  interpolate(f, a, b, {...cl, easing: ease});

type Variant = 'A' | 'B';

const CFG = {
  A: {
    live: 'hliveA.mp4',
    freeze: 'hA.png',
    cut: 'hcutA.png',
    fit: fitA,
    az0: -0.5,
    az1: 0.3,
    el: 0.32,
    npos: [0, -0.45, -12.5] as [number, number, number],
    chip: '拆解一 风扇吸地',
    call: [
      ['车底低压', '#ff5a6a'],
      ['吸附力 最高约2G', '#5ab8ff'],
    ] as [string, string][],
  },
  B: {
    live: 'hliveB.mp4',
    freeze: 'hB.png',
    cut: 'hcutB.png',
    fit: fitB,
    az0: Math.PI + 0.5,
    az1: Math.PI - 0.25,
    el: 0.3,
    npos: [-1.0, -0.35, -13] as [number, number, number],
    chip: '拆解二 冷气推进',
    call: [
      ['高压气罐 + 阀门', '#5ad1ff'],
      ['尾部冷气喷口 不点火', '#ffb347'],
    ] as [string, string][],
  },
};

/** Phase keyframes scaled to durationInFrames.
 * Keep early live/freeze crisp (~same absolute seconds as v2),
 * stretch orbit / xray / flow to fill the voice block.
 */
function phases(D: number) {
  // Absolute-ish early beats (frames), then stretch the rest
  const liveEnd = Math.min(Math.round(D * 0.22), 105); // ~ up to ~3.5s at 30fps for long D
  const freezeStart = liveEnd;
  const dimEnd = freezeStart + 14;
  const threeIn0 = freezeStart + 26;
  const threeIn1 = freezeStart + 38;
  const cutOut1 = freezeStart + 40;
  const matchEnd = Math.round(D * 0.32);
  const orbit0 = Math.max(matchEnd - 10, threeIn1 + 8);
  const xray0 = Math.round(D * 0.36);
  const xray1 = Math.round(D * 0.48);
  const flow0 = Math.round(D * 0.52);
  const flow1 = Math.round(D * 0.62);
  const call0 = Math.round(D * 0.58);
  const call1 = Math.round(D * 0.7);
  return {
    liveEnd,
    freezeStart,
    dimEnd,
    threeIn0,
    threeIn1,
    cutOut1,
    matchEnd,
    orbit0,
    orbit1: D - 2,
    xray0,
    xray1,
    flow0,
    flow1,
    call0,
    call1,
  };
}

const Rig: React.FC<{fov: number}> = ({fov}) => {
  const {camera} = useThree();
  const c = camera as THREE.PerspectiveCamera;
  c.position.set(0, 0, 0);
  c.up.set(0, 1, 0);
  c.lookAt(0, 0, -1);
  c.fov = fov;
  c.near = 0.1;
  c.far = 200;
  c.updateProjectionMatrix();
  return null;
};

const Scene: React.FC<{v: Variant; f: number; P: ReturnType<typeof phases>; wire?: boolean}> = ({
  v,
  f,
  P,
  wire,
}) => {
  const c = CFG[v];
  const fit = c.fit as {
    q: [number, number, number, number];
    pos: number[];
    fov: number;
    scale: number[];
  };
  const tN = wire ? 0 : iv(f, [P.threeIn1, P.matchEnd], [0, 1]);
  const orbit = iv(f, [P.orbit0, P.orbit1], [0, 1]);
  const xray = iv(f, [P.xray0, P.xray1], [0, 1]);
  const flow = iv(f, [P.flow0, P.flow1], [0, 1]);
  const az = c.az0 + (c.az1 - c.az0) * orbit;
  const qN = new THREE.Quaternion().setFromEuler(new THREE.Euler(c.el, az, 0, 'XYZ'));
  const qF = new THREE.Quaternion(...fit.q);
  const q = qF.clone().slerp(qN, tN);
  const pos = fit.pos.map((p, i) => p + (c.npos[i] - p) * tN) as [number, number, number];
  const fov = fit.fov + (30 - fit.fov) * tN;
  const sc = fit.scale.map((s) => s + (1 - s) * tN) as [number, number, number];
  const N = 36;
  const parts: React.ReactNode[] = [];
  if (flow > 0) {
    for (let i = 0; i < N; i++) {
      const t = ((i / N) + f * 0.018) % 1;
      const ang = i * 2.399;
      let p: THREE.Vector3;
      if (v === 'A') {
        const s = new THREE.Vector3(Math.cos(ang) * 1.9, 0.06, Math.sin(ang) * 1.0);
        const m = new THREE.Vector3(-0.1, 0.13, 0);
        const e = new THREE.Vector3(-3.0, 0.3, i % 2 ? 0.45 : -0.45);
        p = t < 0.6 ? s.lerp(m, t / 0.6) : m.clone().lerp(e, (t - 0.6) / 0.4);
      } else {
        const z = i % 2 ? 0.4 : -0.4;
        p = new THREE.Vector3(
          -2.3 - t * 1.9,
          0.58 + Math.sin(ang) * 0.1 * t,
          z + Math.cos(ang) * 0.12 * t,
        );
      }
      parts.push(
        <mesh key={i} position={p}>
          <sphereGeometry args={[v === 'A' ? 0.045 : 0.05 + 0.05 * t, 10, 10]} />
          <meshBasicMaterial
            color={v === 'A' ? '#9fe6ff' : '#e8f6ff'}
            transparent
            opacity={flow * (v === 'A' ? 0.85 : 0.75 * (1 - t))}
            toneMapped={false}
          />
        </mesh>,
      );
    }
  }
  return (
    <>
      <Rig fov={fov} />
      <ambientLight intensity={0.25 + 0.15 * tN} />
      <hemisphereLight args={['#cfe0ff', '#151010', 0.6]} />
      <directionalLight
        position={[3, 10, 4]}
        intensity={1.3 + 1.1 * tN}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-6}
        shadow-camera-right={6}
        shadow-camera-top={6}
        shadow-camera-bottom={-6}
        shadow-camera-near={1}
        shadow-camera-far={60}
        shadow-radius={6}
        shadow-bias={-0.0004}
      />
      <pointLight position={[-6, 3, -12]} intensity={40} color="#5fb8ff" />
      <pointLight position={[6, 2, -12]} intensity={25} color="#ff6b7a" />
      <group position={pos} quaternion={q} scale={sc}>
        <Car2
          wire={wire}
          xray={xray}
          fanSpin={f * 0.55}
          showFan={v === 'A' && !wire && xray > 0.05}
          showThrust={v === 'B' && !wire && xray > 0.05}
          glow={xray * 0.6}
        />
        {!wire && (
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.001, 0]} receiveShadow>
            <planeGeometry args={[14, 14]} />
            <shadowMaterial opacity={0.5 * tN} />
          </mesh>
        )}
        {v === 'A' && !wire && (
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.002, 0]}>
            <planeGeometry args={[9, 0.07]} />
            <meshBasicMaterial color="#e8e8e8" transparent opacity={0.4 * tN} />
          </mesh>
        )}
        {v === 'A' && flow > 0 && (
          <>
            <mesh position={[-0.1, 0.09, 0]}>
              <cylinderGeometry args={[1.7, 1.7, 0.08, 48]} />
              <meshBasicMaterial
                color="#ff3b52"
                transparent
                opacity={0.28 * flow}
                depthWrite={false}
              />
            </mesh>
            {[-1.3, 0, 1.3].map((x, i) => (
              <Arrow
                key={i}
                from={[x, 2.6 - 0.15 * Math.sin(f * 0.2 + i), 0]}
                dir={[0, -1, 0]}
                len={1.0 * flow}
                color="#4aa8ff"
                r={0.07}
                opacity={flow}
              />
            ))}
          </>
        )}
        {v === 'B' && flow > 0 && (
          <>
            {[0.4, -0.4].map((z) => (
              <mesh
                key={z}
                position={[-2.3 - 0.7 * flow, 0.58, z]}
                rotation={[0, 0, -Math.PI / 2]}
              >
                <coneGeometry args={[0.28, 1.4 * flow, 24, 1, true]} />
                <meshBasicMaterial
                  color="#cfeaff"
                  transparent
                  opacity={0.35}
                  blending={THREE.AdditiveBlending}
                  depthWrite={false}
                  side={THREE.DoubleSide}
                />
              </mesh>
            ))}
            {[
              [1.75, 0.62, 0.78, 1],
              [-1.85, 0.82, -0.85, -1],
            ].map((p, i) => (
              <mesh
                key={i}
                position={[p[0], p[1] + p[3] * 0.3 * flow, p[2]]}
                rotation={[p[3] > 0 ? Math.PI : 0, 0, 0]}
              >
                <coneGeometry args={[0.11, 0.55 * flow, 16, 1, true]} />
                <meshBasicMaterial
                  color="#fff2a8"
                  transparent
                  opacity={0.5}
                  blending={THREE.AdditiveBlending}
                  depthWrite={false}
                />
              </mesh>
            ))}
            <Arrow from={[0.3, 1.3, 0]} dir={[1, 0.55, 0]} len={1.6 * flow} color="#ff9a2e" r={0.09} />
          </>
        )}
        {parts}
      </group>
    </>
  );
};

export const Transition3D: React.FC<{
  v: Variant;
  /** Local duration in frames (extended to match voice). */
  durationInFrames: number;
  /** Hide built-in chip/pills when parent drives captions only. */
  showChrome?: boolean;
}> = ({v, durationInFrames, showChrome = true}) => {
  const f = useCurrentFrame();
  const c = CFG[v];
  const P = phases(durationInFrames);
  const frozen = f >= P.freezeStart;
  const dim = iv(f, [P.freezeStart, P.dimEnd], [0, 1]);
  const flash = interpolate(f, [P.freezeStart, P.freezeStart + 2, P.freezeStart + 8], [0, 0.5, 0], cl);
  const glow =
    iv(f, [P.freezeStart + 14, P.freezeStart + 24], [0, 1]) *
    iv(f, [P.freezeStart + 30, P.cutOut1], [1, 0]);
  const cutO = interpolate(f, [P.threeIn0, P.cutOut1], [1, 0], cl);
  const three = interpolate(f, [P.threeIn0, P.threeIn1], [0, 1], cl);
  const callO = iv(f, [P.call0, P.call1], [0, 1]);
  const chipO = iv(f, [P.freezeStart + 4, P.freezeStart + 16], [0, 1]);

  return (
    <AbsoluteFill style={{background: '#05070b'}}>
      {!frozen && <OffthreadVideo src={staticFile(c.live)} style={{width: 1920, height: 1080}} />}
      {frozen && (
        <>
          <Img
            src={staticFile(c.freeze)}
            style={{
              position: 'absolute',
              inset: 0,
              width: 1920,
              height: 1080,
              filter: `brightness(${1 - 0.72 * dim}) blur(${dim * 8}px) saturate(${1 - 0.4 * dim})`,
            }}
          />
          <AbsoluteFill
            style={{
              background:
                'radial-gradient(ellipse at 50% 50%, rgba(30,60,110,0.22) 0%, rgba(0,0,0,0.75) 75%)',
              opacity: dim,
            }}
          />
          <Img
            src={staticFile(c.cut)}
            style={{
              position: 'absolute',
              inset: 0,
              width: 1920,
              height: 1080,
              opacity: cutO * Math.min(1, dim * 3),
              filter: `drop-shadow(0 0 ${4 + 14 * glow}px rgba(111,214,255,${0.95 * glow})) drop-shadow(0 0 ${2 + 6 * glow}px rgba(190,240,255,${glow}))`,
            }}
          />
          <AbsoluteFill style={{opacity: three}}>
            <ThreeCanvas
              width={1920}
              height={1080}
              shadows
              gl={{antialias: true, toneMapping: THREE.ACESFilmicToneMapping}}
            >
              <Scene v={v} f={f} P={P} />
            </ThreeCanvas>
          </AbsoluteFill>
          <AbsoluteFill style={{background: '#fff', opacity: flash}} />
        </>
      )}
      <SourceCredit />
      {showChrome && (
        <>
          <Chip text={c.chip} opacity={chipO} />
          <ModelDisclaimer opacity={three} />
          <Pill text={c.call[0][0]} color={c.call[0][1]} side="left" opacity={callO} top={700} />
          <Pill text={c.call[1][0]} color={c.call[1][1]} side="right" opacity={callO} top={700} />
        </>
      )}
    </AbsoluteFill>
  );
};

/** Export phase helpers for still-frame picking. */
export const transitionPhaseFrames = (durationInFrames: number) => phases(durationInFrames);
