"""整片 OCR：每秒 N 帧，tesseract eng+chi_sim（psm 11）。白名单：AI / 99.9% / iPhone / 数字 + 我们自己的中文。"""
import sys, os, re, json, subprocess, glob
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
V, OUT = sys.argv[1], sys.argv[2]; FPS = sys.argv[3] if len(sys.argv) > 3 else "3"
os.makedirs(f"{OUT}/fr", exist_ok=True)
(None if os.environ.get("SKIPX") else subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", V, "-vf", f"fps={FPS}", f"{OUT}/fr/%05d.png"], check=True))
BAN = ["BBC", "Verify", "VERIFY", "OpenAI", "Hive", "HIVE", "Instagram", "Annahar", "Grok", "grok", "Twitter", "推特", "外网", "外媒", "B站", "搬运号",
       "来源", "信源", "素材", "照片：", "半岛", "霍尔木兹", "海峡", "沉船", "事故", "战争", "封锁", "Social", "media", "GENERATED", "Generated", "Content", "JAL", "CARGO", "UNICEF", "@", "Likely", "POWERED"]
WL = {"ai", "iphone", "iphone18"}
def one(p):
    tsv = subprocess.run(["tesseract", p, "-", "-l", "eng+chi_sim", "--psm", "11", "tsv"], capture_output=True, text=True).stdout
    toks = []
    for ln in tsv.splitlines()[1:]:
        c = ln.split("\t")
        if len(c) >= 12 and c[11].strip(): toks.append((c[11].strip(), float(c[10])))
    full = "".join(t for t, _ in toks)
    hits = [b for b in BAN if b in full]
    eng = [t.strip(".,:;!?()[]「」") for t, cf in toks if cf >= 70 and re.fullmatch(r"[A-Za-z][A-Za-z\-]{2,}", t.strip(".,:;!?()[]「」")) and t.strip(".,:;!?()[]「」").lower() not in WL]
    return os.path.basename(p), hits, eng, full
fs = sorted(glob.glob(f"{OUT}/fr/*.png"))
with ThreadPoolExecutor(8) as ex: res = list(ex.map(one, fs))
fr = float(FPS)
rep = {"video": V, "frames": len(fs), "fps": FPS,
       "ban_hits": {f"{(int(f[:5]) - 1) / fr:.2f}s": h for f, h, _, _ in res if h},
       "english_tokens_conf70": {f"{(int(f[:5]) - 1) / fr:.2f}s": e for f, _, e, _ in res if e}}
json.dump(rep, open(f"{OUT}/ocr_report.json", "w"), ensure_ascii=False, indent=1)
print("frames", len(fs), "ban-hit frames", len(rep["ban_hits"]), "eng-token frames", len(rep["english_tokens_conf70"]))
for f, h in rep["ban_hits"].items(): print("BAN", f, h)
print("ENG", Counter(t for e in rep["english_tokens_conf70"].values() for t in e).most_common(50))
for f, e in rep["english_tokens_conf70"].items(): print("  ", f, e)
