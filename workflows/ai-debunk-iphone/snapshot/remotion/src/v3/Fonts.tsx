import React from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';
import {FONT} from './theme';

let p: Promise<void> | null = null;
export const useV3Font = () => {
  const [h] = React.useState(() => delayRender('v3-font'));
  React.useEffect(() => {
    if (!p) {
      const ff = new FontFace(FONT, `url(${staticFile('v3/fonts/NotoSansSC-Bold-v3.otf')})`, {weight: '700'});
      p = ff.load().then((f) => {
        document.fonts.add(f);
      });
    }
    p.then(() => continueRender(h)).catch(() => continueRender(h));
  }, [h]);
};
