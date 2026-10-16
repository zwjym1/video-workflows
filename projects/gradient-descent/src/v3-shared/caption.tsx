import React from 'react';
import {Alignment,sentences} from './words';
// Karaoke-style caption: current sentence, spoken chars light up.
export const Caption:React.FC<{al:Alignment;f:number;color:string;dim:string;font:string;top?:number;size?:number}>=({al,f,color,dim,font,top=1690,size=40})=>{
 const ss=sentences(al);const s=[...ss].reverse().find(v=>f>=v.start-4)??ss[0];
 return <div style={{position:'absolute',left:60,right:60,top,textAlign:'center',fontFamily:font,fontSize:size,lineHeight:1.5,letterSpacing:2}}>{s.chars.map((v,i)=><span key={i} style={{color:f>=v.f?color:dim,transition:'none'}}>{v.c}</span>)}</div>;
};
