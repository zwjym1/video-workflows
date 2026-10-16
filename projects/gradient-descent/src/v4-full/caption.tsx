import React from 'react';
import {Alignment} from '../v3-shared/words';
// Douyin-style captions: split at EVERY punctuation, one short phrase at a time, punctuation hidden,
// bold white with black stroke + shadow, lower-middle safe band. Timing from word-level alignment.
const PUNCT=/[，。；：、！？,.;:!?\s]/;
type Phrase={text:string;start:number;end:number;chars:{c:string;f:number}[]};
export const phrases=(al:Alignment):Phrase[]=>{
 const out:Phrase[]=[];let cur:{c:string;f:number}[]=[];let k=0,rem=0,last=0,lastEnd=0;
 const push=()=>{if(cur.length){out.push({text:cur.map(v=>v.c).join(''),start:cur[0].f,end:lastEnd,chars:cur});cur=[];}};
 for(const c of al.text){if(PUNCT.test(c)){push();continue;}
  if(rem<=0){const b=al.boundaries[k++];last=Math.round(b.offset*30);lastEnd=Math.round((b.offset+b.duration)*30);rem=[...b.text].length;}
  rem--;cur.push({c,f:last});}
 push();return out;
};
export const PhraseCaption:React.FC<{al:Alignment;f:number;y?:number;accent?:string}>=({al,f,y=1560,accent='#ffd54a'})=>{
 const ps=phrases(al);
 const i=ps.findIndex((p,j)=>f>=p.start-2&&(j===ps.length-1?f<=p.end+20:f<ps[j+1].start-2));
 if(i<0)return null;const p=ps[i];const age=f-(p.start-2);const pop=Math.min(1,age/4);
 return <div style={{position:'absolute',left:54,right:54,top:y,transform:`translateY(-50%) scale(${.86+.14*pop})`,textAlign:'center',fontFamily:'"Microsoft YaHei","Noto Sans CJK SC",sans-serif',fontWeight:900,fontSize:74,letterSpacing:2,lineHeight:1.1,whiteSpace:'nowrap',opacity:Math.min(1,age/2)}}>
  {p.chars.map((v,j)=><span key={j} style={{color:f>=v.f?'#ffffff':'#ffffffb0',WebkitTextStroke:'7px #111',paintOrder:'stroke fill',textShadow:'0 6px 18px #0009'}}>{v.c}</span>)}
 </div>;
};
