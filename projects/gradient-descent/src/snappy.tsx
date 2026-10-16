import React from 'react';
import {AbsoluteFill,Sequence,interpolate,Easing,useCurrentFrame,staticFile} from 'remotion';
import {Audio} from '@remotion/media';
import {Page} from './continuous';
import timing from './v3-timings.json';

const red='#a64531', teal='#34746a', ink='#34312b', paper='#eee5cf';
const serif='"SimSun","Microsoft YaHei",serif',sans='"Microsoft YaHei",sans-serif';
// Fast arrival, bounded settling. Reading holds are separate from travel time.
const move=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.bezier(.16,.78,.25,1)});
const linear=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const word=(i:number,text:string)=>{const b=timing[i].boundaries.find(b=>b.text===text);if(!b)throw new Error(`Missing voice cue: ${i}/${text}`);return timing[i].start+Math.round(b.offset*30);};
const position=word(1,'位置'),problem=word(1,'问题'),target=word(2,'目标'),grow=word(2,'放大'),weaken=word(2,'弱化'),limit=word(2,'限制'),keep=word(2,'保留');
const compareStart=timing[3].start-7;
const cues=[position,problem,target,limit];
const Stroke:React.FC<{d:string;p:number;color?:string;width?:number}>=({d,p,color=red,width=4})=><path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1-p}/>;

const subtitle=(f:number)=>{
 const parts:[number,string][]=[
  [0,'再高级一点？'],[word(0,'这'),'这句话，AI 该改哪里？'],
  [timing[1].start,'先指出位置：首页标题'],[word(1,'说'),'说清问题：太小，重点不清'],
  [timing[2].start,'再给出目标：标题放大，说明弱化'],[word(2,'也'),'也划清限制：按钮保留青色'],
  [timing[3].start,'看，修改前后，一眼就能检查'],[word(3,'把'),'把感觉，变成具体改法'],
 ];const eligible=parts.filter(([start])=>f>=start);return eligible[eligible.length-1]?.[1]??'';
};

