# 实拍热点科普（火箭水母款）工作流 · 冻结版 footage-science-workflow-v1

**什么选题用这套：** 天象、发射、自然奇观这类「很多人亲眼拍到、刷到」的热点，抖音上已经有大量网友/官方实拍，要用 45–60 秒讲清「这是什么、为什么会这样」——用这套。画面全部是**真实拍摄**（署名作者），原理部分用 Remotion 程序画示意图，不用 AI 生成画面。

> 冻结来源：EP-20261029-01《天都黑了，火箭水母为啥还在发光》。用户 2026-10-29 03:16（UTC+8）选定 v6b 作为发布基准；之后按审片官返修单做到 v6h（04:59 交付，成片 51.536 s，sha256 `ca9c1936…29a5`）。`snapshot/` 是整期源码（不含任何媒体），`params.json` 是实测参数。所有数字来自日志和文件，没有记录的写「未知」。

## 三套工作流的区别

| 项 | 实拍热点科普（火箭水母款） | 热点科普（Roadster 款） | 微缩动画科普（打折款，见 miniature 分支） |
|---|---|---|---|
| 选题 | 网友亲眼可见的奇观/事件 + 原理 | 新产品/发布会黑科技 | 生活知识、反常识心理 |
| 画面 | 多位网友 + 官方实拍，逐镜署名；示意图程序绘制 | 官方发布会/官方片 | GPT 出图 → 2.5D 分层动画 |
| 画幅 | 竖屏 1080×1920（JellyFilm） | 横屏 1920×1080 | 竖屏 + 竖横两封面 |
| 配音 | Fish 906524… / s2.1-pro-free，整稿一条 take | Roadster 音色 cfd828…，逐句多条择优 + 1.15× | Fish 每句一条 |
| BGM | 抖音热歌榜曲（dy_hot_bgm.py）+ 切点吸附强拍 + −8 dB 闪避 | 自制 BGM | 无 BGM |
| 字幕 | 一句一字幕（OneLineSubtitles） | 多行 | — |
| 审片 | 自检（cutquality/bgmfit/qwen×3）+ 审片官（review.py + 5 人设） | 人工 | QC 脚本 |
| 渲染 | 盒上 render_box.mjs，51.5 s 片 70–95 s | PC | PC 在线优先 |

## 1. 阶段与产物（`snapshot/`）

| 阶段 | 做什么 | 产物 |
|---|---|---|
| A 选题 + 实地 | douyin-field-collect 搜同题，看高赞版本的开头、评论 | `research/field/`（只留 report.md + collect.json，评论原文不入库） |
| B 事实 | 每条事实带来源；高度、气压、温度这类数字要能追到出处 | `research/facts.md`，`research/sun_calc.py`（算日落后地影高度） |
| C 素材 | 找 4–6 个不同机位的实拍，记作者、地点、链接、发布时间 | `research/footage_sources.md` → `deliver/素材来源.md` |
| D 逐字稿 | 钩子（「天都黑了，它为啥还在发光」）→ 否定 UFO → 原理三段（地影、稀薄空气胀开、冰晶散射）→ 看到的三个条件 → 互动 | `script/`，`vo/cards_master.json` |
| E 配音 | 整稿一条 take → master（去齿音、停顿）→ 字级对时 | `vo/gen_v*.py`、`master_v4.py`、`pause_v4.py`、`build_timing_v2.py`、`cards_timed_v4.json`、`subs_v6.srt` |
| F 素材预处理 | 每镜 ffmpeg 裁成 1080×1920@30（变速、调色、去水印、锐化）+ 署名 | `footage/clips.py`、`footage/*.json` |
| G BGM + 音效 | 热歌榜取 4–5 首试混打分，切点吸附强拍，混音 | `audio/`、`sfx/snap_v2.py`、`sfx/mix_v2.py`、`sfx/trials/` |
| H Remotion | JellyFilm 组件、示意图、关键词时间点 kt.ts、封面 CoverV/CoverH、「丞」朱印 | `remotion/src/`、`remotion/scripts/render_box.mjs` |
| I 渲前闸门（新增） | 切点/字幕/结尾结构检查，不过不渲 | `templates/qc/structure_gate.py` + `templates/qc/prerender_checklist.md` |
| J 审片 | 自检 → 审片官 → 返修单 | `review/`、`review_runs/` |
| K 交付 | 成片 + 两张封面 + 发布文案 + 素材来源，传 PC | `deliver/`、`publish/`、`transfer/` |

