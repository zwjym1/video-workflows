#!/usr/bin/env python3
"""把源码里写死的 hex（CSS 与 SVG 两处）机械替换成主题变量 --m-<token>。
   映射见 src/theme/_map.json（由扫描生成，覆盖全部 110 个色值）。
   用法：python3 scripts/hex_to_tokens.py [--check]"""
import json, re, sys, pathlib

MAP = json.loads(pathlib.Path(__file__).with_name('_map.json').read_text())
BY_LOWER = {}
for h, tok in MAP.items():
    n = h.lstrip('#')
    if len(n) == 8: n = n[:6]
    BY_LOWER['#' + n.lower()] = tok
    if len(n) == 3: BY_LOWER['#' + ''.join(c * 2 for c in n).lower()] = tok

FILES = ['src/kit.tsx', 'src/W.tsx', 'src/Motion.tsx', 'src/Chapters.tsx', 'src/Episode.tsx',
         'src/Root.tsx', 'src/Cover.tsx', 'src/sprites.tsx', 'src/Sprite.tsx',
         'src/lib/PixelBuddy.tsx', 'src/lib/Accessories.tsx']

# 只替换字符串字面量里、或在 svg 属性值里的独立 hex；避免动到注释里的说明
PAT = re.compile(r"'#([0-9A-Fa-f]{3,8})'")

def main(check=False):
    total = 0; unmapped = []
    for f in FILES:
        p = pathlib.Path(f)
        if not p.exists(): continue
        src = p.read_text()
        def sub(mo):
            nonlocal total
            key = '#' + mo.group(1).lower()
            if len(mo.group(1)) == 8: key = key[:7]
            tok = BY_LOWER.get(key)
            if not tok:
                unmapped.append((f, mo.group(0))); return mo.group(0)
            total += 1
            return f"m('{tok}')"
        out = PAT.sub(sub, src)
        if not check and out != src:
            p.write_text(out)
    print(f"replaced {total} literals; unmapped {len(unmapped)}")
    for u in unmapped[:20]: print("  ?", u)

if __name__ == '__main__':
    main('--check' in sys.argv)
