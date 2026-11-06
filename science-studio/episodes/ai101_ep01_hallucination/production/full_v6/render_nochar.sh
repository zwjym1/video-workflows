cd /workspace/science-studio/episodes/ai101_ep01_hallucination/production/full_v6/nochar
rm -f part_*.mp4
for f in timeline.json mouth.npz mouth_env.npz beat_grid.json picture.py;do cp ../$f .;done
N=$(python3 -c "import json;print(int(json.load(open('timeline.json'))['dur']*30))");S=$(( (N+7)/8 ))
for i in 0 1 2 3 4 5 6 7; do NOCHAR=1 python3 picture.py $((i*S)) $(((i+1)*S)) > log_$i.txt 2>&1 & done; wait
ls part_*.mp4 | sort | sed "s/.*/file '&'/" > parts.txt
ffmpeg -y -v error -f concat -safe 0 -i parts.txt -c copy nochar.mp4
ffmpeg -y -v error -i nochar.mp4 -i ../../full_v6.mp4 -map 0:v -map 1:a -c copy nochar_a.mp4
python3 /workspace/science-studio/tools/qc/final_check.py --video nochar_a.mp4 --grid beat_grid.json --dur 150 180 --spec landscape --lufs -14 --sub-band 940 1070 --no-frame-subs --out qc_nochar 2>&1 | grep "^|"
echo NCDONE
