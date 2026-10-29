import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'path';
const times = process.argv.slice(3).map(Number); const outDir = process.argv[2];
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const comp = await selectComposition({serveUrl, id: 'JellyFilm', chromiumOptions: {gl: 'swangle'}});
for (const s of times) { const frame = Math.min(comp.durationInFrames - 1, Math.round(s * 30));
  await renderStill({composition: comp, serveUrl, output: `${outDir}/f_${s.toFixed(2)}.png`, frame, chromiumOptions: {gl: 'swangle'}}); console.log('ok', s); }
const cov = await selectComposition({serveUrl, id: 'CoverV'});
await renderStill({composition: cov, serveUrl, output: `${outDir}/cover_v.png`, frame: 0});
const ch = await selectComposition({serveUrl, id: 'CoverH'});
await renderStill({composition: ch, serveUrl, output: `${outDir}/cover_h.png`, frame: 0}); console.log('covers');
