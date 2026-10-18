# AI 辟谣拆解（iPhone 款）工作流 · 冻结版 ai-debunk-v1

**什么选题用这套：** 网上疯传的图片或视频，要讲清「它是 AI 做的，破绽在哪」——用这套。如果是真实热点要讲原理（发布会、黑科技），用 `../热点科普_Roadster款/`，两套不要混用。

> 冻结来源：iPhone V3f（`IphoneFakeV3f`），成片 `D:\编程\项目\视频制作\作品\2026-10-18_iPhone假货\remotion\out\满海iPhone是假的_秘书丞_V3f_1080p.mp4`（定时发布 2026-10-19 11:00）。参数都来自 V3f 实际用过的代码，代码在 `snapshot/`。

## 两套工作流的关键区别

| 项 | AI 辟谣拆解（iPhone 款） | 热点科普（Roadster 款） |
|---|---|---|
| 选题 | 网传 AI 假图、假视频核查 | 真实热点 + 原理科普 |
| 叙事 | 先信后揭：先让观众信，2–5 秒揭「是 AI」，再逐个圈破绽 | 奇观 → 争议 → 结论 → 原理两段 → 总结 → 量产/售价 → 提问 |
| 素材 | 网传视频、核查机构画面：去水印、去台标、人脸打码，素材只占单镜一部分 | 官方发布会、官方片 |
| 来源写法 | 画面和口播里不点媒体名、平台名，也不用「外网」「外媒」；发布时选「引用来源 → 站外」 | 简介写明画面来源 |
| 配音 | Roadster 音色，speed 1.25，不加情绪标记，不变速 | Roadster 音色，speed 1.05 + 整体 1.15× 变速 |
| 工程 | build_v3.py → v3f.json → `IphoneFakeV3f`；超分、人脸打码、OCR 脚本 | `RoadsterShortV3` + 对齐工具 + 3D |
| 合规 | 过审清单 + OCR 白名单 + AI 生成内容标识 | 常规 |
| 渲染 | box：c6 crf18，传到 PC | PC：c8 angle veryfast |

## 1. 叙事：先信后揭
- 第 0 帧放大家信以为真的那个画面（V3f：满海漂着 iPhone 盒子），第一句话就是提问（「满海的免费 iPhone？」约 1.9 秒）
- 揭秘点落在 2–5 秒之间（V3f 约 4.5 秒揭「是 AI 做的」）；揭之前画面上不出现「AI」字样，也不出结论性标签
- 揭完给一个反转，说明「哪部分是真的」（V3f：「但那艘船，是真的。」）
- 然后逐个拆破绽：放大、红圈、对比（实拍和 AI 分屏）、检测结果卡
- 结尾给方法，不给外链：「刷到「白捡 iPhone」／先看谁最先发的」
- 开头同样遵守 Roadster 复盘的 H1–H7（见 Roadster 款 README 第 2 节）

## 2. 破绽红圈和推镜规则
- 每个破绽红圈至少停留 **2.5 秒**。配音变短时挪镜头切点，不要压缩红圈（V3f 的 s15/s16 切点前移，用 assert 保证 ≥2.55 秒）
- 推镜上限 **1.4×**；只有推到更大还清晰才允许超过（V3f：s16 从 1.8× 降到 1.4×，因为源图只有 1250 高；s23 从 1.95× 降到 1.4×，因为截图源只有 1432 宽）
- 低清源先超分：Real-ESRGAN `realesrgan-ncnn-vulkan`，模型 `realesrgan-x4plus`，`-s 4`；再用 lanczos 缩到 1440×2560，`unsharp=5:5:0.4`，crf 17（`snapshot/v3f/sr_finish_v3e.ps1`）

## 3. 画面清理（`snapshot/remotion/scripts/v3/v3f_patch.py`、`snapshot/v3f/`）
- **台标/水印：** 局部模糊（GaussianBlur），或用纯色块盖住；不整镜换掉，保留证据数字和画面内容
  - 核查机构的「AI-GENERATED」横幅，换成我们自己的红条 + 白字「AI 生成」
  - 英文检测页、标题，盖上中文译文，并标注「（检测页原文，中译）」
  - 检测工具的品牌字样和页脚抹掉，标签改成中文（AI 生成视频 / 语音 / 音乐 / 深度伪造），保留 99.9% 这些数字