## 2. 关键参数（详见 `params.json`）
- 配音：Fish `reference_id 906524668b6d4afe84736962e005cd09`，`model s2.1-pro-free`，speed 1.0，temperature 0.7，top_p 0.7，chunk_length 300，整稿一条。⚠ `state.json` 里 `vo.voice_id` 写的是 `cfd828…`，但生成脚本实际用 `906524…`，以脚本为准。
- 混音（`sfx/mix_meta.json` 实测）：BGM 源 −7.7 LUFS，底电平 −18.2 dB（公式 −17.5 + (−8.4 − 源LUFS)），人声段闪避 −8 dB，前 3 秒不闪避；音效 −14 dB（相对人声）；两遍 loudnorm −16 LUFS / TP −1.5；成片 I −15.9、TP −3.0、LRA 3.2。
- 渲染：`node scripts/render_box.mjs out/<版本> [起帧-止帧]`，swangle、并发 6、crf 18、jpeg 93、静音渲染后 `-c:a copy` 混流。13 次实测 70–95 s，合计 1013 s。
- 交付到 PC：`D:\编程\项目\视频制作\作品\2026-10-29_火箭水母云\发布\`，3 个文件（成片、竖封面、横 4:3 封面）。

## 3. 这期学到的规则（写进下一期）
1. **前 10 秒不出现短于 0.9 s 的镜头**（v6c 的 c04 只有 0.695 s，审片官返修单第 1 条要求恢复到 1.0 s）。渲前跑 `structure_gate.py` 拦住。
2. **钩子窗口（3–10 s）每 1.6 s 内要有一次画面变化**（切点或推/字卡事件），否则「路人」会在这里划走。
3. **切点不落在字中间**（v6c 在 4.305 s 切镜，「箭」字 4.42 s 才说完，返修单要求入点挪到 4.6 s）。注意：structure_gate 的 H3 需要成片时间轴上的字级时间；这期的 asr.json 字边界太粗，cards_timed_v4.json 是加停顿前的时间，两者都没查出这一处，目前要靠人工看切点附近的口播。
4. **审片分数有噪声**：同一版本 qwen 跑三次，路人划走时间 8.1 / 3.2 / 5.3 s，相差 4.9 s；v6c→v6h 六轮审片官总分一直在 73.7–73.8。中位数差不到 1.5 s 不算改进，见 `templates/review/审片官交接单模板.md` 的停止规则。
5. **只交付定稿版**：每轮都重切 PC 分块、把旧版挪进 `v*旧版/`，6 轮重复做了 6 次。改成审片阶段只在盒上留 mp4，用户确认后再打包一次。
6. **PC 传输用通用脚本**：这期早上写了 6 个 ps1（10:04–10:07）才合并成功。下次直接用 `templates/transfer/make_pc_bundle.sh` + `assemble_from_home.ps1`（已在盒上用 PowerShell 7 实测：改名的分块按哈希找回、重跑跳过、坏块报错）。

## 4. 复用步骤
1. 复制 `snapshot/` 到 `/workspace/science-studio/projects/<EP>/`，改 `STATE.md`、`state.json`。
2. `remotion/` 下 `npm ci`；字体 `SmileySans-Oblique.ttf` 和 `brand/seal_t.png` 从上一期工程的 `public/` 拷（媒体不入库）。
3. 按第 1 节阶段走。每个阶段结束时在 STATE.md 记一行时间（这期 A–G 是 01:21 一次性补记的，没法拆开算各阶段用时）。
4. 渲染前过 `templates/qc/prerender_checklist.md`。
5. 审片按 `templates/review/审片官交接单模板.md` 一次交接、带停止规则。
6. 定稿后 `templates/transfer/make_pc_bundle.sh <TAG> <PC目录> <输出目录> 成片 封面…`，把输出目录里的文件 CopyFromBox 到 PC 的 `C:\Users\Administrator\`，在 PC 上跑 `<TAG>__assemble.ps1`，最后一行是 `DONE` 才算成功。

## 5. 缺失项 / 没入库
- 所有媒体（实拍素材、配音 wav、BGM mp3、渲染、封面 png）、`node_modules`、`out/`、`backup*`。
- 字体 SmileySans-Oblique.ttf（2.6 MB 二进制）。
- 实地采集的评论原文 `comments.json`（只留统计和报告）。
