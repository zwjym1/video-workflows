import json,re,subprocess,numpy as np,sys
V={'MCP':'7702426566919212315','Harness':'7701615317113457929','Skill':'7701927915331636515'}
R={}
for k,v in V.items():
    D=f'/workspace/watch/douyin_{v}';seg=json.load(open(D+'/transcript.json'))['segments']
    ch=[len(re.sub(r'[\s,，。！？!?、:：;；"“”]','',s['text'])) for s in seg];du=[s['end']-s['start'] for s in seg]
    words=[w for s in seg for w in s.get('words',[])]
    cs=np.array(ch)/np.maximum(np.array(du),0.3)
    out=subprocess.run(['ffmpeg','-nostats','-i',D+'/video.mp4','-vf','select=gt(scene\\,0.3),showinfo','-an','-f','null','-'],capture_output=True,text=True).stderr
    cuts=[float(x) for x in re.findall(r'pts_time:([\d.]+)',out)];c2=[]
    for c in cuts:
        if not c2 or c-c2[-1]>0.2:c2.append(c)
    dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',D+'/video.mp4'],capture_output=True,text=True).stdout)
    R[k]=dict(dur=round(dur,1),lines=len(seg),line_dur_mean=round(np.mean(du),2),line_dur_median=round(np.median(du),2),chars=int(sum(ch)),cps_overall=round(sum(ch)/dur,2),cps_line_median=round(float(np.median(cs)),2),
      short_le8=int(sum(1 for c in ch if c<=8)),long_ge30=int(sum(1 for c in ch if c>=30)),cuts=len(c2),sec_per_cut=round(dur/max(1,len(c2)),1),has_words=bool(words))
print(json.dumps(R,ensure_ascii=False,indent=1));json.dump(R,open('stats_basic.json','w'),ensure_ascii=False,indent=1)
