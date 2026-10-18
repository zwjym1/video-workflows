"""Fish Audio 逐句合成。密钥只从环境变量 FISH_API_KEY 读取，不落盘。
用法: tts.py <voice_id> <tag> <ids comma|all> [takes]"""
import base64, json, os, sys, subprocess
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).parent))
from sentences import S
OUT = Path(__file__).parent / 'takes'
def synth(text, path, ref, speed, temp=0.65):
    s = requests.Session(); s.trust_env = False
    body = {'text': text, 'format': 'mp3', 'mp3_bitrate': 192, 'temperature': temp,
            'prosody': {'speed': speed, 'volume': 0}, 'latency': 'normal', 'reference_id': ref}
    r = s.post('https://api.fish.audio/v1/tts/stream/with-timestamp',
               headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'], 'model': 's2.1-pro-free',
                        'Content-Type': 'application/json'}, json=body, timeout=180)
    if not r.ok: raise RuntimeError(f'HTTP {r.status_code}: {r.text[:200]}')
    chunks, snaps = [], {}
    for line in r.content.decode('utf-8').splitlines():
        if not line.startswith('data: '): continue
        ev = json.loads(line[6:])
        if ev.get('audio_base64'): chunks.append(base64.b64decode(ev['audio_base64']))
        if ev.get('alignment'): snaps[ev.get('chunk_seq', 0)] = ev
    mp3 = Path(str(path) + '.mp3'); mp3.write_bytes(b''.join(chunks))
    segs = []
    for k in sorted(snaps):
        ev = snaps[k]; off = ev.get('chunk_audio_offset_sec', 0)
        for sg in ev['alignment']['segments']:
            segs.append({'text': sg['text'], 'start': off + sg['start'], 'end': off + sg['end']})
    Path(str(path) + '.align.json').write_text(json.dumps(segs, ensure_ascii=False), encoding='utf-8')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(mp3), '-ar', '48000', '-ac', '1', str(path) + '.wav'], check=True)
if __name__ == '__main__':
    ref, tag, ids = sys.argv[1], sys.argv[2], sys.argv[3]
    takes = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    ids = [x[0] for x in S] if ids == 'all' else ids.split(',')
    for sid, text, tts, cue, speed, pause in S:
        if sid not in ids: continue
        for k in range(takes):
            p = OUT / f'{tag}_{sid}_t{k+1}'
            synth(cue + (tts or text), p, ref, speed)
            print(tag, sid, k + 1, 'ok', flush=True)
