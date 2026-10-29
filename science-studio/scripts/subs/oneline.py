#!/usr/bin/env python3
"""一句一字幕（全局通用）。
把逐字稿卡片（可能一卡多句）切成「一屏一句」的短句卡，并按 ASR 字级时间戳对时。
用法：
  python3 scripts/subs/oneline.py --cards cards.json [--words asr_chunks.json] [--silences silences.txt]
         --out-json subs_oneline.json [--out-srt subs.srt] [--out-ts src/subs_oneline.ts] [--end 116.9]
cards.json：[{text,a,b}...]（a/b 为该卡语音起止秒）；words：[{words:[{w,s,e}]}...]（whisper word_timestamps）。
规则：按 ，。？！；：、… 切句（引号/书名号内不切）；每句一卡、单行；单句超过 MAX_CHARS 时在语义处再切成连续两卡；
句末标点不显示（？！保留）；时间：句首字时间取 ASR 字级时间（逐字对齐 difflib；2026-10-22 起，原为按字符比例映射），没有 ASR 时按字数比例；
句边界若邻近停顿（silences，±0.3s）则吸附到停顿中点；每卡最短 0.45s。
"""
import json, re, argparse
PUNCT = '，。？！；：、…,.?!;:'
MAX_CHARS = 16
KEEP_END = '？！?!'

def clauses(text):
    out, buf, depth = [], '', 0
    for i, ch in enumerate(text):
        if ch == '.' and 0 < i < len(text) - 1 and text[i - 1].isdigit() and text[i + 1].isdigit():
            buf += ch; continue  # 小数点不切
        if ch in '「“《(（': depth += 1
        if ch in '」”》)）': depth = max(0, depth - 1)
        buf += ch
        if ch in PUNCT and depth == 0:
            if buf.strip(PUNCT + ' '): out.append(buf)
            buf = ''
    if buf.strip(PUNCT + ' '): out.append(buf)
    res = []
    for c in out:
        core = c.rstrip(PUNCT + ' ')
        if vis_len(core) > MAX_CHARS:
            k = best_split(core); res += [core[:k], core[k:] + c[len(core):]]
        else: res.append(c)
    return res

def vis_len(s): return sum(0.55 if re.match(r'[0-9.a-zA-Z%–-]', ch) else 1 for ch in s)

def best_split(s):
    n = len(s); best, bd = n // 2, 1e9
    for i in range(3, n - 2):
        bonus = -2 if s[i - 1] in '的了把被在是就和与后' or s[i] in '把被在就和与' else 0
        if re.match(r'[0-9.]', s[i - 1]) and re.match(r'[0-9.]', s[i]): continue
        d = abs(vis_len(s[:i]) - vis_len(s[i:])) + bonus
        if d < bd: best, bd = i, d
    return best

def display(c):
    core = c.rstrip(PUNCT + ' ')
    end = c[len(core):].strip()
    return core + (end[0] if end and end[0] in KEEP_END else '')

def char_times(words, a, b):
    """返回 [(字, 时间)]：只取与本卡 [a,b] 有实际重叠的 ASR 词（词中点在区间内），避免相邻卡的字渗入。"""
    ts = []
    for w in words:
        if w['e'] < a - 0.15 or w['s'] > b + 0.15: continue
        mid = (w['s'] + w['e']) / 2
        if not (a - 0.05 <= mid <= b + 0.05): continue
        chars = [ch for ch in w['w'] if ch.strip() and ch not in '，。？！；：、…,?!;:']
        for j, ch in enumerate(chars): ts.append((ch, w['s'] + (w['e'] - w['s']) * j / max(1, len(chars))))
    return ts

def _norm(ch): return ch.lower()

def map_index(card_chars, asr_chars):
    """卡片字序 → ASR 字序的下标映射（difflib 对齐；数字/英文读法不一致处按相邻锚点线性插值）。"""
    import difflib
    n, m = len(card_chars), len(asr_chars)
    if not n or not m: return lambda i: 0
    sm = difflib.SequenceMatcher(None, [_norm(c) for c in card_chars], [_norm(c) for c in asr_chars], autojunk=False)
    anch = [(0, 0)]
    for blk in sm.get_matching_blocks():
        for t in range(blk.size): anch.append((blk.a + t, blk.b + t))
    anch.append((n, m)); anch = sorted(set(anch))
    def f(i):
        for (i0, j0), (i1, j1) in zip(anch, anch[1:]):
            if i0 <= i <= i1:
                if i == i0: return j0
                return int(round(j0 + (j1 - j0) * (i - i0) / max(1, i1 - i0)))
        return int(round(i * m / n))
    return f

def load_sil(p):
    if not p: return []
    return [tuple(map(float, x.split('-'))) for x in open(p).read().split()]

