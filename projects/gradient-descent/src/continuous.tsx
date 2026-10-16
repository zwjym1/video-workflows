import React from 'react';
import {AbsoluteFill, Sequence, interpolate, Easing, useCurrentFrame, staticFile} from 'remotion';
import {Audio} from '@remotion/media';
import timing from './edge-timings.json';

const ink='#34312b', red='#a64531', teal='#34746a', paper='#eee5cf';
const sans='"Microsoft YaHei",sans-serif';
const serif='"SimSun","Microsoft YaHei",serif';
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const ramp=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
const key=(f:number,points:number[],values:number[])=>interpolate(f,points,values,{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.inOut(Easing.cubic)});
const begin=(i:number,word:string)=>{
 const b=timing[i].boundaries.find(b=>b.text===word);
 return timing[i].start+Math.round((b?.offset??0)*30);
};
const cues=[begin(1,'位置'),begin(1,'问题'),begin(1,'目标'),begin(1,'限制')];
const act=timing[2].start, end=timing[3].start;

const Stroke:React.FC<{d:string;p:number;color?:string;width?:number;dash?:boolean}>=({d,p,color=red,width=4,dash=false})=><path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={dash?'9 12':1} strokeDashoffset={dash?0:1-p} opacity={dash?p:1}/>;

export const Page:React.FC<{growth:number;focus:number;title:string;measure?:number;retain?:number;detail?:number}>=({growth:g,focus,title,measure=0,retain=0,detail=g})=><div style={{width:800,height:800,background:'#faf5e8',boxShadow:'0 18px 48px #56462b22',border:'1px solid #c5b99d',position:'relative',overflow:'hidden'}}>
 <div style={{height:55,borderBottom:'1px solid #cfc4ac',display:'flex',alignItems:'center',padding:'0 30px',gap:12,color:'#8d826d',fontSize:16,letterSpacing:3}}><span style={{width:8,height:8,background:red,borderRadius:10}}/>FIELD / 创作练习<span style={{marginLeft:'auto'}}>01</span></div>
 <div style={{position:'absolute',left:55,top:110,color:teal,fontSize:20,letterSpacing:4}}>IDEAS INTO PRACTICE</div>
 <div style={{position:'absolute',left:55,top:175,fontFamily:serif,fontSize:mix(38,64,g),fontWeight:700,lineHeight:1.45,letterSpacing:1,zIndex:2}}>让好想法，<br/>成为好作品。</div>
 <div style={{position:'absolute',left:55,top:mix(325,405,g),fontSize:27,lineHeight:1.8,color:ink,opacity:mix(.92,.42,detail)}}>把灵感整理成清晰的下一步。<br/>专注创作，让协作更简单。</div>
 <div style={{position:'absolute',left:55,top:mix(467,547,g),padding:'19px 32px',background:teal,color:'#fff9e9',fontSize:25,borderRadius:3}}>开始创作 ↗</div>
 <svg width="220" height="330" style={{position:'absolute',right:35,top:180,transform:`rotate(${mix(9,-3,g)}deg)`}} viewBox="0 0 220 330">
  <path d="M30 30L194 12L205 290L17 309Z" fill="#d9b793"/>
  <path d="M15 58L170 35L195 312L37 319Z" fill="#d5ddcf" stroke="#8b9f8c" strokeWidth="1"/>
  <circle cx="105" cy="155" r="59" fill="#d5a652"/>
  <path d="M70 170Q105 140 142 172M105 98V212M49 155H162" stroke="#856b38" strokeWidth="2" fill="none"/>
  <path d="M60 260L153 247M61 271L129 261" stroke="#78856f" strokeWidth="2"/>
 </svg>
 <svg width="800" height="800" style={{position:'absolute',inset:0,pointerEvents:'none'}}>
  <Stroke d="M42 162 Q210 148 465 167 L467 318 Q200 326 42 313Z" p={focus} width={3}/>
  <g opacity={measure}><path d={`M32 176H15V${mix(285,355,g)}H32`} stroke={red} strokeWidth={2} fill="none"/><text x="340" y="156" fontFamily={sans} fontSize="22" fill={red}>{Math.round(mix(38,64,g))} px</text></g>
  <g opacity={retain}><path d={`M40 ${mix(456,536,g)}H243V${mix(532,612,g)}H40Z`} fill="none" stroke={teal} strokeWidth={2} strokeDasharray="7 5"/><text x="270" y={mix(510,590,g)} fontFamily={sans} fontSize="22" fill={teal}>✓ 颜色保留</text></g>
 </svg>
 <div style={{position:'absolute',bottom:46,left:55,right:55,borderTop:'1px solid #d6ccb7',paddingTop:17,color:'#938874',fontSize:16,letterSpacing:3}}>演示界面 / {title}</div>
