import React from 'react';
import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  interpolate,
  Sequence,
} from 'remotion';
import {
  Chip,
  DanmakuCards,
  FactCard,
  InfoCard,
  SourceCredit,
  Stamp,
  cl,
  F,
} from './ui';
import {Transition3D} from './Transition3D';

const CoverVideo: React.FC<{
  src: string;
  startFrom?: number;
  style?: React.CSSProperties;
}> = ({src, startFrom = 0, style}) => (
  <OffthreadVideo
    src={staticFile(src)}
    startFrom={startFrom}
    style={{width: 1920, height: 1080, objectFit: 'cover', ...style}}
  />
);

const CoverImg: React.FC<{src: string; darken?: number}> = ({src, darken = 0}) => (
  <>
    <Img
      src={staticFile(src)}
      style={{
        width: 1920,
        height: 1080,
        objectFit: 'cover',
        filter: darken ? `brightness(${1 - darken})` : undefined,
      }}
    />
  </>
);

/** S01 Hook — fly over Semi */
export const ShotHook: React.FC = () => {
  // clip-fly ~61s; apex around ~40s into clip (event 1360 ≈ clip 40)
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <CoverVideo src="clip-fly.mp4" startFrom={Math.round(40 * 30)} />
      <SourceCredit />
    </AbsoluteFill>
  );
};

/** S02 Not VFX / Not AI stamps over fly */
export const ShotNotVfx: React.FC = () => {
  const f = useCurrentFrame();
  const showAi = f > 30; // ~1s into shot (也不是AI at ~4.5 global)
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <CoverVideo src="clip-fly.mp4" startFrom={Math.round(43 * 30)} />
      <Stamp lines={showAi ? ['不是特效', '也不是AI'] : ['不是特效']} />
      <SourceCredit />
    </AbsoluteFill>
  );
};

/** S03 Danmaku question cards */
export const ShotDanmaku: React.FC = () => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 10], [0, 1], cl);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <CoverVideo src="clip-fly.mp4" startFrom={Math.round(20 * 30)} />
      <DanmakuCards
        opacity={o}
        cards={[
          '怎么飞的？',
          '假的吧',
          '推进器原理',
          '是不是AI',
          '风扇吸地？',
          '能上路吗',
          '它到底怎么飞起来的',
        ]}
      />
      <Chip text="评论区热问" color="linear-gradient(90deg,#503cc8,#7a5cff)" />
      <SourceCredit />
    </AbsoluteFill>
  );
};

/** S04 Two systems fact */
export const ShotTwoSystems: React.FC = () => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 8], [0, 1], cl);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <CoverImg src="ramp_wall.jpg" darken={0.35} />
      <FactCard title="车上装了两套系统" subtitle="风扇吸地  +  冷气推进" opacity={o} />
      <SourceCredit />
    </AbsoluteFill>
  );
};

/** S05+S06 Transition A extended */
export const ShotTransitionA: React.FC<{durationInFrames: number}> = ({durationInFrames}) => (
  <Transition3D v="A" durationInFrames={durationInFrames} />
);

/** S07 Transition B extended */
export const ShotTransitionB: React.FC<{durationInFrames: number}> = ({durationInFrames}) => (
  <Transition3D v="B" durationInFrames={durationInFrames} />
);

