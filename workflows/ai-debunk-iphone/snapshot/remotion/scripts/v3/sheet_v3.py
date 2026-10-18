# 关键帧拼图：python3 sheet_v3.py <stillsDir> <out.png>
import sys, os
from PIL import Image, ImageDraw, ImageFont
K = [(0.10,"s01 0.1s 开场"),(0.30,"s01 0.3s 跳切后"),(1.60,"s02 第2刀"),(3.30,"s03 第3刀"),(5.55,"s04 首个红章 AI"),
 (7.60,"s05 左假右真①"),(9.80,"s06"),(12.80,"s07 左假右真②"),(14.80,"s08"),(17.50,"s09 @grok"),(19.60,"s10"),(22.50,"s11"),(24.80,"s12"),
 (26.20,"s13 问句14 问号+小官"),(28.20,"s13 虚线圈"),(29.60,"s14 圈 两组摄像头"),(32.00,"s15 圈 字是扭的"),(35.00,"s16 光标圈 OpenAI"),(36.60,"s17"),
 (38.90,"s18 左假右真③"),(40.40,"s19 问句22 问号+小官"),(42.80,"s19 圈 人不动"),(45.50,"s20 左假右真④ 圈"),(47.80,"s21 8000万播放"),
 (49.80,"s22 光标圈 AI 内容"),(50.90,"s23 光标圈 99.9%"),(52.60,"s24 99.9% 计数"),(54.20,"s25"),(56.50,"s26"),(58.80,"s27 问句32 问号"),
 (61.50,"s28"),(65.30,"s29 BBC 信源"),(69.00,"s30"),(71.00,"s31 结尾"),(72.60,"s31 最后一帧")]
if __name__ == "__main__" and sys.argv[1] == "frames":
    print(" ".join(str(round(t * 30)) for t, _ in K)); sys.exit()
d, out = sys.argv[1], sys.argv[2]
TW, TH, C = 640, 360, 4
rows = (len(K) + C - 1) // C
sheet = Image.new("RGB", (C * TW, rows * (TH + 34)), (24, 24, 24))
f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 22, index=2)
dr = ImageDraw.Draw(sheet)
for i, (t, lab) in enumerate(K):
    im = Image.open(os.path.join(d, f"f{round(t*30):04d}.png")).convert("RGB").resize((TW, TH))
    x, y = (i % C) * TW, (i // C) * (TH + 34)
    sheet.paste(im, (x, y + 34)); dr.text((x + 8, y + 4), f"{t:.2f}s  {lab}", fill=(255, 220, 60), font=f)
sheet.save(out); print(out, sheet.size)
