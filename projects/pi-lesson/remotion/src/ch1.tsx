import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C,GridBg,Tx,useT,prog,back,clamp,lerp} from './ui';
import {at,atEnd,ss,se} from './timing';
import {Chip,Cross} from './parts';
const items=[{name:'杯盖',r:160,v:'3.14',c:C.blue},{name:'硬币',r:90,v:'3.13',c:C.orange},{name:'碗口',r:200,v:'3.15',c:C.teal}];
export const Ch1:React.FC=()=>{
 const t=useT();
 const rope=prog(t,at(6,'绳子'),atEnd(6,'周长')-at(6,'绳子'));
 const div=prog(t,at(7,'除以'),.5);
 const v1=back(t,at(8,'三点一四'),.4);
 const others=prog(t,at(9,'硬币'),.7);
 const same=prog(t,at(10,'差不多'),.5);
 const grow=prog(t,at(13,'变长'),.9);
 const name=back(t,at(14,'圆周率'),.5);
 const approx=back(t,at(15,'约等于'),.5);
 const fadeTools=prog(t,at(16,'尺子'),.6);
 const toPaper=prog(t,at(16,'古人'),1.2);
 // layout three circles
 const layout=others>.05;
 const xs=layout?[420,960,1500]:[960,960,960];
 const rs=items.map((it,i)=>it.r*(i===0&&grow>.01?1+grow:1)*(layout||i===0?1:0));
 const show=items.map((_,i)=>i===0?1:clamp(others*3-(i-1)));
 return <AbsoluteFill><svg width={1920} height={1080}>
  <GridBg bg={lerpColor(C.bg,C.paper,toPaper)} line={toPaper>.5?C.paperLine:C.grid}/>
  {items.map((it,i)=>{if(show[i]<=0)return null;const cx=xs[i],cy=480,r=rs[i]*show[i]||it.r;
   return <g key={i} opacity={show[i]}><circle cx={cx} cy={cy} r={r} fill="#fff" stroke={it.c} strokeWidth={14}/>
    <line x1={cx-r} y1={cy} x2={cx+r} y2={cy} stroke={C.ink} strokeWidth={6}/>
    {/* rope around first */}
    {i===0&&<path d={describeArc(cx,cy,r+8, -90, -90+360*Math.min(1,rope*1.2))} fill="none" stroke={C.orange} strokeWidth={10} strokeLinecap="round"/>}
    {i===0&&rope>0.85&&<line x1={cx+r+30} y1={cy-r-40} x2={cx+r+30+(2*Math.PI*r)*.35} y2={cy-r-40} stroke={C.orange} strokeWidth={10} strokeLinecap="round" opacity={clamp((rope-.85)/.15)}/>}
    <Tx x={cx} y={cy+r+40} s={40} c={C.ink}>{it.name}</Tx>
    {(i===0?v1:show[i])>.5&&<Chip x={cx} y={cy+r+100} text={it.v} s={48} bg={it.c} a={i===0?v1:show[i]}/>}
   </g>;})}
  <g opacity={same}><Tx x={960} y={140} s={64} c={C.pink}>周长 ÷ 直径  ≈ 3.1…</Tx></g>
  <g opacity={name}><Chip x={960} y={300} text="圆周率  π" s={64} bg={C.yel} fg={C.ink} a={name}/></g>
  <g opacity={approx}><Chip x={960} y={400} text="π ≈ 3.14" s={56} bg={C.pink} a={approx}/></g>
  {fadeTools>.1&&<g opacity={clamp(1-toPaper)}><rect x={1400} y={200} width={40} height={280} rx={6} fill={C.yel} stroke={C.ink} strokeWidth={3}/><Cross x={1420} y={340} s={80} p={fadeTools}/></g>}
  {/* transition: line circle on paper */}
  {toPaper>.4&&<g opacity={prog(t,at(16,'古人')+.5,.5)}><circle cx={960} cy={520} r={280} fill="none" stroke={C.ink} strokeWidth={6}/><path d={`M${960+280},${520} Q${960+320},${420} ${960+200},${380}`} fill="none" stroke={C.orange} strokeWidth={8}/></g>}
 </svg></AbsoluteFill>;
};
function describeArc(cx:number,cy:number,r:number,start:number,end:number){const s=polar(cx,cy,r,end),e=polar(cx,cy,r,start);const large=end-start<=180?0:1;return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 0 ${e.x} ${e.y}`;}
function polar(cx:number,cy:number,r:number,a:number){const rad=(a-90)*Math.PI/180;return{x:cx+r*Math.cos(rad),y:cy+r*Math.sin(rad)};}
function lerpColor(a:string,b:string,p:number){p=clamp(p);const h=(s:string)=>[1,3,5].map(k=>parseInt(s.slice(k,k+2),16));const A=h(a),B=h(b);return '#'+A.map((v,k)=>Math.round(v+(B[k]-v)*p).toString(16).padStart(2,'0')).join('');}
