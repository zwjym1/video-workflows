import * as THREE from 'three';
import React, {useMemo} from 'react';
import car from './car.json';
export const Arrow: React.FC<{from:[number,number,number]; dir:[number,number,number]; len:number; color:string; r?:number; opacity?:number}> = ({from,dir,len,color,r=0.06,opacity=1}) => {
  const q = useMemo(()=>new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0), new THREE.Vector3(...dir).normalize()),[dir.join()]);
  if (len<=0.01) return null;
  const head = Math.min(r*4, len*0.5);
  return <group position={from} quaternion={q}>
    <mesh position={[0,(len-head)/2,0]}><cylinderGeometry args={[r,r,len-head,16]}/><meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.9} transparent opacity={opacity} toneMapped={false}/></mesh>
    <mesh position={[0,len-head/2,0]}><coneGeometry args={[r*2.6,head,20]}/><meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.9} transparent opacity={opacity} toneMapped={false}/></mesh>
  </group>;
};

const useGeo = () => useMemo(()=>{
  const pos = new THREE.Float32BufferAttribute(car.pos as number[],3);
  const mk = (idx:number[]) => { const g=new THREE.BufferGeometry(); g.setAttribute('position',pos); g.setIndex(idx); g.computeVertexNormals(); return g; };
  const all = mk([...(car.body as number[]),...(car.glass as number[])]);
  return {body:mk(car.body as number[]), glass:mk(car.glass as number[]), all};
},[]);

export const Car2: React.FC<{xray:number; fanSpin:number; showFan:boolean; showThrust:boolean; glow:number; wire?:boolean}> = ({xray,fanSpin,showFan,showThrust,glow,wire}) => {
  const g = useGeo();
  const op = 1-0.8*xray;
  if (wire) return <group>
    <mesh geometry={g.all}><meshBasicMaterial color="#00e5ff" wireframe transparent opacity={0.16}/></mesh>
  </group>;
  return <group>
    <mesh geometry={g.body} castShadow receiveShadow>
      <meshPhysicalMaterial color="#e6e9ec" metalness={0.25} roughness={0.32} clearcoat={1} clearcoatRoughness={0.06} transparent={xray>0} opacity={op} depthWrite={xray<0.3}/>
    </mesh>
    <mesh geometry={g.glass} castShadow>
      <meshPhysicalMaterial color="#05070a" metalness={0.5} roughness={0.05} clearcoat={1} transparent={xray>0} opacity={Math.max(op,0.25)} depthWrite={xray<0.3}/>
    </mesh>
    {xray>0.02 && <mesh geometry={g.all}><meshBasicMaterial color="#7fdcff" wireframe transparent opacity={0.07*xray}/></mesh>}
    {(car.wheels as number[][]).map(([x,y,z],i)=><group key={i} position={[x,y,z]} rotation={[Math.PI/2,0,0]}>
      <mesh castShadow><cylinderGeometry args={[car.wr,car.wr,car.ww,40]}/><meshStandardMaterial color="#121418" roughness={0.85}/></mesh>
      <mesh position={[0,z>0?-car.ww/2-0.005:car.ww/2+0.005,0]}><cylinderGeometry args={[car.wr*0.72,car.wr*0.72,0.02,32]}/><meshStandardMaterial color="#8d959e" metalness={0.9} roughness={0.25}/></mesh>
    </group>)}
    {showFan && <group position={[-0.1,0.13,0]}>
      <mesh rotation={[Math.PI/2,0,0]}><torusGeometry args={[0.5,0.045,16,64]}/><meshStandardMaterial color="#ffb347" emissive="#ff8a00" emissiveIntensity={0.6+glow} toneMapped={false}/></mesh>
      <group rotation={[0,fanSpin,0]}>{Array.from({length:7}).map((_,i)=><mesh key={i} rotation={[0,i*Math.PI*2/7,0.35]}><boxGeometry args={[0.9,0.02,0.13]}/><meshStandardMaterial color="#ffd08a" emissive="#ff9a1f" emissiveIntensity={0.4+glow*0.6} toneMapped={false}/></mesh>)}</group>
    </group>}
    {showThrust && <group>
      <mesh position={[-0.75,0.62,0]} rotation={[Math.PI/2,0,0]}><capsuleGeometry args={[0.2,0.85,8,24]}/><meshStandardMaterial color="#5ad1ff" emissive="#1aa6ff" emissiveIntensity={0.5+glow} metalness={0.6} roughness={0.25} toneMapped={false}/></mesh>
      <mesh position={[-1.12,0.62,0]} rotation={[0,0,Math.PI/2]}><cylinderGeometry args={[0.09,0.09,0.16,20]}/><meshStandardMaterial color="#ff4d5e" emissive="#ff2040" emissiveIntensity={0.6+glow} toneMapped={false}/></mesh>
      {[0.4,-0.4].map(z=><group key={z}>
        <mesh position={[-1.62,0.6,z/2]} rotation={[0,Math.atan2(z/2,0.9),Math.PI/2]}><cylinderGeometry args={[0.035,0.035,0.95,10]}/><meshStandardMaterial color="#cfe9ff" emissive="#79c8ff" emissiveIntensity={0.5+glow*0.5} toneMapped={false}/></mesh>
        <mesh position={[-2.18,0.58,z]} rotation={[0,0,Math.PI/2]}><coneGeometry args={[0.13,0.26,24,1,true]}/><meshStandardMaterial color="#c0c6cc" metalness={0.9} roughness={0.2} side={THREE.DoubleSide}/></mesh>
      </group>)}
      {[[1.75,0.62,0.78],[1.75,0.62,-0.78],[-1.85,0.82,0.85],[-1.85,0.82,-0.85]].map((p,i)=><mesh key={i} position={p as any}><sphereGeometry args={[0.07,16,16]}/><meshStandardMaterial color="#ffe36b" emissive="#ffc400" emissiveIntensity={0.8+glow} toneMapped={false}/></mesh>)}
    </group>}
  </group>;
};
