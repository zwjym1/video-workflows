"""V3f 人脸打码：v3f.json 里所有视频 world + 图片（world / img 叠加层，qban 贴纸除外）逐帧 YuNet 检测，±3 帧并集，椭圆马赛克+高斯。
只写新文件 fb_*；json 改指向新文件。"""
import json, os, sys, subprocess, numpy as np, cv2
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__)); from faces import detect, blur_faces
R = "/workspace/iphone-fake/v2/remotion"; PUB = f"{R}/public"; J = f"{R}/src/v3f/data/v3f.json"
LOG = {}
def pill(f):
    """BBC 台标胶囊（饱和蓝 + 左侧绿点）逐帧检测 → 局部强模糊"""
    b, g, r = f[..., 0].astype(int), f[..., 1].astype(int), f[..., 2].astype(int)
    m = ((b > 170) & (r < 90) & (g < 110)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8); out = f
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a > 250 and w > 2.2 * h and h > 10:
            x0, y0, x1, y1 = max(0, x - int(1.2 * h) - 8), max(0, y - 8), min(f.shape[1], x + w + 8), min(f.shape[0], y + h + 8)
            out = out.copy() if out is f else out
            out[y0:y1, x0:x1] = cv2.GaussianBlur(out[y0:y1, x0:x1], (0, 0), 14)
    return out
def do_video(src):
    out = src.replace("v3/clips/", "v3/clips/fb_")
    p = f"{PUB}/{src}"; W, H = 1920, 1080
    fps = 30
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    dets = [detect(f) for f in fr]
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                            "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", f"{PUB}/{out}"], stdin=subprocess.PIPE)
    nf = 0
    for i, f in enumerate(fr):
        fs = [d for j in range(max(0, i - 3), min(len(fr), i + 4)) for d in dets[j]]
        nf += bool(dets[i]); enc.stdin.write(pill(blur_faces(f, fs)).tobytes())
    enc.stdin.close(); enc.wait()
    return src, out, nf, len(fr), max((len(d) for d in dets), default=0)
SKIP = {"v3/img/w_mag.webp", "v3/img/f_w_mag.webp", "v3/img/w_text.webp", "v3/img/f_fk_boat.png", "v3/img/lens_text.png"}   # 小船假图：没有人，检测到的是 iPhone 摄像头模组（误检）
def do_img(src):
    if src in SKIP: return src, src, 0
    p = f"{PUB}/{src}"; im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im is None: return src, src, 0
    bgr = im[..., :3] if im.shape[2] == 4 else im
    f = detect(np.ascontiguousarray(bgr))
    if im.shape[2] == 4: f = [d for d in f if im[int(d[1] + d[3] / 2), int(d[0] + d[2] / 2), 3] > 0]
    if not f: return src, src, 0
    b = blur_faces(np.ascontiguousarray(bgr), f)
    if im.shape[2] == 4: b = np.dstack([b, im[..., 3]])
    d, n = os.path.split(src); out = f"{d}/fb_{os.path.splitext(n)[0]}.png"
    cv2.imwrite(f"{PUB}/{out}", b); return src, out, len(f)
if __name__ == "__main__":
    d = json.load(open(J))
    vids = sorted({s["world"]["src"] for s in d["shots"] if s["world"]["type"] == "video"})
    imgs = sorted({s["world"]["src"] for s in d["shots"] if s["world"]["type"] == "image"} |
                  {o["src"] for s in d["shots"] for o in s["ov"] if o.get("src", "").startswith("v3/img/")} |
                  {x for s in d["shots"] for o in s["ov"] for x in o.get("items", [])})
    rep = {}
    with Pool(6) as pool:
        for src, out, nf, n, mx in pool.imap_unordered(do_video, vids): rep[src] = out; LOG[src] = dict(out=out, frames_with_faces=nf, frames=n, max_faces=mx); print(src, LOG[src], flush=True)
        for src, out, nf in pool.imap_unordered(do_img, imgs):
            if out != src: rep[src] = out
            LOG[src] = dict(out=out, faces=nf); print(src, LOG[src], flush=True)
    for s in d["shots"]:
        s["world"]["src"] = rep.get(s["world"]["src"], s["world"]["src"])
        for o in s["ov"]:
            if o.get("src") in rep: o["src"] = rep[o["src"]]
            if "items" in o: o["items"] = [rep.get(x, x) for x in o["items"]]
    json.dump(d, open(J, "w"), ensure_ascii=False, indent=1)
    json.dump(LOG, open("/workspace/iphone-fake/v2/v3f/faceblur_log.json", "w"), ensure_ascii=False, indent=1)
