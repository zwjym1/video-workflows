// Master pipeline (cross-platform; uses Remotion's bundled ffmpeg).
//   npm run render:master   -> render picture (muted), then build audio + mux
//   npm run remix-audio     -> audio only: re-render mix from footage-timeline.json, loudnorm, remux into existing master (-c:v copy)
// Options via env: MASTER_OUT (default ../特斯拉Roadster-v3.mp4), RENDER_FLAGS (extra remotion flags), CHROME (browser executable)
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const mode = process.argv[2] ?? 'remix-audio';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
process.chdir(ROOT);
const OUT = path.resolve(process.env.MASTER_OUT ?? '../特斯拉Roadster-v3.mp4');
const VID = path.resolve('out/master-video.mp4'), RAW = path.resolve('out/master-audio-raw.wav'), WAV = path.resolve('out/master-audio.wav');
const npx = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const run = (args) => { console.log('>', args.join(' ')); execFileSync(npx, args, {stdio: 'inherit', shell: process.platform === 'win32'}); };
const q = (s) => (process.platform === 'win32' && /\s|[^\x00-\x7f]/.test(s) ? `"${s}"` : s);
const tl = JSON.parse(fs.readFileSync('src/v3/footage-timeline.json', 'utf8').replace(/^\uFEFF/, ''));
const lufs = tl.audio?.lufs ?? -16;
const extra = (process.env.RENDER_FLAGS ?? '').split(' ').filter(Boolean);
const chrome = process.env.CHROME ? [`--browser-executable=${q(process.env.CHROME)}`] : [];
const t0 = Date.now();
if (mode === 'render:master') {
  run(['remotion', 'render', 'src/index.tsx', 'RoadsterShortV3', q(VID), '--muted', '--codec=h264', '--crf=18', ...chrome, ...extra]);
}
// audio-only render: Remotion skips frame rendering for audio codecs
run(['remotion', 'render', 'src/index.tsx', 'RoadsterShortV3', q(RAW), '--codec=wav', ...chrome]);
run(['remotion', 'ffmpeg', '-y', '-v', 'error', '-i', q(RAW), '-af', `loudnorm=I=${lufs}:TP=-1.5:LRA=11`, '-ar', '48000', '-c:a', 'pcm_s16le', q(WAV)]);
const src = mode === 'render:master' ? VID : (fs.existsSync(OUT) ? OUT : VID);
const tmp = OUT.replace(/\.mp4$/, '.tmp.mp4');
run(['remotion', 'ffmpeg', '-y', '-v', 'error', '-i', q(src), '-i', q(WAV), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-movflags', '+faststart', '-shortest', q(tmp)]);
fs.renameSync(tmp, OUT);
console.log(`\n✔ ${mode} 完成：${OUT}\n  混音音频：${WAV}\n  用时 ${((Date.now() - t0) / 1000).toFixed(1)} s`);
