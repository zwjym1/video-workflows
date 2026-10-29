import React from 'react';
import {Composition, Still} from 'remotion';
import {CoverH, CoverV} from './Cover';
import {FPS, W, H} from './common/theme';
import {Film, FILM_FRAMES} from './Film';
export const RemotionRoot: React.FC = () => <>
  <Composition id="JellyFilm" component={Film} durationInFrames={FILM_FRAMES} fps={FPS} width={W} height={H} />
  <Still id="CoverV" component={CoverV} width={1080} height={1920} />
  <Still id="CoverH" component={CoverH} width={1440} height={1080} />
</>;
