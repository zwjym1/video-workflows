import React from 'react';
import {staticFile} from 'remotion';
export const P={ink:'#2B2D42',blue:'#3A86FF',orange:'#FF8C42',yel:'#FFD23F',teal:'#2EC4B6',pink:'#FF5D8F',purple:'#8338EC',cream:'#FFF8EC',night:'#13213D',red:'#D7263D',paper:'#F6EEDC'};
export const FONT='"Noto Sans CJK SC","Noto Sans SC","Microsoft YaHei",sans-serif';
export const SERIF='"Noto Serif CJK SC","Noto Serif SC","SimSun",serif';
const tex=(id:string,file:string,size:number)=><pattern id={id} patternUnits="userSpaceOnUse" width={size} height={size}><image href={staticFile('tex/'+file)} width={size} height={size} preserveAspectRatio="xMidYMid slice"/></pattern>;
/** shared materials: photo textures (Poly Haven CC0 etc.), soft shadows, metallic/ceramic/plastic gradients */
export const Defs:React.FC=()=><defs>
 {tex('oak','oak_veneer_01.jpg',1024)}{tex('asphalt','asphalt_01.jpg',512)}{tex('grass','grass_ground.jpg',512)}{tex('track','rubberized_track.jpg',256)}{tex('bamboo','bamboo_veneer.jpg',256)}{tex('paperTex','paper.jpg',1600)}{tex('rope','rope.jpg',64)}
 <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="10" stdDeviation="12" floodColor="#2a1a08" floodOpacity=".32"/></filter>
 <filter id="shadowS" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#2a1a08" floodOpacity=".35"/></filter>
 <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <radialGradient id="tire" cx=".5" cy=".5" r=".5"><stop offset=".78" stopColor="#3a3a3a"/><stop offset=".9" stopColor="#1b1b1b"/><stop offset="1" stopColor="#0d0d0d"/></radialGradient>
 <linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#f4f6f8"/><stop offset=".45" stopColor="#a9b1ba"/><stop offset=".55" stopColor="#d7dce1"/><stop offset="1" stopColor="#7b848e"/></linearGradient>
 <radialGradient id="lid" cx=".38" cy=".32" r=".75"><stop offset="0" stopColor="#8fc1ff"/><stop offset=".55" stopColor="#3a86ff"/><stop offset="1" stopColor="#1d4fa8"/></radialGradient>
 <radialGradient id="lidTop" cx=".4" cy=".35" r=".7"><stop offset="0" stopColor="#d9eaff"/><stop offset="1" stopColor="#7fb2ff"/></radialGradient>
 <radialGradient id="coin" cx=".38" cy=".32" r=".8"><stop offset="0" stopColor="#ffffff"/><stop offset=".4" stopColor="#d4d8dc"/><stop offset=".8" stopColor="#9aa1a8"/><stop offset="1" stopColor="#6f767d"/></radialGradient>
 <radialGradient id="bowl" cx=".5" cy=".5" r=".5"><stop offset=".0" stopColor="#e9eef2"/><stop offset=".75" stopColor="#ffffff"/><stop offset=".88" stopColor="#dfe6ec"/><stop offset="1" stopColor="#b8c4cc"/></radialGradient>
 <linearGradient id="screen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#0f2a4f"/><stop offset="1" stopColor="#061427"/></linearGradient>
 <radialGradient id="vignette" cx=".5" cy=".5" r=".75"><stop offset=".6" stopColor="#000" stopOpacity="0"/><stop offset="1" stopColor="#000" stopOpacity=".38"/></radialGradient>
 <radialGradient id="crust" cx=".45" cy=".4" r=".7"><stop offset="0" stopColor="#ffd38a"/><stop offset=".7" stopColor="#e9a23b"/><stop offset="1" stopColor="#b8742a"/></radialGradient>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#8ec5ff"/><stop offset="1" stopColor="#e8f4ff"/></linearGradient>
 <pattern id="graph" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40,0 L0,0 0,40" fill="none" stroke="#c9dbe8" strokeWidth="1.5"/></pattern>
 <radialGradient id="nightG" cx=".5" cy=".35" r=".9"><stop offset="0" stopColor="#24406e"/><stop offset="1" stopColor="#0a1328"/></radialGradient>
</defs>;
export const Tx:React.FC<{x:number;y:number;s:number;c?:string;w?:number;a?:'start'|'middle'|'end';o?:number;f?:string;stroke?:string;sw?:number;children:React.ReactNode}>=({x,y,s,c=P.ink,w=900,a='middle',o=1,f=FONT,stroke,sw=0,children})=>
 <text x={x} y={y} fontSize={s} fill={c} fontWeight={w} textAnchor={a} opacity={o} fontFamily={f} stroke={stroke} strokeWidth={sw} paintOrder="stroke" dominantBaseline="middle">{children}</text>;
/** paper cut-out card with real paper texture + soft shadow */
export const Card:React.FC<{b:[number,number,number,number];fill?:string;tex?:boolean;r?:number;children?:React.ReactNode}>=({b,fill='#fffdf7',tex=true,r=18,children})=><g>
 <rect x={b[0]+6} y={b[1]+6} width={b[2]-12} height={b[3]-12} rx={r} fill={fill} filter="url(#shadow)"/>
 {tex&&<rect x={b[0]+6} y={b[1]+6} width={b[2]-12} height={b[3]-12} rx={r} fill="url(#paperTex)" opacity={.35}/>}
 {children}</g>;
export const textW=(s:string,size:number)=>[...s].reduce((w,c)=>w+(/[\x00-\xff]/.test(c)?size*.58:size),0);
