// 渲染检查帧：node scripts/stills.mjs <outDir>
// 每镜关键帧（beat 镜头取揭之后 10 帧）× 三种图层（all / nosub / bare），转场首中尾帧（all）
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
const out = process.argv[2] || 'stills';
fs.mkdirSync(out, {recursive: true});
const data = JSON.parse(fs.readFileSync('src/data/shots.json', 'utf8'));
const shots = data.shots;
const jobs = [];
shots.forEach((s, i) => {
  const end = (shots[i + 1]?.from ?? data.frames) - 1;
  let key = Math.round((s.from + end) / 2);
  if (s.beat) key = Math.min(end - 2, Math.round(s.beat.t * data.fps) + 10);
  for (const v of ['all', 'nosub', 'bare']) jobs.push({name: `key_${s.id}_${v}`, frame: key, v});
  if (i > 0) for (const [tag, d] of [['a', -1], ['b', 2], ['c', 7]]) jobs.push({name: `tr_${shots[i - 1].id}-${s.id}_${tag}`, frame: s.from + d, v: 'all'});
});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const props = {all: {hideSubs: false, hideExtras: false}, nosub: {hideSubs: true, hideExtras: false}, bare: {hideSubs: true, hideExtras: true}};
const comps = {};
for (const v of Object.keys(props)) comps[v] = await selectComposition({serveUrl, id: 'IphoneFakeV2', inputProps: props[v]});
const index = [];
for (const j of jobs) {
  const output = path.join(out, `${j.name}.png`);
  await renderStill({serveUrl, composition: comps[j.v], frame: j.frame, output, inputProps: props[j.v], imageFormat: 'png', browserExecutable: process.env.REMOTION_BROWSER_EXECUTABLE || null});
  index.push({...j, file: output});
}
fs.writeFileSync(path.join(out, 'index.json'), JSON.stringify(index, null, 1));
console.log('stills', index.length);
