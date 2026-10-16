import React from 'react';
import {staticFile} from 'remotion';
import {El,vis,prog,back,clamp,lerp,circleBox,Box} from './zones';
import {at,atEnd,ss,se,CH,DUR} from './timing';
import {E,title} from './common';
import {Card,Tx,P,SERIF,FONT} from './mat';
import {Portrait,Rod,RodDigit,Calculator,Monitor,Cross,Check,Wheel} from './obj';
import {poly,pts} from './geo';
import {CH4HERO} from './s3';
const PI=Math.PI;
const PIDIG='3141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148086513282306647093844609550582231725359408128481117450284102701938521105559644622948954930381964428810975665933446128475648233786783165271201909145648566923460348610454326648213393607260249141273';
const rnd=(k:number,n:number)=>((Math.sin(k*12.9898+n*78.233)*43758.5453)%1+1)%1;
const DIG=[3,1,4,1,5,9,2,6];
export const scene4=(t:number,out:El[])=>{
 if(t<CH[4]-.01||t>=CH[5]+.01)return;
 const {cx,cy,r}=CH4HERO;
 const nShow=Math.min(768*2**Math.floor(clamp((t-at(63,'继续'))/0.8,0,4)),12288);
 E(out,'hero4','hero','stage',[cx-r,cy-r-70,2*r,2*r+70],vis(t,CH[4]-.02,ss(64),.01),()=><g>
  <circle cx={cx} cy={cy} r={r} fill="#FFE7C2" filter="url(#shadow)"/><polygon points={pts(poly(Math.min(nShow,768),cx,cy,r))} fill="#fffdf7" stroke={P.ink} strokeWidth={2}/>
  <circle cx={cx} cy={cy} r={r} fill="none" stroke={P.ink} strokeWidth={4}/>
  {t>=at(63,'继续')&&<Tx x={cx} y={cy-r-36} s={30} c="#fff" stroke={P.ink} sw={6}>{'边数 '+nShow+' …'}</Tx>}</g>);
 E(out,'zu','zu','side',[1300,250,400,600],vis(t,at(62,'祖冲之'),ss(64)),()=><Portrait href="img/zu-chongzhi-bronze.jpg" b={[1300,250,400,600]} label="祖冲之" sub="后人塑像"/>);
 E(out,'calc','calc','side',[1180,270,320,420],vis(t,at(64,'计算器'),ss(66)),()=><g><Calculator x={1200} y={290} w={280} h={380}/><Cross x={1340} y={480} s={90} p={prog(t,at(64,'计算器')+.2,.5)}/></g>);
 // rods: scattered rods fill the table, then 8 digits laid out in rod numerals
 const fill=prog(t,at(65,'摆满'),1.4),first=prog(t,at(64,'算筹'),.5),done=t>=at(66,'终于');
 const SP='三点一四一五九二六';const dt=[0,2,3,4,5,6,7,8].map(k=>atEnd(66,SP.slice(0,k+1)));
 E(out,'rods','rods','stage',[60,240,1040,640],vis(t,at(64,'算筹'),ss(69)),()=><g>
  {Array.from({length:140},(_,k)=>{const show=k<10?first:clamp(fill*1.25-k/140);if(show<=0)return null;const x=110+rnd(k,1)*900,y=300+rnd(k,2)*520;const v=rnd(k,3)>.5;
   return <Rod key={k} x={x} y={y-(1-show)*120} len={90} vertical={v} rot={(rnd(k,4)-.5)*30} o={show*(done?.18:1)}/>;})}
  {DIG.map((d,i)=>{const a=prog(t,dt[i]-.25,.3);const vertical=(DIG.length-1-i)%2===0;const x=160+i*120;
   return <g key={i} opacity={a}><RodDigit d={d} vertical={vertical} cx={x} cy={640}/><Tx x={x} y={430} s={64} c={P.yel} stroke={P.ink} sw={8}>{String(d)}</Tx></g>;})}
  {t>=dt[0]&&<circle cx={220} cy={450} r={8} fill={P.yel} stroke={P.ink} strokeWidth={3} opacity={prog(t,dt[0],.3)}/>}
 </g>);
 E(out,'steps','steps','side',[1540,270,300,180],vis(t,at(65,'每算'),ss(66)),()=><g><Card b={[1540,270,300,180]}/><Tx x={1690} y={330} s={28}>第几步？</Tx><Tx x={1690} y={395} s={52} c={P.orange}>{'第'+Math.max(1,Math.round(fill*60))+'步'}</Tx></g>);
 E(out,'seven','seven','side',[1180,280,660,160],vis(t,at(67,'七位'),ss(69)),()=><g><Card b={[1180,280,660,160]}/><Tx x={1510} y={360} s={52} c={P.pink}>小数点后 7 位</Tx></g>);
 E(out,'early','early','side',[1180,480,660,320],vis(t,at(68,'一千年'),ss(69)),()=>{const x0=1240,x1=1780,y=640;const sx=(yr:number)=>x0+(yr-400)/(1700-400)*(x1-x0);return <g><Card b={[1180,480,660,320]}/>
  <line x1={x0} y1={y} x2={x1} y2={y} stroke={P.ink} strokeWidth={4}/><circle cx={sx(480)} cy={y} r={12} fill={P.red}/><Tx x={sx(480)+10} y={y-40} s={24}>祖冲之 约480年</Tx>
  <circle cx={sx(1500)} cy={y} r={12} fill={P.blue}/><Tx x={sx(1500)-20} y={y+40} s={24}>欧洲 约1500年后</Tx>
  <Tx x={1510} y={540} s={34} c={P.teal}>早约1000年</Tx></g>;});
 // playground to scale (100 m → 580 px) and sand grain loupe (0.5 mm grain vs < 0.01 mm error, same scale inside loupe)
 // round plaza, 100 m across, to scale: 5.2 px per metre; person 1.7 m
 const M=5.2,FX=580,FY=560,PR=50*M;const cP=prog(t,at(70,'广场')+.3,.8);
 E(out,'field','field','stage',[FX-300,FY-300,600,600],vis(t,at(70,'广场'),ss(71)),()=><g>
  <defs><filter id="stoneN" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves={2} seed={3}/><feColorMatrix values="0 0 0 0 .45  0 0 0 0 .42  0 0 0 0 .38  0 0 0 .22 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>
   <clipPath id="plazaC"><circle cx={FX} cy={FY} r={PR}/></clipPath></defs>
  <circle cx={FX} cy={FY} r={PR+20} fill="#5f8f45"/><circle cx={FX} cy={FY} r={PR+20} fill="url(#grass)" opacity={.7}/>
  <circle cx={FX} cy={FY} r={PR} fill="#cfc6b6" filter="url(#shadow)"/>
  <g clipPath="url(#plazaC)">{Array.from({length:10},(_,k)=><circle key={k} cx={FX} cy={FY} r={PR-k*5*M} fill={k%2?'#d9d1c2':'#c4baa8'}/>)}
   {Array.from({length:10},(_,k)=>{const r0=PR-k*5*M,r1=r0-5*M,n=Math.max(8,Math.round(2*PI*r0/22));return <g key={k}>{Array.from({length:n},(_,j)=>{const an=2*PI*j/n+k*.13;return <line key={j} x1={FX+Math.cos(an)*Math.max(0,r1)} y1={FY+Math.sin(an)*Math.max(0,r1)} x2={FX+Math.cos(an)*r0} y2={FY+Math.sin(an)*r0} stroke="#a89e8c" strokeWidth={1}/>;})}<circle cx={FX} cy={FY} r={r0} fill="none" stroke="#9a907e" strokeWidth={1.5}/></g>;})}
   <rect x={FX-PR} y={FY-PR} width={2*PR} height={2*PR} filter="url(#stoneN)" fill="#fff"/></g>
  <circle cx={FX} cy={FY} r={4*M} fill="#7fb8d8" stroke="#8d8372" strokeWidth={4}/><circle cx={FX} cy={FY} r={2*M} fill="#a9d4ea"/>
  {Array.from({length:16},(_,k)=>{const an=2*PI*k/16+.1;const x=FX+Math.cos(an)*(PR+10),y=FY+Math.sin(an)*(PR+10);return <g key={k} filter="url(#shadowS)"><circle cx={x} cy={y} r={3*M} fill="#3f7a35"/><circle cx={x-4} cy={y-4} r={1.8*M} fill="#5c9a46"/></g>;})}
  {Array.from({length:8},(_,k)=>{const an=2*PI*k/8+PI/8;const r=PR-2*M;const x=FX+Math.cos(an)*r,y=FY+Math.sin(an)*r;return <rect key={k} x={x-M} y={y-.3*M} width={2*M} height={.6*M} fill="#7a5532" transform={`rotate(${an*180/PI+90} ${x} ${y})`}/>;})}
  <g opacity={cP}><circle cx={FX} cy={FY} r={PR} fill="none" stroke={P.yel} strokeWidth={6} strokeDasharray={`${2*PI*PR*cP} 9999`} transform={`rotate(-90 ${FX} ${FY})`}/>
   <line x1={FX-PR} y1={FY} x2={FX+PR} y2={FY} stroke={P.yel} strokeWidth={5} strokeDasharray="16 10"/><Tx x={FX} y={FY-40} s={40} c="#fff" stroke={P.ink} sw={7}>直径100米</Tx></g>
  {(()=>{const px=FX+120,py=FY-150,h=1.7*M;return <g><ellipse cx={px} cy={py+h*.5} rx={h*.3} ry={h*.12} fill="#000" opacity={.25}/><circle cx={px} cy={py-h*.38} r={h*.13} fill={P.ink}/><rect x={px-h*.12} y={py-h*.25} width={h*.24} height={h*.75} rx={1} fill={P.ink}/>
   <circle cx={px} cy={py} r={16} fill="none" stroke={P.pink} strokeWidth={3}/><Tx x={px+20} y={py-34} s={22} a="start" c="#fff" stroke={P.ink} sw={5}>一个人≈1.7米</Tx></g>;})()}</g>);
 E(out,'loupe','loupe','side',[1180,260,660,600],vis(t,at(70,'误差'),ss(71)),()=>{const c=[1510,540];const pxPerMm=360;return <g><Card b={[1180,260,660,600]}/>
  <circle cx={c[0]} cy={c[1]} r={200} fill="#efe3c7" stroke={P.ink} strokeWidth={8}/><circle cx={c[0]} cy={c[1]} r={.25*pxPerMm} fill="#d9b77a" stroke="#a9844a" strokeWidth={3}/>
  <rect x={c[0]-1} y={c[1]-.25*pxPerMm-30} width={Math.max(2,.01*pxPerMm)} height={24} fill={P.red}/>
  <Tx x={c[0]} y={c[1]-160} s={24} c={P.red}>误差 {'<'} 0.01毫米（红线）</Tx><Tx x={c[0]} y={790} s={28}>一粒沙 ≈ 0.5毫米</Tx></g>;});
 E(out,'remember','remember','stage',[180,330,800,440],vis(t,ss(71),at(73,'还能')),()=><g><Card b={[180,330,800,440]}/>
  <Tx x={460} y={460} s={60}>发现</Tx><Cross x={640} y={460} s={36} p={prog(t,at(71,'发现'),.5)}/>
  <Tx x={520} y={620} s={60}>算得更准</Tx><Check x={780} y={612} s={40} p={prog(t,at(71,'算得更准'),.5)}/></g>);
 // handover to ch5: digit string grows
 E(out,'digits','digits','stage',[80,480,1000,140],vis(t,at(73,'还能'),at(76,'截至')),()=>{const n=7+Math.floor(prog(t,at(73,'还能'),CH[5]+1.2-at(73,'还能'))*22);return <g><rect x={86} y={486} width={988} height={128} rx={20} fill="#0b1a33" opacity={.6}/><Tx x={580} y={552} s={52} c={P.yel} f="monospace">{('3.'+PIDIG.slice(1,1+n)).slice(0,30)+'…'}</Tx></g>;});
 title(out,t,'t4a','约1500年前',ss(61),at(62,'祖冲之'));
 title(out,t,'t4b','祖冲之 · 南北朝',at(62,'祖冲之'),ss(64));
 title(out,t,'t4c','算筹：一根根小竹棍',at(64,'算筹'),ss(65));
 title(out,t,'t4d','每算一步，都要摆满一大桌',ss(65),ss(66));
 title(out,t,'t4e','3.1415926 < π < 3.1415927',at(66,'大于'),ss(69));
 title(out,t,'t4f','七位小数，有多准？',at(70,'如果'),ss(71));
 title(out,t,'t4g','要记住',ss(71),ss(72));
 title(out,t,'t4h','七位已经很厉害了',ss(72),at(73,'还能'));
 title(out,t,'t4i','π 还能算得更准吗？',at(73,'还能'),CH[5]+.5);
};
export const scene5=(t:number,out:El[])=>{
 if(t<CH[5]-.01||t>=CH[6]+.01)return;
 const rec=back(t,at(76,'三百一十四万亿'),.5),days=prog(t,at(77,'一百一十天'),.4);
 E(out,'monitor','monitor','side',[1260,280,520,440],vis(t,at(75,'计算机'),ss(78)),()=><Monitor x={1260} y={280} w={520} h={440}><Tx x={1520} y={420} s={44} c={P.yel} f="monospace">3.14159265…</Tx><Tx x={1520} y={500} s={30} c="#9BD1FF" o={days}>连续算了约110天</Tx></Monitor>);
 E(out,'record','record','stage',[80,300,1000,420],vis(t,at(76,'截至'),ss(78)),()=><g><rect x={86} y={306} width={988} height={408} rx={30} fill="#0b1a33" stroke={P.yel} strokeWidth={4} filter="url(#shadow)"/>
  <Tx x={580} y={400} s={34} c="#fff">截至2026年 · 世界纪录</Tx><g transform={`translate(580,520) scale(${.8+.2*rec}) translate(-580,-520)`}><Tx x={580} y={520} s={96} c={P.yel}>314万亿位小数</Tx></g></g>);
 const yrs=prog(t,at(79,'大约'),atEnd(79,'万年')-at(79,'大约'));
 E(out,'years','years','stage',[180,320,800,400],vis(t,ss(79),ss(80)),()=><g><Card b={[180,320,800,400]}/><Tx x={580} y={410} s={32}>每秒念1位，念完314万亿位要…</Tx><Tx x={580} y={540} s={100} c={P.orange}>{Math.round(yrs*1000)+'万年'}</Tx><Tx x={580} y={650} s={24} c="#6b6f80" w={500}>314万亿秒 ≈ 1000万年</Tx></g>);
 E(out,'stream','stream','stage',[60,470,1040,160],vis(t,ss(80),ss(83)),()=>{const off=((t-ss(80))*160)%560;return <g><defs><clipPath id="strm"><rect x={66} y={476} width={1028} height={148} rx={20}/></clipPath></defs><rect x={66} y={476} width={1028} height={148} rx={20} fill="#0b1a33"/>
  <g clipPath="url(#strm)"><Tx x={100-off} y={552} s={56} c={P.yel} a="start" f="monospace">{'3.'+PIDIG.slice(1,80)}</Tx></g></g>;});
 E(out,'inf','inf','side',[1180,400,660,180],vis(t,at(81,'无限'),ss(83)),()=><g><Card b={[1180,400,660,180]}/><Tx x={1350} y={490} s={56} c={P.pink}>无限</Tx><Tx x={1670} y={490} s={56} c={P.teal} o={prog(t,at(81,'不会'),.4)}>不循环</Tx></g>);
 const g=prog(t,at(83,'为什么'),CH[6]-at(83,'为什么'));
 E(out,'piHero','hero','stage',[380,330,400,460],vis(t,at(83,'为什么'),CH[6]+.05,.4,.01),()=><Tx x={580} y={570} s={lerp(120,360,g)} c={P.pink} f={SERIF} stroke="#fff" sw={6}>π</Tx>);
 title(out,t,'t5a','能，而且远远不止',ss(74),ss(75));
 title(out,t,'t5b','计算机来帮忙',at(75,'计算机'),ss(76));
 title(out,t,'t5c','一台计算机，约110天',at(77,'一台'),ss(78));
 title(out,t,'t5d','3.14 只是近似值',at(82,'近似值'),ss(83));
 title(out,t,'t5e','为什么用 π 表示？',at(83,'为什么'),CH[6]+.3);
};
export const scene6=(t:number,out:El[])=>{
 if(t<CH[6]-.01)return;
 const jones=prog(t,ss(84),1.0);
 E(out,'book','hero','stage',[160,280,840,560],vis(t,CH[6]-.02,ss(86),.01),()=><g>
  <g opacity={jones}><rect x={166} y={286} width={828} height={548} rx={18} fill="#7a3b1f" filter="url(#shadow)"/><rect x={196} y={306} width={384} height={508} fill="#fffdf7"/><rect x={580} y={306} width={384} height={508} fill="#fbf6ea"/><rect x={196} y={306} width={768} height={508} fill="url(#paperTex)" opacity={.35}/>
   <Tx x={772} y={420} s={34} f={SERIF}>1706年</Tx><Tx x={772} y={490} s={26} f={SERIF}>William Jones</Tx><Tx x={772} y={620} s={28} f={SERIF}>3.14159… = π</Tx></g>
  <Tx x={lerp(580,388,jones)} y={lerp(570,560,jones)} s={lerp(360,220,jones)} c={P.pink} f={SERIF} stroke="#fff" sw={6}>π</Tx></g>);
 E(out,'greek','greek','side',[1180,300,660,280],vis(t,at(84,'符号'),ss(85)),()=><g><Card b={[1180,300,660,280]}/><Tx x={1510} y={400} s={60} f={SERIF}><tspan fill={P.pink}>π</tspan>ερίμετρος</Tx><Tx x={1510} y={490} s={30} c="#6b6f80" w={500}>希腊语“周长”的第一个字母</Tx></g>);
 E(out,'euler','euler','side',[1180,300,660,260],vis(t,at(85,'欧拉'),ss(86)),()=><g><Card b={[1180,300,660,260]}/><Tx x={1510} y={390} s={52}>欧拉也用 π</Tx><Tx x={1510} y={470} s={30} c="#6b6f80" w={500}>18世纪的大数学家</Tx></g>);
 E(out,'cal','cal','stage',[200,280,560,580],vis(t,ss(86),ss(88)),()=><g><rect x={206} y={286} width={548} height={568} rx={30} fill="#fffdf7" filter="url(#shadow)"/><rect x={206} y={286} width={548} height={568} rx={30} fill="url(#paperTex)" opacity={.3}/>
  <rect x={206} y={286} width={548} height={140} rx={30} fill={P.red}/><rect x={206} y={386} width={548} height={40} fill={P.red}/><Tx x={480} y={356} s={64} c="#fff">3 月</Tx><Tx x={480} y={640} s={250} c={P.ink}>14</Tx></g>);
 E(out,'pie','pie','side',[1180,300,660,480],vis(t,ss(86),ss(88)),()=><g><ellipse cx={1510} cy={560} rx={320} ry={210} fill="#d9d4cc" filter="url(#shadow)"/><ellipse cx={1510} cy={545} rx={280} ry={170} fill="url(#crust)"/>
  <Tx x={1510} y={560} s={180} c="#fff" stroke="#9a5a1a" sw={6} f={SERIF}>π</Tx></g>);
 const D=200,R=100,X0=560,GY=760,L=PI*D;const roll=prog(t,at(88,'下次'),atEnd(88,'一个圆')+.8-at(88,'下次'));
 E(out,'end','hero','wide',[460,560,1100,300],vis(t,ss(88),DUR+5),()=><g><rect x={460} y={GY} width={1100} height={50} rx={10} fill="url(#asphalt)" filter="url(#shadow)"/><line x1={X0} y1={GY+2} x2={X0+L*roll} y2={GY+2} stroke={P.orange} strokeWidth={10} strokeLinecap="round"/><Wheel cx={X0+L*roll} cy={GY-R} r={R} rot={roll*360}/></g>);
 title(out,t,'t6a','1706年 · 英国数学家 琼斯',at(84,'英国'),ss(85));
 title(out,t,'t6b','大家都用开了',at(85,'大家'),ss(86));
 title(out,t,'t6c','3月14日 · π日 · 国际数学日',ss(86),ss(87));
 title(out,t,'t6d','比一比，谁背得更多',ss(87),ss(88));
 title(out,t,'t6e','藏着一个永远写不完的数',at(88,'里面'),DUR+5);
};
