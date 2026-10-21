# 制作配置（v1.1，2026-10-21；规则依据 workflow_spec §1.1）

## 规格
- 抖音竖屏：1080×1920，30 fps，H.264 High，yuv420p，AAC 192k 48 kHz。预览：720×1280（`--scale=0.6667 --crf=23`）。母版 `--crf=18`。
- B 站横屏（如需）：1920×1080，同上参数。
- 响度：母版 loudnorm 两遍，约 −16 LUFS integrated，真峰 ≤ −1.5 dBTP（技术规格，不是创作规则）。
- 字幕：一句一卡（硬规则），下方安全区，同时导出 `.srt`。
- 角标：「丞」朱印，`/workspace/brand/v2/avatar_1_朱印丞.png`，全片统一。

## 渲染路由
| 条件 | 在哪渲 | 怎么做 |
|---|---|---|
| 用户 PC 在线（ListMachines 显示 PC-20260301WTTM connected） | **用户 PC**（Windows，RTX 3080） | 每条命令需用户点批准（见下） |
| PC 离线 | 盒子（8 核 CPU、15 GB RAM、无 GPU、`/usr/bin/google-chrome`） | `npx remotion render ... --gl=angle --concurrency=4` |
| 3D 重渲染 / Blender | 只能用户 PC（盒上无 Blender、无 GPU） | 同 PC 流程；PC 上 Blender 是否安装待确认 |
| ~~720p 片段预览、1 段局部修在盒子~~ | 【已废止 2026-10-21】PC 在线时预览也在 PC | — |

### PC 渲染步骤（v1.1，光遗传学实测：1080 全片 5246 帧 13 分钟）
1. 盒上打源码包（去掉 `node_modules`、`out`，python zipfile）+ 混音 wav + 参数化脚本（模板 `/workspace/optogenetics/pc_pack/render_film_pc.ps1`；新一期复制后改 composition 名、zip 名、混音文件名（模板里写死 `audio\film_mix_v1.wav`）、冒烟帧号，`-Root` 指向 D 盘工程目录）。
2. **传输**：≥30 MB 的 CopyFromBox 会失败 → 盒上切成 ≤4 MB 分块逐个 CopyFromBox，PC 上合并后 `Get-FileHash -Algorithm SHA256` 与盒上 `sha256sum` 比对，一致才继续。
3. **位置**：全部放 `D:\编程\项目\视频制作\作品\<YYYY-MM-DD_选题>\`：`工程\`（源码包、解压后工程、ps1）、`预览\`（720p）、`out\`（1080 成片）、`发布\`（封面、文案、清单）。~~`%USERPROFILE%\<EP>_<版本>\`~~【已废止 2026-10-21，不在 C:\Users\Administrator 下建目录】。
4. **启动**：`Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File render_film_pc.ps1 -Mode 1080 -Root <D盘工程>' -RedirectStandardOutput <log>` 脱离运行；轮询日志看帧进度。单段重渲用 `-Frames a-b`；分段预览可并行起多个 `-Mode 720 -Frames`。
5. PC 环境（2026-10-21 实测）：Node v24.19.0、npm 11.17.0、ffmpeg 9.0、RTX 3080 10GB、桌面 Chrome。脚本自带：解压/依赖幂等跳过、桌面 Chrome 冒烟失败自动切 Headless Shell、gl=angle 失败切 swangle、并发默认 75% 核、ffmpeg 合轨与 ffprobe 核对。
6. 回传：只把小体积预览或抽帧取回盒子质检；>100 MB 母版留 PC，告诉用户 D 盘路径。
7. 换声不重渲画面：`ffmpeg -i 成片.mp4 -i 新混音.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k` 输出新文件名，旧版保留。

