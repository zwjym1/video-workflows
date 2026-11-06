# 制作配置（v1.1，2026-10-21；规则依据 workflow_spec §1.1）

## 规格
- 抖音竖屏：1080×1920，30 fps，H.264 High，yuv420p，AAC 192k 48 kHz。预览：720×1280（`--scale=0.6667 --crf=23`）。母版 `--crf=18`。
- B 站横屏（如需）：1920×1080，同上参数。
- **抖音横版封面 4:3**：1440×1080 PNG（不是 16:9）；竖版封面 1080×1920。模板 `src/Cover.tsx`：`CoverV` 1080×1920，`CoverH` 默认 1440×1080。
- 响度：母版 loudnorm 两遍，约 −16 LUFS integrated，真峰 ≤ −1.5 dBTP（技术规格，不是创作规则）。
- 字幕：一句一卡（硬规则），下方安全区，同时导出 `.srt`。
- 角标：「丞」朱印，`/workspace/brand/v2/avatar_1_朱印丞.png`，全片统一。

## 渲染路由（2026-10-29 改定）
短片默认在**盒子**（助手的 Linux）上渲。~~PC 在线就全部在 PC 渲，含 720p 预览；只有离线才用盒子~~【已废止 2026-10-29】。

| 条件 | 在哪渲 | 怎么做 |
|---|---|---|
| 短片（约 60 秒及以内） | **盒子**（8 核 CPU、15 GB RAM、无 GPU、`/usr/bin/google-chrome`） | 默认，不看 PC 在不在线。预览和成片都在盒上：`npx remotion render ... --gl=angle --concurrency=4`，或该期 `render_box.mjs` |
| 更长的片子、盒上渲不动 | 用户 PC（Windows，RTX 3080） | 每条命令需用户点批准（见下「PC 渲染步骤」） |
| 3D 重渲染 / Blender | 只能用户 PC（盒上无 Blender、无 GPU） | 同 PC 流程；PC 上 Blender 是否安装待确认 |

### 短片交给 PC（2026-10-29）
定稿后只传 3 个文件：成片、两张封面。目录 `D:\编程\项目\视频制作\作品\<YYYY-MM-DD_选题>\发布\`。不传工程、不传预览、不传中间版。
`templates/transfer/make_pc_bundle.sh <TAG> 'D:\编程\项目\视频制作\作品\<YYYY-MM-DD_选题>\发布' <盒上输出目录> 成片 封面 封面`
审片阶段不打包。分块可以暂时落在 PC 的 $HOME，由 `assemble_from_home.ps1` 合并进 `发布\`，不在 `C:\Users\Administrator` 下建工程目录。

### PC 渲染步骤（只给长片、3D、盒上渲不动的；光遗传学实测：1080 全片 5246 帧 13 分钟）
1. 盒上打源码包（去掉 `node_modules`、`out`，python zipfile）+ 混音 wav + 参数化脚本（模板 `/workspace/optogenetics/pc_pack/render_film_pc.ps1`；新一期复制后改 composition 名、zip 名、混音文件名（模板里写死 `audio\film_mix_v1.wav`）、冒烟帧号，`-Root` 指向 D 盘工程目录）。
2. **传输**：≥30 MB 的 CopyFromBox 会失败 → 盒上切成 ≤4 MB 分块逐个 CopyFromBox，PC 上合并后 `Get-FileHash -Algorithm SHA256` 与盒上 `sha256sum` 比对，一致才继续。
3. **位置**：全部放 `D:\编程\项目\视频制作\作品\<YYYY-MM-DD_选题>\`：`工程\`（源码包、解压后工程、ps1）、`预览\`（720p）、`out\`（1080 成片）、`发布\`（封面、文案、清单）。~~`%USERPROFILE%\<EP>_<版本>\`~~【已废止 2026-10-21，不在 C:\Users\Administrator 下建目录】。
4. **启动**：`Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File render_film_pc.ps1 -Mode 1080 -Root <D盘工程>' -RedirectStandardOutput <log>` 脱离运行；轮询日志看帧进度。单段重渲用 `-Frames a-b`；分段预览可并行起多个 `-Mode 720 -Frames`。
5. PC 环境（2026-10-21 实测）：Node v24.19.0、npm 11.17.0、ffmpeg 9.0、RTX 3080 10GB、桌面 Chrome。脚本自带：解压/依赖幂等跳过、桌面 Chrome 冒烟失败自动切 Headless Shell、gl=angle 失败切 swangle、并发默认 75% 核、ffmpeg 合轨与 ffprobe 核对。
6. 回传：只把小体积预览或抽帧取回盒子质检；>100 MB 母版留 PC，告诉用户 D 盘路径。
7. 换声不重渲画面：`ffmpeg -i 成片.mp4 -i 新混音.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k` 输出新文件名，旧版保留。

