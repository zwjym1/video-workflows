import React from 'react';
import {useCurrentFrame} from 'remotion';
import {SUB_FONT} from './theme';

// 01/02 示意弹幕：在主画面区（x 528–1392）从右往左飘；不进字幕区（y<900）
export type DM = {text: string; y: number; delay: number};
export const Danmaku: React.FC<{items: DM[]; speed?: number}> = ({items, speed = 9}) => {
  const f = useCurrentFrame();
  return (
    <div data-layer="danmaku" style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
      {items.map((d, i) => {
        const x = 1420 - (f - d.delay) * speed;
        if (f < d.delay) return null;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: d.y, whiteSpace: 'nowrap', fontFamily: `${SUB_FONT}, sans-serif`, fontWeight: 700, fontSize: 40, color: '#fff', WebkitTextStroke: '0px', textShadow: '0 0 4px #000, 2px 2px 0 #000, -2px 2px 0 #000, 2px -2px 0 #000, -2px -2px 0 #000'}}>
            {d.text}
          </div>
        );
      })}
      <div style={{position: 'absolute', left: 548, top: 830, padding: '3px 10px', borderRadius: 6, background: 'rgba(0,0,0,.66)', color: '#FF9F43', fontFamily: `${SUB_FONT}, sans-serif`, fontWeight: 700, fontSize: 20}}>示意弹幕</div>
    </div>
  );
};
