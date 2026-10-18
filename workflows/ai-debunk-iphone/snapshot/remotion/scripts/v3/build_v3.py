"""IphoneFakeV3 素材 + 时间轴。
world = 每镜 1920×1080 的底层画面（视频或图，按 layout 预合成）；Remotion 只做摄像机推拉 + 叠加层。
所有时间来自 vo/words_v3c.json；坐标为 world 1x 像素。输出 src/v3/data/v3.json"""
import json, os, sys, subprocess, math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
sys.path.insert(0, "/workspace/iphone-fake/v2/preview")
import compose as C

V2 = "/workspace/iphone-fake/v2"; R = f"{V2}/remotion"; PUB = f"{R}/public/v3"
A = f"{V2}/preview/assets"; SS = f"{V2}/assets/screenshots"; PH = f"{V2}/assets/photos"; ST = f"{V2}/assets/stickers"
SRC = "/workspace/iphone-fake/source"
G1 = f"{SRC}/pc_raw/x_blomahn_.mp4"; BBC = f"{SRC}/bbc_verify_c52e9zwd2vx8o_1080x1920.mp4"
BEACH = f"{SRC}/beach_fake_x_cuichenghao_2111241316801847763_720x1280.mp4"
FPS = 30
W = json.load(open(f"{V2}/vo/words_v3f.json" if "--v3f" in sys.argv else (f"{V2}/vo/words_v3d.json" if ("--v3d" in sys.argv or "--v3e" in sys.argv) else f"{V2}/vo/words_v3c.json")))
AM = json.load(open(f"{R}/scripts/v3/audio_meta.json"))
TOTAL = round(W["total_sec"], 2)   # 与口播尾音同步收片（最后一字后约 0.63s，BGM 在末 1.6s 内淡出）
REBUILD = "--force" in sys.argv
V3F = "--v3f" in sys.argv   # 去第三方版：自制证据卡、无品牌/平台/来源、口播去品牌词（words_v3f）
V3E = "--v3e" in sys.argv or V3F   # 清晰度版（在 V3d 基础上）：720 源换超分版、推镜 ≤1.1×、s19 静帧、X/IG 去平台外框
V3D = "--v3d" in sys.argv or V3E   # 去地名版：words_v3d、标题改「满海漂着」、去掉含地名的备选热评卡
SRD = f"{V2}/v3e/sr"
G1E, BEACHE = f"{SRD}/g1_sr1440.mp4", f"{SRD}/beach_sr1440.mp4"   # Real-ESRGAN x4plus → 1440×2560（坐标 = 720 原片 ×2）
G1STILL = f"{SRD}/g1_0145_x4.png"                                  # G1 6.0s 帧 x4 超分（2880×5120）
def sr2(c): return tuple(v * 2 for v in c)
def sr4(c): return tuple(v * 4 for v in c)

WT_ALIAS = {("09", "@Grok"): ("09", "AI"), ("19", "OpenAI"): ("19", "AI"), ("30", "搬"): ("30", "账")}   # V3f 改句后的锚点
def wt(sid, ch, occ=1):
    if V3F and (sid, ch) in WT_ALIAS: sid, ch = WT_ALIAS[(sid, ch)]
    n = 0
    for w in W["words"]:
        if w["id"] == sid and w["text"] == ch:
            n += 1
            if n == occ: return w["start"]
    raise KeyError((sid, ch, occ))
def ss(sid): return next(s for s in W["sentences"] if s["id"] == sid)["start"]

def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)
def need(p): return REBUILD or not os.path.exists(p)

# ---------------- 映射 ----------------
def m_panel(crop, cx=960, H=1080):
    x0, y0, x1, y1 = crop; s = H / (y1 - y0); pw = (x1 - x0) * s; left = cx - pw / 2
    return (lambda u, v: (round(left + (u - x0) * s, 1), round((v - y0) * s, 1))), s, (left, 0, pw, H)
def m_full(crop):
    x0, y0, x1, y1 = crop; s = 1920 / (x1 - x0)
    return (lambda u, v: (round((u - x0) * s, 1), round((v - y0) * s, 1))), s
PL, PR = (0, 0, 954, 1080), (966, 0, 954, 1080)    # 左右分屏窗口
def m_split(crop, side):
    x0, y0, x1, y1 = crop; rx, ry, rw, rh = PL if side == "L" else PR; s = rh / (y1 - y0)
    return (lambda u, v: (round(rx + (u - x0) * s, 1), round(ry + (v - y0) * s, 1))), s

# ---------------- 视频 world ----------------
def vlayer(src, t0, rate, crop, box, gray=False, still=False):
    return dict(src=src, t0=t0, rate=rate, crop=crop, box=box, gray=gray, still=still)
