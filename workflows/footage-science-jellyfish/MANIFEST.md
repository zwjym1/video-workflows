# MANIFEST · 火箭水母工作流快照（footage-science-workflow-v1）

生成：2026-10-29（UTC+8）。包里的相对路径 = 仓库里的目标路径，直接按原路径放进 `video-workflows` 新分支即可。对比基准：`main`（4c07add）。

共 339 个文件，1.48 MB：新增 335、修改 4、与 main 相同 0。

## 合并说明
- **建议分支**：从 `main` 开新分支（如 `cursor/footage-science-jellyfish-workflow`）。如果 `cursor/miniature-anim-workflow-08a7` 先合进 main，会在 `README.md`（同一张表相邻行）和 `VERSIONS.md`（同一张表末尾）出现文本冲突，两边的行都保留即可。
- `science-studio/config/workflow_spec.md`：本包版本与 miniature 分支里的版本**逐字相同**（都是盒上最新版），两个分支都合时不会冲突。
- 打标签：`footage-science-workflow-v1`。
- 媒体、渲染、node_modules、备份一律不入库（见文末「排除」）。

## 密钥扫描
- 扫描规则：`sk-`/`ghp_`/`gho_`/`github_pat_`/`AKIA`/`AIza`/`xox[bp]-`/`Bearer `/`api[_-]?key\s*[=:]`/`token\s*[=:]`/`secret`/`password`/`cookie`/邮箱/32+ 位十六进制串，逐个人工复核。
- **未发现 API key、token、cookie、密码。** Fish key 只从环境变量 `FISH_API_KEY` 读（`vo/fish_lib.py`）。
- **已去掉 1 处个人信息**：`science-studio/config/production_config.md` 第 54 行原来是用户的 Google 账号邮箱，已换成 main 里同样的占位符 `<用户 Google Pro 账号（见盒上 config/drive.json）>`。
- 保留的 32 位十六进制串是 Fish 公开音色 ID（`906524…`、`cfd828…`）和文件 sha256，不是密钥；`science-studio/tools/review/README.md` 里只有截断的机器 ID `0376e70a-…`。


## 修改的文件（相对 main 的 diff）

### `README.md`
```diff
--- main:README.md
+++ new:README.md
@@ -30,9 +30,11 @@
 | `topics-workflow/` | 选题采集系统 v2、文案系统 v2、口播自检清单、抖音实地硬规则、field 模板、前期 SOP | `/workspace/topics/workflow/` |
 | `science-studio/` | 资产库和数据闭环：scripts/（含 Feedback Engine）、config/（workflow_spec、production_config）、docs/feedback_engine.md、adapters/（开放平台 stub）、reports/、projects/、reviews/ | `/workspace/science-studio/`（`db/studio.db` 不入库） |
 | `templates/render/` | PC 渲染 ps1 模板（光遗传学全片 1080 实测 13 分钟），以及 README | 来源 `/workspace/optogenetics/pc_pack/` |
-| `templates/transfer/` | 大文件分块传输：盒上 `split_for_pc.sh` 切块，PC 上 `merge_on_pc.ps1` 合并并校验 sha256 | — |
-| `templates/qc/` | `qc_render.sh` 跑黑场、冻帧、响度、帧数和接缝峰值机检；`contact_sheet_stills.sh` 生成抽帧联系表 | — |
+| `templates/transfer/` | 大文件分块传输：盒上 `split_for_pc.sh` 切块，PC 上 `merge_on_pc.ps1` 合并并校验 sha256；通用版 `make_pc_bundle.sh` + `assemble_from_home.ps1`（PC 上在 $HOME/下载/桌面自动找分块，按 sha256 校验，只新建不删除，2026-10-29） | — |
+| `templates/qc/` | `qc_render.sh` 跑黑场、冻帧、响度、帧数和接缝峰值机检；`contact_sheet_stills.sh` 生成抽帧联系表；`structure_gate.py` + `prerender_checklist.md` 渲前结构闸门（2026-10-29） | — |
+| `templates/review/`、`templates/state/` | 审片官一次交接单（时限 + 停止规则）；`stage_log.py` 给 STATE.md 记阶段用时（2026-10-29） | — |
 | `templates/audio/`、`templates/vo/` | 混音（film_mix）、配音拼接（stitch_v2）、ASR 抽查脚本 | 来源 `/workspace/optogenetics/audio`、`/workspace/optogenetics/vo` |
+| `workflows/footage-science-jellyfish/` | 实拍热点科普（火箭水母款）：网友/官方实拍逐镜署名 + 程序示意图 → Fish 整稿一条配音 → 抖音热歌 BGM（切点吸附强拍、−8 dB 闪避）→ 一句一字幕 → 盒上渲染 → 渲前结构闸门 → 自检 + 审片官 → 竖横两封面 + 「丞」朱印。标签 `footage-science-workflow-v1`；配套 `science-studio/tools/review/`（审片系统）、`templates/qc/structure_gate.py`、`templates/transfer/make_pc_bundle.sh`、`docs/效率审计_2026-10-29.md` | 来源 `/workspace/science-studio/projects/EP-20261029-01/` |
 | `skills/`、`workflows/`、`projects/`、`docs/` | 2026-10-18/19 的旧版 skill、Roadster 和 iPhone 模板、示例工程、运营文档（保留，未改） | — |
 
 模板里写死了光遗传学那期的 composition 名、zip 名和混音文件名。新一期复制后照 `science-studio/config/production_config.md` 的「PC 渲染步骤」改。
```

### `VERSIONS.md`
```diff
--- main:VERSIONS.md
+++ new:VERSIONS.md
@@ -16,6 +16,7 @@
 | `roadster-v3` | **v3 定稿**：播放器卡死修复、用户定稿的 footage-timeline.json、render:master / remix-audio；成片 特斯拉Roadster-v3.mp4 |
 | `roadster-workflow-v1` | 「热点科普（Roadster 款）」工作流模板冻结版：workflows/hot-science-roadster/（README、params.json、V3 终版源码快照）。原定标签名 roadster-v1 已被 Roadster 第一版占用，所以改用这个名字 |
 | `ai-debunk-v1` | 「AI 辟谣拆解（iPhone 款）」工作流模板冻结版：workflows/ai-debunk-iphone/（README、params.json、v3f_naming.md、V3f 源码和打码/OCR/配音脚本快照） |
+| `footage-science-workflow-v1` | 「实拍热点科普（火箭水母款）」工作流模板冻结版：workflows/footage-science-jellyfish/（README、params.json、EP-20261029-01 源码快照，不含媒体）+ science-studio/tools/review（审片系统）、tools/dy_hot_bgm.py、lib/sound_palette_v1.py、scripts/subs/oneline.py、lib/remotion/OneLineSubtitles.tsx + templates/qc/structure_gate.py、templates/transfer/make_pc_bundle.sh、templates/review、templates/state + docs/效率审计_2026-10-29.md。2026-10-29 |
 
 ## 怎么退回某个版本
```

