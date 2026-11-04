#!/usr/bin/env python3
"""第二遍：替换字符串字面量里的 hex（fill="…" / filter:'drop-shadow(… #1E1B25 …)' / '4px dashed #E07A3A'）。
   只处理引号包住、且内容里出现 hex 的片段。"""
import json, re, pathlib
MAP = json.loads(pathlib.Path(__file__).with_name('_map.json').read_text())
BY = {}
for h, tok in MAP.items():
    n = h.lstrip('#')
    if len(n) == 8: n = n[:6]
    BY['#' + n.lower()] = tok
    if len(n) == 3: BY['#' + ''.join(c*2 for c in n).lower()] = tok

FILES = ['src/kit.tsx','src/W.tsx','src/Motion.tsx','src/Chapters.tsx','src/Episode.tsx',
         'src/Root.tsx','src/Cover.tsx','src/sprites.tsx','src/Sprite.tsx',
         'src/lib/PixelBuddy.tsx','src/lib/Accessories.tsx']

STR = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"' + r"|'([^'\\]*(?:\\.[^'\\]*)*)'")
HEX = re.compile(r'#([0-9A-Fa-f]{3,8})\b')

def main():
    n=0; miss=[]
    for f in FILES:
        p=pathlib.Path(f); src=p.read_text()
        def sub_str(mo):
            nonlocal n
            body = mo.group(1) if mo.group(1) is not None else mo.group(2)
            quote = '"' if mo.group(1) is not None else "'"
            if '#' not in body: return mo.group(0)
            def rh(m):
                nonlocal n
                tok = BY.get('#'+m.group(1).lower())
                if not tok: miss.append((f, m.group(0))); return m.group(0)
                n += 1
                return 'var(--m-%s)' % tok
            nb = HEX.sub(rh, body)
            return quote + nb + quote
        out = []
        for line in src.splitlines(keepends=True):
            st = line.lstrip()
            if st.startswith('//') or st.startswith('*') or st.startswith('/*'):
                out.append(line); continue
            out.append(STR.sub(sub_str, line))
        p.write_text(''.join(out))
    print('string hex replaced:', n, 'missed:', len(miss))
    for m in miss[:10]: print('  ?', m)

main()
