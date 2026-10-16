import React from 'react';
import {El,vis,prog,back,clamp,lerp,circleBox,Box} from './zones';
import {at,atEnd,ss,se,CH} from './timing';
import {E,title} from './common';
import {Card,Tx,P,SERIF} from './mat';
import {Portrait,Seal} from './obj';
import {poly,pts,morph} from './geo';
import {DISC} from './s012';
const PI=Math.PI;
const ROWS=[{n:6,v:'3.0000',sid:33,col:P.blue},{n:12,v:'3.1058',sid:34,col:P.teal},{n:24,v:'3.1326',sid:35,col:P.pink},{n:48,v:'3.1394',sid:36,col:P.orange},{n:96,v:'3.1410',sid:37,col:P.purple},{n:192,v:'≈3.1415',sid:38,col:P.ink}];
const GAPS=[0.1416,0.0358,0.0090,0.0022,0.0006,0.0001];
export const CH4HERO={cx:330,cy:580,r:170};
export const scene3=(t:number,out:El[])=>{
 if(t<CH[3]-.01||t>=CH[4]+.01)return;
 const {cx:X,cy:Y,r:R0}=DISC;
 // polygon stage
 const cut=prog(t,at(31,'切开'),atEnd(32,'十二条边')-at(31,'切开'));
 let shape:[number,number][];let col=P.blue;let label='6';
 const st=ROWS.reduce((s,row,i)=>t>=ss(row.sid)-.1?i:s,-1);
 if(st<0){shape=morph(6,cut,X,Y,R0);col=cut>.5?P.teal:P.blue;label=cut>.5?'12':'6';}
 else if(st===0){shape=poly(6,X,Y,R0);}
 else{const p=prog(t,ss(ROWS[st].sid)-.1,.6);shape=morph(ROWS[st-1].n,p,X,Y,R0);col=ROWS[st].col;label=String(ROWS[st].n);}
 if(st>=0&&st===0)col=P.blue;
 // final handover to chapter 4: more cuts, then shrink & move
 const more=prog(t,at(60,'一直'),1.2);
 if(t>=at(60,'一直'))shape=poly(768,X,Y,R0);
 const go=prog(t,CH[4]-1.3,1.3);
 const cx=lerp(X,CH4HERO.cx,go),cy=lerp(Y,CH4HERO.cy,go),r=lerp(R0,CH4HERO.r,go);const sc=r/R0;
 const tr=(p:[number,number][])=>p.map(v=>[cx+(v[0]-X)*sc,cy+(v[1]-Y)*sc] as [number,number]);
 // inner/outer (Archimedes) hexagons → 96-gons
 const inO=prog(t,at(54,'圆里面'),.6),outO=prog(t,at(54,'圆外面'),.6),to96=prog(t,at(55,'九十六'),.8),archEnd=1-prog(t,ss(56),.4);
 const archOn=t>=at(54,'圆里面')&&t<ss(56)+.4;const outerR=R0/Math.cos(PI/(to96>.5?96:6));
 const box:Box=archOn&&outO>0?circleBox(cx,cy,outerR):circleBox(cx,cy,r);
 const zoomMark=vis(t,at(44,'多边形'),ss(45));
 E(out,'disc','hero','stage',box,1,()=><g>
  <circle cx={cx} cy={cy} r={r} fill="#FFE7C2" filter="url(#shadow)"/>
  <polygon points={pts(tr(shape))} fill="#fffdf7" stroke={archOn?P.blue:col} strokeWidth={st>=4||more>0?3:6} strokeLinejoin="round" opacity={archOn?.9:1}/>
  <circle cx={cx} cy={cy} r={r} fill="none" stroke={P.ink} strokeWidth={4}/>
  <circle cx={cx} cy={cy} r={6} fill={P.ink}/>
  {archOn&&<g opacity={archEnd}><polygon points={pts(poly(to96>.5?96:6,cx,cy,R0))} fill="none" stroke={P.blue} strokeWidth={5} opacity={inO}/>
   <polygon points={pts(poly(to96>.5?96:6,cx,cy,outerR))} fill="none" stroke={P.orange} strokeWidth={5} opacity={outO}/></g>}
  {zoomMark>0&&<circle cx={cx} cy={cy-r} r={26} fill="none" stroke={P.pink} strokeWidth={5} opacity={zoomMark}/>}
  {go<.05&&st<0&&<Tx x={cx} y={cy} s={44} c={col} o={.0}>{label}</Tx>}
 </g>);
 // side panel shots -------------------------------------------------
 const table=(id:string,a:number)=>E(out,id,id,'side',[1180,250,660,620],a,()=><g><Card b={[1180,250,660,620]}/>
  <Tx x={1300} y={300} s={34}>边数</Tx><Tx x={1600} y={300} s={34}>周长 ÷ 直径</Tx><line x1={1210} y1={330} x2={1810} y2={330} stroke="#e3d8c4" strokeWidth={3}/>
  {ROWS.map((row,i)=>{const a=back(t,ss(row.sid),.35);const y=380+i*80;const on=t>=ss(row.sid);
   return <g key={i} opacity={on?clamp(a*2):0}>{i===st&&<rect x={1210} y={y-32} width={600} height={64} rx={14} fill="#eef4ff"/>}<Tx x={1300} y={y} s={46} c={row.col}>{row.n}</Tx><Tx x={1600} y={y} s={46} c={row.col}>{row.v}</Tx></g>;})}
  <g opacity={prog(t,at(39,'接近'),.4)}><Tx x={1510} y={845} s={30} c={P.pink}>π = 3.14159…</Tx></g></g>);
 table('table',vis(t,ss(33),ss(41)));
 E(out,'gaps','gaps','side',[1180,300,660,440],vis(t,ss(41),ss(42)),()=><g><Card b={[1180,300,660,440]}/>
  <Tx x={1510} y={350} s={30}>和 π 的差距（按比例）</Tx>
  {GAPS.map((g,i)=><g key={i}><Tx x={1260} y={410+i*52} s={26} c={ROWS[i].col}>{ROWS[i].n}</Tx><rect x={1310} y={398+i*52} width={Math.max(2,g*3800)} height={24} rx={4} fill={ROWS[i].col}/></g>)}
  <Tx x={1510} y={712} s={26} c={P.orange}>每翻一倍，差距约变成原来的四分之一</Tx></g>);
 table('table2',vis(t,ss(42),at(44,'多边形')));
 // zoom: 192-gon edge vs arc, magnified 200x (sagitta = r(1−cos(π/192)) ≈ 0.036 px × 200)
 const sag=R0*(1-Math.cos(PI/192))*200;
 E(out,'zoom','zoom','side',[1180,260,660,560],vis(t,at(44,'多边形'),ss(45)),()=><g><Card b={[1180,260,660,560]}/>
  <Tx x={1510} y={310} s={30}>放大200倍看192边形</Tx>
  <path d={'M'+Array.from({length:59},(_,i)=>{const x=-290+i*10;return (1510+x)+','+(560-sag*(1-(x/883)**2)).toFixed(2);}).join(' L')} fill="none" stroke={P.ink} strokeWidth={5}/>
  <line x1={1220} y1={560} x2={1800} y2={560} stroke={P.blue} strokeWidth={5}/>
  <Tx x={1510} y={640} s={28} c={P.blue}>蓝：多边形的边（在圆里面）</Tx><Tx x={1510} y={690} s={28}>黑：圆</Tx><Tx x={1510} y={760} s={30} c={P.pink}>永远小一点</Tx></g>);
 // Liu Hui shot
 E(out,'liu','liu','side',[1180,260,300,420],vis(t,ss(45),ss(53)),()=><Portrait href="img/liu-hui-portrait.jpg" b={[1180,260,300,420]} label="刘徽" sub="后人想象画像"/>);
 E(out,'book9','book9','side',[1540,260,300,420],vis(t,ss(45),at(51,'三点一四')),()=><Portrait href="img/nine-chapters-page.jpg" b={[1540,260,300,420]} label="《九章算术》注" sub="约公元263年"/>);
 E(out,'quote','quote','side',[1180,700,660,170],vis(t,at(47,'割之'),ss(50)),()=><g><Card b={[1180,700,660,170]} fill="#f3e6c8"/><Tx x={1510} y={750} s={42} f={SERIF}>割之弥细，所失弥少</Tx><g opacity={prog(t,ss(48),.4)}><Tx x={1510} y={815} s={28} c={P.orange}>切得越细，丢掉的就越少</Tx></g></g>);
 E(out,'vals','vals','side',[1540,260,300,420],vis(t,at(51,'三点一四'),ss(53)),()=><g><Card b={[1540,260,300,420]}/><Tx x={1690} y={330} s={28}>刘徽算出</Tx>
  <Tx x={1690} y={430} s={64} c={P.pink}>3.14</Tx><g opacity={prog(t,at(52,'三点一四一六'),.4)}><Tx x={1690} y={510} s={36}>↓</Tx><Tx x={1690} y={590} s={64} c={P.pink}>3.1416</Tx></g></g>);
 // Archimedes shot
 E(out,'arch','arch','side',[1180,260,300,420],vis(t,ss(53),ss(56)),()=><Portrait href="img/archimedes-fetti.jpg" b={[1180,260,300,420]} label="阿基米德" sub="后人想象画像 · 古希腊"/>);
 E(out,'bounds','bounds','side',[1540,260,300,420],vis(t,at(55,'九十六'),ss(56)),()=><g><Card b={[1540,260,300,420]}/><Tx x={1690} y={320} s={28}>96边形夹住圆</Tx>
  <Tx x={1690} y={410} s={50} c={P.blue}>3.1408</Tx><Tx x={1690} y={480} s={44}>{'< π <'}</Tx><Tx x={1690} y={550} s={50} c={P.orange}>3.1429</Tx><Tx x={1690} y={620} s={22} c="#6b6f80" w={500}>蓝：里面　橙：外面</Tx></g>);
 // both
 E(out,'both','both','side',[1180,260,660,600],vis(t,ss(56),ss(57)),()=><g><Portrait href="img/liu-hui-portrait.jpg" b={[1180,260,300,420]} label="刘徽" sub="中国 · 约263年"/><Portrait href="img/archimedes-fetti.jpg" b={[1540,260,300,420]} label="阿基米德" sub="古希腊 · 约前250年"/>
  <path d="M1330,720 Q1510,820 1690,720" fill="none" stroke={P.orange} strokeWidth={5} strokeDasharray="12 10"/><Tx x={1510} y={830} s={28} c={P.orange}>相隔很远</Tx></g>);
 // hands-on: notebook drawing hex → 12-gon
 const hp=prog(t,at(58,'六边形'),.9),hp2=prog(t,at(58,'十二边形'),.9),mids=prog(t,at(58,'中点'),.5);
 E(out,'hands','hands','side',[1180,260,660,600],vis(t,ss(57),ss(59)),()=>{const c=[1510,560],rr=220;return <g><Card b={[1180,260,660,600]}/>
  <circle cx={c[0]} cy={c[1]} r={rr} fill="none" stroke="#555" strokeWidth={3}/>
  <polygon points={pts(poly(6,c[0],c[1],rr))} fill="none" stroke={P.blue} strokeWidth={4} pathLength={1} strokeDasharray={`${hp} 1`}/>
  {poly(12,c[0],c[1],rr).filter((_,i)=>i%2===1).map((p,i)=><circle key={i} cx={p[0]} cy={p[1]} r={8} fill={P.pink} opacity={mids}/>)}
  <polygon points={pts(poly(12,c[0],c[1],rr))} fill="none" stroke={P.teal} strokeWidth={4} pathLength={1} strokeDasharray={`${hp2} 1`}/></g>;});
 // titles
 title(out,t,'t3a','把每段圆弧从中间切开',at(31,'切开'),ss(33));
 title(out,t,'t3b','边数翻倍，算一算',ss(33),at(39,'接近'));
 title(out,t,'t3c','越来越接近 π',at(39,'接近'),ss(40));
 title(out,t,'t3d','差距每次约缩小到四分之一',at(41,'四分之一'),ss(42));
 title(out,t,'t3e','永远比 π 小一点',at(43,'不会'),ss(45));
 title(out,t,'t3f','刘徽 · 约1700多年前',at(45,'刘徽'),ss(49));
 const sealA=vis(t,at(49,'割圆术'),ss(50));
 E(out,'seal','title:seal','title',[650,44,400,140],sealA,()=><Seal x={850} y={114} s={84} text="割圆术" a={back(t,at(49,'割圆术'),.4)}/>);
 title(out,t,'t3g','和刘徽一样的思路',at(50,'一样'),ss(53));
 title(out,t,'t3h','阿基米德 · 约公元前250年',at(53,'阿基米德'),ss(56));
 title(out,t,'t3i','同一个好主意',ss(56),ss(57));
 title(out,t,'t3j','动手试一试',ss(57),ss(59));
 title(out,t,'t3k','一直切下去呢？',ss(59),CH[4]);
};
