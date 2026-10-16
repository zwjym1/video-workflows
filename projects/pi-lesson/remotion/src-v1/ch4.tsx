import React from 'react';
import {AbsoluteFill,staticFile} from 'remotion';
import {C,Tx,useT,prog,back,clamp,lerp} from './ui';
import {at,atEnd,ss,se} from './timing';
import {Chip,Img2,Cross,Check} from './parts';
// 算筹: digits 3 1 4 1 5 9 2 6; from units (rightmost) vertical, then horizontal alternating
const DIG=[3,1,4,1,5,9,2,6];
const ROD=(x:number,y:number,w:number,h:number,k:string)=><rect key={k} x={x} y={y} width={w} height={h} rx={5} fill={C.rod} stroke={C.rodEdge} strokeWidth={2}/>;
const rodDigit=(d:number,vertical:boolean,cx:number,cy:number,key:string)=>{const out:React.ReactNode[]=[];const L=90,T=12,G=20;
 if(vertical){const n=d>5?d-5:d;const w=(n-1)*G;for(let i=0;i<n;i++)out.push(ROD(cx-w/2+i*G-T/2,cy-L/2+(d>5?14:0),T,L-(d>5?14:0),key+'v'+i));if(d>5)out.push(ROD(cx-L/2+10,cy-L/2-8,L-20,T,key+'h5'));}
 else{const n=d>5?d-5:d;const h=(n-1)*G;for(let i=0;i<n;i++)out.push(ROD(cx-L/2,cy-h/2+i*G-T/2+(d>5?18:0),L,T,key+'h'+i));if(d>5)out.push(ROD(cx-T/2,cy-h/2-60+18,T,44,key+'v5'));}
 return out;};
