import React,{useMemo} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {loss,gradient,HEIGHT,Param,surface,pointAt} from '../gradient/model';

export type View={camera:[number,number,number];target:[number,number,number]};
export const cameraFor=(view:View)=>{const c=new THREE.PerspectiveCamera(42,1080/1480,.1,100);c.position.set(...view.camera);c.lookAt(...view.target);c.updateMatrixWorld();return c;};
export const project=(p:[number,number,number],v:View)=>{const q=new THREE.Vector3(...p).project(cameraFor(v));return[(q.x*.5+.5)*1080,(-q.y*.5+.5)*1480+130] as [number,number];};
const Camera:React.FC<{view:View}>=({view})=>{const{camera}=useThree();camera.position.set(...view.camera);camera.lookAt(...view.target);camera.updateMatrixWorld();return null;};

const Curve:React.FC<{points:THREE.Vector3[];color:string;radius?:number}>=({points,color,radius=.027})=>{const curve=useMemo(()=>new THREE.CatmullRomCurve3(points,false,'centripetal'),[points]);return <mesh><tubeGeometry args={[curve,Math.max(20,points.length*3),radius,7,false]}/><meshStandardMaterial color={color} roughness={.8}/></mesh>;};
const Terrain:React.FC<{rise:number;grid:number}>=({rise,grid})=>{const geo=useMemo(()=>{const geometry=new THREE.PlaneGeometry(7.2,7.2,40,40);geometry.rotateX(-Math.PI/2);const a=geometry.attributes.position;for(let i=0;i<a.count;i++)a.setY(i,HEIGHT*loss([a.getX(i),a.getZ(i)])*rise);geometry.computeVertexNormals();return geometry;},[rise]);return <group scale={[grid,1,grid]}><mesh geometry={geo}><meshStandardMaterial color="#b6c8b3" roughness={1} metalness={0} transparent opacity={.88}/></mesh><mesh geometry={geo} position={[0,.012,0]}><meshBasicMaterial color="#758d77" wireframe transparent opacity={.28}/></mesh></group>;};
const Axis:React.FC<{from:[number,number,number];to:[number,number,number];color:string}>=({from,to,color})=>{const a=new THREE.Vector3(...from),b=new THREE.Vector3(...to),dir=b.clone().sub(a).normalize(),quat=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0),dir);return <><Curve points={[a,b]} color={color} radius={.017}/><mesh position={b} quaternion={quat}><coneGeometry args={[.08,.23,12]}/><meshStandardMaterial color={color}/></mesh></>;};

export const Landscape:React.FC<{view:View;points:Param[];phase:number;color:string;arrow:number;rise:number;grid:number;axis:number}>=({view,points,phase,color,arrow,rise,grid,axis})=>{
 const p=pointAt(points,phase),actual=surface(p,.2),grad=gradient(p),next:[number,number]=[p[0]-.45*grad[0],p[1]-.45*grad[1]];actual[1]=(actual[1]-.2)*rise+.2;
 const curvePoints:THREE.Vector3[]=[];
 for(let t=0;t<phase;t+=.06)curvePoints.push(new THREE.Vector3(...surface(pointAt(points,t),.045)));
 curvePoints.push(new THREE.Vector3(...surface(p,.045)));
 const arrowPoints:THREE.Vector3[]=[];for(let t=0;t<=1;t+=.05)arrowPoints.push(new THREE.Vector3(...surface([p[0]+(next[0]-p[0])*t,p[1]+(next[1]-p[1])*t],.1)));
 const last=arrowPoints[arrowPoints.length-1],prev=arrowPoints[arrowPoints.length-2],quat=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0),last.clone().sub(prev).normalize());
 return <div style={{position:'absolute',top:130,left:0,width:1080,height:1480}}><ThreeCanvas width={1080} height={1480} camera={{position:view.camera,fov:42}} gl={{antialias:true,alpha:true}} shadows><Camera view={view}/><ambientLight intensity={1.4}/><directionalLight position={[4,10,5]} intensity={2.3}/><directionalLight position={[-5,3,-4]} intensity={.7} color="#c1d3ce"/>
  <group scale={[grid,1,grid]}><gridHelper args={[8,16,'#b5a88c','#cdc1a7']} position={[0,-.2,0]}/></group>
  <Terrain rise={rise} grid={grid}/><group scale={[axis,1,axis]}><Axis from={[-4.3,-.15,4.3]} to={[4.3,-.15,4.3]} color="#a64531"/><Axis from={[-4.3,-.15,4.3]} to={[-4.3,-.15,-4.3]} color="#34746a"/></group><group scale={[1,Math.max(.001,rise),1]}><Axis from={[-4.3,-.15,4.3]} to={[-4.3,4.5,4.3]} color="#82714e"/></group>
  <Curve points={[new THREE.Vector3(p[0],.03,p[1]),new THREE.Vector3(...actual)]} color="#b8864e" radius={.018}/>
  <mesh position={[p[0],.03,p[1]]}><sphereGeometry args={[.09,16,12]}/><meshStandardMaterial color="#b8864e"/></mesh>
  {curvePoints.length>1&&<Curve points={curvePoints} color={color} radius={.037}/>}
  {rise>.99&&points.slice(0,Math.floor(phase)+1).map((q,i)=><mesh key={i} position={surface(q,.055)}><sphereGeometry args={[.055,12,12]}/><meshStandardMaterial color={color}/></mesh>)}
  <mesh position={actual} castShadow><sphereGeometry args={[.16,32,24]}/><meshStandardMaterial color={color} roughness={.38} metalness={.12}/></mesh>
  {arrow>.01&&<group scale={1}><Curve points={arrowPoints} color="#a64531" radius={.045*arrow}/><mesh position={last} quaternion={quat} scale={arrow}><coneGeometry args={[.14,.34,16]}/><meshStandardMaterial color="#a64531"/></mesh></group>}
 </ThreeCanvas></div>;
};

