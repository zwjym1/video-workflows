import React from 'react';
import {registerRoot,Composition} from 'remotion';
import {PiLesson,PiChapter,TOTAL,FPS,chapterFrames} from './PiLesson';
registerRoot(()=><>
 <Composition id="PiLesson" component={PiLesson} width={1920} height={1080} fps={FPS} durationInFrames={TOTAL}/>
 {[0,1,2,3,4,5,6].map(c=>{const {dur}=chapterFrames(c);const Comp:React.FC=()=><PiChapter chapter={c}/>;return <Composition key={c} id={`PiCh${c}`} component={Comp} width={1920} height={1080} fps={FPS} durationInFrames={dur}/>;})}
</>);
