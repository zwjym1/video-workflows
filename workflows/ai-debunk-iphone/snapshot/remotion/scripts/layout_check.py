"""Remotion 检查帧排版检查 + 汇总图。
- 字幕层（all − nosub）：必须全部落在 y≥900，左右不出 40px 安全边，单行
- 其他 Remotion 叠加层（nosub − bare：弹幕/角标）：不得进入 y≥900 字幕区
- 底板本身已过 preview/compose.py 的 layout_check（标注不进字幕区）
输出 preview/sheets/remotion_layout_check.json + remotion_stills_check.png"""
import json, sys
from PIL import Image, ImageChops, ImageDraw, ImageFont
D = sys.argv[1] if len(sys.argv) > 1 else "/workspace/iphone-fake/v2/preview/remotion_stills"
SHEETS = "/workspace/iphone-fake/v2/preview/sheets"
idx = json.load(open(f"{D}/index.json"))
SUB_TOP = 900
def diffmask(a, b, th=24):
    d = ImageChops.difference(Image.open(a).convert("RGB"), Image.open(b).convert("RGB")).convert("L")
    return d.point(lambda v: 255 if v > th else 0)
res = {}
keys = sorted({j["name"][4:].rsplit("_", 1)[0] for j in idx if j["name"].startswith("key_")}, key=lambda s: (int(s[:2]), s))
for sid in keys:
    a, n, b = (f"{D}/key_{sid}_{v}.png" for v in ("all", "nosub", "bare"))
    issues = []
    sm = diffmask(a, n); bb = sm.getbbox()
    if bb:
        if bb[1] < SUB_TOP: issues.append(f"字幕层越过 y{SUB_TOP}: bbox={bb}")
        if bb[0] < 40 or bb[2] > 1880: issues.append(f"字幕超出左右安全边: bbox={bb}")
        if bb[3] - bb[1] > 140: issues.append(f"字幕疑似换行: h={bb[3]-bb[1]}")
    em = diffmask(n, b); zone = em.crop((0, SUB_TOP, 1920, 1080))
    cnt = sum(1 for v in zone.getdata() if v)
    if cnt > 50: issues.append(f"叠加层进入字幕区: {cnt}px bbox={zone.getbbox()}")
    res[sid] = {"subs_bbox": bb, "extras_bbox": em.getbbox(), "issues": issues}
json.dump(res, open(f"{SHEETS}/remotion_layout_check.json", "w"), ensure_ascii=False, indent=1)
bad = {k: v["issues"] for k, v in res.items() if v["issues"]}
print("layout issues:", bad if bad else "无")
# 汇总图：每镜关键帧一行 11 张；转场 a/b/c 三张一组
TW, TH = 384, 216
f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 22)
tiles = [(f"{D}/key_{s}_all.png", f"{s} 关键帧" + (" ⚠" if res[s]["issues"] else "")) for s in keys]
trs = sorted({j["name"][3:-2] for j in idx if j["name"].startswith("tr_")}, key=lambda s: (int(s[:2]), s))
for t in trs:
    for tag, lab in (("a", "尾"), ("b", "首"), ("c", "中")):
        tiles.append((f"{D}/tr_{t}_{tag}.png", f"{t} {lab}"))
cols = 12
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (TW + 8) + 8, rows * (TH + 36) + 8), "#202124")
d = ImageDraw.Draw(sheet)
for i, (p, lab) in enumerate(tiles):
    x = 8 + (i % cols) * (TW + 8); y = 8 + (i // cols) * (TH + 36)
    im = Image.open(p).convert("RGB").resize((TW, TH), Image.LANCZOS)
    sheet.paste(im, (x, y)); d.line([(x, y + int(TH * 900 / 1080)), (x + TW, y + int(TH * 900 / 1080))], fill="#00E5FF", width=1)
    d.text((x + 4, y + TH + 4), lab, font=f, fill="#FFD84A" if "关键" in lab else "#DDDDDD")
sheet.save(f"{SHEETS}/remotion_stills_check.png"); print(sheet.size)
