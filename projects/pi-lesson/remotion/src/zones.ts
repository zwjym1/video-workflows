// Fixed layout zones (1920x1080). Every element lives in exactly one zone.
export type Box=[number,number,number,number]; // x,y,w,h
export const ZONES={
 tag:[20,20,440,84] as Box,
 title:[480,24,740,180] as Box,
 think:[1240,16,664,216] as Box,
 stage:[60,240,1040,640] as Box,
 side:[1160,240,700,640] as Box,
 wide:[60,240,1800,640] as Box,   // only when stage+side are both empty
 sub:[0,890,1920,190] as Box,     // subtitles only
};
export type Zone=keyof typeof ZONES;
export type El={id:string;g:string;zone:Zone;box:Box;a:number;draw:()=>React.ReactNode};
export const clamp=(x:number,a=0,b=1)=>Math.max(a,Math.min(b,x));
export const lerp=(a:number,b:number,p:number)=>a+(b-a)*p;
export const ease=(x:number)=>{x=clamp(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;};
export const prog=(t:number,a:number,d=.5)=>ease((t-a)/d);
export const back=(t:number,a:number,d=.45)=>{const x=clamp((t-a)/d);if(x<=0)return 0;const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2);};
/** visible window: fades in over fi after t0; fully gone by t1 (fade-out ends at t1). */
export const vis=(t:number,t0:number,t1:number,fi=.35,fo=.35)=>{if(t<t0||t>=t1)return 0;return Math.min(clamp((t-t0)/fi),clamp((t1-t)/fo));};
export const lerpBox=(a:Box,b:Box,p:number):Box=>[lerp(a[0],b[0],p),lerp(a[1],b[1],p),lerp(a[2],b[2],p),lerp(a[3],b[3],p)];
export const circleBox=(cx:number,cy:number,r:number):Box=>[cx-r,cy-r,2*r,2*r];
export const inside=(b:Box,z:Box)=>b[0]>=z[0]-.5&&b[1]>=z[1]-.5&&b[0]+b[2]<=z[0]+z[2]+.5&&b[1]+b[3]<=z[1]+z[3]+.5;
export const hit=(a:Box,b:Box)=>a[0]<b[0]+b[2]-.5&&b[0]<a[0]+a[2]-.5&&a[1]<b[1]+b[3]-.5&&b[1]<a[1]+a[3]-.5;
export const lerpColor=(a:string,b:string,p:number)=>{p=clamp(p);const h=(s:string)=>[1,3,5].map(k=>parseInt(s.slice(k,k+2),16));const A=h(a),B=h(b);return '#'+A.map((v,k)=>Math.round(v+(B[k]-v)*p).toString(16).padStart(2,'0')).join('');};
