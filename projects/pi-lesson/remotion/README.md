# 圆周率学习课 · Remotion 工程（Windows 渲染）

## 环境
- Node 18+，Chrome/Edge
- `npm install`（首次）
- 本机有 ffmpeg（loudnorm 需要）

## 渲染整片 + 响度母版
```bat
cd remotion
npm install
npm run render:master
```
产物：`out/pi-lesson.mp4`（原始）和 `out/pi-lesson-master.mp4`（loudnorm −16 LUFS / −1.5 dBTP）。

只用渲染命令（不加响度）：
```bat
npx remotion render src/index.tsx PiLesson out/pi-lesson-master.mp4 --gl=angle --concurrency=4
```
（若只要一条母版文件，可把输出路径直接写成 master；建议先出 raw 再 loudnorm。）

## 分章预览（加快迭代）
```bat
npx remotion render src/index.tsx PiCh3 out/ch3.mp4 --gl=angle --concurrency=4
```
合成 id：`PiLesson`、`PiCh0` … `PiCh6`。

## 说明
- 1920×1080 · 30fps · 约 330.8 秒（9928+ 帧）
- 配音：`public/pi-lesson-voice.mp3`；词级时间戳：`src/alignment.json`
- 画幅与风格见 `/workspace/pi/step4-storyboard.md`
