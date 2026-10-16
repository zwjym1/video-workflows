import React from 'react';
import {X as DATA_X,target,predict,loss,Param} from '../gradient-story/model';
// Display mapping only (model unchanged): x∈[-1,1] -> study hours 1..5 h, y -> exam score 60+25y.
export const hours=(x:number)=>3+2*x,score=(y:number)=>60+25*y;
const green='#1f6b57',red='#e0662f',muted='#9e947e';
export const DataChart:React.FC<{p:Param;w:number;h:number;residual?:number;draw?:number;glow?:number;showLine?:number;labels?:boolean}>=({p,w,h,residual=1,draw=1,glow=0,showLine=1,labels=true})=>{
 const L=w*.13,R=w*.95,T=h*.08,B=h*.84,sx=(x:number)=>L+(x+1.2)/2.4*(R-L),sy=(y:number)=>B-(y+.6)/5.4*(B-T);
 const x0=-1.2,x1=-1.2+2.4*draw;
 return <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
  <rect width={w} height={h} rx={w*.02} fill="#fffaf0" stroke="#e4d9c2"/>
  <defs><clipPath id={`clip${w}`}><rect x={L} y={T} width={R-L} height={B-T}/></clipPath></defs>
  {[50,60,70,80,90,100,110,120,130,140,150,160,170].filter(v=>sy((v-60)/25)>=T&&sy((v-60)/25)<=B).map(v=><g key={v}><path d={`M${L} ${sy((v-60)/25)}H${R}`} stroke="#eee5d3"/>{labels&&v%20===0&&v<=100&&<text x={L-8} y={sy((v-60)/25)+5} textAnchor="end" fontSize={h*.035} fill={muted}>{v}</text>}</g>)}
  {DATA_X.map(x=><g key={x}><path d={`M${sx(x)} ${T}V${B}`} stroke="#eee5d3"/>{labels&&<text x={sx(x)} y={B+h*.055} textAnchor="middle" fontSize={h*.035} fill={muted}>{hours(x)}h</text>}</g>)}
  <path d={`M${L} ${B}H${R}M${L} ${T}V${B}`} stroke="#b5a88b" strokeWidth="1.5"/>
  {labels&&<><text x={R} y={h*.975} textAnchor="end" fontSize={h*.04} fill="#5b5446">学习时长 →</text><text x={L} y={T-h*.02} fontSize={h*.04} fill="#5b5446">成绩</text></>}
  {showLine>0&&<path d={`M${sx(x0)} ${sy(predict(x0,p))}L${sx(x1)} ${sy(predict(x1,p))}`} stroke={red} strokeWidth={Math.max(3,w*.009)} clipPath={`url(#clip${w})`} opacity={showLine} style={{filter:glow?`drop-shadow(0 0 ${glow*14}px ${red})`:undefined}}/>}
  {DATA_X.map(x=><g key={x}>{showLine>0&&<path d={`M${sx(x)} ${sy(target(x))}V${sy(predict(x,p))}`} stroke={red} strokeWidth="2" strokeDasharray="5 6" opacity={residual*.75*showLine} clipPath={`url(#clip${w})`}/>}<circle cx={sx(x)} cy={sy(target(x))} r={Math.max(5,w*.017)} fill={green}/></g>)}
  {labels&&showLine>0&&<text x={R-6} y={T+h*.07} textAnchor="end" fontSize={h*.05} fill={red} opacity={showLine}>误差 {loss(p).toFixed(3)}</text>}
 </svg>;
};
export const MiniChart:React.FC<{p:Param;w:number;h:number}>=({p,w,h})=><div style={{boxShadow:'0 14px 40px #5a4a2a22',borderRadius:8}}><DataChart p={p} w={w} h={h}/></div>;
