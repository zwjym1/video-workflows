// 盒上渲染（PC 离线回退）：静音画面 → out/film_silent.mp4；音轨由 mux 步骤 -c:a copy 盒上编好的 AAC
import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import path from 'path';
const out = process.argv[2] || 'out/render_v1'; const frameRange = process.argv[3] ? process.argv[3].split('-').map(Number) : null;
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const chromiumOptions = {gl: 'swangle'};
const comp = await selectComposition({serveUrl, id: 'JellyFilm', chromiumOptions});
console.log('frames', comp.durationInFrames);
let last = -1; const t0 = Date.now();
await renderMedia({composition: comp, serveUrl, codec: 'h264', crf: 18, pixelFormat: 'yuv420p', imageFormat: 'jpeg', jpegQuality: 93, muted: true,
  outputLocation: `${out}/film_silent.mp4`, chromiumOptions, concurrency: 6, frameRange: frameRange || undefined,
  onProgress: ({progress}) => { const p = Math.floor(progress * 100); if (p >= last + 5) { last = p; console.log(`progress ${p}% ${((Date.now() - t0) / 1000).toFixed(0)}s`); } }});
for (const [id, f] of [['CoverV', 'cover_v_1080x1920.png'], ['CoverH', 'cover_h_1440x1080.png']]) {
  const c = await selectComposition({serveUrl, id, chromiumOptions}); await renderStill({composition: c, serveUrl, output: `${out}/${f}`, frame: 0, chromiumOptions}); }
console.log('DONE', ((Date.now() - t0) / 1000).toFixed(0), 's');
