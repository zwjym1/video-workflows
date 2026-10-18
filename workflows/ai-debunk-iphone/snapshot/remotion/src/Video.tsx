import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import data from './data/shots.json';
import sfx from './data/sfx.json';
import {Subtitles} from './Subtitles';
import {BrandBadge} from './Brand';
import {Danmaku, DM} from './Danmaku';
import {useSubFont} from './Fonts';
import {INK, clamp} from './theme';

export type Props = {hideSubs: boolean; hideExtras: boolean};

type Hole = {kind: string; x: number; y: number; w: number; h: number; r: number; feather?: number};
type Beat = {t: number; img: string; bbox: number[] | null};
type Shot = {id: string; start: number; end: number; from: number; plate: string; holes: Hole[]; clip?: string; beat?: Beat};
const SHOTS = data.shots as Shot[];
const FPS = data.fps;

// 进场方式（沿用 preview 的 TRANSITIONS）：key = 进入的镜头
type Enter = 'hard' | 'reveal' | 'ai_beat' | 'whip' | 'push' | 'lens_push' | 'real_beat';
const ENTER: Record<string, Enter> = {
  '03': 'reveal', '07': 'ai_beat', '08': 'whip', '11': 'ai_beat', '12a': 'push', '12b': 'lens_push',
  '16': 'whip', '17': 'real_beat', '18': 'ai_beat', '19': 'push', '23': 'whip', '25': 'real_beat', '27': 'whip',
};

const DANMAKU: Record<string, DM[]> = {
  '01': [{text: '冲了冲了', y: 300, delay: 4}, {text: '在哪捡？？', y: 420, delay: 16}],
  '02': [{text: '我已经在划了', y: 300, delay: 2}, {text: '冲！！', y: 600, delay: 20}],
};

const ShotView: React.FC<{s: Shot; prev?: Shot; dur: number; hideExtras: boolean}> = ({s, prev, dur, hideExtras}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = ENTER[s.id] ?? 'hard';
  // ---- 进场
  let tx = 0, scale = 1, blur = 0, gray = 0, flash = 0;
  if (enter === 'whip' || enter === 'push') {
    const k = interpolate(f, [0, enter === 'whip' ? 6 : 8], [1, 0], {...clamp, easing: (x) => 1 - Math.pow(1 - x, 3)});
    tx = k * (enter === 'whip' ? 1920 : 1920);
    blur = enter === 'whip' ? k * 14 : k * 4;
  } else if (enter === 'lens_push') {
    scale = interpolate(f, [0, 8], [1.12, 1], {...clamp, easing: (x) => 1 - Math.pow(1 - x, 3)});
  } else if (enter === 'ai_beat') {
    gray = interpolate(f, [0, 8], [1, 0], clamp);
    flash = interpolate(f, [0, 1, 4], [0.5, 0.35, 0], clamp);
  } else if (enter === 'real_beat') {
    scale = interpolate(f, [0, 6], [1.04, 1], clamp);
  } else if (enter === 'reveal') {
    scale = interpolate(f, [0, 5], [1.06, 1], clamp);
  }
  // ---- 揭的那一拍
  const bf = s.beat ? Math.round((s.beat.t - s.start) * fps) : 1e9;
  const sinceBeat = f - bf;
  let shakeX = 0, shakeY = 0, beatFlash = 0;
  if (s.beat && sinceBeat >= 0 && sinceBeat < 8) {
    const a = (1 - sinceBeat / 8) * 10;
    shakeX = Math.sin(sinceBeat * 2.7) * a;
    shakeY = Math.cos(sinceBeat * 3.3) * a * 0.6;
    beatFlash = interpolate(sinceBeat, [0, 1, 4], [0.28, 0.18, 0], clamp);
  }
  const pop = s.beat && sinceBeat >= 0 ? spring({frame: sinceBeat, fps, config: {damping: 9, stiffness: 240}}) : 0;
  const bb = s.beat?.bbox;
  const origin = bb ? `${(bb[0] + bb[2]) / 2}px ${(bb[1] + bb[3]) / 2}px` : 'center';

  return (
    <AbsoluteFill style={{background: INK, overflow: 'hidden'}}>
      {prev && tx > 0 ? (
        <AbsoluteFill style={{transform: `translateX(${tx - 1920}px)`, filter: `blur(${blur}px)`}}>
          <Img src={staticFile(prev.plate)} />
        </AbsoluteFill>
      ) : null}
      <AbsoluteFill style={{transform: `translate(${tx + shakeX}px, ${shakeY}px) scale(${scale})`, filter: `${blur ? `blur(${blur}px) ` : ''}grayscale(${gray})`}}>
        {s.clip
          ? s.holes.map((h, i) => (
              <div key={i} style={{position: 'absolute', left: h.x, top: h.y, width: h.w, height: h.h, borderRadius: h.r, overflow: 'hidden', background: '#000'}}>
                <OffthreadVideo src={staticFile(s.clip!)} muted style={{width: h.w, height: h.h, objectFit: 'cover'}} />
              </div>
            ))
          : null}
        <Img src={staticFile(s.plate)} style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080}} />
        {s.beat && sinceBeat >= 0 ? (
          <Img
            src={staticFile(s.beat.img)}
            style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transformOrigin: origin, transform: `scale(${interpolate(pop, [0, 1], [1.35, 1])})`, opacity: Math.min(1, sinceBeat / 2 + 0.5)}}
          />
        ) : null}
        {!hideExtras && DANMAKU[s.id] ? <Danmaku items={DANMAKU[s.id]} /> : null}
      </AbsoluteFill>
      {flash + beatFlash > 0 ? <AbsoluteFill style={{background: '#fff', opacity: flash + beatFlash}} /> : null}
    </AbsoluteFill>
  );
};

export const IphoneFakeV2: React.FC<Props> = ({hideSubs, hideExtras}) => {
  useSubFont();
  return (
    <AbsoluteFill style={{background: INK}}>
      {SHOTS.map((s, i) => {
        const next = SHOTS[i + 1];
        const dur = (next ? next.from : data.frames) - s.from;
        return (
          <Sequence key={s.id} from={s.from} durationInFrames={dur} name={`镜${s.id}`}>
            <ShotView s={s} prev={SHOTS[i - 1]} dur={dur} hideExtras={hideExtras} />
          </Sequence>
        );
      })}
      {!hideExtras ? <BrandBadge /> : null}
      {!hideSubs ? <Subtitles /> : null}
      <Audio src={staticFile('vo/vo_master.wav')} />
      {sfx.map((x, i) => (
        <Sequence key={`sfx${i}`} from={Math.max(0, Math.round(x.t * FPS))} name={`sfx ${x.file}`} layout="none">
          <Audio src={staticFile(x.file)} volume={x.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
