import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Sequence, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {BrandBadge, SMILEY, fontCss} from './common/theme';
import {OneLineSubtitles} from './common/OneLineSubtitles';
import {SUBS} from './data/subs_v1';
import {CUTS, NAMES, ShotHost, TOTAL} from './Shots';
export const FPS = 30;
export const FILM_FRAMES = Math.round(TOTAL * FPS);
const fr = (s: number) => Math.round(s * FPS);
const useFont = () => {
  const [h] = useState(() => delayRender('font'));
  useEffect(() => { const f = new FontFace('Smiley', `url(${staticFile('fonts/SmileySans-Oblique.ttf')})`); f.load().then((ff) => { (document as any).fonts.add(ff); continueRender(h); }).catch(() => continueRender(h)); }, [h]);
};
const Subs: React.FC = () => { const f = useCurrentFrame(); const {fps} = useVideoConfig(); return <OneLineSubtitles t={f / fps} subs={SUBS} fontFamily={SMILEY} maxFont={84} />; };
/** v6c：山东镜（城市夜景亮底）字幕下垫 40% 暗条 */
const SubBar: React.FC = () => { const f = useCurrentFrame(); const {fps} = useVideoConfig(); const t = f / fps; const k = NAMES.indexOf('c09_jn_sd');
  if (k < 0 || t < CUTS[k] || t >= CUTS[k + 1]) return null;
  return <div data-layer="subbar" style={{position: 'absolute', left: 30, width: 1020, top: 1608, height: 124, borderRadius: 22, background: 'rgba(0,0,0,.4)', zIndex: 79}} />; };
/** 全片角落小水印「AI配音」（右下，半透明） */
const AiMark: React.FC = () => <div data-layer="aimark" style={{position: 'absolute', right: 36, top: 1788, opacity: 0.5, zIndex: 75, fontFamily: SMILEY, fontSize: 24, lineHeight: '30px', color: '#efe8da', WebkitTextStroke: '3px rgba(0,0,0,.6)', paintOrder: 'stroke fill', letterSpacing: 1}}>AI配音</div>;
export const Film: React.FC = () => { useFont();
  return <AbsoluteFill style={{background: '#0c0d12'}}><style>{fontCss}</style>
    {CUTS.map((_, i) => { const a = fr(CUTS[i]); const b = i < CUTS.length - 1 ? fr(CUTS[i + 1]) : FILM_FRAMES;
      return <Sequence key={i} from={a} durationInFrames={b - a} name={`镜${i + 1} ${NAMES[i]}`} premountFor={15}><ShotHost i={i} /></Sequence>; })}
    <SubBar /><Subs /><BrandBadge startAt={-36} /><AiMark />
  </AbsoluteFill>; };
