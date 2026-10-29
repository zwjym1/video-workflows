#!/usr/bin/env python3
"""渲染前结构闸门（秒级，不渲染、不调模型）。在 Remotion 渲染之前跑，挡掉审片官最常打回的结构问题。

来源：EP-20261029-01 火箭水母云 v5→v6h 共 8 轮返修，其中 v6c/v6d 被打回的「c04 0.7s 一闪」「4.305 切在『箭』字中间」
都能在渲染前用切点表 + 字级时间查出来，不需要等 75 s 渲染 + 5–10 min 审片。

输入（都是工程里已有的文件）：
  --cuts   design_cuts.json：{"cuts":[秒...], "names":[...]}，或 sfx/cuts_v2.json：{"cuts":[[name,秒],...], "total":秒}
  --words  字级时间：cards_timed_*.json（[{text,a,b,chars:[[字,a,b],...]}]）或审片工具 asr.json（[{a,b,text,words:[[字,a,b]]}]）
  --total  成片时长（秒；cuts_v2.json 里有 total 时可省）
  --events 可选：贴纸/戳/描线等「信息点」时间表 JSON：[{"t":秒,"what":"太原·起飞"}...]
规则（阈值可用参数改；默认值来自本期返修记录）：
  H1 首个切点必须是 0（第 0 帧就是正片画面）
  H2 前 --hook-end 秒（默认 10）内任何镜头时长 < --min-shot（默认 0.9 s）→ FAIL（v6c c04 0.695 s 被判「一闪」）
  H3 前 --hook-end 秒内，切点落在一个字的发声区间内部（距字头/字尾都 > --word-margin，默认 0.04 s）→ WARN（v6c 4.305 切在「箭」字中间）
     只查开头：正片中段按拍点切进字里很常见，不报。字级时间必须对应最终配音版本（用审片工具对成片跑出的 asr.json 最稳）。
  H4 3–10 s 窗口里，相邻两个「信息变化」（切点或 --events）间隔 > --max-gap（默认 1.6 s）→ WARN（v6e/v6f「6.2–6.8 只有灰弧不动」）
  H5 最后一个切点到片尾 < --min-shot → FAIL；口播结束晚于片尾 → FAIL
  H6 镜头名重复相邻（同一素材被切成两段）→ WARN
退出码：0 全部通过；1 有 FAIL；2 输入有误。WARN 不挡渲染，但要在返修单里写明为什么保留。
用法：
  python3 structure_gate.py --cuts review/design_cuts.json --words vo/cards_timed_v4.json --total 51.536 [--events review/events.json] [--json out.json]
"""
import argparse, json, sys

def load_cuts(p, total):
    d = json.load(open(p, encoding='utf-8'))
    if isinstance(d.get('cuts', [None])[0], list):
        names = [c[0] for c in d['cuts']]; cuts = [float(c[1]) for c in d['cuts']]
    else:
        cuts = [float(x) for x in d['cuts']]; names = d.get('names') or [f'shot{i+1:02d}' for i in range(len(cuts))]
    total = total or d.get('total') or d.get('total_s')
    if total is None: sys.exit('需要 --total（切点表里没有 total）')
    return cuts, names, float(total)

def load_words(p):
    if not p: return []
    d = json.load(open(p, encoding='utf-8')); out = []
    for seg in d:
        for w in seg.get('chars') or seg.get('words') or []:
            ch, a, b = w[0], float(w[1]), float(w[2])
            if ch.strip() and ch not in '，。？！、；：,.?!「」“”" ': out.append((ch, a, b))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cuts', required=True); ap.add_argument('--words'); ap.add_argument('--total', type=float)
    ap.add_argument('--events'); ap.add_argument('--json')
    ap.add_argument('--min-shot', type=float, default=0.9); ap.add_argument('--hook-end', type=float, default=10.0)
    ap.add_argument('--word-margin', type=float, default=0.04); ap.add_argument('--max-gap', type=float, default=1.6)
    ap.add_argument('--win', default='3,10', help='H4 检查窗口，默认 3,10')
    a = ap.parse_args()
    try:
        cuts, names, total = load_cuts(a.cuts, a.total); words = load_words(a.words)
        events = json.load(open(a.events, encoding='utf-8')) if a.events else []
    except Exception as e:
        print('输入有误：', e); sys.exit(2)
    R = []
    def add(level, rule, msg): R.append(dict(level=level, rule=rule, msg=msg))
    if abs(cuts[0]) > 1e-6: add('FAIL', 'H1', f'第一个切点是 {cuts[0]}s，不是 0')
    bounds = cuts + [total]
    for i, n in enumerate(names):
        dur = bounds[i + 1] - bounds[i]
        if dur <= 0: add('FAIL', 'H0', f'{n} 时长 {dur:.3f}s（切点没排好序）'); continue
        if bounds[i] < a.hook_end and dur < a.min_shot:
            add('FAIL', 'H2', f'{n} {bounds[i]:.3f}–{bounds[i+1]:.3f} 只有 {dur:.3f}s < {a.min_shot}s（前 {a.hook_end:g}s 内会被看成一闪）')
        if i and names[i - 1].split('_')[0] == n.split('_')[0] and names[i-1] == n: add('WARN', 'H6', f'{n} 与上一镜同名')
    if total - cuts[-1] < a.min_shot: add('FAIL', 'H5', f'最后一镜只有 {total - cuts[-1]:.3f}s')
    if words and words[-1][2] > total + 1e-3: add('FAIL', 'H5', f'口播结束 {words[-1][2]:.3f}s 晚于片尾 {total:.3f}s')
    for i, c in enumerate(cuts[1:], 1):
        if c >= a.hook_end: break
        for ch, wa, wb in words:
            if wa + a.word_margin < c < wb - a.word_margin:
                add('WARN', 'H3', f'切点 {c:.3f}s（进 {names[i]}）落在「{ch}」{wa:.2f}–{wb:.2f} 中间；挪到 {wa:.2f} 或 {wb:.2f} 附近的气口')
                break
    w0, w1 = (float(x) for x in a.win.split(','))
    marks = sorted([c for c in cuts if w0 <= c <= w1] + [float(e['t']) for e in events if w0 <= float(e['t']) <= w1] + [w0, w1])
    for x, y in zip(marks, marks[1:]):
        if y - x > a.max_gap: add('WARN', 'H4', f'{x:.2f}–{y:.2f}s 共 {y-x:.2f}s 没有新的切点/贴纸/动效（>{a.max_gap}s），3–10s 划走风险')
    nf = sum(r['level'] == 'FAIL' for r in R); nw = sum(r['level'] == 'WARN' for r in R)
    print(f'结构闸门：{len(names)} 镜，时长 {total:.3f}s，FAIL {nf}，WARN {nw}')
    for r in R: print(f"  [{r['level']}] {r['rule']} {r['msg']}")
    if not R: print('  全部通过')
    if a.json: json.dump(dict(fails=nf, warns=nw, items=R), open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.exit(1 if nf else 0)

if __name__ == '__main__':
    main()
