import {bundle} from '@remotion/bundler';import {renderStill,selectComposition,openBrowser} from '@remotion/renderer';import fs from 'fs';
const list=JSON.parse(fs.readFileSync('.lc/shots.json'));const out='../output/review-v2/';
const serveUrl=await bundle({entryPoint:'src/index.tsx'});const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/google-chrome',chromiumOptions:{gl:'angle'}});
const composition=await selectComposition({serveUrl,id:'PiLesson',puppeteerInstance:browser});
const todo=list.filter(x=>!fs.existsSync(out+`${String(x.f).padStart(5,'0')}-${x.name}.png`));
for(let i=0;i<todo.length;i+=4)await Promise.all(todo.slice(i,i+4).map(x=>renderStill({composition,serveUrl,frame:x.f,output:out+`${String(x.f).padStart(5,'0')}-${x.name}.png`,puppeteerInstance:browser,imageFormat:'png'}).then(()=>console.log('ok',x.f,x.name))));
await browser.close({silent:true});console.log('DONE');