export const Snappy=()=>{
 const f=useCurrentFrame();
 // Anticipate the next spoken beat by 5–7 frames, with no full-scene fade.
 const locate=move(f,position-7,position+9), push=move(f,problem-6,problem+10), apply=move(f,target-6,target+8), compare=move(f,compareStart,compareStart+18);
 const growth=move(f,grow-4,grow+14), detail=move(f,weaken-4,weaken+6);
 const x=mix(mix(mix(140,160,locate),105,push),568,compare);
 const y=mix(mix(mix(760,690,locate),610,push),800,compare);
 const scale=mix(mix(mix(.98,.95,locate),1.08,push),.55,compare);
 const focus=move(f,position-6,position+4)*(1-move(f,grow-8,grow+2));
 const measure=move(f,grow-8,grow-1)*(1-move(f,weaken+5,weaken+11));
 const retain=move(f,keep-5,keep+3)*(1-compare);
 const introOut=move(f,position-10,position+1);
 const active=cues.reduce((n,c,i)=>f>=c-5?i:n,-1);
 const labelFade=1-compare;
 const words=['位置','问题','目标','限制'];
 const detailText=['首页标题','太小，重点不清','标题放大 · 说明弱化','按钮保留青色'];
 const state=f<position?'感觉太模糊':f<problem?'01 / 指向对象':f<target?'02 / 说清问题':f<limit?'03 / 给出改法':f<compareStart?'04 / 划清边界':'前后对照 / 验证结果';
 const mainTitleY=mix(200,170,locate);
 return <AbsoluteFill style={{background:paper,color:ink,fontFamily:sans,overflow:'hidden'}}>
  <AbsoluteFill style={{backgroundImage:'radial-gradient(#9c876e20 .8px,transparent .8px),linear-gradient(#a693721b 1px,transparent 1px),linear-gradient(90deg,#a693721b 1px,transparent 1px)',backgroundSize:'7px 7px,54px 54px,54px 54px'}}/>
  <div style={{position:'absolute',left:40,top:0,bottom:0,width:1,background:'#bb705b22'}}/>
  <div style={{position:'absolute',left:80,right:80,top:90,display:'flex',gap:18,alignItems:'center',color:'#857660',fontSize:20,letterSpacing:3}}><span style={{background:red,color:paper,padding:'7px 12px'}}>01</span>AI 协作笔记<span style={{marginLeft:'auto',letterSpacing:1}}>节奏优化版</span></div>
  <div style={{position:'absolute',top:mainTitleY,left:80,fontFamily:serif,fontWeight:700,fontSize:66,lineHeight:1.4}}>把<span style={{color:red}}>“感觉”</span>变成改法</div>
  <div style={{position:'absolute',left:84,top:mainTitleY+110,fontSize:25,color:'#84755f',letterSpacing:3}}>{state}</div>

  <div style={{position:'absolute',left:x,top:y,transform:`scale(${scale}) rotate(${mix(-2,0,locate)}deg)`,transformOrigin:'0 0',zIndex:3}}><Page growth={growth} detail={detail} focus={focus} measure={measure} retain={retain} title={compare>.5?'修改后':growth>.95?'已修改':'待修改'}/></div>

  <div style={{position:'absolute',left:160,top:445,opacity:1-introOut,transform:`translateY(${-introOut*30}px) rotate(-3deg)`,zIndex:5}}><div style={{fontFamily:serif,fontSize:76}}>再高级一点？</div><svg width="730" height="155"><Stroke d="M5 25Q240 43 622 17" p={linear(f,39,47)}/><Stroke d="M640 35Q755 70 651 143M651 143L659 111M651 143L684 131" p={linear(f,75,84)}/><text x="400" y="110" fill={red} fontSize="35" fontFamily={serif}>具体改哪里？</text></svg></div>

  {/* Each item hands off to the next while staying anchored to the same object. */}
  {words.map((w,i)=>{
   const cue=cues[i],seen=move(f,cue-6,cue+2),next=i<3?move(f,cues[i+1]-7,cues[i+1]+3):0;
   const mini=next, highlighted=active===i;
   const left=mix(80,80+i*236,mini),top=mix(405,350,mini),s=mix(1,.64,mini);
   return <div key={w} style={{position:'absolute',left,top,width:900,transform:`scale(${s}) translateY(${(1-seen)*16}px)`,transformOrigin:'0 0',opacity:seen*labelFade,zIndex:6}}>
    <div style={{fontFamily:serif,fontSize:48,color:highlighted?(i===3?teal:red):'#82745f'}}><span style={{fontSize:23,marginRight:16}}>0{i+1}</span>{w}</div>
    <div style={{fontFamily:serif,fontSize:42,marginTop:18,opacity:1-mini,color:i===3?teal:ink}}>{detailText[i]}</div>
   </div>;
  })}
  <svg width="1080" height="1920" style={{position:'absolute',inset:0,pointerEvents:'none',zIndex:4}}>
   <g opacity={locate*(1-push)}><Stroke d="M350 560Q235 607 230 850M230 850L212 823M230 850L250 827" p={move(f,position-3,position+7)} width={3}/></g>
   <g opacity={push*(1-apply)}><Stroke d="M560 554Q605 680 554 793" p={move(f,problem-4,problem+7)} width={3}/></g>
   <g opacity={apply*(1-move(f,limit-7,limit+2))}><Stroke d="M373 552Q230 600 217 790" p={move(f,target-2,target+7)} width={3}/></g>
  </svg>

  <div style={{position:'absolute',left:95,top:1535,zIndex:5,opacity:move(f,grow+13,grow+19)*(1-compare),color:teal,fontSize:29}}>✓ 标题放大<span style={{opacity:move(f,weaken+4,weaken+9),marginLeft:35}}>✓ 说明弱化</span><span style={{opacity:move(f,keep+2,keep+7),marginLeft:35}}>✓ 按钮保留</span></div>

  <div style={{position:'absolute',left:mix(-410,70,compare),top:800,opacity:compare,transform:'scale(.55)',transformOrigin:'0 0',zIndex:2}}><Page growth={0} detail={0} focus={0} title="修改前"/></div>
  <div style={{position:'absolute',left:80,top:505,opacity:compare,transform:`translateY(${(1-compare)*18}px)`,fontFamily:serif,fontSize:52,lineHeight:1.5}}>改没改好，<br/><span style={{color:red}}>用结果来检查。</span></div>
  <div style={{position:'absolute',left:70,top:745,color:'#897b65',fontSize:25,opacity:compare}}>修改前</div><div style={{position:'absolute',left:568,top:745,color:teal,fontSize:25,opacity:compare}}>修改后</div>
  <div style={{position:'absolute',left:518,top:990,color:red,fontSize:45,opacity:compare,zIndex:5}}>→</div>
  <div style={{position:'absolute',left:80,top:1370,opacity:move(f,compareStart+14,compareStart+23),fontFamily:serif,fontSize:42}}>位置 → 问题 → 目标 → 限制</div>
  <div style={{position:'absolute',left:80,top:1455,fontSize:28,color:'#84765f',opacity:move(f,word(3,'把')-5,word(3,'把')+3)}}>每条意见，都有可检查的落点。</div>

  <div style={{position:'absolute',left:65,right:65,top:1690,textAlign:'center',fontSize:36,lineHeight:1.65,fontWeight:500}}>{subtitle(f)}</div>
  <div style={{position:'absolute',left:80,right:80,bottom:80,borderTop:'1px solid #bbaa8b',paddingTop:19,display:'flex',justifyContent:'space-between',fontSize:18,color:'#8f8068'}}><span>代码演示 / 非真实操作录屏</span><span>Edge TTS · 云希</span></div>
  {timing.map((t,i)=><Sequence key={i} from={t.start} durationInFrames={t.frames}><Audio src={staticFile(t.audio)}/></Sequence>)}
 </AbsoluteFill>;
};
