import React,{createContext,useContext} from 'react';
import {useCurrentFrame} from 'remotion';
import {FPS,S,sentText,charT,charE,PUN,se,at,CH} from './timing';
export const C={bg:'#FFF8EC',grid:'#EDE4D3',ink:'#2B2D42',blue:'#3A86FF',orange:'#FF8C42',yel:'#FFD23F',teal:'#2EC4B6',pink:'#FF5D8F',paper:'#F4E3C3',paperLine:'#E6D0A6',wood:'#C98B4F',woodDark:'#A86E3A',rod:'#F2D8A7',rodEdge:'#7A4E24',night:'#1B2A4A',purple:'#8338EC',grey:'#8D99AE',light:'#B8B8C8',gap:'#FFD9A8'};
export const FONT='"Noto Sans CJK SC","Noto Sans SC","Microsoft YaHei",sans-serif';
export const SERIF='"Noto Serif CJK SC","Noto Serif SC",serif';
export const OffsetCtx=createContext(0);
export const useT=()=>{const f=useCurrentFrame();const off=useContext(OffsetCtx);return (f+off)/FPS;};
export const clamp=(x:number,a=0,b=1)=>Math.max(a,Math.min(b,x));
export const lerp=(a:number,b:number,p:number)=>a+(b-a)*p;
export const ease=(x:number)=>{x=clamp(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;};
export const prog=(t:number,a:number,d=.5)=>ease((t-a)/d);
export const back=(t:number,a:number,d=.4)=>{const x=clamp((t-a)/d);if(x<=0)return 0;const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2);};
export const mixColor=(a:string,b:string,p:number)=>{const h=(s:string)=>[1,3,5].map(k=>parseInt(s.slice(k,k+2),16));const A=h(a),B=h(b);return '#'+A.map((v,k)=>Math.round(lerp(v,B[k],clamp(p))).toString(16).padStart(2,'0')).join('');};
export const Tx:React.FC<{x:number;y:number;s:number;c?:string;w?:number;a?:'start'|'middle'|'end';o?:number;f?:string;stroke?:string;sw?:number;children:React.ReactNode;ls?:number}>=({x,y,s,c=C.ink,w=900,a='middle',o=1,f=FONT,stroke,sw=0,children,ls})=>
 <text x={x} y={y} fontSize={s} fill={c} fontWeight={w} textAnchor={a} opacity={o} fontFamily={f} stroke={stroke} strokeWidth={sw} paintOrder="stroke" letterSpacing={ls} dominantBaseline="middle">{children}</text>;
export const GridBg:React.FC<{bg?:string;line?:string;o?:number}>=({bg=C.bg,line=C.grid,o=1})=><g opacity={o}><rect width={1920} height={1080} fill={bg}/>{Array.from({length:33},(_,k)=><line key={'v'+k} x1={k*60} y1={0} x2={k*60} y2={1080} stroke={line} strokeWidth={2}/>)}{Array.from({length:19},(_,k)=><line key={'h'+k} x1={0} y1={k*60} x2={1920} y2={k*60} stroke={line} strokeWidth={2}/>)}</g>;
export const poly=(n:number,cx:number,cy:number,r:number,rot=-Math.PI/2)=>Array.from({length:n},(_,k)=>[cx+r*Math.cos(rot+2*Math.PI*k/n),cy+r*Math.sin(rot+2*Math.PI*k/n)] as [number,number]);
export const pts=(p:[number,number][])=>p.map(v=>v[0].toFixed(2)+','+v[1].toFixed(2)).join(' ');
/** polygon with n vertices growing to 2n: odd vertices move from chord midpoint (p=0) to arc (p=1) */
export const morph=(n:number,p:number,cx:number,cy:number,r:number,rot=-Math.PI/2)=>{const out:[number,number][]=[];for(let k=0;k<2*n;k++){const a=rot+Math.PI*k/n;const arc:[number,number]=[cx+r*Math.cos(a),cy+r*Math.sin(a)];if(k%2===0){out.push(arc);continue;}
 const a0=rot+Math.PI*(k-1)/n,a1=rot+Math.PI*(k+1)/n;const m:[number,number]=[cx+r*(Math.cos(a0)+Math.cos(a1))/2,cy+r*(Math.sin(a0)+Math.sin(a1))/2];out.push([lerp(m[0],arc[0],p),lerp(m[1],arc[1],p)]);}return out;};
// ---------- subtitles ----------
const DISPLAY:[string,string][]=[['三点一四一五九二六','3.1415926'],['三点一四一五九二七','3.1415927'],['三点一零五八','3.1058'],['三点一三二六','3.1326'],['三点一三九四','3.1394'],['三点一四一零','3.1410'],['三点一四一五','3.1415'],['三点一四一六','3.1416'],['三点一四','3.14'],['三点一','3.1'],['一百九十二','192'],['九十六','96'],['四十八','48'],['二十四','24'],['十二边形','12边形'],['十二条边','12条边'],['三百一十四万亿','314万亿'],['二零二六','2026'],['一百一十','110'],['一千五百','1500'],['一千七百','1700'],['三月十四日','3月14日'],['一千万年','1000万年']];
export const toDisplay=(s:string)=>{for(const [a,b] of DISPLAY)s=s.split(a).join(b);return s;};
type Phrase={text:string;start:number;end:number};
export const PHRASES:Phrase[]=(()=>{const out:Phrase[]=[];S.forEach((s,i)=>{let cur='';let idx=0;let st=0;const flush=()=>{if(cur){const n=[...cur].length;out.push({text:toDisplay(cur),start:charT[i][st],end:charE[i][st+n-1]});}cur='';};
 for(const ch of [...s.text]){if(PUN.test(ch)){flush();continue;}if(!cur)st=idx;cur+=ch;idx++;}flush();});return out;})();
