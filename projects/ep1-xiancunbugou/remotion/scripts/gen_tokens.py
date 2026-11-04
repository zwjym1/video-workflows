#!/usr/bin/env python3
"""从源码里扫出全部 hex 色值，生成 src/theme/tokens.ts（画材基准表）。
   新增写死颜色时跑一次，保证 tokens.ts 不漏色。
   用法：python3 scripts/gen_tokens.py [--check]"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAP = json.loads((ROOT / 'scripts/_map.json').read_text())
FILES = ['src/kit.tsx','src/W.tsx','src/Motion.tsx','src/Chapters.tsx','src/Episode.tsx',
         'src/Root.tsx','src/Cover.tsx','src/sprites.tsx','src/Sprite.tsx',
         'src/lib/PixelBuddy.tsx','src/lib/Accessories.tsx']

def norm(h):
    h = h.replace('#','').upper()
    if len(h) == 3: h = ''.join(c*2 for c in h)
    return '#' + h[:6]

def main(check=False):
    tok = {}
    for h, name in MAP.items():
        tok.setdefault(name, norm(h))
    body = '\n'.join(f"  '{k}': '{tok[k]}'," for k in sorted(tok))
    out = f'''/**
 * 材质色板（Material Tokens）
 * ------------------------------------------------------------------
 * 像素道具（显卡、仓库、机柜、工作台、小人）是拿画笔一格一格画的，
 * 它们的颜色不是「语义色」，而是画材本身 —— 所以单独一层。
 *
 * BASE_MATERIALS 是 pixelDark 皮肤下的原始色，其它皮肤从这里推导，
 * 保证「换皮不换构图」也「换皮不丢画材层次」。
 * 本文件由 scripts/gen_tokens.py 生成（共 {len(tok)} 个 token）。
 */
export const BASE_MATERIALS = {{
{body}
}} as const;

export type MaterialToken = keyof typeof BASE_MATERIALS;
export const MATERIAL_NAMES = Object.keys(BASE_MATERIALS) as MaterialToken[];
'''
    p = ROOT / 'src/theme/tokens.ts'
    if check:
        print('current tokens.ts matches generator' if p.read_text() == out else 'tokens.ts is STALE — rerun gen_tokens.py')
        return
    p.write_text(out)
    print(f'wrote {p} with {len(tok)} tokens')

if __name__ == '__main__':
    main('--check' in sys.argv)
