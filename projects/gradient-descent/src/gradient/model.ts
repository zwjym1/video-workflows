export type Param=[number,number];
// Positive definite quadratic: Hessian [[0.7,0.18],[0.18,1.6]].
export const loss=([x,z]:Param)=>.35*x*x+.8*z*z+.18*x*z;
export const gradient=([x,z]:Param):Param=>[.7*x+.18*z,1.6*z+.18*x];
export const initial:Param=[2.6,1.9];
export const HEIGHT=.32;
export const step=(p:Param,rate:number):Param=>{const g=gradient(p);return[p[0]-rate*g[0],p[1]-rate*g[1]];};
export const path=(rate:number,count:number)=>{const points:Param[]=[initial];for(let i=0;i<count;i++)points.push(step(points[points.length-1],rate));return points;};
export const paths={normal:path(.5,9),small:path(.06,9),large:path(1.32,3)};
export const surface=(p:Param,offset=0):[number,number,number]=>[p[0],HEIGHT*loss(p)+offset,p[1]];
export const pointAt=(points:Param[],phase:number)=>{const n=Math.max(0,Math.min(points.length-1,phase)),i=Math.min(points.length-2,Math.floor(n)),t=n-i;return[points[i][0]+(points[i+1][0]-points[i][0])*t,points[i][1]+(points[i+1][1]-points[i][1])*t] as Param;};