## 渲后质检（workflow_spec §1.1-3）
- ffmpeg：`blackdetect`、`freezedetect`、`ebur128`（约 −16 LUFS，真峰 ≤ −1.5 dBTP）、接缝前后 ±0.1 s 峰值查爆音、帧数=时长×fps。
- 抽帧：`ffmpeg -vf fps=1/5` → 每 ≤5 张一组调 `qoderclicn -p -m Qwen3.8-Flash --permission-mode bypass_permissions --attachment ...`，问字幕/人名卡是否出框、黑块、错字、角标是否在。我只汇总 Flash 结论；可疑处用前后 ±0.5 s 再抽帧交 Flash 判是否为滑入滑出瞬间（是则不算硬错）。
- 结果写 `projects/<EP>/review/qc_vN.md`。只自动修硬错。

## 配音（TTS）
- 默认：Fish Audio，模型 **`s2.1-pro-free`**（免费）。按意思段（3–5 句）带前后文生成，只出一条给用户听；音调靠标点/断句在生成时管住；~~分句配音、批量 3 条、事后压音高/大幅变速~~【已废止 2026-10-21】。密钥：环境变量 `FISH_API_KEY`（已存在，2026-10-20 实测 1 句合成成功，余额 −$0.0014 不变）。
- 接口：`POST https://api.fish.audio/v1/tts/stream/with-timestamp`，header `model: s2.1-pro-free`；带逐字时间戳。可复用 `/workspace/zhangxue-water/vo/fish.py` 的 `synth()`。
- 默认音色：`cfd828bdf120410c923fac0056c687c2`（「穆祉尘音色1」，公共库音色；可能是真人克隆，商用授权有风险，待用户定）。音色文档 `/workspace/video-workflows/docs/VOICE-CONFIG.md`。
- 改用付费模型（Drama 3 等）、换音色、充值：先征得用户同意。
- 听审前不对齐画面（硬规则 5）。

## ASR / 时间戳
- faster-whisper 1.2.1（`/workspace/.venv-dy/bin/python`），本地缓存模型 base/small/medium/large-v3（CPU int8）。实测 small 转 3 s 音频约 3 s。
- 用途：逐字时间戳对齐、读音核对。Fish 自带时间戳可作首选，ASR 复核。

## 看片 / 抽帧审查
- 盒上：ffmpeg 抽帧、拼图（`/workspace/tools/watch.py --local` 可出 contact sheet / 开头拼图）；我能直接看 jpg/png，不能直接看视频。
- 省额度：抽帧交 **qoder flash**：`qoderclicn -p -m Qwen3.8-Flash --permission-mode bypass_permissions --attachment <帧或mp4> "<提示词>"`（已登录，2026-10-20 实测读对角标和字幕）。批量模板 `/workspace/tools/qoder_job.sh <dir>`（读 `<dir>/qoder_job.json` 的 atts 与 P，输出 `qoder_b.md`）。
- ~~qoder 结论只当初筛；关键帧我再抽查~~【已废止 2026-10-21】：按上面「渲后质检」，我只汇总 Flash 结论；看不到的写「未确认」。

## 素材与品牌
见 `assets/INDEX.md`。AI 生成画面标「AI 生成」，来源记入 `projects/<EP>/assets/SOURCES.md`。

## 资产库与 Drive 备份（2026-10-20 建）
- 索引库：`db/studio.db`（SQLite + FTS5 trigram，只在盒上读写，**不放进任何同步目录**）。脚本：`scripts/db.py`（表结构）、`ingest_field.py`（采集入库）、`ingest_seed.py`（存量登记）、`search.py`（检索/雷达）、`backup.py`（快照+上传清单）。说明见 `db/README.md`。
- Drive：账号 **<用户 Google Pro 账号（见盒上 config/drive.json）>**（用户确认就是 Pro 账号）。MCP 命名空间用 **`user-Google-drive`**；`user-Google-drive--pro` 是同一个账号，两个都能用。UploadFile 的 connection 填 `user-Google-drive`。
- 根目录「AI科学内容资产中心」id **1JSMXiO93pxGfn-xKvj-fKywx0pCQnJIt**；01–08 子文件夹和 06 下各期文件夹的 id 见 `config/drive.json`。
- 备份流程：`backup.py plan --with-works` → 读 `backup/<时间>/manifest.json`，`skip=false` 的条目逐个 UploadFile（destination.folderId=item.folder_id，name=item.name）→ 每传完一个跑 `backup.py record <path> <drive_id> --folder <folder>`。按 sha256 去重，中间渲染不传，DB 快照按日期命名、不覆盖。
- 配额：连接器读不到，以用户在 drive.google.com/settings/storage 看到的为准。