const SPOKEN='三点一四一五九二六';
export const Ch4:React.FC=()=>{
 const t=useT();
 const zu=prog(t,at(62,'祖冲之'),.6);
 const noCalc=prog(t,at(64,'计算器'),.6);
 const rods=prog(t,at(64,'算筹'),.6);
 const full=prog(t,at(65,'摆满'),1.3);
 const seven=back(t,at(67,'七位'),.45);
 const early=prog(t,at(68,'一千年'),.6);
 const field=prog(t,at(70,'操场'),.6);
 const sand=prog(t,at(70,'一粒沙子'),.6);
 const remember=prog(t,at(71,'要记住'),.5);
 const better=prog(t,at(71,'算得更准'),.5);
 const more=prog(t,at(73,'还能'),1.2);
 const digitT=[...SPOKEN].map((_,k)=>atEnd(66,SPOKEN.slice(0,k+1)));
 const digitIdx=[0,2,3,4,5,6,7,8]; // skip 点
 const scatter=Array.from({length:120},(_,k)=>{const r=(n:number)=>((Math.sin(k*12.9898+n*78.233)*43758.5453)%1+1)%1;return {x:180+r(1)*1560,y:360+r(2)*440,a:r(3)*180,d:r(4)};});
 const table=1-field*(1-remember);
 return <AbsoluteFill><svg width={1920} height={1080}><rect width={1920} height={1080} fill={lerpCol(C.paper,C.night,more)}/>
  <g opacity={(1-more)*table}><rect x={100} y={300} width={1720} height={600} rx={36} fill={C.wood}/>{Array.from({length:18},(_,k)=><line key={k} x1={120+k*95} y1={310} x2={160+k*95} y2={890} stroke={C.woodDark} strokeWidth={3} opacity={.4}/>)}
   {scatter.map((s,k)=>{const show=k<12?rods:clamp(full*1.2-(k/120));if(show<=0)return null;const dy=(1-show)*-300;
    return <rect key={k} x={s.x} y={s.y+dy} width={100} height={12} rx={5} fill={C.rod} stroke={C.rodEdge} strokeWidth={2} transform={`rotate(${s.a} ${s.x+50} ${s.y+dy+6})`} opacity={show*(t>at(66,'终于')?.25:1)}/>;})}
   {DIG.map((d,i)=>{const tt=digitT[digitIdx[i]];const a=prog(t,tt-.2,.3);const vertical=(DIG.length-1-i)%2===0;const cx=420+i*150,cy=620;
    return <g key={i} opacity={a}>{rodDigit(d,vertical,cx,cy,'d'+i)}<Tx x={cx} y={470} s={60} c={C.yel} stroke={C.ink} sw={6}>{String(d)}</Tx></g>;})}
   {t>digitT[0]&&<circle cx={495} cy={500} r={8} fill={C.yel} opacity={prog(t,digitT[0],.3)}/>}
  </g>
  <g opacity={zu*(1-field)*(1-more)}><Img2 href={staticFile('img/zu-chongzhi-bronze.jpg')} x={1580} y={40} w={240} h={240}/><Tx x={1700} y={300-10} s={22} c={C.ink}>祖冲之（后人塑像）</Tx>
   <Chip x={960} y={150} text="祖冲之 · 南北朝 · 约1500年前" s={42} bg={C.blue} a={zu}/></g>
  {noCalc>.05&&noCalc<1.01&&t<at(66,'终于')&&<g opacity={1-full}><rect x={300} y={90} width={110} height={150} rx={14} fill={C.grey}/><Cross x={355} y={165} s={60} p={noCalc}/></g>}
  {t>=at(66,'大于')&&<g opacity={(1-field)*(1-more)}><Tx x={960} y={250} s={56} c={C.ink}>3.1415926 {'<'} π {'<'} 3.1415927</Tx></g>}
  {seven>.05&&<g opacity={(1-field)*(1-more)}><Chip x={960} y={830} text="小数点后 7 位" s={46} bg={C.pink} a={seven}/></g>}
  {early>.05&&<g opacity={early*(1-field)*(1-more)}><Chip x={1500} y={830} text="比国外早约1000年" s={36} bg={C.teal} a={early}/></g>}
  {/* playground */}
  {field>.02&&<g opacity={field*(1-remember)}><rect width={1920} height={1080} fill="#8FD694"/>
   <circle cx={620} cy={540} r={330} fill="none" stroke="#D9534F" strokeWidth={40}/><circle cx={620} cy={540} r={330} fill="none" stroke="#fff" strokeWidth={3}/>
   <line x1={290} y1={540} x2={950} y2={540} stroke="#fff" strokeWidth={4} strokeDasharray="14 10"/><Tx x={620} y={510} s={40} c="#fff" stroke={C.ink} sw={5}>直径100米</Tx>
   {sand>.05&&<g opacity={sand}><circle cx={1440} cy={520} r={260} fill="#FFF8EC" stroke={C.ink} strokeWidth={8}/><line x1={950} y1={540} x2={1180} y2={520} stroke={C.ink} strokeWidth={6}/>
    <circle cx={1440} cy={520} r={90} fill="#E8C98A" stroke="#B8935A" strokeWidth={4}/><Tx x={1440} y={660} s={30} c={C.ink}>一粒沙 ≈ 0.5毫米</Tx>
    <rect x={1440-1} y={420} width={2} height={20} fill="#D7263D"/><Tx x={1440} y={395} s={26} c="#D7263D">误差 &lt; 0.01毫米</Tx></g>}
  </g>}
  {remember>.05&&<g opacity={remember*(1-more)}><rect x={560} y={380} width={800} height={280} rx={30} fill="#fff" stroke={C.ink} strokeWidth={5}/>
   <Tx x={760} y={470} s={60} c={C.ink}>发现</Tx><Cross x={900} y={470} s={36} p={remember}/>
   <Tx x={860} y={580} s={60} c={C.ink}>算得更准</Tx><Check x={1100} y={575} s={40} p={better}/></g>}
  {more>.05&&<Tx x={960} y={300} s={64} c={C.yel}>{'3.1415926'+'535897932384626'.slice(0,Math.floor(more*15))+'…'}</Tx>}
 </svg></AbsoluteFill>;
};
function lerpCol(a:string,b:string,p:number){p=clamp(p);const h=(s:string)=>[1,3,5].map(k=>parseInt(s.slice(k,k+2),16));const A=h(a),B=h(b);return '#'+A.map((v,k)=>Math.round(v+(B[k]-v)*p).toString(16).padStart(2,'0')).join('');}
