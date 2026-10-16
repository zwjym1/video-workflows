import React from 'react';
import {staticFile} from 'remotion';
import {P,Tx,FONT,SERIF} from './mat';
import {clamp} from './zones';
export const Wheel:React.FC<{cx:number;cy:number;r:number;rot:number;o?:number}>=({cx,cy,r,rot,o=1})=><g opacity={o} filter="url(#shadowS)">
 <circle cx={cx} cy={cy} r={r} fill="url(#tire)"/>
 {Array.from({length:36},(_,k)=>{const a=(rot+k*10)*Math.PI/180;return <line key={k} x1={cx+(r-3)*Math.cos(a)} y1={cy+(r-3)*Math.sin(a)} x2={cx+(r-13)*Math.cos(a)} y2={cy+(r-13)*Math.sin(a)} stroke="#555" strokeWidth={3}/>;})}
 <circle cx={cx} cy={cy} r={r*.78} fill="none" stroke="url(#rim)" strokeWidth={r*.09}/>
 {Array.from({length:16},(_,k)=>{const a=(rot+k*22.5)*Math.PI/180;return <line key={'s'+k} x1={cx} y1={cy} x2={cx+r*.74*Math.cos(a)} y2={cy+r*.74*Math.sin(a)} stroke="#c9ced3" strokeWidth={2.2}/>;})}
 <circle cx={cx} cy={cy} r={r*.12} fill="url(#rim)" stroke="#6f767d" strokeWidth={2}/>
 {(()=>{const a=rot*Math.PI/180;return <circle cx={cx+r*.6*Math.cos(a)} cy={cy+r*.6*Math.sin(a)} r={r*.07} fill={P.yel} stroke={P.ink} strokeWidth={2}/>;})()}
</g>;
export const Lid:React.FC<{cx:number;cy:number;r:number;o?:number}>=({cx,cy,r,o=1})=><g opacity={o}>
 <circle cx={cx} cy={cy} r={r} fill="url(#lid)" filter="url(#shadow)"/>
 <circle cx={cx} cy={cy} r={r*.84} fill="url(#lidTop)"/>
 <circle cx={cx} cy={cy} r={r*.84} fill="none" stroke="#2c6bd6" strokeWidth={3} opacity={.6}/>
 <ellipse cx={cx-r*.3} cy={cy-r*.38} rx={r*.32} ry={r*.12} fill="#fff" opacity={.35} transform={`rotate(-30 ${cx-r*.3} ${cy-r*.38})`}/>
</g>;
export const Coin:React.FC<{cx:number;cy:number;r:number;o?:number}>=({cx,cy,r,o=1})=><g opacity={o}>
 <circle cx={cx} cy={cy} r={r} fill="url(#coin)" filter="url(#shadowS)"/>
 <circle cx={cx} cy={cy} r={r*.86} fill="none" stroke="#8a9198" strokeWidth={2}/>
 <Tx x={cx} y={cy+2} s={r*.9} c="#7d848b" w={900}>1</Tx>
</g>;
export const Bowl:React.FC<{cx:number;cy:number;r:number;o?:number}>=({cx,cy,r,o=1})=><g opacity={o}>
 <circle cx={cx} cy={cy} r={r} fill="url(#bowl)" filter="url(#shadow)"/>
 <circle cx={cx} cy={cy} r={r*.93} fill="none" stroke="#2f6db5" strokeWidth={r*.04}/>
 <circle cx={cx} cy={cy} r={r*.45} fill="none" stroke="#d7dee4" strokeWidth={3}/>
