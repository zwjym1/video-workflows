cd /workspace/science-studio/episodes/ai101_ep01_hallucination/production/full_v5
python3 final.py
python3 - <<'PY'
L=[l for l in open('subs.ass') if l.startswith('Dialogue')];o=[]
f=lambda s:'%02d:%02d:%06.3f'%(int(s.split(':')[0]),int(s.split(':')[1]),float(s.split(':')[2]))
for i,l in enumerate(L):
    import re
    p=l.split(',',9);p[9]=re.sub(r'\{[^}]*\}','',p[9]);o.append(f"{i+1}\n{f(p[1]).replace('.',',')} --> {f(p[2]).replace('.',',')}\n{p[9].strip()}\n")
open('full_v5.srt','w').write('\n'.join(o))
PY
cp full_v5.srt ../
cd .. && python3 sync_check.py full_v5 | tail -1
cd full_v5 && python3 /workspace/science-studio/tools/qc/final_check.py --video ../full_v5.mp4 --srt full_v5.srt --grid beat_grid.json --dur 150 180 --spec landscape --lufs -14 --voice-start 0.36 --sub-band 940 1070 --out qc_final | grep "^|"
echo ALLDONE
