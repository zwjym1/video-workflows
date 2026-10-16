import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {TOTAL,FPS,chapterFrames,DUR} from './timing';
import {Defs} from './mat';
import {Background} from './bg';
import {elementsAt} from './scenes';
const Frame:React.FC<{off:number}>=({off})=>{const t=(useCurrentFrame()+off)/FPS;const els=elementsAt(t);
 return <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}><Defs/><Background t={t}/>
  {els.map(e=><g key={e.id} opacity={Math.min(1,e.a)}>{e.draw()}</g>)}</svg>;};
export const PiLesson:React.FC=()=><AbsoluteFill style={{background:'#000'}}><Audio src={staticFile('pi-lesson-voice.mp3')}/><Frame off={0}/></AbsoluteFill>;
export const PiChapter:React.FC<{chapter:number}>=({chapter})=>{const {from,dur}=chapterFrames(chapter);
 return <AbsoluteFill style={{background:'#000'}}><Audio src={staticFile('pi-lesson-voice.mp3')} trimBefore={from} trimAfter={from+dur}/><Frame off={from}/></AbsoluteFill>;};
export {TOTAL,FPS,DUR,chapterFrames};