### `science-studio/config/production_config.md`
```diff
--- main:science-studio/config/production_config.md
+++ new:science-studio/config/production_config.md
@@ -3,6 +3,7 @@
 ## 规格
 - 抖音竖屏：1080×1920，30 fps，H.264 High，yuv420p，AAC 192k 48 kHz。预览：720×1280（`--scale=0.6667 --crf=23`）。母版 `--crf=18`。
 - B 站横屏（如需）：1920×1080，同上参数。
+- **抖音横版封面 4:3**：1440×1080 PNG（不是 16:9）；竖版封面 1080×1920。模板 `src/Cover.tsx`：`CoverV` 1080×1920，`CoverH` 默认 1440×1080。
 - 响度：母版 loudnorm 两遍，约 −16 LUFS integrated，真峰 ≤ −1.5 dBTP（技术规格，不是创作规则）。
 - 字幕：一句一卡（硬规则），下方安全区，同时导出 `.srt`。
 - 角标：「丞」朱印，`/workspace/brand/v2/avatar_1_朱印丞.png`，全片统一。
@@ -78,3 +79,28 @@
 - **审批**：`approve_suggestion.py approve <id>` 只能在用户明确批准后执行。
 - **检索**：脚本和分镜阶段先跑 `search.py feedback "<关键词>"`。
 - **备份**：`fb_backup.py plan`，然后 UploadFile，再 record、DownloadFile 回读，最后 `verify --readback`。
+
+## 字幕：一句一字幕（全局通用，2026-10-21 起所有片必须调用）
+- 规则：每张字幕卡只显示一句——按 ，。？！；：、… 切成短句，一屏一句、单行、不换行、不拼接；句末逗号/句号不显示（？！保留）；小数点不切；单句超过 16 字在语义处再拆成前后两张卡（仍各自单行）；第 0 帧就有字幕（H7）。
+- 切句+字级对时脚本：`/workspace/science-studio/scripts/subs/oneline.py`
+  `python3 scripts/subs/oneline.py --cards <cards.json> --words <asr_chunks.json(含 words 字级时间)> --silences <silences.txt> --out-json <subs.json> --out-srt <subs.srt> --out-ts <remotion/src/subs_oneline.ts> --end <成片时长>`
+  对时：用 ASR 字级时间戳把每句句首映射到对应字的发声时刻，邻近停顿（±0.3s）时吸附到停顿；无 ASR 时按字数比例。输出自带校验：任何一卡含逗号/句号或超长即报错退出。
+- Remotion 公共组件：`/workspace/science-studio/lib/remotion/OneLineSubtitles.tsx`（复制到工程 `src/common/`，`<OneLineSubtitles t={t} subs={SUBS} fontFamily={...} />`）；禁止再用工程内自写的多行/拼接字幕组件。
+- 逐字稿卡片（cards_*.json）可以一卡多句（用于配音段落），但画面字幕只能用 oneline.py 的输出。
+
+## 音效（2026-10-21 起）
+- 一律按 config/sound_design_spec.md：先定风格家族，按类别固定电平自动归一，禁跨家族梗音；实现 lib/sound_palette_v1.py。
+
+## Gemini 交接（2026-10-22 新增；只是附加的交接层，spec 和 skill 的方法部分未改）
+- 依据：用户 10-22 08:55 / 08:57。从抖音实地采集到逐字稿、第四部分：分镜要点，都由 Gemini 完成（Spark 浏览 + Deep Research）。我们从配音开始接手，并负责入库。
+- 文档：`docs/gemini_handoff/`，内含 01_部署方案、02_交接文档、03_提示词集、04_字段格式_gemini_field_v1。Drive 位置：`00_Gemini交接/`（id 记在 `config/drive.json` 的 `handoff_folder`）。
+- 每期 Drive 文件命名：`00_数据包_<EP>_<时间>.md`｜`G1_实地_<EP>_<批次>.json`（+摘要 md）｜`G2_选题卡_<EP>`｜`G3_事实表_<EP>`｜`G4_方案与逐字稿_<EP>_v<N>`｜`G5_修订记录_<EP>.md`｜`G6_数据复盘_<EP>_<检查点>`。
+- 导出数据包（只读，不采集、不写库）：
+  `python3 scripts/export_gemini_pack.py <EP> [--topic N] [--all-candidates] [--q 词…]`
+  → `projects/<EP>/handoff/gemini_pack_<EP>_<时间>.md`。之后用 UploadFile 传到 06/<EP>，再跑 `backup.py record`。
+- G1 入库（用户下指令后才执行）：
+  `python3 scripts/gemini_field_convert.py check <json>` → `convert <json> --out projects/<EP>/research/field_gemini/<批次>` → `ingest_field.py <目录> --topic "<选题>" --label gemini-spark`。
+  check 有错误就不转换（退出码 2），把错误清单交给 Gemini，用提示词 E 让它重交。
+- 对照验证（上线前一次，用户下指令才执行）：
+  `python3 scripts/gemini_field_convert.py diff <json> <douyin-field-collect 输出目录> --out projects/<EP>/research/gemini_vs_script.md`
+- 接手前的硬规则复核清单：见 01_部署方案 §5。
```

### `science-studio/config/workflow_spec.md`
```diff
--- main:science-studio/config/workflow_spec.md
+++ new:science-studio/config/workflow_spec.md
@@ -108,7 +108,7 @@
 
 ## 9. 数据闭环（2026-10-21 起）
 抖音没有接口，数据只来自用户导出的创作者中心 xlsx（或截图转录），只存真数、写来源，不估不编。
-1. **选题、写稿前**先读 `python3 scripts/search.py insights`。只有标「已验证」的规律能当依据，标「验证中」的只当线索。
+1. **选题、写稿时**可参考 `python3 scripts/search.py insights`，但后台数据只作低权重参考（用户 2026-10-21 定），选题仍按 §A 原方法为主；「验证中」的只当线索。
 2. **发布前**：`mark_published.py <EP> --plan '时间'` 记下计划发布时间。计划时间过了 3 小时还没发，就问用户一次。
 3. **发布后**：用户告知后跑 `mark_published.py <EP> --time '实际时间' --url <链接> [--search-first yes|no]`。
 4. **检查点**：`due_checkpoints.py` 输出到期提醒的 JSON，类型包括 2h/24h/72h 导数、采评论、缺链接、缺发布时间、问是否已发。按提醒请用户导出数据，然后：
@@ -124,4 +124,4 @@
 2. **结论口径**：只和作品自身的历史比、和账号同档作品比（排名或分位）。不设固定增长阈值，不说「平台算法规律」。每条发现都要写六项：现象、依据、原因加其他解释、可信度、建议、下一轮实验。
 3. **时间段诊断**：只在平台标注了低谷时才做，精度 ±1–2s，并对到逐字稿和镜头上。没有逐秒数值时，不说「第 N 秒掉了 X%」。
 4. **建议与经验库**：建议默认是「待批」，用户批准后才进 lessons。假设被否定后保留「已否定」状态，不删。
-5. **选题和脚本阶段**：先跑 `feedback.py 根据历史反馈开始下一期选题 --topic <词>` 和 `search.py feedback`。
+5. **选题和脚本阶段**：`feedback.py 根据历史反馈开始下一期选题` 和 `search.py feedback` 只作低权重参考，不主导选题（用户 2026-10-21 定）；选题按 §A 原方法。
```

## 文件清单（按目录）

### `(根目录)/` — 3 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `README.md` | 修改 | 9170 | main 版 + 新增/改 4 行 |
| `VERSIONS.md` | 修改 | 3691 | main 版 + 新增标签行 |
| `MANIFEST.md` | 新增 | 68854 | 本文件 |

### `docs/` — 1 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `docs/效率审计_2026-10-29.md` | 新增 | 11191 | 本次新写：效率审计 |

### `science-studio/config/` — 3 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `science-studio/config/production_config.md` | 修改 | 13651 | /workspace/science-studio/config/production_config.md |
| `science-studio/config/sound_design_spec.md` | 新增 | 6830 | /workspace/science-studio/config/sound_design_spec.md |
| `science-studio/config/workflow_spec.md` | 修改 | 15910 | /workspace/science-studio/config/workflow_spec.md |

### `science-studio/lib/remotion/` — 1 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `science-studio/lib/remotion/OneLineSubtitles.tsx` | 新增 | 1533 | /workspace/science-studio/lib/remotion/OneLineSubtitles.tsx |

### `science-studio/lib/` — 1 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `science-studio/lib/sound_palette_v1.py` | 新增 | 11654 | /workspace/science-studio/lib/sound_palette_v1.py |

### `science-studio/scripts/subs/` — 1 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `science-studio/scripts/subs/oneline.py` | 新增 | 8105 | /workspace/science-studio/scripts/subs/oneline.py |

### `science-studio/tools/` — 1 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `science-studio/tools/dy_hot_bgm.py` | 新增 | 13122 | /workspace/science-studio/tools/dy_hot_bgm.py |