- **去掉所有「素材/信源/来源」角标**；只保留「丞」角标和开场印章
- **评论、帖子：** 用户名、头像、视频编号、点赞数、表情代码都去掉，文字原样重排，标注「网友评论（文字原样）」
- **人脸打码**（`faces.py` + `faceblur_v3f.py`）：OpenCV YuNet，放大 1.5 倍检测，阈值 0.55，去掉 w>40 且 h/w<1 的框；±3 帧取并集；每张脸做 5×5 马赛克 + 高斯模糊，用羽化椭圆贴回。iPhone 镜头模组会被误检成人脸，相关素材放进 SKIP 名单
- **灾难画面压低：** 冒烟的船、人群哄抢的画面，改裁成漂浮集装箱、平静海面的近景；作为证据必须保留的画面只清理标识
- **弹幕：** 只留中性好奇类（「在哪捡？」「真的假的？」）
- **图片素材：** 优先用 CC0；必须署名的 CC BY 图片尽量换掉

## 4. 中性称呼改写表（全文见 `v3f_naming.md`）
| 原来的说法 | 改成 |
|---|---|
| BBC 等媒体 | 核查机构 / 专业机构 |
| X、Instagram 等平台 | 网上流传 / 网友 / 账号 |
| Hive、OpenAI | 检测工具 / AI 工具 |
| Grok | AI |
| 搬运号 | 转发的账号 / 转发的人 |
| 「船沉了」这类灾难表述 | 中性表述（「那艘船，是真的」） |
口播、字幕、标题栏、弹幕都不出现：BBC、X、推特、Instagram、Annahar、Hive、OpenAI、外网、外媒、B站、搬运号。

## 5. 配音（改句只重配改过的那几句）
- 音色 Roadster `cfd828bdf120410c923fac0056c687c2`；`s2.1-pro-free`，temperature **0.65**，speed **1.25**；不加情绪标记，不要笑声
- 每个单元生成 3 条，并行（`snapshot/vo/v3f/gen_f.py`，调用 `vo/tts.py` 里的 synth）
- 用 faster-whisper `large-v3` int8 听写（`feats_f.py`），要求字错率 0（只差数字格式的可以）；再按尾音音高挑选
- 拼接（`build_f.py`）：按单元拼接 + 句间停顿；只对极少数尖峰软限幅；两遍 loudnorm 到 −16 LUFS，TP ≤ −1.5
- V3f 人声实测：−16.0 LUFS，TP −2.13，LRA 2.6，75.744 秒
- Key 只从环境变量 `FISH_API_KEY` 读取，绝不打印，也不写进文件

