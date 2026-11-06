#!/usr/bin/env python3
"""抖音热门 BGM：免登录取热歌榜 / 按 music_id 取音乐详情 → 下载试听音频 → 本地分析（BPM、高能段、3 秒炸开起点）。

数据源（均为公开、无签名、无 cookie 的接口；遇到非 200 / status_code≠0 / 验证页就记录并停止，不重试换身份）：
  1) 热歌榜  https://aweme.snssdk.com/aweme/v1/chart/music/list/?chart_id=6853972723954146568
     （飙升榜/原创榜的 chart_id 在游客态返回 status_code=4，未采到）
  2) 音乐详情 https://aweme.snssdk.com/aweme/v1/music/detail/?music_id=<id>
     music_id 可从 douyin-field-collect 的 collect.json → bgm.meta.music_id 拿到（视频里用到的曲子）。
  play_url.url_list 是抖音 CDN 的试听 mp3；strong_beat_url 是抖音自己给的强拍点（有就一并存）。

用法：
  PY=/workspace/.venv-dy/bin/python
  $PY dy_hot_bgm.py chart -o OUT                  # 只拉榜单 → OUT/chart.json + chart.md
  $PY dy_hot_bgm.py get ID [ID...] -o OUT         # 按 music_id 下载+分析
  $PY dy_hot_bgm.py chart -o OUT --pick 19,21,27  # 拉榜并下载第 19/21/27 名
  $PY dy_hot_bgm.py analyze FILE.mp3 [...]        # 只做本地分析
  $PY dy_hot_bgm.py reindex -o OUT                # 已下载的重新分析、重写 index
输出：OUT/<序号>_<曲名>.mp3、同名 .json（元数据+分析）、OUT/index.json、OUT/index.md
分析是 librosa 启发式：BPM 可能差 2 倍；「高能到来」= 平滑 RMS 首次持续 ≥1s 超过全曲 70 分位；
「炸开起点」= 平滑 RMS 进入高能段前 1 小节对齐拍点；low_end_drops = 35-150Hz 低频前后 1s 跃升 ≥6dB 的点（底鼓/贝斯进场），
每个给 start_s（跃升前 0.8-2.2s 的拍点），从 start_s 开播约 1.5-2s 内炸开——做「3 秒内炸开」开头优先用它。
若 first_loud_s<1.2 也可直接从 0 开播。
"""
import argparse, json, os, re, sys, time
import requests

UA = {'User-Agent': 'okhttp3'}
Q = dict(device_platform='android', version_name='13.2.0', version_code='130200', aid='1128')
HOT_CHART = '6853972723954146568'
BASE = 'https://aweme.snssdk.com/aweme/v1'


class Blocked(Exception):
    pass


def _get(url, params):
    r = requests.get(url, params={**params, **Q}, headers=UA, timeout=20)
    if r.status_code != 200:
        raise Blocked(f'HTTP {r.status_code} {url}')
    try:
        d = r.json()
    except Exception:
        raise Blocked(f'non-JSON (可能是验证页) {url}: {r.text[:120]!r}')
    if d.get('status_code') not in (0, None):
        raise Blocked(f'status_code={d.get("status_code")} {d.get("status_msg") or d.get("msg")} {url}')
    return d


def _info(mi, rank=None, heat=None):
    pu = (mi.get('play_url') or {}).get('url_list') or []
    sb = mi.get('strong_beat_url') or {}
    return dict(rank=rank, music_id=mi.get('id_str'), title=mi.get('title'), author=mi.get('author'),
                heat=heat, user_count=mi.get('user_count'), duration_s=mi.get('duration'),
                is_commerce_music=mi.get('is_commerce_music'), is_original_sound=mi.get('is_original_sound'),
                is_pgc=mi.get('is_pgc'), prevent_download=mi.get('prevent_download'),
                preview_start_time=mi.get('preview_start_time'), shoot_duration=mi.get('shoot_duration'),
                play_url=pu[0] if pu else None, strong_beat_url=(sb.get('url_list') or [None])[0],
                music_page_url=f'https://www.douyin.com/music/{mi.get("id_str")}')


def fetch_chart(chart_id=HOT_CHART):
    d = _get(f'{BASE}/chart/music/list/', dict(chart_id=chart_id, count=100))
    out = [_info(m['music_info'], i + 1, m.get('heat')) for i, m in enumerate(d.get('music_list') or [])]
    return dict(chart_id=chart_id, fetched_at=time.strftime('%Y-%m-%d %H:%M:%S %z'), items=out)


def fetch_detail(mid):
    d = _get(f'{BASE}/music/detail/', dict(music_id=mid))
    return _info(d['music_info'])


def safe(s):
    return re.sub(r'[\\/:*?"<>|\s]+', '_', s or 'x')[:40]


def download(url, path):
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
    if r.status_code != 200 or len(r.content) < 10000:
        raise Blocked(f'audio HTTP {r.status_code} len={len(r.content)}')
    open(path, 'wb').write(r.content)


