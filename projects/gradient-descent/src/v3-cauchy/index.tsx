import React from 'react';
import {AbsoluteFill,Audio,Img,Sequence,interpolate,Easing,staticFile,useCurrentFrame} from 'remotion';
import al0 from './alignment.json';
import {Alignment,wordFrame,rand} from '../v3-shared/words';
import {Caption} from '../v3-shared/caption';
const al=al0 as Alignment;
export const CAUCHY_DURATION=al.frames+26;
const gold='#d8b46a',goldHi='#f3d79a',ink='#0d0c0a',paper='#f1e6cc';
const serif='"Noto Serif CJK SC","SimSun",serif',sans='"Microsoft YaHei","Noto Sans CJK SC",sans-serif',latin='"Noto Serif","Georgia",serif';
const snap=Easing.bezier(.16,1,.3,1);
const r=(f:number,a:number,b:number,e=snap)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:e});
const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
const E={y1847:wordFrame(al,'一八四七'),cauchy:wordFrame(al,'柯西'),idea:wordFrame(al,'朴素'),fn:wordFrame(al,'让函数'),small:wordFrame(al,'变小'),today:wordFrame(al,'今天'),gd:wordFrame(al,'梯度下降'),trace:wordFrame(al,'追溯'),here:wordFrame(al,'这里')};
const END=al.frames-4;
export const cauchySfx=[{frame:E.y1847,audio:'sync-sweep.wav',volume:.35},{frame:E.cauchy,audio:'sync-paper.wav',volume:.5},{frame:E.idea,audio:'sync-paper.wav',volume:.4},{frame:E.small,audio:'sync-tap.wav',volume:.45},{frame:E.gd,audio:'sync-arrow.wav',volume:.4},{frame:E.trace,audio:'sync-sweep.wav',volume:.35},{frame:END,audio:'sync-tap.wav',volume:.4}];
// deterministic particle field
const N=440;const P=(()=>{const R=rand(1847);return Array.from({length:N},()=>({x:R()*1080,y:R()*1920,th:R()*Math.PI*2,rr:.75+R()*.5,sp:(R()-.5)*.02,s:.6+R()*2.2,a:.25+R()*.75,u:R()*2-1}));})();
const valley=(u:number):[number,number]=>[540+u*400,1260-380*u*u];
export const CauchyHook=()=>{
 const f=useCurrentFrame();
 const in1847=r(f,E.y1847,E.y1847+16),toCard=r(f,E.cauchy,E.cauchy+16),scan=r(f,E.idea,E.idea+14),quote=r(f,E.fn,E.fn+14),hl=r(f,E.small,E.small+10);
 const today=r(f,E.today,E.today+16),gd=r(f,E.gd,E.trace+6,Easing.inOut(Easing.cubic)),trace=r(f,E.trace,E.here+10,Easing.inOut(Easing.cubic)),out=r(f,END,END+11,Easing.inOut(Easing.cubic));
 // particle targets: drift -> ring around card -> valley curve
 const ringC:[number,number]=[mix(300,250,today),mix(700,560,today)];
 const pts=P.map((p,i)=>{const drift:[number,number]=[(p.x+Math.sin(f*.02+p.th)*30+f*p.sp*60+1080)%1080,(p.y-f*.6*p.s+1920*3)%1920];
  const ang=p.th+f*.012*(i%2?1:-1),ring:[number,number]=[ringC[0]+Math.cos(ang)*300*p.rr,ringC[1]+Math.sin(ang)*380*p.rr];
  const v=valley(p.u),jit=Math.sin(f*.08+p.th)*14*p.rr,curve:[number,number]=[v[0],v[1]+jit];
  const a=toCard*(1-today),b=today;const x=drift[0]*(1-a-b)+ring[0]*a+curve[0]*b,y=drift[1]*(1-a-b)+ring[1]*a+curve[1]*b;
  return {x,y,s:p.s,al:p.a};});
 const ball=valley(mix(-.86,0,gd));
 return <AbsoluteFill style={{background:ink,overflow:'hidden',fontFamily:sans}}>
  <AbsoluteFill style={{background:`radial-gradient(ellipse 700px 900px at 50% ${mix(40,62,today)}%,#3a2a1088 0%,transparent 70%)`}}/>
  <svg width="1080" height="1920" style={{position:'absolute',inset:0}}>
   <defs><radialGradient id="dust"><stop offset="0" stopColor={goldHi}/><stop offset="1" stopColor={gold} stopOpacity="0"/></radialGradient></defs>
   {pts.map((p,i)=><circle key={i} cx={p.x} cy={p.y} r={p.s*1.7} fill={i%7?gold:'url(#dust)'} opacity={p.al*mix(.55,.95,today)}/>)}
  </svg>
  {/* 1847 */}
  <div style={{position:'absolute',left:mix(540,95,toCard),top:mix(330,120,toCard),transform:`translate(${mix(-50,0,toCard)}%,-50%) scale(${mix(1.35,1,in1847)})`,transformOrigin:'left center',opacity:in1847*(1-today*.6),fontFamily:latin,fontSize:mix(250,110,toCard),fontWeight:700,letterSpacing:mix(40,6,in1847),color:'transparent',backgroundImage:`linear-gradient(180deg,${goldHi},${gold} 55%,#8a6a32)`,WebkitBackgroundClip:'text',backgroundClip:'text',filter:`blur(${(1-in1847)*8}px) drop-shadow(0 0 30px #d8b46a55)`}}>1847</div>
  <div style={{position:'absolute',left:110,top:205,fontFamily:serif,fontSize:34,color:'#cdb98d',opacity:toCard*(1-today),letterSpacing:4}}>巴黎 · 法兰西科学院周报</div>
  {/* scan page */}
  <div style={{position:'absolute',left:470,top:mix(1900,450,scan),width:540,transform:`rotate(${mix(14,5,scan)}deg)`,opacity:scan*(1-today),boxShadow:'0 30px 80px #000c'}}>
   <Img src={staticFile('v3/cauchy-1847-page-1.png')} style={{width:540,display:'block',filter:'sepia(.35) contrast(1.05)'}}/>
   <div style={{position:'absolute',left:'24%',width:`${hl*72}%`,top:'49.2%',height:'3.2%',background:'#e8b84a66',mixBlendMode:'multiply'}}/>
  </div>
  {/* portrait card */}
  <div style={{position:'absolute',left:mix(110,60,today),top:mix(1900,430,toCard)+mix(0,-120,today),width:400,transform:`rotate(${mix(-12,-4,toCard)}deg) scale(${mix(1,.72,today)})`,transformOrigin:'top left',background:paper,padding:'18px 18px 22px',boxShadow:'0 30px 90px #000d, 0 0 0 1px #c9b27f',opacity:toCard>0?1-today*.15:0}}>
   <Img src={staticFile('v3/cauchy-portrait-1901.jpg')} style={{width:364,height:470,objectFit:'cover',display:'block',filter:'sepia(.45) contrast(1.08)'}}/>
   <div style={{fontFamily:latin,fontSize:30,color:'#2b2418',marginTop:14}}>Augustin-Louis Cauchy</div>
   <div style={{fontFamily:serif,fontSize:24,color:'#6b5a3a',marginTop:4}}>柯西 · 1789 – 1857</div>
   <div style={{position:'absolute',right:-26,top:400,width:112,height:112,borderRadius:'50%',border:'5px solid #b1352a',color:'#b1352a',display:'flex',alignItems:'center',justifyContent:'center',fontFamily:latin,fontWeight:700,fontSize:30,transform:`rotate(-14deg) scale(${mix(2.2,1,r(f,E.idea-6,E.idea+4))})`,opacity:r(f,E.idea-6,E.idea+2)}}>1847</div>
  </div>
  {/* quote */}
  <div style={{position:'absolute',left:80,right:80,top:mix(1250,1170,quote)-today*90,opacity:quote*(1-today),textAlign:'center'}}>
   <div style={{fontFamily:latin,fontStyle:'italic',fontSize:34,color:goldHi,lineHeight:1.45}}>« il suffira de faire <span style={{color:'#fff',textShadow:`0 0 ${hl*24}px ${gold}`}}>décroître</span> indéfiniment la fonction u »</div>
   <div style={{fontFamily:serif,fontSize:44,color:'#f4ead2',marginTop:18,letterSpacing:3}}>只需让函数 u <span style={{color:goldHi,fontSize:mix(44,58,hl),textShadow:`0 0 ${hl*30}px ${gold}`}}>不断变小</span></div>
  </div>
  {/* today: valley + gradient descent */}
  {today>.01&&<svg width="1080" height="1920" style={{position:'absolute',inset:0,opacity:today}}>
   <path d={Array.from({length:61},(_,i)=>{const v=valley(-1+i/30);return(i?'L':'M')+v[0]+' '+v[1];}).join('')} fill="none" stroke={goldHi} strokeWidth="4" strokeDasharray={`${today*1700} 1700`} opacity=".9"/>
   {gd>0&&<path d={Array.from({length:31},(_,i)=>{const v=valley(-.86+(.86)*gd*i/30);return(i?'L':'M')+v[0]+' '+(v[1]-18);}).join('')} fill="none" stroke="#fff" strokeWidth="5" strokeLinecap="round" opacity=".85"/>}
   <circle cx={ball[0]} cy={ball[1]-18} r="18" fill="#fff" style={{filter:'drop-shadow(0 0 18px #f3d79a)'}}/>
  </svg>}
  <div style={{position:'absolute',left:540,top:1350,transform:'translateX(-50%)',opacity:r(f,E.gd,E.gd+10),textAlign:'center',whiteSpace:'nowrap'}}>
   <div style={{fontFamily:serif,fontSize:62,color:'#fff',letterSpacing:6}}>梯度下降</div><div style={{fontFamily:latin,fontSize:28,color:gold,letterSpacing:5}}>GRADIENT DESCENT</div>
  </div>
  {/* trace back timeline: today -> 1847 */}
  {trace>.01&&<svg width="1080" height="1920" style={{position:'absolute',inset:0}}>
   <path d="M150 1560H930" stroke={gold} strokeWidth="2" opacity=".6"/>
   <path d={`M930 1560H${mix(930,150,trace)}`} stroke={goldHi} strokeWidth="5"/>
   <circle cx={mix(930,150,trace)} cy="1560" r="11" fill="#fff" style={{filter:'drop-shadow(0 0 14px #f3d79a)'}}/>
   <text x="150" y="1610" textAnchor="middle" fontFamily={latin} fontSize="34" fill={goldHi}>1847</text>
   <text x="930" y="1610" textAnchor="middle" fontFamily={serif} fontSize="32" fill="#f4ead2">今天</text>
  </svg>}
  <Caption al={al} f={f} color="#fff6df" dim="#7d6c4c" font={serif} top={1680}/>
  {/* transition into the problem */}
  {out>0&&<AbsoluteFill style={{background:'#f4efe4',clipPath:`circle(${out*2100}px at 150px 1560px)`}}>
   <div style={{position:'absolute',left:80,right:80,top:820,textAlign:'center',fontFamily:serif,fontSize:64,color:'#393a30',lineHeight:1.5,opacity:r(f,END+6,END+14)}}>可是——<br/>往哪边走，才算<span style={{color:'#a34632'}}>变小</span>？</div>
  </AbsoluteFill>}
  <Audio src={staticFile(al.audio)} volume={.95}/>
  {cauchySfx.map((v,i)=><Sequence key={i} from={v.frame}><Audio src={staticFile(v.audio)} volume={v.volume}/></Sequence>)}
 </AbsoluteFill>;
};