### `science-studio/tools/review/` — 31 个文件：审片系统（review.py、lib、config、prompts、PC 抽帧脚本）

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `science-studio/tools/review/README.md` | 新增 | 5628 | /workspace/science-studio/tools/review/README.md |
| `science-studio/tools/review/calibrate.py` | 新增 | 5210 | /workspace/science-studio/tools/review/calibrate.py |
| `science-studio/tools/review/calibrate_v2.py` | 新增 | 5359 | /workspace/science-studio/tools/review/calibrate_v2.py |
| `science-studio/tools/review/config/lexicon_plain.txt` | 新增 | 196 | /workspace/science-studio/tools/review/config/lexicon_plain.txt |
| `science-studio/tools/review/config/lexicon_terms.txt` | 新增 | 334 | /workspace/science-studio/tools/review/config/lexicon_terms.txt |
| `science-studio/tools/review/config/rubric.json` | 新增 | 4260 | /workspace/science-studio/tools/review/config/rubric.json |
| `science-studio/tools/review/config/style_model.json` | 新增 | 370 | /workspace/science-studio/tools/review/config/style_model.json |
| `science-studio/tools/review/ledger.py` | 新增 | 4434 | /workspace/science-studio/tools/review/ledger.py |
| `science-studio/tools/review/lib/asr.py` | 新增 | 3411 | /workspace/science-studio/tools/review/lib/asr.py |
| `science-studio/tools/review/lib/bgm_compare.py` | 新增 | 7984 | /workspace/science-studio/tools/review/lib/bgm_compare.py |
| `science-studio/tools/review/lib/bgmfit.py` | 新增 | 7228 | /workspace/science-studio/tools/review/lib/bgmfit.py |
| `science-studio/tools/review/lib/cutquality.py` | 新增 | 17328 | /workspace/science-studio/tools/review/lib/cutquality.py |
| `science-studio/tools/review/lib/focus_review.py` | 新增 | 1562 | /workspace/science-studio/tools/review/lib/focus_review.py |
| `science-studio/tools/review/lib/focus_run.py` | 新增 | 11042 | /workspace/science-studio/tools/review/lib/focus_run.py |
| `science-studio/tools/review/lib/focus_validate.py` | 新增 | 8796 | /workspace/science-studio/tools/review/lib/focus_validate.py |
| `science-studio/tools/review/lib/merge.py` | 新增 | 18499 | /workspace/science-studio/tools/review/lib/merge.py |
| `science-studio/tools/review/lib/objective.py` | 新增 | 18778 | /workspace/science-studio/tools/review/lib/objective.py |
| `science-studio/tools/review/lib/sheets.py` | 新增 | 2770 | /workspace/science-studio/tools/review/lib/sheets.py |
| `science-studio/tools/review/lib/shotreview.py` | 新增 | 6656 | /workspace/science-studio/tools/review/lib/shotreview.py |
| `science-studio/tools/review/lib/subjective.py` | 新增 | 2494 | /workspace/science-studio/tools/review/lib/subjective.py |
| `science-studio/tools/review/pc/pc_frames.ps1` | 新增 | 1617 | /workspace/science-studio/tools/review/pc/pc_frames.ps1 |
| `science-studio/tools/review/pc/pc_proxy.ps1` | 新增 | 1727 | /workspace/science-studio/tools/review/pc/pc_proxy.ps1 |
| `science-studio/tools/review/prompts/focus_cuts.md` | 新增 | 2199 | /workspace/science-studio/tools/review/prompts/focus_cuts.md |
| `science-studio/tools/review/prompts/focus_cuts_late.md` | 新增 | 2496 | /workspace/science-studio/tools/review/prompts/focus_cuts_late.md |
| `science-studio/tools/review/prompts/focus_cuts_late_v3.md` | 新增 | 2495 | /workspace/science-studio/tools/review/prompts/focus_cuts_late_v3.md |
| `science-studio/tools/review/prompts/focus_seg.md` | 新增 | 1815 | /workspace/science-studio/tools/review/prompts/focus_seg.md |
| `science-studio/tools/review/prompts/persona_review.md` | 新增 | 4103 | /workspace/science-studio/tools/review/prompts/persona_review.md |
| `science-studio/tools/review/review.py` | 新增 | 4608 | /workspace/science-studio/tools/review/review.py |
| `science-studio/tools/review/run_edit_bgm_corpus.py` | 新增 | 2389 | /workspace/science-studio/tools/review/run_edit_bgm_corpus.py |
| `science-studio/tools/review/run_objective_corpus.py` | 新增 | 960 | /workspace/science-studio/tools/review/run_objective_corpus.py |
| `science-studio/tools/review/run_subjective_corpus.sh` | 新增 | 618 | /workspace/science-studio/tools/review/run_subjective_corpus.sh |

### `templates/qc/` — 2 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `templates/qc/prerender_checklist.md` | 新增 | 2927 | 本次新写：渲前检查清单 |
| `templates/qc/structure_gate.py` | 新增 | 6033 | 本次新写：渲前结构闸门（H1–H6） |

### `templates/review/` — 1 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `templates/review/审片官交接单模板.md` | 新增 | 2771 | 本次新写：审片官一次交接单 + 停止规则 |

### `templates/state/` — 1 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `templates/state/stage_log.py` | 新增 | 2146 | 本次新写：STATE 阶段计时 |

### `templates/transfer/` — 2 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `templates/transfer/assemble_from_home.ps1` | 新增 | 3517 | 本次新写：PC 端找块、校验、合并 |
| `templates/transfer/make_pc_bundle.sh` | 新增 | 4024 | 本次新写：通用 PC 分块打包 |

### `workflows/footage-science-jellyfish/` — 2 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/README.md` | 新增 | 7319 | 本次新写：工作流模板说明 |
| `workflows/footage-science-jellyfish/params.json` | 新增 | 4441 | 本次新写：实测参数 |

### `workflows/footage-science-jellyfish/snapshot/` — 2 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/STATE.md` | 新增 | 3765 | <EP>/STATE.md |
| `workflows/footage-science-jellyfish/snapshot/state.json` | 新增 | 14529 | <EP>/state.json |

### `workflows/footage-science-jellyfish/snapshot/assets/` — 1 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/assets/SOURCES.md` | 新增 | 104 | <EP>/assets/SOURCES.md |

