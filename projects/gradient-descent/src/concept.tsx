import React from 'react';
import {AbsoluteFill,Audio,Easing,interpolate,staticFile,useCurrentFrame} from 'remotion';
import timing from './concept-timing.json';

const c={paper:'#eee5cf',white:'#fcf7ea',ink:'#34312b',red:'#a64531',green:'#34746a',muted:'#93836a'};
const serif='"SimSun","Microsoft YaHei",serif',sans='"Microsoft YaHei",sans-serif';
const ease=Easing.bezier(.18,.76,.28,1);
const progress=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:ease});
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const word=(text:string)=>{const b=timing.boundaries.find(b=>b.text.includes(text));if(!b)throw new Error(`Missing narration word: ${text}`);return Math.round(b.offset*30);};
const colorAt=word('颜色'),layoutAt=word('排版'),lockAt=word('锁定'),intentAt=word('明确'),growAt=word('放大');
const Path:React.FC<{d:string;p:number;color?:string;w?:number;opacity?:number}>=({d,p,color=c.red,w=4,opacity=1})=>p<=0?null:<path d={d} fill="none" stroke={color} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1-p} opacity={opacity}/>;

export const Concept=()=>{
 const f=useCurrentFrame();
 const branch=progress(f,19,37),lock=progress(f,lockAt-5,lockAt+12);
 const color=progress(f,colorAt-3,colorAt+8),layout=progress(f,layoutAt-3,layoutAt+9);
 const arrival=growAt+6,growth=progress(f,arrival,arrival+15);
 const titleX=mix(750,180,lock),titleY=mix(890,670,lock),titleS=mix(1,2.6,lock);
 const off=(1-lock),otherOpacity=1-progress(f,lockAt-5,lockAt+4);
 const quoteY=mix(360,330,lock),quoteScale=mix(1,.62,lock);
 const token=progress(f,growAt-8,arrival),tokenOpacity=progress(f,growAt-9,growAt-6)*(1-progress(f,arrival+3,arrival+8));
 const target=[titleX+241*titleS,titleY+110*titleS];
 const tokenX=(1-token)**2*640+2*(1-token)*token*930+token**2*target[0];
 const tokenY=(1-token)**2*470+2*(1-token)*token*520+token**2*target[1];
 const subtitle=f<40?'“再高级一点”？':f<layoutAt-3?'改颜色？':f<lockAt-9?'还是改排版？':f<intentAt-4?'先锁定标题':f<growAt-3?'再明确改法':'放大。';
 return <AbsoluteFill style={{background:c.paper,color:c.ink,fontFamily:sans,overflow:'hidden'}}>
  <AbsoluteFill style={{backgroundImage:'radial-gradient(#9c876e22 .8px,transparent .8px),linear-gradient(#a693721b 1px,transparent 1px),linear-gradient(90deg,#a693721b 1px,transparent 1px)',backgroundSize:'7px 7px,54px 54px,54px 54px',transform:`translateY(${-lock*12}px)`}}/>
  <div style={{position:'absolute',top:100,left:80,fontSize:21,letterSpacing:5,color:c.muted}}>AI 协作笔记 / 视觉叙事实验</div>
  <div style={{position:'absolute',left:80,top:quoteY,transform:`scale(${quoteScale})`,transformOrigin:'0 0',opacity:1-progress(f,lockAt+6,lockAt+15)*.6}}><div style={{fontFamily:serif,fontSize:83,lineHeight:1.35}}>再<span style={{color:c.red}}>高级</span>一点？</div><div style={{fontSize:27,color:c.muted,marginTop:25,opacity:branch*off}}>同一句话，可能指向三个方向。</div></div>
  <div style={{position:'absolute',top:420,left:80,fontFamily:serif,fontSize:65,color:c.red,opacity:progress(f,lockAt+5,lockAt+13)}}>先锁定，再改变。</div>

  <svg width="1080" height="1920" style={{position:'absolute',inset:0,pointerEvents:'none'}}>
   <g opacity={off}><Path d="M500 575C500 710 195 680 195 865" p={branch} color={c.muted} w={3}/><Path d="M500 575C500 720 540 715 540 865" p={branch} color={c.muted} w={3}/></g>
   <Path d={`M${mix(500,800,lock)} ${mix(575,570,lock)}C${mix(500,900,lock)} ${mix(730,620,lock)} ${mix(885,850,lock)} ${mix(685,650,lock)} ${mix(885,805,lock)} ${mix(865,670,lock)}`} p={branch} color={lock>.01?c.red:c.muted} w={mix(3,5,lock)} opacity={1-progress(f,lockAt+8,lockAt+14)}/>
   <circle cx="500" cy="575" r={6} fill={c.red} opacity={branch*off}/>
  </svg>

  {/* Possible meanings appear together, then react individually to the narration. */}
  <div style={{position:'absolute',left:60-lock*250,top:890+lock*90,width:270,height:340,opacity:branch*otherOpacity,transform:`rotate(${-5-lock*12}deg)`,background:c.white,boxShadow:'0 14px 35px #6c553b22'}}>
   <div style={{padding:'32px 27px',fontFamily:serif,fontSize:37}}>改颜色？</div>
   <div style={{margin:'0 27px',height:100,background:color>.5?c.green:'#d2b288',position:'relative',overflow:'hidden'}}><div style={{position:'absolute',inset:0,background:c.green,transform:`translateX(${(1-color)*-100}%)`}}/><div style={{position:'absolute',inset:20,border:'1px solid #fff7',color:c.white,fontSize:23,padding:12}}>让想法发光</div></div>
   <div style={{display:'flex',gap:16,padding:27}}>{['#d2b288',c.green,c.red].map((bg,i)=><div key={bg} style={{width:42,height:42,borderRadius:24,background:bg,transform:`translateY(${i===1?-color*8:0}px)`,outline:i===1&&color>.9?`2px solid ${c.green}`:undefined,outlineOffset:5}}/>)}</div>
  </div>
  <div style={{position:'absolute',left:405,top:890+lock*230,width:270,height:340,opacity:branch*otherOpacity,transform:`rotate(${3+lock*10}deg)`,background:c.white,boxShadow:'0 14px 35px #6c553b22'}}>
   <div style={{padding:'32px 27px',fontFamily:serif,fontSize:37}}>改排版？</div>
   <div style={{position:'absolute',left:27,top:120,width:mix(80,216,layout),height:mix(135,58,layout),background:'#c9d4c5'}}/>
   {[0,1,2].map(i=><div key={i} style={{position:'absolute',left:mix(125,27,layout),top:mix(125+i*35,203+i*26,layout),width:mix(i===2?75:116,i===2?160:216,layout),height:10,background:'#b6aa91'}}/>)}
  </div>

  {/* The title paper is the same object from the branch through the final change. */}
  <div style={{position:'absolute',left:titleX,top:titleY,width:270,height:340,transform:`scale(${titleS}) rotate(${mix(4,0,lock)}deg)`,transformOrigin:'0 0',background:c.white,boxShadow:'0 14px 35px #6c553b22',opacity:branch,zIndex:3}}>
   <div style={{position:'absolute',left:27,top:28,fontFamily:serif,fontSize:mix(37,17,lock),color:lock>.5?c.red:c.ink}}>{lock>.5?'修改对象 / 标题':'改标题？'}</div>
   <div style={{position:'absolute',left:27,top:mix(120,100,lock),fontFamily:serif,fontWeight:700,fontSize:mix(24,42,growth),lineHeight:1.4}}>让想法<br/>成为作品</div>
   <div style={{position:'absolute',left:27,top:mix(225,245,growth),width:170,height:3,background:'#d7ccb7',opacity:1-growth*.6}}/>
   <div style={{position:'absolute',left:27,top:284,fontSize:11,color:c.muted,opacity:lock}}>内容不变，层级更清楚。</div>
   <svg width="270" height="340" style={{position:'absolute',inset:0}}>
    <g opacity={progress(f,lockAt+9,lockAt+14)}><Path d={`M19 93H12V${mix(170,225,growth)}H19`} p={1} color={c.red} w={1.5}/><text x="180" y="85" fill={c.red} fontSize="13" fontFamily={sans}>{Math.round(mix(24,42,growth))} px</text></g>
    <circle cx="241" cy="110" r={mix(3,7,progress(f,arrival,arrival+5))} fill="none" stroke={c.red} strokeWidth={1.5} opacity={progress(f,arrival-1,arrival+1)*(1-progress(f,arrival+4,arrival+9))}/>
   </svg>
  </div>

  <svg width="1080" height="1920" style={{position:'absolute',inset:0,zIndex:5,pointerEvents:'none'}}>
   <g opacity={progress(f,intentAt-4,intentAt+4)*(1-progress(f,arrival+4,arrival+9))}><Path d={`M640 470Q930 520 ${target}`} p={token} w={2} opacity={.5}/></g>
   <g opacity={tokenOpacity} transform={`translate(${tokenX},${tokenY}) rotate(${-4*(1-token)})`}><rect x="-58" y="-30" width="116" height="60" rx="4" fill={c.red}/><text x="0" y="12" textAnchor="middle" fontFamily={serif} fontSize="36" fill={c.white}>放大</text></g>
  </svg>
  <div style={{position:'absolute',left:180,top:1580,fontFamily:serif,fontSize:43,color:c.green,opacity:progress(f,arrival+17,arrival+23)}}>✓ 改哪里、怎么改，都清楚了。</div>
  <div style={{position:'absolute',left:65,right:65,top:1720,textAlign:'center',fontSize:38}}>{subtitle}</div>
  <div style={{position:'absolute',left:80,right:80,bottom:70,paddingTop:20,borderTop:'1px solid #bbaa8b',display:'flex',justifyContent:'space-between',color:c.muted,fontSize:18}}><span>8秒代表段 / 代码演示</span><span>Edge TTS · 云希</span></div>
  <Audio src={staticFile('concept-voice.mp3')}/>
 </AbsoluteFill>;
};
