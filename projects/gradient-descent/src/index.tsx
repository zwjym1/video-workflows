import React from 'react';
import {registerRoot, Composition} from 'remotion';
import {Feedback} from './video';
import timings from './timings.json';
import {Continuous} from './continuous';
import edgeTimings from './edge-timings.json';
import {Snappy} from './snappy';
import {Guided} from './guided';
import v3Timings from './v3-timings.json';
import {Concept} from './concept';
import conceptTiming from './concept-timing.json';
import {Story} from './story';
import storyTiming from './story-timing.json';
import {Gradient} from './gradient';
import gradientTiming from './gradient/timing.json';
import {GradientDynamic} from './gradient-dynamic';
import {GradientFocus} from './gradient-focus';
import {GradientSync} from './gradient-sync';
import syncTiming from './gradient-sync/timing.json';
import {GradientStory} from './gradient-story';
import {GradientView} from './gradient-view';
import {DURATION as gradientViewDuration} from './gradient-view/timeline';
import {GradientView2} from './gradient-view-2';
import {DURATION as gradientView2Duration} from './gradient-view-2/timeline';
import {CauchyHook,CAUCHY_DURATION} from './v3-cauchy';
import {ChalkSteps,CHALK_DURATION} from './v3-chalk';
import {GradientV3Full,V3_FULL_DURATION} from './v3-full';
import {GradientV4Full,V4_FULL_DURATION} from './v4-full';
import gradientStoryTiming from './gradient-story/timing.json';
const duration = timings.reduce((sum, item) => sum + item.frames, 0);
registerRoot(() => <><Composition id="Feedback" component={Feedback} width={1920} height={1080} fps={30} durationInFrames={duration}/><Composition id="Continuous" component={Continuous} width={1080} height={1920} fps={30} durationInFrames={edgeTimings.reduce((n,t)=>n+t.frames,0)}/><Composition id="Snappy" component={Snappy} width={1080} height={1920} fps={30} durationInFrames={v3Timings.reduce((n,t)=>n+t.frames,0)}/><Composition id="Guided" component={Guided} width={1080} height={1920} fps={30} durationInFrames={v3Timings.reduce((n,t)=>n+t.frames,0)}/><Composition id="Concept" component={Concept} width={1080} height={1920} fps={30} durationInFrames={conceptTiming.frames}/><Composition id="Story" component={Story} width={1080} height={1920} fps={30} durationInFrames={storyTiming.reduce((n,t)=>n+t.frames,0)}/><Composition id="Gradient" component={Gradient} width={1080} height={1920} fps={30} durationInFrames={gradientTiming.reduce((n,t)=>n+t.frames,0)}/><Composition id="GradientDynamic" component={GradientDynamic} width={1080} height={1920} fps={30} durationInFrames={gradientTiming.reduce((n,t)=>n+t.frames,0)}/><Composition id="GradientFocus" component={GradientFocus} width={1080} height={1920} fps={30} durationInFrames={gradientTiming.reduce((n,t)=>n+t.frames,0)}/><Composition id="GradientSync" component={GradientSync} width={1080} height={1920} fps={30} durationInFrames={syncTiming.frames}/><Composition id="GradientStory" component={GradientStory} width={1080} height={1920} fps={30} durationInFrames={gradientStoryTiming.frames}/><Composition id="GradientViewTest" component={GradientView} width={1080} height={1920} fps={30} durationInFrames={gradientViewDuration}/><Composition id="GradientViewTest2" component={GradientView2} width={1080} height={1920} fps={30} durationInFrames={gradientView2Duration}/><Composition id="V3CauchyHook" component={CauchyHook} width={1080} height={1920} fps={30} durationInFrames={CAUCHY_DURATION}/><Composition id="V3ChalkSteps" component={ChalkSteps} width={1080} height={1920} fps={30} durationInFrames={CHALK_DURATION}/><Composition id="GradientV3Full" component={GradientV3Full} width={1080} height={1920} fps={30} durationInFrames={V3_FULL_DURATION}/><Composition id="GradientV4Full" component={GradientV4Full} width={1080} height={1920} fps={30} durationInFrames={V4_FULL_DURATION}/></>);




