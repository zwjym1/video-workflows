# 关键帧拼图（按 v3.json 自动取帧）：python3 sheet_v3c.py frames | <stillsDir> <out.jpg>
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
d = json.load(open("src/v3/data/v3.json")); FPS = d["fps"]; S = d["shots"]
K = [(0.10, "s01 0.1s"), (0.30, "s01 0.3s 跳切"), ((S[1]["t0"] + S[1]["t1"]) / 2, "s02"), ((S[2]["t0"] + S[2]["t1"]) / 2, "s03")]
for s in S:
    for o in s["ov"]:
        if o["k"] == "stamp" and not o.get("still"): K.append((o["t"] + 0.2, f"{s['id']} 首个红章"))
        if o["k"] == "split": K.append(((s["t0"] + s["t1"]) / 2 + 0.3, f"{s['id']} 左假右真"))
        if o["k"] == "qmark": K.append((o["t"] + 0.35, f"{s['id']} 设问"))
        c = o.get("circle") if o["k"] == "cursor" else (o if o["k"] == "dash" else None)
        if c: K.append((min(s["t1"] - 0.15, max(c["t"], s["t0"]) + 1.3), f"{s['id']} 圈选"))
K += [(d["total"] - 1.2, "结尾"), (d["total"] - 0.1, "最后一帧")]
K = sorted({round(t * FPS): (t, l) for t, l in K}.values())
if sys.argv[1] == "frames": print(" ".join(str(round(t * FPS)) for t, _ in K)); sys.exit()
src, out = sys.argv[1], sys.argv[2]
TW, TH, C = 560, 315, 4; rows = (len(K) + C - 1) // C
sheet = Image.new("RGB", (C * TW, rows * (TH + 30)), (24, 24, 24)); dr = ImageDraw.Draw(sheet)
f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 20, index=2)
for i, (t, lab) in enumerate(K):
    im = Image.open(os.path.join(src, f"f{round(t*FPS):04d}.png")).convert("RGB").resize((TW, TH))
    x, y = (i % C) * TW, (i // C) * (TH + 30); sheet.paste(im, (x, y + 30)); dr.text((x + 6, y + 3), f"{t:.2f}s {lab}", fill=(255, 220, 60), font=f)
sheet.save(out, quality=88); print(out, sheet.size, len(K))
