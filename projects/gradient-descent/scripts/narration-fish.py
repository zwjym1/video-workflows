"""Fish free-tier narration with word timestamps. Key is read from environment only."""
import base64
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import requests

ROOT = Path(__file__).resolve().parent.parent

def synthesize(index, text):
    session = requests.Session()
    # This machine's local proxy intermittently drops the Fish TLS handshake.
    session.trust_env = False
    response = session.post(
        'https://api.fish.audio/v1/tts/stream/with-timestamp',
        headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'],
                 'model': 's2.1-pro-free', 'Content-Type': 'application/json'},
        json={'text': text, 'format': 'mp3', 'temperature': .65,
              'prosody': {'speed': 1.08, 'volume': 0}, 'latency': 'normal'},
        timeout=120,
    )
    if not response.ok:
        raise RuntimeError(f'Fish HTTP {response.status_code}: {response.text[:250]}')
    chunks = []
    snapshots = {}
    for line in response.content.decode('utf-8').splitlines():
        if not line.startswith('data: '):
            continue
        event = json.loads(line[6:])
        if event.get('audio_base64'):
            chunks.append(base64.b64decode(event['audio_base64']))
        if event.get('alignment'):
            snapshots[event.get('chunk_seq', 0)] = event
    target = ROOT / 'public' / f'fish-gradient-{index}.mp3'
    target.write_bytes(b''.join(chunks))
    if not chunks or not snapshots:
        raise RuntimeError('No audio or alignment received')
    duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=nw=1:nk=1', str(target)], text=True))
    boundaries = []
    for seq in sorted(snapshots):
        event = snapshots[seq]
        offset = event.get('chunk_audio_offset_sec', 0)
        for segment in event['alignment']['segments']:
            boundaries.append({'text': segment['text'], 'offset': offset + segment['start'],
                               'duration': segment['end'] - segment['start']})
    result = {'audio': target.name, 'text': text, 'duration': duration,
              'frames': math.ceil(duration * 30) + 5, 'boundaries': boundaries}
    (ROOT / 'output' / f'fish-gradient-{index}-alignment.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Segment {index}: {duration:.3f}s, {len(boundaries)} timestamp segments')
    return result

if __name__ == '__main__':
    source = json.loads((ROOT / 'src/gradient/timing.json').read_text(encoding='utf-8'))
    if sys.argv[1:] == ['full']:
        synthesize('full', ''.join(item['text'] for item in source))
        sys.exit(0)
    indices = [int(v) for v in sys.argv[1:]] or [0, 1, 2, 3]
    for i in indices:
        synthesize(i, source[i]['text'])
    if len(indices) == 4:
        output = []
        start = 0
        for i in range(4):
            item = json.loads((ROOT / 'output' / f'fish-gradient-{i}-alignment.json').read_text(encoding='utf-8'))
            item['start'] = start
            start += item['frames']
            output.append(item)
        folder = ROOT / 'src/gradient-sync'
        folder.mkdir(exist_ok=True)
        (folder / 'timing.json').write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Total frames:', start)