/** S08 Dual summary panels */
export const ShotSummary: React.FC = () => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 10], [0, 1], cl);
  return (
    <AbsoluteFill style={{background: '#05070b'}}>
      <Chip text="一句话记住" color="linear-gradient(90deg,#2878c8,#40a0ff)" opacity={o} />
      <div
        style={{
          position: 'absolute',
          left: 40,
          top: 200,
          width: 900,
          height: 506,
          border: '4px solid #5ab4ff',
          borderRadius: 8,
          overflow: 'hidden',
          opacity: o,
        }}
      >
        <Img src={staticFile('panel-A-flow.png')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'brightness(0.55)'}} />
        {/* reuse freeze as panel bg; overlay label */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'radial-gradient(ellipse at 40% 60%, rgba(40,80,140,0.35), rgba(0,0,0,0.55))',
          }}
        />
      </div>
      <div
        style={{
          position: 'absolute',
          left: 980,
          top: 200,
          width: 900,
          height: 506,
          border: '4px solid #ff8c3c',
          borderRadius: 8,
          overflow: 'hidden',
          opacity: o,
        }}
      >
        <Img src={staticFile('panel-B-flow.png')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'brightness(0.55)'}} />
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'radial-gradient(ellipse at 60% 50%, rgba(140,60,20,0.35), rgba(0,0,0,0.55))',
          }}
        />
      </div>
      {[
        {t: '风扇负责吸', x: 40, color: '#5ab4ff'},
        {t: '喷气负责飞', x: 980, color: '#ff8c3c'},
      ].map((lab) => (
        <div
          key={lab.t}
          style={{
            position: 'absolute',
            left: lab.x + (900 - 280) / 2,
            top: 120,
            width: 280,
            textAlign: 'center',
            fontFamily: F,
            fontWeight: 900,
            fontSize: 40,
            color: lab.color,
            padding: '10px 16px',
            borderRadius: 14,
            background: 'rgba(12,16,24,0.9)',
            border: `3px solid ${lab.color}`,
            opacity: o,
          }}
        >
          {lab.t}
        </div>
      ))}
      <SourceCredit extra="示意模型 非官方" />
    </AbsoluteFill>
  );
};

/** S09 Can you buy / info / price — phases by local frame */
export const ShotInfo: React.FC<{durationInFrames: number}> = ({durationInFrames}) => {
  const f = useCurrentFrame();
  // Phase splits roughly matching voice sentences 22-25
  // 那你能开上吗 ~1.3s, 2028 ~1.8s, 封闭场地 ~2.6s, 售价 ~2.5s
  const p1 = Math.round(durationInFrames * 0.14);
  const p2 = Math.round(durationInFrames * 0.36);
  const p3 = Math.round(durationInFrames * 0.62);
  let phase: 'ask' | 'year' | 'site' | 'price' = 'ask';
  if (f >= p3) phase = 'price';
  else if (f >= p2) phase = 'site';
  else if (f >= p1) phase = 'year';

  const bg =
    phase === 'ask' ? 'promo_01.jpg' : phase === 'price' ? 'promo_03.jpg' : 'promo_02.jpg';

  return (
    <AbsoluteFill style={{background: '#000'}}>
      <CoverImg src={bg} darken={0.4} />
      {phase === 'ask' && <FactCard title="那你能开上它吗？" />}
      {(phase === 'year' || phase === 'site') && (
        <InfoCard
          title="量产与上路"
          items={[
            {label: '2028 年才量产', color: '#5ac8ff'},
            {label: '会飞版仅限封闭场地', color: '#ffb450'},
            {label: '订金最高 25 万美元', color: '#ff6464'},
          ]}
        />
      )}
      {phase === 'price' && (
        <FactCard title="售价没公布" subtitle="订金最高二十五万美元" />
      )}
      <SourceCredit />
    </AbsoluteFill>
  );
};

/** S10 Ending CTA */
export const ShotEnding: React.FC = () => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 8], [0, 1], cl);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <CoverVideo src="clip-fly.mp4" startFrom={Math.round(55 * 30)} />
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          background: 'rgba(0,0,0,0.3)',
          opacity: o,
        }}
      >
        <div
          style={{
            fontFamily: F,
            fontWeight: 900,
            fontSize: 74,
            color: '#fff5f5',
            padding: '28px 52px',
            borderRadius: 20,
            background: 'rgba(10,14,22,0.78)',
            border: '4px solid #ff3c50',
            textShadow: '0 4px 0 #000',
            transform: 'translateY(-20px)',
          }}
        >
          如果真能买 你敢坐吗
        </div>
      </AbsoluteFill>
      <SourceCredit />
    </AbsoluteFill>
  );
};

// re-export Sequence for convenience
export {Sequence};
