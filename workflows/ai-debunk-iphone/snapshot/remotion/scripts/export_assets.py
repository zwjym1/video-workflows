"""从 preview/compose.py 导出 Remotion 用素材：
  public/plates/<shot>.webp      无字幕/无标注/视频窗口挖空 的底板（beat 镜头为「揭之前」）
  public/plates/<shot>_beat.webp 该镜「揭」那一拍新增的标注层（透明）
  public/clips/<shot>.mp4        预裁好的静音视频片段（尺寸=窗口尺寸，已含慢放/去色）
  src/data/shots.json, src/data/subs.json
"""
import sys, os, json, subprocess, re
sys.path.insert(0, "/workspace/iphone-fake/v2/preview")
import compose as C
from PIL import Image, ImageChops, ImageFilter

V2 = "/workspace/iphone-fake/v2"
R = f"{V2}/remotion"
PUB = f"{R}/public"
FPS = 30
W = json.load(open(f"{V2}/vo/words.json"))
SENT = {s["id"]: s for s in W["sentences"]}
G1 = f"{V2}/source/pc_raw/x_blomahn_.mp4"
BBC = f"{V2}/source/bbc_verify_c52e9zwd2vx8o_1080x1920.mp4"
BEACH = f"{V2}/source/beach_fake_x_cuichenghao_2111241316801847763_720x1280.mp4"
for p in (G1, BBC, BEACH):
    if not os.path.exists(p):
        alt = p.replace("/v2/source/", "/source/")
        assert os.path.exists(alt), p
G1, BBC, BEACH = [p if os.path.exists(p) else p.replace("/v2/source/", "/source/") for p in (G1, BBC, BEACH)]

# 镜头起止（storyboard v6，按 words.json）
TC = [("01",0,1.89),("02",1.89,4.71),("03",4.71,7.53),("04",7.53,9.78),("05",9.78,12.04),("06",12.04,14.87),
      ("07",14.87,17.69),("08",17.69,20.57),("09",20.57,22.74),("10",22.74,26.49),("11",26.49,28.01),
      ("12a",28.01,30.75),("12b",30.75,32.59),("13",32.59,35.15),("14",35.15,37.75),("15",37.75,40.59),
      ("16",40.59,42.51),("17",42.51,45.59),("18",45.59,48.42),("19",48.42,51.03),("20",51.03,53.03),
      ("21",53.03,56.93),("22",56.93,60.83),("23",60.83,62.23),("24",62.23,65.61),("25",65.61,67.99),
      ("26",67.99,72.27),("27",72.27,74.88),("28",74.88,78.88),("29",78.88,82.96),("30",82.96,None)]
TOTAL = W["total_sec"]

# 视频窗口：shot -> 片段列表 [(src, start, rate, gray)]；按镜头时长自动截取
VID = {
    "01": [(G1, 0.0, 1.0, False)], "02": [(G1, 1.89, 1.0, False)],
    "03": "special",
    "04": [(BBC, 8.9, 0.8, False)], "05": [(BBC, 16.0, 1.0, False)], "06": [(BBC, 41.3, 1.0, False)],
    "08": [(BEACH, 0.0, 0.8, False)], "09": [(BEACH, 2.3, 0.8, False)], "10": [(BEACH, 4.04, 0.8, False)],
    "18": [(G1, 5.3, 0.5, False)],
    "20": [(BEACH, 0.0, 1.0, False)], "21": [(BEACH, 2.0, 0.8, False)], "22": [(BEACH, 4.9, 0.75, False)],
    "23": [(BEACH, 4.0, 0.8, False)], "25": [(BBC, 18.4, 0.7, False)], "26": [(BBC, 69.2, 0.8, False)],
}
ZOOM = {"25": 1.1}
CROP18 = C.G1_18_CROP
# 揭的那一拍：shot -> (句子 id, 字, 第几次出现)
BEAT = {"03": ("03", "A", 1), "12b": ("12", "两", 1), "13": ("13", "扭", 1), "16": ("16", "也", 1),
        "18": ("18", "人", 1), "21": ("21", "自", 1), "24": ("24", "被", 1), "27": ("27", "海", 1)}
SFX = []  # (time, file, vol)

def word_time(sid, ch, occ=1):
    n = 0
    for w in W["words"]:
        if w["id"] == sid and w["text"] == ch:
            n += 1
            if n == occ:
                return w["start"]
    raise KeyError((sid, ch))

