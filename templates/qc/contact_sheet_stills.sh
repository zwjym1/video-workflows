#!/bin/bash
# usage: stills.sh frame1 frame2 ...  (bundle first)
cd /workspace/optogenetics/remotion && npx remotion bundle src/index.tsx --out-dir=/tmp/opto_bundle >/dev/null 2>&1
for f in "$@"; do npx remotion still /tmp/opto_bundle OptoHook /workspace/optogenetics/render/stills/f$(printf %03d $f).jpg --frame=$f --gl=angle --scale=0.5 >/dev/null 2>&1 || echo FAIL $f; done
cd /workspace/optogenetics/render/stills && ffmpeg -v error -y $(for f in "$@"; do echo -i f$(printf %03d $f).jpg; done) -filter_complex "$(n=0; for f in "$@"; do printf "[$n:v]scale=270:480,drawtext=text='f$f':x=6:y=6:fontsize=20:fontcolor=yellow[v$n];"; n=$((n+1)); done; for i in $(seq 0 $(($#-1))); do printf "[v$i]"; done; echo "xstack=inputs=$#:layout=$(python3 -c "
import sys;n=$#;c=min(n,6);print('|'.join(f'{(i%c)*270}_{(i//c)*480}' for i in range(n)))"):fill=black")" grid.jpg
