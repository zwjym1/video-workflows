"""从 v3.json + V3 源码收集所有用到的字，子集化 Noto Sans CJK SC Bold → public/v3/fonts/NotoSansSC-Bold-v3.otf"""
import json, re, subprocess, glob
from fontTools.ttLib import TTCollection
R = "/workspace/iphone-fake/v2/remotion"
d = json.load(open(f"{R}/src/v3/data/v3.json"))
chars = set(d["title"])
def walk(x):
    if isinstance(x, str): chars.update(x)
    elif isinstance(x, dict): [walk(v) for k, v in x.items() if k not in ("src", "file", "k", "kind", "id", "enter", "color", "accent", "world", "type")]
    elif isinstance(x, list): [walk(v) for v in x]
import os
for jp in (f"{R}/src/v3/data/v3.json", f"{R}/src/v3d/data/v3d.json", f"{R}/src/v3e/data/v3e.json", f"{R}/src/v3f/data/v3f.json"):   # V3 与 V3d 共用一个字体子集（并集）
    if not os.path.exists(jp): continue
    d = json.load(open(jp)); chars.update(d["title"])
    walk(d["subs"]); walk([s["ov"] for s in d["shots"]]); walk([s["src"] for s in d["shots"] if s["src"]])
for p in glob.glob(f"{R}/src/v3/*.tsx") + glob.glob(f"{R}/src/v3d/*.tsx") + glob.glob(f"{R}/src/v3e/*.tsx") + glob.glob(f"{R}/src/v3f/*.tsx"):
    for m in re.findall(r"[\u3000-\u9fff\uff00-\uffef]+", open(p).read()): chars.update(m)
chars.update("0123456789%.,:;!?@#()[]+-/·✓…「」『』 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz①②")
ttc = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
idx = [i for i, f in enumerate(TTCollection(ttc).fonts) if "SC" in f["name"].getDebugName(1)][0]
open("/tmp/v3chars.txt", "w").write("".join(sorted(chars)))
subprocess.run(["pyftsubset", ttc, f"--font-number={idx}", "--text-file=/tmp/v3chars.txt", f"--output-file={R}/public/v3/fonts/NotoSansSC-Bold-v3.otf", "--layout-features=*", "--no-hinting"], check=True)
print("font idx", idx, "chars", len(chars))
