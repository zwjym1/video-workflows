#!/usr/bin/env bash
# 盒子 → 用户 PC 大文件传输（CopyFromBox ≥30 MB 会失败）：切成 ≤4 MB 分块 + sha256 清单
# 用法: split_for_pc.sh <文件> [块大小=4M]  → <文件>.parts/<名>.partNN + SHA256.txt
# 然后逐块 CopyFromBox 到 PC 同一目录，在 PC 上运行 merge_on_pc.ps1。
set -euo pipefail
f="$1"; sz="${2:-4M}"; d="$f.parts"; n=$(basename "$f")
mkdir -p "$d"; split -b "$sz" -d -a 2 "$f" "$d/$n.part"
(cd "$(dirname "$f")" && sha256sum "$n") | awk '{print $1}' > "$d/SHA256.txt"
ls "$d" | wc -l | xargs echo "parts+manifest:"; cat "$d/SHA256.txt"
