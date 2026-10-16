"""v3 test segments narration. Reuses narration-fish.synthesize (key from env only); new filenames."""
import importlib.util,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('nf',ROOT/'scripts/narration-fish.py');nf=importlib.util.module_from_spec(spec);spec.loader.exec_module(nf)
TEXT={
 'v3-cauchy':'一八四七年，柯西写下一个朴素的想法：让函数不断变小。今天的梯度下降，思路就能追溯到这里。',
 'v3-chalk':'同一个起点，同样走三步。步子太小，误差还剩一点一六五；步子太大，冲过了头，变成二点五五一；步子合适，只剩零点零五五。',
}
for k in (sys.argv[1:] or TEXT): nf.synthesize(k,TEXT[k])
