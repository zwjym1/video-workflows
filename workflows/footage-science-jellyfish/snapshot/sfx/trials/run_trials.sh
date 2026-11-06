#!/bin/bash
# 候选 BGM 试混 + bgmfit：每首按自己的强拍重新吸附切点
cd /workspace/science-studio/projects/EP-20261029-01/sfx
PY=/workspace/.venv-dy/bin/python; A=../audio
run(){ tag=$1; f=$2; off=$3; title=$4; author=$5; id=$6; T=trials/$tag; mkdir -p $T
  BGM=$(readlink -f "$f") BGM_OFF=$off OUT=$T/cuts.json WRITE_TS=0 $PY snap_v2.py > $T/snap.log
  CUTS=$T/cuts.json OUTDIR=$T STEM=$T BGM_TITLE="$title" BGM_AUTHOR="$author" BGM_ID=$id $PY mix_v2.py > $T/mix.log 2>&1
  cuts=$($PY -c "import json;print(','.join(str(t) for n,t in json.load(open('$T/cuts.json'))['cuts'] if t>0))")
  (cd /workspace/science-studio/tools/review && $PY lib/bgmfit.py --audio ../../projects/EP-20261029-01/sfx/$T/mix.wav --cuts $cuts --bgm-stem ../../projects/EP-20261029-01/sfx/$T/stem_bgm.wav --vo-stem ../../projects/EP-20261029-01/sfx/$T/stem_vo.wav --out ../../projects/EP-20261029-01/sfx/$T/bgmfit.json > /dev/null 2>&1)
  echo "$tag $($PY -c "import json;d=json.load(open('$T/bgmfit.json'));print(d['score'],d['subscores'],d.get('tempo_bpm'),d.get('mode'))")"
}
run cur  "$A/bgm/02_一切都在变好（生命力BGM）.mp3" 0.5 "一切都在变好（生命力BGM）" "Martins Garix" 7552893524178733082
#run ditto "$A/bgm2/01_ditto(氛围感).mp3" 9.89 "ditto(氛围感)" "@天子" 7543081193115584539
#run hwm "$A/bgm2/02_here_with_me_(Tove_Ball_Remix).mp3" 1.0 "here with me (Tove Ball Remix)" "Tove Ball" 7439986145566492735
#run heroes "$A/bgm2/03_Heroes_3.mp3" 1.0 "Heroes 3" "VZEUS" 7592565700519020560
#run proof "$A/bgm2/04_Proof(Slowed).mp3" 0.9 "Proof(Slowed)" "GOLD999" 7604414083081996298
wait
