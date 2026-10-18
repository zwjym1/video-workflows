"""V3f：去掉所有第三方页面/品牌/平台元素，改成自制中性证据卡；不写任何 V3/V3d/V3e 用到的文件（新文件一律 f_ 前缀）。
由 build_v3.py --v3f 在 main() 里调用：patch(G)，G = build_v3 的 globals()。"""
import os, json
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
import numpy as np

def patch(G):
    C = G["C"]; ELS = G["ELS"]; SHOTS = G["SHOTS"]; el = G["el"]; load = G["load"]; crop_fit = G["crop_fit"]; blur_bg = G["blur_bg"]
    save_world = G["save_world"]; vid_world = G["vid_world"]; vlayer = G["vlayer"]; ff = G["ff"]; wt = G["wt"]; T = G["ss"]
    A, PH, PUB = G["A"], G["PH"], G["PUB"]; BBC, G1E, BEACHE, G1STILL = G["BBC"], G["G1E"], G["BEACHE"], G["G1STILL"]
    PL, PR = G["PL"], G["PR"]; sr2 = G["sr2"]; m_full = G["m_full"]; cam = G["cam"]; I = G["I"]; V = G["V"]
    S = {s["id"]: s for s in SHOTS}
    font = C.font; INK, PAPER, RED, YELLOW = C.INK, C.PAPER, C.RED, C.YELLOW
    META = {}

    # ---------- 1. 假图卡：保留原裁切；BBC 角标/「Social media」局部模糊，红色英文横条盖成我们自己的「AI 生成」条 ----------
    def clean_bbc(im):
        a = np.asarray(im.convert("RGB")).astype(int); H, W_ = a.shape[:2]; R_, G_, B_ = a[..., 0], a[..., 1], a[..., 2]
        out = im.convert("RGBA").copy()
        blue = (B_ > 170) & (R_ < 90) & (G_ < 110); top = int(H * 0.2); ys, xs = np.where(blue[:top])
        if len(ys) > 50:
            y0, y1 = ys.min() - 14, ys.max() + 14; x0, x1 = max(0, xs.min() - 70), min(W_, xs.max() + 16)
            for box in ((x0, y0, x1, y1), (int(W_ * 0.68), y0 - 6, W_ - 4, y1 + 6)):   # 左上台标 + 右上「Social media」
                reg = out.crop(box).filter(ImageFilter.GaussianBlur(22)); out.paste(reg, box[:2])
        red = (R_ > 170) & (G_ < 90) & (B_ < 90); rows = np.where(red.mean(1) > 0.25)[0]
        if len(rows) > 10:
            y0, y1 = rows.min(), rows.max(); cols = np.where(red[y0:y1 + 1].mean(0) > 0.3)[0]; x0, x1 = cols.min(), cols.max()
            d = ImageDraw.Draw(out); d.rectangle([x0, y0, x1, y1], fill=(217, 58, 38, 255))
            fz = font(int((y1 - y0) * 0.62), True); d.text(((x0 + x1) / 2, (y0 + y1) / 2), "AI 生成", font=fz, fill="#FFFFFF", anchor="mm")
        return out
    for k, src, cr in (("fk_boat", f"{A}/bbc1080_0616_boat.png", (90, 260, 990, 1460)),
                       ("fk_fish", f"{A}/bbc1080_0675.png", (60, 250, 1020, 1530)),
                       ("fk_fish2", f"{A}/bbc1080_0655.png", (60, 250, 1020, 1530)),
                       ("fk_sea", f"{A}/bbc_sea_only.jpg", (0, 160, 720, 1120))):
        el("f_" + k, crop_fit(clean_bbc(load(src)), cr, (900, 1200))); ELS[k] = ELS["f_" + k]

    # ---------- 2. 评论卡：自制中性气泡（无平台、头像、用户名、日期）----------
    def bubble(name, body, label, hl=None, w=820, h=250, size=64):
        card = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
        d.rounded_rectangle([4, 4, w, h - 30], radius=26, fill="#FFFFFF", outline=YELLOW, width=5)
        d.polygon([(70, h - 32), (130, h - 32), (66, h + 6)], fill="#FFFFFF"); d.line([(70, h - 30), (66, h + 6), (130, h - 30)], fill=YELLOW, width=5)
        d.rounded_rectangle([26, 22, 26 + 20 + d.textlength(label, font=font(22, True)), 56], radius=8, fill=INK)
        d.text((36, 26), label, font=font(22, True), fill=YELLOW)
        fb = font(size, True); x0, y0 = 34, 86
        d.text((x0, y0), body, font=fb, fill=INK); bb = d.textbbox((x0, y0), body, font=fb); m = dict(size=card.size, body=bb)
        if hl:
            i = body.index(hl); hx0 = x0 + d.textlength(body[:i], font=fb); hx1 = hx0 + d.textlength(hl, font=fb)
            d.text((hx0, y0), hl, font=fb, fill="#1D9BF0"); m["hl"] = (hx0, bb[1], hx1, bb[3])
        el(name, card); META[name] = m
    bubble("f_c1", "问 AI：是真的吗？", "网友评论", hl="AI")
    bubble("f_c2", "又是一眼ai", "网友评论，文字原样")
    # f_c3：与 c3 同版式（下划线坐标不变），去掉平台名、视频号、赞数、表情码
    w3, h3 = 700, 250
    c3 = Image.new("RGBA", (w3 + 20, h3 + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(c3)
    d.rounded_rectangle([4, 4, w3, h3], radius=18, fill="#FFF8E7", outline=YELLOW, width=5)
    d.rounded_rectangle([26, 22, 268, 56], radius=8, fill=INK); d.text((38, 26), "网友热评，文字原样", font=font(22, True), fill=YELLOW)
    d.text((30, 80), "全新 iPhone 未激活仅泡水", font=font(36, True), fill=INK)
    el("f_c3", c3)
    for k in ("c1", "c2", "c3"): ELS[k] = ELS["f_" + k]

    # ---------- 3. 原帖标注卡（中译，无媒体名/平台名/账号名）----------
    q = Image.new("RGBA", (1000, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(q)
    d.rounded_rectangle([0, 0, 999, 559], radius=24, fill=PAPER); d.rectangle([0, 30, 14, 530], fill=RED)
    d.text((44, 30), "核查结论（中译）", font=font(34, True), fill=INK)
    yy = 100
    for ln in ["「这条视频最早发布的账号，", "发布时间是 10 月 16 日，", "账号自己给帖子加了标识："]:
        d.text((44, yy), ln, font=font(40, True), fill="#333"); yy += 62
    d.text((44, yy + 6), "AI 内容」", font=font(64, True), fill=RED)
    AIC = (44, yy + 6, 44 + d.textlength("AI 内容", font=font(64, True)), yy + 6 + 78)
    el("f_quote", q)

    # ---------- 4. 自制检测卡（替代 OpenAI 检测页 / Hive 检测页）----------
    def det_card():
        w, h = 1100, 760; c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill="#FFFFFF")
        d.rounded_rectangle([0, 0, w - 1, 110], radius=30, fill=INK); d.rectangle([0, 80, w - 1, 110], fill=INK)
        d.text((50, 26), "检测结果", font=font(50, True), fill=YELLOW)
        d.ellipse([w // 2 - 70, 160, w // 2 + 70, 300], fill="#E3F3E8"); d.line([(w // 2 - 34, 232), (w // 2 - 6, 262), (w // 2 + 40, 200)], fill="#2E8B57", width=14)
        rows = [("隐形水印", "已检出", RED), ("生成方式", "AI 工具", RED), ("结论", "AI 生成内容", RED)]
        y = 340; boxes = []
        for a, b, col in rows:
            d.rounded_rectangle([60, y, w - 60, y + 100], radius=18, fill="#FBEDEA" if col == RED else "#F2F2F2")
            d.text((100, y + 22), a, font=font(48, True), fill="#333"); tw = d.textlength(b, font=font(52, True))
            d.text((w - 100 - tw, y + 20), b, font=font(52, True), fill=col); boxes.append((60, y, w - 60, y + 100)); y += 130
        return c, boxes
    dc, dboxes = det_card()
    def hive_card():
        w, h = 1400, 700; c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill="#FFFFFF")
        d.text((60, 40), "AI 检测结果", font=font(56, True), fill=INK)
        d.text((60, 120), "检测对象：海滩捡 iPhone 视频", font=font(32, False), fill="#777")
        rows = [("AI 生成画面", "99.9%", True), ("AI 生成语音", "0%", False), ("AI 生成音乐", "99.9%", True), ("换脸", "0%", False)]
        y = 190; boxes = []
        for a, b, hot in rows:
            d.rounded_rectangle([60, y, w - 60, y + 108], radius=18, fill="#FDE3E3" if hot else "#F1F1F1")
            d.text((100, y + 14), b, font=font(64, True), fill="#D0141B" if hot else "#333")
            tw = d.textlength(a, font=font(44, True)); d.text((w - 100 - tw, y + 24), a, font=font(44, True), fill="#222")
            if hot: d.rounded_rectangle([100, y + 92, w - 100, y + 100], radius=4, fill="#D0141B")
            boxes.append((60, y, w - 60, y + 108)); y += 124
        return c, boxes
    hc, hboxes = hive_card()

    # ---------- 5. 搬运/转发卡 ----------
    tp = "/tmp/f_tv_src.png"; ff(["-ss", "1.0", "-i", BEACHE, "-frames:v", "1", tp])
    tv = Image.new("RGBA", (900, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(tv)
    d.rounded_rectangle([0, 0, 899, 519], radius=16, fill="#222")
    tv.paste(crop_fit(load(tp), sr2((0, 300, 720, 705)), (860, 480)).convert("RGB"), (20, 20))
    d.text((10, 526), "假片被当成新闻转发", font=font(26, False), fill="#BBB")
    el("f_tv", tv); ELS["tv"] = ELS["f_tv"]
    el("f_xrepost", C.side_card(640, 210, "转发帖", ["「大量 iPhone18 散落在大海上」", "「今天又有大量 iPhone 被冲到沙滩」"], tilt=0)); ELS["xrepost"] = ELS["f_xrepost"]
    ht = load(f"{PH}/handtruck_cut.png"); ht = ht.resize((int(ht.width * 520 / ht.height), 520), Image.LANCZOS)
    bx = Image.new("RGBA", (230, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(bx)
    bd.rectangle([0, 0, 229, 149], fill="#C89B5E", outline="#7A5A2E", width=4); bd.line([(0, 30), (229, 30)], fill="#A97E44", width=3)
    bd.text((115, 88), "转发", font=font(64, True), fill=RED, anchor="mm")
    grp = Image.new("RGBA", (ht.width + 120, ht.height + 20), (0, 0, 0, 0)); grp.alpha_composite(ht, (60, 20)); grp.alpha_composite(bx, (40, ht.height - 175))
    el("f_truck", grp.rotate(12, expand=True, resample=Image.BICUBIC))

    # ---------- 6. 照片：飞机换 CC0（JAL 货机，涂装字样打码）----------
    pl = load(f"{PH}/plane_cc0_jal_unicef.jpg").convert("RGB")
    for (x0, y0, x1, y1) in ((480, 640, 900, 800), (1460, 680, 1520, 720)):
        reg = pl.crop((x0, y0, x1, y1)); pl.paste(reg.resize((max(1, (x1 - x0) // 18), max(1, (y1 - y0) // 18))).resize(reg.size, Image.NEAREST).filter(ImageFilter.GaussianBlur(6)), (x0, y0))
    pl = pl.crop((0, 250, 2083, 1433)).convert("RGBA")
    el("f_ph_plane", G["card"](pl, 860, border=12)); ELS["ph_plane"] = ELS["f_ph_plane"]
    ship = load(f"{PH}/ship_orig.jpg")

    # 模糊底一律换成我们自己的超分假片帧 / CC0 照片
    g1s = load(G1STILL)
    bg_g1 = save_world("f_w_flood", blur_bg(g1s, 0.4)); bg_q1 = save_world("f_w_q1", blur_bg(g1s, 0.35)); bg_fish = save_world("f_w_fish", blur_bg(g1s, 0.38))
    bg_end = save_world("f_w_end", blur_bg(ship, 0.42)); bg_air = save_world("f_w_air", blur_bg(pl, 0.35))

    # ---------- 7. 逐镜替换 ----------
    def ov_of(sid, k, **match):
        return [o for o in S[sid]["ov"] if o["k"] == k and all(o.get(a) == b for a, b in match.items())]
    for s in SHOTS: s["src"] = None                                    # 所有来源角标清空
    def remap_imgs(sh):
        rep = {"v3/img/fk_boat.png": ELS["fk_boat"][0], "v3/img/fk_fish.png": ELS["fk_fish"][0], "v3/img/fk_fish2.png": ELS["fk_fish2"][0], "v3/img/fk_sea.png": ELS["fk_sea"][0],
               "v3/img/c1.png": ELS["c1"][0], "v3/img/c2.png": ELS["c2"][0], "v3/img/c3.png": ELS["c3"][0], "v3/img/tv.png": ELS["tv"][0],
               "v3/img/xrepost.png": ELS["xrepost"][0], "v3/img/truck.png": ELS["f_truck"][0], "v3/img/ph_plane.png": ELS["ph_plane"][0], "v3/img/quote.png": ELS["f_quote"][0]}
        for o in sh["ov"]:
            if o.get("src") in rep: o["src"] = rep[o["src"]]
            if "items" in o: o["items"] = [rep.get(x, x) for x in o["items"]]
    for s in SHOTS: remap_imgs(s)
    # 弹幕：中性好奇
    ov_of("s01", "danmaku")[0]["text"] = "在哪捡？"
    ov_of("s03", "danmaku")[0]["text"] = "真的假的？"
    # s05：右侧换成漂浮集装箱近景（不拍冒烟大船），标签中性
    cl = (0, 230, 720, 1043)
    S["s05"]["world"] = V(vid_world("f_s05", 3.2, [vlayer(G1E, 1.0, 1.0, sr2(cl), PL, gray=True), vlayer(BBC, 15.9, 0.8, (380, 700, 1080, 1493), PR)]))
    for o in ov_of("s05", "tag"):
        if "BBC" in o["text"]: o["text"] = "实拍画面"
    # s06：只取海面漂浮物 + 远处集装箱，慢放，避开人群
    S["s06"]["world"] = V(vid_world("f_s06", 3.2, [vlayer(BBC, 15.6, 0.6, (0, 880, 1080, 1488), (0, 0, 1920, 1080))]))
    # s07：右侧裁到画中画（主持人）下方
    cl = (0, 234, 720, 1047)
    S["s07"]["world"] = V(vid_world("f_s07", 3.4, [vlayer(BEACHE, 2.0, 1.0, sr2(cl), PL), vlayer(BBC, 41.3, 1.0, (100, 920, 983, 1920), PR)]))
    for o in ov_of("s07", "tag"):
        if "BBC" in o["text"]: o["text"] = "实拍画面"
    S["s08"]["world"] = I(bg_g1)
    # s09 评论气泡
    cx0, cy0 = 880, 330; m = META["f_c1"]; ke = 820 / m["size"][0]; hx0, hy0, hx1, hy1 = [v * ke for v in m["hl"]]
    ta = wt("09", "AI")
    S["s09"]["ov"] = [dict(k="img", t=T("09") + 0.05, src=ELS["c1"][0], x=cx0, y=cy0, w=820, enter="slideRight", shadow=True),
        dict(k="cursor", t=T("09") + 0.1, path=[[T("09") + 0.1, 1700, 860], [ta - 0.02, cx0 + hx1 - 10, cy0 + hy1 - 6]], click=ta, sfx="click"),
        dict(k="hl", t=ta, x=cx0 + hx0 - 6, y=cy0 + hy0 - 6, w=hx1 - hx0 + 12, h=hy1 - hy0 + 12, color="yellow")]
    m = META["f_c2"]; kc = 1000 / m["size"][0]; bx0, by0, bx1, by1 = [v * kc for v in m["body"]]; X0, Y0 = 460, 300
    S["s10"]["ov"] = [dict(k="dim", t=T("10"), a=0.45), dict(k="img", t=T("10") + 0.04, src=ELS["c2"][0], x=X0, y=Y0, w=1000, enter="pop", shadow=True),
        dict(k="underline", t=wt("10", "一"), t1=wt("10", "AI") + 0.25, x=X0 + bx0 + 10, y=Y0 + by1 + 14, w=bx1 - bx0 - 10, color="red")]
    S["s13"]["world"] = I(bg_q1)
    # s14：保留原放大镜画面（裁切范围内没有台标/横条）
    # s15：去掉「BBC Verify 核查」角标
    S["s15"]["ov"] = [o for o in S["s15"]["ov"] if o["k"] != "chip"]
    # 18-19 句变短：s15/s16 切点前移，两镜的圈都 ≥2.5s
    t20 = S["s16"]["t1"]; B15o = S["s16"]["t0"]; B15 = round(t20 - 2.62, 3); dB = B15 - B15o
    assert B15 - S["s15"]["t0"] >= 2.55, (B15, S["s15"]["t0"])
    S["s15"]["t1"] = B15; S["s16"]["t0"] = B15; S["s15"]["cam"][-1]["t"] = B15
    for o in S["s15"]["ov"]:
        if o.get("t1") is not None and o["t1"] > B15 - 0.2: o["t1"] = B15
    S["s16"]["cam"][0]["t"] = B15
    for o in S["s16"]["ov"]:
        if o["k"] == "cursor":
            o["t"] = B15; o["path"] = [[p_[0] + dB, p_[1], p_[2]] for p_ in o["path"]]; o["circle"]["t"] += dB
    # s16：保留检测页镜头；页面 logo / 台标局部模糊，英文字样盖成中文译文；推镜 1.8× → 1.4×（源图 1250 高，1.8× 会发虚）
    page = load(f"{A}/bbc1080_0545.png").crop((0, 0, 1080, 1250)); dpg = ImageDraw.Draw(page)
    for box in ((10, 10, 240, 90),):
        page.paste(page.crop(box).filter(ImageFilter.GaussianBlur(20)), box[:2])
    pa = np.asarray(page.convert("RGB")).astype(int); bl = (pa[..., 2] > 170) & (pa[..., 0] < 90) & (pa[..., 1] < 110); ys, xs = np.where(bl[:400])
    if len(ys):
        box = (max(0, xs.min() - 70), ys.min() - 12, xs.max() + 14, ys.max() + 12)
        page.paste(page.crop(box).filter(ImageFilter.GaussianBlur(24)), box[:2])
    bgc = tuple(pa[620, 540][:3])
    dpg.rectangle([120, 430, 960, 615], fill=bgc); dpg.text((540, 470), "由 AI 工具生成", font=font(76, True), fill="#1F4A2E", anchor="mm")
    dpg.text((540, 560), "（检测页原文，中译）", font=font(30, False), fill="#5A7A66", anchor="mm")
    dpg.rectangle([110, 670, 970, 980], fill=bgc)
    for i_, ln in enumerate(["该内容由 AI 工具生成。", "下方的检测信号", "为这一结论提供了佐证。"]):
        dpg.text((540, 720 + i_ * 80), ln, font=font(46, False), fill="#333333", anchor="mm")
    bg = blur_bg(page, 0.35); ph = 1000; pw = round(1080 * ph / 1250); px = 960 - pw // 2; py = 140
    big = bg.resize((3840, 2160), Image.LANCZOS); big.alpha_composite(page.resize((pw * 2, ph * 2), Image.LANCZOS), (px * 2, py * 2))
    S["s16"]["world"] = I(save_world("f_w_openai", big, 2), 2)
    for kf in S["s16"]["cam"]:
        kf["s"] = round(1 + (kf["s"] - 1) * 0.4 / 0.8, 3) if kf["s"] > 1.05 else kf["s"]
    for o in S["s16"]["ov"]:
        if o["k"] == "cap": o["text"] = "AI 工具生成"
    S["s17"]["world"] = I(bg_fish)
    # s18：保留原对比画面；左图红色英文横条盖成「AI 生成」条
    fk = clean_bbc(load("/tmp/bbc_f_8.75.png")); rl = clean_bbc(load("/tmp/bbc_f_11.6.png"))
    crop = (30, 400, 1051, 1556)
    L = crop_fit(fk, crop, (954, 1080)); Rr = crop_fit(rl, crop, (954, 1080))
    base = Image.new("RGBA", (1920, 1080), INK); base.alpha_composite(L, (0, 0)); base.alpha_composite(Rr, (966, 0))
    S["s18"]["world"] = I(save_world("f_w_split3", base))
    for o in ov_of("s20", "tag"):
        if "BBC" in o["text"]: o["text"] = "实拍海面"
    # s21：原帖截图换成海滩假片卡；去掉「来源」小字
    for o in S["s21"]["ov"]:
        if o["k"] == "text": o.pop("sub", None)
    # s22：原帖标注卡（自制）
    qx, qy, qw = 360, 220, 1200; qk = qw / 1000
    a0, a1, a2, a3 = AIC; acx, acy = qx + (a0 + a2) / 2 * qk, qy + (a1 + a3) / 2 * qk
    for o in S["s22"]["ov"]:
        if o["k"] == "cursor":
            o["path"][-1][1:] = [qx + a2 * qk + 10, acy]; o["circle"].update(cx=acx, cy=acy, rx=(a2 - a0) / 2 * qk + 40, ry=(a3 - a1) / 2 * qk + 26)
    S["s22"]["cam"][-1].update(x=acx, y=acy)
    # s23：保留检测页镜头；品牌字样/页脚模糊，英文标签盖成中文；推镜 1.95× → 1.4×（截图源 1432 宽，1.95× 发虚）
    hv = load(f"{PUB}/img/hive.png"); dh = ImageDraw.Draw(hv); ha = np.asarray(hv.convert("RGB"))
    def fillsamp(box, sx, sy, text=None, size=24, anchor="rm", col="#222222", tx=None, ty=None):
        c_ = tuple(int(v) for v in ha[sy, sx][:3]); dh.rectangle(box, fill=c_)
        if text: dh.text((tx if tx is not None else box[2], ty if ty is not None else (box[1] + box[3]) / 2), text, font=font(size, True), fill=col, anchor=anchor)
    fillsamp((1005, 62, 1130, 92), 1000, 77, "检测结果", 22, "lm", tx=1012)
    for (y0, y1, lab) in ((118, 163, "AI 生成视频"), (219, 263, "AI 生成语音"), (308, 362, "AI 生成音乐"), (410, 463, "深度伪造")):
        fillsamp((1180, y0, 1372, y1), 1170, (y0 + y1) // 2, lab, 26, "rm", tx=1366)
    for (y0, y1, lab) in ((466, 492, "AI 生成"), (513, 540, "AI 生成语音"), (561, 588, "AI 生成音乐")):
        fillsamp((86, y0, 250, y1), 80, (y0 + y1) // 2, lab, 18, "lm", tx=92)
    fillsamp((1150, 505, 1385, 552), 1140, 528)
    fillsamp((1040, 588, 1400, 616), 1030, 600)
    th = (450, 70, 574, 287); hv.paste(hv.crop(th).filter(ImageFilter.GaussianBlur(3)), th[:2])
    hx, hy, hw = 260, 250, 1400   # 与 V3e 同几何（hive.png 已是带白边的卡片），圈选坐标不变
    hb = blur_bg(load(f"{A}/beach_070.jpg"), 0.35).resize((3840, 2160), Image.LANCZOS)
    hcard = hv.resize((hw * 2, round(hv.height * hw * 2 / hv.width)), Image.LANCZOS)
    hb.alpha_composite(hcard, (hx * 2, hy * 2)); S["s23"]["world"] = I(save_world("f_w_hive", hb, 2), 2)
    for kf in S["s23"]["cam"]:
        if kf["s"] > 1.05: kf["s"] = round(1 + (kf["s"] - 1) * 0.4 / 0.95, 3)
    # s26 手推车箱子写「转发」（31 句改成「转发的人也被 AI 骗了」）
    # s27：同一段实拍，改裁平静海面 + 漂浮物（不拍人群哄抢）
    S["s27"]["world"] = V(vid_world("f_s27", 3.2, [vlayer(BBC, 14.2, 0.8, (0, 800, 1080, 1408), (0, 0, 1920, 1080))]))   # 仍是原片，换成平静海面近景（无人群）
    # s28：保留原镜头（人脸、台标在打码步骤处理）；标题「专家说」
    for o in ov_of("s28", "quote"):
        if o.get("title"): o["title"] = "专家说"
    # s29 / s29b：飞机照片换 CC0；去掉 BBC 报道标题图和信源条
    S["s29"]["world"] = I(bg_air); S["s29b"]["world"] = I(bg_air)
    S["s29b"]["ov"] = [o for o in S["s29b"]["ov"] if not (o["k"] == "chip" or (o["k"] == "img" and "bbc" in o["src"]))]
    # s30：不放搜索框（不做外部搜索引导），换成两行中性提示
    S["s30"]["ov"] = [o for o in S["s30"]["ov"] if o["k"] != "search"] + [
        dict(k="text", t=wt("38", "白"), text="刷到「白捡 iPhone」", x=1210, y=400, size=72, color="white", box=True),
        dict(k="text", t=wt("39", "查"), text="先看谁最先发的", x=1210, y=600, size=84, color="yellow", box=True)]
    S["s31"]["world"] = I(bg_end)
    json.dump(META, open("/workspace/iphone-fake/v2/v3e/assets_meta_v3f.json", "w"), indent=1)
