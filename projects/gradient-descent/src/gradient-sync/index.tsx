import React from 'react';
import {AbsoluteFill,Audio,Sequence,Easing,interpolate,staticFile,useCurrentFrame} from 'remotion';
import timing from './timing.json';
import {Landscape,project,View} from './scene';
import {loss,paths,pointAt,surface,HEIGHT} from '../gradient/model';
const focusPaths=paths;
const HEIGHT_VALUE=(p:[number,number])=>HEIGHT*loss(p);
const c={paper:'#eee5cf',ink:'#34312b',red:'#a64531',green:'#34746a',muted:'#8b7a61'};
const serif='"SimSun","Microsoft YaHei",serif',sans='"Microsoft YaHei",sans-serif';
const ramp=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const e=timing.events,u=timing.updates;
const slope=e.slope.frame,update=u.first[0].start,small=e.small.frame,big=e.big.frame,normal=e.normal.frame;
type Update={start:number;end:number;arrow:number};
const phaseAt=(f:number,updates:Update[])=>updates.reduce((n,v)=>n+ramp(f,v.start,v.end),0);
// Each update travels for 12 frames, then pauses; no physics simulation is used.
const discrete=(f:number,start:number,spacing:number,count:number)=>{const n=Math.max(0,(f-start)/spacing),whole=Math.min(count,Math.floor(n)),travel=Math.min(12,spacing*.65);return Math.min(count,whole+ramp(f,start+whole*spacing,start+whole*spacing+travel));};
export const GradientSync=()=>{
 const f=useCurrentFrame();
 const axis=ramp(f,e.axis.frame,e.axis.frame+16),grid=ramp(f,e.grid.frame,e.grid.frame+16),rise=ramp(f,e.rise.frame,e.rise.frame+16);
 const close=ramp(f,slope-10,slope+6)*(1-ramp(f,e.term.frame-5,e.term.frame+11));
 const turn=ramp(f,big-5,big+11)*(1-ramp(f,normal-5,normal+11));
 const finish=ramp(f,e.caveat.frame,e.caveat.frame+16);
 const mode=f<small?'normal':f<big?'small':f<normal?'large':'normal';
 const rate=mode==='small'?.06:mode==='large'?1.32:.5;
 const points=focusPaths[mode];
 const updates=f<small?u.first:f<big?u.small:f<normal?u.big:f<e.caveat.frame?u.normal:u.continue;
 const phase=(f>=e.caveat.frame?3:0)+phaseAt(f,updates);
 const ghost=f<small?undefined:f<big?focusPaths.normal.slice(0,4):f<normal?focusPaths.small.slice(0,4):focusPaths.large;
 const patch=ramp(f,slope,slope+12)*(1-ramp(f,u.first[0].end,u.first[0].end+8));
 const recurring=Math.max(0,...updates.map(v=>ramp(f,v.arrow,v.start-1)*(1-ramp(f,v.start,v.start+4))));
 const recalculation=ramp(f,e.recalculate.frame,e.recalculate.frame+6)*(1-ramp(f,u.first[1].start,u.first[1].start+3));
 const arrow=Math.max(ramp(f,e.direction.frame,e.direction.frame+12)*(1-ramp(f,update,update+4)),recurring*.75,recalculation);
 const landed=Math.max(0,...updates.map(v=>ramp(f,v.end-1,v.end)*(1-ramp(f,v.end,v.end+6))));
 const p=pointAt(points,phase),height=loss(p);
 const anticipation=Math.max(0,...updates.map(v=>ramp(f,v.start-5,v.start)*(1-ramp(f,v.end,v.end+6))));
 const distance=1-.025*anticipation;
 const targetP:[number,number,number]=[p[0]*close*.62,mix(1.4,HEIGHT_VALUE(p)*.65,close),p[1]*close*.62];
 const view:View={camera:[targetP[0]+mix(mix(6,3.4,close),-5,turn)*distance,targetP[1]+mix(mix(24,17,close),25,finish)*distance,targetP[2]+mix(mix(8,5,close),8.5,turn)*distance],target:targetP};
 const moving=updates.some(v=>f>=v.start&&f<v.end);
 const rethinking=f>=e.recalculate.frame&&f<u.first[1].start;
 const beat=moving?'update':rethinking?'recalculate':'slope';
 const lifted=surface(p,.16);lifted[1]=(lifted[1]-.16)*rise+.16;
 const ball=project(lifted,view);
 const axes=[{pos:[4.3,-.15,4.3] as [number,number,number],text:'参数 ①',color:c.red},{pos:[-4.3,-.15,2.8] as [number,number,number],text:'参数 ②',color:c.green},{pos:[-4.3,4.5,4.3] as [number,number,number],text:'误差 ↑',color:c.muted}];
 const active=timing.captions.filter(item=>f>=item.frame);const subtitle=active[active.length-1]?.text??'';
 const titleAlpha=(1-ramp(f,e.axis.frame-12,e.axis.frame+4))+ramp(f,e.term.frame,e.term.frame+12)*(1-ramp(f,e.steps.frame-8,e.steps.frame+6));
 return <AbsoluteFill style={{background:c.paper,color:c.ink,fontFamily:sans,overflow:'hidden'}}>
  <AbsoluteFill style={{backgroundImage:'radial-gradient(#9c876e16 .8px,transparent .8px)',backgroundSize:'7px 7px'}}/>
  <div style={{position:'absolute',top:65,left:75,right:75,color:c.muted,fontSize:20,letterSpacing:4}}>AI 原理笔记 / 两参数示意</div>
  <Landscape view={view} points={points} phase={phase} color={mode==='large'?c.red:c.green} arrow={arrow} rise={rise} grid={Math.max(.001,grid)} axis={Math.max(.001,axis)} patch={patch} ghost={ghost} pulse={landed}/>
  <div style={{position:'absolute',top:f<e.slope.frame?235:190,left:75,fontFamily:serif,fontSize:f<e.slope.frame?68:74,color:c.ink,opacity:titleAlpha,transform:`translateY(${(1-ramp(f,e.term.frame,e.term.frame+16))*10}px)`}}>{f<e.slope.frame?'AI 学习，到底在改什么？':'梯度下降'}</div>
  {axes.map((a,i)=>{const pos=project(a.pos,view);return <div key={a.text} style={{position:'absolute',left:Math.min(940,Math.max(90,pos[0])),top:pos[1]-30,transform:'translateX(-50%)',fontSize:27,color:a.color,opacity:(i<2?axis:rise)*(1-close*.85),padding:'5px 10px',background:'#eee5cfe6',whiteSpace:'nowrap'}}>{a.text}</div>})}
  <div style={{position:'absolute',left:Math.min(810,Math.max(110,ball[0]+50)),top:Math.max(250,ball[1]-105),fontSize:25,color:mode==='large'?c.red:c.green,background:'#fcf7eae8',padding:'11px 17px',border:'1px solid #b4a68b',opacity:rise}}><span style={{fontSize:18,color:c.muted}}>误差 L </span>{height.toFixed(2)}</div>
  <div style={{position:'absolute',top:1550,left:75,right:75,display:'flex',justifyContent:'space-between',alignItems:'center',fontFamily:serif,fontSize:37,color:mode==='large'?c.red:c.green,opacity:ramp(f,e.slope.frame,e.slope.frame+15)}}><span>{f<e.steps.frame?<><span style={{color:beat==='slope'?c.red:c.muted}}>坡度</span><span style={{color:c.muted}}> → </span><span style={{color:beat==='update'?c.red:c.muted}}>更新</span><span style={{color:c.muted}}> → </span><span style={{color:beat==='recalculate'?c.red:c.muted}}>重新计算</span></>:mode==='small'?'短而密 · 进展慢':mode==='large'?'跨过低点 · 来回跳':'合适步长 · 收稳'}</span><span style={{fontFamily:sans,fontSize:25}}>η = {rate}</span></div>
  <div style={{position:'absolute',left:75,right:75,top:1605,color:c.muted,fontSize:21,lineHeight:1.5,opacity:f>=small?1:0}}><div>{f<e.caveat.frame?'同一起点 · 各更新 3 次':'继续更新，逐步收稳'}　<span style={{color:'#ad8d65'}}>浅金：前一次轨迹</span></div><div style={{display:'flex',gap:30}}><span style={{opacity:f>=small&&phase>=3||f>=big?1:.25}}>小步 6.14 → 3.70</span><span style={{color:c.red,opacity:f>=big&&phase>=3||f>=normal?1:.25}}>大步 → 10.94</span><span style={{color:c.green,opacity:f>=normal&&phase>=3?1:.25}}>合适 → 0.14</span></div></div>
  <div style={{position:'absolute',left:65,right:65,top:1685,textAlign:'center',fontSize:35,lineHeight:1.6}}>{subtitle}</div>
  <div style={{position:'absolute',bottom:66,left:75,right:75,borderTop:'1px solid #bbaa8b',paddingTop:20,color:c.muted,fontSize:18,display:'flex',justifyContent:'space-between'}}><span>解析梯度计算 / 3D 数学示意</span><span>Fish Audio · 同音色旁白</span></div>
  <Audio src={staticFile(timing.audio)} volume={.85}/>
  {timing.sfx.map((item,i)=><Sequence key={i} from={item.frame}><Audio src={staticFile(item.audio)} volume={item.volume}/></Sequence>)}
 </AbsoluteFill>;
};