def vid_world(name, dur, layers, bg=None):
    dur = dur + 1.0   # v3c 时间轴镜头变长，片段留余量
    out = f"{PUB}/clips/{name}.mp4"
    if not need(out): return f"v3/clips/{name}.mp4"
    args, fc = [], []
    for i, L in enumerate(layers):
        if L["still"]: args += ["-loop", "1", "-t", f"{dur:.3f}", "-i", L["src"]]
        else: args += ["-ss", f"{L['t0']:.3f}", "-t", f"{dur * L['rate'] + 0.2:.3f}", "-i", L["src"]]
    fc.append(f"color=c=0x111214:s=1920x1080:r={FPS}:d={dur:.3f}[base]")
    cur = "base"
    if bg is not None:   # 模糊底：取第 bg 层整幅
        L = layers[bg]
        fc.append(f"[{bg}:v]setpts=PTS/{L['rate']},fps={FPS},scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=40:2,eq=brightness=-0.18:saturation=0.8[bg]")
        fc.append(f"[{cur}][bg]overlay=0:0:shortest=1[b0]"); cur = "b0"
    for i, L in enumerate(layers):
        x0, y0, x1, y1 = L["crop"]; bx, by, bw, bh = [round(v) for v in L["box"]]
        g = ",hue=s=0" if L["gray"] else ""
        sp = "" if L["still"] else f"setpts=PTS/{L['rate']},"
        fc.append(f"[{i}:v]{sp}fps={FPS},crop={x1-x0}:{y1-y0}:{x0}:{y0},scale={bw}:{bh}:flags=lanczos,unsharp=5:5:0.5{g}[l{i}]")
        fc.append(f"[{cur}][l{i}]overlay={bx}:{by}:shortest=0:eof_action=repeat[o{i}]"); cur = f"o{i}"
    ff([*args, "-filter_complex", ";".join(fc), "-map", f"[{cur}]", "-t", f"{dur:.3f}", "-an", "-c:v", "libx264", "-crf", "19",
        "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), out])
    return f"v3/clips/{name}.mp4"

# ---------------- 图 world ----------------
def load(p): return Image.open(p).convert("RGBA")
def blur_bg(im, dark=0.55):
    b = ImageOps.fit(im.convert("RGB"), (1920, 1080), Image.LANCZOS).filter(ImageFilter.GaussianBlur(36))
    return ImageEnhance.Brightness(b).enhance(dark).convert("RGBA")
def save_world(name, im, k=1):
    p = f"{PUB}/img/{name}.webp"
    if k != 1 and im.size != (1920 * k, 1080 * k): im = im.resize((1920 * k, 1080 * k), Image.LANCZOS)
    im.convert("RGB").save(p, "WEBP", quality=90, method=5)
    return f"v3/img/{name}.webp"
def save_el(name, im):
    p = f"{PUB}/img/{name}.png"; im.save(p); return f"v3/img/{name}.png", im.size
def crop_fit(im, crop, size):
    return im.crop(crop).resize(size, Image.LANCZOS)

# ---------------- 元素 ----------------
def card(im, w, border=10, radius=18, bg="#FFFFFF"):
    h = round(im.height * w / im.width)
    body = im.convert("RGBA").resize((w, h), Image.LANCZOS)
    c = Image.new("RGBA", (w + 2 * border, h + 2 * border), (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle([0, 0, c.width - 1, c.height - 1], radius=radius, fill=bg)
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=max(4, radius - border), fill=255)
    c.paste(body, (border, border), m)
    return c

ELS = {}
def el(name, im):
    ELS[name] = save_el(name, im)
    return ELS[name]

def build_elements():
    # 假图卡（原图裁 3:4，避开 BBC 红条）
    fakes = {
        "fk_g1": (load(f"{A}/g1_blomahn_f001.png"), (0, 200, 720, 1160)),
        "fk_beach": (load(f"{A}/beach_030.jpg"), (0, 160, 720, 1120)),
        "fk_boat": (load(f"{A}/bbc1080_0616_boat.png"), (90, 260, 990, 1460)),
        "fk_fish": (load(f"{A}/bbc1080_0675.png"), (60, 250, 1020, 1530)),
        "fk_fish2": (load(f"{A}/bbc1080_0655.png"), (60, 250, 1020, 1530)),
        "fk_sea": (load(f"{A}/bbc_sea_only.jpg"), (0, 160, 720, 1120)),
    }
    for k, (im, cr) in fakes.items():
        el(k, crop_fit(im, cr, (900, 1200)))   # 高清版（推镜用），显示时缩到 360×480
    if V3E:   # G1/海滩两张假图卡换超分帧（新文件名，V3/V3d 的 fk_* 不动）
        for k, src, t_, cr in (("fk_g1", G1E, 0.0, (0, 200, 720, 1160)), ("fk_beach", BEACHE, 3.0, (0, 160, 720, 1120))):
            tp = f"/tmp/e_{k}.png"; ff(["-ss", str(t_), "-i", src, "-frames:v", "1", tp])
            el("e_" + k, crop_fit(load(tp), sr2(cr), (900, 1200)).filter(ImageFilter.UnsharpMask(1.5, 40, 2)))
            ELS[k] = ELS["e_" + k]
    el("c1", card(C.load_shot("comment_C1_x.png"), 900, border=14))   # 评论昵称不打码（用户要求）
    el("c2", card(C.load_shot("comment_C2_x.png"), 900, border=14))
    el("c3", C.c3_card())
    # 备选热评（文字原样，按 facts.md 备选）
    for k, (src, txt) in {"c4": ("B站热评", "霍尔木兹限定版iphone"), "c5": ("X 评论", "这个是真的吗？霍尔木兹海峡，在哪个城市？")}.items():
        im = Image.new("RGBA", (700, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, 699, 149], radius=18, fill="#FFFFFF")
        d.text((26, 18), src + " · 文字原样", font=C.font(22, True), fill="#888")
        d.text((26, 62), txt, font=C.font(34, True), fill=C.INK)
        el(k, im)
    ig = load(f"{SS}/annahar_instagram_ai_label.png")
    el("ig", card(ig, 600, border=12))
    hive = load(f"{SS}/annahar_hive_999.png").crop((0, 62, 920, 455))
    el("hive", card(hive, 1400, border=16))
    el("bbc_title", card(load(f"{SS}/bbc_article_title.png"), 620, border=8))
    # Annahar 原话卡（中译）
    q = Image.new("RGBA", (1000, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(q)
    d.rounded_rectangle([0, 0, 999, 559], radius=24, fill=C.PAPER); d.rectangle([0, 30, 14, 530], fill=C.RED)
    d.text((44, 30), "Annahar 核查原文（中译）", font=C.font(34, True), fill=C.INK)
    yy = 100
    for ln in ["「最早发在 Instagram 账号 @nativ0ra，", "时间是 2026 年 10 月 16 日……", "该账号给帖子加上了数字标识"]:
        d.text((44, yy), ln, font=C.font(40, True), fill="#333"); yy += 62
    d.text((44, yy + 6), "AI Content」", font=C.font(64, True), fill=C.RED)
    AIC = (44, yy + 6, 44 + d.textlength("AI Content", font=C.font(64, True)), yy + 6 + 78)
    d.text((44, 500), "原帖嵌入页不显示该标识，以 Annahar 原文为准", font=C.font(24, False), fill="#777")
    el("quote", q)
    # 搬运号：电视画中画 + X 转发卡
    kola = load(f"{A}/kola_360.jpg")
    tv = Image.new("RGBA", (900, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(tv)
    d.rounded_rectangle([0, 0, 899, 519], radius=16, fill="#222")
    tv.paste(ImageOps.fit(kola.convert("RGB"), (860, 480), Image.LANCZOS), (20, 20))
    d.text((10, 526), "搬运号把假片当新闻播", font=C.font(26, False), fill="#BBB")
    el("tv", tv)
    el("xrepost", C.side_card(640, 210, "X 转发帖", ["「大量 iPhone18 散落在大海上」", "「今天又有大量 iPhone 被冲到沙滩」"], tilt=0))
    # 照片卡
    el("ph_plane", card(load(f"{PH}/plane_orig.jpg").crop(C.PH_PLANE[1]), 860, border=12))
    el("ph_ship", card(load(f"{PH}/ship_orig.jpg").crop(C.PH_SHIP[1]), 640, border=12))
    # 手推车 + 「搬运」箱
    ht = load(f"{PH}/handtruck_cut.png"); ht = ht.resize((int(ht.width * 520 / ht.height), 520), Image.LANCZOS)
    bx = Image.new("RGBA", (230, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(bx)
    bd.rectangle([0, 0, 229, 149], fill="#C89B5E", outline="#7A5A2E", width=4); bd.line([(0, 30), (229, 30)], fill="#A97E44", width=3)
    bd.text((115, 88), "搬运", font=C.font(64, True), fill=C.RED, anchor="mm")
    grp = Image.new("RGBA", (ht.width + 120, ht.height + 20), (0, 0, 0, 0)); grp.alpha_composite(ht, (60, 20)); grp.alpha_composite(bx, (40, ht.height - 175))
    el("truck", grp.rotate(12, expand=True, resample=Image.BICUBIC))
    el("bubble", C.comment_icon(160))
    el("sparkle", load(f"{ST}/sparkle.png"))
    # 放大镜：17 镜盒子侧面印字（boat 1080 原图 TEXT_C 附近）
    boat = load(f"{A}/bbc1080_0616_boat.png")
    r = 300; span = 95; cx, cy = 712, 880
    reg = boat.crop((cx - span, cy - span, cx + span, cy + span)).resize((2 * r, 2 * r), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 110, 2))
    L = Image.new("RGBA", (2 * r + 24, 2 * r + 24), (0, 0, 0, 0)); sh = Image.new("RGBA", L.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([10, 14, 2 * r + 14, 2 * r + 18], fill=(0, 0, 0, 140)); L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    mk = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(mk).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    L.paste(reg, (12, 12), mk); ImageDraw.Draw(L).ellipse([12, 12, 12 + 2 * r - 1, 12 + 2 * r - 1], outline="#FFFFFF", width=10)
    el("lens_text", L)
    return {"lens": {"r": r, "span": span, "c": (cx, cy)}, "AIC": AIC}

# ---------------- 镜头表 ----------------
SHOTS = []
def shot(id, t0, t1, world, cam=None, ov=None, src=None, enter="cut", gray_at=None, note=""):
    SHOTS.append(dict(id=id, t0=round(t0, 3), t1=round(t1, 3), world=world, cam=cam or [], ov=ov or [], src=src, enter=enter, grayAt=gray_at, note=note))
def V(path): return {"type": "video", "src": path}
def I(path, k=1): return {"type": "image", "src": path, "k": k}
def cam(*kf): return [dict(t=round(t, 3), s=s, x=x, y=y) for (t, s, x, y) in kf]

def main():
    os.makedirs(f"{PUB}/img", exist_ok=True); os.makedirs(f"{PUB}/clips", exist_ok=True)
    E = build_elements()
    T = lambda sid: ss(sid)
    nxt = lambda sid: ss(f"{int(sid)+1:02d}")
    # ===== 钩子 =====
    # 01 0.00–1.17：G1 竖屏居中 + 模糊底；第 0.27s 从 1.75 倍特写跳到全景
    if V3E:   # 超分 G1，只取下半（满海盒子 + 小船），集装箱只露一角；不推镜（≤1.05×）；弹幕只留一条
        m, s, box = m_panel((0, 600, 720, 1280))
        w = vid_world("e_s01", 1.6, [vlayer(G1E, 0.0, 1.0, sr2((0, 600, 720, 1280)), box)], bg=0)
        shot("s01", 0, wt("01", "满"), V(w), cam((0, 1.0, 960, 540), (wt("01", "满"), 1.05, 960, 560)),
             [dict(k="danmaku", t=0.3, text="在哪捡？？", y=300)], enter="none")
    else:
        m, s, box = m_panel((0, 0, 720, 1280))
        w = vid_world("s01", 1.6, [vlayer(G1, 0.0, 1.0, (0, 0, 720, 1280), box)], bg=0)
        shot("s01", 0, wt("01", "满"), V(w), cam((0, 1.75, 960, 600), (0.26, 1.82, 960, 600), (0.267, 1.12, 960, 540), (1.17, 1.2, 960, 540)),
             [dict(k="danmaku", t=0.3, text="在哪捡？？", y=300), dict(k="danmaku", t=0.5, text="冲了冲了", y=430)], enter="none")
    # 02 1.17–2.43：G1 下半段全幅（盒子漂满）+ 黄胶囊「免费 iPhone？」
    if V3E:
        w = vid_world("e_s02", 1.6, [vlayer(G1E, 3.0, 1.0, sr2((0, 560, 720, 965)), (0, 0, 1920, 1080))])
        shot("s02", wt("01", "满"), T("02"), V(w), cam((wt("01", "满"), 1.0, 960, 540), (T("02"), 1.06, 960, 560)),
             [dict(k="cap", t=wt("01", "免"), text="免费 iPhone？", color="yellow", x=1380, y=300, size=64, rot=-4, sfx="pop")])
    else:
        w = vid_world("s02", 1.6, [vlayer(G1, 3.0, 1.0, (0, 560, 720, 965), (0, 0, 1920, 1080))])
        shot("s02", wt("01", "满"), T("02"), V(w), cam((wt("01", "满"), 1.0, 960, 540), (T("02"), 1.08, 960, 560)),
             [dict(k="cap", t=wt("01", "免"), text="免费 iPhone？", color="yellow", x=1380, y=300, size=64, rot=-4, sfx="pop"),
              dict(k="danmaku", t=wt("01", "满") + 0.25, text="发财了发财了", y=230)])
    # 03 2.43–4.34：海滩假片 + 小官抱船桨入画；「放下」时船桨落下
    if V3E:   # 超分海滩片，裁掉顶部远处货轮（y<300），推镜 ≤1.1×；弹幕只留一条
        m, s, box = m_panel((0, 300, 720, 1280), cx=720)
        w = vid_world("e_s03", 2.2, [vlayer(BEACHE, 0.6, 1.0, sr2((0, 300, 720, 1280)), box)], bg=0)
        shot("s03", T("02"), T("03"), V(w), cam((T("02"), 1.0, 960, 540), (wt("02", "桨"), 1.02, 960, 540), (wt("02", "放") + 0.12, 1.08, 1180, 560), (T("03"), 1.1, 1180, 560)),
             [dict(k="img", t=T("02") + 0.1, src="v3/qban/02_oar_c1.png", x=1180, y=250, w=560, enter="slideRight", dropAt=wt("02", "放")),
              dict(k="danmaku", t=T("02") + 0.05, text="我已经在划了", y=230)])
    else:
        m, s, box = m_panel((0, 0, 720, 1280), cx=720)
        w = vid_world("s03", 2.2, [vlayer(BEACH, 0.6, 1.0, (0, 0, 720, 1280), box)], bg=0)
        shot("s03", T("02"), T("03"), V(w), cam((T("02"), 1.0, 960, 540), (wt("02", "桨"), 1.02, 960, 540), (wt("02", "放") + 0.12, 1.12, 1180, 560), (T("03"), 1.13, 1180, 560)),
             [dict(k="img", t=T("02") + 0.1, src="v3/qban/02_oar_c1.png", x=1180, y=250, w=560, enter="slideRight", dropAt=wt("02", "放")),
              dict(k="danmaku", t=T("02") + 0.05, text="我已经在划了", y=230), dict(k="danmaku", t=T("02") + 0.4, text="坐标发一下", y=360)])
    # 04（03 句）4.34–T04B：四张画面飞入拼 2×2 → 「AI」那一拍去色 + 红章 + 重音
    g1bg = blur_bg(load(f"{A}/g1_blomahn_f073.png"), 0.45)
    w = save_world("w_grid", g1bg)
    cards4 = [("fk_g1", 330, 500, -6), ("fk_beach", 750, 520, 3), ("fk_boat", 1170, 500, -3), ("fk_fish", 1590, 520, 5)]
    ov = [dict(k="img", t=T("03") + 0.05 * i, src=ELS[n][0], x=x - 180, y=y - 240, w=360, rot=r, enter="drop", frame=True) for i, (n, x, y, r) in enumerate(cards4)]
    tA = wt("03", "AI")
    ov += [dict(k="stamp", t=tA, text="AI 生成", x=960, y=500, size=150, rot=-10, sfx="hit"), dict(k="shake", t=tA), dict(k="flash", t=tA)]
    T04B = wt("03", "的") + 0.09   # 原 5.90s：「的」后 3 帧切分屏
    shot("s04", T("03"), T04B, I(w), cam((T("03"), 1.0, 960, 540), (T04B, 1.05, 960, 520)), ov, gray_at=tA)
    # ===== 证据 =====
    # 05（04 句）T04B–8.43 左假右真①：左 G1 去色 + 红章残影 / 右 BBC 真实沉船
    cl, cr = (0, 230, 720, 1043), (0, 300, 1080, 1520)
    w = vid_world("e_s05", 2.7, [vlayer(G1E, 1.0, 1.0, sr2(cl), PL, gray=True), vlayer(BBC, 9.9, 1.0, cr, PR)]) if V3E else vid_world("s05", 2.7, [vlayer(G1, 1.0, 1.0, cl, PL, gray=True), vlayer(BBC, 9.9, 1.0, cr, PR)])
    shot("s05", T04B, T("05"), V(w), cam((T04B, 1.0, 960, 540), (T("05"), 1.03, 960, 540)),
         [dict(k="split", t=T04B), dict(k="tag", t=T04B, text="网传画面 · AI 生成", color="red", x=40, y=150),
          dict(k="stamp", t=T04B, text="AI 生成", x=477, y=560, size=96, rot=-10, still=True),
          dict(k="tag", t=wt("04", "真"), text="BBC 实拍 · 船真沉了", color="green", x=1006, y=150, sfx="pop", popin=True)], src="素材：BBC Verify · X 网传视频")
    # 06（05 句）8.43–11.20：BBC 真实小船围集装箱，全幅；「也是真的」加速推近 + 绿胶囊
    w = vid_world("s06", 3.0, [vlayer(BBC, 15.6, 0.9, (0, 760, 1080, 1368), (0, 0, 1920, 1080))])
    shot("s06", T("05"), T("06"), V(w), cam((T("05"), 1.0, 960, 540), (wt("05", "也"), 1.04, 960, 540), (wt("05", "真") + 0.1, 1.16, 900, 560), (T("06"), 1.18, 900, 560)),
         [dict(k="cap", t=wt("05", "真"), text="也是真的", color="green", x=1480, y=300, size=60, rot=3, sfx="pop")], src="素材：BBC Verify")
    # 07（06+07 句）11.20–13.80 左假右真②：左海滩假片 / 右 BBC「要 iPhone 吗」真视频
    cl, cr = (0, 234, 720, 1047), (0, 350, 1080, 1570)
    w = vid_world("e_s07", 2.8, [vlayer(BEACHE, 2.0, 1.0, sr2(cl), PL), vlayer(BBC, 41.3, 1.0, cr, PR)]) if V3E else vid_world("s07", 2.8, [vlayer(BEACH, 2.0, 1.0, cl, PL), vlayer(BBC, 41.3, 1.0, cr, PR)])
    shot("s07", T("06"), T("08"), V(w), cam((T("06"), 1.0, 960, 540), (T("08"), 1.03, 960, 540)),
         [dict(k="split", t=T("06")), dict(k="tag", t=T("06"), text="网传假片", color="red", x=40, y=150),
          dict(k="tag", t=T("06"), text="BBC 实拍", color="green", x=1006, y=150),
          dict(k="quote", t=wt("06", "要"), title="原声直译", text="「要 iPhone 吗？」", x=1180, y=560),
          dict(k="cap", t=wt("07", "真"), text="也是真的", color="green", x=1500, y=330, size=58, rot=-3)], src="素材：BBC Verify · X 网传视频")
    # 08 13.80–15.83：假图刷屏，六张卡片依次砸满屏
    w = save_world("w_flood", blur_bg(load(f"{A}/bbc1080_0505.png"), 0.4))
    pos = [("fk_g1", 380, 470, -8), ("fk_boat", 760, 520, 5), ("fk_beach", 1140, 470, -4), ("fk_fish2", 1520, 520, 7), ("fk_fish", 560, 560, 9), ("fk_sea", 1340, 560, -6)]
    tt = [T("08") + 0.05, wt("08", "假"), wt("08", "图"), wt("08", "就"), wt("08", "刷"), wt("08", "屏")]
    ov = [dict(k="img", t=t, src=ELS[n][0], x=x - 170, y=y - 225, w=340, rot=r, enter="slam", frame=True) for t, (n, x, y, r) in zip(tt, pos)]
    shot("s08", T("08"), T("09"), I(w), cam((T("08"), 1.0, 960, 540), (T("09"), 1.06, 960, 540)), ov)
    # 09 15.83–18.15：海滩假片 + X 评论 C1，光标点 @grok
    m, s, box = m_panel((0, 0, 720, 1280), cx=520)
    w = vid_world("e_s09", 2.5, [vlayer(BEACHE, 3.0, 1.0, sr2((0, 0, 720, 1280)), box)], bg=0) if V3E else vid_world("s09", 2.5, [vlayer(BEACH, 3.0, 1.0, (0, 0, 720, 1280), box)], bg=0)
    cx0, cy0 = 880, 330      # C1 卡左上（宽 900+28 → 显示 820）
    k = 820 / ELS["c1"][1][0]
    grok = (cx0 + (14 + 2 * 900 / 568 * 0 + 30) * k, cy0 + (14 + 106 * 900 / 568) * k)
    shot("s09", T("09"), T("10"), V(w), cam((T("09"), 1.0, 960, 540), (T("10"), 1.05, 1100, 520)),
         [dict(k="img", t=T("09") + 0.05, src=ELS["c1"][0], x=cx0, y=cy0, w=820, enter="slideRight", shadow=True),
          dict(k="cursor", t=T("09") + 0.1, path=[[T("09") + 0.1, 1700, 860], [wt("09", "@Grok") - 0.02, grok[0] + 10, grok[1] + 10]],
               click=wt("09", "@Grok"), sfx="click"),
          dict(k="hl", t=wt("09", "@Grok"), x=cx0 + 14 * k, y=grok[1] - 22, w=60 * 900 / 568 * k, h=40, color="yellow"),
          dict(k="text", t=wt("09", "@Grok") + 0.12, text="「@grok 是真的吗」", x=1290, y=720, size=66, color="white", box=True)], src="X 网传视频 · 评论为原帖截图")
    EM = json.load(open(f"{V2}/v3e/assets_meta.json")) if V3E else {}
    if V3E:   # X 评论只留文字内容（按原文排版，无头像栏/按钮栏），来源写在信源角标
        c1m = EM["e_c1"]; ke = 820 / c1m["size"][0]
        hx0, hy0, hx1, hy1 = [v * ke for v in c1m["hl"]]
        SHOTS[-1]["ov"] = [dict(k="img", t=T("09") + 0.05, src="v3/img/e_c1.png", x=cx0, y=cy0, w=820, enter="slideRight", shadow=True),
            dict(k="cursor", t=T("09") + 0.1, path=[[T("09") + 0.1, 1700, 860], [wt("09", "@Grok") - 0.02, cx0 + hx1 - 10, cy0 + hy1 - 6]], click=wt("09", "@Grok"), sfx="click"),
            dict(k="hl", t=wt("09", "@Grok"), x=cx0 + hx0 - 6, y=cy0 + hy0 - 6, w=hx1 - hx0 + 12, h=hy1 - hy0 + 12, color="yellow")]
        SHOTS[-1]["src"] = "信源：X 网传视频 · X 评论文字原样"
    # 10 18.15–20.09：评论 C2「又是一眼ai」，红线划重点
    w = vid_world("e_s10", 2.2, [vlayer(BEACHE, 4.0, 1.0, sr2((0, 300, 720, 705)), (0, 0, 1920, 1080))]) if V3E else vid_world("s10", 2.2, [vlayer(BEACH, 4.0, 1.0, (0, 300, 720, 705), (0, 0, 1920, 1080))])
    k2 = 980 / ELS["c2"][1][0]
    shot("s10", T("10"), T("11"), V(w), cam((T("10"), 1.0, 960, 540), (T("11"), 1.05, 960, 520)),
         [dict(k="dim", t=T("10"), a=0.45),
          dict(k="img", t=T("10") + 0.04, src=ELS["c2"][0], x=560, y=170, w=800, enter="pop", shadow=True),
          dict(k="text", t=wt("10", "说"), text="「又是一眼 ai」", x=960, y=640, size=104, color="white"),
          dict(k="underline", t=wt("10", "一"), t1=wt("10", "AI") + 0.25, x=690, y=722, w=540, color="red")], src="X 评论原帖截图")
    if V3E:
        c2m = EM["e_c2"]; kc = 1000 / c2m["size"][0]; bx0, by0, bx1, by1 = [v * kc for v in c2m["body"]]; X0, Y0 = 460, 300
        SHOTS[-1]["ov"] = [dict(k="dim", t=T("10"), a=0.45),
            dict(k="img", t=T("10") + 0.04, src="v3/img/e_c2.png", x=X0, y=Y0, w=1000, enter="pop", shadow=True),
            dict(k="underline", t=wt("10", "一"), t1=wt("10", "AI") + 0.25, x=X0 + bx0 + 10, y=Y0 + by1 + 14, w=bx1 - bx0 - 10, color="red")]
        SHOTS[-1]["src"] = "信源：X 评论文字原样"
    # 11 20.09–23.22：B 站热评 C3「全新未激活，仅泡水」，说到「仅泡水」推近 + 气泡
    m, s, box = m_panel((0, 0, 720, 1280), cx=500)
    w = vid_world("e_s11", 3.4, [vlayer(BEACHE, 4.5, 0.9, sr2((0, 0, 720, 1280)), box)], bg=0) if V3E else vid_world("s11", 3.4, [vlayer(BEACH, 4.5, 0.9, (0, 0, 720, 1280), box)], bg=0)
    zA, zB = (1.08, 1.1) if V3E else (1.22, 1.25)   # V3e：720 源推镜 ≤1.1×
    shot("s11", T("11"), T("13"), V(w), cam((T("11"), 1.0, 960, 540), (wt("12", "仅") - 0.05, 1.02, 960, 540), (wt("12", "仅") + 0.3, zA, 1300, 500), (T("13"), zB, 1300, 500)),
         [dict(k="img", t=wt("11", "玩"), src=ELS["c3"][0], x=900, y=360, w=820, enter="pop", shadow=True, rot=-2, sfx="pop"),
          dict(k="bubbles", t=wt("12", "泡"), x=1500, y=640),
          dict(k="underline", t=wt("12", "仅"), t1=wt("12", "水") + 0.25, x=900 + 26 * 820 / 720 + 296 * 820 / 720, y=360 + 128 * 820 / 720, w=150 * 820 / 720, color="yellow")], src="X 网传视频 · B 站热评文字原样")
    # 12 23.22–25.41：评论区比海面还热闹：小官捂嘴笑 + 评论卡上滚
    w = save_world("w_cmt", blur_bg(load(f"{A}/g1_blomahn_f073.png"), 0.42))
    sc = [("c3", 640), ("c1", 640), ("c2", 640), ("c3", 640), ("c1", 640)] if V3D else [("c3", 640), ("c1", 640), ("c4", 640), ("c2", 640), ("c5", 640)]   # c4/c5 原文含地名，V3d 不用
    shot("s12", T("13"), T("14"), I(w), cam((T("13"), 1.0, 960, 540), (T("14"), 1.04, 960, 540)),
         [dict(k="scroll", t=T("13"), items=[ELS[n][0] for n, _ in sc], x=1060, w=700, y0=160, speed=230, gap=40),
          dict(k="img", t=T("13") + 0.05, src="v3/qban/10_cover_mouth_c1.png", x=180, y=230, w=600, enter="slideLeft")])
    # ===== 揭穿 =====
    # 13（14+15 句）25.41–28.36：设问①，四张假图一排 + 大问号 + 小官思考 → 「先看小船这张」推进小船卡
    w = save_world("w_q1", blur_bg(load(f"{A}/bbc1080_0505.png"), 0.35), 1)
    row = [("fk_g1", 330, 560, -5), ("fk_beach", 750, 580, 3), ("fk_boat", 1170, 560, 0), ("fk_fish", 1590, 580, 4)]
    ov = [dict(k="img", t=T("14"), src=ELS[n][0], x=x - 180, y=y - 240, w=360, rot=r, enter="none", frame=True, hiAt=None) for (n, x, y, r) in row]
    tq = wt("14", "什")
    ov += [dict(k="qmark", t=tq, x=960, y=250, size=210, sfx="pop", t1=T("15") - 0.05),
           dict(k="img", t=tq + 0.05, src="v3/qban/st_think.png", x=1620, y=120, w=250, enter="pop", t1=T("15") - 0.05)]
    # 小船卡 360×480，左上 (990,320)；船上白盒子（1080 原图 452,925）→ 卡内 ((452-90)*0.4, (925-260)*0.4)
    bxw, byw = 990 + (452 - 90) * 0.4, 320 + (925 - 260) * 0.4
    ov += [dict(k="dash", t=wt("15", "这"), t1=T("16"), cx=bxw, cy=byw, rx=34, ry=28, color="red")]
    zc = 480 / 1080
    shot("s13", T("14"), T("16"), I(w), cam((T("14"), 1.0, 960, 540), (T("15"), 1.02, 960, 540), (T("15") + 0.45, 2.15, 1170, 560), (T("16"), 2.3, bxw - 20, byw - 30)), ov,
         note="小船卡推满屏（卡片源图 900×1200）")
    # 14（16 句）28.36–30.22：BBC 放大镜帧，虚线圈延续 + ①② 红圈 + 红胶囊
    crop = (0, 560, 1080, 1168); mf, s = m_full(crop)
    mag = load(f"{A}/bbc1080_0630_mag.png")
    w = save_world("w_mag", crop_fit(mag, crop, (1920, 1080)))
    lc = mf(*C.MAG_C); c1 = mf(*C.CAM1); c2 = mf(*C.CAM2)
    B14 = wt("17", "的") + 0.06; B15 = wt("18", "隐")   # 圈选单镜停留 ≥2.5s
    shot("s14", T("16"), B14, I(w), cam((T("16"), 1.0, lc[0], lc[1]), (B14, 1.08, lc[0], lc[1])),
         [dict(k="dash", t=T("16"), t1=B14, cx=lc[0], cy=lc[1], rx=195 * s + 22, ry=195 * s + 22, color="red", noDraw=True),
          dict(k="ring", t=wt("16", "两"), cx=c1[0], cy=c1[1], r=40 * s + 14, label="①"),
          dict(k="ring", t=wt("16", "组"), cx=c2[0], cy=c2[1], r=40 * s + 14, label="②"),
          dict(k="cap", t=wt("16", "两"), text="画了两组摄像头", color="red", x=1490, y=230, size=60, rot=-3, sfx="pop", kit=True)], src="素材：BBC Verify（BBC 放大镜画面）")
    # 15（17 句 + 18 句前半）30.22–32.78：放大镜看盒侧印字，虚线圈 + 红波浪线；「BBC 一查」角标滑入
    crop = (300, 700, 1000, 1094); mf, s = m_full(crop)
    w = save_world("w_text", ImageEnhance.Color(crop_fit(load(f"{A}/bbc1080_0616_boat.png"), crop, (1920, 1080))).enhance(0.25), 1)
    lens = E["lens"]; LX, LY = 1290, 500; LR = lens["r"]
    def lmap(u, v): return (LX + (u - lens["c"][0]) * LR / lens["span"], LY + (v - lens["c"][1]) * LR / lens["span"])
    t1c, t2c = lmap(698, 903), lmap(745, 840)
    tp = mf(698, 903)
    shot("s15", B14, B15, I(w), cam((B14, 1.0, 960, 540), (B15, 1.06, 1150, 520)),
         [dict(k="leader", t=B14, x0=tp[0], y0=tp[1], x1=LX - LR, y1=LY, r0=40),
          dict(k="img", t=B14, src=ELS["lens_text"][0], x=LX - LR - 12, y=LY - LR - 12, w=ELS["lens_text"][1][0], enter="pop"),
          dict(k="dash", t=B14 + 0.03, t1=B15, cx=t1c[0], cy=t1c[1] + 4, rx=150, ry=70, color="red", rot=-12),
          dict(k="wavy", t=wt("17", "扭"), x=t1c[0] - 120, y=t1c[1] + 70, w=240, rot=-12),
          dict(k="cap", t=wt("17", "扭"), text="字全是扭的", color="red", x=560, y=250, size=60, rot=-3, sfx="pop", kit=True),
          dict(k="chip", t=T("18"), text="BBC Verify 核查", x=40, y=150)], src="素材：BBC Verify")
    # 16（18 句后半 + 19 句）32.78–35.76：OpenAI 检测页，光标圈出「Generated with OpenAI tools」，说到 OpenAI 推近 + 红胶囊
    page = load(f"{A}/bbc1080_0545.png").crop((0, 0, 1080, 1250))
    bg = blur_bg(page, 0.35); ph = 1000; pw = round(1080 * ph / 1250); px = 960 - pw // 2; py = 140
    K = 2; big = bg.resize((3840, 2160), Image.LANCZOS)
    pg = page.resize((pw * K, ph * K), Image.LANCZOS); big.alpha_composite(pg, (px * K, py * K))
    w = save_world("w_openai", big, 2)
    sk = ph / 1250
    gx0, gy0, gx1, gy1 = px + 130 * sk, py + 385 * sk, px + 950 * sk, py + 520 * sk   # 「Generated with OpenAI tools」（1080 原图约 y400–560）
    gcx, gcy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
    t_o = wt("19", "OpenAI")
    shot("s16", B15, T("20"), I(w, 2), cam((B15, 1.0, 960, 540), (T("19") - 0.02, 1.03, 960, 540), (T("19") + 0.3, 1.75, gcx, gcy + 40), (T("20"), 1.8, gcx, gcy + 40)),
         [dict(k="cursor", t=B15, path=[[B15, 1650, 900], [B15 + 0.12, gx1 + 10, gcy]],
               circle=dict(t=B15 + 0.1, cx=gcx, cy=gcy, rx=(gx1 - gx0) / 2 + 30, ry=(gy1 - gy0) / 2 + 22, dur=0.7, t1=T("20"))),
          dict(k="cap", t=t_o, text="OpenAI 工具生成", color="red", x=960, y=800, size=64, rot=0, sfx="pop", kit=True, screen=True)], src="素材：BBC Verify（OpenAI 检测页截屏）")
    # 17（20 句）35.76–37.07：渔民两张，白签「也有水印」
    w = save_world("w_fish", blur_bg(load(f"{A}/bbc1080_0655.png"), 0.38))
    ov = []
    for i, (n, x, r) in enumerate([("fk_fish2", 560, -3), ("fk_fish", 1360, 3)]):
        ov.append(dict(k="img", t=T("20") + 0.05 * i, src=ELS[n][0], x=x - 230, y=150, w=460, rot=r, enter="drop", frame=True))
        ov.append(dict(k="chip", t=wt("20", "也"), text="✓ 也有水印", x=x - 110, y=770, light=True, sfx="click" if i == 0 else None))
    shot("s17", T("20"), T("21") - 0.19, I(w), cam((T("20"), 1.0, 960, 540), (T("21") - 0.19, 1.05, 960, 540)), ov, src="素材：BBC Verify")
    # 18（21 句）37.07–39.64 左假右真③：BBC 改图（带盒子）vs 原照片
    crop = (30, 400, 1051, 1556)   # 船 + 水面上的盒子（src y≈1080–1550）都要在画里
    fake = load(f"/tmp/bbc_f_7.6.png") if os.path.exists("/tmp/bbc_f_7.6.png") else None
    for t_, n in ((8.75, "fake"), (11.6, "real")):
        p = f"/tmp/bbc_f_{t_}.png"
        if not os.path.exists(p): ff(["-ss", str(t_), "-i", BBC, "-frames:v", "1", p])
    L = crop_fit(load("/tmp/bbc_f_8.75.png"), crop, (954, 1080)); Rr = crop_fit(load("/tmp/bbc_f_11.6.png"), crop, (954, 1080))
    base = Image.new("RGBA", (1920, 1080), C.INK); base.alpha_composite(L, (0, 0)); base.alpha_composite(Rr, (966, 0))
    w = save_world("w_split3", base)
    mL, sL = m_split(crop, "L")
    bx0, by0 = mL(45, 1075); bx1, by1 = mL(1035, 1550)
    shot("s18", T("21") - 0.19, wt("22", "总"), I(w), cam((T("21") - 0.19, 1.0, 960, 540), (wt("22", "总"), 1.04, 960, 540)),
         [dict(k="split", t=T("21") - 0.19), dict(k="tag", t=T("21") - 0.19, text="网传图 · 改过的", color="red", x=40, y=150),
          dict(k="tag", t=wt("21", "真"), text="原照片 · 真", color="green", x=1006, y=150, popin=True),
          dict(k="dashrect", t=wt("21", "改"), x=bx0, y=by0, w=bx1 - bx0, h=min(by1, 890) - by0, color="yellow", label="加上去的盒子")], src="素材：BBC Verify")
    # 19（22+23 句）39.64–43.54：G1 慢放；设问②问号 + 小官惊讶 → 推到船上的人，虚线圈 + 红胶囊「人不动」
    crop = C.G1_18_CROP; mp, s, box = m_panel(crop)
    if V3E:   # 超分静帧（G1 6.0s，x4）替代 0.5× 慢放 + 2× 推镜；裁 9:16 让船上的人更大
        crop = (220, 300, 720, 1189); mp, s, box = m_panel(crop)
        st = load(G1STILL); bw_ = round(box[2])
        wim = blur_bg(st, 0.45); pnl = st.crop(sr4(crop)).resize((bw_, 1080), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.5, 40, 2))
        wim.alpha_composite(pnl, (round(box[0]), 0)); w19 = save_world("e_w_s19", wim)
    else:
        w = vid_world("s19", 4.1, [vlayer(G1, 5.0, 0.5, crop, box)], bg=0)
    pX = (C.G1_PEOPLE[0] + C.G1_PEOPLE[2]) / 2; pY = (C.G1_PEOPLE[1] + C.G1_PEOPLE[3]) / 2
    pc = mp(pX, pY); prx = (C.G1_PEOPLE[2] - C.G1_PEOPLE[0]) / 2 * s + 26; pry = (C.G1_PEOPLE[3] - C.G1_PEOPLE[1]) / 2 * s + 30
    B19 = wt("22", "总"); tq = B19 + 0.03   # s19 从「总」切入，避免单镜 >4s
    cam19 = cam((B19, 1.0, 960, 540), (T("23") - 0.35, 1.02, 960, 540), (T("24"), 1.08, (960 + pc[0]) / 2, 540)) if V3E else cam((B19, 1.0, 960, 540), (T("23") - 0.35, 1.03, 960, 540), (T("23") + 0.1, 1.9, pc[0], pc[1] + 60), (T("24"), 2.0, pc[0], pc[1] + 60))
    shot("s19", B19, T("24"), I(w19) if V3E else V(w), cam19,
         [dict(k="qmark", t=tq, x=1430, y=330, size=200, sfx="pop", t1=T("23") - 0.3),
          dict(k="img", t=tq + 0.05, src="v3/qban/st_surprise.png", x=1520, y=520, w=280, enter="pop", t1=T("23") - 0.3),
          dict(k="dash", t=T("23") - 0.3, t1=T("24"), cx=pc[0], cy=pc[1], rx=prx, ry=pry, color="red"),
          dict(k="waves", t=wt("23", "晃"), x=pc[0] - prx - 60, y=pc[1] + pry + 30),
          dict(k="cap", t=wt("23", "人", 1), text="人一动不动", color="red", x=960, y=220, size=66, rot=-2, sfx="hit", kit=True, screen=True)], src="信源：X 网传视频 · 超分静帧" if V3E else "X 网传视频 · 0.5 倍慢放")
    # 20（24 句 + 25 句前半）43.54–46.30 左假右真④：G1 盒子特写（新得像刚出厂）vs BBC 实拍海面
    crop = (324, 850, 624, 1189)
    if V3E:   # 盒子特写改用 x4 超分帧（原来是 300×339 像素放大 3.2 倍）
        g = crop_fit(load(G1STILL), sr4(crop), (954 * 2, 1080 * 2)).filter(ImageFilter.UnsharpMask(1.5, 40, 2))
        gp = f"/tmp/g1box_e.png"; g.save(gp)
        w = vid_world("e_s20", 2.9, [vlayer(gp, 0, 1.0, (0, 0, 1908, 2160), PL, still=True), vlayer(BBC, 14.2, 0.9, (0, 400, 1080, 1620), PR)])
    else:
        g = crop_fit(load(f"{A}/{C.G1_18}"), crop, (954 * 2, 1080 * 2)).filter(ImageFilter.UnsharpMask(2, 90, 2))
        gp = f"/tmp/g1box.png"; g.save(gp)
        w = vid_world("s20", 2.9, [vlayer(gp, 0, 1.0, (0, 0, 1908, 2160), PL, still=True), vlayer(BBC, 14.2, 0.9, (0, 400, 1080, 1620), PR)])
    mL, sL = m_split(crop, "L"); bc = mL(*C.G1_BOX)
    shot("s20", T("24"), wt("25", "iPhone"), V(w), cam((T("24"), 1.0, 960, 540), (wt("25", "iPhone"), 1.03, 960, 540)),
         [dict(k="split", t=T("24")), dict(k="tag", t=T("24"), text="网传视频截帧（放大）", color="red", x=40, y=150),
          dict(k="tag", t=T("24"), text="BBC 实拍海面", color="green", x=1006, y=150),
          dict(k="dash", t=T("24") + 0.02, t1=wt("25", "iPhone"), cx=bc[0], cy=bc[1], rx=190, ry=150, color="red"),
          dict(k="sparkle", t=wt("24", "新"), pts=[[bc[0] + 150, bc[1] - 160, 110], [bc[0] - 190, bc[1] - 90, 80], [bc[0] + 200, bc[1] + 90, 70]]),
          dict(k="cap", t=wt("24", "新"), text="新得像刚出厂", color="red", x=477, y=780, size=60, rot=-3, sfx="pop", kit=True)], src="素材：BBC Verify · X 网传视频")
    # 21（25 句后半 + 26 句）46.30–48.38：海滩假片 + IG 原帖卡 + 八千万播放
    m, s, box = m_panel((0, 0, 720, 1280), cx=520)
    w = vid_world("e_s21", 2.4, [vlayer(BEACHE, 0.0, 1.0, sr2((0, 0, 720, 1280)), box)], bg=0) if V3E else vid_world("s21", 2.4, [vlayer(BEACH, 0.0, 1.0, (0, 0, 720, 1280), box)], bg=0)
    B21 = wt("26", "早")
    shot("s21", wt("25", "iPhone"), B21, V(w), cam((wt("25", "iPhone"), 1.0, 960, 540), (B21, 1.05, 1100, 520)),
         [dict(k="img", t=T("26"), src=ELS["ig"][0], x=1020, y=150, w=520, enter="slideRight", shadow=True, rot=2),
          dict(k="text", t=wt("25", "那"), text="这批视频合计约 8000 万播放", sub="来源：半岛电视台开源组 10/17", x=1290, y=790, size=40, color="yellow")], src="X 网传视频 · Instagram 原帖为 Annahar 文章嵌入截图")
    if V3E:   # IG 只留视频内容区（去头像栏 / View profile / 播放键），不拉伸
        SHOTS[-1]["ov"][0] = dict(k="img", t=T("26"), src="v3/img/e_ig.png", x=1110, y=170, w=360, enter="slideRight", shadow=True, rot=2)
        SHOTS[-1]["src"] = "信源：Instagram 原帖（Annahar 嵌入截图）· X 网传视频"
    # 22（27 句）48.38–50.30：Annahar 原话卡，光标圈「AI Content」+ 红胶囊
    w = save_world("w_quote", blur_bg(load(f"{A}/beach_055.jpg"), 0.35))
    qx, qy, qw = 360, 220, 1200; qk = qw / 1000
    a0, a1, a2, a3 = E["AIC"]; acx, acy = qx + (a0 + a2) / 2 * qk, qy + (a1 + a3) / 2 * qk
    shot("s22", B21, T("28"), I(w), cam((B21, 1.0, 960, 540), (T("28"), 1.07, acx, acy)),
         [dict(k="img", t=B21, src=ELS["quote"][0], x=qx, y=qy, w=qw, enter="pop", shadow=True),
          dict(k="cursor", t=B21 + 0.02, path=[[B21 + 0.02, 1700, 900], [B21 + 0.1, qx + a2 * qk + 10, acy]],
               circle=dict(t=B21 + 0.12, cx=acx, cy=acy, rx=(a2 - a0) / 2 * qk + 40, ry=(a3 - a1) / 2 * qk + 26, dur=0.6, t1=T("28"))),
          dict(k="cap", t=wt("27", "AI"), text="自己标了 AI 内容", color="red", x=1310, y=610, size=60, rot=-2, sfx="pop", kit=True, screen=True)], src="据 Annahar 2026-10-17")
    # 23（28 句）50.30–51.16：Hive 检测页（Annahar 截图），光标移到 99.9%
    hx, hy, hw = 260, 250, 1400; hk = hw / ELS["hive"][1][0]
    hb = blur_bg(load(f"{A}/beach_070.jpg"), 0.35).resize((3840, 2160), Image.LANCZOS)
    hc = load(f"{PUB}/img/hive.png"); hc = hc.resize((hw * 2, round(hc.height * hw * 2 / hc.width)), Image.LANCZOS)
    hb.alpha_composite(hc, (hx * 2, hy * 2)); w = save_world("w_hive", hb, 2)
    tgt = (hx + (16 + 770 * 1400 / 920) * hk, hy + (16 + (147 - 62) * 1400 / 920) * hk)   # 99.9% AI-Generated Video 框中心（截图坐标约 x657–884,y119–176）
    trx, trY = 120 * 1400 / 920 * hk, 34 * 1400 / 920 * hk
    shot("s23", T("28"), T("30"), I(w, 2), cam((T("28"), 1.0, 960, 540), (T("29") - 0.02, 1.03, 960, 540), (T("29") + 0.28, 1.85, tgt[0] - 60, tgt[1] + 40), (T("30"), 1.95, tgt[0] - 60, tgt[1] + 40)),
         [dict(k="cursor", t=T("28") + 0.02, path=[[T("28") + 0.02, 600, 900], [T("28") + 0.18, tgt[0] + trx, tgt[1]]],
               circle=dict(t=T("28") + 0.2, cx=tgt[0], cy=tgt[1], rx=trx + 26, ry=trY + 24, dur=0.55, t1=T("30")), t1=T("30")),
          dict(k="penring", t=T("29") + 0.3, cx=tgt[0], cy=tgt[1], rx=trx + 26, ry=trY + 24),
          dict(k="counter", t=wt("29", "九", 1), t2=wt("29", "九", 2) + 0.2, to=99.9, prefix="AI 概率 ", suffix="%", x=960, y=780, size=72, sfx="pop", kit=True, screen=True)],
         src="据 Annahar · Hive 检测截图", note="s23+s24 合并：圈选单镜停留 ≥2.5s，说到 AI 概率时快推")
    # 25（30 句）53.04–54.70：搬运号把假片当新闻
    w = save_world("w_repost", blur_bg(load(f"{A}/beach_010.jpg"), 0.35))
    shot("s25", T("30"), T("31"), I(w), cam((T("30"), 1.0, 960, 540), (T("31"), 1.07, 760, 500)),
         [dict(k="img", t=T("30"), src=ELS["tv"][0], x=120, y=200, w=900, enter="pop", shadow=True, rot=-2),
          dict(k="img", t=wt("30", "搬"), src=ELS["xrepost"][0], x=1110, y=470, w=700, enter="slideRight", shadow=True, rot=3)], src="B 站 / X 搬运号")
    # 26（31 句）54.70–57.43：小官扶额 + 手推车把「搬运」运走
    w = save_world("w_truck", blur_bg(load(f"{A}/g1_blomahn_f145.png"), 0.32))
    shot("s26", T("31"), T("32"), I(w), cam((T("31"), 1.0, 960, 540), (T("32"), 1.05, 960, 540)),
         [dict(k="img", t=T("31") + 0.04, src="v3/qban/24_facepalm_c2.png", x=200, y=210, w=560, enter="slideLeft"),
          dict(k="move", t=wt("31", "被") - 0.25, t1=T("32") - 0.1, src=ELS["truck"][0], w=520, x0=2000, x1=1080, y=260, x2=2300, tmid=wt("31", "AI") + 0.15)],
         src="手推车：Abraham / Wikimedia Commons · CC0")
    # ===== 解释 =====
    # 27（32 句）57.43–59.47：设问③，BBC 真实漂浮集装箱 + 大问号
    w = vid_world("s27", 2.3, [vlayer(BBC, 18.4, 0.8, (0, 700, 1080, 1308), (0, 0, 1920, 1080))])
    shot("s27", T("32"), T("33"), V(w), cam((T("32"), 1.0, 960, 540), (T("33"), 1.08, 960, 520)),
         [dict(k="qmark", t=wt("32", "上"), x=1500, y=360, size=230, sfx="pop")], src="素材：BBC Verify")
    # 28（33+34 句）59.47–62.09：BBC 片段 + 专家原话卡
    m, s, box = m_panel((0, 0, 1080, 1920), cx=560)
    w = vid_world("s28", 2.8, [vlayer(BBC, 69.2, 0.9, (0, 0, 1080, 1920), box)], bg=0)
    shot("s28", T("33"), T("35"), V(w), cam((T("33"), 1.0, 960, 540), (T("35"), 1.04, 1000, 540)),
         [dict(k="quote", t=wt("33", "说"), title="BBC 采访的专家", text="「不能排除」", x=960, y=270, w=760, accent="gray"),
          dict(k="quote", t=wt("34", "可"), title="", text="「但可能性很低」", x=960, y=520, w=760, accent="red", big=True, sfx="pop")], src="素材：BBC Verify")
    # 29（35+36+37 句）62.09–65.88：空运 vs 海运照片 → 「基本没戏」+ BBC 信源角标
    w = save_world("w_air", blur_bg(load(f"{PH}/plane_orig.jpg").crop(C.PH_PLANE[1]), 0.35))
    PHS = "照片：CC BY 4.0 4300streetcar / CC0 Martin Dörsch"
    base29 = lambda tt: [dict(k="img", t=tt(T("35")), src=ELS["ph_plane"][0], x=90, y=170, w=880, enter="slideLeft", shadow=True, rot=-2),
          dict(k="cap", t=tt(wt("35", "空")), text="一般走空运 ✓", color="green", x=520, y=760, size=56, rot=-2),
          dict(k="img", t=tt(T("35") + 0.1), src=ELS["ph_ship"][0], x=1110, y=260, w=680, enter="slideRight", shadow=True, rot=3),
          dict(k="cross", t=tt(wt("36", "不")), x=1450, y=490, size=300)]
    shot("s29", T("35"), T("37"), I(w), cam((T("35"), 1.0, 960, 540), (T("37"), 1.04, 960, 540)), base29(lambda x: x), src=PHS)
    # 29b（37 句）：同一 world 跳切推近 →「基本没戏」+ BBC 信源（拆开以免单镜 >4s）
    shot("s29b", T("37"), T("38"), I(w), cam((T("37"), 1.22, 960, 470), (T("38"), 1.26, 960, 470)),
         base29(lambda x: T("37") - 1.0) +
         [dict(k="text", t=wt("37", "基"), text="基本没戏", x=960, y=430, size=150, color="white", box=True),
          dict(k="img", t=T("37"), src=("v3/img/bbc_title_blur.png" if V3D else ELS["bbc_title"][0]), x=1290, y=676, w=540, enter="slideRight", shadow=True),
          dict(k="chip", t=T("37"), text="信源：BBC Verify · 10 月 16 日核查", x=1290, y=622)], src=PHS, gray_at=T("37"))
    # ===== 收尾 =====
    # 30（38+39 句）65.88–69.58：小官举手机 + 搜索框打字 →「谁先发的」高亮推近
    w = save_world("w_search", blur_bg(load(f"{A}/beach_030.jpg"), 0.3))
    shot("s30", T("38"), T("40"), I(w), cam((T("38"), 1.0, 960, 540), (T("39") - 0.02, 1.02, 960, 540), (T("39") + 0.3, 1.18, 1180, 470), (T("40"), 1.2, 1180, 470)),
         [dict(k="img", t=T("38") + 0.04, src="v3/qban/29_show_phone_c2.png", x=130, y=200, w=560, enter="slideLeft"),
          dict(k="search", t=T("38"), x=760, y=400, w=900, type0=wt("38", "白"), type1=wt("38", "iPhone") + 0.3, text="白捡 iPhone",
               add=" 谁最先发的？", add0=wt("39", "查"), add1=wt("39", "的"))])
    # 31（40+41 句）69.58–72.70：小官指向观众 + 评论气泡
    w = save_world("w_end", blur_bg(load(f"{A}/bbc_sea_only.jpg"), 0.42))   # 换成蓝色海面底，和上一镜粉色沙滩拉开差别
    row = [("fk_g1", 240), ("fk_beach", 460), ("fk_boat", 680), ("fk_fish", 900)]
    ov = [dict(k="img", t=T("40") + 0.04 * i, src=ELS[n][0], x=x - 100, y=250, w=200, rot=(-4, 3, -2, 4)[i], enter="drop", frame=True) for i, (n, x) in enumerate(row)]
    ov += [dict(k="img", t=T("40"), src="v3/qban/30_point_v2_c3.png", x=1160, y=230, w=600, enter="slideRight"),
           dict(k="text", t=wt("40", "信"), text="你信了哪条？", x=570, y=620, size=84, color="yellow"),
           dict(k="img", t=T("41"), src=ELS["bubble"][0], x=330, y=700, w=140, enter="pop", sfx="pop"),
           dict(k="img", t=T("41") + 0.12, src=ELS["bubble"][0], x=710, y=690, w=120, enter="pop", rot=8)]
    shot("s31", T("40"), TOTAL, I(w), cam((T("40"), 1.0, 960, 540), (TOTAL, 1.06, 1000, 540)), ov)

    if V3F:
        import v3f_patch; v3f_patch.patch(globals())
    # ---- 镜头连续性检查
    for a, b in zip(SHOTS, SHOTS[1:]):
        assert abs(a["t1"] - b["t0"]) < 1e-6, (a["id"], a["t1"], b["id"], b["t0"])
    # ---- 音效：一刀一 whoosh（峰值对切点）+ 叠加层自带 sfx
    SM = AM["sfx"]; WH = ["whoosh_c", "whoosh_d", "whoosh_e", "whoosh_f"]; POP = ["pop_a", "pop_c", "pop_b"]; HIT = ["hit_d", "hit_c"]; CLK = ["click_b", "click_c"]
    VOL = {"whoosh": 0.32, "pop": 0.42, "hit": 0.62, "click": 0.38}
    sfx = []; ci = {"whoosh": 0, "pop": 0, "hit": 0, "click": 0}
    def add(kind, t, align="onset"):
        lst = {"whoosh": WH, "pop": POP, "hit": HIT, "click": CLK}[kind]
        name = lst[ci[kind] % len(lst)]; ci[kind] += 1
        off = SM[name]["peak"] if align == "peak" else 0.0
        sfx.append(dict(t=round(t - off, 3), at=round(t, 3), file=f"v3/sfx/{name}.wav", vol=VOL[kind], kind=kind))
    for sh in SHOTS[1:]:
        add("whoosh", sh["t0"], "peak")
    for sh in SHOTS:
        for o in sh["ov"]:
            if o.get("sfx"):
                t = o.get("click", o["t"]) if o["k"] == "cursor" else o["t"]
                add(o["sfx"], t, "peak" if o["sfx"] == "hit" else "onset")
    sfx.sort(key=lambda x: x["t"])
    # ---- 字幕
    cues = make_subs()
    # ---- BGM 闪避区间（口播句）
    speech = [[s["start"], s["end"]] for s in W["sentences"]]
    data = dict(fps=FPS, total=TOTAL, frames=int(round(TOTAL * FPS)), shots=SHOTS, sfx=sfx, subs=cues, speech=speech,
                vo="v3/audio/vo_v3f.wav" if V3F else "v3/audio/vo_v3d.wav" if V3D else "v3/audio/vo_v3c.wav", bgm=AM["bgm"]["file"], title="满海漂着免费 iPhone？真相拆给你看" if V3D else "霍尔木兹海峡 免费 iPhone？真相拆给你看")
    OUTJ = f"{R}/src/v3f/data/v3f.json" if V3F else f"{R}/src/v3e/data/v3e.json" if V3E else (f"{R}/src/v3d/data/v3d.json" if V3D else f"{R}/src/v3/data/v3.json"); os.makedirs(os.path.dirname(OUTJ), exist_ok=True)
    json.dump(data, open(OUTJ, "w"), ensure_ascii=False, indent=1)
    print("shots", len(SHOTS), "cuts", len(SHOTS) - 1, "sfx", len(sfx), {k: sum(1 for x in sfx if x['kind'] == k) for k in VOL}, "frames", data["frames"])
    for sh in SHOTS: print(sh["id"], sh["t0"], sh["t1"], round(sh["t1"] - sh["t0"], 2))

# ---------------- 字幕（≤10 字/条，关键词上色）----------------
KW_F = {"04": {"是真的": "#4BE38A"}, "09": {"AI": "#FFD84A"}, "18": {"隐形水印": "#FFD84A"}, "19": {"AI工具": "#FF5A45"}, "31": {"被AI骗了": "#FFD84A"}}
KW = {"01": {"霍尔木兹海峡": "#FFD84A", "免费": "#FFD84A", "iPhone": "#FFD84A", "海面": "#FFD84A"}, "02": {"放下": "#FFD84A"}, "03": {"AI": "#FF5A45"},
      "04": {"真沉了": "#4BE38A"}, "05": {"也是真的": "#4BE38A"}, "07": {"也是真的": "#4BE38A"}, "08": {"刷屏": "#FF5A45"},
      "09": {"@Grok": "#FFD84A"}, "10": {"一眼AI": "#FF5A45"}, "12": {"仅泡水": "#FFD84A"}, "14": {"假的": "#FF5A45"},
      "16": {"两组摄像头": "#FF5A45"}, "17": {"全是扭的": "#FF5A45"}, "18": {"隐形水印": "#FFD84A"}, "19": {"OpenAI": "#FF5A45"},
      "20": {"也有": "#FF5A45"}, "21": {"真照片改的": "#FFD84A"}, "22": {"真的吧": "#FFD84A"}, "23": {"人不动": "#FF5A45"},
      "24": {"刚出厂": "#FF5A45"}, "27": {"AI内容": "#FF5A45"}, "29": {"九成九": "#FF5A45"}, "31": {"被AI搬运了": "#FFD84A"},
      "32": {"到底有没有": "#FFD84A"}, "34": {"很低": "#FF5A45"}, "35": {"空运": "#4BE38A"}, "37": {"基本没戏": "#FFD84A"},
      "39": {"谁先发的": "#FFD84A"}, "40": {"信了哪条": "#FFD84A"}, "41": {"评论区": "#FFD84A"}}
def make_subs():
    import re
    PB = "，。？！：；、"
    def units(t): return sum(0 if c == " " else (0.5 if ord(c) < 128 else 1) for c in t)
    words = W["words"]; cues = []
    for s in W["sentences"]:
        sid = s["id"]; toks = [w for w in words if w["id"] == sid]
        # 按标点切小句；每个小句对应若干 token
        clauses, cur = [], ""
        for c in s["text"]:
            if c in PB:
                if cur.strip(): clauses.append(cur.strip() + ("？" if c == "？" else ""))
                cur = ""
            else: cur += c
        if cur.strip(): clauses.append(cur.strip())
        ti = 0
        for cl in clauses:
            body = cl.replace("？", "")
            need_ = re.sub(r"\s", "", body).replace("@", "")
            got = ""; seg = []
            while ti < len(toks) and len(got) < len(need_):
                got += toks[ti]["text"].replace("@", ""); seg.append(toks[ti]); ti += 1
            t0 = seg[0]["start"] if seg else s["start"]; t1 = seg[-1]["end"] if seg else s["end"]
            kw = (KW_F.get(sid) if (V3F and sid in KW_F) else KW.get(sid, {})); flat = need_
            col = [None] * len(flat)
            for k, v in kw.items():
                for m in re.finditer(re.escape(k.replace("@", "")), flat):
                    for q in range(m.start(), m.end()): col[q] = v
            segs, p = [], 0
            for c in cl:
                cc = None
                if c not in " ？@": cc = col[p] if p < len(col) else None; p += 1
                elif c == "@": cc = col[p] if p < len(col) else None
                if segs and segs[-1][1] == cc: segs[-1][0] += c
                else: segs.append([c, cc])
            assert units(cl) <= 13, cl
            cues.append(dict(sid=sid, start=round(max(0, t0 - 0.05), 3), end=round(t1, 3), text=cl, segs=segs))
    for i, c in enumerate(cues):
        nx = cues[i + 1]["start"] if i + 1 < len(cues) else TOTAL
        c["end"] = round(nx if nx - c["end"] < 0.8 else c["end"] + 0.35, 3)
    return cues

if __name__ == "__main__":
    main()