def analyze(path):
    import numpy as np, librosa
    import subprocess, tempfile
    tmp = tempfile.mktemp(suffix='.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-ac', '1', '-ar', '22050', tmp], check=True)
    y, sr = librosa.load(tmp, sr=22050, mono=True)
    os.remove(tmp)
    dur = len(y) / sr
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])
    bt = librosa.frames_to_time(beats, sr=sr)
    hop = 512
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    k = max(1, int(0.5 * sr / hop))
    sm = np.convolve(rms, np.ones(k) / k, mode='same')
    db = 20 * np.log10(sm + 1e-9)
    thr = np.percentile(db, 70)
    need = int(1.0 * sr / hop)
    above = db >= thr
    hi = None
    run = 0
    for i, a in enumerate(above):
        run = run + 1 if a else 0
        if run >= need:
            hi = float(t[i - need + 1]); break
    w = int(2.0 * sr / hop)
    skip = int(4.0 * sr / hop)  # 跳过开头淡入，避免把淡入当成跃升
    best, bi = -1e9, None
    for i in range(max(w, skip), len(db) - w):
        jump = db[i:i + w].mean() - db[i - w:i].mean()
        if jump > best:
            best, bi = jump, i
    drop = float(t[bi]) if bi is not None else None
    bar = 4 * 60 / tempo if tempo > 0 else 2.0
    # 炸开起点：在「高能到来」前推 1 小节并对齐拍点 → 开播后约 1 小节（<2s@120BPM）进入高能段
    start = 0.0
    if hi is not None and hi > 2.0:
        s0 = max(0.0, hi - bar)
        if len(bt):
            s0 = float(bt[np.argmin(np.abs(bt - s0))])
        start = s0
    start = round(start, 2)
    curve = [round(float(db[(t >= a) & (t < a + 1)].mean()), 1) for a in range(int(dur))]
    # 低频（35-150Hz，底鼓/贝斯）跃升点：前后 1s 均值差，取 ≥6dB 的前 3 个（间隔 ≥8s）
    h2 = 256
    S2 = np.abs(librosa.stft(y, n_fft=2048, hop_length=h2)) ** 2
    f2 = librosa.fft_frequencies(sr=sr, n_fft=2048)
    low = 10 * np.log10(S2[(f2 >= 35) & (f2 <= 150)].sum(0) + 1e-12)
    t2 = librosa.frames_to_time(np.arange(len(low)), sr=sr, hop_length=h2)
    kk = int(1.0 * sr / h2)
    c = np.concatenate([[0], np.cumsum(low)])
    jumps = np.full(len(low), -1e9)
    for j in range(max(kk, int(1.5 * sr / h2)), len(low) - kk):  # 跳过开头 1.5s 静音→有声的边沿
        jumps[j] = (c[j + kk] - c[j]) / kk - (c[j] - c[j - kk]) / kk
    drops = []
    for j in np.argsort(-jumps):
        if jumps[j] < 6 or len(drops) >= 3:
            break
        td = float(t2[j])
        if any(abs(td - d['drop_s']) < 8 for d in drops):
            continue
        st = max(0.0, td - 1.8)
        cand = bt[(bt <= td - 0.8) & (bt >= td - 2.2)] if len(bt) else []
        if len(cand):
            st = float(cand[0])
        drops.append(dict(drop_s=round(td, 2), low_jump_db=round(float(jumps[j]), 1), start_s=round(st, 2), explode_after_start_s=round(td - st, 2)))
    first_loud = float(t[np.argmax(db > db.max() - 12)])
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    ot = librosa.times_like(onset, sr=sr)
    first3 = float(onset[ot < 3].mean()) if (ot < 3).any() else None
    # 人声粗判：谐波占比 + 300-3400Hz 能量占比（启发式）
    S = np.abs(librosa.stft(y[: sr * 60]))
    f = librosa.fft_frequencies(sr=sr)
    voc = float(S[(f > 300) & (f < 3400)].sum() / (S.sum() + 1e-9))
    return dict(duration_s=round(dur, 2), bpm=round(tempo, 1), first_beat_s=round(float(bt[0]), 2) if len(bt) else None,
                high_energy_arrival_s=round(hi, 2) if hi is not None else None, biggest_energy_jump_s=round(drop, 2) if drop else None,
                jump_db=round(float(best), 1), explode_start_s=start,
                explode_note=(f'从 {start}s 开播 → 约 {round(hi - start, 2)}s 后进入高能段' if hi is not None else '全曲能量平稳，无明显高能段'),
                low_end_drops=sorted(drops, key=lambda d: d['drop_s']), first_loud_s=round(first_loud, 2),
                rms_db_per_sec=curve, energy_p70_db=round(float(thr), 1),
                onset_mean_first3s=round(first3, 2) if first3 else None, onset_mean_all=round(float(onset.mean()), 2),
                loudness_rms_db_mean=round(float(db.mean()), 1), vocal_band_share=round(voc, 2), heuristic=True)