## 6. 工程和渲染
- `snapshot/remotion/`：remotion 4.0.536；`src/v3f/V3f.tsx`（导出 `IphoneFakeV3f`，在 `src/Root.tsx` 里注册）；数据 `src/v3f/data/v3f.json`；字体 `public/fonts/NotoSansSC-Bold-sub.otf`（由 `scripts/v3/font_v3.py` 生成子集）
- 生成数据：`python scripts/v3/build_v3.py --v3f`（会自动带上 V3E、V3D 的改动；结尾调用 `v3f_patch.patch(globals())`）→ 跑人脸打码 `v3f/faceblur_v3f.py`
- 画幅 **1920×1080，30 fps**，h264；`remotion.config.ts` 里帧格式 jpeg，质量 92
- 渲染：`npx remotion render src/index.ts IphoneFakeV3f out/<名字>.mp4 --concurrency=6 --crf=18 --audio-bitrate=320k`（box 上约 6 分钟）
- 预览帧：`COMP=IphoneFakeV3f JSONP=src/v3f/data/v3f.json node scripts/v3/stills_v3.mjs <目录> 0.5`
- 音效（49 个，都在 `public/v3/sfx/`）：whoosh_c/d/e/f、pop_a/b/c、hit_c/d、click_b/c；BGM `public/v3/audio/bgm_281.wav`
- 传到 PC：拆成 7 MB 分块，逐块 CopyFromBox 到 `C:\Users\Administrator`（只有这个目录能直接写），再移到 `out\_staging_<版本>\`，在 PC 上拼回并核对 sha256。断线就重试，Administrator 里不留文件

## 7. 验收
- ffprobe：1920×1080，30 fps，aac 48k
- 响度 **−16 ± 0.5 LUFS**，真峰值 **≤ −1**（V3f：−15.97 / −2.75 / LRA 2.50）
- **OCR 白名单**（`snapshot/v3f/ocr_v3f.py`）：成片按每秒 3 帧抽帧，tesseract eng+chi_sim，psm 11；对照 BAN 列表，并列出置信度 ≥70 的英文词。画面上只允许我们自己的字幕，加上「AI」「99.9%」「iPhone」和数字。命中的帧逐个放大目检（V3f 的「@」命中都是眼睛、水瓶之类的误识别）
  - 跑 OCR 时要设 `OMP_THREAD_LIMIT=1`，否则 8 个并行进程会把机器拖到负载 38
- 12 帧检查图：`preview/sheets/v3f_check.jpg`

## 8. 过审清单（发布前逐条打勾）
- [ ] 标题、话题里不放敏感地名或事件词（V3 版标题和话题带「霍尔木兹海峡」，被判「不适宜公开」）
- [ ] 画面里没有他台台标、水印、平台 UI、用户名、头像
- [ ] 没有「素材/信源/来源」角标，也没有外媒报道标题图
- [ ] 口播和字幕里没有媒体名、平台名、外网、外媒、搬运号
- [ ] 人脸已打码
- [ ] 灾难画面已压低，没有血腥、惊悚内容，不评述灾难
- [ ] 弹幕只有中性内容；不引导观众去外网搜索
- [ ] OCR 白名单通过；响度、真峰值通过
- [ ] 外来素材都配了自己的讲解、圈注、对比（评论/核查类二创，不是简单搬运）

## 9. V3/V3d 被拦的教训（依据：用户发来的抖音后台截图）
- 2026-10-18 20:10 发布的版本：标题「霍尔木兹海峡漂满免费 iPhone？…」，话题 `#AI造假 #iPhone #霍尔木兹海峡`，时长 1:18 → 状态 **「不适宜公开」**
- 2026-10-18 21:18 发布的版本：标题「满海漂着免费 iPhone？AI 画面拆给你看 …」，时长 1:18 → 仍然 **「不适宜公开」**。所以光改标题不够，画面和口播也有问题
- 当时画面里有：BBC 台标和横幅、「素材/信源」角标、外媒报道页、平台评论 UI 和用户名、未打码的人脸、冒烟大船和哄抢人群；口播里有 BBC、@Grok、OpenAI、Hive、搬运号
- V3f 按第 3–5 节逐项清理后，定时在 2026-10-19 11:00 发布。简介写「核查依据为公开报道和检测工具」（截至冻结时还没有审核结果）
- 平台没有给出具体原因，以上是对照截图做的推断

## 10. 发布设置
- **内容标识：** 选「AI 生成内容」；引用了站外素材的，选「引用来源 → 站外」
- **不加定位**（「添加标签 → 位置」留空）；不关联敏感热点
- 标题和话题不放敏感地名；简介写「核查依据为公开报道和检测工具」，不放外链
- 署名：图片换成 CC0 后就不需要署名（V3f 用到的货轮照片 Martin Dörsch、飞机照片 AlfvanBeem、手推车，都是 CC0），可以选加一行；BGM 署名可选
- 封面：主体清楚，Q 版小官和主体互动，封面要真的展示标题承诺的内容（iPhone 用的是封面 B）

## 11. 媒体文件（不复制，只记路径）
- PC 工程：`D:\编程\项目\视频制作\作品\2026-10-18_iPhone假货\remotion\`（public\v3\clips、img、audio、sfx、fonts）
- box 工程：`/workspace/iphone-fake/v2/remotion/`；配音 `/workspace/iphone-fake/v2/vo/`；超分 `/workspace/iphone-fake/v2/v3e/sr/`；OCR 报告 `/workspace/iphone-fake/v2/v3f/ocr/ocr_report.json`
- 原始素材：box `/workspace/iphone-fake/source/`
- 人脸模型：box `/workspace/models/yunet.onnx`

## 目录
```
README.md           本文件
params.json         数值参数
v3f_naming.md       称呼调研（规定原文 + 链接）+ 口播改句对照表
snapshot/remotion/  src（含 v3 / v3d / v3e / v3f）、scripts（build_v3.py、v3f_patch.py、font_v3.py、stills_v3.mjs 等）、package.json、配置文件
snapshot/vo/        tts.py（只从环境变量读 key）、v3f/gen_f.py、feats_f.py、build_f.py
snapshot/v3f/       faces.py、faceblur_v3f.py、ocr_v3f.py、sr_finish_v3e.ps1
```
