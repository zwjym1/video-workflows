#!/usr/bin/env python3
"""给 STATE.md 记一行带时间的阶段日志（UTC+8），供下次效率审计算各阶段用时。

用法：
  python3 stage_log.py <STATE.md> <阶段> <start|done|note> [说明...]
  例：python3 stage_log.py STATE.md E start "配音 v4"
      python3 stage_log.py STATE.md E done  "vo_v4 51.4s"
  汇总：python3 stage_log.py <STATE.md> --report   # 列出每个阶段 start→done 用时

只追加，不改已有内容；日志写在 STATE.md 末尾的「## 阶段计时」小节（没有就新建）。
"""
import re, sys
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
HEAD = '## 阶段计时（UTC+8，stage_log.py 自动追加）'
LINE = re.compile(r'^- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\S+) \| (start|done|note) \|(.*)$')

def report(path):
    starts, rows = {}, []
    for ln in open(path, encoding='utf-8'):
        m = LINE.match(ln.rstrip('\n'))
        if not m: continue
        t = datetime.strptime(m[1], '%Y-%m-%d %H:%M:%S'); st, kind = m[2], m[3]
        if kind == 'start': starts[st] = t
        elif kind == 'done' and st in starts:
            rows.append((st, starts.pop(st), t))
    for st, a, b in rows:
        print(f'{st}\t{a:%m-%d %H:%M}→{b:%H:%M}\t{(b - a).total_seconds() / 60:.1f} min')
    for st, a in starts.items():
        print(f'{st}\t{a:%m-%d %H:%M}→（未结束）')

def main():
    if len(sys.argv) >= 3 and sys.argv[2] == '--report':
        return report(sys.argv[1])
    if len(sys.argv) < 4 or sys.argv[3] not in ('start', 'done', 'note'):
        print(__doc__); sys.exit(2)
    path, stage, kind, note = sys.argv[1], sys.argv[2], sys.argv[3], ' '.join(sys.argv[4:])
    now = datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')
    text = open(path, encoding='utf-8').read() if __import__('os').path.exists(path) else ''
    add = '' if HEAD in text else ('\n' if text and not text.endswith('\n') else '') + f'\n{HEAD}\n'
    with open(path, 'a', encoding='utf-8') as f:
        f.write(add + f'- {now} | {stage} | {kind} | {note}\n')
    print(f'{now} {stage} {kind} {note}')

if __name__ == '__main__':
    main()
