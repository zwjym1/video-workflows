import React from 'react';
import {AbsoluteFill,interpolate,Easing,useCurrentFrame} from 'remotion';
import {Param,loss,gradient,update,initial} from '../gradient-story/model';
import {World,View,project,W,surfH,FlatArrow,Tube,A_RANGE,B_RANGE} from '../gradient-view-2/scene';
import {TEACH_T as T} from './events';
import {MiniChart} from './chart';
const c={paper:'#f4efe4',ink:'#2f3029',green:'#1f6b57',red:'#e0662f',gold:'#c9962e',amber:'#e8a317'};
const font='"Microsoft YaHei","Noto Sans CJK SC",sans-serif',serif='"SimSun","Noto Serif CJK SC","Microsoft YaHei",serif';
const ease=Easing.bezier(.2,.8,.2,1);
const r=(f:number,[a,b]:readonly [number,number])=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:ease});
const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
const mix3=(a:number[],b:number[],t:number)=>a.map((v,i)=>mix(v,b[i],t)) as [number,number,number];
const ETA=.35,p0:Param=initial,g0=gradient(p0),p1=update(p0,ETA);
const compA:Param=[p0[0]-ETA*g0[0],p0[1]],compB:Param=[p0[0],p0[1]-ETA*g0[1]];
const actual=(p:Param)=>[p[0]+.8,p[1]+.5];
const lerpView=(a:View,b:View,t:number):View=>({position:mix3(a.position,b.position,t),target:mix3(a.target,b.target,t),up:mix3(a.up,b.up,t),zoom:Math.exp(mix(Math.log(a.zoom),Math.log(b.zoom),t))});
const above=(t:[number,number,number],zoom:number):View=>({position:[t[0],t[1]+30,t[2]],target:t,up:[0,0,-1],zoom});
const vTop=above([.4,0,-.2],228);
const vObl:View={position:[.55+9,1.0+11,-.2+16],target:[.55,1.0,-.2],up:[0,1,0],zoom:150};
const vLocal=above([1.0,0,-.78],560);
const vSide:View={position:[1.0+3,.75+5,-.8+30],target:[1.0,.75,-.8],up:[0,1,0],zoom:400};
const Label:React.FC<{at:[number,number];dx?:number;dy?:number;color:string;size?:number;opacity?:number;anchor?:'l'|'c'|'r';bg?:boolean;children:React.ReactNode}>=({at,dx=0,dy=0,color,size=28,opacity=1,anchor='l',bg=true,children})=>opacity<.01?null:<div style={{position:'absolute',left:at[0]+dx,top:at[1]+dy,transform:`translate(${anchor==='l'?0:anchor==='c'?-50:-100}%,-50%)`,fontSize:size,color,opacity,whiteSpace:'nowrap',background:bg?'#fcf8edea':'none',padding:bg?'6px 12px':0,borderRadius:6,lineHeight:1.25}}>{children}</div>;
export const Teach=()=>{
 const f=useCurrentFrame();
 const planeIn=r(f,T.planeIn),axes=r(f,T.axes),tgt=r(f,T.target),pt=r(f,T.point),guides=r(f,T.guides);
 const tilt=r(f,T.tilt),rise=r(f,T.rise),proj=r(f,T.proj),labels=r(f,T.labels),bar=r(f,T.bar);
 const local=f>=T.cut;
 const a1=r(f,T.compA),b1=r(f,T.compB),para=r(f,T.para),res=r(f,T.result),fadeC=r(f,T.fadeComp);
 const move=r(f,T.move),side=r(f,T.side),delta=r(f,T.delta);
 const view=!local?lerpView(vTop,vObl,tilt):vLocal;void vSide;
 const P:Param=[mix(p0[0],p1[0],move),mix(p0[1],p1[1],move)];
 const ballR=20/view.zoom,hBall=surfH(P,rise),h0=surfH(p0,rise);
 const arrowH=h0+.03,aw=6/view.zoom;
 const S=(p:Param,h=0)=>project(W(p,h),view);
 const pBall=S(P,hBall+ballR),pBase=S(P,0),pTarget=S([0,0],0);
 const ghost=move>.02;
 const err=bar*loss(P);
 const shot4b=side>.5;
 const shot=f<T.tilt[0]?1:!local?2:f<T.move[0]?3:4;
 const title=['','先看底板：一个点 = 一组参数','抬起来：高度 = 误差','俯视局部：往哪走？','走一步，误差变小'][shot];
 const title2=shot4b?'侧面截线：同一步，高度降了':title;
 const caption=['','横向调斜率 a，纵向调截距 b','位置不变，只是多看了一个维度：高度','两个方向各走一段，合起来就是负梯度','η = 0.35：沿负梯度挪一步，高度条变短'][shot];
 const caption2=shot4b?'横轴：沿更新方向的位置　纵轴：误差（与右侧刻度同尺）':caption;
 const axisOn=!local?1-tilt*.35:0;
 const dimAround=local?1-move:0;
 // bar geometry (fixed reference scale, 1 unit = 280px)
 const BX=968,B0=1520,BS=280;
 return <AbsoluteFill style={{background:c.paper,fontFamily:font,color:c.ink,overflow:'hidden'}}>
  <AbsoluteFill style={{backgroundImage:'radial-gradient(#98826113 .8px,transparent .8px)',backgroundSize:'7px 7px'}}/>
  <div style={{position:'absolute',inset:0,opacity:1-side*.88}}><World view={view} board={planeIn*(local?.75:1)} grid={local?.5:1} contours={local?.9:tilt*.0+(local?0:.0)} axes={local?0:axes} rise={rise} surfaceOpacity={local?mix(.16,.1,side):mix(1,.62,labels)}>
   {/* target */}
   {tgt>.01&&<mesh position={W([0,0],.012)} scale={tgt}><cylinderGeometry args={[14/view.zoom,14/view.zoom,.01,32]}/><meshBasicMaterial color={c.green} transparent opacity={.9}/></mesh>}
   {/* base marker + projection line */}
   {rise>.01&&<mesh position={W(P,.012)}><cylinderGeometry args={[12/view.zoom,12/view.zoom,.01,32]}/><meshBasicMaterial color={c.gold}/></mesh>}
   {proj>.01&&<Tube points={[W(P,0),W(P,hBall*proj)]} color={c.gold} radius={3/view.zoom}/>}
   {ghost&&<><mesh position={W(p0,h0+ballR)}><sphereGeometry args={[ballR,24,18]}/><meshStandardMaterial color={c.green} transparent opacity={.3} depthWrite={false}/></mesh><Tube points={[W(p0,0),W(p0,h0)]} color={c.gold} radius={2.5/view.zoom} opacity={.45}/></>}
   {/* components & resultant (flat, straight, in a horizontal plane) */}
   <FlatArrow from={p0} to={compA} h={arrowH} color={c.red} t={a1} opacity={(1-fadeC*.7)*(1-move)} width={aw}/>
   <FlatArrow from={p0} to={compB} h={arrowH} color={c.green} t={b1} opacity={(1-fadeC*.7)*(1-move)} width={aw}/>
   {para>.01&&<><Tube points={[W(compA,arrowH),W(p1,arrowH)]} color="#a89470" radius={2.2/view.zoom} opacity={para*(1-fadeC*.6)*(1-move)}/><Tube points={[W(compB,arrowH),W(p1,arrowH)]} color="#a89470" radius={2.2/view.zoom} opacity={para*(1-fadeC*.6)*(1-move)}/></>}
   <FlatArrow from={p0} to={p1} h={arrowH} color={c.amber} t={res} opacity={1-side} width={aw*1.25}/>
   {/* the single point (same identity throughout) */}
   {pt>.01&&<mesh position={W(P,hBall+ballR)} scale={Math.min(1.25,pt*1.25)-Math.max(0,pt-.8)*1.25}><sphereGeometry args={[ballR,32,24]}/><meshStandardMaterial color={c.green} roughness={.35}/></mesh>}
  </World></div>
  {/* dashed parallelogram drawn in screen space for crisp dashes */}
  <svg width="1080" height="1920" style={{position:'absolute',inset:0,pointerEvents:'none'}}>
   {guides>.01&&!local&&(()=>{const pa=S([P[0],B_RANGE[0]]),pb=S([A_RANGE[0],P[1]]),m=S(P,hBall*0);return <g opacity={guides*axisOn} strokeDasharray="7 8" strokeWidth="2.5" fill="none"><path d={`M${m[0]} ${m[1]}L${mix(m[0],pa[0],guides)} ${mix(m[1],pa[1],guides)}`} stroke={c.red}/><path d={`M${m[0]} ${m[1]}L${mix(m[0],pb[0],guides)} ${mix(m[1],pb[1],guides)}`} stroke={c.green}/></g>;})()}
   {para>.01&&(()=>{const A=S(compA,arrowH),B=S(compB,arrowH),C=S(p1,arrowH);return <path d={`M${A[0]} ${A[1]}L${C[0]} ${C[1]}L${B[0]} ${B[1]}`} fill="none" stroke="#7d6a48" strokeWidth="3" strokeDasharray="10 9" opacity={para*(1-fadeC*.6)*(1-move)}/>;})()}
  </svg>
  {dimAround>.01&&<AbsoluteFill style={{pointerEvents:'none',background:'radial-gradient(ellipse 520px 640px at 46% 50%,transparent 60%,#eee6d2cc 100%)',opacity:dimAround}}/>}
  {/* axis ticks & labels */}
  {axisOn>.01&&axes>.01&&<>
   {[-1,0,1,2,3].map(a=><Label key={'a'+a} at={S([a-.8,B_RANGE[0]])} dy={30} anchor="c" color="#8a7c60" size={22} bg={false} opacity={axes*axisOn}>{a}</Label>)}
   {[-1,0,1,2].map(b=><Label key={'b'+b} at={S([A_RANGE[0],b-.5])} dx={-16} anchor="r" color="#8a7c60" size={22} bg={false} opacity={axes*axisOn}>{b}</Label>)}
   <Label at={S([A_RANGE[1],B_RANGE[0]])} dy={74} anchor="r" color={c.red} size={34} opacity={axes*axisOn}>斜率 a →</Label>
   <Label at={S([A_RANGE[0],B_RANGE[1]])} dy={-40} dx={-30} color={c.green} size={34} opacity={axes*axisOn}>↑ 截距 b</Label>
  </>}
  {!local&&<Label at={pTarget} dx={26} dy={34} color={c.green} size={25} opacity={tgt*(1-tilt)}>目标 a=0.8, b=0.5</Label>}
  {!local&&<Label at={pBase} dx={30} dy={-44} color={c.ink} size={27} opacity={guides*(1-tilt)}>当前 a=<b style={{color:c.red}}>2.0</b>, b=<b style={{color:c.green}}>1.7</b></Label>}
  {!local&&<><Label at={pBase} dx={24} dy={40} color={c.gold} size={30} opacity={labels}>位置 = 参数</Label><Label at={S(P,hBall*.55)} dx={-26} anchor="r" color={c.gold} size={30} opacity={labels}>高度 = 误差</Label></>}
  {/* local view labels */}
  {local&&<>
   <Label at={S(compA,arrowH)} dx={-22} dy={-46} anchor="r" color={c.red} size={30} opacity={a1*(1-fadeC*.7)*(1-move)}>−∂L/∂a</Label>
   <Label at={S(compB,arrowH)} dx={24} dy={10} color={c.green} size={30} opacity={b1*(1-fadeC*.7)*(1-move)}>−∂L/∂b</Label>
   <Label at={S(p1,arrowH)} dx={-26} dy={34} anchor="r" color={c.amber} size={32} opacity={res*(1-move)}>−梯度（合成）</Label>
   
   <Label at={pBall} dx={36} dy={10} color={c.ink} size={26} opacity={move*(1-side)}>新位置 a=1.58, b=0.86</Label>
   
   
  </>}
  {/* fixed height reference bar */}
  {bar>.01&&<div style={{position:'absolute',left:0,top:0,opacity:Math.min(1,bar*3)*(shot===3?.4:1)}}>
   <svg width="1080" height="1920" style={{position:'absolute',left:0,top:0}}>
    <rect x={BX-34} y={B0-3*BS-60} width={88} height={3*BS+100} rx={10} fill="#fcf8edee"/>
    {[0,1,2,3].map(v=><g key={v}><path d={`M${BX-14} ${B0-v*BS}H${BX+38}`} stroke="#c7b998" strokeWidth="2"/><text x={BX-20} y={B0-v*BS+7} textAnchor="end" fontSize="20" fill="#8a7c60">{v}</text></g>)}
    <rect x={BX} y={B0-err*BS} width={26} height={err*BS} fill={c.gold}/>
    {ghost&&<><path d={`M${BX-8} ${B0-2.16*BS}H${BX+44}`} stroke={c.red} strokeWidth="3" strokeDasharray="6 5"/><text x={BX+13} y={B0-2.16*BS-12} textAnchor="middle" fontSize="22" fill={c.red}>2.160</text></>}
   </svg>
   <div style={{position:'absolute',left:BX+13,top:B0-3*BS-100,transform:'translateX(-50%)',fontSize:24,color:c.gold,whiteSpace:'nowrap'}}>误差（高度）</div>
   <div style={{position:'absolute',left:BX+50,top:B0-err*BS,transform:'translate(-100%,-150%)',fontSize:26,color:c.ink,background:'#fcf8edee',padding:'2px 8px',whiteSpace:'nowrap',fontVariantNumeric:'tabular-nums'}}>{err.toFixed(3)}</div>
  </div>}
  {local&&<div style={{position:'absolute',left:500,top:150,fontSize:32,opacity:a1*(1-move),color:c.ink,background:'#fffaf0ee',padding:'12px 18px',borderRadius:10,boxShadow:'0 8px 24px #5a4a2a22',fontFamily:'"Noto Serif",serif'}}>∇L = [p₀, 2p₁] = [1.2, 2.4]<br/>η = 0.35</div>}
  {side>.01&&<Section t={side} slide={r(f,[296,316])} BX={BX} B0={B0} BS={BS}/>}
  {delta>.01&&<div style={{position:'absolute',left:75,top:1625,fontSize:34,opacity:delta,transform:`translateY(${(1-delta)*20}px)`}}>误差 <span style={{color:c.gold}}>2.160</span> → <span style={{color:c.green,fontWeight:700}}>{loss(p1).toFixed(3)}</span></div>}
  <div style={{position:'absolute',left:60,top:110,opacity:1}}><MiniChart p={P} w={400} h={300}/></div>
 </AbsoluteFill>;
};