def build(cards, words=None, sil=None, end=None):
    allw = [w for ch in (words or []) for w in ch.get('words', [])]
    out = []
    for ci, c in enumerate(cards):
        parts = clauses(c['text']); a, b = c['a'], c['b']
        lens = [max(1, len([x for x in p if x not in '，。？！；：、…,?!;: '])) for p in parts]
        tot = sum(lens); ctc = char_times(allw, a, b); ct = [t for _, t in ctc]
        cchars = [x for p in parts for x in p if x not in '，。？！；：、…,?!;: ']
        mp = map_index(cchars, [ch for ch, _ in ctc])
        starts, acc = [], 0
        for L in lens:
            frac = acc / tot
            # 2026-10-22 修复：原先按「字数比例 × ASR 字数」取下标，ASR 窗口里混入相邻卡的字（±0.15s）或数字读法字数不同时，
            # 句首会偏到后一个字（如「按下去是软的」1.48→1.64）。现改为逐字对齐取句首字的真实时间；无 ASR 时行为不变。
            if ct and len(ct) >= 2: t = ct[min(len(ct) - 1, mp(acc))] if acc else a
            else: t = a + (b - a) * frac
            starts.append(max(a, min(b, t))); acc += L
        for k in range(1, len(starts) if not (ct and len(ct) >= 2) else 1):  # 有字级 ASR 时直接用句首字时间，不再吸附停顿（吸附到 silence_end 会比开口晚 0.1–0.15s）
            for s0, s1 in (sil or []):
                m = (s0 + s1) / 2
                if abs(m - starts[k]) < 0.3 and starts[k - 1] < m < b: starts[k] = s1 if s1 - s0 < 0.6 else m; break
        for k, p in enumerate(parts):
            sa = starts[k]; sb = starts[k + 1] if k + 1 < len(parts) else b
            out.append({'card': c.get('card', ci + 1), 'sub': k + 1, 'text': display(p), 'a': round(sa, 2), 'b': round(sb, 2)})
    for i, s in enumerate(out):  # 显示区间：前后衔接，无空屏闪烁
        nxt = out[i + 1]['a'] if i + 1 < len(out) else (end or s['b'] + 0.3)
        s['show_a'] = round(max(0, s['a'] - 0.04) if i == 0 or out[i - 1]['b'] < s['a'] - 0.6 else out[i - 1]['show_b'] if 'show_b' in out[i - 1] else s['a'], 2)
        s['show_b'] = round(nxt if nxt - s['b'] < 0.8 else s['b'] + 0.35, 2)
        if s['show_b'] - s['show_a'] < 0.45: s['show_b'] = round(s['show_a'] + 0.45, 2)
    for i in range(1, len(out)):
        if out[i]['show_a'] < out[i - 1]['show_b']: out[i]['show_a'] = out[i - 1]['show_b']
    if out and out[0]['a'] < 0.6: out[0]['show_a'] = 0.0  # H7：第 0 帧就有字幕
    if end: out[-1]['show_b'] = min(out[-1]['show_b'], end)
    return out

def srt(subs):
    f = lambda t: f'{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int(round(t%1*1000)) % 1000:03d}'
    return '\n'.join(f"{i+1}\n{f(s['show_a'])} --> {f(s['show_b'])}\n{s['text']}\n" for i, s in enumerate(subs))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--cards', required=True); ap.add_argument('--words'); ap.add_argument('--silences')
    ap.add_argument('--out-json', required=True); ap.add_argument('--out-srt'); ap.add_argument('--out-ts'); ap.add_argument('--end', type=float)
    A = ap.parse_args(); cards = json.load(open(A.cards)); cards = cards['cards'] if isinstance(cards, dict) else cards
    subs = build(cards, json.load(open(A.words)) if A.words else None, load_sil(A.silences), A.end)
    bad = [s for s in subs if any(ch in s['text'] for ch in '，。；：、,;') or vis_len(s['text']) > MAX_CHARS + 1.5]
    if bad: raise SystemExit(f'一句一字幕校验失败: {bad[:3]}')
    json.dump(subs, open(A.out_json, 'w'), ensure_ascii=False, indent=0)
    if A.out_srt: open(A.out_srt, 'w').write(srt(subs))
    if A.out_ts: open(A.out_ts, 'w').write('// 由 science-studio/scripts/subs/oneline.py 生成：一句一字幕\nexport const SUBS: {text:string;a:number;b:number;show_a:number;show_b:number}[] = ' + json.dumps([{k: s[k] for k in ('text','a','b','show_a','show_b')} for s in subs], ensure_ascii=False) + ';\n')
    print(f'{len(cards)} 卡 → {len(subs)} 句；最长 {max(vis_len(s["text"]) for s in subs):.1f} 字')
