# Tesla Roadster 横屏短视频 · Remotion 成片工程

**状态：关键帧 + 低清 scrub 预览已出，等待用户确认后再全片 master 渲染。**

## 规格
- 画幅：1920×1080 · 16:9 · 30fps · 主发 B站横屏
- 时长：1915 frames ≈ **63.83s**（口播 63.66s + 尾）
- 风格：轻资讯短视频（真机发布会素材 + 定格转 3D），**不是**浙大学长科普 / 小学讲题风
- Composition：`RoadsterShort`（另有独立 `TA` / `TB` 拉长转场）

## 交付物（先审这些）
| 路径 | 说明 |
|---|---|
| `frames/*.jpg` | 全片 23 张关键帧（每镜 + 转场 start/mid/end） |
| `sheets/contact-all.jpg` | 总览拼图 |
| `sheets/contact-transition-A.jpg` | 风扇转场 7 帧 |
| `sheets/contact-transition-B.jpg` | 推进器转场 7 帧 |
| `sheets/contact-shots.jpg` | 非 3D 镜 |
| `out/scrub-preview.mp4` | 960×540 低清 scrub（约 4.1MB，含配音） |

## 口播与字幕
- 音频：`public/voice.mp3` ← `voice/tesla-voice.mp3`
- 对齐：`public/alignment.json` + `src/captions.json`（按标点拆句，屏上无标点，单行）
- 价格句已更新：**售价没公布，订金最高二十五万美元。**

## 分镜时间（frame @30fps）
| Shot | frames | 秒 | 内容 |
|---|---|---|---|
| S01 | 0–96 | 0–3.2 | 飞越卡车钩子 |
| S02 | 96–191 | 3.2–6.4 | 不是特效 / 也不是AI |
| S03 | 191–307 | 6.4–10.2 | 示意弹幕卡 |
| S04 | 307–393 | 10.2–13.1 | 两套系统 |
| TA | 393–855 | 13.1–28.5 | 定格→风扇 3D（拉长 orbit/xray/flow ≈14.6s） |
| TB | 855–1408 | 28.5–46.9 | 定格→推进器 3D（≈17.8s） |
| S08 | 1408–1537 | 46.9–51.2 | 左右对比总结 |
| S09 | 1537–1836 | 51.2–61.2 | 2028 / 封闭场地 / 订金卡 |
| S10 | 1836–1915 | 61.2–63.8 | 你敢坐吗 |

## 已知缺口
1. 弹幕为示意卡片，非真实截图。
2. 3D 车模为示意（非官方 Roadster），推进器段轮廓约 92% 重合。
3. 原片多为 720p，放大到 1080 夜景偏糊。
4. S08 左右面板复用 preview-3d 气流静帧（内含旧转场字幕），与全局口播字幕并存。
5. hliveA/B 实拍 live 段仅约 1s，转场前半段 live 较短后进入定格。
6. **未做 master 全片渲染**——等用户批关键帧。

## 命令
```bash
cd /workspace/topics/tesla-roadster/remotion
npm run stills          # 重抽关键帧
# 用户批准后：
# remotion render src/index.tsx RoadsterShort out/roadster-master.mp4 --gl=angle --concurrency=2
```