def render(sid, beat=True, hole=False):
    C.RM.update({"sub": False, "notes": False, "hole": hole, "beat": beat, "danmaku": False})
    C.REG.clear(); C.HOLES.clear(); C.SUBLOG.clear()
    im = C.SHOTS[sid]()
    return im, list(C.HOLES), list(C.SUBLOG)

def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)

def make_clip(sid, dur, hole, out):
    w, h = hole["w"], hole["h"]
    segs = VID[sid]
    def vf_for(src, rate, gray, crop=None, zoom=1.0):
        f = []
        if crop:
            x0, y0, x1, y1 = crop; f.append(f"crop={x1-x0}:{y1-y0}:{x0}:{y0}")
        f.append(f"scale={w}*{zoom}:{h}*{zoom}:force_original_aspect_ratio=increase:flags=lanczos")
        f.append(f"crop={w}:{h}")
        if gray: f.append("hue=s=0")
        f.append(f"setpts=PTS/{rate}" if rate != 1 else "setpts=PTS")
        f.append(f"fps={FPS}")
        f.append("unsharp=5:5:0.6")
        return ",".join(f)
    enc = ["-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    pad = 0.4
    if sid == "03":
        bt = word_time("03", "A") - 4.71
        a = out + ".a.mp4"; b = out + ".b.mp4"
        ff(["-ss", "4.71", "-t", f"{bt:.3f}", "-i", G1, "-vf", vf_for(G1, 1.0, False), *enc, a])
        rest = dur - bt + pad
        ff(["-ss", "4.4", "-t", f"{rest*0.8:.3f}", "-i", BBC, "-vf", vf_for(BBC, 0.8, True), *enc, b])
        lst = out + ".txt"; open(lst, "w").write(f"file '{a}'\nfile '{b}'\n")
        ff(["-f", "concat", "-safe", "0", "-i", lst, *enc, out]); [os.remove(p) for p in (a, b, lst)]
        return
    src, start, rate, gray = segs[0]
    crop = None
    if hole["kind"] == "full": crop = C.G1_B_CROP
    if sid == "18": crop = CROP18
    ff(["-ss", f"{start}", "-t", f"{(dur+pad)*rate:.3f}", "-i", src, "-vf", vf_for(src, rate, gray, crop, ZOOM.get(sid, 1.0)), "-t", f"{dur+pad:.3f}", *enc, out])

def to_webp(im, path, lossless=False):
    im.save(path, "WEBP", quality=92, method=6, lossless=lossless)

def main():
    shots = []
    sublog = {}
    for i, (sid, t0, t1) in enumerate(TC):
        t1 = TOTAL if t1 is None else t1
        dur = t1 - t0
        hole_on = sid in VID
        full, holes, sl = render(sid, beat=True, hole=hole_on)
        sublog[sid] = sl
        rec = {"id": sid, "start": t0, "end": t1, "from": round(t0 * FPS), "plate": f"plates/{sid}.webp", "holes": holes}
        if sid in BEAT:
            pre, _, _ = render(sid, beat=False, hole=hole_on)
            diff = ImageChops.difference(full, pre)
            m = diff.convert("RGB").split(); m = ImageChops.lighter(ImageChops.lighter(m[0], m[1]), m[2])
            ma = ImageChops.difference(full.getchannel("A"), pre.getchannel("A"))
            m = ImageChops.lighter(m, ma).point(lambda v: 255 if v > 10 else 0).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(1.5))
            ov = full.copy(); ov.putalpha(ImageChops.multiply(m, full.getchannel("A")))
            bbox = m.getbbox()
            to_webp(pre, f"{PUB}/plates/{sid}.webp")
            to_webp(ov, f"{PUB}/plates/{sid}_beat.webp")
            sidx, ch, occ = BEAT[sid]
            rec.update({"beat": {"t": word_time(sidx, ch, occ), "img": f"plates/{sid}_beat.webp", "bbox": bbox}})
        else:
            to_webp(full, f"{PUB}/plates/{sid}.webp")
        if hole_on:
            assert len(holes) == 1, (sid, holes)
            make_clip(sid, dur, holes[0], f"{PUB}/clips/{sid}.mp4")
            rec["clip"] = f"clips/{sid}.mp4"
        shots.append(rec); print(sid, round(dur, 2), "hole" if hole_on else "", "beat" if "beat" in rec else "", flush=True)
    os.makedirs(f"{R}/src/data", exist_ok=True)
    json.dump({"fps": FPS, "total": TOTAL, "frames": int(round(TOTAL * FPS)), "shots": shots}, open(f"{R}/src/data/shots.json", "w"), ensure_ascii=False, indent=1)
    json.dump(sublog, open(f"{R}/scripts/sublog.json", "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
