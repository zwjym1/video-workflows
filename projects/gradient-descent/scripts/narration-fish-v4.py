"""v4 narration: per-sentence Fish takes (same voice), S2 [bracket] cues, per-sentence speed.
Key only from FISH_API_KEY env. Outputs under output/v4-voice/."""
import base64,json,os,subprocess,sys
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'output'/'v4-voice';OUT.mkdir(parents=True,exist_ok=True)
SENT=json.loads((ROOT/'scripts'/'v4-sentences.json').read_text(encoding='utf-8'))
def synth(text,path,ref=None,speed=1.08,temp=.65):
    s=requests.Session();s.trust_env=False
    body={'text':text,'format':'mp3','temperature':temp,'prosody':{'speed':speed,'volume':0},'latency':'normal'}
    if ref:body['reference_id']=ref
    r=s.post('https://api.fish.audio/v1/tts/stream/with-timestamp',headers={'Authorization':'Bearer '+os.environ['FISH_API_KEY'],'model':'s2.1-pro-free','Content-Type':'application/json'},json=body,timeout=180)
    if not r.ok:raise RuntimeError(f'HTTP {r.status_code}: {r.text[:200]}')
    chunks=[];snaps={}
    for line in r.content.decode('utf-8').splitlines():
        if not line.startswith('data: '):continue
        ev=json.loads(line[6:])
        if ev.get('audio_base64'):chunks.append(base64.b64decode(ev['audio_base64']))
        if ev.get('alignment'):snaps[ev.get('chunk_seq',0)]=ev
    Path(path).write_bytes(b''.join(chunks))
    b=[]
    for k in sorted(snaps):
        ev=snaps[k];off=ev.get('chunk_audio_offset_sec',0)
        for sg in ev['alignment']['segments']:b.append({'text':sg['text'],'offset':off+sg['start'],'duration':sg['end']-sg['start']})
    Path(str(path)+'.json').write_text(json.dumps(b,ensure_ascii=False),encoding='utf-8')
    return b
if __name__=='__main__':
    # usage: narration-fish-v4.py <tag> <ref|none> <sentence indices comma|all> [speedScale]
    tag,ref,idx=sys.argv[1],sys.argv[2],sys.argv[3]
    scale=float(sys.argv[4]) if len(sys.argv)>4 else 1
    ids=range(len(SENT)) if idx=='all' else [int(i) for i in idx.split(',')]
    for i in ids:
        s=SENT[i];text=(s.get('cue','')+s['text'])
        synth(text,OUT/f'{tag}-{i:02d}.mp3',None if ref=='none' else ref,s.get('speed',1.08)*scale)
        print(tag,i,'ok')
