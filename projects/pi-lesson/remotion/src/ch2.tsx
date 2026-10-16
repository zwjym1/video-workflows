import React from 'react';
import {AbsoluteFill,staticFile} from 'remotion';
import {C,GridBg,Tx,useT,prog,back,clamp,poly,pts,lerp} from './ui';
import {at,atEnd,ss,se} from './timing';
import {Chip,Img2} from './parts';
const CX=960,CY=540,R=300;
export const Ch2:React.FC=()=>{
 const t=useT();
 const stamp=prog(t,at(17,'四个字'),atEnd(18,'周三径一')-at(17,'四个字'));
 const hex=prog(t,at(21,'六边形'),.8);
 const sides=prog(t,at(22,'每条边'),1);
 const three=prog(t,at(23,'三个直径'),.9);
 const short=prog(t,at(25,'短一点'),.5);
 const crescent=prog(t,at(26,'抄了近路'),.7);
 const gt3=back(t,at(27,'比三大'),.4);
 const more=prog(t,at(29,'再多几条边'),.6);
 const paper=1-prog(t,at(29,'再多'),.8);
 const hexPts=poly(6,CX,CY,R);
 const chars=['周','三','径','一'];
 return <AbsoluteFill><svg width={1920} height={1080}>
  <GridBg bg={lerpCol(C.paper,C.bg,1-paper)} line={lerpCol(C.paperLine,C.grid,1-paper)}/>
  <g opacity={.35}><Img2 href={staticFile('img/zhoubi-gougu-diagram.png')} x={80} y={160} w={280} h={280}/></g>
  {/* stamp 周三径一 */}
  <g>{chars.map((ch,i)=>{const a=clamp(stamp*4-i);return <g key={i} opacity={a} transform={`translate(${720+i*120},${200}) scale(${.6+.4*a})`}>
    <rect x={-50} y={-50} width={100} height={100} rx={10} fill="#D7263D"/><Tx x={0} y={6} s={70} c="#fff" f={'"Noto Serif CJK SC",serif'}>{ch}</Tx></g>;})}</g>
  {/* circle + hex */}
  <circle cx={CX} cy={CY} r={R} fill="#fff8" stroke={C.ink} strokeWidth={6}/>
  <polygon points={pts(hexPts)} fill="none" stroke={C.blue} strokeWidth={8} opacity={hex} strokeDasharray={1800} strokeDashoffset={1800*(1-hex)}/>
  {/* radius sticks on each side */}
  {hexPts.map((p,i)=>{const a=clamp(sides*6-i);const mid=[(p[0]+hexPts[(i+1)%6][0])/2,(p[1]+hexPts[(i+1)%6][1])/2];
   return <g key={i} opacity={a}><line x1={CX} y1={CY} x2={p[0]} y2={p[1]} stroke={C.teal} strokeWidth={5} strokeDasharray="8 6"/>
    <circle cx={p[0]} cy={p[1]} r={8} fill={C.orange}/></g>;})}
  {/* 3 diameters lined up */}
  {three>.05&&[0,1,2].map(i=>{const a=clamp(three*3-i);return <rect key={i} x={200+i*(2*R+10)} y={900} width={2*R} height={24} rx={10} fill={[C.blue,C.teal,C.pink][i]} opacity={a}/>;})}
  {three>.5&&<Tx x={960} y={860} s={40} c={C.ink} o={three}>6个半径 = 3个直径</Tx>}
  {/* crescents */}
  {crescent>.05&&hexPts.map((p,i)=>{const q=hexPts[(i+1)%6];const midA=Math.atan2((p[1]+q[1])/2-CY,(p[0]+q[0])/2-CX);
   return <path key={i} d={`M${p[0]},${p[1]} A${R},${R} 0 0 1 ${q[0]},${q[1]} L${q[0]},${q[1]}`} fill={C.yel} opacity={.45*crescent}/>;})}
  <g opacity={gt3}><Chip x={1600} y={500} text="π > 3" s={64} bg={C.pink} a={gt3}/></g>
  {/* next cut hint */}
  {more>.1&&(()=>{const a=more;const mid=hexPts[0];const ang=-Math.PI/2+Math.PI/6;const tip=[CX+R*Math.cos(ang),CY+R*Math.sin(ang)];
   return <g opacity={a}><circle cx={tip[0]} cy={tip[1]} r={12} fill={C.orange}/><Tx x={tip[0]+40} y={tip[1]-20} s={32} c={C.orange}>再切？</Tx></g>;})()}
 </svg></AbsoluteFill>;
};
function lerpCol(a:string,b:string,p:number){p=clamp(p);const h=(s:string)=>[1,3,5].map(k=>parseInt(s.slice(k,k+2),16));const A=h(a),B=h(b);return '#'+A.map((v,k)=>Math.round(v+(B[k]-v)*p).toString(16).padStart(2,'0')).join('');}
