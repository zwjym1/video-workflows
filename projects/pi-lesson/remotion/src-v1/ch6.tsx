import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C,GridBg,Tx,useT,prog,back,clamp,lerp} from './ui';
import {at,atEnd,ss,se,CH} from './timing';
import {Chip} from './parts';
export const Ch6:React.FC=()=>{
 const t=useT();
 const jones=prog(t,at(84,'英国'),.6);
 const euler=prog(t,at(85,'欧拉'),.5);
 const day=prog(t,at(86,'三月十四日'),.6);
 const end=prog(t,at(88,'下次'),1.5);
 const D=180,R=D/2,X0=400,Y=900,len=Math.PI*D;
 return <AbsoluteFill><svg width={1920} height={1080}><GridBg/>
  {/* big pi shrinks to book */}
  <g opacity={1-day*.5} transform={`translate(${lerp(960,520,jones)},${lerp(500,420,jones)}) scale(${lerp(3.2,.9,jones)})`}>
   <Tx x={0} y={0} s={160} c={C.pink} f={'"Noto Serif CJK SC",serif'}>π</Tx>
  </g>
  {jones>.2&&euler<.8&&<g opacity={jones}><rect x={700} y={300} width={420} height={520} rx={16} fill={C.paper} stroke={C.ink} strokeWidth={5}/>
   <Tx x={910} y={380} s={36} c={C.ink}>1706 · Jones</Tx>
   <Tx x={910} y={480} s={48} c={C.orange} f={'"Noto Serif CJK SC",serif'}>perimetron</Tx>
   <Tx x={740} y={560} s={90} c={C.pink} a="start">π</Tx>
   <Tx x={910} y={720} s={32} c={C.ink}>周长 / 直径</Tx></g>}
  {euler>.05&&day<.5&&<g opacity={euler}><Chip x={1500} y={400} text="欧拉" s={48} bg={C.blue} a={euler}/>
   {[0,1,2,3,4].map(i=><Tx key={i} x={1300+i*80} y={560+Math.sin(i)*40} s={70} c={C.pink} o={euler}>π</Tx>)}</g>}
  {day>.05&&end<.5&&<g opacity={day}><rect x={200} y={220} width={560} height={580} rx={36} fill="#fff" stroke={C.ink} strokeWidth={6}/>
   <rect x={200} y={220} width={560} height={140} rx={36} fill={C.pink}/><rect x={200} y={320} width={560} height={40} fill={C.pink}/>
   <Tx x={480} y={290} s={70} c="#fff">3 月</Tx><Tx x={480} y={560} s={260} c={C.ink}>14</Tx>
   <ellipse cx={1300} cy={560} rx={330} ry={200} fill={C.wood}/><ellipse cx={1300} cy={540} rx={290} ry={160} fill="#E9A23B"/>
   <Tx x={1300} y={560} s={200} c="#fff" stroke={C.ink} sw={6} f={'"Noto Serif CJK SC",serif'}>π</Tx>
   <Chip x={1300} y={220} text="国际数学日" s={48} bg={C.blue} a={day}/></g>}
  {/* closing: wheel returns */}
  {end>.05&&(()=>{const a=end;const cx=X0+len*a,cy=Y-R;
   return <g opacity={clamp(a*3)}><rect x={0} y={Y} width={1920} height={1080-Y} fill="#CDEAC0"/><line x1={0} y1={Y} x2={1920} y2={Y} stroke={C.ink} strokeWidth={6}/>
    <line x1={X0} y1={Y-6} x2={cx} y2={Y-6} stroke={C.orange} strokeWidth={12}/>
    <circle cx={cx} cy={cy} r={R} fill={C.ink}/><circle cx={cx} cy={cy} r={R-24} fill={C.grey}/><circle cx={cx} cy={cy} r={16} fill={C.yel}/>
    <Tx x={960} y={200} s={56} c={C.ink}>里面藏着一个，永远写不完的数</Tx></g>;})()}
 </svg></AbsoluteFill>;
};
