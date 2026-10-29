#!/usr/bin/env bash
# 盒 → PC 交付打包（通用版，取代每期手写 assemble_*.ps1）。只新建目录，不删除任何东西。
# 来源：EP-20261029-01 火箭水母云。CopyFromBox 写 D:\ 中文路径被拒，只能落到 C:\Users\Administrator\（PC 的 $HOME），
#       当晚为此临时写了 assemble_jelly/2/3、find_parts/2、assemble_final 共 6 个脚本（10:04–10:07）。这里一次做成通用的。
# 做法：
#   1) 每个文件切成 ≤ 块大小（默认 8M）的分块，分块名全 ASCII 且带期号前缀：<TAG>__f<序号>.partNN（不会和 $HOME 里别的文件撞名，也不会乱码）
#   2) 小文件（< 块大小）也改成 ASCII 名 <TAG>__f<序号>.part00，PC 端按 manifest 还原中文名
#   3) 生成 <TAG>__manifest.json（目标目录、原文件名、大小、整体 sha256、每块 sha256）
#   4) 生成 <TAG>__assemble.ps1（= assemble_from_home.ps1 + 默认参数，UTF-8 BOM，PowerShell 5.1/7 都能读中文）和 传输步骤.md
# 用法：
#   make_pc_bundle.sh <TAG> <PC目标目录> <输出目录> <文件1> [文件2 ...]
#   例：make_pc_bundle.sh jelly 'D:\编程\项目\视频制作\作品\2026-10-29_火箭水母云\发布' /workspace/xfer_jelly \
#         deliver/火箭水母云_成片_1080x1920.mp4 deliver/火箭水母云_封面_竖9x16_1080x1920.png deliver/火箭水母云_封面_横4x3_1440x1080.png
#   环境变量 CHUNK=8M 可改块大小（CopyFromBox 单文件 ≥30 MB 会失败；8M 已实测可用）。
set -euo pipefail
[ $# -ge 4 ] || { sed -n '2,16p' "$0"; exit 2; }
TAG="$1"; DEST="$2"; OUT="$3"; shift 3
[[ "$TAG" =~ ^[A-Za-z0-9_-]+$ ]] || { echo "TAG 只能用字母数字_-" >&2; exit 2; }
CHUNK="${CHUNK:-8M}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"
if ls "$OUT"/"${TAG}"__* >/dev/null 2>&1; then echo "输出目录里已有 ${TAG}__* 分块；换个 TAG 或换个空目录（本脚本不删除文件）" >&2; exit 3; fi
python3 - "$TAG" "$DEST" "$OUT" "$CHUNK" "$@" <<'PY'
import sys, os, json, hashlib, re
tag, dest, out, chunk, *files = sys.argv[1:]
m = re.fullmatch(r'(\d+)([KMG]?)', chunk.upper()); n = int(m.group(1)) * {'': 1, 'K': 1024, 'M': 1024**2, 'G': 1024**3}[m.group(2)]
man = dict(tag=tag, dest=dest, chunk=n, files=[])
for i, f in enumerate(files):
    data = open(f, 'rb').read(); parts = []
    for k in range(0, max(len(data), 1), n):
        b = data[k:k + n]; name = f'{tag}__f{i}.part{k // n:02d}'
        open(os.path.join(out, name), 'wb').write(b)
        parts.append(dict(name=name, size=len(b), sha256=hashlib.sha256(b).hexdigest()))
    man['files'].append(dict(name=os.path.basename(f), size=len(data), sha256=hashlib.sha256(data).hexdigest(), parts=parts))
json.dump(man, open(os.path.join(out, f'{tag}__manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
L = [f'# PC 传输步骤（{tag}；make_pc_bundle.sh 生成，勿手改）', '',
     f'目标目录：`{dest}`', '',
     '1. CopyFromBox 把下面每个文件传到 PC 的 `C:\\Users\\Administrator\\`（即 $HOME；不要传 D:\\，会被拒）：']
names = [p['name'] for fi in man['files'] for p in fi['parts']] + [f'{tag}__manifest.json', f'{tag}__assemble.ps1']
L += [f'   - `{os.path.join(out, x)}`' for x in names]
L += ['2. PC 上运行（只新建、不删除；分块和哈希不对会直接报错停下）：',
      f'   `powershell -NoProfile -ExecutionPolicy Bypass -File $HOME\\{tag}__assemble.ps1`',
      '3. 输出最后一行是 `DONE` 才算成功；成品清单：']
L += [f'   - {fi["name"]}  {fi["size"]} B  sha256 {fi["sha256"]}' for fi in man['files']]
L += ['4. 某块 HASH_FAIL：只重传那一块，再跑第 2 步。']
open(os.path.join(out, '传输步骤.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L))
PY
# assemble 脚本：模板 + 默认 TAG，写成 UTF-8 BOM
{ printf '\xEF\xBB\xBF'; sed "s/__DEFAULT_TAG__/${TAG}/" "$HERE/assemble_from_home.ps1" | sed '1s/^\xEF\xBB\xBF//'; } > "$OUT/${TAG}__assemble.ps1"
echo "OK → $OUT"
