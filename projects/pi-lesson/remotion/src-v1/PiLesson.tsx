import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile} from 'remotion';
import {TOTAL,FPS,CH,chapterFrames,DUR} from './timing';
import {OffsetCtx,Caption,ThinkCard,ChapterTag,useT} from './ui';
import {Ch0} from './ch0';
import {Ch1} from './ch1';
import {Ch2} from './ch2';
import {Ch3} from './ch3';
import {Ch4} from './ch4';
import {Ch5} from './ch5';
import {Ch6} from './ch6';
import {Sfx} from './sfx';
const CHAPTERS=[Ch0,Ch1,Ch2,Ch3,Ch4,Ch5,Ch6];
const Overlay:React.FC=()=>{const t=useT();return <><ChapterTag t={t}/><Caption t={t}/><ThinkCard t={t}/></>;};
export const PiLesson:React.FC=()=><AbsoluteFill style={{background:'#FFF8EC'}}>
 <Audio src={staticFile('pi-lesson-voice.mp3')}/>
 <Sfx/>
 {CHAPTERS.map((Comp,c)=>{const {from,dur}=chapterFrames(c);return <Sequence key={c} from={from} durationInFrames={dur}><OffsetCtx.Provider value={from}><Comp/><Overlay/></OffsetCtx.Provider></Sequence>;})}
</AbsoluteFill>;
export const PiChapter:React.FC<{chapter:number}> =({chapter})=>{
 const Comp=CHAPTERS[chapter];const {from,dur}=chapterFrames(chapter);
 return <AbsoluteFill style={{background:'#FFF8EC'}}>
  <Audio src={staticFile('pi-lesson-voice.mp3')} trimBefore={from} trimAfter={from+dur}/>
  <OffsetCtx.Provider value={from}><Comp/><Overlay/></OffsetCtx.Provider>
 </AbsoluteFill>;
};
export {TOTAL,FPS,DUR,chapterFrames};
