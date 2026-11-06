# 热点科普（Roadster 款）工作流 · 冻结版 roadster-v1

**什么选题用这套：** 新产品、发布会、黑科技这类热点，手里有真实画面（官方片、发布会），要用 60–90 秒讲清「它是怎么做到的」——用这套。如果选题是「网传图片/视频是真是假」，用 `../AI辟谣拆解_iPhone款/`，两套不要混用。

> 冻结来源：Roadster 已发布版是 V4（`D:\编程\项目\视频制作\品牌\特斯拉Roadster_秘书丞_V4_1080p.mp4`），但 **V4 源码没找到**（见文末「缺失项」）。下面所有参数来自能找到的 **V3 终版源码**（`snapshot/`，与 GitHub tag `roadster-v3` 一致）、V3 README/混音清单，以及 `roadster_24h` 复盘。没有实测记录的参数一律不写。

## 两套工作流的关键区别

| 项 | 热点科普（Roadster 款） | AI 辟谣拆解（iPhone 款） |
|---|---|---|
| 选题 | 真实热点 + 原理科普 | 网传 AI 假图/假视频核查 |
| 叙事 | 奇观 → 争议 → 结论 → 原理两段 → 总结 → 量产/售价 → 提问 | 先信后揭：先让观众信，2–5 秒揭「是 AI」，再逐个圈破绽 |
| 素材 | 官方发布会/官方片（品牌方公开素材） | 网传视频、核查机构画面；必须去水印、去台标、人脸打码 |
| 来源写法 | V3 简介写明画面来源（Tesla 官方片、TechCrunch/Engadget 截图） | 画面和口播里不点媒体名和平台名；用「内容标识 → 引用来源 → 站外」 |
| 配音 | Roadster 音色，speed 1.05 + 整体 1.15× 变速 | Roadster 音色，speed 1.25，不再变速 |
| 工程 | `RoadsterShortV3`，footage-timeline.json + 对齐工具，含 3D（three.js） | `IphoneFakeV3f`，build_v3.py 生成 JSON，超分 + 人脸打码 + OCR |
| 合规 | 常规 | 过审清单 + OCR 白名单（V3/V3d 曾被判「不适宜公开」） |
| 渲染 | 冻结版在 PC（含 3D）：`npm run render:master`，c8 angle veryfast | 冻结版在盒上：c6 crf18，再传到 PC |

上表是冻结版当时的做法。2026-10-29 起，约 60 秒及以内的短片默认在盒上渲，传到 PC 的只有定稿成片和两张封面（`science-studio/config/workflow_spec.md` §1.1）。本款冻结版含 3D、片长约 90 秒，仍属 PC 那一档。

## 1. 脚本结构（V3 实稿，`snapshot/voice/v3/script.txt`，共 22 句）
1. 钩子：一句奇观（V3 是「…最出圈的不是加速，是这一下。它飞起来了。」）+ 奇观补充（「连Semi大卡车都在它肚子底下」）
2. 评论区争议：「特效吧？AI吧？马斯克又画饼了吧？」
3. ~~自我介绍「大家好，我是秘书丞」~~：按复盘 H5 **删掉**
4. 先说结论：「这回还真不是特效，但它也不是你以为的那种飞」
5. 原理两段（各自开头「先说吸」/「那真正把它送上天的，又是什么？」），每段 3–5 句，用生活类比（松手放气球）
6. 一句话总结：「风扇负责吸，喷气负责飞」
7. 能不能买：量产时间、售价/订金
8. 结尾互动提问：「如果真能买，你敢坐吗？」

复盘数据：章节点击里「量产与售价」占 59.5%，搜索流量占 80%。下一条可以把售价、量产提前，标题前几个字放搜索词。

## 2. 开头规则 H1–H7（来自 `douyin-growth/reviews/roadster_24h_2026-10-18.md`）
- H1 第 0 帧就是全片最强的画面（奇观或结果），最晚 1 秒内出现，不放铺垫镜头。
- H2 第一句不超过 2 秒、8 个字左右，直接抛问题或反常识的断言；不要用「XX发布会，最XX的不是A，是B」这种先铺垫的句式。
- H3 前 2 秒主体要大：横屏片里主体至少占画面高度一半，标题带写悬念。
- H4 前 5 秒讲清「讲什么、为什么继续看」，留一个反转。
- H5 不自我介绍。品牌只用开场小印章 + 右上角徽标，不要片尾卡。
- H6 先信后揭：揭秘点落在 2–5 秒之间，揭之前不出任何结论性标签。
- H7 第 0 帧就有声音和字幕，不淡入、不静音起步；首帧要和封面、标题的承诺一致。

V3 的问题（反面例子）：0–3.6 秒是起步加速，飞越的奇观到 3.6 秒才出现；第一句约 3 秒，全是铺垫；13 秒才自我介绍。数据：2 秒跳出率 40.81%，5 秒完播率 46.40%，完播率 7.27%。

