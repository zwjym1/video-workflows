import al from './alignment.json';
export const FPS=30;
type Word={text:string;start:number;end:number;sentence:number};
type Sent={i:number;chapter:number;text:string;start:number;end:number;pause_after:number};
export const S=al.sentences as Sent[];
const words=al.words as Word[];
export const DUR:number=al.duration;
export const TOTAL=Math.ceil(DUR*FPS)+15;
export const PUN=/[，。；：、！？,.;:!?\s“”"'（）()]/;
export const sentText=S.map(s=>[...s.text].filter(c=>!PUN.test(c)).join(''));
export const charT:number[][]=S.map(()=>[]);
export const charE:number[][]=S.map(()=>[]);
for(const w of words){if(PUN.test(w.text))continue;charT[w.sentence].push(w.start);charE[w.sentence].push(w.end);}
S.forEach((s,i)=>{if(charT[i].length!==[...sentText[i]].length)throw new Error('char mismatch '+i);});
const find=(i:number,ph:string,occ:number)=>{const txt=[...sentText[i]].join('');let idx=-1,from=0;for(let k=0;k<=occ;k++){idx=txt.indexOf(ph,from);if(idx<0)break;from=idx+1;}
 if(idx<0)throw new Error(`phrase "${ph}" not in sentence ${i}: ${txt}`);return [...txt.slice(0,idx)].length;};
/** time (s) when the first char of phrase is spoken in sentence i */
export const at=(i:number,ph:string,occ=0)=>charT[i][find(i,ph,occ)];
/** time (s) when the last char of phrase ends */
export const atEnd=(i:number,ph:string,occ=0)=>charE[i][find(i,ph,occ)+[...ph].length-1];
export const ss=(i:number)=>S[i].start;
export const se=(i:number)=>S[i].end;
export const CH=[0,1,2,3,4,5,6].map(c=>S.find(s=>s.chapter===c)!.start);
export const CH_END=[...CH.slice(1),DUR];
export const chapterFrames=(c:number)=>{const a=Math.round(CH[c]*FPS);const b=c===6?TOTAL:Math.round(CH[c+1]*FPS);return {from:a,dur:b-a};};
