import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

export const F = '"Noto Sans CJK SC","Noto Sans SC","Source Han Sans SC",sans-serif';
export const W = 1920;
export const H = 1080;
export const cl = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

export const stripPunct = (t: string) =>
  t.replace(/[，。？、！：；,.!?;:]/g, ' ').replace(/\s+/g, ' ').trim();

/** Bottom-safe one-line subtitle. No punctuation. */
export const Subtitle: React.FC<{text: string; opacity?: number}> = ({text, opacity = 1}) => {
  if (!text || opacity <= 0) return null;
  const display = stripPunct(text);
  return (
    <div
      style={{
        position: 'absolute',
        left: 80,
        right: 80,
        bottom: 88,
        textAlign: 'center',
        opacity,
        pointerEvents: 'none',
        zIndex: 40,
      }}
    >
      <span
        style={{
          display: 'inline-block',
          fontFamily: F,
          fontWeight: 900,
          fontSize: 52,
          color: '#fff',
          lineHeight: 1.25,
          padding: '12px 28px',
          borderRadius: 12,
          background: 'rgba(0,0,0,0.55)',
          textShadow: '0 3px 0 #000, 0 0 16px rgba(0,0,0,0.9)',
          WebkitTextStroke: '1.5px rgba(0,0,0,0.45)',
          maxWidth: '100%',
        }}
      >
        {display}
      </span>
    </div>
  );
};

export const SourceCredit: React.FC<{extra?: string}> = ({extra}) => (
  <div
    style={{
      position: 'absolute',
      top: 36,
      left: 44,
      fontFamily: F,
      fontSize: 26,
      color: 'rgba(255,255,255,0.7)',
      textShadow: '0 2px 6px #000',
      zIndex: 35,
      pointerEvents: 'none',
    }}
  >
    {extra ? `${extra} · ` : ''}画面来源：Tesla
  </div>
);

export const Chip: React.FC<{text: string; color?: string; top?: number; opacity?: number}> = ({
  text,
  color = 'linear-gradient(90deg,#e31937,#ff5a3c)',
  top = 44,
  opacity = 1,
}) => (
  <div
    style={{
      position: 'absolute',
      top,
      left: 0,
      right: 0,
      textAlign: 'center',
      opacity,
      zIndex: 36,
      pointerEvents: 'none',
    }}
  >
    <span
      style={{
        fontFamily: F,
        fontWeight: 900,
        fontSize: 44,
        color: '#fff',
        padding: '12px 32px',
        borderRadius: 16,
        background: color,
        boxShadow: '0 8px 28px rgba(0,0,0,0.35)',
      }}
    >
      {text}
    </span>
  </div>
);

export const ModelDisclaimer: React.FC<{opacity?: number}> = ({opacity = 1}) => (
  <div
    style={{
      position: 'absolute',
      top: 118,
      left: 0,
      right: 0,
      textAlign: 'center',
      fontFamily: F,
      fontSize: 26,
      color: 'rgba(255,255,255,0.6)',
      opacity,
      zIndex: 36,
      pointerEvents: 'none',
    }}
  >
    示意模型 非官方
  </div>
);

export const Pill: React.FC<{
  text: string;
  color: string;
  side: 'left' | 'right';
  opacity: number;
  top?: number;
}> = ({text, color, side, opacity, top = 820}) => {
  if (opacity <= 0) return null;
  return (
    <div
      style={{
        position: 'absolute',
        top,
        [side]: 110,
        opacity,
        transform: `translateY(${(1 - opacity) * 18}px)`,
        padding: '12px 24px',
        borderRadius: 40,
        background: 'rgba(12,16,24,0.75)',
        border: `3px solid ${color}`,
        color: '#fff',
        fontFamily: F,
        fontWeight: 700,
        fontSize: 36,
        whiteSpace: 'nowrap',
        boxShadow: `0 0 22px ${color}55`,
        zIndex: 37,
        pointerEvents: 'none',
      }}
    >
      <span
        style={{
          display: 'inline-block',
          width: 14,
          height: 14,
          borderRadius: 7,
          background: color,
          marginRight: 12,
          verticalAlign: 'middle',
        }}
      />
      {text}
    </div>
  );
};

