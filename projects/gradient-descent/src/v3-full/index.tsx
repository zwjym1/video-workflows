import React from 'react';
import {AbsoluteFill,Audio,Img,Sequence,interpolate,Easing,staticFile,useCurrentFrame} from 'remotion';
import {al,G,S,DURATION} from './events';
import {rand} from '../v3-shared/words';
import {Caption} from '../v3-shared/caption';
import {DataChart} from './chart';
import {Teach} from './teach';
import {Chalk,chalkSfx} from './chalk';
import {Param,paths,at,initial,loss} from '../gradient-story/model';
export {DURATION as V3_FULL_DURATION};
const gold='#d8b46a',goldHi='#f3d79a',ink='#0d0c0a',paper='#f4efe4';
const serif='"Noto Serif CJK SC","SimSun",serif',sans='"Microsoft YaHei","Noto Sans CJK SC",sans-serif',latin='"Noto Serif","Georgia",serif';
const snap=Easing.bezier(.16,1,.3,1);
const r=(f:number,a:number,b:number,e=snap)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:e});
const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
const valley=(u:number):[number,number]=>[540+u*420,1240-400*u*u];
const U0=-.6,U1=-.6*Math.sqrt(loss([.78,.36])/loss(initial)); // display: height ∝ model MSE, 2.160 -> 0.434
const errAt=(u:number)=>loss(initial)*(u/U0)**2;
// ---------------- Hook (0 .. data) ----------------
const tileHues=[['#6b4bd8','#f2a65a'],['#1e7fd0','#f4e3a1'],['#c2417b','#3b2a7a'],['#2a9d8f','#e9c46a']];
const NP=640;const PP=(()=>{const R=rand(2026);return Array.from({length:NP},(_,i)=>{const inTiles=i<420;const tile=i%4;const sx=inTiles?190+(tile%2)*350+R()*330:140+R()*800,sy=inTiles?700+Math.floor(tile/2)*270+R()*250:400+R()*290;const col=inTiles?tileHues[tile][R()<.5?0:1]:(R()<.5?'#e8e6e3':'#6d6a66');const th=R()*Math.PI*2,v=.4+R();return{sx,sy,col,vx:Math.cos(th)*v,vy:Math.sin(th)*v-.3,u:R()*2-1,s:1.2+R()*2.4,ph:R()*6};});})();
const Hook=()=>{
 const f=useCurrentFrame();
 const shatter=r(f,G.much,G.much+14),conv=r(f,G.much+8,G.downhill,Easing.inOut(Easing.cubic)),card=1-r(f,G.much,G.much+2);
 const ballIn=r(f,G.downhill-6,G.downhill+4),step=r(f,G.shan,G.shan+12),rewind=r(f,G.but,G.but+14,Easing.inOut(Easing.cubic));
 const u=mix(mix(U0,U1,step),U0,rewind),ball=valley(u),err=errAt(u);
 const blind=r(f,G.blind,G.blind+16),errPop=r(f,G.errWord,G.errWord+10),where=r(f,G.where,G.where+12),title=r(f,G.downhill,G.downhill+10)*(1-r(f,G.but,G.but+8));
 const iris=r(f,S.data-14,S.data+2,Easing.inOut(Easing.cubic));
 const zoom=mix(1.06,1,r(f,0,G.much));
 return <AbsoluteFill style={{background:ink,overflow:'hidden',fontFamily:sans}}>
  <AbsoluteFill style={{background:'radial-gradient(ellipse 760px 900px at 50% 58%,#3a2a1066 0%,transparent 70%)',opacity:conv}}/>
  {/* chat window (mid-action at frame 0) */}
  {card>0&&<div style={{position:'absolute',left:120,top:380,width:840,height:820,borderRadius:28,background:'#1b1b1d',boxShadow:'0 40px 120px #000',transform:`scale(${zoom})`,overflow:'hidden'}}>
   <div style={{height:70,borderBottom:'1px solid #2c2c2f',display:'flex',alignItems:'center',paddingLeft:30,color:'#cfcfd4',fontSize:28,gap:14}}><div style={{width:16,height:16,borderRadius:8,background:'#3ecf8e'}}/>AI 助手</div>
   <div style={{position:'absolute',right:30,top:100,background:'#2f6fed',color:'#fff',fontSize:30,padding:'14px 22px',borderRadius:22}}>画一张月光下的猫</div>
   <div style={{position:'absolute',left:30,top:190,color:'#e8e6e3',fontSize:30}}>好的，为你生成了 4 张：<span style={{opacity:Math.floor(f/8)%2}}>▍</span></div>
   {tileHues.map((h,i)=><div key={i} style={{position:'absolute',left:70+(i%2)*350,top:320+Math.floor(i/2)*270,width:330,height:250,borderRadius:16,background:`radial-gradient(circle at ${30+i*15}% ${35+i*8}%,${h[1]} 0%,${h[0]} 55%,#0d0b1a 100%)`}}><div style={{position:'absolute',left:'38%',top:'40%',width:70,height:70,borderRadius:'50%',background:'#f8f1d8',boxShadow:'0 0 40px #fff8'}}/></div>)}
  </div>}
  <svg width="1080" height="1920" style={{position:'absolute',inset:0}}>
   {shatter>0&&PP.map((p,i)=>{const ex=p.sx+p.vx*260*shatter,ey=p.sy+p.vy*260*shatter+40*shatter*shatter;const v=valley(p.u),wob=Math.sin(f*.09+p.ph)*10;const x=mix(ex,v[0],conv),y=mix(ey,v[1]+wob,conv);return <circle key={i} cx={x} cy={y} r={p.s*mix(1.4,.9,conv)} fill={conv>.5?(i%5?gold:goldHi):p.col} opacity={mix(1,.85,conv)*(1-blind*.85)}/>;})}
   {conv>.5&&<path d={Array.from({length:61},(_,i)=>{const v=valley(-1+i/30);return(i?'L':'M')+v[0].toFixed(1)+' '+v[1].toFixed(1);}).join('')} fill="none" stroke={goldHi} strokeWidth="4" opacity={(conv-.5)*2*(1-blind*.9)}/>}
   {step>0&&rewind<1&&<path d={Array.from({length:21},(_,i)=>{const v=valley(mix(U0,u,i/20));return(i?'L':'M')+v[0].toFixed(1)+' '+(v[1]-20).toFixed(1);}).join('')} fill="none" stroke="#fff" strokeWidth="6" strokeLinecap="round" opacity={.8*(1-rewind)}/>}
   {ballIn>0&&<circle cx={ball[0]} cy={ball[1]-20} r={20*ballIn} fill="#fff" style={{filter:'drop-shadow(0 0 22px #f3d79a)'}}/>}
  </svg>
  {/* blindfold darkness with spotlight hole */}
  {blind>0&&<AbsoluteFill style={{background:`radial-gradient(circle ${mix(900,190,blind)}px at ${ball[0]}px ${ball[1]-20}px,transparent 55%,#050504f2 100%)`}}/>}
  {where>0&&<svg width="1080" height="1920" style={{position:'absolute',inset:0}}>{Array.from({length:8},(_,k)=>{const a=k/8*Math.PI*2+f*.02,rr=mix(60,150,where);return <path key={k} d={`M${ball[0]+Math.cos(a)*60} ${ball[1]-20+Math.sin(a)*60}L${ball[0]+Math.cos(a)*rr} ${ball[1]-20+Math.sin(a)*rr}`} stroke={goldHi} strokeWidth="4" strokeDasharray="8 8" opacity={where*(.4+.6*((k+Math.floor(f/5))%3===0?1:0))}/>;})}<text x={ball[0]} y={ball[1]-210} textAnchor="middle" fontFamily={serif} fontSize="110" fill={goldHi} opacity={where}>?</text></svg>}
  {/* readout */}
  {ballIn>0&&<div style={{position:'absolute',left:ball[0]+(blind>0?60:50),top:ball[1]-120-errPop*20,fontFamily:latin,fontSize:mix(40,56,errPop),color:'#fff',opacity:ballIn,textShadow:`0 0 ${12+errPop*20}px ${gold}`,whiteSpace:'nowrap'}}><span style={{fontFamily:serif,fontSize:30,color:gold,marginRight:10}}>误差</span>{err.toFixed(3)}</div>}
  <div style={{position:'absolute',left:0,right:0,top:300,textAlign:'center',fontFamily:serif,fontSize:92,letterSpacing:10,color:'transparent',backgroundImage:`linear-gradient(180deg,${goldHi},${gold})`,WebkitBackgroundClip:'text',backgroundClip:'text',opacity:title,transform:`scale(${mix(1.25,1,title)})`}}>AI 学习 ≈ 下山</div>
  <div style={{position:'absolute',left:0,right:0,top:330,textAlign:'center',fontFamily:serif,fontSize:64,color:'#d9cfb8',opacity:r(f,G.blind+4,G.blind+14)*(1-where*.5)}}>看不见山，只有一个数</div>
  {iris>0&&<AbsoluteFill style={{background:paper,clipPath:`circle(${iris*2200}px at ${ball[0]}px ${ball[1]-20}px)`}}/>}
 </AbsoluteFill>;
};
// ---------------- Data (real scenario) ----------------
const DataScene=()=>{
 const f=useCurrentFrame()+S.data;
 const ptsIn=r(f,G.data,G.data+14),line=r(f,G.line,G.line+16),params=r(f,G.params,G.params+10);
 const wa=r(f,G.slope,G.slope+22,Easing.inOut(Easing.sin)),wb=r(f,G.intercept,G.intercept+22,Easing.inOut(Easing.sin));
 const p:Param=[initial[0]+Math.sin(wa*Math.PI*2)*.7,initial[1]+Math.sin(wb*Math.PI*2)*.9];
 const shrink=r(f,S.teach-14,S.teach,Easing.inOut(Easing.cubic));
 const w=mix(960,400,shrink),h=mix(760,300,shrink),x=mix(60,60,shrink),y=mix(330,110,shrink);
 return <AbsoluteFill style={{background:paper,fontFamily:sans,color:'#2f3029'}}>
  <AbsoluteFill style={{backgroundImage:'radial-gradient(#98826118 .8px,transparent .8px)',backgroundSize:'7px 7px'}}/>
  <div style={{position:'absolute',left:x,top:y,opacity:ptsIn,transform:`translateY(${(1-ptsIn)*40}px)`,boxShadow:'0 24px 70px #5a4a2a26',borderRadius:12}}><DataChart p={p} w={w} h={h} showLine={line} draw={line}/></div>
  <div style={{position:'absolute',left:60,top:120,fontFamily:serif,fontSize:54,opacity:ptsIn*(1-shrink)}}>学习时长 → 考试成绩</div>
  <div style={{position:'absolute',left:62,top:200,fontSize:26,color:'#8a7c60',opacity:ptsIn*(1-shrink)}}>5 位同学（示意数据）</div>
  <div style={{position:'absolute',left:0,right:0,top:1170,display:'flex',justifyContent:'center',gap:60,opacity:params*(1-shrink)}}>
   {[['斜率 a',p[0]+.8,'#e0662f',wa>0&&wa<1],['截距 b',p[1]+.5,'#1f6b57',wb>0&&wb<1]].map(([n,v,c,act])=><div key={n as string} style={{padding:'18px 34px',borderRadius:16,background:'#fffaf0',border:`3px solid ${c}`,color:c as string,fontSize:40,transform:`scale(${act?1.12:1})`,boxShadow:act?`0 0 30px ${c}55`:'none'}}>{n as string} = <span style={{fontFamily:latin}}>{(v as number).toFixed(2)}</span></div>)}
  </div>
  <div style={{position:'absolute',left:0,right:0,top:1310,textAlign:'center',fontSize:30,color:'#8a7c60',opacity:params*(1-shrink)}}>预测成绩 = a × 学习时长 + b</div>
 </AbsoluteFill>;
};
// ---------------- Cauchy credibility beat ----------------
const NC=380;const PC=(()=>{const R=rand(1847);return Array.from({length:NC},()=>({x:R()*1080,y:R()*1920,s:.6+R()*2.2,a:.25+R()*.75,th:R()*6.28,rr:.7+R()*.6}));})();
const CauchyScene=()=>{
 const f=useCurrentFrame()+S.cauchy;
 const enter=r(f,S.cauchy,S.cauchy+10),y=r(f,G.y1847,G.y1847+14),card=r(f,G.cauchy,G.cauchy+14),q=r(f,G.fnSmall,G.fnSmall+12),hl=r(f,G.bianxiao,G.bianxiao+8);
 return <AbsoluteFill style={{background:ink,overflow:'hidden',fontFamily:sans}}>
  <AbsoluteFill style={{background:'radial-gradient(ellipse 700px 900px at 45% 45%,#3a2a1088 0%,transparent 70%)'}}/>
  <svg width="1080" height="1920" style={{position:'absolute',inset:0}}>{PC.map((p,i)=>{const a=p.th+f*.01*(i%2?1:-1),ring=card;const x=mix((p.x+Math.sin(f*.02+p.th)*30)%1080,330+Math.cos(a)*300*p.rr,ring),yy=mix((p.y-f*.8*p.s+1920*4)%1920,820+Math.sin(a)*380*p.rr,ring);return <circle key={i} cx={x} cy={yy} r={p.s*1.6} fill={gold} opacity={p.a*enter}/>;})}</svg>
  <div style={{position:'absolute',left:mix(540,80,card),top:mix(420,180,card),transform:`translate(${mix(-50,0,card)}%,-50%) scale(${mix(1.3,1,y)})`,transformOrigin:'left center',opacity:y,fontFamily:latin,fontWeight:700,fontSize:mix(240,120,card),letterSpacing:mix(40,6,y),color:'transparent',backgroundImage:`linear-gradient(180deg,${goldHi},${gold} 55%,#8a6a32)`,WebkitBackgroundClip:'text',backgroundClip:'text',filter:`blur(${(1-y)*8}px) drop-shadow(0 0 30px #d8b46a55)`}}>1847</div>
  <div style={{position:'absolute',left:500,top:mix(1920,500,card),width:500,transform:`rotate(${mix(14,6,card)}deg)`,opacity:card,boxShadow:'0 30px 80px #000c'}}><Img src={staticFile('v3/cauchy-1847-page-1.png')} style={{width:500,display:'block',filter:'sepia(.35)'}}/></div>
  <div style={{position:'absolute',left:110,top:mix(1920,430,card),width:400,transform:`rotate(${mix(-12,-4,card)}deg)`,background:'#f1e6cc',padding:'18px 18px 22px',boxShadow:'0 30px 90px #000d',opacity:card>0?1:0}}>
   <Img src={staticFile('v3/cauchy-portrait-1901.jpg')} style={{width:364,height:470,objectFit:'cover',display:'block',filter:'sepia(.45) contrast(1.08)'}}/>
   <div style={{fontFamily:latin,fontSize:30,color:'#2b2418',marginTop:14}}>Augustin-Louis Cauchy</div>
   <div style={{fontFamily:serif,fontSize:24,color:'#6b5a3a',marginTop:4}}>柯西 · 1789 – 1857</div>
   <div style={{position:'absolute',right:-26,top:400,width:112,height:112,borderRadius:'50%',border:'5px solid #b1352a',color:'#b1352a',display:'flex',alignItems:'center',justifyContent:'center',fontFamily:latin,fontWeight:700,fontSize:30,transform:`rotate(-14deg) scale(${mix(2.2,1,r(f,G.cauchy+8,G.cauchy+16))})`,opacity:r(f,G.cauchy+8,G.cauchy+12)}}>1847</div>
  </div>
  <div style={{position:'absolute',left:80,right:80,top:mix(1270,1200,q),opacity:q,textAlign:'center'}}>
   <div style={{fontFamily:latin,fontStyle:'italic',fontSize:34,color:goldHi,lineHeight:1.45}}>« il suffira de faire <span style={{color:'#fff',textShadow:`0 0 ${hl*24}px ${gold}`}}>décroître</span> indéfiniment la fonction u »</div>
   <div style={{fontFamily:serif,fontSize:46,color:'#f4ead2',marginTop:18,letterSpacing:3}}>只需让函数 u <span style={{color:goldHi,fontSize:mix(46,60,hl),textShadow:`0 0 ${hl*30}px ${gold}`}}>不断变小</span></div>
   <div style={{fontSize:24,color:'#9c8a64',marginTop:16}}>Cauchy, Comptes rendus 25 (1847), p. 536</div>
  </div>
 </AbsoluteFill>;
};
// ---------------- End: back to data ----------------
const EndScene=()=>{
 const f=useCurrentFrame()+S.end;
 const up=r(f,S.end,S.end+14,Easing.inOut(Easing.cubic)),walk=r(f,G.walk,G.fit,Easing.inOut(Easing.quad)),glow=r(f,G.fit,G.fit+12),card=r(f,G.fit+14,G.fit+28);
 const p=at(paths.normal,walk*9);
 return <AbsoluteFill style={{background:paper,transform:`translateY(${(1-up)*1920}px)`,fontFamily:sans,color:'#2f3029'}}>
  <AbsoluteFill style={{backgroundImage:'radial-gradient(#98826118 .8px,transparent .8px)',backgroundSize:'7px 7px'}}/>
  <div style={{position:'absolute',left:60,top:120,fontFamily:serif,fontSize:54}}>同一批数据，<span style={{color:'#1f6b57'}}>误差更小</span></div>
  <div style={{position:'absolute',left:62,top:200,fontSize:28,color:'#8a7c60',fontFamily:latin}}>η = 0.35 · 第 {Math.min(9,Math.floor(walk*9+1e-6))}/9 步</div>
  <div style={{position:'absolute',left:60,top:330,boxShadow:'0 24px 70px #5a4a2a26',borderRadius:12}}><DataChart p={p} w={960} h={760} residual={1-glow*.6} glow={glow}/></div>
  <div style={{position:'absolute',left:0,right:0,top:1200,textAlign:'center',opacity:card}}><div style={{fontFamily:serif,fontSize:76,letterSpacing:8,color:'#2f3029'}}>梯度下降</div><div style={{fontFamily:latin,fontSize:30,letterSpacing:6,color:'#c9962e'}}>GRADIENT DESCENT</div></div>
 </AbsoluteFill>;
};
const sfx=[
 {f:G.much,a:'sync-sweep.wav',v:.5},{f:G.downhill,a:'sync-tap.wav',v:.45},{f:G.shan,a:'sync-arrow.wav',v:.5},{f:G.but,a:'sync-sweep.wav',v:.35},{f:G.where,a:'sync-tap.wav',v:.4},
 {f:G.data,a:'sync-paper.wav',v:.45},{f:G.line,a:'sync-arrow.wav',v:.4},{f:G.map,a:'sync-paper.wav',v:.45},{f:G.eachPoint,a:'sync-tap.wav',v:.45},{f:G.lift,a:'sync-sweep.wav',v:.45},
 {f:G.alongA,a:'sync-arrow.wav',v:.45},{f:G.alongB,a:'sync-arrow.wav',v:.45},{f:G.combine,a:'sync-arrow.wav',v:.5},{f:G.negGrad,a:'sync-paper.wav',v:.45},
 {f:G.idea,a:'sync-sweep.wav',v:.35},{f:G.cauchy,a:'sync-paper.wav',v:.5},{f:G.bianxiao,a:'sync-tap.wav',v:.4},
 ...chalkSfx.filter(s=>s.frame>=0).map(s=>({f:s.frame+S.chalk,a:s.audio,v:s.volume})),
 {f:G.walk,a:'sync-sweep.wav',v:.35},{f:G.fit,a:'sync-tap.wav',v:.5},
];
const darkAt=(f:number)=>f<S.data-8||(f>=S.cauchy&&f<S.end);
export const GradientV3Full=()=>{
 const f=useCurrentFrame();
 const chalkWipe=r(f,S.chalk,S.chalk+12,Easing.inOut(Easing.cubic));
 const dark=darkAt(f);
 return <AbsoluteFill style={{background:ink}}>
  <Sequence durationInFrames={S.data}><Hook/></Sequence>
  <Sequence from={S.data} durationInFrames={S.teach-S.data}><DataScene/></Sequence>
  <Sequence from={S.teach} durationInFrames={S.cauchy-S.teach}><Teach/></Sequence>
  <Sequence from={S.cauchy} durationInFrames={S.chalk-S.cauchy+12}><CauchyScene/></Sequence>
  <Sequence from={S.chalk} durationInFrames={S.end-S.chalk+14}><AbsoluteFill style={{clipPath:`inset(0 0 0 ${(1-chalkWipe)*100}%)`}}><Chalk/></AbsoluteFill></Sequence>
  <Sequence from={S.end}><EndScene/></Sequence>
  {f>=S.cauchy-3&&f<S.cauchy+5&&<AbsoluteFill style={{background:goldHi,opacity:1-Math.abs(f-S.cauchy)/5}}/>}
  <Caption al={al} f={f} color={dark?'#fff6df':'#2f3029'} dim={dark?'#6d6250':'#b9ad94'} font={serif} top={1690} size={40}/>
  <Audio src={staticFile(al.audio)} volume={.95}/>
  {sfx.map((s,i)=><Sequence key={i} from={s.f}><Audio src={staticFile(s.a)} volume={s.v}/></Sequence>)}
 </AbsoluteFill>;
};