// True side cross-section: error along the update direction, same vertical scale as the bar.
const Section:React.FC<{t:number;slide:number;BX:number;B0:number;BS:number}>=({t,slide,BX,B0,BS})=>{
 const s0=-.25,s1=1.35,X0=110,X1=840,sx=(s:number)=>X0+(s-s0)/(s1-s0)*(X1-X0),sy=(v:number)=>B0-v*BS;
 const L=(s:number)=>loss([p0[0]+s*(p1[0]-p0[0]),p0[1]+s*(p1[1]-p0[1])]);
 let d='';for(let i=0;i<=80;i++){const s=s0+(s1-s0)*i/80;d+=(i?'L':'M')+sx(s).toFixed(1)+' '+sy(L(s)).toFixed(1);}
 const sb=slide,lb=L(sb),l0=L(0),l1=L(1);
 return <svg width="1080" height="1920" style={{position:'absolute',inset:0,opacity:t,pointerEvents:'none'}}>
  <rect x={X0-40} y={sy(3)-40} width={X1-X0+80} height={3*BS+110} rx={12} fill="#fcf8edf2"/>
  {[0,1,2,3].map(v=><path key={v} d={`M${X0} ${sy(v)}H${BX-20}`} stroke="#e2d8c2" strokeWidth="1.5"/>)}
  <path d={`M${X0} ${B0}H${X1}`} stroke="#b5a88b" strokeWidth="2"/>
  <path d={d} fill="none" stroke="#8a9984" strokeWidth="5" strokeDasharray={`${t*2400} 2400`}/>
  <path d={`M${sx(0)} ${B0}V${sy(l0)}`} stroke={c.gold} strokeWidth="3" opacity=".55"/>
  <path d={`M${sx(sb)} ${B0}V${sy(lb)}`} stroke={c.gold} strokeWidth="4"/>
  <path d={`M${sx(0)} ${sy(l0)}H${BX-6}`} stroke={c.red} strokeWidth="2.5" strokeDasharray="7 7"/>
  <path d={`M${sx(sb)} ${sy(lb)}H${BX-6}`} stroke={c.green} strokeWidth="2.5" strokeDasharray="7 7"/>
  <circle cx={sx(0)} cy={sy(l0)} r="16" fill={c.green} opacity=".3"/>
  <circle cx={sx(sb)} cy={sy(lb)} r="17" fill={c.green}/>
  <text x={sx(0)+30} y={sy(l0)-18} textAnchor="start" fontSize="28" fill={c.gold}>更新前 {l0.toFixed(3)}</text>
  <text x={sx(sb)+10} y={sy(lb)-34} textAnchor="middle" fontSize="28" fill={c.green} opacity={Math.min(1,slide*4)}>{slide>.99?`更新后 ${l1.toFixed(3)}`:`误差 ${lb.toFixed(3)}`}</text>
  <text x={sx(0)} y={B0+40} textAnchor="middle" fontSize="22" fill="#8a7c60">起点</text>
  <text x={sx(1)} y={B0+40} textAnchor="middle" fontSize="22" fill="#8a7c60">走一步 (η=0.35)</text>
  <text x={X1} y={B0+40} textAnchor="end" fontSize="22" fill="#8a7c60">→</text>
 </svg>;};
