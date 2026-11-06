import subprocess,re,json,asyncio,numpy as np,glob,os
from shazamio import Shazam
B='/workspace/science-studio/knowledge/aning_rhythm/sep/out/htdemucs'
def lufs(f):
    e=subprocess.run(['ffmpeg','-nostats','-i',f,'-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',e)[-1])
def gaps(f):
    e=subprocess.run(['ffmpeg','-nostats','-i',f,'-af','silencedetect=n=-38dB:d=0.08','-f','null','-'],capture_output=True,text=True).stderr
    return [float(x) for x in re.findall(r'silence_duration: ([\d.]+)',e)]
async def main():
    sh=Shazam();R={}
    for d in sorted(glob.glob(B+'/*')):
        k=os.path.basename(d);nv=d+'/no_vocals.wav';vo=d+'/vocals.wav';ms=[]
        for ss in (5,40,80):
            subprocess.run(['ffmpeg','-y','-v','error','-ss',str(ss),'-t','20','-i',nv,'-ac','1','-ar','16000','/tmp/nv.wav'])
            try: s=await sh.recognize('/tmp/nv.wav'); t=s.get('track',{}); ms.append((t.get('title'),t.get('subtitle')))
            except Exception as ex: ms.append(str(ex)[:60])
        g=np.array(gaps(vo));g=g[g<2.5]
        R[k]=dict(shazam=ms,lufs_vocal=lufs(vo),lufs_bgm=lufs(nv),gap_n=len(g),gap_median=round(float(np.median(g)),2),gap_p25=round(float(np.percentile(g,25)),2),gap_p75=round(float(np.percentile(g,75)),2),gap_over_0_6=int((g>0.6).sum()))
    print(json.dumps(R,ensure_ascii=False,indent=1));json.dump(R,open('stats_sep.json','w'),ensure_ascii=False,indent=1)
asyncio.run(main())