</div>;

const subtitle=(f:number)=>{
 const i=timing.findIndex(t=>f>=t.start&&f<t.start+t.frames);
 if(i<0)return '';
 const t=timing[i];
 const phrases=[['和 AI 改作品，你是不是也说过','再高级一点？'],['把感觉，拆成四件事','位置：哪里要改？','问题：哪里不好？','目标：改成什么？','限制：保留什么？'],['比如这个页面','标题太小，重点不清','把标题放大，说明弱化','按钮保留原来的青色','每一条，都能检查'],['再看前后对比','把模糊的不满意，写成看得见的变化']];
 const starts=[[0,begin(0,'再')],[t.start,...cues],[t.start,begin(2,'标题'),begin(2,'把'),begin(2,'按钮'),begin(2,'每')],[t.start,begin(3,'把')]][i];
 let n=0;starts.forEach((v,j)=>{if(f>=v)n=j;});
 return phrases[i][n];
};

export const Continuous=()=>{
 const f=useCurrentFrame();
 const explore=ramp(f,150,205), apply=ramp(f,act-12,act+30), compare=ramp(f,end-12,end+35);
 const growth=ramp(f,begin(2,'把'),begin(2,'把')+58);
 const px=key(f,[0,150,205,act-12,act+30,end-12,end+35],[140,140,260,260,140,140,568]);
 const py=key(f,[0,150,205,act-12,act+30,end-12,end+35],[740,740,745,745,610,610,810]);
 const ps=key(f,[0,150,205,act-12,act+30,end-12,end+35],[1,1,.7,.7,1,1,.55]);
 const wordOpacity=1-ramp(f,150,215)*.78;
 const framework=explore*(1-apply);
 const labels=['位置','问题','目标','限制'];
 const descriptions=['首页标题','太小，层级不清','放大标题，弱化说明','保留青色按钮'];
 const coords=[[80,530],[610,565],[70,1320],[615,1305]];
 const paths=['M230 643 Q210 756 347 875','M750 682 Q810 790 596 880','M240 1300 Q250 1130 435 1020','M760 1282 Q815 1200 375 1095'];
 const active=cues.reduce((n,c,i)=>f>=c?i:n,-1);
 const noteAlpha=ramp(f,act+35,act+60)*(1-compare);
 const section=f<150?'一句感觉':f<act?'拆成四个问题':f<end?'让修改发生':'检查可见的变化';
 return <AbsoluteFill style={{background:paper,color:ink,fontFamily:sans,overflow:'hidden'}}>
  <AbsoluteFill style={{backgroundImage:'radial-gradient(#9c876e22 .8px,transparent .8px),linear-gradient(#a6937220 1px,transparent 1px),linear-gradient(90deg,#a6937220 1px,transparent 1px)',backgroundSize:'7px 7px,54px 54px,54px 54px',opacity:.55}}/>
  <div style={{position:'absolute',top:0,bottom:0,left:40,width:1,background:'#bb705b22'}}/>
  <div style={{position:'absolute',left:80,right:80,top:90,display:'flex',alignItems:'center',gap:18,fontSize:20,letterSpacing:4,color:'#857660'}}><span style={{background:red,color:paper,padding:'7px 12px'}}>01</span>AI 协作笔记<span style={{marginLeft:'auto',letterSpacing:1}}>连续动效练习</span></div>
  <div style={{position:'absolute',left:80,top:200,fontFamily:serif,fontSize:68,fontWeight:700,lineHeight:1.38,letterSpacing:2}}><span style={{color:red}}>“高级”</span>到底怎么改？</div>
  <div style={{position:'absolute',left:84,top:310,fontSize:26,color:'#897b65',letterSpacing:5}}>{section}</div>

  {/* One persistent page is carried through every beat; its state changes in place. */}
  <div style={{position:'absolute',left:px,top:py,transform:`scale(${ps}) rotate(${mix(-2,0,explore)}deg)`,transformOrigin:'0 0',zIndex:3}}><Page growth={growth} focus={ramp(f,cues[0],cues[0]+25)*(1-ramp(f,act+130,act+165))} measure={ramp(f,begin(2,'把')-15,begin(2,'把')+8)*(1-ramp(f,begin(2,'按钮')-10,begin(2,'按钮')+10))} retain={ramp(f,begin(2,'按钮'),begin(2,'按钮')+20)*(1-compare)} title={compare>.5?'修改后':'待修改'}/></div>

  <div style={{position:'absolute',left:mix(160,80,explore),top:mix(465,405,explore),transform:`scale(${mix(1,.68,explore)}) rotate(-3deg)`,transformOrigin:'0 0',opacity:wordOpacity*(1-apply),zIndex:5}}>
   <div style={{fontFamily:serif,fontSize:72,letterSpacing:3}}>再高级一点</div>
   <svg width="650" height="40"><Stroke d="M2 18Q245 36 584 9" p={ramp(f,105,145)} width={5}/></svg>
  </div>
  <svg width="1080" height="1920" style={{position:'absolute',inset:0,zIndex:4,pointerEvents:'none'}}>
   <g opacity={(1-explore)*ramp(f,75,100)}><Stroke d="M730 550Q845 600 760 710M760 710L755 675M760 710L790 690" p={ramp(f,75,115)} width={4}/><text x="800" y="645" fill={red} fontSize="34" fontFamily={serif}>改哪儿？</text></g>
   {paths.map((d,i)=><g key={d} opacity={framework*(active===i?1:.42)}><Stroke d={d} p={ramp(f,cues[i],cues[i]+25)} color={i===3?teal:red} width={3}/></g>)}
  </svg>

  {labels.map((label,i)=>{const seen=ramp(f,cues[i],cues[i]+18);const current=active===i;return <div key={label} style={{position:'absolute',left:mix(coords[i][0],80+i*245,apply),top:mix(coords[i][1],430,apply),width:320,opacity:seen*explore*(1-compare),transform:`scale(${mix(1,.65,apply)}) translateY(${(1-seen)*20}px)`,transformOrigin:'0 0',zIndex:6}}>
   <div style={{display:'flex',alignItems:'baseline',gap:16,color:current&&apply<.5?red:ink}}><span style={{fontFamily:serif,fontSize:24,color:red}}>0{i+1}</span><span style={{fontFamily:serif,fontSize:50,fontWeight:700}}>{label}</span></div>
   <div style={{fontSize:27,lineHeight:1.5,marginTop:16,opacity:1-apply,color:i===3?teal:ink}}>{descriptions[i]}</div>
  </div>})}

  <div style={{position:'absolute',left:95,top:1470,opacity:noteAlpha,zIndex:6}}><div style={{fontFamily:serif,fontSize:41,color:red}}>把“感觉”落到对象上</div><div style={{fontSize:29,marginTop:24,color:'#766954'}}>标题变大 · 说明变轻 · 按钮保留</div><svg width="850" height="36"><Stroke d="M0 15Q370 29 825 10" p={ramp(f,act+160,act+200)} width={2}/></svg></div>

  {/* The original state enters beside the same modified page as the camera pulls back. */}
  <div style={{position:'absolute',left:mix(-520,70,compare),top:810,transform:'scale(.55)',transformOrigin:'0 0',opacity:compare,zIndex:2}}><Page growth={0} focus={0} title="修改前"/></div>
  <div style={{position:'absolute',left:80,top:650,opacity:compare,fontFamily:serif,fontSize:48}}>从模糊的要求，<br/><span style={{color:red}}>到看得见的变化。</span></div>
  <div style={{position:'absolute',left:70,top:755,fontSize:23,color:'#897b65',opacity:compare}}>修改前</div><div style={{position:'absolute',left:568,top:755,fontSize:23,color:teal,opacity:compare}}>修改后</div>
  <div style={{position:'absolute',left:520,top:995,fontSize:45,color:red,opacity:compare,zIndex:5}}>→</div>
  <div style={{position:'absolute',left:80,top:1370,opacity:compare}}><div style={{fontFamily:serif,fontSize:42}}>位置 → 问题 → 目标 → 限制</div><div style={{fontSize:27,color:'#84765f',marginTop:26}}>每一条意见，都有可以检查的落点。</div></div>

  <div style={{position:'absolute',left:65,right:65,top:1690,textAlign:'center',fontSize:36,lineHeight:1.65,fontWeight:500}}>{subtitle(f)}</div>
  <div style={{position:'absolute',left:80,right:80,bottom:80,borderTop:'1px solid #bbaa8b',paddingTop:19,display:'flex',justifyContent:'space-between',fontSize:18,color:'#8f8068'}}><span>代码演示 / 非真实操作录屏</span><span>Edge TTS · 云希</span></div>
  {timing.map((t,i)=><Sequence key={i} from={t.start} durationInFrames={t.frames}><Audio src={staticFile(t.audio)}/></Sequence>)}
 </AbsoluteFill>;
};
