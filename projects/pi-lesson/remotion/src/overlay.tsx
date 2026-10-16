import React from 'react';
import {El,clamp,back,prog} from './zones';
import {E} from './common';
import {Tx,P,FONT,textW} from './mat';
import {Mascot} from './obj';
import {S,se,CH} from './timing';
import {PHRASES,THINK,toDisplay} from './ui';
const TAGS=['开场','第1章 量一量','第2章 周三径一','第3章 割圆术','第4章 祖冲之','第5章 计算机时代','第6章 π日'];
export const overlay=(t:number,out:El[])=>{
 let c=0;for(let k=0;k<7;k++)if(t>=CH[k])c=k;const w=TAGS[c].length*34+56;const a=back(t,CH[c],.4);
 E(out,'tag'+c,'tag','tag',[40,34,w,62],1,()=><g transform={`translate(40,34) scale(${a})`} filter="url(#shadowS)"><rect width={w} height={62} rx={31} fill={P.blue}/><Tx x={w/2} y={33} s={32} c="#fff">{TAGS[c]}</Tx></g>);
 const i=THINK.find(k=>t>=S[k].start-.1&&t<se(k)+2.25);
 if(i!==undefined){const a0=S[i].start,end=se(i)+2.1;const inA=back(t,a0,.45);const o=Math.min(clamp((t-a0)/.15),1-prog(t,end,.25));const cd=clamp((t-se(i))/2);
  const q=toDisplay(S[i].text.replace(/^再?想一想，/,''));const fs=q.length>14?32:40;
  E(out,'think'+i,'think','think',[1250,30,640,190],o,()=><g opacity={o}>
   <Mascot x={1325} y={135} s={.62*inA} bob={Math.sin(t*6)*3}/>
   <g transform={`translate(1410,40) scale(${.6+.4*inA})`} filter="url(#shadow)"><rect width={470} height={170} rx={30} fill={P.orange}/>
    <rect x={20} y={16} width={130} height={46} rx={23} fill="#fff"/><Tx x={85} y={40} s={28} c={P.orange}>想一想</Tx>
    <foreignObject x={20} y={70} width={350} height={96}><div style={{fontFamily:FONT,fontWeight:900,fontSize:fs,color:'#fff',lineHeight:1.15}}>{q}</div></foreignObject>
    <circle cx={420} cy={52} r={32} fill="#fff" opacity={.35}/><circle cx={420} cy={52} r={32} fill="none" stroke="#fff" strokeWidth={8} strokeDasharray={`${2*Math.PI*32*(1-cd)} 999`} transform="rotate(-90 420 52)" strokeLinecap="round"/>
    <Tx x={420} y={54} s={28}>{t>=se(i)?String(Math.max(1,Math.ceil(2-cd*2))):'?'}</Tx></g></g>);}
 const j=PHRASES.findIndex((p,k)=>t>=p.start-.06&&t<(k<PHRASES.length-1?Math.min(PHRASES[k+1].start-.06,p.end+.7):p.end+1));
 if(j>=0){const p=PHRASES[j];const ca=clamp((t-p.start+.06)/.12);const tw=Math.min(1880,textW(p.text,66)+40);
  E(out,'cap','cap','sub',[960-tw/2,915,tw,90],ca,()=><text x={960} y={962} textAnchor="middle" dominantBaseline="middle" fontFamily={FONT} fontWeight={900} fontSize={66} letterSpacing={3} fill="#fff" stroke={P.ink} strokeWidth={9} paintOrder="stroke fill" opacity={ca}>{p.text}</text>);}
};