### `workflows/footage-science-jellyfish/snapshot/audio/` — 33 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/01_Proof(Slowed).json` | 新增 | 3024 | <EP>/audio/bgm/01_Proof(Slowed).json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/01_Proof(Slowed).strong_beat.json` | 新增 | 12082 | <EP>/audio/bgm/01_Proof(Slowed).strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/01_咏春_(氛围版)（Cover_七朵组合）.json` | 新增 | 4071 | <EP>/audio/bgm/01_咏春_(氛围版)（Cover_七朵组合）.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/01_咏春_(氛围版)（Cover_七朵组合）.strong_beat.json` | 新增 | 17656 | <EP>/audio/bgm/01_咏春_(氛围版)（Cover_七朵组合）.strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/02_一切都在变好（生命力BGM）.json` | 新增 | 2070 | <EP>/audio/bgm/02_一切都在变好（生命力BGM）.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/02_一切都在变好（生命力BGM）.strong_beat.json` | 新增 | 5395 | <EP>/audio/bgm/02_一切都在变好（生命力BGM）.strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/02_远去的列车.json` | 新增 | 4062 | <EP>/audio/bgm/02_远去的列车.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/02_远去的列车.strong_beat.json` | 新增 | 17448 | <EP>/audio/bgm/02_远去的列车.strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/03_Heroes_3.json` | 新增 | 2525 | <EP>/audio/bgm/03_Heroes_3.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/03_Heroes_3.strong_beat.json` | 新增 | 8686 | <EP>/audio/bgm/03_Heroes_3.strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/03_无尽幸福.json` | 新增 | 2964 | <EP>/audio/bgm/03_无尽幸福.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/03_无尽幸福.strong_beat.json` | 新增 | 9899 | <EP>/audio/bgm/03_无尽幸福.strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/04_雨日思绪（雨の日の想い）（剪辑版2）.json` | 新增 | 2571 | <EP>/audio/bgm/04_雨日思绪（雨の日の想い）（剪辑版2）.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/04_雨日思绪（雨の日の想い）（剪辑版2）.strong_beat.json` | 新增 | 6732 | <EP>/audio/bgm/04_雨日思绪（雨の日の想い）（剪辑版2）.strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/05_Proof(Slowed).strong_beat.json` | 新增 | 12082 | <EP>/audio/bgm/05_Proof(Slowed).strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/chart.json` | 新增 | 22702 | <EP>/audio/bgm/chart.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/chart.md` | 新增 | 3743 | <EP>/audio/bgm/chart.md |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/index.json` | 新增 | 10756 | <EP>/audio/bgm/index.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/index.md` | 新增 | 573 | <EP>/audio/bgm/index.md |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm/pick2.log` | 新增 | 323 | <EP>/audio/bgm/pick2.log |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2.log` | 新增 | 274 | <EP>/audio/bgm2.log |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/01_ditto(氛围感).json` | 新增 | 2672 | <EP>/audio/bgm2/01_ditto(氛围感).json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/01_ditto(氛围感).strong_beat.json` | 新增 | 7599 | <EP>/audio/bgm2/01_ditto(氛围感).strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/02_here_with_me_(Tove_Ball_Remix).json` | 新增 | 3583 | <EP>/audio/bgm2/02_here_with_me_(Tove_Ball_Remix).json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/02_here_with_me_(Tove_Ball_Remix).strong_beat.json` | 新增 | 13890 | <EP>/audio/bgm2/02_here_with_me_(Tove_Ball_Remix).strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/03_Heroes_3.json` | 新增 | 2527 | <EP>/audio/bgm2/03_Heroes_3.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/03_Heroes_3.strong_beat.json` | 新增 | 8686 | <EP>/audio/bgm2/03_Heroes_3.strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/04_Proof(Slowed).json` | 新增 | 3026 | <EP>/audio/bgm2/04_Proof(Slowed).json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/04_Proof(Slowed).strong_beat.json` | 新增 | 12082 | <EP>/audio/bgm2/04_Proof(Slowed).strong_beat.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/chart.json` | 新增 | 22698 | <EP>/audio/bgm2/chart.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/chart.md` | 新增 | 3743 | <EP>/audio/bgm2/chart.md |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/index.json` | 新增 | 12599 | <EP>/audio/bgm2/index.json |
| `workflows/footage-science-jellyfish/snapshot/audio/bgm2/index.md` | 新增 | 691 | <EP>/audio/bgm2/index.md |

### `workflows/footage-science-jellyfish/snapshot/deliver/` — 19 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/deliver/SHA256SUMS.txt` | 新增 | 578 | <EP>/deliver/SHA256SUMS.txt |
| `workflows/footage-science-jellyfish/snapshot/deliver/v5旧版/SHA256SUMS_v5.txt` | 新增 | 577 | <EP>/deliver/v5旧版/SHA256SUMS_v5.txt |
| `workflows/footage-science-jellyfish/snapshot/deliver/v5旧版/发布文案_v5.md` | 新增 | 2458 | <EP>/deliver/v5旧版/发布文案_v5.md |
| `workflows/footage-science-jellyfish/snapshot/deliver/v5旧版/审片_返修单_v5.md` | 新增 | 2359 | <EP>/deliver/v5旧版/审片_返修单_v5.md |
| `workflows/footage-science-jellyfish/snapshot/deliver/v5旧版/素材来源_v5.md` | 新增 | 1424 | <EP>/deliver/v5旧版/素材来源_v5.md |
| `workflows/footage-science-jellyfish/snapshot/deliver/v6b旧版/SHA256SUMS_v6b.txt` | 新增 | 578 | <EP>/deliver/v6b旧版/SHA256SUMS_v6b.txt |
| `workflows/footage-science-jellyfish/snapshot/deliver/v6b旧版/审片_返修单_v6b.md` | 新增 | 2999 | <EP>/deliver/v6b旧版/审片_返修单_v6b.md |
| `workflows/footage-science-jellyfish/snapshot/deliver/v6c旧版/SHA256SUMS_v6c.txt` | 新增 | 193 | <EP>/deliver/v6c旧版/SHA256SUMS_v6c.txt |
| `workflows/footage-science-jellyfish/snapshot/deliver/v6c旧版/审片_返修单_v6c.md` | 新增 | 2069 | <EP>/deliver/v6c旧版/审片_返修单_v6c.md |
| `workflows/footage-science-jellyfish/snapshot/deliver/v6d未采用/审片_返修单_v6d.md` | 新增 | 2953 | <EP>/deliver/v6d未采用/审片_返修单_v6d.md |
| `workflows/footage-science-jellyfish/snapshot/deliver/v6e旧版/SHA256SUMS_v6e.txt` | 新增 | 578 | <EP>/deliver/v6e旧版/SHA256SUMS_v6e.txt |
| `workflows/footage-science-jellyfish/snapshot/deliver/v6e旧版/审片_返修单_v6e.md` | 新增 | 3282 | <EP>/deliver/v6e旧版/审片_返修单_v6e.md |
| `workflows/footage-science-jellyfish/snapshot/deliver/v6f旧版/SHA256SUMS_v6f.txt` | 新增 | 578 | <EP>/deliver/v6f旧版/SHA256SUMS_v6f.txt |
| `workflows/footage-science-jellyfish/snapshot/deliver/v6f旧版/审片_返修单_v6f.md` | 新增 | 1750 | <EP>/deliver/v6f旧版/审片_返修单_v6f.md |
| `workflows/footage-science-jellyfish/snapshot/deliver/v6g旧版/SHA256SUMS_v6g.txt` | 新增 | 578 | <EP>/deliver/v6g旧版/SHA256SUMS_v6g.txt |
| `workflows/footage-science-jellyfish/snapshot/deliver/v6g旧版/审片_返修单_v6g.md` | 新增 | 1343 | <EP>/deliver/v6g旧版/审片_返修单_v6g.md |
| `workflows/footage-science-jellyfish/snapshot/deliver/发布文案.md` | 新增 | 2471 | <EP>/deliver/发布文案.md |
| `workflows/footage-science-jellyfish/snapshot/deliver/审片_返修单_v6h.md` | 新增 | 1160 | <EP>/deliver/审片_返修单_v6h.md |
| `workflows/footage-science-jellyfish/snapshot/deliver/素材来源.md` | 新增 | 1494 | <EP>/deliver/素材来源.md |

### `workflows/footage-science-jellyfish/snapshot/footage/` — 2 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/footage/clips.py` | 新增 | 4908 | <EP>/footage/clips.py |
| `workflows/footage-science-jellyfish/snapshot/footage/clips_meta.json` | 新增 | 3311 | <EP>/footage/clips_meta.json |

### `workflows/footage-science-jellyfish/snapshot/publish/` — 2 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/publish/发布文案.md` | 新增 | 2471 | <EP>/publish/发布文案.md |
| `workflows/footage-science-jellyfish/snapshot/publish/发布文案_v6b草稿.md` | 新增 | 2497 | <EP>/publish/发布文案_v6b草稿.md |

