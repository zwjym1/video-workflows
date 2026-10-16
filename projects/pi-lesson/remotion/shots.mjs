import fs from 'fs';const m=await import('./.lc/scenes.mjs');
const N=9938,seg=[];let prev=null;
for(let f=0;f<N;f+=3){const els=m.elementsAt(f/30).filter(e=>!['cap','tag','think'].includes(e.g));const full=els.filter(e=>e.a>.98).map(e=>e.id).sort().join(',');const any=els.some(e=>e.a<=.98);
 const key=any?'~':full;if(!prev||prev.key!==key){prev={key,f0:f,f1:f};seg.push(prev);}else prev.f1=f;}
const shots=seg.filter(s=>s.key!=='~'&&s.f1-s.f0>=15);const list=[];
shots.forEach((s,i)=>{list.push({f:Math.round((s.f0+s.f1)/2),name:`shot${String(i+1).padStart(2,'0')}`,els:s.key});
 const n=shots[i+1];if(n){const a=s.f1,b=n.f0;list.push({f:a,name:`tr${String(i+1).padStart(2,'0')}-start`},{f:Math.round((a+b)/2),name:`tr${String(i+1).padStart(2,'0')}-mid`},{f:b,name:`tr${String(i+1).padStart(2,'0')}-end`});}});
fs.writeFileSync('.lc/shots.json',JSON.stringify(list,null,1));console.log(shots.length,list.length);
