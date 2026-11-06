import base64,json,os,sys
from pathlib import Path
import requests
def synth(text,path,ref,speed=1.0,temp=.7,top_p=None,latency='normal',chunk_length=None):
    s=requests.Session();s.trust_env=False
    body={'text':text,'format':'mp3','temperature':temp,'prosody':{'speed':speed,'volume':0},'latency':latency,'reference_id':ref}
    if top_p is not None: body['top_p']=top_p
    if chunk_length is not None: body['chunk_length']=chunk_length
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
if __name__=='__main__':
    # fish.py <tag> <ref> <ids|all>
    tag,ref,ids=sys.argv[1:4]
    S=json.load(open('/workspace/pi/voice/sentences.json'))
    ids=range(len(S)) if ids=='all' else [int(i) for i in ids.split(',')]
    from concurrent.futures import ThreadPoolExecutor
    def job(i):
        s=S[i];p=f'/workspace/pi/voice/takes/{tag}-{i:02d}.mp3'
        for a in range(3):
            try: synth(s['cue']+s['tts'],p,ref,s['speed']*float(os.environ.get('SPEED_SCALE','1')));return f'{i} ok'
            except Exception as e: err=str(e)
        return f'{i} FAIL {err}'
    with ThreadPoolExecutor(4) as ex:
        for r in ex.map(job,ids): print(tag,r,flush=True)
