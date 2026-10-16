import React from 'react';
import {staticFile} from 'remotion';
import {El,vis,prog,back,clamp,lerp,circleBox,Box} from './zones';
import {at,atEnd,ss,se,CH} from './timing';
import {E,title} from './common';
import {Card,Tx,P,SERIF} from './mat';
import {Wheel,Lid,Coin,Bowl,RopePath,arcPath,Ruler,Seal,Cross} from './obj';
import {poly,pts} from './geo';
const PI=Math.PI;
// ---------------- chapter 0 + hero handover into chapter 1/2 ----------------
const D=240,R=120,X0=180,GY=740,LEN=PI*D;      // road: rolled track = π × D, bars = D, extra = 0.1416 D
export const LID={cx:580,cy:560,r:150};          // cup lid, rope = 2π r = 942 px (fits stage)
export const DISC={cx:580,cy:560,r:270};         // chapter 2/3 circle
export const scene0=(t:number,out:El[])=>{
 const roll=prog(t,at(0,'车轮'),atEnd(0,'多远')-at(0,'车轮'));
 const toLid=prog(t,at(5,'我们'),atEnd(5,'量一量')-at(5,'我们'));
 const roadA=vis(t,0,at(5,'我们')+.4,.01,.4);
 const bars=prog(t,at(1,'三倍'),.9),extra=prog(t,at(1,'一小截'),.5);
 // road + track + bars (one object group with the wheel)
 E(out,'road','hero','stage',[60,500,1040,360],roadA,()=><g>
  <rect x={60} y={GY} width={1040} height={60} rx={10} fill="url(#asphalt)" filter="url(#shadow)"/>
  <line x1={X0} y1={GY+2} x2={X0+LEN*roll} y2={GY+2} stroke={P.orange} strokeWidth={10} strokeLinecap="round"/>
  <g opacity={1-roll*.7}><circle cx={X0} cy={GY-R} r={R} fill="none" stroke="#fff" strokeWidth={4} strokeDasharray="10 8"/></g>
  {[P.blue,P.teal,P.pink].map((c,i)=><g key={i} opacity={clamp(bars*3-i)}><rect x={X0+i*D+2} y={GY+70} width={D-4} height={22} rx={8} fill={c} filter="url(#shadowS)"/><Tx x={X0+i*D+D/2} y={GY+112} s={26} c="#fff" stroke={P.ink} sw={5}>1个直径</Tx></g>)}
  <g opacity={extra}><rect x={X0+3*D} y={GY+70} width={.1416*D} height={22} fill={P.yel} stroke={P.orange} strokeWidth={3}/></g>
 </g>);
 if(t<CH[2]){
  // wheel rolls, then becomes the cup lid (same object, morph)
  const wx=X0+LEN*roll,wy=GY-R;const cx=lerp(wx,LID.cx,toLid),cy=lerp(wy,LID.cy,toLid),r=lerp(R,LID.r,toLid);
  if(t<CH[1]+.01) E(out,'wheel','hero','stage',circleBox(cx,cy,r),1,()=><g><Wheel cx={cx} cy={cy} r={r} rot={roll*360+toLid*90} o={1-toLid}/><Lid cx={cx} cy={cy} r={r} o={toLid}/></g>);
 }
 title(out,t,'t0a','车轮滚一圈，走了多远？',ss(0),ss(3));
 title(out,t,'t0b','人类算了几千年',at(3,'几千年'),ss(5));
 title(out,t,'t0c','一起动手量一量',at(5,'量一量')-.2,CH[1]+.6);
 const side=vis(t,at(1,'一小截'),ss(3));
 E(out,'gapNote','gapNote','side',[1180,480,660,300],side,()=><g><Card b={[1180,480,660,300]}/>
  <Tx x={1510} y={560} s={40}>3个直径 + 一小截</Tx>
  <rect x={1290} y={620} width={3*90} height={22} fill={P.blue} rx={6}/><rect x={1290+270} y={620} width={.1416*90} height={22} fill={P.yel} stroke={P.orange} strokeWidth={2}/>
  <Tx x={1510} y={700} s={32} c={P.orange}>{t>=at(2,'到底')?'这一小截 = ？':'一小截 ≈ 0.14个直径'}</Tx></g>);
};
// ---------------- chapter 1 ----------------
export const scene1=(t:number,out:El[])=>{
 if(t<CH[1]-.01||t>=CH[2]+.6)return;
 const {cx,cy,r}=LID;
 const wrap=prog(t,at(6,'绕'),atEnd(6,'一圈')-at(6,'绕')),unroll=prog(t,at(6,'拉直'),.9);
 const toDisc=prog(t,at(16,'他们'),CH[2]-at(16,'他们'));
 const diam=prog(t,at(7,'直径'),.5);
 const R2=lerp(r,DISC.r,toDisc);
 E(out,'lid','hero','stage',circleBox(cx,cy,R2),1,()=><g>
  <Lid cx={cx} cy={cy} r={R2} o={1-toDisc}/>
  <circle cx={cx} cy={cy} r={R2} fill="#fffdf7" opacity={toDisc} filter="url(#shadow)"/><circle cx={cx} cy={cy} r={R2} fill="url(#paperTex)" opacity={toDisc*.4}/><circle cx={cx} cy={cy} r={R2} fill="none" stroke={P.ink} strokeWidth={5} opacity={toDisc}/>
  <g opacity={diam*(1-toDisc)}><line x1={cx-r} y1={cy} x2={cx+r} y2={cy} stroke={P.ink} strokeWidth={5}/><Tx x={cx} y={cy-26} s={30} c={P.ink}>直径</Tx></g>
  {t<ss(9)&&<RopePath d={arcPath(cx,cy,r+9,PI/2+2*PI*unroll,PI/2+2*PI*Math.max(unroll+.0001,wrap))} o={vis(t,ss(6),ss(9))}/>}
 </g>);
 const ropeA=vis(t,at(6,'拉直'),ss(9));
 E(out,'ropeLine','hero','stage',[100,790,960,70],ropeA,()=>{const L=2*PI*r;return <g><RopePath d={`M${109},${845} L${109+L*unroll},${845}`}/><Tx x={580} y={808} s={30} c="#fff" stroke={P.ink} sw={6}>周长（绳子拉直）</Tx></g>;});
 E(out,'lidBadge','hero','stage',[520,724,120,62],vis(t,at(8,'三点一四'),ss(9)),()=><g><rect x={520} y={724} width={120} height={62} rx={31} fill={P.blue} filter="url(#shadowS)"/><Tx x={580} y={756} s={38} c="#fff">3.14</Tx></g>);
 // side: coin & bowl (real-object look), their measured ratios
 const sa=vis(t,at(9,'硬币'),ss(12));
 E(out,'samples','samples','side',[1180,270,660,560],sa,()=><g><Card b={[1180,270,660,560]}/>
  <Coin cx={1300} cy={480} r={60}/><Tx x={1300} y={580} s={30}>硬币</Tx><rect x={1245} y={620} width={110} height={56} rx={28} fill={P.orange}/><Tx x={1300} y={650} s={34} c="#fff">3.13</Tx>
  <Bowl cx={1640} cy={470} r={170}/><Tx x={1640} y={670} s={30}>碗口</Tx><rect x={1585} y={710} width={110} height={56} rx={28} fill={P.teal}/><Tx x={1640} y={740} s={34} c="#fff">3.15</Tx></g>);
 // lid label under lid
 E(out,'lidName','hero','stage',[520,790,120,50],vis(t,at(9,'硬币'),ss(12)),()=><Tx x={580} y={815} s={32}>杯盖</Tx>);
 E(out,'lidBadge2','hero','stage',[520,724,120,62],vis(t,at(9,'硬币'),ss(12)),()=><g><rect x={520} y={724} width={120} height={62} rx={31} fill={P.blue}/><Tx x={580} y={756} s={38} c="#fff">3.14</Tx></g>);
 // ratio bars to scale: C = π d, d grows
 const g=prog(t,at(13,'变长'),1.4);const d=lerp(80,160,g);
 E(out,'bars','bars','side',[1180,360,660,360],vis(t,ss(12),ss(14)),()=><g><Card b={[1180,360,660,360]}/>
  <Tx x={1220} y={440} s={30} a="start">周长</Tx><rect x={1310} y={425} width={PI*d} height={30} rx={8} fill={P.orange}/>
  <Tx x={1220} y={520} s={30} a="start">直径</Tx><rect x={1310} y={505} width={d} height={30} rx={8} fill={P.teal}/>
  <Tx x={1510} y={640} s={40} c={P.pink}>周长 ÷ 直径 一直 ≈ 3.14</Tx></g>);
 E(out,'ruler','ruler','side',[1220,420,580,220],vis(t,at(16,'尺子'),CH[2]-.2),()=><g><Ruler x={1240} y={480} w={540} h={80}/><Cross x={1510} y={520} s={70} p={prog(t,at(16,'尺子')+.3,.5)}/></g>);
 title(out,t,'t1a',t>=at(8,'三点一四')?'周长 ÷ 直径 = 3.14':'周长 ÷ 直径',at(7,'除以'),ss(9));
 title(out,t,'t1b','周长 ÷ 直径 ≈ 3.1',at(9,'三点一'),ss(14));
 title(out,t,'t1c','这个不变的数：圆周率 π',at(14,'圆周率'),ss(15));
 title(out,t,'t1d','π ≈ 3.14',at(15,'约等于'),ss(16));
 title(out,t,'t1e','古人没有精确的尺子',at(16,'古人'),CH[2]);
};
// ---------------- chapter 2 ----------------
export const scene2=(t:number,out:El[])=>{
 if(t<CH[2]-.01||t>=CH[3]+.01)return;
 const {cx,cy,r}=DISC;const hex=poly(6,cx,cy,r);
 const hx=prog(t,at(21,'六边形'),.9),rad=prog(t,at(22,'每条边'),1),cres=prog(t,at(26,'抄了近路'),.7),mids=prog(t,at(29,'再多'),.5);
 E(out,'disc','hero','stage',circleBox(cx,cy,r),1,()=><g>
  <circle cx={cx} cy={cy} r={r} fill="#fffdf7" filter="url(#shadow)"/><circle cx={cx} cy={cy} r={r} fill="url(#paperTex)" opacity={.4}/>
  {cres>0&&hex.map((p,i)=>{const q=hex[(i+1)%6];return <path key={i} d={`M${p[0]},${p[1]} A${r},${r} 0 0 1 ${q[0]},${q[1]} Z`} fill={P.yel} opacity={.55*cres}/>;})}
  <circle cx={cx} cy={cy} r={r} fill="none" stroke={P.ink} strokeWidth={5}/>
  <polygon points={pts(hex)} fill="none" stroke={P.blue} strokeWidth={7} pathLength={1} strokeDasharray={`${hx} 1`} strokeLinejoin="round"/>
  {hex.map((p,i)=><g key={i} opacity={clamp(rad*6-i)}><line x1={cx} y1={cy} x2={p[0]} y2={p[1]} stroke={P.teal} strokeWidth={4} strokeDasharray="10 8"/><circle cx={p[0]} cy={p[1]} r={8} fill={P.orange}/></g>)}
  <circle cx={cx} cy={cy} r={7} fill={P.ink}/>
  {mids>0&&hex.map((_,i)=>{const a=-PI/2+PI/6+i*PI/3;return <circle key={'m'+i} cx={cx+r*Math.cos(a)} cy={cy+r*Math.sin(a)} r={9+3*Math.sin(t*8)} fill={P.pink} opacity={mids}/>;})}
 </g>);
 E(out,'book','book','side',[1180,260,320,440],vis(t,ss(17),ss(21)),()=><g><Card b={[1180,260,320,440]} fill="#f3e6c8"/>
  <image href={staticFile('img/zhoubi-gougu-diagram.png')} x={1210} y={290} width={260} height={260} preserveAspectRatio="xMidYMid slice"/><Tx x={1340} y={600} s={34} f={SERIF}>《周髀算经》</Tx><Tx x={1340} y={650} s={22} c="#6b6f80" w={500}>两千多年前的古书</Tx></g>);
 E(out,'seals','seals','side',[1540,280,300,300],vis(t,at(17,'四个字'),ss(21)),()=><g>{['周','三','径','一'].map((ch,i)=>{const a=back(t,at(18,ch),.35);return <g key={i} opacity={clamp(a*2)}><Seal x={1615+(i%2)*150} y={355+Math.floor(i/2)*150} s={96} text={ch} a={a}/></g>;})}</g>);
 // side: to-scale comparison, k = 0.4  (edge = r k = 108, diameter = 216, circumference = π·2r·k ≈ 678.6)
 const k=.36,e=r*k;const sa=vis(t,at(23,'六条边'),at(29,'再多')+.3);
 const dA=prog(t,at(23,'三个直径'),.6),cA=prog(t,at(26,'拐弯'),.6);
 E(out,'sticks','sticks','side',[1170,290,690,310],sa,()=><g><Card b={[1170,290,690,310]}/>
  <Tx x={1205} y={322} s={24} a="start">6条边</Tx>{[0,1,2,3,4,5].map(i=><rect key={i} x={1200+i*e} y={340} width={e-3} height={18} rx={4} fill={P.blue}/>)}
  <g opacity={dA}><Tx x={1205} y={402} s={24} a="start">3个直径</Tx>{[0,1,2].map(i=><rect key={i} x={1200+i*2*e} y={420} width={2*e-3} height={18} rx={4} fill={[P.blue,P.teal,P.pink][i]}/>)}</g>
  <g opacity={cA}><Tx x={1205} y={482} s={24} a="start">圆的周长（更长）</Tx><rect x={1200} y={500} width={PI*2*r*k} height={18} rx={4} fill={P.orange}/></g></g>);
 title(out,t,'t2a','周长 ≈ 3 × 直径',at(19,'意思'),ss(20));
 title(out,t,'t2b','为什么是 3？',ss(20),ss(24));
 title(out,t,'t2c','六边形抄了近路',at(26,'因为'),ss(27));
 title(out,t,'t2d','π > 3',at(27,'一定'),ss(28));
 title(out,t,'t2e','再多几条边呢？',ss(28),CH[3]+.4);
};
