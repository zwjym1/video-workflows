import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C,Tx,useT,prog,back,clamp,lerp} from './ui';
import {at,atEnd,ss,se,CH} from './timing';
import {Chip} from './parts';
const PI='3141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148086513282306647093844609550582231725359408128481117450284102701938521105559644622948954930381964428810975665933446128475648233786783165271201909145648566923460348610454326648213393607260249141273';
export const Ch5:React.FC=()=>{
 const t=useT();const dt=t-CH[5];
 const pc=back(t,at(75,'计算机'),.5);
 const rec=back(t,at(76,'三百一十四万亿'),.5);
 const days=back(t,at(77,'一百一十天'),.4);
 const years=prog(t,at(79,'大约'),atEnd(79,'万年')-at(79,'大约'));
 const inf=prog(t,at(81,'无限'),.6);
 const approx=back(t,at(82,'近似值'),.4);
 const gather=prog(t,at(83,'为什么'),CH[6]-at(83,'为什么'));
 const speed=(t:number)=>60*t+40*Math.max(0,t-(at(75,'计算机')-CH[5]))**1.6;
 const off=speed(dt);
 const cols=Array.from({length:40},(_,k)=>k);
 return <AbsoluteFill><svg width={1920} height={1080}><rect width={1920} height={1080} fill={lerpCol(C.night,C.bg,clamp((gather-.7)/.3))}/>
  <g opacity={.5*(1-gather)}>{cols.map(k=>Array.from({length:24},(_,j)=>{const y=((j*48+off*(1+k%3*.3)+k*37)%1150)-50;const ch=PI[(k*7+j)%PI.length];
   return <text key={k+'_'+j} x={30+k*48} y={y} fontSize={30} fill={[C.teal,C.yel,'#9BD1FF','#fff'][(k+j)%4]} fontFamily="monospace" opacity={.6}>{ch}</text>;}))}</g>
  {pc>.05&&rec<.3&&<g opacity={pc}><rect x={760} y={330} width={400} height={260} rx={20} fill="#0E1A30" stroke={C.teal} strokeWidth={6}/><rect x={920} y={590} width={80} height={60} fill={C.teal}/><Tx x={960} y={460} s={54} c={C.yel}>3.14159…</Tx></g>}
  {rec>.05&&gather<.5&&years<.05&&<g opacity={rec}><rect x={460} y={340} width={1000} height={320} rx={40} fill="#1B2A4Aee" stroke={C.yel} strokeWidth={4}/>
   <Tx x={960} y={460} s={110} c={C.yel}>314万亿位小数</Tx><Tx x={960} y={580} s={40} c="#fff">截至2026年{days>.5?' · 一台计算机连续算了约110天':''}</Tx></g>}
  {years>.01&&inf<.3&&<g><Tx x={960} y={430} s={44} c="#fff">每秒念1位，314万亿位要念…</Tx><Tx x={960} y={540} s={110} c={C.yel}>{Math.round(years*1000)}万年</Tx></g>}
  {inf>.05&&gather<.3&&<g opacity={inf}><Tx x={960-((dt*200)%400)} y={540} s={70} c={C.yel} a="start">{'3.'+PI.slice(1,60)}</Tx>
   <Chip x={760} y={700} text="无限" s={48} bg={C.pink} a={inf}/><Chip x={1160} y={700} text="不循环" s={48} bg={C.teal} a={inf}/></g>}
  {approx>.05&&gather<.3&&<Chip x={960} y={380} text="3.14 只是近似值" s={52} bg={C.orange} a={approx}/>}
  {gather>.05&&<Tx x={960} y={520} s={lerp(80,420,gather)} c={lerpCol(C.yel,C.pink,gather)} f={'"Noto Serif CJK SC",serif'}>π</Tx>}
 </svg></AbsoluteFill>;
};
function lerpCol(a:string,b:string,p:number){p=clamp(p);const h=(s:string)=>[1,3,5].map(k=>parseInt(s.slice(k,k+2),16));const A=h(a),B=h(b);return '#'+A.map((v,k)=>Math.round(v+(B[k]-v)*p).toString(16).padStart(2,'0')).join('');}
