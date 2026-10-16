import React from 'react';
import {X,target,predict,loss,Param} from './model';
const green='#245f51',red='#a34632',muted='#9e947e';
const sx=(x:number)=>330+x*222,sy=(y:number)=>530-y*72;
export const Chart:React.FC<{p:Param;residual:number;label?:string}>=({p,residual,label})=><svg width="660" height="690" viewBox="0 0 660 690">
 <rect width="660" height="690" rx="10" fill="#fcf8ed"/>
 <text x="45" y="55" fill="#443f34" fontFamily="Microsoft YaHei" fontSize="25">{label??'让预测，靠近真实数据。'}</text>
 {[-1,-.5,0,.5,1].map(x=><g key={x}><path d={`M${sx(x)} 95V585`} stroke="#e2daca"/><text x={sx(x)} y="617" textAnchor="middle" fill={muted} fontSize="16">{x}</text></g>)}
 {[0,1,2,3,4,5].map(y=><path key={y} d={`M65 ${sy(y)}H595`} stroke="#e2daca"/>)}
 <path d={`M65 ${sy(0)}H600M${sx(0)} 85V587`} stroke="#b5a88b" strokeWidth="1.5"/>
 <defs><clipPath id="regression-plot"><rect x="65" y="95" width="535" height="505"/></clipPath></defs>
 <path d={`M${sx(-1.15)} ${sy(predict(-1.15,p))}L${sx(1.15)} ${sy(predict(1.15,p))}`} stroke={red} strokeWidth="4" clipPath="url(#regression-plot)"/>
 {X.map(x=><g key={x}><path d={`M${sx(x)} ${sy(target(x))}V${sy(predict(x,p))}`} stroke={red} strokeWidth="2" strokeDasharray="5 6" opacity={residual*.7}/><circle cx={sx(x)} cy={sy(target(x))} r="8" fill={green}/><circle cx={sx(x)} cy={sy(predict(x,p))} r="4" fill={red} opacity={residual}/></g>)}
 <circle cx="56" cy="651" r="6" fill={green}/><text x="72" y="657" fontSize="18" fill={green}>真实点</text><path d="M187 651H221" stroke={red} strokeWidth="3"/><text x="233" y="657" fontSize="18" fill={red}>预测</text><text x="603" y="657" textAnchor="end" fontSize="23" fill={red}>误差 {loss(p).toFixed(3)}</text>
</svg>;
export const Knob:React.FC<{value:number;name:string;color:string}>=({value,name,color})=><svg width="200" height="220"><text x="100" y="29" textAnchor="middle" fontSize="25" fill={color} fontFamily="Microsoft YaHei">{name}</text><circle cx="100" cy="109" r="59" fill="#e5dcc5" stroke="#c4b696" strokeWidth="2"/><circle cx="100" cy="109" r="46" fill="#faf5e8"/>{[-120,-60,0,60,120].map(deg=><path key={deg} d="M100 42V49" stroke="#a39476" transform={`rotate(${deg} 100 109)`}/>)}<g transform={`rotate(${value*52-45} 100 109)`}><path d="M100 109V69" stroke={color} strokeWidth="6" strokeLinecap="round"/><circle cx="100" cy="109" r="6" fill={color}/></g><text x="100" y="201" textAnchor="middle" fill={color} fontSize="26">{value.toFixed(2)}</text></svg>;