## 渲前结构闸门（2026-10-29，workflow_spec §5.1）
渲染前跑 `templates/qc/structure_gate.py`，对照 `templates/qc/prerender_checklist.md`。退出码 1（有 FAIL）先改再渲。主观自审限时 15 分钟，和审片官并行。短片在盒上渲；定稿后只用 `templates/transfer/make_pc_bundle.sh` + `assemble_from_home.ps1` 把成片和两张封面打进 `发布\`，审片阶段不打包。渲染路由见上一节。

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

## 字幕：一句一字幕（全局通用，2026-10-21 起所有片必须调用）
- 规则：每张字幕卡只显示一句——按 ，。？！；：、… 切成短句，一屏一句、单行、不换行、不拼接；句末逗号/句号不显示（？！保留）；小数点不切；单句超过 16 字在语义处再拆成前后两张卡（仍各自单行）；第 0 帧就有字幕（H7）。
- 切句+字级对时脚本：`/workspace/science-studio/scripts/subs/oneline.py`
  `python3 scripts/subs/oneline.py --cards <cards.json> --words <asr_chunks.json(含 words 字级时间)> --silences <silences.txt> --out-json <subs.json> --out-srt <subs.srt> --out-ts <remotion/src/subs_oneline.ts> --end <成片时长>`
  对时：用 ASR 字级时间戳把每句句首映射到对应字的发声时刻，邻近停顿（±0.3s）时吸附到停顿；无 ASR 时按字数比例。输出自带校验：任何一卡含逗号/句号或超长即报错退出。
- Remotion 公共组件：`/workspace/science-studio/lib/remotion/OneLineSubtitles.tsx`（复制到工程 `src/common/`，`<OneLineSubtitles t={t} subs={SUBS} fontFamily={...} />`）；禁止再用工程内自写的多行/拼接字幕组件。
- 逐字稿卡片（cards_*.json）可以一卡多句（用于配音段落），但画面字幕只能用 oneline.py 的输出。

## 音效（2026-10-21 起）
- 一律按 config/sound_design_spec.md：先定风格家族，按类别固定电平自动归一，禁跨家族梗音；实现 lib/sound_palette_v1.py。

## Gemini 交接（2026-10-22 新增；只是附加的交接层，spec 和 skill 的方法部分未改）
- 依据：用户 10-22 08:55 / 08:57。从抖音实地采集到逐字稿、第四部分：分镜要点，都由 Gemini 完成（Spark 浏览 + Deep Research）。我们从配音开始接手，并负责入库。
- 文档：`docs/gemini_handoff/`，内含 01_部署方案、02_交接文档、03_提示词集、04_字段格式_gemini_field_v1。Drive 位置：`00_Gemini交接/`（id 记在 `config/drive.json` 的 `handoff_folder`）。
- 每期 Drive 文件命名：`00_数据包_<EP>_<时间>.md`｜`G1_实地_<EP>_<批次>.json`（+摘要 md）｜`G2_选题卡_<EP>`｜`G3_事实表_<EP>`｜`G4_方案与逐字稿_<EP>_v<N>`｜`G5_修订记录_<EP>.md`｜`G6_数据复盘_<EP>_<检查点>`。
- 导出数据包（只读，不采集、不写库）：
  `python3 scripts/export_gemini_pack.py <EP> [--topic N] [--all-candidates] [--q 词…]`
  → `projects/<EP>/handoff/gemini_pack_<EP>_<时间>.md`。之后用 UploadFile 传到 06/<EP>，再跑 `backup.py record`。
- G1 入库（用户下指令后才执行）：
  `python3 scripts/gemini_field_convert.py check <json>` → `convert <json> --out projects/<EP>/research/field_gemini/<批次>` → `ingest_field.py <目录> --topic "<选题>" --label gemini-spark`。
  check 有错误就不转换（退出码 2），把错误清单交给 Gemini，用提示词 E 让它重交。
- 对照验证（上线前一次，用户下指令才执行）：
  `python3 scripts/gemini_field_convert.py diff <json> <douyin-field-collect 输出目录> --out projects/<EP>/research/gemini_vs_script.md`
- 接手前的硬规则复核清单：见 01_部署方案 §5。
