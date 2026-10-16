import React,{useMemo} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as T from 'three';
import {Param,loss,HEIGHT} from '../gradient-story/model';
// World mapping: x = a-offset, y = height, z = -(b-offset) so +b points up in top view.
export const W=(p:Param,h=0):[number,number,number]=>[p[0],h,-p[1]];
export const surfH=(p:Param,rise:number)=>HEIGHT*loss(p)*rise;
export const A_RANGE:[number,number]=[-1.8,2.3],B_RANGE:[number,number]=[-1.6,2.0];
export type View={position:[number,number,number];target:[number,number,number];up:[number,number,number];zoom:number};
export const VW=1080,VH=1340,TOP=250;
const makeCam=(v:View)=>{const c=new T.OrthographicCamera(-VW/2,VW/2,VH/2,-VH/2,.1,200);c.zoom=v.zoom;c.position.set(...v.position);c.up.set(...v.up).normalize();c.lookAt(...v.target);c.updateProjectionMatrix();c.updateMatrixWorld();return c;};
export const project=(pt:[number,number,number],v:View):[number,number]=>{const p=new T.Vector3(...pt).project(makeCam(v));return[(p.x+1)*VW/2,TOP+(1-p.y)*VH/2];};
const Camera:React.FC<{view:View}>=({view})=>{const{camera}=useThree();const c=camera as T.OrthographicCamera;c.left=-VW/2;c.right=VW/2;c.top=VH/2;c.bottom=-VH/2;c.near=.1;c.far=200;c.zoom=view.zoom;c.position.set(...view.position);c.up.set(...view.up).normalize();c.lookAt(...view.target);c.updateProjectionMatrix();c.updateMatrixWorld();return null;};
type V3=[number,number,number];
export const Tube:React.FC<{points:V3[];color:string;radius?:number;opacity?:number}>=({points,color,radius=.012,opacity=1})=>{const curve=useMemo(()=>new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p)),false,'centripetal'),[JSON.stringify(points)]);if(opacity<.01)return null;return <mesh><tubeGeometry args={[curve,Math.max(8,points.length*2),radius,6,false]}/><meshBasicMaterial color={color} transparent opacity={opacity} depthWrite={opacity>.99}/></mesh>;};
// Straight flat arrow in the horizontal plane at height h.
export const FlatArrow:React.FC<{from:Param;to:Param;h:number;color:string;t:number;opacity?:number;width?:number}>=({from,to,h,color,t,opacity=1,width=.03})=>{if(t<.01||opacity<.01)return null;const dx=to[0]-from[0],dy=to[1]-from[1],len=Math.hypot(dx,dy)*t,ang=Math.atan2(dy,dx);const head=Math.min(.13,len*.5),body=Math.max(0,len-head);const dir=new T.Vector3(dx,0,-dy).normalize();const q=new T.Quaternion().setFromUnitVectors(new T.Vector3(0,1,0),dir);const start=new T.Vector3(...W(from,h));const mid=start.clone().add(dir.clone().multiplyScalar(body/2)),tip=start.clone().add(dir.clone().multiplyScalar(body+head/2));void ang;return <><mesh position={mid} quaternion={q}><cylinderGeometry args={[width,width,body,12]}/><meshBasicMaterial color={color} transparent opacity={opacity}/></mesh><mesh position={tip} quaternion={q}><coneGeometry args={[width*2.8,head,16]}/><meshBasicMaterial color={color} transparent opacity={opacity}/></mesh></>;};
const Surface:React.FC<{rise:number;opacity:number}>=({rise,opacity})=>{const geo=useMemo(()=>{const w=A_RANGE[1]-A_RANGE[0],d=B_RANGE[1]-B_RANGE[0];const g=new T.PlaneGeometry(w,d,40,36);g.rotateX(-Math.PI/2);g.translate((A_RANGE[0]+A_RANGE[1])/2,0,-(B_RANGE[0]+B_RANGE[1])/2);const a=g.attributes.position;for(let i=0;i<a.count;i++)a.setY(i,surfH([a.getX(i),-a.getZ(i)],rise));g.computeVertexNormals();return g;},[rise]);if(rise<.005||opacity<.01)return null;return <><mesh geometry={geo}><meshStandardMaterial color="#c8d2bd" roughness={1} transparent opacity={.88*opacity} depthWrite={false} side={T.DoubleSide}/></mesh><mesh geometry={geo}><meshBasicMaterial color="#7f8f78" wireframe transparent opacity={.16*opacity} depthWrite={false}/></mesh></>;};
const Board:React.FC<{alpha:number;grid:number;contours:number}>=({alpha,grid,contours})=>{
 const lines=useMemo(()=>{const pts:number[]=[];for(const a of [-1,0,1,2,3]){const x=a-.8;pts.push(x,0.001,-B_RANGE[0],x,.001,-B_RANGE[1]);}for(const b of [-1,0,1,2]){const z=-(b-.5);pts.push(A_RANGE[0],.001,z,A_RANGE[1],.001,z);}const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(pts,3));return g;},[]);
 const rings=useMemo(()=>[.25,.6,1.2,2.16].map(c=>{const r:V3[]=[];for(let i=0;i<=72;i++){const th=i/72*Math.PI*2;r.push(W([Math.sqrt(2*c)*Math.cos(th),Math.sqrt(c)*Math.sin(th)],.004));}return{c,r};}),[]);
 const w=A_RANGE[1]-A_RANGE[0],d=B_RANGE[1]-B_RANGE[0];
 return <group>
  <mesh rotation={[-Math.PI/2,0,0]} position={[(A_RANGE[0]+A_RANGE[1])/2,-.01,-(B_RANGE[0]+B_RANGE[1])/2]}><planeGeometry args={[w,d]}/><meshBasicMaterial color="#f7f1e2" toneMapped={false} transparent opacity={alpha}/></mesh>
  <lineSegments geometry={lines}><lineBasicMaterial color="#cfc2a6" transparent opacity={grid*alpha}/></lineSegments>
  {rings.map(({c,r})=><Tube key={c} points={r} color={c===2.16?'#b89762':'#c9bc9c'} radius={c===2.16?.008:.006} opacity={contours*alpha}/>)}
 </group>;};
export const World:React.FC<{view:View;board:number;grid:number;contours:number;axes:number;rise:number;surfaceOpacity:number;children?:React.ReactNode}>=({view,board,grid,contours,axes,rise,surfaceOpacity,children})=>
 <div style={{position:'absolute',left:0,top:TOP,width:VW,height:VH}}><ThreeCanvas orthographic width={VW} height={VH} camera={{position:view.position,zoom:view.zoom,near:.1,far:200}} gl={{antialias:true,alpha:true}}><Camera view={view}/><ambientLight intensity={1.6}/><directionalLight position={[4,9,5]} intensity={2.2}/><directionalLight position={[-4,5,-3]} intensity={.6}/>
  <Board alpha={board} grid={grid} contours={contours}/>
  <Tube points={[[A_RANGE[0],.01,-B_RANGE[0]],[A_RANGE[0]+(A_RANGE[1]-A_RANGE[0]+.15)*axes,.01,-B_RANGE[0]]]} color="#a34632" radius={.014} opacity={axes>.01?1:0}/>
  <Tube points={[[A_RANGE[0],.01,-B_RANGE[0]],[A_RANGE[0],.01,-B_RANGE[0]-(B_RANGE[1]-B_RANGE[0]+.15)*axes]]} color="#245f51" radius={.014} opacity={axes>.01?1:0}/>
  <Surface rise={rise} opacity={surfaceOpacity}/>
  {children}
 </ThreeCanvas></div>;
