import React from 'react';
import {AbsoluteFill,interpolate} from 'remotion';
import {C,GridBg,Tx,useT,prog,back,clamp,lerp} from './ui';
import {at,atEnd,ss,se} from './timing';
import {Chip} from './parts';
const D=200,R=D/2,X0=260,Y=620,PI=Math.PI;
export const Ch0:React.FC=()=>{
 const t=useT();
 const roll=prog(t,at(0,'车轮'),atEnd(0,'多远')-at(0,'车轮'));
 const bars=prog(t,at(1,'三倍'),.9);
 const extra=prog(t,at(1,'一小截'),.5);
 const zoom=prog(t,at(2,'这一小截'),.6);
 const shrink=prog(t,at(5,'量一量'),.9);
 const len=PI*D;const xe=X0+len;const cx=X0+len*roll;const cy=Y-R;
 const ghostO=1-roll*.6;const barCols=[C.blue,C.teal,C.pink];
 // transform to cup: scale down and move to center of desk
 const toCup=shrink;const sc=lerp(1,.55,toCup);const ox=lerp(0,200,toCup);const oy=lerp(0,-80,toCup);
 return <AbsoluteFill><svg width={1920} height={1080}><GridBg/>
  <g transform={`translate(${ox},${oy}) scale(${sc})`} style={{transformOrigin:'960px 540px'}}>
   <rect x={0} y={Y} width={1920} height={1080-Y} fill="#CDEAC0"/><line x1={0} y1={Y} x2={1920} y2={Y} stroke={C.ink} strokeWidth={6}/>
   {/* ghost start */}
   <g opacity={ghostO}><circle cx={X0} cy={cy} r={R} fill="none" stroke={C.light} strokeWidth={8}/><line x1={X0} y1={Y-8} x2={X0} y2={Y+8} stroke={C.ink} strokeWidth={4}/></g>
   {/* track */}
   <line x1={X0} y1={Y-6} x2={cx} y2={Y-6} stroke={C.orange} strokeWidth={14} strokeLinecap="round"/>
   {/* wheel */}
   <g transform={`rotate(${roll*360} ${cx} ${cy})`}>
    <circle cx={cx} cy={cy} r={R} fill={C.ink}/><circle cx={cx} cy={cy} r={R-28} fill={C.grey}/>
    {Array.from({length:8},(_,k)=>{const a=(-Math.PI/2+k*Math.PI/4);return <line key={k} x1={cx} y1={cy} x2={cx+(R-28)*Math.cos(a)} y2={cy+(R-28)*Math.sin(a)} stroke={C.ink} strokeWidth={8}/>;})}
    <circle cx={cx} cy={cy} r={18} fill={C.yel}/>
   </g>
   {/* diameter bars */}
   {barCols.map((c,i)=>{const p=clamp(bars*3-i);return <g key={i} opacity={p}><rect x={X0+i*D+3} y={Y+40} width={D-6} height={30} rx={12} fill={c}/><Tx x={X0+i*D+D/2} y={Y+100} s={30} c={C.ink}>直径</Tx></g>;})}
   {/* extra 0.1416 D */}
   <g opacity={extra}><rect x={X0+3*D} y={Y+40} width={.1416*D} height={30} fill={C.yel} stroke={C.orange} strokeWidth={3}/><Tx x={X0+3*D+70} y={Y+145} s={32} c={C.orange}>还多一小截（约0.14个直径）</Tx>
    <polygon points={`${X0+3*D+2},${Y+125} ${X0+3*D+.1416*D-2},${Y+125} ${X0+3*D+.07*D},${Y+78}`} fill={C.orange}/></g>
   <g opacity={1-toCup*.8}><Tx x={960} y={160} s={68} c={C.ink}>车轮滚一圈，到底走了多远？</Tx></g>
   {/* zoom on gap */}
   <g opacity={zoom*.7}><circle cx={X0+3*D+.07*D} cy={Y+55} r={lerp(30,90,zoom)} fill="none" stroke={C.orange} strokeWidth={4} strokeDasharray="8 6"/></g>
  </g>
  {/* cup forming */}
  {toCup>.3&&(()=>{const a=prog(t,at(5,'量一量')+.3,.5);const cx2=960,cy2=500,r2=160;
   return <g opacity={a}><ellipse cx={cx2} cy={cy2} rx={r2} ry={r2} fill="#fff" stroke={C.blue} strokeWidth={14}/><Tx x={cx2} y={cy2+r2+50} s={44} c={C.ink}>杯盖</Tx>
    <path d={`M${cx2+r2},${cy2} A${r2},${r2} 0 1 1 ${cx2},${cy2-r2}`} fill="none" stroke={C.orange} strokeWidth={10} strokeLinecap="round" opacity={.8}/>
   </g>;})()}
 </svg></AbsoluteFill>;
};
