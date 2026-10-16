# 在 Windows 上渲染圆周率学习课

## 1. 解压并安装
```bat
cd remotion
npm install
```
需要本机已装 Google Chrome 或 Edge。若 Remotion 找不到浏览器，设置：
```bat
set REMOTION_BROWSER_EXECUTABLE=C:\Program Files\Google\Chrome\Application\chrome.exe
```

## 2. 渲染整片（推荐）
```bat
npm run render:master
```
等价于：
```bat
npx remotion render src/index.tsx PiLesson out/pi-lesson.mp4 --gl=angle --concurrency=4
ffmpeg -y -i out/pi-lesson.mp4 -c:v copy -af loudnorm=I=-16:TP=-1.5:LRA=11 out/pi-lesson-master.mp4
```
- `--gl=angle`：Windows 上更稳的 OpenGL
- `--concurrency=4`：按 RTX 3080 / R5 5600 内存调的，可改成 6–8 试一下
- 成片约 331 秒（5分31秒），1920×1080，30fps

## 3. 分章快速迭代
```bat
npx remotion render src/index.tsx PiCh3 out/ch3.mp4 --gl=angle --concurrency=4
```
合成：`PiLesson`、`PiCh0` … `PiCh6`。

## 4. Studio 预览
```bat
npm run studio
```
