"""V3e 新素材：X 评论按原文排版（去掉头像栏/按钮栏），IG 截图只留内容区（去头像栏、按钮、播放键）。
只写新文件 public/v3/img/e_*.png，不覆盖 V3/V3d 用到的任何文件。"""
import sys, json
sys.path.insert(0, "/workspace/iphone-fake/v2/preview")
import compose as C
from PIL import Image, ImageDraw
import numpy as np, cv2
PUB = "/workspace/iphone-fake/v2/remotion/public/v3/img"; SS = "/workspace/iphone-fake/v2/assets/screenshots"
META = {}

def xcard(name, body, hl=None, date="10 月 18 日"):
    w, h = 820, 250
    card = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle([4, 4, w, h], radius=18, fill="#FFFFFF", outline=C.YELLOW, width=5)
    d.rounded_rectangle([26, 22, 252, 56], radius=8, fill=C.INK)
    d.text((38, 26), "X 评论，文字原样", font=C.font(22, True), fill=C.YELLOW)
    d.text((270, 30), f"原帖评论区 · {date}", font=C.font(18), fill="#888")
    fb = C.font(64, True); x0, y0 = 34, 100
    d.text((x0, y0), body, font=fb, fill=C.INK)
    bb = d.textbbox((x0, y0), body, font=fb)
    m = dict(size=card.size, body=bb)
    if hl:
        i = body.index(hl); pre = body[:i]
        hx0 = x0 + d.textlength(pre, font=fb); hx1 = hx0 + d.textlength(hl, font=fb)
        d.text((hx0, y0), hl, font=fb, fill="#1D9BF0")   # 原截图里 @grok 是蓝色链接色
        m["hl"] = (hx0, bb[1], hx1, bb[3])
    card.save(f"{PUB}/{name}.png"); META[name] = m

xcard("e_c1", "@grok 是真的吗", hl="@grok")
xcard("e_c2", "又是一眼ai")

# IG：内容区 = 视频画面 (141,60)-(777,1024)；中间播放键用 inpaint 抹掉
ig = cv2.imread(f"{SS}/annahar_instagram_ai_label.png")
ct = ig[60:1024, 141:777].copy()
hsv = cv2.cvtColor(ct, cv2.COLOR_BGR2HSV)
mask = np.zeros(ct.shape[:2], np.uint8)
x0, y0, x1, y1 = 425 - 141, 585 - 60, 500 - 141, 660 - 60   # 播放键约 (430–492, 590–655)
reg = ct[y0:y1, x0:x1]
white = ((reg.min(axis=2) > 205)).astype(np.uint8) * 255
white = cv2.dilate(white, np.ones((7, 7), np.uint8))
mask[y0:y1, x0:x1] = white
ct = cv2.inpaint(ct, mask, 7, cv2.INPAINT_TELEA)
cv2.imwrite("/tmp/e_ig_content.png", ct)
im = Image.open("/tmp/e_ig_content.png").convert("RGBA")
bw = 12; card = Image.new("RGBA", (im.width + 2 * bw, im.height + 2 * bw), (0, 0, 0, 0))
ImageDraw.Draw(card).rounded_rectangle([0, 0, card.width - 1, card.height - 1], radius=18, fill="#FFFFFF")
mk = Image.new("L", im.size, 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=8, fill=255)
card.paste(im, (bw, bw), mk); card.save(f"{PUB}/e_ig.png"); META["e_ig"] = dict(size=card.size, mask_px=int((mask > 0).sum()))
json.dump(META, open("/workspace/iphone-fake/v2/v3e/assets_meta.json", "w"), indent=1)
print(json.dumps(META))
