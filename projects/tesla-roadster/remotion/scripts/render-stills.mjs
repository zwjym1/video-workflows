#!/usr/bin/env node
/**
 * Render keyframe stills for EVERY shot + transition start/mid/end.
 * Does NOT full-render the master.
 */
import {execSync} from 'node:child_process';
import {mkdirSync, writeFileSync, existsSync} from 'node:fs';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const FRAMES = join(ROOT, 'frames');
const SHEETS = join(ROOT, 'sheets');
mkdirSync(FRAMES, {recursive: true});
mkdirSync(SHEETS, {recursive: true});

const FPS = 30;
const SHOTS = {
  S01: {from: 0, to: 96},
  S02: {from: 96, to: 191},
  S03: {from: 191, to: 307},
  S04: {from: 307, to: 393},
  TA: {from: 393, to: 855},
  TB: {from: 855, to: 1408},
  S08: {from: 1408, to: 1537},
  S09: {from: 1537, to: 1836},
  S10: {from: 1836, to: 1915},
};
const TA_FRAMES = SHOTS.TA.to - SHOTS.TA.from;
const TB_FRAMES = SHOTS.TB.to - SHOTS.TB.from;

function phases(D) {
  const liveEnd = Math.min(Math.round(D * 0.22), 105);
  const freezeStart = liveEnd;
  const threeIn1 = freezeStart + 38;
  const matchEnd = Math.round(D * 0.32);
  const xray0 = Math.round(D * 0.36);
  const xray1 = Math.round(D * 0.48);
  const flow0 = Math.round(D * 0.52);
  const flow1 = Math.round(D * 0.62);
  const call1 = Math.round(D * 0.7);
  return {liveEnd, freezeStart, threeIn1, matchEnd, xray0, xray1, flow0, flow1, call1};
}

const PA = phases(TA_FRAMES);
const PB = phases(TB_FRAMES);

/** Absolute frame + label for RoadsterShort composition */
const KEYS = [
  // S01
  {name: 'S01_hook_mid', frame: SHOTS.S01.from + 30},
  // S02
  {name: 'S02_not_vfx_mid', frame: SHOTS.S02.from + 50},
  // S03
  {name: 'S03_danmaku_mid', frame: SHOTS.S03.from + 40},
  // S04
  {name: 'S04_two_systems_mid', frame: SHOTS.S04.from + 30},
  // TA start / mid / end phases (absolute = TA.from + local)
  {name: 'TA_start_live', frame: SHOTS.TA.from + Math.max(5, Math.floor(PA.liveEnd * 0.4))},
  {name: 'TA_freeze', frame: SHOTS.TA.from + PA.freezeStart + 8},
  {name: 'TA_crossfade', frame: SHOTS.TA.from + PA.threeIn1 + 4},
  {name: 'TA_matched', frame: SHOTS.TA.from + PA.matchEnd + 4},
  {name: 'TA_xray', frame: SHOTS.TA.from + Math.floor((PA.xray0 + PA.xray1) / 2)},
  {name: 'TA_flow', frame: SHOTS.TA.from + Math.floor((PA.flow0 + PA.flow1) / 2)},
  {name: 'TA_end', frame: SHOTS.TA.to - 8},
  // TB
  {name: 'TB_start_live', frame: SHOTS.TB.from + Math.max(5, Math.floor(PB.liveEnd * 0.4))},
  {name: 'TB_freeze', frame: SHOTS.TB.from + PB.freezeStart + 8},
  {name: 'TB_crossfade', frame: SHOTS.TB.from + PB.threeIn1 + 4},
  {name: 'TB_matched', frame: SHOTS.TB.from + PB.matchEnd + 4},
  {name: 'TB_xray', frame: SHOTS.TB.from + Math.floor((PB.xray0 + PB.xray1) / 2)},
  {name: 'TB_flow', frame: SHOTS.TB.from + Math.floor((PB.flow0 + PB.flow1) / 2)},
  {name: 'TB_end', frame: SHOTS.TB.to - 8},
  // S08
  {name: 'S08_summary_mid', frame: SHOTS.S08.from + 40},
  // S09 phases
  {name: 'S09_ask', frame: SHOTS.S09.from + 10},
  {name: 'S09_info', frame: SHOTS.S09.from + Math.round((SHOTS.S09.to - SHOTS.S09.from) * 0.4)},
  {name: 'S09_price', frame: SHOTS.S09.from + Math.round((SHOTS.S09.to - SHOTS.S09.from) * 0.75)},
  // S10
  {name: 'S10_ending', frame: SHOTS.S10.from + 20},
];

const stillBin = join(ROOT, 'node_modules', '.bin', 'remotion');
const entry = join(ROOT, 'src', 'index.tsx');

function renderStill(name, frame) {
  const out = join(FRAMES, `${name}.jpg`);
  if (existsSync(out) && process.env.FORCE !== '1') {
    // always re-render for this pass
  }
  const cmd = [
    stillBin,
    'still',
    entry,
    'RoadsterShort',
    out,
    `--frame=${frame}`,
    '--image-format=jpeg',
    '--jpeg-quality=90',
    '--gl=angle',
    '--log=error',
  ].join(' ');
  console.log(`→ ${name} @ frame ${frame} (${(frame / FPS).toFixed(2)}s)`);
  execSync(cmd, {cwd: ROOT, stdio: 'inherit', env: {...process.env}});
  return out;
}

const meta = [];
for (const k of KEYS) {
  const path = renderStill(k.name, k.frame);
  meta.push({...k, path, t: k.frame / FPS});
}

writeFileSync(join(FRAMES, 'keyframes.json'), JSON.stringify({keys: meta, phases: {PA, PB}, shots: SHOTS}, null, 2));
console.log('DONE stills', meta.length);