### `workflows/footage-science-jellyfish/snapshot/remotion/` — 16 个文件：Remotion 工程源码（JellyFilm、封面、组件、render_box.mjs）

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/remotion/package-lock.json` | 新增 | 132438 | <EP>/remotion/package-lock.json |
| `workflows/footage-science-jellyfish/snapshot/remotion/package.json` | 新增 | 590 | <EP>/remotion/package.json |
| `workflows/footage-science-jellyfish/snapshot/remotion/remotion.config.ts` | 新增 | 242 | <EP>/remotion/remotion.config.ts |
| `workflows/footage-science-jellyfish/snapshot/remotion/scripts/render_box.mjs` | 新增 | 1468 | <EP>/remotion/scripts/render_box.mjs |
| `workflows/footage-science-jellyfish/snapshot/remotion/scripts/stills.mjs` | 新增 | 978 | <EP>/remotion/scripts/stills.mjs |
| `workflows/footage-science-jellyfish/snapshot/remotion/src/Cover.tsx` | 新增 | 2097 | <EP>/remotion/src/Cover.tsx |
| `workflows/footage-science-jellyfish/snapshot/remotion/src/Film.tsx` | 新增 | 2303 | <EP>/remotion/src/Film.tsx |
| `workflows/footage-science-jellyfish/snapshot/remotion/src/Root.tsx` | 新增 | 500 | <EP>/remotion/src/Root.tsx |
| `workflows/footage-science-jellyfish/snapshot/remotion/src/Shots.tsx` | 新增 | 22448 | <EP>/remotion/src/Shots.tsx |
| `workflows/footage-science-jellyfish/snapshot/remotion/src/common/OneLineSubtitles.tsx` | 新增 | 1533 | <EP>/remotion/src/common/OneLineSubtitles.tsx |
| `workflows/footage-science-jellyfish/snapshot/remotion/src/common/theme.tsx` | 新增 | 4309 | <EP>/remotion/src/common/theme.tsx |
| `workflows/footage-science-jellyfish/snapshot/remotion/src/data/cuts_v1.ts` | 新增 | 586 | <EP>/remotion/src/data/cuts_v1.ts |
| `workflows/footage-science-jellyfish/snapshot/remotion/src/data/kt.ts` | 新增 | 704 | <EP>/remotion/src/data/kt.ts |
| `workflows/footage-science-jellyfish/snapshot/remotion/src/data/subs_v1.ts` | 新增 | 3266 | <EP>/remotion/src/data/subs_v1.ts |
| `workflows/footage-science-jellyfish/snapshot/remotion/src/index.ts` | 新增 | 104 | <EP>/remotion/src/index.ts |
| `workflows/footage-science-jellyfish/snapshot/remotion/tsconfig.json` | 新增 | 219 | <EP>/remotion/tsconfig.json |

### `workflows/footage-science-jellyfish/snapshot/research/` — 22 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/research/facts.md` | 新增 | 4871 | <EP>/research/facts.md |
| `workflows/footage-science-jellyfish/snapshot/research/field/search_jelly.json` | 新增 | 3433 | <EP>/research/field/search_jelly.json |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7699839721425390882/collect.json` | 新增 | 5002 | <EP>/research/field/v/douyin_7699839721425390882/collect.json |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7699839721425390882/report.md` | 新增 | 3119 | <EP>/research/field/v/douyin_7699839721425390882/report.md |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7699881476779184315/collect.json` | 新增 | 5009 | <EP>/research/field/v/douyin_7699881476779184315/collect.json |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7699881476779184315/report.md` | 新增 | 3391 | <EP>/research/field/v/douyin_7699881476779184315/report.md |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7699893173379690105/collect.json` | 新增 | 5062 | <EP>/research/field/v/douyin_7699893173379690105/collect.json |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7699893173379690105/report.md` | 新增 | 3409 | <EP>/research/field/v/douyin_7699893173379690105/report.md |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7699974715628178738/collect.json` | 新增 | 4920 | <EP>/research/field/v/douyin_7699974715628178738/collect.json |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7699974715628178738/report.md` | 新增 | 3084 | <EP>/research/field/v/douyin_7699974715628178738/report.md |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7700034022797287887/collect.json` | 新增 | 4961 | <EP>/research/field/v/douyin_7700034022797287887/collect.json |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7700034022797287887/report.md` | 新增 | 3308 | <EP>/research/field/v/douyin_7700034022797287887/report.md |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7700114551659924779/collect.json` | 新增 | 4815 | <EP>/research/field/v/douyin_7700114551659924779/collect.json |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7700114551659924779/report.md` | 新增 | 2700 | <EP>/research/field/v/douyin_7700114551659924779/report.md |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7700174253680856347/collect.json` | 新增 | 4756 | <EP>/research/field/v/douyin_7700174253680856347/collect.json |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7700174253680856347/report.md` | 新增 | 2841 | <EP>/research/field/v/douyin_7700174253680856347/report.md |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7700455457504152859/collect.json` | 新增 | 4707 | <EP>/research/field/v/douyin_7700455457504152859/collect.json |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7700455457504152859/report.md` | 新增 | 3176 | <EP>/research/field/v/douyin_7700455457504152859/report.md |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7700520059432602943/collect.json` | 新增 | 5861 | <EP>/research/field/v/douyin_7700520059432602943/collect.json |
| `workflows/footage-science-jellyfish/snapshot/research/field/v/douyin_7700520059432602943/report.md` | 新增 | 3403 | <EP>/research/field/v/douyin_7700520059432602943/report.md |
| `workflows/footage-science-jellyfish/snapshot/research/footage_sources.md` | 新增 | 1424 | <EP>/research/footage_sources.md |
| `workflows/footage-science-jellyfish/snapshot/research/sun_calc.py` | 新增 | 1489 | <EP>/research/sun_calc.py |

### `workflows/footage-science-jellyfish/snapshot/review/` — 3 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/review/changes.md` | 新增 | 102 | <EP>/review/changes.md |
| `workflows/footage-science-jellyfish/snapshot/review/design_cuts.json` | 新增 | 552 | <EP>/review/design_cuts.json |
| `workflows/footage-science-jellyfish/snapshot/review/返修单_v6d.md` | 新增 | 2953 | <EP>/review/返修单_v6d.md |