</g>;
/** rope drawn with a real rope photo texture as the stroke */
export const RopePath:React.FC<{d:string;w?:number;o?:number}>=({d,w=14,o=1})=><g opacity={o}><path d={d} fill="none" stroke="#8b6a3e" strokeWidth={w+2} strokeLinecap="round"/><path d={d} fill="none" stroke="url(#rope)" strokeWidth={w} strokeLinecap="round"/></g>;
export const arcPath=(cx:number,cy:number,r:number,a0:number,a1:number)=>{const p=(a:number)=>[cx+r*Math.cos(a),cy+r*Math.sin(a)];const s=p(a0),e=p(a1);const large=Math.abs(a1-a0)>Math.PI?1:0;return `M${s[0]},${s[1]} A${r},${r} 0 ${large} 1 ${e[0]},${e[1]}`;};
export const Ruler:React.FC<{x:number;y:number;w:number;h:number}>=({x,y,w,h})=><g filter="url(#shadowS)"><rect x={x} y={y} width={w} height={h} rx={6} fill="#e8c27a"/><rect x={x} y={y} width={w} height={h} rx={6} fill="url(#oak)" opacity={.45}/>
 {Array.from({length:Math.floor(w/12)},(_,k)=><line key={k} x1={x+8+k*12} y1={y} x2={x+8+k*12} y2={y+(k%5===0?h*.45:h*.25)} stroke="#5a3d1a" strokeWidth={2}/>)}</g>;
export const Rod:React.FC<{x:number;y:number;len:number;vertical:boolean;o?:number;rot?:number}>=({x,y,len,vertical,o=1,rot=0})=>{const T=12;const w=vertical?T:len,h=vertical?len:T;
 return <g opacity={o} transform={rot?`rotate(${rot} ${x+w/2} ${y+h/2})`:undefined}><rect x={x} y={y} width={w} height={h} rx={T/2} fill="#e9cf98" filter="url(#shadowS)"/><rect x={x} y={y} width={w} height={h} rx={T/2} fill="url(#bamboo)" opacity={.55}/><rect x={x} y={y} width={w} height={h} rx={T/2} fill="none" stroke="#8a6236" strokeWidth={1.5}/></g>;};
/** 算筹 numeral: vertical form for units/hundreds…, horizontal for tens/thousands…; 6–9 use a 5-rod perpendicular on top */
export const RodDigit:React.FC<{d:number;vertical:boolean;cx:number;cy:number;o?:number}>=({d,vertical,cx,cy,o=1})=>{const out:React.ReactNode[]=[];const L=84,G=20;const n=d>5?d-5:d;
 if(vertical){const w=(n-1)*G;const top=d>5?cy-L/2+20:cy-L/2;for(let i=0;i<n;i++)out.push(<Rod key={'v'+i} x={cx-w/2+i*G-6} y={top} len={d>5?L-20:L} vertical/>);if(d>5)out.push(<Rod key="h5" x={cx-L/2+6} y={cy-L/2-6} len={L-12} vertical={false}/>);}
 else{const h=(n-1)*G;const top=d>5?cy-h/2+20:cy-h/2;for(let i=0;i<n;i++)out.push(<Rod key={'h'+i} x={cx-L/2} y={top+i*G-6} len={L} vertical={false}/>);if(d>5)out.push(<Rod key="v5" x={cx-6} y={top-50} len={40} vertical/>);}
 return <g opacity={o}>{out}</g>;};
export const Calculator:React.FC<{x:number;y:number;w:number;h:number}>=({x,y,w,h})=><g filter="url(#shadow)"><rect x={x} y={y} width={w} height={h} rx={18} fill="#3b3f46"/><rect x={x+18} y={y+18} width={w-36} height={h*.22} rx={8} fill="#a9c3a0"/>
 {Array.from({length:12},(_,k)=><rect key={k} x={x+22+(k%3)*((w-44)/3)} y={y+h*.32+Math.floor(k/3)*((h*.62)/4)} width={(w-44)/3-10} height={(h*.62)/4-10} rx={6} fill="#5c626b"/>)}</g>;
