#!/usr/bin/env bash
# 盒子桌面录屏：ffmpeg x11grab → <ep>/rec/<name>.mp4 （1920x1080 30fps，H.264 CRF18）
# 用法:
#   record_box.sh start <episode_dir> <name> （可选 OFF=x,y SIZE=WxH 环境变量）
#   record_box.sh stop  <episode_dir> <name>
#   record_box.sh once  <episode_dir> <name> <秒数>   # 定时录
# 同时记录 <name>.cursor.tsv（每 50ms 鼠标坐标/按键，供后期加点击波纹）
set -euo pipefail
cmd=$1; ep=$2; name=$3; D=${DISPLAY:-:0}; out="$ep/rec"; mkdir -p "$out"
off=${OFF:-0,0}; size=${SIZE:-1920x1080}   # 区域用环境变量 OFF=x,y SIZE=WxH
pidf="$out/.$name.pid"; cpf="$out/.$name.cpid"
log_cursor(){ while true; do eval "$(xdotool getmouselocation --shell 2>/dev/null)"; echo -e "$(date +%s.%N)\t$X\t$Y" ; sleep 0.05; done >> "$out/$name.cursor.tsv"; }
rec(){ ffmpeg -v error -y -f x11grab -draw_mouse 1 -framerate 30 -video_size "$size" -i "$D+$off" \
      -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$@" "$out/$name.mp4"; }
case $cmd in
 start) : > "$out/$name.cursor.tsv"; log_cursor & echo $! > "$cpf"
        (rec < /dev/null) & echo $! > "$pidf"; echo "recording $out/$name.mp4 (pid $(cat $pidf))";;
 stop)  pkill -INT -P "$(cat $pidf)" ffmpeg 2>/dev/null || kill -INT "$(cat $pidf)" 2>/dev/null || true
        kill "$(cat $cpf)" 2>/dev/null || true; sleep 1.5; rm -f "$pidf" "$cpf"; ls -la "$out/$name.mp4";;
 once)  : > "$out/$name.cursor.tsv"; log_cursor & cp=$!; rec -t "$4"; kill $cp; ls -la "$out/$name.mp4";;
 *) echo "start|stop|once"; exit 1;;
esac
