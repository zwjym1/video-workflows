"""规则 v2：在旧总分上按硬指标扣分（不否决），网感分单独算。规则见 config/rules_v2.md。
用法（独立）：python lib/rules_v2.py --id <id>；merge.py 默认会调用 apply()（--rules v1 时不调用）。"""
import json, os, argparse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _j(p):
    try: return json.load(open(p))
    except Exception: return None

def hard(M, orient):
    D = []; NA = []
    def add(k, ded, msg): D.append(dict(k=k, deduct=round(ded, 2), msg=msg))
    L = M.get('lufs'); tgt = -14 if orient == 'landscape' else -16
    if L is None: NA.append('H1 响度')
    else:
        dv = abs(L - tgt); add('H1', 0 if dv <= 1 else (2 if dv <= 2 else 4), f'响度 {L} LUFS，目标 {tgt}±1（{orient}）')
    b = M.get('beats')
    if not b: NA.append('H2 拍点')
    else:
        r = b['rate'] * 100; add('H2', 0 if r >= 85 else min(5, (85 - r) / 5), f"拍点命中 {b['hits']}/{b['onsets']}={r:.1f}%（随机基线 {b.get('chance',0)*100:.0f}%）")
    v = M.get('voice')
    if not v: NA.append('H3 音色')
    else:
        n = sum(len(x.get('outliers', [])) for x in v.values()); cmin = min(x['cos_min'] for x in v.values())
        add('H3a', min(3, max(0, n - 2)), f"离群句 {n}（各角色余弦最小 {cmin}）")
        if 'O' in v: f = v['O']['f0_median']; add('H3b', 0 if f < 170 else 3, f'O 中位 F0 {f} Hz（<170）')
    ls = M.get('lipsync')
    if ls is None: NA.append('H4 口型')
    else:
        e = ls['max_err']; add('H4', 0 if e <= 0.08 else min(3, -(-(e - 0.08) // 0.04)), f"口型最大误差 {e}s（来源：{ls.get('source','?')}）")
    p = M.get('plus1')
    if p is None: NA.append('H5 +1 读法')
    else:
        bad = [x for x in p if not x['ok']]; add('H5', min(4, 2 * len(bad)), f"「+1」{len(p)} 处，读错 {len(bad)}" + ('：' if bad else '') + '；'.join(f"{x['t']}s 听成「{x['heard']}」" for x in bad))
    s = M.get('subs')
    if not s: NA.append('H6 字幕')
    else:
        add('H6a', min(3, 0.5 * s['over16']), f"字幕 >16 字 {s['over16']} 卡（最长 {s['maxlen']}）")
        if s.get('top_layer') is None: NA.append('H6b 字幕最上层')
        else: add('H6b', 0 if s['top_layer'] else 3, '字幕在最上层' if s['top_layer'] else f"字幕被遮挡：{s.get('top_note','')}")
    r = M.get('rhythm')
    if r:   # 对照项：只报数字，不扣分
        u, c = r.get('unit_s'), r.get('cps')
        if u is not None: add('R7a', 0, f'【对照，不扣分】画面单元平均 {u}s（阿柠约 4）')
        if c is not None: add('R7b', 0, f'【对照，不扣分】语速 {c} 字/秒（阿柠约 6.5）')
    tot = min(15, sum(x['deduct'] for x in D))
    return D, NA, round(tot, 2)

def netgan(N):
    if not N: return None
    w = {'done': 1, 'partial': 0.5, 'miss': 0}; it = N.get('items', [])
    if not it: return None
    s = 100 * sum(w.get(x['status'], 0) for x in it) / len(it) - (10 if N.get('overstuffed') else 0)
    return dict(score=round(max(0, s), 1), n=len(it), done=sum(x['status'] == 'done' for x in it), partial=sum(x['status'] == 'partial' for x in it), miss=sum(x['status'] == 'miss' for x in it), overstuffed=bool(N.get('overstuffed')), note='单独报告，不计入总分')

def apply(out, odir):
    M = _j(os.path.join(odir, 'measure_v2.json')) or {}
    D, NA, tot = hard(M, M.get('orientation', 'portrait'))
    out['total_v1'] = out['total']; out['total'] = round(out['total'] - tot, 1)
    out['rules'] = 'v2'; out['hard_v2'] = dict(deductions=D, not_measured=NA, total_deduct=tot, cap=15, rule='config/rules_v2.md：硬指标不达标只扣分，不否决')
    out['netgan_v2'] = netgan(_j(os.path.join(odir, 'netgan.json')))
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--id', required=True); a = ap.parse_args()
    od = os.path.join(ROOT, 'out', a.id); v = json.load(open(os.path.join(od, 'verdict.json')))
    if v.get('rules') == 'v2': v['total'] = v.get('total_v1', v['total'])
    print(json.dumps(apply(v, od), ensure_ascii=False, indent=1)[:3000])
