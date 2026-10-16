import React from 'react';
import {AbsoluteFill,Audio,Sequence,interpolate,Easing,staticFile,useCurrentFrame} from 'remotion';
import timing from './timing.json';
import {Param,paths,at,loss,surface} from './model';
import {Chart,Knob} from './chart';
import {World,View,project} from './scene';
const c={paper:'#eee6d2',ink:'#393a30',green:'#245f51',red:'#a34632',gold:'#9b835e'};
const font='"Microsoft YaHei",sans-serif',serif='"SimSun","Microsoft YaHei",serif';
const r=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
const e=timing.events;
const phases=(f:number,updates:{start:number;end:number}[])=>updates.reduce((v,item)=>v+r(f,item.start,item.end),0);
export const GradientStory=()=>{
 const f=useCurrentFrame();
 const knobA=r(f,e.slopeKnob.frame,e.slopeKnob.end),knobB=r(f,e.interceptKnob.frame,e.interceptKnob.end);
 const map=r(f,e.map.frame,e.map.frame+24),handoff=r(f,e.mapHere.frame,e.mapHere.frame+20),rise=r(f,e.rise.frame,e.height.end);
 const close=r(f,e.local.frame,e.local.frame+20)*(1-r(f,e.term.frame,e.term.frame+20));
 const compareIn=r(f,e.compare.frame-8,e.compare.frame+8),compareOut=r(f,e.suitable.frame,e.suitable.frame+14),compare=compareIn*(1-compareOut);
 const returning=r(f,e.return.frame,e.return.frame+25);
 const firstPhase=phases(f,timing.updates),comparisonPhase=phases(f,timing.compareUpdates),settling=3+phases(f,timing.settleUpdates);
 const preview=f>=e.small.frame&&f<e.compare.frame;
 const previewLarge=f>=e.large.frame;
 const mainPoints=preview?(previewLarge?paths.large:paths.small):paths.normal;
 const mainPhase=preview?r(f,(previewLarge?e.large:e.small).frame+8,(previewLarge?e.large:e.small).frame+24):f<e.compare.frame?firstPhase:f<e.suitable.frame?comparisonPhase:settling;
 const param:Param=f<e.map.frame?[mix(1.7,1.2,knobA),mix(1.7,1.2,knobB)]:at(mainPoints,mainPhase);
 const localOrigin=f>=e.recalculate.frame?paths.normal[1]:paths.normal[0];
 const cut=r(f,e.local.end-12,e.components.frame+8)*(1-r(f,e.move.frame,e.move.end));
 const compA=r(f,e.components.frame,e.components.frame+15)*(1-r(f,e.move.frame,e.move.end));
 const compB=r(f,e.components.frame+28,e.components.frame+43)*(1-r(f,e.move.frame,e.move.end));
 const resultant=r(f,e.combine.frame,e.combine.frame+18)*(1-r(f,e.move.frame+3,e.move.end));
 const recalc=r(f,e.recalculate.frame,e.recalculate.frame+14)*(1-r(f,e.again.frame,e.again.end));
 const view:View={position:[mix(4,2.7,close),mix(14,11.5,close),mix(6,3.6,close)],target:[mix(0,.7,close),mix(.7,.9,close),mix(0,.7,close)]};
 const marker=project(surface(param,.15,rise),view),origin=project(surface(paths.normal[0],.15,rise),view);
 const chartScale=mix(mix(1.3,.48,map),1.3,returning),chartX=mix(mix(110,55,map),110,returning),chartY=mix(mix(240,150,map),240,returning);
 const chartDim=1-r(f,e.local.frame,e.local.frame+15)*(1-returning);
 const onMap=map*(1-returning);
 const title=f<e.map.frame?'这条线，能预测准吗？':f<e.local.frame?'每组参数，都有一个误差。':f<e.term.frame?'方向，要从坡度里找。':f<e.small.frame?'梯度下降':f<e.compare.frame?'步子不同，结果不同。':f<e.suitable.frame?'同一起点，同样三步。':f<e.return.frame?'合适的步长，逐步靠近。':'预测，真的改善了。';
 const caption=timing.captions.filter(v=>f>=v.frame).slice(-1)[0]?.text??'';
 const termFade=f<e.map.frame?1:f>=e.local.frame&&f<e.term.frame?1:1;
 const mapBallX=mix(670,origin[0],handoff),mapBallY=mix(1320,origin[1],handoff);
 return <AbsoluteFill style={{background:c.paper,fontFamily:font,color:c.ink,overflow:'hidden'}}>
  <AbsoluteFill style={{backgroundImage:'radial-gradient(#98826113 .8px,transparent .8px)',backgroundSize:'7px 7px'}}/>
  <div style={{position:'absolute',left:75,top:80,fontSize:48,fontFamily:serif,opacity:termFade,lineHeight:1.4}}>{title}</div>
  <div style={{opacity:onMap>.001?1:0,transform:`scale(${mix(.25,1,map)*(1-returning*.65)})`,transformOrigin:'540px 950px'}}><World view={view} rise={rise} mainPhase={mainPhase} mainPoints={mainPoints} arrowOrigin={localOrigin} compare={compare} comparisonPhase={comparisonPhase} componentA={compA} componentB={compB} combined={Math.max(resultant,recalc)} slices={Math.max(cut,recalc*.7)*(1-resultant*.65)} ballAlpha={handoff>.99?1:0}/></div>
  <div style={{position:'absolute',left:chartX,top:chartY,transform:`scale(${chartScale})`,transformOrigin:'0 0',opacity:chartDim,boxShadow:'0 16px 60px #71613a13'}}><Chart p={param} residual={1} label={returning>.5?'同一批数据，误差更小。':undefined}/></div>
  <div style={{position:'absolute',left:310,top:1210,display:'flex',gap:60,opacity:1-map+returning,transform:`translateY(${-map*70*(1-returning)}px)`}}><Knob value={param[0]+.8} name="斜率 a" color={c.red}/><Knob value={param[1]+.5} name="截距 b" color={c.green}/></div>
  <svg width="1080" height="1920" style={{position:'absolute',inset:0,pointerEvents:'none'}}>
   {map>.01&&handoff<.99&&<><path d={`M670 1320Q920 1200 ${origin[0]} ${origin[1]}`} fill="none" stroke={c.green} strokeWidth="2" strokeDasharray="6 8" opacity={map*.45}/><circle cx={mapBallX} cy={mapBallY} r="13" fill={c.green}/></>}
  </svg>
  {onMap>.8&&<div style={{position:'absolute',left:Math.min(820,Math.max(80,marker[0]+mix(32,-200,close))),top:Math.max(480,marker[1]-mix(83,165,close)),fontSize:25,color:c.green,background:'#fcf8eddc',padding:'10px 15px',opacity:(1-compare)*(1-returning)*handoff}}>误差 {loss(param).toFixed(3)}</div>}
  {onMap>.8&&f<e.local.frame&&<><div style={{position:'absolute',left:180,top:1440,fontSize:25,color:c.red}}>斜率 a = {(param[0]+.8).toFixed(2)}</div><div style={{position:'absolute',left:650,top:1440,fontSize:25,color:c.green}}>截距 b = {(param[1]+.5).toFixed(2)}</div></>}
  <div style={{position:'absolute',left:75,right:75,top:1490,fontFamily:serif,fontSize:35,opacity:f>=e.local.frame&&f<e.term.frame?1:0}}><span style={{color:c.red,opacity:compA}}>斜率方向</span><span style={{color:c.green,opacity:compB,marginLeft:40}}>截距方向</span><span style={{color:'#a6762d',opacity:resultant,marginLeft:40}}>→ 合成</span></div>
  {compareIn>.01&&f<e.return.frame&&<div style={{position:'absolute',left:75,right:75,top:1480,display:'flex',justifyContent:'space-between',opacity:compareIn,fontSize:24}}>{[['小步',paths.small,c.gold],['大步',paths.large,c.red],['合适',paths.normal,c.green]].map(([label,points,color])=><div key={label as string} style={{color:color as string,lineHeight:1.7}}><div>{label as string} · {Math.min(3,Math.floor(comparisonPhase+.001))}/3 步</div><div>误差 {loss(at(points as Param[],comparisonPhase)).toFixed(3)}</div></div>)}</div>}
  <div style={{position:'absolute',left:65,right:65,top:1710,fontSize:35,lineHeight:1.6,textAlign:'center'}}>{caption}</div>
  <Audio src={staticFile(timing.audio)} volume={.85}/>{timing.sfx.map((v,i)=><Sequence key={i} from={v.frame}><Audio src={staticFile(v.audio)} volume={v.volume}/></Sequence>)}
 </AbsoluteFill>;
};
