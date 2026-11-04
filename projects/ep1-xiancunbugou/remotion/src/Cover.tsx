import React from 'react';
import {AbsoluteFill} from 'remotion';
import {FontFace, P, FONT, PaperBg, m} from './kit';
import {BoltSprite, Dust} from './sprites';
import {GpuCard, Kid} from './Motion';
const sh = 'var(--t-shadow-accent-8)';
const T: React.FC<{s: number; color: string; children: React.ReactNode}> = ({s, color, children}) => <div style={{fontFamily: FONT, fontSize: s, color, lineHeight: 1.12}}>{children}</div>;
export const Cover: React.FC<{v: boolean}> = ({v}) => (
  <AbsoluteFill><FontFace /><PaperBg /><Dust n={18} seed={4} />
    <div style={{position: 'absolute', left: v ? 70 : 80, top: v ? 150 : 70, right: v ? 70 : 80}}>
      <div style={{display: 'inline-flex', gap: 18, alignItems: 'center', background: P.plate, padding: '12px 30px', boxShadow: sh}}><BoltSprite px={v ? 8 : 7} /><T s={v ? 92 : 78} color={P.gold}>FlashAttention</T></div>
      <div style={{marginTop: v ? 60 : 36}}>
        <T s={v ? 118 : 104} color={P.text}>一行参数</T>
        <T s={v ? 118 : 104} color={P.text}>凭什么让注意力</T>
        <T s={v ? 140 : 120} color={P.heart}>快好几倍？</T>
      </div>
      <div style={{display: 'inline-block', marginTop: v ? 44 : 26, background: P.orange, padding: '8px 24px', boxShadow: sh}}><T s={v ? 52 : 44} color={P.white}>不是算得慢，是搬得慢</T></div>
    </div>
    <div style={{position: 'absolute', left: v ? 80 : 600, top: v ? 1240 : 690}}><GpuCard w={v ? 560 : 420} /></div>
    <div style={{position: 'absolute', left: v ? 660 : 1070, top: v ? 1150 : 400, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <div style={{background: P.bubble, border: `5px solid ${P.stroke}`, padding: '6px 16px', boxShadow: sh, marginBottom: 12}}><T s={v ? 44 : 38} color={P.text}>显存又爆了…</T></div>
      <Kid h={v ? 560 : 520} poses={[[0, v ? 'point' : 'think']]} flip={v} />
    </div>
    <div style={{position: 'absolute', right: 30, top: 24, background: m('hud-bg'), padding: '8px 18px', boxShadow: sh}}><T s={40} color={P.white}><span style={{color: P.heart}}>♥♥♥</span> 显存不够</T></div>
  </AbsoluteFill>
);