### `workflows/footage-science-jellyfish/snapshot/review_runs/` — 120 个文件：自检（jelly_v*）和审片官（jellyfish_v*）各版报告、返修单、verdict

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v2/bgmfit.json` | 新增 | 707 | /workspace/science-studio/tools/review/out/jelly_v2/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v2/cutquality_design.json` | 新增 | 2958 | /workspace/science-studio/tools/review/out/jelly_v2/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v2/verdict.json` | 新增 | 3088 | /workspace/science-studio/tools/review/out/jelly_v2/verdict.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v2/返修单.md` | 新增 | 2018 | /workspace/science-studio/tools/review/out/jelly_v2/返修单.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v3/cutquality_design.json` | 新增 | 2852 | /workspace/science-studio/tools/review/out/jelly_v3/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v3/focus_run.json` | 新增 | 5930 | /workspace/science-studio/tools/review/out/jelly_v3/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v3/focus_validated.json` | 新增 | 1695 | /workspace/science-studio/tools/review/out/jelly_v3/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v4/bgmfit.json` | 新增 | 698 | /workspace/science-studio/tools/review/out/jelly_v4/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v4/cutquality_design.json` | 新增 | 2667 | /workspace/science-studio/tools/review/out/jelly_v4/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v4/focus_run.json` | 新增 | 6587 | /workspace/science-studio/tools/review/out/jelly_v4/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v4/focus_validated.json` | 新增 | 2396 | /workspace/science-studio/tools/review/out/jelly_v4/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5/bgmfit.json` | 新增 | 707 | /workspace/science-studio/tools/review/out/jelly_v5/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5/cutquality_design.json` | 新增 | 2859 | /workspace/science-studio/tools/review/out/jelly_v5/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5/focus_run.json` | 新增 | 5247 | /workspace/science-studio/tools/review/out/jelly_v5/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5/focus_validated.json` | 新增 | 2254 | /workspace/science-studio/tools/review/out/jelly_v5/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5/verdict.json` | 新增 | 3812 | /workspace/science-studio/tools/review/out/jelly_v5/verdict.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5/返修单.md` | 新增 | 2359 | /workspace/science-studio/tools/review/out/jelly_v5/返修单.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5r/bgmfit.json` | 新增 | 707 | /workspace/science-studio/tools/review/out/jelly_v5r/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5r/cutquality_design.json` | 新增 | 2859 | /workspace/science-studio/tools/review/out/jelly_v5r/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5r/focus_run.json` | 新增 | 5247 | /workspace/science-studio/tools/review/out/jelly_v5r/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5r/focus_validated.json` | 新增 | 2254 | /workspace/science-studio/tools/review/out/jelly_v5r/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5r/verdict.json` | 新增 | 4561 | /workspace/science-studio/tools/review/out/jelly_v5r/verdict.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5r/返修单.md` | 新增 | 2693 | /workspace/science-studio/tools/review/out/jelly_v5r/返修单.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v5r/返修单_runs2.md` | 新增 | 2487 | /workspace/science-studio/tools/review/out/jelly_v5r/返修单_runs2.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6/bgmfit.json` | 新增 | 706 | /workspace/science-studio/tools/review/out/jelly_v6/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6/cutquality_design.json` | 新增 | 3518 | /workspace/science-studio/tools/review/out/jelly_v6/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6/focus_run.json` | 新增 | 5745 | /workspace/science-studio/tools/review/out/jelly_v6/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6/focus_validated.json` | 新增 | 1949 | /workspace/science-studio/tools/review/out/jelly_v6/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6/verdict.json` | 新增 | 4364 | /workspace/science-studio/tools/review/out/jelly_v6/verdict.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6/返修单.md` | 新增 | 2865 | /workspace/science-studio/tools/review/out/jelly_v6/返修单.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6b/bgmfit.json` | 新增 | 708 | /workspace/science-studio/tools/review/out/jelly_v6b/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6b/cutquality_design.json` | 新增 | 3017 | /workspace/science-studio/tools/review/out/jelly_v6b/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6b/focus_run.json` | 新增 | 4814 | /workspace/science-studio/tools/review/out/jelly_v6b/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6b/focus_validated.json` | 新增 | 1143 | /workspace/science-studio/tools/review/out/jelly_v6b/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6b/verdict.json` | 新增 | 4486 | /workspace/science-studio/tools/review/out/jelly_v6b/verdict.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6b/返修单.md` | 新增 | 2579 | /workspace/science-studio/tools/review/out/jelly_v6b/返修单.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6b/返修单_runs2.md` | 新增 | 2308 | /workspace/science-studio/tools/review/out/jelly_v6b/返修单_runs2.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6c/cutquality_design.json` | 新增 | 2984 | /workspace/science-studio/tools/review/out/jelly_v6c/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6c/focus_run.json` | 新增 | 5314 | /workspace/science-studio/tools/review/out/jelly_v6c/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6c/focus_validated.json` | 新增 | 2331 | /workspace/science-studio/tools/review/out/jelly_v6c/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6d/cutquality_design.json` | 新增 | 2983 | /workspace/science-studio/tools/review/out/jelly_v6d/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6d/focus_run.json` | 新增 | 5503 | /workspace/science-studio/tools/review/out/jelly_v6d/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6d/focus_validated.json` | 新增 | 2179 | /workspace/science-studio/tools/review/out/jelly_v6d/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6e/cutquality_design.json` | 新增 | 2903 | /workspace/science-studio/tools/review/out/jelly_v6e/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6e/focus_run.json` | 新增 | 5348 | /workspace/science-studio/tools/review/out/jelly_v6e/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6e/focus_validated.json` | 新增 | 1444 | /workspace/science-studio/tools/review/out/jelly_v6e/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6f/cutquality_design.json` | 新增 | 2903 | /workspace/science-studio/tools/review/out/jelly_v6f/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6f/focus_run.json` | 新增 | 5614 | /workspace/science-studio/tools/review/out/jelly_v6f/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6f/focus_validated.json` | 新增 | 1935 | /workspace/science-studio/tools/review/out/jelly_v6f/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6g/cutquality_design.json` | 新增 | 2902 | /workspace/science-studio/tools/review/out/jelly_v6g/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6g/focus_run.json` | 新增 | 5806 | /workspace/science-studio/tools/review/out/jelly_v6g/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6g/focus_validated.json` | 新增 | 2417 | /workspace/science-studio/tools/review/out/jelly_v6g/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6h/cutquality_design.json` | 新增 | 2903 | /workspace/science-studio/tools/review/out/jelly_v6h/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6h/focus_run.json` | 新增 | 6792 | /workspace/science-studio/tools/review/out/jelly_v6h/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jelly_v6h/focus_validated.json` | 新增 | 1591 | /workspace/science-studio/tools/review/out/jelly_v6h/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6b/bgmfit.json` | 新增 | 722 | /workspace/science-studio/tools/review/out/jellyfish_v6b/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6b/cutquality_design.json` | 新增 | 3253 | /workspace/science-studio/tools/review/out/jellyfish_v6b/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6b/design_cuts.json` | 新增 | 554 | /workspace/science-studio/tools/review/out/jellyfish_v6b/design_cuts.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6b/extra_3-10/focus_run.json` | 新增 | 7987 | /workspace/science-studio/tools/review/out/jellyfish_v6b/extra_3-10/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6b/extra_3-10/focus_validated.json` | 新增 | 2040 | /workspace/science-studio/tools/review/out/jellyfish_v6b/extra_3-10/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6b/focus_seg_3-10.md` | 新增 | 3356 | /workspace/science-studio/tools/review/out/jellyfish_v6b/focus_seg_3-10.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6b/verdict.json` | 新增 | 3923 | /workspace/science-studio/tools/review/out/jellyfish_v6b/verdict.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6b/返修单.md` | 新增 | 1888 | /workspace/science-studio/tools/review/out/jellyfish_v6b/返修单.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6b/返修单_merge原始.md` | 新增 | 2478 | /workspace/science-studio/tools/review/out/jellyfish_v6b/返修单_merge原始.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6b/返修单_退分后merge.md` | 新增 | 2169 | /workspace/science-studio/tools/review/out/jellyfish_v6b/返修单_退分后merge.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6c/bgmfit.json` | 新增 | 722 | /workspace/science-studio/tools/review/out/jellyfish_v6c/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6c/cutquality_design.json` | 新增 | 3572 | /workspace/science-studio/tools/review/out/jellyfish_v6c/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6c/design_cuts.json` | 新增 | 554 | /workspace/science-studio/tools/review/out/jellyfish_v6c/design_cuts.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6c/extra_3-10/focus_run.json` | 新增 | 8932 | /workspace/science-studio/tools/review/out/jellyfish_v6c/extra_3-10/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6c/extra_3-10/focus_validated.json` | 新增 | 356 | /workspace/science-studio/tools/review/out/jellyfish_v6c/extra_3-10/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6c/focus_run.json` | 新增 | 130 | /workspace/science-studio/tools/review/out/jellyfish_v6c/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6c/focus_seg_3-10.md` | 新增 | 3577 | /workspace/science-studio/tools/review/out/jellyfish_v6c/focus_seg_3-10.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6c/verdict.json` | 新增 | 4605 | /workspace/science-studio/tools/review/out/jellyfish_v6c/verdict.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6c/返修单.md` | 新增 | 967 | /workspace/science-studio/tools/review/out/jellyfish_v6c/返修单.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6c/返修单_merge原始.md` | 新增 | 2564 | /workspace/science-studio/tools/review/out/jellyfish_v6c/返修单_merge原始.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6c/返修单_退分后merge.md` | 新增 | 2151 | /workspace/science-studio/tools/review/out/jellyfish_v6c/返修单_退分后merge.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6e/bgmfit.json` | 新增 | 722 | /workspace/science-studio/tools/review/out/jellyfish_v6e/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6e/cutquality_design.json` | 新增 | 3301 | /workspace/science-studio/tools/review/out/jellyfish_v6e/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6e/design_cuts.json` | 新增 | 552 | /workspace/science-studio/tools/review/out/jellyfish_v6e/design_cuts.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6e/extra_3-10/focus_run.json` | 新增 | 8242 | /workspace/science-studio/tools/review/out/jellyfish_v6e/extra_3-10/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6e/extra_3-10/focus_validated.json` | 新增 | 356 | /workspace/science-studio/tools/review/out/jellyfish_v6e/extra_3-10/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6e/focus_run.json` | 新增 | 57 | /workspace/science-studio/tools/review/out/jellyfish_v6e/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6e/focus_seg_3-10.md` | 新增 | 3810 | /workspace/science-studio/tools/review/out/jellyfish_v6e/focus_seg_3-10.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6e/verdict.json` | 新增 | 4200 | /workspace/science-studio/tools/review/out/jellyfish_v6e/verdict.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6e/返修单.md` | 新增 | 701 | /workspace/science-studio/tools/review/out/jellyfish_v6e/返修单.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6e/返修单_merge原始.md` | 新增 | 2460 | /workspace/science-studio/tools/review/out/jellyfish_v6e/返修单_merge原始.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6e/返修单_退分后merge.md` | 新增 | 2149 | /workspace/science-studio/tools/review/out/jellyfish_v6e/返修单_退分后merge.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6f/bgmfit.json` | 新增 | 722 | /workspace/science-studio/tools/review/out/jellyfish_v6f/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6f/cutquality_design.json` | 新增 | 3217 | /workspace/science-studio/tools/review/out/jellyfish_v6f/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6f/design_cuts.json` | 新增 | 552 | /workspace/science-studio/tools/review/out/jellyfish_v6f/design_cuts.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6f/extra_3-10/focus_run.json` | 新增 | 8759 | /workspace/science-studio/tools/review/out/jellyfish_v6f/extra_3-10/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6f/extra_3-10/focus_validated.json` | 新增 | 696 | /workspace/science-studio/tools/review/out/jellyfish_v6f/extra_3-10/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6f/focus_run.json` | 新增 | 57 | /workspace/science-studio/tools/review/out/jellyfish_v6f/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6f/focus_seg_3-10.md` | 新增 | 3908 | /workspace/science-studio/tools/review/out/jellyfish_v6f/focus_seg_3-10.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6f/verdict.json` | 新增 | 3810 | /workspace/science-studio/tools/review/out/jellyfish_v6f/verdict.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6f/返修单.md` | 新增 | 496 | /workspace/science-studio/tools/review/out/jellyfish_v6f/返修单.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6f/返修单_merge原始.md` | 新增 | 2460 | /workspace/science-studio/tools/review/out/jellyfish_v6f/返修单_merge原始.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6f/返修单_退分后merge.md` | 新增 | 2149 | /workspace/science-studio/tools/review/out/jellyfish_v6f/返修单_退分后merge.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6g/bgmfit.json` | 新增 | 722 | /workspace/science-studio/tools/review/out/jellyfish_v6g/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6g/cutquality_design.json` | 新增 | 3220 | /workspace/science-studio/tools/review/out/jellyfish_v6g/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6g/design_cuts.json` | 新增 | 552 | /workspace/science-studio/tools/review/out/jellyfish_v6g/design_cuts.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6g/extra_3-10/focus_run.json` | 新增 | 7944 | /workspace/science-studio/tools/review/out/jellyfish_v6g/extra_3-10/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6g/extra_3-10/focus_validated.json` | 新增 | 356 | /workspace/science-studio/tools/review/out/jellyfish_v6g/extra_3-10/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6g/focus_run.json` | 新增 | 57 | /workspace/science-studio/tools/review/out/jellyfish_v6g/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6g/focus_seg_3-10.md` | 新增 | 3870 | /workspace/science-studio/tools/review/out/jellyfish_v6g/focus_seg_3-10.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6g/verdict.json` | 新增 | 4001 | /workspace/science-studio/tools/review/out/jellyfish_v6g/verdict.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6g/返修单.md` | 新增 | 526 | /workspace/science-studio/tools/review/out/jellyfish_v6g/返修单.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6g/返修单_merge原始.md` | 新增 | 2460 | /workspace/science-studio/tools/review/out/jellyfish_v6g/返修单_merge原始.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6g/返修单_退分后merge.md` | 新增 | 2149 | /workspace/science-studio/tools/review/out/jellyfish_v6g/返修单_退分后merge.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6h/bgmfit.json` | 新增 | 722 | /workspace/science-studio/tools/review/out/jellyfish_v6h/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6h/cutquality_design.json` | 新增 | 3222 | /workspace/science-studio/tools/review/out/jellyfish_v6h/cutquality_design.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6h/design_cuts.json` | 新增 | 552 | /workspace/science-studio/tools/review/out/jellyfish_v6h/design_cuts.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6h/extra_3-10/focus_run.json` | 新增 | 8511 | /workspace/science-studio/tools/review/out/jellyfish_v6h/extra_3-10/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6h/extra_3-10/focus_validated.json` | 新增 | 842 | /workspace/science-studio/tools/review/out/jellyfish_v6h/extra_3-10/focus_validated.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6h/focus_run.json` | 新增 | 57 | /workspace/science-studio/tools/review/out/jellyfish_v6h/focus_run.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6h/focus_seg_3-10.md` | 新增 | 3916 | /workspace/science-studio/tools/review/out/jellyfish_v6h/focus_seg_3-10.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6h/verdict.json` | 新增 | 4070 | /workspace/science-studio/tools/review/out/jellyfish_v6h/verdict.json |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6h/返修单.md` | 新增 | 530 | /workspace/science-studio/tools/review/out/jellyfish_v6h/返修单.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6h/返修单_merge原始.md` | 新增 | 2460 | /workspace/science-studio/tools/review/out/jellyfish_v6h/返修单_merge原始.md |
| `workflows/footage-science-jellyfish/snapshot/review_runs/jellyfish_v6h/返修单_退分后merge.md` | 新增 | 2149 | /workspace/science-studio/tools/review/out/jellyfish_v6h/返修单_退分后merge.md |

### `workflows/footage-science-jellyfish/snapshot/script/` — 2 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/script/v1_draft.txt` | 新增 | 1100 | <EP>/script/v1_draft.txt |
| `workflows/footage-science-jellyfish/snapshot/script/v2_edit.md` | 新增 | 973 | <EP>/script/v2_edit.md |