def process(items, out):
    os.makedirs(out, exist_ok=True)
    idx = []
    for n, it in enumerate(items, 1):
        rec = dict(it)
        if not it.get('play_url'):
            rec['download'] = 'observed_empty（无 play_url）'
        else:
            p = os.path.join(out, f'{n:02d}_{safe(it["title"])}.mp3')
            try:
                download(it['play_url'], p)
                rec['file'] = p
                rec['download'] = 'available'
                if it.get('strong_beat_url'):
                    try:
                        r = requests.get(it['strong_beat_url'], timeout=20)
                        if r.status_code == 200:
                            open(p[:-4] + '.strong_beat.json', 'wb').write(r.content)
                            rec['strong_beat_file'] = p[:-4] + '.strong_beat.json'
                    except Exception as e:
                        rec['strong_beat_file'] = f'error {e}'
                try:
                    rec['analysis'] = analyze(p)
                except Exception as e:
                    rec['analysis'] = {'status': f'error {e}'}
            except Blocked as e:
                rec['download'] = f'blocked_verification/error: {e}'
                print('STOP:', e, file=sys.stderr)
                idx.append(rec); break
            json.dump(rec, open(p[:-4] + '.json', 'w'), ensure_ascii=False, indent=1)
        idx.append(rec)
        print(n, rec.get('title'), rec.get('download'), (rec.get('analysis') or {}).get('bpm'))
        time.sleep(1.0)
    write_index(idx, out)
    return idx


def write_index(idx, out):
    json.dump(idx, open(os.path.join(out, 'index.json'), 'w'), ensure_ascii=False, indent=1)
    L = ['| # | 曲名 | 作者 | 热度 | 使用数 | 时长 | BPM | 高能到来 | 最大跃升 | 3秒炸开起点 | 文件 |', '|' + '---|' * 11]
    for r in idx:
        a = r.get('analysis') or {}
        L.append(f"| {r.get('rank') or ''} | {r.get('title')} | {r.get('author')} | {r.get('heat') or '未采到'} | {r.get('user_count')} | {a.get('duration_s')} | {a.get('bpm')} | {a.get('high_energy_arrival_s')} | {a.get('biggest_energy_jump_s')} ({a.get('jump_db')}dB) | {a.get('explode_start_s')} | {os.path.basename(r.get('file') or r.get('download'))} |")
    open(os.path.join(out, 'index.md'), 'w').write('\n'.join(L) + '\n')


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    c = sp.add_parser('chart'); c.add_argument('-o', required=True); c.add_argument('--pick', default='')
    g = sp.add_parser('get'); g.add_argument('ids', nargs='+'); g.add_argument('-o', required=True)
    ri = sp.add_parser('reindex'); ri.add_argument('-o', required=True)
    a = sp.add_parser('analyze'); a.add_argument('files', nargs='+')
    x = ap.parse_args()
    try:
        if x.cmd == 'chart':
            os.makedirs(x.o, exist_ok=True)
            ch = fetch_chart()
            json.dump(ch, open(os.path.join(x.o, 'chart.json'), 'w'), ensure_ascii=False, indent=1)
            md = [f"抖音热歌榜 chart_id={ch['chart_id']} 取于 {ch['fetched_at']}", '', '| # | 曲名 | 作者 | 热度 | 使用数 | 时长s | music_id |', '|---|---|---|---|---|---|---|']
            md += [f"| {i['rank']} | {i['title']} | {i['author']} | {i['heat']} | {i['user_count']} | {i['duration_s']} | {i['music_id']} |" for i in ch['items']]
            open(os.path.join(x.o, 'chart.md'), 'w').write('\n'.join(md) + '\n')
            print(f"chart: {len(ch['items'])} items -> {x.o}/chart.md")
            if x.pick:
                ranks = [int(v) for v in x.pick.split(',')]
                process([i for i in ch['items'] if i['rank'] in ranks], x.o)
        elif x.cmd == 'get':
            items = []
            for mid in x.ids:
                items.append(fetch_detail(mid)); time.sleep(1.0)
            process(items, x.o)
        elif x.cmd == 'reindex':
            idx = json.load(open(os.path.join(x.o, 'index.json')))
            for r in idx:
                if r.get('file') and os.path.exists(r['file']):
                    r['analysis'] = analyze(r['file']); json.dump(r, open(r['file'][:-4] + '.json', 'w'), ensure_ascii=False, indent=1)
            write_index(idx, x.o)
        else:
            for f in x.files:
                print(f, json.dumps(analyze(f), ensure_ascii=False))
    except Blocked as e:
        print('STOP（按规则不重试）:', e, file=sys.stderr); sys.exit(2)


if __name__ == '__main__':
    main()
