import {registerRoot, Composition} from 'remotion';
import {RoadsterShort, DURATION_FRAMES, FPS} from './RoadsterShort';
import {Transition3D} from './Transition3D';
import {TA_FRAMES, TB_FRAMES} from './timing';
import {RoadsterShortV2, V2_FRAMES} from './v2/Short';
import {RoadsterShortV3, V3_FRAMES} from './v3/Short';

const Root: React.FC = () => (
  <>
    <Composition id="RoadsterShortV3" component={RoadsterShortV3} durationInFrames={V3_FRAMES} fps={FPS} width={1920} height={1080} defaultProps={{withVoice: true}} />
    <Composition id="RoadsterShortV2" component={RoadsterShortV2} durationInFrames={V2_FRAMES} fps={FPS} width={1920} height={1080} />
    <Composition
      id="RoadsterShort"
      component={RoadsterShort}
      durationInFrames={DURATION_FRAMES}
      fps={FPS}
      width={1920}
      height={1080}
    />
    {/* Standalone extended transitions for still sampling */}
    <Composition
      id="TA"
      component={Transition3D}
      defaultProps={{v: 'A' as const, durationInFrames: TA_FRAMES, showChrome: true}}
      durationInFrames={TA_FRAMES}
      fps={FPS}
      width={1920}
      height={1080}
    />
    <Composition
      id="TB"
      component={Transition3D}
      defaultProps={{v: 'B' as const, durationInFrames: TB_FRAMES, showChrome: true}}
      durationInFrames={TB_FRAMES}
      fps={FPS}
      width={1920}
      height={1080}
    />
  </>
);

registerRoot(Root);