## 3. 配音（实测参数，`snapshot/voice/v3/`）
- 音色：Roadster `cfd828bdf120410c923fac0056c687c2`（穆祉尘音色1）
- 接口：Fish `POST /v1/tts/stream/with-timestamp`，请求头 `model: s2.1-pro-free`，`latency: normal`，`prosody.volume: 0`，temperature **0.65**
- 逐句生成：`gen.py`，每句 `prosody.speed` **1.05**，生成多条（ta/tb/tc），4 线程并行，失败重试 3 次
- TTS 送字：`2028年` 写成「二零二八年」，`AI` 写成「A I」（只改送 TTS 的文本，字幕不改）
- 挑选（`proc.py`）：用 faster-whisper `medium` int8 听写，选拼音错误最少的；问句（第 2、11、18、21 句）选尾音上扬大的；语速接近 6 字/秒
- 句内静音：超过 0.3 秒的剪到两边各留 0.15 秒
- `stitch.py`：整体 **1.15× 变速**（优先 `rubberband=tempo=1.15`，没有就用 `atempo=1.15`），字幕时间戳同步除以 1.15
- 句间停顿（变速后插入）：默认 0.30 秒；第 1 句后 0.55 秒，第 4 句后 0.35 秒，第 11 句后 0.55 秒，最后一句后 0.6 秒；开头留 0.12 秒
- 人声 `loudnorm=I=-16:TP=-1.5:LRA=11`。成片混音后再按 `footage-timeline.json` 的 `audio.lufs` = **−16** 做一次 loudnorm（TP −1.5）
- Key 只从环境变量 `FISH_API_KEY` 读取（`fish.py`），绝不写进文件
- ⚠ 任务说明里写的「speed 1.08」在 Roadster 的任何记录里都**没找到**。1.08 是梯度下降 v4 的默认语速。Roadster 实际用的是 1.05 + 1.15× 变速（叠加后约 1.21）。没有 V4 源码，无法确认 V4 是否改过。

## 4. Remotion 工程（`snapshot/remotion/`）
- remotion / @remotion/cli / @remotion/media / @remotion/three / @remotion/player 版本 ^4.0.535；three ^0.186.1，@react-three/fiber ^9.8.2；typescript ^7.0.2
- 合成 `RoadsterShortV3`：**1920×1080（16:9 横屏）、30 fps**（`src/index.tsx`、`src/v3/theme.tsx`）
- 字体：`"Noto Sans CJK SC","Noto Sans SC",sans-serif`（`src/v3/theme.tsx` 里的 `F`）
- 组件：`src/v3/Short.tsx`（主时间线）、`Explain3D.tsx`（3D 原理动画）、`v2shots.tsx`、`shots.ts`、`warp.tsx`、`shotctx.tsx`；`src/Car2.tsx` + `car.json`（3D 车模）、`Transition3D.tsx`、`ui.tsx`（评论卡、标题卡）
- 镜头入出点和混音都写在 `src/v3/footage-timeline.json`，用对齐工具改（`npm run align` 打开 http://localhost:3210，Windows 下用 `align/start-align.bat`；说明见 `align/使用说明.md`）
- 混音参数：voiceDb 0，sfxDb 0，bgmDb 10，duckDb 10，lufs −16（BGM 用 sidechaincompress 以人声闪避）

### 分镜节奏（V3 实际镜头时长，单位秒）
开场起步 3.59 → 飞越 Semi 5.31 → 评论区 4.13 →（自我介绍 1.55，H5 已删）→ 结论 4.44 → 两套系统 4.16 → 吸·实拍定格 1.23 → 下压力读数 1.60 → 冲弯墙 1.85 → 顶上倒过来 4.10 → 设问·飞行 6.37 → 能开上吗 3.40 → 2028 量产 2.16 → 封闭场地 2.95 → 结尾 3.33。全片 89.53 秒。
新片按 H1 调整：飞越的奇观放到第 0 帧。

### 音效 / BGM（全部自制，`SFX-BGM-v3.md`、`scripts/make_bgm_v3.py`）
- bgm_A：Am-F-C-G，112 BPM，pad + 琶音 + 轻鼓；bgm_B：从「那真正把它送上天的」起，加完整鼓组和贝斯，A→B 交叉淡化
- sting（频道提示音）；boom ×2（开场、起飞）；whoosh ×6（只用在真正的转场）；ding ×3（只给关键数字：2 倍 / 2028 / 25 万美元）
- click ×4、shutter ×2、fanhum、jet、hiss、puff ×3（评论卡、定格、拟音）
- 文件在 `remotion/public/sfx/` 和 `public/v3/`（媒体文件不入库，路径见下）

