# 环境检查报告（实测，2026-10-20 22:45–22:55 UTC+8）

## 盒子硬件
| 项 | 结果 |
|---|---|
| 系统 | Debian 13 (trixie)，Linux 6.12 x86_64 |
| CPU | 8 核 Intel Xeon |
| 内存 | 15 GiB（可用约 11 GiB），无 swap |
| 磁盘 | 125 GB，已用 30 GB，剩 96 GB |
| GPU | **无**（`nvidia-smi` 不存在） |

## 软件
| 工具 | 结果 |
|---|---|
| Python | 3.13.5；采集/ASR 虚拟环境 `/workspace/.venv-dy` |
| FFmpeg / ffprobe | 7.1.5 ✅ |
| Node / npm | v20.19.2 / 11.21.0 ✅ |
| Remotion | 4.0.536（各工程 node_modules 内）✅ **实测**：zhangxue-water `WaterPlaneVertical` 渲 30 帧 540×960，6.2 s 完成，抽帧正常（有「丞」角标、字幕） |
| Chrome | Google Chrome 155（/usr/bin/google-chrome）✅；无 chromium |
| Blender | ❌ 未安装（3D 重渲染走用户 PC） |
| ASR | faster-whisper 1.2.1 + 本地模型 base/small/medium/large-v3 ✅ **实测** small 转写 3 s 音频，结果「这是一具免费模型的环境测试」（"句"→"具"，同音误识，说明 ASR 结果需复核） |
| Fish TTS | `FISH_API_KEY` 存在 ✅ **实测** `s2.1-pro-free` 合成 1 句（3.13 s），余额前后都是 −$0.001380，未花钱。付费模型（Drama 3）需充值 |
| qoder | `qoderclicn`（/usr/local/bin）已登录 ✅ **实测** `-m Qwen3.8-Flash --attachment 帧.jpg` 正确读出右上「丞」印章、底部字幕、非黑屏，用时 13 s |
| yt-dlp | 2026.08.19 ✅ |
| git | 2.47.3 ✅；`/workspace/video-workflows` 最新提交 97923ab |
| gh CLI | 已装但**未登录**；之前推 GitHub 走的是 cursor-github 连接 |

## 抖音采集（douyin-field-collect）实测
- 采集虚拟环境原先缺 `playwright`（requirements 里有）→ 已在 `/workspace/.venv-dy` 补装 playwright（只这一个包，用系统 Chrome，没下 Chromium）。
- `dy_search.py "光遗传学" -n 3 --src so,sm`：so.douyin.com available（44 条），神马 available（1 条）；返回 3 条同题视频（最高 5.9w 赞）。用时约 45 s。
- `dy_collect.py sug "光遗传学"`：搜索联想 available（如「光遗传学怎么治疗抑郁症」「光遗传学基本原理」）。
- `dy_collect.py video 7693192655819679338 -n 20`：详情 available，平台字幕 missing（这条没有平台字幕），评论 partial 20/154（到上限），comment_top_rec / detail_suggest_words available；未开 `--media/--browse`。用时约 4 s。
- 没有触发验证码或 403。产物在 `data/env_test/`。

## 看视频 / 抽帧
- 我不能直接播放视频；能看 jpg/png。路线：ffmpeg 抽帧/拼图（`/workspace/tools/watch.py --local`）→ qoder flash 初筛 → 我抽查关键帧。

## 用户 Windows PC
- ListMachines：PC-20260301WTTM（machineId 37d9228d-…）**此刻在线**；本次按要求**没有在 PC 上执行任何命令**。
- 已知：RTX 3080；之前用过 Chrome + npm + ffmpeg 渲 Remotion（render_pc.ps1）。待首期确认：Node/ffmpeg 版本、并发最佳值、是否装 Blender、已有 3D 工程/模型位置。

## 文件导出/同步
- 盒子 → PC：CopyFromBox（≤100 MiB/个，大包用分片，参考 /workspace/pcsync）；PC → 盒子：CopyToBox。
- 聊天发文件（SendToUser，由主代理执行）；Google Drive / Gmail 连接可用（UploadFile）；GitHub 走 cursor-github。

## 不可用/待补
1. GPU、Blender：盒上没有 → 3D 重渲染只能用 PC。
2. gh 未登录（不影响，cursor-github 可用）。
3. qoder 看片提示词模板未定稿（首期定）。
4. Fish 付费模型需充值（默认免费模型不受影响）。
5. 默认音色可能涉及真人克隆授权风险，待用户决定。
