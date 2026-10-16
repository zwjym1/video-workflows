// Word-level sync helpers shared by v3 test segments. All timing comes from Fish alignment JSON.
export type Alignment={audio:string;text:string;duration:number;frames:number;boundaries:{text:string;offset:number;duration:number}[]};
const PUNCT=/[，。；：、！？,.;:!?\s]/;
export const FPS=30;
// Frame where `phrase` starts (nth occurrence). Throws if the phrase is not found, so timing errors fail loudly.
export const wordFrame=(al:Alignment,phrase:string,nth=0):number=>{
 const chars=al.boundaries.map(b=>b.text).join('');let from=0,idx=-1;
 for(let i=0;i<=nth;i++){idx=chars.indexOf(phrase,from);if(idx<0)throw new Error(`phrase not found: ${phrase}`);from=idx+1;}
 return Math.round(al.boundaries[idx].offset*FPS);
};
export const wordEnd=(al:Alignment,phrase:string,nth=0):number=>{
 const chars=al.boundaries.map(b=>b.text).join('');let from=0,idx=-1;
 for(let i=0;i<=nth;i++){idx=chars.indexOf(phrase,from);from=idx+1;}
 const last=al.boundaries[idx+phrase.length-1];return Math.round((last.offset+last.duration)*FPS);
};
// Sentences of the narration with per-char start frames (punctuation kept, inherits previous char time).
export const sentences=(al:Alignment)=>{
 const out:{chars:{c:string;f:number}[];start:number}[]=[];let cur:{c:string;f:number}[]=[];let k=0,last=0,rem=0;
 for(const c of al.text){if(PUNCT.test(c)){cur.push({c,f:last});if(/[。；！？]/.test(c)){out.push({chars:cur,start:cur[0].f});cur=[];}continue;}
  if(rem<=0){const b=al.boundaries[k++];last=Math.round(b.offset*FPS);rem=[...b.text].length;}rem--;cur.push({c,f:last});}
 if(cur.length)out.push({chars:cur,start:cur[0].f});return out;
};
export const rand=(seed:number)=>{let t=seed+0x6d2b79f5;return()=>{t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};};