export const Monitor:React.FC<{x:number;y:number;w:number;h:number;children?:React.ReactNode}>=({x,y,w,h,children})=><g filter="url(#shadow)"><rect x={x} y={y} width={w} height={h*.82} rx={16} fill="#1f232a"/><rect x={x+16} y={y+16} width={w-32} height={h*.82-32} rx={6} fill="url(#screen)"/>
 <rect x={x+w/2-30} y={y+h*.82} width={60} height={h*.12} fill="#2b2f36"/><rect x={x+w/2-110} y={y+h*.94} width={220} height={h*.06} rx={8} fill="#2b2f36"/>{children}</g>;
export const Seal:React.FC<{x:number;y:number;s:number;text:string;a?:number}>=({x,y,s,text,a=1})=><g transform={`translate(${x},${y}) scale(${a<1?1.4-.4*a:1})`} opacity={clamp(a*2)}>
 <rect x={-s*text.length/2-12} y={-s/2-12} width={s*text.length+24} height={s+24} rx={10} fill={P.red} filter="url(#shadowS)"/>
 <rect x={-s*text.length/2-4} y={-s/2-4} width={s*text.length+8} height={s+8} rx={6} fill="none" stroke="#fff" strokeWidth={3}/>
 <Tx x={0} y={3} s={s*.9} c="#fff" f={SERIF}>{text}</Tx></g>;
export const Portrait:React.FC<{href:string;b:[number,number,number,number];label:string;sub?:string}>=({href,b,label,sub})=>{const [x,y,w,h]=b;const ih=h-(sub?92:60);const id='pc'+Math.round(x)+'_'+Math.round(y);
 return <g filter="url(#shadow)"><rect x={x} y={y} width={w} height={h} rx={14} fill="#fffdf7"/><defs><clipPath id={id}><rect x={x+12} y={y+12} width={w-24} height={ih-12} rx={8}/></clipPath></defs>
  <image href={staticFile(href)} x={x+12} y={y+12} width={w-24} height={ih-12} preserveAspectRatio="xMidYMid slice" clipPath={`url(#${id})`}/>
  <Tx x={x+w/2} y={y+ih+22} s={26} c={P.ink}>{label}</Tx>{sub&&<Tx x={x+w/2} y={y+ih+58} s={20} c="#6b6f80" w={500}>{sub}</Tx>}</g>;};
export const Mascot:React.FC<{x:number;y:number;s?:number;bob?:number}>=({x,y,s=1,bob=0})=><g transform={`translate(${x},${y+bob}) scale(${s})`} filter="url(#shadowS)">
 <path d="M0,-62 C-6,-85 10,-90 4,-104" stroke={P.ink} strokeWidth={6} fill="none" strokeLinecap="round"/><text x={6} y={-112} fontSize={30} fontWeight={900} fill={P.pink} textAnchor="middle" fontFamily={FONT}>π</text>
 <circle r={62} fill={P.yel} stroke={P.ink} strokeWidth={5}/><circle cx={-20} cy={-8} r={7} fill={P.ink}/><circle cx={20} cy={-8} r={7} fill={P.ink}/><path d="M-18,16 Q0,32 18,16" stroke={P.ink} strokeWidth={5} fill="none" strokeLinecap="round"/></g>;
export const Cross:React.FC<{x:number;y:number;s:number;p:number}>=({x,y,s,p})=><g stroke={P.red} strokeWidth={12} strokeLinecap="round"><line x1={x-s} y1={y-s} x2={x-s+2*s*clamp(p*2)} y2={y-s+2*s*clamp(p*2)}/>{p>.5&&<line x1={x+s} y1={y-s} x2={x+s-2*s*clamp(p*2-1)} y2={y-s+2*s*clamp(p*2-1)}/>}</g>;
export const Check:React.FC<{x:number;y:number;s:number;p:number}>=({x,y,s,p})=><path d={`M${x-s},${y} L${x-s*.3},${y+s*.7} L${x+s},${y-s*.8}`} stroke={P.teal} strokeWidth={14} fill="none" strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={`${clamp(p)} 1`}/>;
