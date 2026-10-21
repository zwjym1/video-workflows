#!/usr/bin/env bash
# 渲后硬质检（workflow_spec §1.1-3 / production_config「渲后质检」）
# 用法: qc_render.sh <成片.mp4> [fps=30] [接缝秒,逗号分隔，如 4.0,12.5]
# 输出到 stdout，用 > projects/<EP>/review/qc_vN.md 保存。只做机检；抽帧看字幕出框/错字交 qoder Flash（≤5 张/次）。
set -euo pipefail
f="$1"; fps="${2:-30}"; seams="${3:-}"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" | tr -d ",\n")
nb=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$f" | tr -d ",\n")
exp=$(python3 -c "print(round($dur*$fps))")
echo "# QC $(basename "$f")  $(date '+%F %T %Z')"
echo "- 时长 ${dur}s；帧数 $nb（期望约 $exp @${fps}fps）$([ $((nb-exp)) -le 2 ] && [ $((exp-nb)) -le 2 ] && echo ✓ || echo '✗ 帧数不符')"
echo "- 黑场（blackdetect d≥0.1s）："; ffmpeg -hide_banner -nostats -i "$f" -vf blackdetect=d=0.1:pix_th=0.05 -an -f null - 2>&1 | rg -o "black_start:\S+ black_end:\S+" | sed 's/^/  - /' || echo "  - 无"
echo "- 冻帧（freezedetect d≥1s）："; ffmpeg -hide_banner -nostats -i "$f" -vf freezedetect=n=0.003:d=1 -an -f null - 2>&1 | rg -o "freeze_(start|end): \S+" | paste - - | sed 's/^/  - /' || echo "  - 无"
echo "- 响度（目标约 −16 LUFS，真峰 ≤ −1.5 dBTP）："
ffmpeg -hide_banner -nostats -i "$f" -vn -af ebur128=peak=true -f null - 2>&1 | rg -A20 "^\[Parsed_ebur128.*Summary" | rg "I:|Peak:" | sed 's/^ */  - /'
if [ -n "$seams" ]; then echo "- 接缝 ±0.1s 峰值（查爆音）："
  for s in ${seams//,/ }; do a=$(python3 -c "print(max(0,$s-0.1))")
    pk=$(ffmpeg -hide_banner -nostats -ss "$a" -t 0.2 -i "$f" -vn -af astats=metadata=0 -f null - 2>&1 | rg "Peak level dB" | tail -1 | awk '{print $NF}')
    echo "  - ${s}s: peak ${pk} dBFS"; done; fi
