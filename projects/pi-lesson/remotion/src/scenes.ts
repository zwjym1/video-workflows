import {El,ZONES,hit,inside} from './zones';
import {scene0,scene1,scene2} from './s012';
import {scene3} from './s3';
import {scene4,scene5,scene6} from './s456';
import {overlay} from './overlay';
export const elementsAt=(t:number):El[]=>{const out:El[]=[];for(const f of [scene0,scene1,scene2,scene3,scene4,scene5,scene6,overlay])f(t,out);return out;};
export type Problem={t:number;kind:string;a:string;b?:string};
export const checkAt=(t:number):Problem[]=>{const els=elementsAt(t);const pr:Problem[]=[];
 const used=new Set(els.map(e=>e.zone));
 for(const e of els){if(!inside(e.box,ZONES[e.zone]))pr.push({t,kind:'outside-zone:'+e.zone,a:e.id});
  if(e.zone!=='sub'&&hit(e.box,ZONES.sub))pr.push({t,kind:'subtitle-intrusion',a:e.id});
  if(e.zone==='wide'&&(used.has('stage')||used.has('side')))pr.push({t,kind:'wide-with-stage/side',a:e.id});}
 for(let i=0;i<els.length;i++)for(let j=i+1;j<els.length;j++){const A=els[i],B=els[j];if(A.g===B.g)continue;if(A.a>.02&&B.a>.02&&hit(A.box,B.box))pr.push({t,kind:'overlap',a:A.id,b:B.id});}
 return pr;};