### `workflows/footage-science-jellyfish/snapshot/sfx/` — 33 个文件：切点吸附强拍、混音、BGM 试混

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/sfx/cuts_v1.json` | 新增 | 806 | <EP>/sfx/cuts_v1.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/cuts_v2.json` | 新增 | 915 | <EP>/sfx/cuts_v2.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/mix_meta.json` | 新增 | 1873 | <EP>/sfx/mix_meta.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/mix_v1.py` | 新增 | 7472 | <EP>/sfx/mix_v1.py |
| `workflows/footage-science-jellyfish/snapshot/sfx/mix_v2.py` | 新增 | 7834 | <EP>/sfx/mix_v2.py |
| `workflows/footage-science-jellyfish/snapshot/sfx/snap_v1.py` | 新增 | 2189 | <EP>/sfx/snap_v1.py |
| `workflows/footage-science-jellyfish/snapshot/sfx/snap_v2.py` | 新增 | 3441 | <EP>/sfx/snap_v2.py |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/cur/bgmfit.json` | 新增 | 679 | <EP>/sfx/trials/cur/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/cur/cuts.json` | 新增 | 952 | <EP>/sfx/trials/cur/cuts.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/cur/mix.log` | 新增 | 188 | <EP>/sfx/trials/cur/mix.log |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/cur/mix_meta.json` | 新增 | 1871 | <EP>/sfx/trials/cur/mix_meta.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/cur/snap.log` | 新增 | 1101 | <EP>/sfx/trials/cur/snap.log |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/ditto/bgmfit.json` | 新增 | 680 | <EP>/sfx/trials/ditto/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/ditto/cuts.json` | 新增 | 936 | <EP>/sfx/trials/ditto/cuts.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/ditto/mix.log` | 新增 | 186 | <EP>/sfx/trials/ditto/mix.log |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/ditto/mix_meta.json` | 新增 | 1845 | <EP>/sfx/trials/ditto/mix_meta.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/ditto/snap.log` | 新增 | 1102 | <EP>/sfx/trials/ditto/snap.log |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/heroes/bgmfit.json` | 新增 | 683 | <EP>/sfx/trials/heroes/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/heroes/cuts.json` | 新增 | 931 | <EP>/sfx/trials/heroes/cuts.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/heroes/mix.log` | 新增 | 187 | <EP>/sfx/trials/heroes/mix.log |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/heroes/mix_meta.json` | 新增 | 1835 | <EP>/sfx/trials/heroes/mix_meta.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/heroes/snap.log` | 新增 | 1104 | <EP>/sfx/trials/heroes/snap.log |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/hwm/bgmfit.json` | 新增 | 678 | <EP>/sfx/trials/hwm/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/hwm/cuts.json` | 新增 | 950 | <EP>/sfx/trials/hwm/cuts.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/hwm/mix.log` | 新增 | 187 | <EP>/sfx/trials/hwm/mix.log |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/hwm/mix_meta.json` | 新增 | 1863 | <EP>/sfx/trials/hwm/mix_meta.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/hwm/snap.log` | 新增 | 1104 | <EP>/sfx/trials/hwm/snap.log |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/proof/bgmfit.json` | 新增 | 682 | <EP>/sfx/trials/proof/bgmfit.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/proof/cuts.json` | 新增 | 929 | <EP>/sfx/trials/proof/cuts.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/proof/mix.log` | 新增 | 186 | <EP>/sfx/trials/proof/mix.log |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/proof/mix_meta.json` | 新增 | 1840 | <EP>/sfx/trials/proof/mix_meta.json |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/proof/snap.log` | 新增 | 1101 | <EP>/sfx/trials/proof/snap.log |
| `workflows/footage-science-jellyfish/snapshot/sfx/trials/run_trials.sh` | 新增 | 1614 | <EP>/sfx/trials/run_trials.sh |

### `workflows/footage-science-jellyfish/snapshot/transfer/` — 3 个文件

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/transfer/PC传输步骤.md` | 新增 | 1163 | /workspace/xfer_jelly/PC传输步骤.md |
| `workflows/footage-science-jellyfish/snapshot/transfer/SUMS.txt` | 新增 | 620 | /workspace/xfer_jelly/SUMS.txt |
| `workflows/footage-science-jellyfish/snapshot/transfer/assemble_final.ps1` | 新增 | 2679 | /workspace/xfer_jelly/assemble_final.ps1 |

