// 封面：Atumu 山西忻州实拍（10月23日 长征六号改火箭云）+ 标题；角注为素材署名
import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {BrandBadge, CINNABAR, PAPER, SMILEY, fontCss} from './common/theme';
const T: React.CSSProperties = {fontFamily: SMILEY, fontWeight: 700, color: PAPER, WebkitTextStroke: '12px #000', paintOrder: 'stroke fill'};
const Note: React.FC = () => <div style={{position: 'absolute', left: 36, bottom: 40, fontFamily: SMILEY, fontSize: 30, color: 'rgba(239,232,218,.85)', WebkitTextStroke: '4px #000', paintOrder: 'stroke fill'}}>实拍：Atumu · 山西忻州 · 10月23日</div>;
export const CoverV: React.FC = () => <AbsoluteFill style={{background: '#05070f', overflow: 'hidden'}}><style>{fontCss}</style>
  <Img src={staticFile('img/cover_v.jpg')} style={{width: 1080, height: 1920}} />
  <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0) 62%, rgba(0,0,0,.5) 100%)'}} />
  <div style={{...T, position: 'absolute', top: 1200, width: '100%', textAlign: 'center'}}>
    <div style={{fontSize: 104}}>天都黑了</div>
    <div style={{fontSize: 150, color: '#ffe9c4', marginTop: 6}}>这只<span style={{color: CINNABAR}}>火箭水母</span></div>
    <div style={{fontSize: 120}}>为啥还在发光？</div>
  </div>
  <Note /><BrandBadge startAt={-100} />
</AbsoluteFill>;
export const CoverH: React.FC = () => <AbsoluteFill style={{background: '#05070f', overflow: 'hidden'}}><style>{fontCss}</style>
  <Img src={staticFile('img/cover_h.jpg')} style={{width: 1440, height: 1080}} />
  <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0) 45%, rgba(0,0,0,.6) 100%)'}} />
  <div style={{...T, position: 'absolute', left: 0, width: '100%', top: 700, textAlign: 'center'}}>
    <div style={{fontSize: 120, color: '#ffe9c4'}}>天黑了，<span style={{color: CINNABAR}}>火箭水母</span>为啥还亮？</div>
  </div>
  <Note /><BrandBadge startAt={-100} />
</AbsoluteFill>;
