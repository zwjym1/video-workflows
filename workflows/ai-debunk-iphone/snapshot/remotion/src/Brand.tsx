import React from 'react';
import {Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {clamp} from './theme';

// 开场小印章盖下 → 停在右上角当角标（60% 不透明度）。无片尾卡。
const SIZE = 78, RIGHT = 40, TOP = 34;
export const BrandBadge: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const st = spring({frame: f - 4, fps, config: {damping: 10, stiffness: 210}});
  const scale = f < 4 ? 0 : interpolate(st, [0, 1], [2.4, 1]);
  const op = f < 4 ? 0 : interpolate(f, [4, 8, 26, 40], [0, 1, 1, 0.6], clamp);
  const rot = interpolate(st, [0, 1], [-18, -6]);
  return (
    <div data-layer="brand" style={{position: 'absolute', right: RIGHT, top: TOP, width: SIZE, height: SIZE, opacity: op, transform: `scale(${scale}) rotate(${rot}deg)`, transformOrigin: 'center'}}>
      <Img src={staticFile('brand/seal_t.png')} style={{width: SIZE, height: SIZE, filter: 'drop-shadow(0 3px 6px rgba(0,0,0,.5))'}} />
    </div>
  );
};
