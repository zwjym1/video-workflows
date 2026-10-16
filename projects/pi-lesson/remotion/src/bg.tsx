import React from 'react';
import {clamp} from './zones';
import {CH} from './timing';
// per-chapter real-material backgrounds, crossfaded over 0.8 s, with slow parallax zoom (background only)
const BG:((k:number)=>React.ReactNode)[]=[
 ()=><g><rect width={1920} height={1080} fill="#cfe6f7"/><rect y={760} width={1920} height={320} fill="url(#asphalt)"/><rect width={1920} height={760} fill="url(#sky)"/></g>,
 ()=><rect width={1920} height={1080} fill="url(#oak)"/>,
 ()=><g><rect width={1920} height={1080} fill="#e9dcc0"/><rect width={1920} height={1080} fill="url(#paperTex)"/></g>,
 ()=><g><rect width={1920} height={1080} fill="url(#oak)"/><rect x={40} y={225} width={1840} height={670} rx={10} fill="#fbf8f0" filter="url(#shadow)"/><rect x={40} y={225} width={1840} height={670} fill="url(#graph)"/></g>,
 ()=><g><rect width={1920} height={1080} fill="#3a2414"/><rect width={1920} height={1080} fill="url(#oak)" opacity={.45}/></g>,
 ()=><rect width={1920} height={1080} fill="url(#nightG)"/>,
 ()=><rect width={1920} height={1080} fill="url(#oak)"/>,
];
export const Background:React.FC<{t:number}>=({t})=>{let c=0;for(let k=0;k<7;k++)if(t>=CH[k]-.4)c=k;
 const a=clamp((t-(CH[c]-.4))/.8);const z=(k:number)=>1.04-0.04*clamp((t-CH[k])/((CH[k+1]??t+1)-CH[k]));
 const layer=(k:number,o:number)=><g key={k} opacity={o} transform={`translate(960,540) scale(${z(k)}) translate(-960,-540)`}>{BG[k](k)}</g>;
 return <g>{c>0&&a<1&&layer(c-1,1)}{layer(c,c===0?1:a)}<rect width={1920} height={1080} fill="url(#vignette)"/></g>;};
