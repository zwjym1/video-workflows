import {build} from 'esbuild';import fs from 'fs';
await build({entryPoints:['src/scenes.ts'],bundle:true,platform:'node',format:'esm',outfile:'.lc/scenes.mjs',jsx:'automatic',external:['react','react/jsx-runtime','remotion'],logLevel:'error'});
const m=await import('./.lc/scenes.mjs');const {TOTAL}=await import('./.lc/scenes.mjs');
const N=9938;const pr=[];for(let f=0;f<N;f+=5)pr.push(...m.checkAt(f/30));
const g={};for(const p of pr){const k=p.kind+'|'+p.a+'|'+(p.b||'');(g[k]??=[]).push(p.t);}
const rows=Object.entries(g).map(([k,ts])=>({k,frames:ts.length,first:Math.round(ts[0]*30),last:Math.round(ts.at(-1)*30)}));
fs.writeFileSync('../output/review-v2/layout-check.json',JSON.stringify({sampledEvery:5,frames:N,problems:pr.length,groups:rows},null,1));
fs.writeFileSync('../output/review-v2/layout-check.md',`# Layout check\nSampled every 5 frames over ${N} frames.\nResult: ${pr.length?'FAIL':'PASS'} (${pr.length} problem samples)\n\n`+rows.map(r=>`- ${r.k} frames ${r.first}–${r.last} (${r.frames} samples)`).join('\n')+'\n');
console.log(pr.length?'FAIL':'PASS',pr.length);for(const r of rows)console.log(r.k,r.first,r.last,r.frames);process.exit(pr.length?1:0);
