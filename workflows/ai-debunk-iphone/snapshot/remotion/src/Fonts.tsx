import React from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';
import {SUB_FONT} from './theme';

let p: Promise<void> | null = null;
export const useSubFont = () => {
  const [h] = React.useState(() => delayRender('sub-font'));
  React.useEffect(() => {
    if (!p) {
      const ff = new FontFace(SUB_FONT, `url(${staticFile('fonts/NotoSansSC-Bold-sub.otf')})`, {weight: '700'});
      p = ff.load().then((f) => {
        document.fonts.add(f);
      });
    }
    p.then(() => continueRender(h)).catch(() => continueRender(h));
  }, [h]);
};