## 数据闭环（2026-10-21，脚本在 scripts/，库 schema v2）
| 何时 | 命令 |
|---|---|
| 选题/写稿前 | `python3 scripts/search.py insights`（= `insights.py show`） |
| 定发布时间 | `python3 scripts/mark_published.py <EP> --plan 'YYYY-MM-DD HH:MM'` |
| 用户说已发 | `python3 scripts/mark_published.py <EP> --time 'YYYY-MM-DD HH:MM' --url <抖音链接> [--title 实际标题] [--search-first yes\|no]` |
| 定时巡检（每次对话开头/定时任务） | `python3 scripts/due_checkpoints.py [--mark-asked]` → JSON reminders；只把 message 转述给用户 |
| 收到导出表 | `python3 scripts/ingest_metrics.py <xlsx/csv> --work <EP> --checkpoint 2h\|24h\|72h\|7d [--set search_share=0.8 --source '截图…']` |
| 导入后 | `python3 scripts/diagnose.py <EP> [--checkpoint 24h]` → 复盘「## 数据」段（`<!-- DATA:平台:检查点 -->` 可重复覆盖）+ lessons（真实数据） |
| 满 24h 有链接 | `python3 scripts/harvest_comments.py <EP>`（douyin-field-collect，免登录；结果 `data/field/harvest/work<ID>_<时间>/harvest_report.md`） |
| 新数据后 | `python3 scripts/insights.py recompute` |
| 每周 | `python3 scripts/weekly_report.py` → `reviews/weekly/YYYY-Www.md` |
- 表：`metrics_snapshots`（每作品×平台×检查点一行，source 必填，raw_json 存原表）、`retention_curve`（秒→留存 0–1）、`insights`（kind 开头/标题/时长/选题/段落，状态 验证中/已验证/已推翻，n 写明样本）+ `insights_history`；`works` 加 publish_time / planned_publish_time / publish_asked / video_url / checkpoints_done / comments_harvested(_at) / timeline_path；`content_dna` 加 hook_class / topic_class / title_search_first / duration_note（insights 分组用，每期归档时填）。旧 `work_metrics` 保留只读，新数据只进 metrics_snapshots。
- 导出表解析：列名嗅探（横排/竖排/CSV，百分号、万、mm:ss 自动换算）；留存 sheet 需有「时间/秒」+「留存/观看人数占比」列；多作品表用 `--row`。作品名对不上会警告。
- 时间轴：诊断自动找 `vo/cards.json`、`*align*.json`、`footage-timeline.json`、state.json 的 shots 帧区间；也可在 works.timeline_path 指定。
- 测试：设 `STUDIO_DB=/tmp/x.db STUDIO_REVIEWS=/tmp/r STUDIO_FIELD=/tmp/f STUDIO_NOW='2026-10-22 21:00'` 在副本上跑，不碰真库。

## Feedback Engine（2026-10-21，schema v3，说明在 docs/feedback_engine.md）
- **数据源**：创作者中心截图配合 `ingest_screenshot.py`（qoder Qwen3.8-Flash，每批最多 5 张），以及 xlsx 导出配合 `ingest_metrics.py`。抖音开放平台没有授权，只留了 stub `adapters/douyin_openapi.py`。
- **六个指令**：`python3 scripts/feedback.py 复盘最新视频 | 检查最近作品表现 | 最近观众有什么新需求 | 找出近期最值得改进作品 | 对比这期与历史同类 | 根据历史反馈开始下一期选题`
- **审批**：`approve_suggestion.py approve <id>` 只能在用户明确批准后执行。
- **检索**：脚本和分镜阶段先跑 `search.py feedback "<关键词>"`。
- **备份**：`fb_backup.py plan`，然后 UploadFile，再 record、DownloadFile 回读，最后 `verify --readback`。
