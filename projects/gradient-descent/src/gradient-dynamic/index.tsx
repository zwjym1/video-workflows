import React from 'react';
import {AbsoluteFill,Audio,Sequence,Easing,interpolate,staticFile,useCurrentFrame} from 'remotion';
import timing from '../gradient/timing.json';
import {Landscape,project,View} from './scene';
import {loss,paths,pointAt,surface,HEIGHT} from '../gradient/model';
const HEIGHT_VALUE=(p:[number,number])=>HEIGHT*loss(p);
const c={paper:'#eee5cf',ink:'#34312b',red:'#a64531',green:'#34746a',muted:'#8b7a61'};
const serif='"SimSun","Microsoft YaHei",serif',sans='"Microsoft YaHei",sans-serif';
const ramp=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const cue=(i:number,text:string)=>{const b=timing[i].boundaries.find(b=>b.text===text);if(!b)throw new Error(`Missing gradient voice cue ${text}`);return timing[i].start+Math.round(b.offset*30);};
const slope=cue(1,'坡度'),update=cue(1,'调整'),small=cue(2,'小')-7,big=cue(2,'大')-7,normal=cue(2,'换回');
// Each update travels for 12 frames, then pauses; no physics simulation is used.
const discrete=(f:number,start:number,spacing:number,count:number)=>{const n=Math.max(0,(f-start)/spacing),whole=Math.min(count,Math.floor(n)),travel=Math.min(12,spacing*.65);return Math.min(count,whole+ramp(f,start+whole*spacing,start+whole*spacing+travel));};
export const GradientDynamic=()=>{
 const f=useCurrentFrame();
 const axis=ramp(f,5,21),grid=ramp(f,108,124),rise=ramp(f,196,214);
 const close=ramp(f,slope-8,slope+8)*(1-ramp(f,440,456));
 const turn=ramp(f,big-5,big+11)*(1-ramp(f,normal-5,normal+11));
 const finish=ramp(f,794,810);
 const mode=f<small?'normal':f<big?'small':f<normal?'large':'normal';
 const rate=mode==='small'?.06:mode==='large'?1.32:.5;
 const points=paths[mode];
 const phase=f<small?discrete(f,update+2,25,6):f<big?discrete(f,small+3,6,9):f<normal?discrete(f,big+3,14,3):discrete(f,normal+4,14,9);
 const stepStart=f<small?update+2:f<big?small+3:f<normal?big+3:normal+4;
 const spacing=f<small?25:f<big?6:14;
 const elapsed=Math.max(0,f-stepStart),cycle=Math.floor(elapsed/spacing),within=elapsed-cycle*spacing;
 const recurring=f>=stepStart&&phase<points.length-1?(1-ramp(within,0,6))*.8:0;
 const arrow=Math.max(ramp(f,slope-5,slope+8)*(1-ramp(f,update-4,update+6)),recurring);
 const p=pointAt(points,phase),height=loss(p);
 const targetP:[number,number,number]=[p[0]*close*.62,mix(1.4,HEIGHT_VALUE(p)*.65,close),p[1]*close*.62];
 const view:View={camera:[targetP[0]+mix(mix(6,3.4,close),-5,turn),targetP[1]+mix(mix(24,17,close),25,finish),targetP[2]+mix(mix(8,5,close),8.5,turn)],target:targetP};
 const lifted=surface(p,.16);lifted[1]=(lifted[1]-.16)*rise+.16;
 const ball=project(lifted,view);
 const axes=[{pos:[4.3,-.15,4.3] as [number,number,number],text:'参数 ①',color:c.red},{pos:[-4.3,-.15,2.8] as [number,number,number],text:'参数 ②',color:c.green},{pos:[-4.3,4.5,4.3] as [number,number,number],text:'误差 ↑',color:c.muted}];
 const captions:[number,string][]=[[0,'AI 学习，到底在改什么？'],[cue(0,'把'),'把两个参数，画成一张地图'],[cue(0,'位置'),'位置代表参数，高度代表误差'],[261,'根据当前位置的坡度'],[cue(1,'朝'),'朝误差减小的方向，调整一步'],[cue(1,'再'),'再计算，再调整'],[cue(1,'这'),'这就是梯度下降'],[517,'步子也有讲究'],[small,'太小，走得慢'],[big,'太大，可能来回跳'],[normal,'换回合适的步长'],[cue(2,'更'),'更稳地降低误差'],[794,'这是两参数示意，真实模型维度更高'],[cue(3,'球'),'球表示参数位置，不是自己滚下山']];
 const active=captions.filter(([at])=>f>=at);const subtitle=active[active.length-1][1];
 const titleAlpha=(1-ramp(f,55,71))+ramp(f,440,456)*(1-ramp(f,500,516));
 return <AbsoluteFill style={{background:c.paper,color:c.ink,fontFamily:sans,overflow:'hidden'}}>
  <AbsoluteFill style={{backgroundImage:'radial-gradient(#9c876e16 .8px,transparent .8px)',backgroundSize:'7px 7px'}}/>
  <div style={{position:'absolute',top:65,left:75,right:75,color:c.muted,fontSize:20,letterSpacing:4}}>AI 原理笔记 / 两参数示意</div>
  <Landscape view={view} points={points} phase={phase} color={mode==='large'?c.red:c.green} arrow={arrow} rise={rise} grid={Math.max(.001,grid)} axis={Math.max(.001,axis)}/>
  <div style={{position:'absolute',top:f<261?235:190,left:75,fontFamily:serif,fontSize:f<261?68:74,color:c.ink,opacity:titleAlpha,transform:`translateY(${(1-ramp(f,440,456))*10}px)`}}>{f<261?'AI 学习，到底在改什么？':'梯度下降'}</div>
  {axes.map((a,i)=>{const pos=project(a.pos,view);return <div key={a.text} style={{position:'absolute',left:Math.min(940,Math.max(90,pos[0])),top:pos[1]-30,transform:'translateX(-50%)',fontSize:27,color:a.color,opacity:(i<2?axis:rise)*(1-close*.85),padding:'5px 10px',background:'#eee5cfe6',whiteSpace:'nowrap'}}>{a.text}</div>})}
  <div style={{position:'absolute',left:Math.min(810,Math.max(110,ball[0]+50)),top:Math.max(250,ball[1]-105),fontSize:25,color:mode==='large'?c.red:c.green,background:'#fcf7eae8',padding:'11px 17px',border:'1px solid #b4a68b',opacity:rise}}><span style={{fontSize:18,color:c.muted}}>误差 L </span>{height.toFixed(2)}</div>
  <div style={{position:'absolute',top:1550,left:75,right:75,display:'flex',justifyContent:'space-between',alignItems:'center',fontFamily:serif,fontSize:37,color:mode==='large'?c.red:c.green,opacity:ramp(f,261,276)}}><span>{f<517?'坡度 → 更新 → 重新计算':mode==='small'?'短而密 · 进展慢':mode==='large'?'跨过低点 · 来回跳':'合适步长 · 收稳'}</span><span style={{fontFamily:sans,fontSize:25}}>η = {rate}</span></div>
  <div style={{position:'absolute',left:75,right:75,top:1610,color:c.muted,fontSize:23,opacity:f>=small&&f<normal?1:0}}>同一地形、同一起点比较步长</div>
  <div style={{position:'absolute',left:65,right:65,top:1685,textAlign:'center',fontSize:35,lineHeight:1.6}}>{subtitle}</div>
  <div style={{position:'absolute',bottom:66,left:75,right:75,borderTop:'1px solid #bbaa8b',paddingTop:20,color:c.muted,fontSize:18,display:'flex',justifyContent:'space-between'}}><span>解析梯度计算 / 3D 数学示意</span><span>Edge TTS · 云希</span></div>
  {timing.map((t,i)=><Sequence key={i} from={t.start} durationInFrames={t.frames}><Audio src={staticFile(t.audio)}/></Sequence>)}
 </AbsoluteFill>;
};

