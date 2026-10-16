import React from 'react';
import {El,Box,Zone,ZONES,vis,clamp,back} from './zones';
import {Card,Tx,P,textW,FONT} from './mat';
export const E=(out:El[],id:string,g:string,zone:Zone,box:Box,a:number,draw:()=>React.ReactNode)=>{if(a>0.001)out.push({id,g,zone,box,a,draw});};
/** title strip in the title zone, auto-sized and centered */
export const title=(out:El[],t:number,id:string,text:string,t0:number,t1:number,s=48,color=P.ink)=>{const a=vis(t,t0,t1);if(a<=0)return;const z=ZONES.title;
 let size=s;while(textW(text,size)+70>z[2]&&size>28)size-=2;const w=textW(text,size)+70,h=size+56;const x=z[0]+(z[2]-w)/2,y=z[1]+(z[3]-h)/2+10;const pop=back(t,t0,.4);
 E(out,id,'title:'+id,'title',[x,y,w,h],a,()=><g transform={`translate(${x+w/2},${y+h/2}) scale(${.85+.15*pop}) translate(${-(x+w/2)},${-(y+h/2)})`}><Card b={[x,y,w,h]} r={22}/><Tx x={x+w/2} y={y+h/2+2} s={size} c={color}>{text}</Tx></g>);};
export {ZONES};
