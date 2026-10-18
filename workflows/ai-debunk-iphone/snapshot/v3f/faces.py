import cv2, numpy as np
DET = {}
def detect(img, scale=1.5, thr=0.55):
    h, w = img.shape[:2]; W, H = int(w * scale), int(h * scale)
    key = (W, H)
    if key not in DET: DET[key] = cv2.FaceDetectorYN.create("/workspace/models/yunet.onnx", "", (W, H), thr, 0.3, 5000)
    big = cv2.resize(img, (W, H), interpolation=cv2.INTER_CUBIC)
    _, f = DET[key].detect(big)
    out = []
    if f is not None:
        for r in f:
            x, y, bw, bh = (r[:4] / scale)
            if bw > 40 and bh / bw < 1.0: continue   # 盒子/摄像头模组是方的，人脸框偏高
            out.append((x, y, bw, bh, float(r[-1])))
    return out
def blur_faces(img, faces, k=1.5):
    """每张脸按自身大小：先粗马赛克（约 5×5 格）再高斯，椭圆羽化贴回"""
    if not faces: return img
    out = img.astype(np.float32); h, w = img.shape[:2]
    for x, y, bw, bh, *_ in faces:
        cx, cy = x + bw / 2, y + bh / 2; ax, ay = bw * k / 2 + 4, bh * k / 2 + 6
        x0, y0, x1, y1 = int(max(0, cx - ax - 8)), int(max(0, cy - ay - 8)), int(min(w, cx + ax + 8)), int(min(h, cy + ay + 8))
        if x1 - x0 < 4 or y1 - y0 < 4: continue
        reg = img[y0:y1, x0:x1]; n = 5
        pix = cv2.resize(cv2.resize(reg, (n, max(1, round(n * (y1 - y0) / (x1 - x0)))), interpolation=cv2.INTER_AREA), (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST)
        pix = cv2.GaussianBlur(pix, (0, 0), max(3, bw / 6))
        m = np.zeros((y1 - y0, x1 - x0), np.float32)
        cv2.ellipse(m, (int(cx - x0), int(cy - y0)), (int(ax), int(ay)), 0, 0, 360, 1.0, -1)
        m = cv2.GaussianBlur(m, (0, 0), 2 + bw / 30)[..., None]
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - m) + pix * m
    return out.astype(np.uint8)