### `workflows/footage-science-jellyfish/snapshot/vo/` — 31 个文件：配音：Fish 生成、母带、停顿、字级对时、字幕

| 仓库路径 | 状态 | 字节 | 来源（盒上） |
|---|---|---|---|
| `workflows/footage-science-jellyfish/snapshot/vo/asr_v1.py` | 新增 | 1053 | <EP>/vo/asr_v1.py |
| `workflows/footage-science-jellyfish/snapshot/vo/asr_v1_medium.json` | 新增 | 11314 | <EP>/vo/asr_v1_medium.json |
| `workflows/footage-science-jellyfish/snapshot/vo/build_kt.py` | 新增 | 1174 | <EP>/vo/build_kt.py |
| `workflows/footage-science-jellyfish/snapshot/vo/build_subs.py` | 新增 | 1760 | <EP>/vo/build_subs.py |
| `workflows/footage-science-jellyfish/snapshot/vo/build_timing.py` | 新增 | 1003 | <EP>/vo/build_timing.py |
| `workflows/footage-science-jellyfish/snapshot/vo/build_timing_v2.py` | 新增 | 1003 | <EP>/vo/build_timing_v2.py |
| `workflows/footage-science-jellyfish/snapshot/vo/cards_master.json` | 新增 | 15120 | <EP>/vo/cards_master.json |
| `workflows/footage-science-jellyfish/snapshot/vo/cards_timed.json` | 新增 | 15105 | <EP>/vo/cards_timed.json |
| `workflows/footage-science-jellyfish/snapshot/vo/cards_timed_v2.json` | 新增 | 15105 | <EP>/vo/cards_timed_v2.json |
| `workflows/footage-science-jellyfish/snapshot/vo/cards_timed_v3.json` | 新增 | 15095 | <EP>/vo/cards_timed_v3.json |
| `workflows/footage-science-jellyfish/snapshot/vo/cards_timed_v4.json` | 新增 | 15108 | <EP>/vo/cards_timed_v4.json |
| `workflows/footage-science-jellyfish/snapshot/vo/fish_lib.py` | 新增 | 2084 | <EP>/vo/fish_lib.py |
| `workflows/footage-science-jellyfish/snapshot/vo/gen_v1.py` | 新增 | 1526 | <EP>/vo/gen_v1.py |
| `workflows/footage-science-jellyfish/snapshot/vo/gen_v2.py` | 新增 | 1547 | <EP>/vo/gen_v2.py |
| `workflows/footage-science-jellyfish/snapshot/vo/master_v1.py` | 新增 | 3004 | <EP>/vo/master_v1.py |
| `workflows/footage-science-jellyfish/snapshot/vo/master_v2.py` | 新增 | 3004 | <EP>/vo/master_v2.py |
| `workflows/footage-science-jellyfish/snapshot/vo/master_v3.py` | 新增 | 2923 | <EP>/vo/master_v3.py |
| `workflows/footage-science-jellyfish/snapshot/vo/master_v4.py` | 新增 | 2923 | <EP>/vo/master_v4.py |
| `workflows/footage-science-jellyfish/snapshot/vo/pause_v4.py` | 新增 | 1026 | <EP>/vo/pause_v4.py |
| `workflows/footage-science-jellyfish/snapshot/vo/splice_v3.py` | 新增 | 1995 | <EP>/vo/splice_v3.py |
| `workflows/footage-science-jellyfish/snapshot/vo/subs_v1.json` | 新增 | 3464 | <EP>/vo/subs_v1.json |
| `workflows/footage-science-jellyfish/snapshot/vo/subs_v1.srt` | 新增 | 1867 | <EP>/vo/subs_v1.srt |
| `workflows/footage-science-jellyfish/snapshot/vo/subs_v6.srt` | 新增 | 1862 | <EP>/vo/subs_v6.srt |
| `workflows/footage-science-jellyfish/snapshot/vo/take_v1.mp3.json` | 新增 | 20047 | <EP>/vo/take_v1.mp3.json |
| `workflows/footage-science-jellyfish/snapshot/vo/take_v2.mp3.json` | 新增 | 20106 | <EP>/vo/take_v2.mp3.json |
| `workflows/footage-science-jellyfish/snapshot/vo/tts_input_v1.txt` | 新增 | 1060 | <EP>/vo/tts_input_v1.txt |
| `workflows/footage-science-jellyfish/snapshot/vo/tts_input_v2.txt` | 新增 | 1054 | <EP>/vo/tts_input_v2.txt |
| `workflows/footage-science-jellyfish/snapshot/vo/vo_v1.meta.json` | 新增 | 626 | <EP>/vo/vo_v1.meta.json |
| `workflows/footage-science-jellyfish/snapshot/vo/vo_v2.meta.json` | 新增 | 623 | <EP>/vo/vo_v2.meta.json |
| `workflows/footage-science-jellyfish/snapshot/vo/vo_v3.meta.json` | 新增 | 625 | <EP>/vo/vo_v3.meta.json |
| `workflows/footage-science-jellyfish/snapshot/vo/vo_v4.meta.json` | 新增 | 626 | <EP>/vo/vo_v4.meta.json |

## 排除（没放进包，原因）
| 项 | 原因 |
|---|---|
| 所有 mp4/wav/mp3/m4a/png/jpg/ttf、`out/`、`node_modules/`、`backup*/`、`deliver/` 里的成片和封面、`xfer_*` 分块 | 媒体/产物，不入库 |
| `science-studio/config/drive.json` | 和 main 的差别只是新的 Drive 文件夹 ID；main 版已脱敏，保持不动 |
| `science-studio/config/house_formula.md`、`proposals_20261028.md` | 这期没用到，另起提交更合适 |
| `science-studio/scripts/export_gemini_pack.py`、`gemini_field_convert.py`、`docs/gemini_handoff/` | Gemini 交接层，这期没用到（production_config 里有对应说明段，路径指向盒上） |
| `science-studio/scripts/feedback.py` | 盒上版只多一个小的去重改动，这期没用到 |
| `science-studio/tools/review/lib/merge_v1_backup*` | 旧备份 |
| `remotion/public/fonts/SmileySans-Oblique.ttf` | 2.6 MB 二进制字体 |
| `research/field/v/*/comments.json` | 评论原文（第三方用户内容），只留 report.md + collect.json |
