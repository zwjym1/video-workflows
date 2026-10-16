import React from 'react';
import {Audio,Sequence,staticFile} from 'remotion';
import {FPS,at,ss,se,S} from './timing';
import {THINK} from './ui';
const hits=[
 {t:at(0,'车轮'),file:'sfx/sync-sweep.wav',vol:.35},
 {t:at(1,'三倍'),file:'sfx/sync-tap.wav',vol:.4},
 {t:at(1,'一小截'),file:'sfx/sync-tap.wav',vol:.45},
 {t:at(6,'绳子'),file:'sfx/sync-paper.wav',vol:.4},
 {t:at(8,'三点一四'),file:'sfx/sync-tap.wav',vol:.4},
 {t:at(14,'圆周率'),file:'sfx/sync-arrow.wav',vol:.4},
 {t:at(18,'周三径一'),file:'sfx/sync-tap.wav',vol:.45},
 {t:at(21,'六边形'),file:'sfx/sync-paper.wav',vol:.35},
 {t:at(31,'切开'),file:'sfx/sync-sweep.wav',vol:.4},
 {t:at(34,'三点一零五八'),file:'sfx/sync-tap.wav',vol:.3},
 {t:at(35,'三点一三二六'),file:'sfx/sync-tap.wav',vol:.3},
 {t:at(36,'三点一三九四'),file:'sfx/sync-tap.wav',vol:.3},
 {t:at(37,'三点一四一零'),file:'sfx/sync-tap.wav',vol:.3},
 {t:at(38,'三点一四一五'),file:'sfx/sync-tap.wav',vol:.35},
 {t:at(49,'割圆术'),file:'sfx/sync-arrow.wav',vol:.45},
 {t:at(62,'祖冲之'),file:'sfx/sync-paper.wav',vol:.4},
 {t:at(65,'摆满'),file:'sfx/sync-tap.wav',vol:.4},
 {t:at(67,'七位'),file:'sfx/sync-arrow.wav',vol:.5},
 {t:at(70,'一粒沙子'),file:'sfx/sync-tap.wav',vol:.4},
 {t:at(76,'三百一十四万亿'),file:'sfx/sync-arrow.wav',vol:.5},
 {t:at(86,'三月十四日'),file:'sfx/sync-paper.wav',vol:.4},
];
export const Sfx:React.FC=()=><>
 {hits.map((h,i)=><Sequence key={i} from={Math.max(0,Math.round(h.t*FPS)-2)}><Audio src={staticFile(h.file)} volume={h.vol}/></Sequence>)}
 {THINK.map((i,k)=><Sequence key={'th'+k} from={Math.round(se(i)*FPS)}><Audio src={staticFile('sfx/sync-tap.wav')} volume={.25}/></Sequence>)}
</>;
