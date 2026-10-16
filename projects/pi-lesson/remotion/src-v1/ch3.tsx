import React from 'react';
import {AbsoluteFill,staticFile} from 'remotion';
import {C,GridBg,Tx,useT,prog,back,clamp,poly,pts,morph,lerp} from './ui';
import {at,atEnd,ss,se} from './timing';
import {Chip,Img2,Seal} from './parts';
const CX=520,CY=520,R=340;
const ROWS: {n:number;v:string;ph:string;sid:number;col:string}[]=[
 {n:6,v:'3.0000',ph:'是三',sid:33,col:C.blue},
 {n:12,v:'3.1058',ph:'三点一零五八',sid:34,col:C.teal},
 {n:24,v:'3.1326',ph:'三点一三二六',sid:35,col:C.pink},
 {n:48,v:'3.1394',ph:'三点一三九四',sid:36,col:C.orange},
 {n:96,v:'3.1410',ph:'三点一四一零',sid:37,col:C.purple},
 {n:192,v:'≈3.1415',ph:'三点一四一五',sid:38,col:C.ink},
];
export const Ch3:React.FC=()=>{
 const t=useT();
 // which polygon stage is active
 let stage=0;for(let i=0;i<ROWS.length;i++)if(t>=ss(ROWS[i].sid)-.15)stage=i;
 // better: morph 6→12 during s31, then snap higher
 const m12=prog(t,at(31,'切开'),atEnd(32,'十二条边')-at(31,'切开'));
 const curN=stage===0?6:ROWS[stage].n;
 const ptsNow=stage===0?poly(6,CX,CY,R):stage===1?morph(6,m12,CX,CY,R):poly(curN,CX,CY,R);
 const rowA=ROWS.map(r=>back(t,ss(r.sid),.35));
 const near=prog(t,at(39,'接近'),.5);
 const q1=prog(t,at(41,'四分之一'),.5);
 const never=prog(t,at(43,'不会'),.4);
 const liu=prog(t,at(45,'刘徽'),.6);
 const quote=prog(t,at(47,'割之弥细'),1);
 const method=back(t,at(49,'割圆术'),.45);
 const same=prog(t,at(50,'一样的思路'),.5);
 const v314=back(t,at(51,'三点一四'),.4);
 const v1416=back(t,at(52,'三点一四一六'),.4);
 const arch=prog(t,at(53,'阿基米德'),.6);
 const clampV=prog(t,at(54,'夹在中间'),.8);
 const far=prog(t,at(56,'同一个好主意'),.5);
 const hand=prog(t,at(58,'画个圆'),.8);
 const keep=prog(t,at(60,'一直切下去'),.7);
 return <AbsoluteFill><svg width={1920} height={1080}><GridBg/>
  {/* left circle */}
  <circle cx={CX} cy={CY} r={R} fill="#FFE7C2"/><circle cx={CX} cy={CY} r={R} fill="none" stroke={C.ink} strokeWidth={6}/>
  <polygon points={pts(ptsNow)} fill="none" stroke={ROWS[stage].col} strokeWidth={stage>=4?4:7}/>
  {stage>=1&&<polygon points={pts(poly(6,CX,CY,R))} fill="none" stroke={C.blue} strokeWidth={2} opacity={.25}/>}
  <circle cx={CX} cy={CY} r={8} fill={C.ink}/>
  {/* crescents hint for early stages */}
  {stage<2&&m12<.95&&<polygon points={pts(poly(6,CX,CY,R))} fill="none" stroke={C.blue} strokeWidth={3} opacity={.4}/>}
  {/* table */}
  <g><rect x={1000} y={120} width={840} height={720} rx={28} fill="#fff" stroke={C.ink} strokeWidth={4}/>
   <Tx x={1100} y={170} s={40} c={C.ink} a="start">边数</Tx><Tx x={1400} y={170} s={40} c={C.ink} a="start">周长 ÷ 直径</Tx>
   <line x1={1020} y1={200} x2={1820} y2={200} stroke={C.grid} strokeWidth={3}/>
   {ROWS.map((r,i)=>{const a=rowA[i];const y=240+i*95;
    return <g key={i} opacity={a}><rect x={1020} y={y-36} width={800} height={80} rx={16} fill={i===stage?'#F3F7FF':'#fff'}/>
     <Tx x={1100} y={y} s={54} c={r.col} a="start">{r.n}</Tx><Tx x={1400} y={y} s={54} c={r.col} a="start">{r.v}</Tx></g>;})}
   <g opacity={near}><Tx x={1420} y={800} s={36} c={C.pink}>π = 3.14159…</Tx><line x1={1380} y1={240} x2={1380} y2={760} stroke={C.pink} strokeWidth={3} strokeDasharray="6 8" opacity={.5}/></g>
  </g>
  {/* gap bars */}
  {q1>.1&&<g opacity={q1}><Tx x={200} y={920} s={36} c={C.ink} a="start">差距 ≈ ÷4</Tx>
   {[0.1416,0.0358,0.0090].map((g,i)=><rect key={i} x={420} y={900+i*28} width={g*1800} height={18} fill={[C.blue,C.teal,C.pink][i]}/>)}</g>}
  {never>.1&&<Chip x={CX} y={120} text="永远小一点" s={44} bg={C.teal} a={never}/>}
  {/* Liu Hui */}
  {liu>.05&&<g opacity={liu}><Img2 href={staticFile('img/liu-hui-portrait.jpg')} x={80} y={80} w={140} h={170}/><Tx x={150} y={270} s={22} c={C.ink}>刘徽（后人想象像）</Tx>
   <Img2 href={staticFile('img/nine-chapters-page.jpg')} x={250} y={80} w={120} h={170}/></g>}
  {quote>.05&&<g opacity={quote}><rect x={80} y={320} width={420} height={160} rx={20} fill={C.paper} stroke={C.ink} strokeWidth={3}/>
   <Tx x={290} y={370} s={40} c={C.ink} f={'"Noto Serif CJK SC",serif'}>割之弥细，所失弥少</Tx>
   <Tx x={290} y={430} s={30} c={C.orange}>切得越细，丢掉的就越少</Tx></g>}
  {method>.05&&<Seal x={700} y={200} ch="割圆术" s={160} a={method}/>}
  {same>.1&&<line x1={220} y1={250} x2={CX} y2={CY-R} stroke={C.blue} strokeWidth={4} opacity={same} strokeDasharray="10 8"/>}
  {(v314>.1||v1416>.1)&&<Chip x={CX} y={CY+R+50} text={v1416>.5?'3.14 → 3.1416':'≈ 3.14'} s={48} bg={C.pink} a={Math.max(v314,v1416)}/>}
  {/* Archimedes */}
  {arch>.05&&<g opacity={arch}><Img2 href={staticFile('img/archimedes-fetti.jpg')} x={1500} y={40} w={160} h={210}/><Tx x={1580} y={270} s={22} c={C.ink}>阿基米德</Tx></g>}
  {clampV>.1&&(()=>{const out=poly(96,CX,CY,R*1.045);const inn=poly(96,CX,CY,R);
   return <g opacity={clampV}><polygon points={pts(out)} fill="none" stroke={C.orange} strokeWidth={3}/><polygon points={pts(inn)} fill="none" stroke={C.blue} strokeWidth={3}/>
    <Chip x={CX} y={80} text="3.1408 ～ 3.1429" s={40} bg={C.yel} fg={C.ink} a={clampV}/></g>;})()}
  {far>.1&&<g opacity={far}><Tx x={960} y={1000} s={36} c={C.ink}>相隔很远，想到同一个主意</Tx></g>}
  {hand>.1&&<g opacity={hand}><Tx x={1600} y={900} s={40} c={C.orange}>动手试 →</Tx></g>}
  {keep>.2&&<g opacity={keep}><circle cx={CX} cy={CY} r={R} fill="none" stroke={C.ink} strokeWidth={4}/><polygon points={pts(poly(192,CX,CY,R))} fill="none" stroke={C.ink} strokeWidth={2}/></g>}
 </svg></AbsoluteFill>;
};