export const Caption:React.FC<{t:number}>=({t})=>{const i=PHRASES.findIndex((p,j)=>t>=p.start-.06&&t<(j<PHRASES.length-1?Math.min(PHRASES[j+1].start-.06,p.end+.7):p.end+1));if(i<0)return null;const p=PHRASES[i];const a=clamp((t-p.start+.06)/.12);
 return <div style={{position:'absolute',left:0,right:0,top:960,transform:`translateY(-50%) scale(${.9+.1*a})`,textAlign:'center',fontFamily:FONT,fontWeight:900,fontSize:66,letterSpacing:3,whiteSpace:'nowrap',color:'#fff',WebkitTextStroke:`9px ${C.ink}`,paintOrder:'stroke fill',textShadow:'0 6px 16px rgba(0,0,0,.25)',opacity:a}}>{p.text}</div>;};
// ---------- 想一想 card ----------
export const THINK=[11,24,40,42,69,78];
const thinkQ=(i:number)=>S[i].text.replace(/^再?想一想，/,'');
export const Mascot:React.FC<{x:number;y:number;s?:number;bob?:number}>=({x,y,s=1,bob=0})=><g transform={`translate(${x},${y+bob}) scale(${s})`}>
 <path d="M0,-70 C-6,-95 10,-100 4,-118" stroke={C.ink} strokeWidth={6} fill="none" strokeLinecap="round"/><text x={6} y={-122} fontSize={34} fontWeight={900} fill={C.pink} textAnchor="middle" fontFamily={FONT}>π</text>
 <circle r={70} fill={C.yel} stroke={C.ink} strokeWidth={6}/><circle cx={-22} cy={-10} r={8} fill={C.ink}/><circle cx={22} cy={-10} r={8} fill={C.ink}/><path d="M-20,18 Q0,36 20,18" stroke={C.ink} strokeWidth={6} fill="none" strokeLinecap="round"/><circle cx={-42} cy={14} r={9} fill={C.pink} opacity={.5}/><circle cx={42} cy={14} r={9} fill={C.pink} opacity={.5}/></g>;
export const ThinkCard:React.FC<{t:number}>=({t})=>{const i=THINK.find(k=>t>=S[k].start-.1&&t<se(k)+2.25);if(i===undefined)return null;
 const a0=S[i].start,end=se(i)+2.1;const inA=back(t,a0,.45),out=1-prog(t,end,.25);const o=Math.min(clamp((t-a0)/.15),out);const cd=clamp((t-se(i))/2);
 const q=thinkQ(i);const fs=q.length>14?36:42;
 return <svg width={1920} height={1080} style={{position:'absolute',inset:0}}><g opacity={o} transform={`translate(1290,40) scale(${.6+.4*inA})`} style={{transformOrigin:'300px 90px'}}>
  <rect x={0} y={0} width={600} height={180} rx={34} fill={C.orange} stroke={C.ink} strokeWidth={5}/>
  <rect x={24} y={20} width={140} height={50} rx={25} fill="#fff"/><Tx x={94} y={46} s={30} c={C.orange}>想一想</Tx>
  <foreignObject x={24} y={78} width={470} height={96}><div style={{fontFamily:FONT,fontWeight:900,fontSize:fs,color:'#fff',lineHeight:1.18}}>{toDisplay(q)}</div></foreignObject>
  <circle cx={540} cy={56} r={34} fill="#fff" opacity={.35}/>
  <circle cx={540} cy={56} r={34} fill="none" stroke="#fff" strokeWidth={9} strokeDasharray={`${2*Math.PI*34*(1-cd)} 999`} transform="rotate(-90 540 56)" strokeLinecap="round"/>
  <Tx x={540} y={58} s={30} c={C.ink}>{t>=se(i)?Math.max(1,Math.ceil(2-cd*2)).toString():'?'}</Tx>
 </g><g opacity={o}><Mascot x={1220} y={150} s={.75*inA} bob={Math.sin(t*6)*4}/></g></svg>;};
// ---------- chapter tag ----------
const TAGS=['开场','第1章 量一量','第2章 周三径一','第3章 割圆术','第4章 祖冲之','第5章 计算机时代','第6章 π日'];
export const ChapterTag:React.FC<{t:number}>=({t})=>{let c=0;for(let k=0;k<7;k++)if(t>=CH[k])c=k;const a=back(t,CH[c],.4);const w=TAGS[c].length*34+56;
 return <svg width={1920} height={1080} style={{position:'absolute',inset:0}}><g transform={`translate(40,34) scale(${a})`}><rect width={w} height={62} rx={31} fill={C.blue}/><Tx x={w/2} y={33} s={32} c="#fff">{TAGS[c]}</Tx></g></svg>;};
export const tAt=at;