## 5. 渲染（V3 当时在 PC：R5 5600 / 16GB / RTX 3080）

下面是 V3 的实测。新的短片不要把工程拿到 PC 渲，见 `science-studio/config/workflow_spec.md` §1.1。本款含 3D、片长约 90 秒，仍走 PC。

- `npm run render:master`：先渲无声画面（`--muted --codec=h264 --crf=18`），再渲纯音频 wav，loudnorm −16 / TP −1.5 / LRA 11，最后用 aac 320k、`+faststart` 合成
- 推荐参数：`--concurrency=8 --gl=angle --x264-preset=veryfast --offthreadvideo-video-threads=4`（基准测试 7.66 fps，全片画面约 5.5 分钟；c12 反而更慢；Remotion 没有 NVENC）
- 只改了音量时用 `npm run remix-audio`（约 2 分钟，画面 `-c:v copy` 不重编码）
- 成片规格（V3 实测）：1920×1080 30fps，h264 + AAC 320k 48k，−15.9 LUFS，TP −2.3

## 6. 发布规范
- 抖音为主，同步 B 站；横屏 16:9、1 分钟以上（为了中视频计划）
- 标题：前几个字放搜索词（V4 实测搜索词：「特斯拉Roadster为什么会飞」57.2%、「特斯拉飞行汽车」26.5%）；V4 标题是「特斯拉新跑车真能飞？」
- 封面：主体清楚，Q 版小官和主体互动，封面要真的展示标题承诺的内容；V4 用的是封面 E5（横版 16:9 + 竖版 3:4）
- 品牌：开场小印章 + 右上角徽标；不要「其一/其二」，不要片尾卡
- 简介（V3 实稿）：一句话讲清卖点 + 画面来源 + 「BGM：原创合成配乐（自制）」
- 复盘：24h / 72h 按 `douyin-growth/checklists/03_24h_72h复盘.md` 看数（先看 2 秒跳出，再看 5 秒完播、完播率）

## 7. 媒体文件（不复制，只记路径）
- PC 工程：`D:\编程\项目\视频制作\作品\2026-10-17_特斯拉Roadster\remotion\`（public\ 里有 clip-*.mp4、hlive*.mp4、sfx\、v3\bgm_A/B.wav、voice-v3.wav 等）
- V3 成片：`D:\编程\项目\视频制作\作品\2026-10-17_特斯拉Roadster\特斯拉Roadster-v3.mp4`
- V4 成片：`D:\编程\项目\视频制作\品牌\特斯拉Roadster_秘书丞_V4_1080p.mp4`
- 封面 E5：box `/workspace/brand/deliver/品牌/封面_Roadster/`
- box 源码：`/workspace/topics/tesla-roadster/`；GitHub：`zwjym1/video-workflows` 下的 `projects/tesla-roadster`（tag roadster-v3）

## 8. 缺失项（找不到，没有写进模板）
- V4 源码 `src/v4/` 和 `remotion_v4_patch.zip`：迁出记录写在 box `/workspace/topics/tesla-roadster/remotion/src/v4/`、`/workspace/brand/deliver/remotion_v4_patch.zip`，现在 box 上都没有；PC 上也没搜到 v4 目录（PC 中途掉线，搜索没做完）
- V4 相对 V3 改了哪些内容（开头、脚本、镜头），没有记录
- V4 的配音参数、渲染日志、响度实测值
- 「speed 1.08」：没有出处

## 共用效率模板（2026-10-29）

本款的选题、叙事、画风不改。渲染地点按 `science-studio/config/workflow_spec.md` §1.1：约 60 秒的短片在盒上渲，本款含 3D、片长约 90 秒，仍在 PC。定稿后只把成片和两张封面传到 `发布\`。返修用共用模板（§5.1，依据 `docs/效率审计_2026-10-29.md`）：

- 渲前：`templates/qc/structure_gate.py`，清单 `templates/qc/prerender_checklist.md`。有 FAIL 不渲。
- 审片：`templates/review/审片官交接单模板.md`。主观自审限时 15 分钟，和审片官并行。一次改动算改进，只当路人划走中位数比上一版高 ≥1.5 秒，且同一版本至少 4 次。局部补丁最多 2 轮，然后改结构，或把当前最好的一版交给用户拍板。
- 定稿后才打包：`templates/transfer/make_pc_bundle.sh` + `assemble_from_home.ps1`。审片阶段不切分块、不挪旧版。
- 阶段用时：`templates/state/stage_log.py` 记进 STATE.md。

## 目录
```
README.md        本文件
params.json      全部数值参数（机器可读）
snapshot/remotion/   V3 终版 Remotion 源码（src、scripts、align 工具、package.json 等，不含 node_modules、public、out）
snapshot/voice/      v2/v3 配音脚本（gen.py → proc.py → stitch.py，fish.py），脚本文本、选句、对齐结果
```