export const Stamp: React.FC<{lines: string[]; colors?: string[]; opacity?: number}> = ({
  lines,
  colors = ['#ff5050', '#50c8ff'],
  opacity = 1,
}) => (
  <AbsoluteFill
    style={{
      justifyContent: 'center',
      alignItems: 'center',
      gap: 28,
      opacity,
      background: 'rgba(0,0,0,0.35)',
      zIndex: 30,
    }}
  >
    {lines.map((line, i) => (
      <div
        key={i}
        style={{
          fontFamily: F,
          fontWeight: 900,
          fontSize: 92,
          color: colors[i % colors.length],
          padding: '22px 48px',
          borderRadius: 20,
          background: 'rgba(10,14,22,0.85)',
          border: `5px solid ${colors[i % colors.length]}`,
          textShadow: '0 4px 0 #000',
        }}
      >
        {line}
      </div>
    ))}
  </AbsoluteFill>
);

export const DanmakuCards: React.FC<{cards: string[]; opacity?: number}> = ({cards, opacity = 1}) => {
  const positions = [
    [120, 200],
    [980, 260],
    [220, 400],
    [1100, 460],
    [160, 580],
    [900, 620],
    [480, 320],
  ];
  const colors = ['#ff78a0', '#78dcff', '#ffd25a', '#a0ffb4', '#ffa064', '#b4a0ff', '#ffffff'];
  return (
    <AbsoluteFill style={{opacity, background: 'rgba(0,0,0,0.4)', zIndex: 28}}>
      {cards.map((text, i) => {
        const [x, y] = positions[i % positions.length];
        const c = colors[i % colors.length];
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: Math.min(y, 720),
              padding: '12px 22px 12px 36px',
              borderRadius: 28,
              background: 'rgba(12,16,24,0.82)',
              border: `3px solid ${c}`,
              color: '#fff',
              fontFamily: F,
              fontWeight: 700,
              fontSize: 34,
              boxShadow: `0 0 18px ${c}44`,
            }}
          >
            <span
              style={{
                position: 'absolute',
                left: 12,
                top: '50%',
                transform: 'translateY(-50%)',
                width: 12,
                height: 12,
                borderRadius: 6,
                background: c,
              }}
            />
            {text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

export const FactCard: React.FC<{
  title: string;
  subtitle?: string;
  opacity?: number;
}> = ({title, subtitle, opacity = 1}) => (
  <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', opacity, zIndex: 30}}>
    <div
      style={{
        minWidth: 700,
        maxWidth: 1100,
        padding: '36px 56px',
        borderRadius: 24,
        background: 'rgba(10,14,22,0.88)',
        border: '4px solid #ff5a3c',
        textAlign: 'center',
        transform: 'translateY(-40px)',
      }}
    >
      <div style={{fontFamily: F, fontWeight: 900, fontSize: 68, color: '#ffdcb4'}}>{title}</div>
      {subtitle ? (
        <div style={{fontFamily: F, fontSize: 36, color: '#c8c8c8', marginTop: 16}}>{subtitle}</div>
      ) : null}
    </div>
  </AbsoluteFill>
);

export const InfoCard: React.FC<{
  title: string;
  items: {label: string; color: string}[];
  opacity?: number;
}> = ({title, items, opacity = 1}) => (
  <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', opacity, zIndex: 30}}>
    <div
      style={{
        width: 920,
        padding: '36px 40px 44px',
        borderRadius: 24,
        background: 'rgba(10,14,22,0.9)',
        border: '3px solid #5ab4ff',
        transform: 'translateY(-36px)',
      }}
    >
      <div style={{fontFamily: F, fontWeight: 900, fontSize: 44, color: '#5ac8ff', marginBottom: 24}}>
        {title}
      </div>
      {items.map((it, i) => (
        <div key={i} style={{display: 'flex', alignItems: 'center', marginBottom: 18}}>
          <span
            style={{
              width: 16,
              height: 16,
              borderRadius: 8,
              background: it.color,
              marginRight: 18,
              flexShrink: 0,
            }}
          />
          <span style={{fontFamily: F, fontWeight: 700, fontSize: 38, color: '#fff'}}>{it.label}</span>
        </div>
      ))}
    </div>
  </AbsoluteFill>
);

/** Word-synced subtitle from caption cues. */
export const SyncedSubs: React.FC<{
  cues: {text: string; start: number; end: number}[];
  fps: number;
}> = ({cues, fps}) => {
  const frame = useCurrentFrame();
  const t = frame / fps;
  const cue = cues.find((c) => t >= c.start && t < c.end);
  if (!cue) return null;
  const fade = interpolate(t, [cue.start, cue.start + 0.08, cue.end - 0.06, cue.end], [0, 1, 1, 0], cl);
  return <Subtitle text={cue.text} opacity={fade} />;
};
