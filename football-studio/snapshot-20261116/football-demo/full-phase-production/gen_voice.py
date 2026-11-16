from pathlib import Path
import sys,json,subprocess
sys.path.insert(0,'/workspace/football-demo/manutd-tactics/src');from fish_lib import synth
R=Path(__file__).parent;plan=json.loads((R/'script/ORIGINAL_SCRIPT.json').read_text());out=[]
for s in plan['scenes']:
 p=R/'audio'/f"{s['id']}.mp3"
 if not p.exists():synth(s['voiceover'],str(p),'906524668b6d4afe84736962e005cd09',speed=.97,temp=.65,top_p=.7,latency='normal',chunk_length=300,model='s2.1-pro-free')
 w=json.loads(Path(str(p)+'.json').read_text());out.append({'id':s['id'],'text':s['voiceover'],'words':w,'core_end':max(x['offset']+x['duration'] for x in w),'file':str(p)});print(s['id'],out[-1]['core_end'],flush=True)
(R/'script/VOICE_TIMESTAMPS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('VOICE_READY',flush=True)
