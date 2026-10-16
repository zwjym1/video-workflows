export const lerp=(a:number,b:number,p:number)=>a+(b-a)*p;
export const poly=(n:number,cx:number,cy:number,r:number,rot=-Math.PI/2)=>Array.from({length:n},(_,k)=>[cx+r*Math.cos(rot+2*Math.PI*k/n),cy+r*Math.sin(rot+2*Math.PI*k/n)] as [number,number]);
export const pts=(p:[number,number][])=>p.map(v=>v[0].toFixed(2)+','+v[1].toFixed(2)).join(' ');
/** n-gon growing to a 2n-gon: new vertices move from chord midpoint (p=0) onto the arc (p=1) */
export const morph=(n:number,p:number,cx:number,cy:number,r:number,rot=-Math.PI/2)=>{const out:[number,number][]=[];for(let k=0;k<2*n;k++){const a=rot+Math.PI*k/n;const arc:[number,number]=[cx+r*Math.cos(a),cy+r*Math.sin(a)];if(k%2===0){out.push(arc);continue;}
 const a0=rot+Math.PI*(k-1)/n,a1=rot+Math.PI*(k+1)/n;const m:[number,number]=[cx+r*(Math.cos(a0)+Math.cos(a1))/2,cy+r*(Math.sin(a0)+Math.sin(a1))/2];out.push([lerp(m[0],arc[0],p),lerp(m[1],arc[1],p)]);}return out;};
