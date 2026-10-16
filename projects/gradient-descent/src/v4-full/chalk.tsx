import React from 'react';
import {AbsoluteFill,Audio,Sequence,interpolate,Easing,staticFile,useCurrentFrame} from 'remotion';
import {rand} from '../v3-shared/words';
import {CHALK_E} from './events';
import {Param,paths,loss,initial} from '../gradient-story/model';
const board='#22302a',chalk='#f1ede0',yellow='#e8d27a',red='#ef7f6a',mint='#8fdcb6';
const hand='"KaiTi","STKaiti","Noto Serif CJK SC",serif',latin='"Noto Serif","Georgia",serif';
const snap=Easing.bezier(.16,1,.3,1);
const r=(f:number,a:number,b:number,e=snap)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:e});
const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
const E=CHALK_E;
const X=(a:number)=>540+a*280,Y=(b:number)=>800-b*280;
type Run={key:string;label:string;eta:number;pts:Param[];color:string;from:number;to:number;val:number;col:number};
const runs:Run[]=[
 {key:'small',label:'太小',eta:.06,pts:paths.small,color:yellow,from:E.small+4,to:E.smallVal-2,val:E.smallVal,col:190},
 {key:'large',label:'太大',eta:1.05,pts:paths.large,color:red,from:E.large+4,to:E.largeVal-2,val:E.largeVal,col:540},
 {key:'ok',label:'合适',eta:.35,pts:paths.normal.slice(0,4),color:mint,from:E.ok+3,to:E.okVal-2,val:E.okVal,col:890},
];
// step k (0..3) progress of a run, each step a snappy hop
const stepPhase=(f:number,run:Run)=>{const d=(run.to-run.from)/3;let ph=0;for(let k=0;k<3;k++)ph+=r(f,run.from+k*d,run.from+k*d+d*.8);return ph;};
const at=(pts:Param[],ph:number):Param=>{const i=Math.min(2,Math.floor(ph)),t=ph-i;return[mix(pts[i][0],pts[i+1][0],t),mix(pts[i][1],pts[i+1][1],t)];};
export const chalkSfx=[{frame:E.start,audio:'sync-tap.wav',volume:.5},...runs.flatMap(run=>[0,1,2].map(k=>({frame:Math.round(run.from+k*(run.to-run.from)/3),audio:'sync-tap.wav',volume:.4}))),{frame:E.over,audio:'sync-sweep.wav',volume:.45},{frame:E.okVal,audio:'sync-paper.wav',volume:.5}];
const dust=(()=>{const R=rand(35);return Array.from({length:70},()=>({x:R()*1080,y:R()*1920,w:20+R()*120,o:.012+R()*.025}));})();
const fmt=(v:number)=>v.toFixed(3);
export const Chalk=()=>{
 const f=useCurrentFrame();
 const start=r(f,E.start,E.start+12),three=r(f,E.three,E.three+12);
 const shakeT=f>=E.over&&f<E.over+12?(1-(f-E.over)/12):0,sx=Math.sin(f*2.3)*10*shakeT,sy=Math.cos(f*3.1)*6*shakeT;
 const endGlow=r(f,E.okVal,E.okVal+14);
 const active=f>=E.ok?'ok':f>=E.large?'large':f>=E.small?'small':'';
 return <AbsoluteFill style={{background:board,overflow:'hidden',fontFamily:hand,color:chalk}}>
  <AbsoluteFill style={{background:'radial-gradient(ellipse 900px 1200px at 50% 45%,#2c3d35 0%,#1b2621 75%,#141c18 100%)'}}/>
  <svg width="1080" height="1920" style={{position:'absolute',inset:0}}>
   <defs>
    <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .09 0"/></filter>
    <filter id="chalk" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="1.2" numOctaves="2" seed="9" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="3.5"/></filter>
    <clipPath id="plot"><rect x="60" y="300" width="960" height="935"/></clipPath>
    {[yellow,red,mint].map(c=><marker key={c} id={'m'+c.slice(1)} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill={c}/></marker>)}
   </defs>
   <rect width="1080" height="1920" filter="url(#grain)"/>
   {dust.map((d,i)=><ellipse key={i} cx={d.x} cy={d.y} rx={d.w} ry={d.w*.35} fill={chalk} opacity={d.o}/>)}
   <g transform={`translate(${sx} ${sy})`}>
   <g clipPath="url(#plot)" filter="url(#chalk)" opacity={start}>
    {[.25,.6,1.2,2.16,3.2].map(c=><ellipse key={c} cx={X(0)} cy={Y(0)} rx={Math.sqrt(2*c)*280} ry={Math.sqrt(c)*280} fill="none" stroke={chalk} strokeWidth={c===2.16?2.6:1.6} strokeDasharray={c===2.16?'':'10 9'} opacity={c===2.16?.55:.28} pathLength={1} style={{strokeDasharray:c===2.16?undefined:'.012 .01'}}/>)}
    <path d={`M${X(-1.8)} ${Y(0)}H${X(1.8)}M${X(0)} ${Y(1.9)}V${Y(-1.9)}`} stroke={chalk} strokeWidth="1.5" opacity=".25"/>
   </g>
   <g filter="url(#chalk)">
    <text x={X(0)} y={Y(0)+48} textAnchor="middle" fontSize="30" fill={chalk} opacity={start*.75}>最低点</text>
    <path d={`M${X(0)-14} ${Y(0)-14}l28 28m0 -28l-28 28`} stroke={chalk} strokeWidth="4" opacity={start*.8}/>
    {runs.map(run=>{const ph=stepPhase(f,run);if(f<run.from)return null;const isA=active===run.key;const op=isA?1:.38+(run.key==='ok'?.62:0)*endGlow;const cur=at(run.pts,ph);const done=Math.floor(ph+1e-6);
     return <g key={run.key} opacity={op}>
      {[0,1,2].filter(k=>k<ph).map(k=>{const a=run.pts[k],b=k<done?run.pts[k+1]:cur;return <path key={k} d={`M${X(a[0])} ${Y(a[1])}L${X(b[0])} ${Y(b[1])}`} stroke={run.color} strokeWidth="6" strokeLinecap="round" markerEnd={k<done?`url(#m${run.color.slice(1)})`:undefined}/>;})}
      {run.pts.slice(1,done+1).map((p,k)=><g key={k}><circle cx={X(p[0])} cy={Y(p[1])} r="9" fill={run.color}/><text x={X(p[0])+(run.key==='large'?-34:18)} y={Y(p[1])+(run.key==='large'?10:-14)} fontSize="28" fill={run.color}>{k+1}</text></g>)}
      <circle cx={X(cur[0])} cy={Y(cur[1])} r={isA?17:11} fill={run.color}/>
     </g>;})}
    {/* start point */}
    <circle cx={X(initial[0])} cy={Y(initial[1])} r={mix(0,20,start)} fill={chalk}/>
    <circle cx={X(initial[0])} cy={Y(initial[1])} r={mix(60,32,start)} fill="none" stroke={chalk} strokeWidth="3" opacity={start*(1-r(f,E.small,E.small+10))}/>
    <text x={X(initial[0])+34} y={Y(initial[1])-30} fontSize="36" fill={chalk} opacity={start}>同一起点</text>
    {/* overshoot flash */}
    {(()=>{const o=r(f,E.over,E.over+6)*(1-r(f,E.ok-6,E.ok+4));if(o<.01)return null;const sc=mix(1.6,1,r(f,E.over,E.over+8));return <g transform={`translate(${X(-1.05)} ${Y(-.55)}) rotate(-6) scale(${sc})`} opacity={o}><rect x="-150" y="-58" width="300" height="92" rx="10" fill="none" stroke={red} strokeWidth="4"/><text x="0" y="10" textAnchor="middle" fontSize="60" fill="#ffa08c">冲过头！</text></g>;})()}
    {(()=>{const run=runs[0],o=r(f,run.from-6,run.from+4)*(1-r(f,E.large,E.large+10)*.75);if(o<.01)return null;const ph=stepPhase(f,run),cur=at(run.pts,ph),Z=2.5,M:[number,number]=[X(-.85),Y(1.2)],s0=initial,tx=(p:Param):[number,number]=>[M[0]+(X(p[0])-X(s0[0]))*Z+70,M[1]+(Y(p[1])-Y(s0[1]))*Z-140];const done=Math.floor(ph+1e-6);
     return <g opacity={o}><path d={`M${X(s0[0])-24} ${Y(s0[1])+8}L${M[0]+150} ${M[1]-40}`} stroke={yellow} strokeWidth="2" strokeDasharray="6 6"/><circle cx={M[0]} cy={M[1]} r="170" fill="#1b2621ee" stroke={yellow} strokeWidth="4"/><text x={M[0]} y={M[1]-185} textAnchor="middle" fontSize="28" fill={yellow}>放大 ×2.5</text>
      <circle cx={tx(s0)[0]} cy={tx(s0)[1]} r="12" fill={chalk}/>
      {[0,1,2].filter(k=>k<ph).map(k=>{const a=tx(run.pts[k]),b=tx(k<done?run.pts[k+1]:cur);return <path key={k} d={`M${a[0]} ${a[1]}L${b[0]} ${b[1]}`} stroke={yellow} strokeWidth="7" strokeLinecap="round"/>;})}
      {run.pts.slice(1,done+1).map((p,k)=><g key={k}><circle cx={tx(p)[0]} cy={tx(p)[1]} r="10" fill={yellow}/><text x={tx(p)[0]-30} y={tx(p)[1]+10} fontSize="28" fill={yellow}>{k+1}</text></g>)}
      <circle cx={tx(cur)[0]} cy={tx(cur)[1]} r="16" fill={yellow}/></g>;})()}
    {/* final success ring */}
    {endGlow>0&&(()=>{const p=paths.normal[3];return <><circle cx={X(p[0])} cy={Y(p[1])} r={56} fill="none" stroke={mint} strokeWidth="5" pathLength={1} strokeDasharray={`${endGlow} 1`}/><text x={X(p[0])+66} y={Y(p[1])+66} fontSize="40" fill={mint} opacity={endGlow}>✓</text></>;})()}
   </g>
   </g>
  </svg>
  {/* title */}
  <div style={{position:'absolute',left:70,top:90,fontSize:66,letterSpacing:4,opacity:start,filter:'url(#chalk)'}}>步长 <span style={{fontFamily:latin,fontStyle:'italic'}}>η</span> 对比</div>
  <div style={{position:'absolute',left:72,top:185,fontSize:32,color:'#c9d2c8',opacity:three}}>同一起点 · 同样三步 · 误差起点 <span style={{fontFamily:latin}}>{fmt(loss(initial))}</span></div>
  {/* scoreboard */}
  <div style={{position:'absolute',left:0,right:0,top:1250,height:300}}>
   {runs.map(run=>{const ph=stepPhase(f,run),shown=f>=run.from,val=loss(at(run.pts,ph)),lock=r(f,run.val,run.val+8),isA=active===run.key;
    return <div key={run.key} style={{position:'absolute',left:run.col,top:0,transform:`translateX(-50%) scale(${shown&&isA?1.08:1})`,textAlign:'center',opacity:shown?(isA||run.key==='ok'&&endGlow>0?1:.55):.18,width:300}}>
     <div style={{fontSize:40,color:run.color}}>{run.label} <span style={{fontFamily:latin,fontSize:30}}>η={run.eta}</span></div>
     <div style={{fontFamily:latin,fontSize:mix(54,66,lock),color:run.color,marginTop:6,textShadow:lock?`0 0 ${lock*18}px ${run.color}88`:undefined}}>{shown?fmt(val):'—'}</div>
     <div style={{fontSize:24,color:'#aab5ab',marginTop:2}}>{shown?`第 ${Math.min(3,Math.floor(ph+1e-6))}/3 步`:''}</div>
     <svg width="240" height="34" style={{marginTop:6}}><rect x="0" y="10" width="240" height="14" fill="#ffffff14"/><rect x="0" y="10" width={Math.min(240,val/2.6*240)} height="14" fill={run.color} opacity={shown?.9:0}/><path d={`M${2.16/2.6*240} 2V32`} stroke={chalk} strokeWidth="2" strokeDasharray="3 3"/></svg>
    </div>;})}
   <div style={{position:'absolute',left:0,right:0,top:226,textAlign:'center',fontSize:20,color:'#8f9a90'}}>条形图虚线 = 起点误差 2.160</div>
  </div>
 </AbsoluteFill>;
};
