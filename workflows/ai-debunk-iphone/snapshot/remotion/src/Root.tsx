import React from 'react';
import {Composition} from 'remotion';
import {IphoneFakeV2, Props} from './Video';
import {IphoneFakeV3, V3Props} from './v3/V3';
import data from './data/shots.json';
import v3 from './v3/data/v3.json';
import {IphoneFakeV3d, V3dProps} from './v3d/V3d';
import v3d from './v3d/data/v3d.json';
import {IphoneFakeV3e, V3eProps} from './v3e/V3e';
import v3e from './v3e/data/v3e.json';
import {IphoneFakeV3f, V3fProps} from './v3f/V3f';
import v3f from './v3f/data/v3f.json';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="IphoneFakeV2"
      component={IphoneFakeV2}
      durationInFrames={data.frames}
      fps={data.fps}
      width={1920}
      height={1080}
      defaultProps={{hideSubs: false, hideExtras: false} satisfies Props}
    />
    <Composition
      id="IphoneFakeV3"
      component={IphoneFakeV3}
      durationInFrames={v3.frames}
      fps={v3.fps}
      width={1920}
      height={1080}
      defaultProps={{hideSubs: false, hideExtras: false} satisfies V3Props}
    />
    <Composition
      id="IphoneFakeV3d"
      component={IphoneFakeV3d}
      durationInFrames={v3d.frames}
      fps={v3d.fps}
      width={1920}
      height={1080}
      defaultProps={{hideSubs: false, hideExtras: false} satisfies V3dProps}
    />
    <Composition
      id="IphoneFakeV3e"
      component={IphoneFakeV3e}
      durationInFrames={v3e.frames}
      fps={v3e.fps}
      width={1920}
      height={1080}
      defaultProps={{hideSubs: false, hideExtras: false} satisfies V3eProps}
    />
      <Composition
      id="IphoneFakeV3f"
      component={IphoneFakeV3f}
      durationInFrames={v3f.frames}
      fps={v3f.fps}
      width={1920}
      height={1080}
      defaultProps={{hideSubs: false, hideExtras: false} satisfies V3fProps}
    />
  </>
);
