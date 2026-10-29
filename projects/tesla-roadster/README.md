# 特斯拉 Roadster 科普短视频（B 站 · 差评君风格）

成片：`D:\编程\项目\视频制作\特斯拉Roadster\特斯拉Roadster-v3.mp4`（1920x1080 30fps，89.53s，h264 + AAC 320k 48k，-15.9 LUFS / TP -2.3 dBFS，解码 0 错误）。成片和素材视频不入库。

## 目录
```
remotion/                 Remotion 源码（合成：RoadsterShort=v1，v2，RoadsterShortV3=v3）
  src/v3/                 v3 源码；footage-timeline.json = 镜头入出点 + 混音（对齐工具保存）
  align/                  对齐/混音工具（npm run align → http://localhost:3210），使用说明.md
  scripts/master.mjs      render:master / remix-audio
  SFX-BGM-v3.md           音效/BGM 清单；SFX-v2.md 旧版
  DESCRIPTION.md          投稿简介（BGM 为自制）
voice/v2, voice/v3        配音脚本、选句、对齐、ASR 核对（音频不入库）
notes/                    选题、风格、受众、来源、BGM 候选记录
```
public/ 下的图片、视频、音频不入库（clip-*.mp4、hlive*.mp4、voice*.mp3、sfx/、v3/ 等），需从 PC 项目目录拷回。

## 渲染（V3 当时在 Windows PC：R5 5600 / 16GB / RTX 3080）

这是 89 秒、带 3D 的 V3 实测。约 60 秒的新短片改在盒子上渲，只把成片和两张封面传到 `发布\`（`science-studio/config/workflow_spec.md` §1.1，2026-10-29）。
```
npm run render:master    # 无声画面 + 纯音频 wav + loudnorm(-16 LUFS) + 合成
npm run remix-audio      # 只改了音量/BGM 时用
```
推荐参数（已写进 master.mjs 默认值，可用 RENDER_FLAGS 覆盖）：
`--concurrency=8 --gl=angle --x264-preset=veryfast --offthreadvideo-video-threads=4`

### 基准测试（300 帧，含约 10s 启动；空闲内存约 4.5GB）
| 配置 | 用时 | fps | 峰值内存 |
|---|---|---|---|
| A c8 angle | 43.9s | 6.83 | 7.1GB |
| B c12 angle | 52.8s | 5.68 | 7.2GB（更慢） |
| C c8 vulkan | 41.6s | 7.21 | 6.7GB |
| D c8 angle + hardware-acceleration if-possible | 39.7s | 7.55 | 7.1GB（Windows 下基本无效） |
| **E c8 angle + x264 veryfast** | **39.1s** | **7.66** | 6.45GB |
| F c10 angle + ovt threads 4 + cache 2GB | 40.3s | 7.44 | 5.4GB |

结论：c12 反而慢（CPU 只有 12 线程）；Remotion 无 NVENC 选项，显卡不参与编码。全片画面约 5.5 分钟。

## remix-audio（只重做声音）
1. 在对齐工具里调音量 / 闪避 / BGM 包络，点保存（写入 `src/v3/footage-timeline.json` 的 `audio`）。
2. `npm run remix-audio`：按 JSON 重新渲染纯音频 → loudnorm 到 `audio.lufs`（默认 -16）→ `-c:v copy` 换进现有成片，画面不重编码。
3. 用时约 2 分钟（纯音频渲染仍要逐帧计算）。混好的音频同时在 `out/master-audio.wav`。
