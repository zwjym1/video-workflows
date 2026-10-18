// node scripts/v3/stills_v3.mjs <outDir> <scale> frame1 frame2 ...   （帧号；不给则每镜中点）
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
const [out = 'stills_v3', scale = '0.5', ...fr] = process.argv.slice(2);
fs.mkdirSync(out, {recursive: true});
const CID = process.env.COMP || 'IphoneFakeV3'; const JP = process.env.JSONP || 'src/v3/data/v3.json';
const d = JSON.parse(fs.readFileSync(JP, 'utf8'));
let frames = fr.map(Number);
if (!frames.length) frames = d.shots.map((s) => Math.round(((s.t0 + s.t1) / 2) * d.fps));
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const comp = await selectComposition({serveUrl, id: CID, inputProps: {hideSubs: false, hideExtras: false}});
for (const f of frames) {
  const output = path.join(out, `f${String(f).padStart(4, '0')}.png`);
  await renderStill({serveUrl, composition: comp, frame: f, output, scale: Number(scale), imageFormat: 'png', inputProps: {hideSubs: false, hideExtras: false}, browserExecutable: process.env.REMOTION_BROWSER_EXECUTABLE || null});
}
console.log('stills', frames.length);
