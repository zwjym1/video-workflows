---
name: AI科普视频全流程制作
description: >-
  秘书丞抖音/B站中文科普视频从选题到发布包再到发布后数据闭环的总入口：用户说「开始新一期科普视频」（日常档）、「开始新一期精品科普视频」（精品档）、「继续上一期」，或告知已发布/发来创作者中心数据时使用；按阶段路由到
  douyin-field-collect、选题闸门、猫学长2D、讲题等现有 skill，状态与资产库在
  /workspace/science-studio，不代发布。
---
# AI 科普视频全流程制作（总入口）

本 skill 只管**顺序、闸门、状态和路由**，方法细节不在这里重复，按下表去读对应文件。脚本都在 `/workspace/science-studio/scripts/`。

| 内容 | 位置 |
|---|---|
| 规范全文（冲突时以它为准，§1 硬规则、§1.1 执行规则、§9 数据闭环） | `/workspace/science-studio/config/workflow_spec.md` |
| 渲染/传输/质检/TTS/Drive/数据闭环配置 | `/workspace/science-studio/config/production_config.md` |
| 「继续上一期」步骤 | `/workspace/science-studio/config/resume.md` |
| 资产库（需求/选题/BGM/动画资产/作品/经验/数据/规律） | `db/studio.db`，入口 `scripts/search.py`，说明 `db/README.md` |
| 素材与旧规范索引（含已废止标注） | `assets/INDEX.md` |
| 首期样板（全流程跑通） | `projects/EP-20261021-01`（工程 `/workspace/optogenetics`） |

## 硬规则（只有这 6 条是闸门）
1. 字幕一句一卡。
2. 每部片统一「丞」朱印角标（`/workspace/brand/v2/avatar_1_朱印丞.png`）。
3. 发布不挂无关组件和定位。
4. 不做 PPT 式示意图卡，用连续运动的画面。
5. 文案通过才配音；配音听审通过才对齐画面；不交无声骨架预览。
6. 改稿按段验收：只重渲不合格的那段，不全片重渲。

执行规则（spec §1.1，同样照做）：PC 在线就在 PC 渲染（含 720p 预览）；PC 文件只放 `D:\编程\项目\视频制作\作品\<YYYY-MM-DD_选题>\{out,发布,工程,预览}`，不在 `C:\Users\Administrator` 下建目录；大文件 ≤4 MB 分块传 + SHA256；渲后 ffmpeg + qoder Flash 质检、我只汇总；配音按意思段生成、只出一条；发布包自动附发布页逐项清单；创意文案能路由 opus5.5 就路由。

## 启动
- 「开始新一期科普视频」→ `python3 /workspace/science-studio/scripts/new_episode.py --tier daily --title "<暂定题>"`
- 「开始新一期精品科普视频」→ `--tier premium`
- 「继续上一期」→ `python3 scripts/state.py latest`，再按 `config/resume.md`；核对 state 里的文件真的存在，从 `next_action` 继续，已批准的不重做。
- 旧目录续做 → `new_episode.py --adopt <旧目录>`（不搬文件）。
- 每完成一步：`scripts/state.py stage|set|log|approve <EP> ...`。
- 用户说「发了」或发来创作者中心 xlsx → 直接跳到阶段 9。

## 阶段

### 1 选题与实地包　【用户闸门：选题】
0. 先读数据规律：`python3 scripts/search.py insights`。「已验证」的当依据（在选题理由里写引用了哪条）；「验证中」的只当线索，要用就写明是试验。也看周报里的追更候选（`follow_up_of` 需求）。
1. 再查库：`search.py q "<关键词>"`、`search.py radar`（看旧需求、做过没、可复用资产、复活需求）。
2. 采集：skill **douyin-field-collect**（`/home/box/agent-data/workflows/douyin-field-collect/SKILL.md`），两级筛：先 `dy_search`+`sug` 低成本过滤，再对入选题跑 `video`。输出到 `projects/<EP>/research/field/`。
3. 采完立刻入库：`python3 scripts/ingest_field.py <输出目录> --topic "<候选题>"`。
4. 选题判断参考 skill **skill-1792258671706**（科技短视频前期调研与核查）的事实核查和红线部分；其中的权重和硬门槛已废止。
5. 产出 `research/topics.md`：日常档 2–3 个、精品档 5 个，用文字推荐，写清真实来源和不确定性，不编播放量。等用户选。

### 2 事实表 + 创意方向 + 逐字稿　【用户闸门：方向、「文案通过」】
0. 同样先读 `search.py insights`，开头、标题、时长、段落节奏按已验证规律来，并在稿件说明里写引用。
1. 事实表 `research/facts.md`：权威来源，数字用代码复算，每条核到原文（人名、作者顺序这类细节也要核）。
2. 创意方向 `creative/directions.md`：至少 2 个明显不同的方向，推荐 1 个。
3. 逐字稿：`script/v1_draft.md` → 一轮深编 → `script/v2_edit.md`。用户给了原稿就逐字用原稿。
4. 写稿时就为配音着想：少用感叹号和「居然」「最让人破防」这类容易被读成喊的写法。
5. 只有用户说「文案通过」才往下走；锁定的段落不改。

### 3 配音　【用户闸门：听审】
- Fish `s2.1-pro-free`，音色见 production_config。按意思段（3–5 句）带前后文生成，音调靠标点和断句管住。
- **只出一条**给用户听，不批量出 3 条；不做事后压音高，不大幅变速。
- 用户点出的问题，整段带上下文重配，再截出要换的句子。
- 过审后取逐字时间戳（Fish 自带，ASR 复核），写进 state。

### 4 分镜设计
- 按 spec §D 写 `storyboard/v1.md` 和 `shots.json`，用连续运动的画面，不做图卡；优先复用 `assets/INDEX.md` 和 `search.py q ... --lib asset` 能查到的资产。
- 制作方法：科普短片走 **skill-1792258650910**（猫学长 2D Remotion：时间戳驱动、分区防遮挡、布局自检），讲题或课程走 **skill-1792258664507**。那两个 skill 里的钩子公式、句式要求、逐句配音已废止。
- 画面按新配音的时间轴对齐，画跟声走；AI 生成的画面要标「AI 生成」，来源写进 `assets/SOURCES.md`。
- 把逐句/分段时间轴路径写进 works.timeline_path，发布后 diagnose 要用。

### 5 分段预览（PC 并行）　【用户闸门：逐段审】
- 每段做独立入口（参照 `/workspace/optogenetics/remotion/src/film/seg4/entry.tsx`），各段可以并行做。
- 渲染：先 ListMachines。PC（PC-20260301WTTM）在线就在 PC 渲，每条命令都要用户批准；离线才用盒子。脚本模板是 `/workspace/optogenetics/pc_pack/render_film_pc.ps1`，用 `-Mode 720 -Frames a-b -Root <D盘工程>`（-Root 必填），`Start-Process` 脱离运行并写日志。
- 每段带声 720p 预览交用户人工审。用户点哪段就只改哪段（硬规则 6），新版本用新文件名，旧版本保留；改动记进 `review/changes.md`。

### 6 全片渲染 + 质检
- 所有段都过了，在 PC 上 `-Mode 1080` 渲全片，输出到 `out\`。只改声音时不重渲画面，用 ffmpeg `-c:v copy` 换音轨。
- 质检按 production_config 的「渲后质检」：
  - ffmpeg 测黑屏、冻帧、响度（−16 LUFS，真峰 ≤ −1.5 dBTP）、接缝爆音。
  - 每 5 秒抽 1 帧交 qoder Flash 判，每次 ≤5 张；我只汇总 Flash 的结论。
  - 滑入、滑出瞬间的截边不算硬错。只自动修硬错，审美问题交用户。
- 结果写 `review/qc_vN.md`。

### 7 发布包（自动附上，不等用户问）　【用户闸门：用户自己发布】
放 PC 的 `发布\`，盒上留一份：
- 封面 A/B：9:16，加 3:4 信息流安全区核对，B 站加 4:3。
- 3 个搜索词前置的标题，推荐其中 1 个。
- 可直接粘贴的简介：含章节、素材署名与协议、AI 说明；话题标签。
- 置顶评论、备用回复、建议发布时间。
- **抖音发布页逐项清单**（按页面顺序）：
  - 视频章节：每条写时间点 + 标题。
  - 添加标签：位置留空。
  - 关联热点：没有直接相关的就留空。
  - 谁可以看：公开。
  - 保存权限：允许。
  - 发布时间：立即发布，或定时到具体时刻。
  - 作者声明：勾「内容由 AI 生成」。
- 我们永远不替用户发布。

### 8 归档 + 复盘
1. state 改成「待发布」或「已发布」，写入 PC 成片路径。定好发布时间就跑 `python3 scripts/mark_published.py <EP> --plan 'YYYY-MM-DD HH:MM'`。
2. 入库 `db/studio.db`：
   - works：状态可用 已发布 / 待发布 / 制作中 …
   - content_dna：填上 hook_class / topic_class / title_search_first / duration，供规律分组统计。
   - 本期新增的可复用资产登记进 anim_assets / bgm，授权分开写。**每期至少新增一项可复用资产。**
   - lessons 分四类：长期偏好、单期意见、真实数据、未验证推测。
   - 示例脚本：`scripts/archive_ep01.py`。
3. 传 Drive「AI科学内容资产中心」（connection `user-Google-drive`，各文件夹 id 见 `config/drive.json`）：
   - 在 06 下建本期文件夹，放稿件、事实表、发布包、封面、混音 m4a。
   - 07 放复盘，08 放 `backup.py plan` 生成的 DB 快照和文档 zip。
   - 每传一个就跑 `backup.py record`。**成片（>100 MB）留在 PC 不传。** Drive 上不删任何东西。
4. 复盘写 `reviews/<EP>_<题>_复盘.md`，包括内容 DNA、做得好的、要改进的。数据段由阶段 9 的 diagnose 填，不估不编。

### 9 发布后（数据闭环）　【用户只需：告诉发布时间和链接、导出数据】
1. 用户说发了：`mark_published.py <EP> --time '实际时间' --url <链接> --search-first yes|no`。
2. 定时任务「发布后数据回收」每天 14:30/22:30 跑 `due_checkpoints.py`，只把 reminders 里的 message 转述给用户，每条只提醒一次：
   - 2h/24h/72h 到了：请用户导出创作者中心数据。
   - 缺链接或缺发布时间：问一次。
   - 计划时间过了 3 小时还没发：问一次，然后跑 `--mark-asked`。
3. 收到导出表后依次跑：
   - `ingest_metrics.py <xlsx> --work <EP> --checkpoint 2h|24h|72h|7d`
   - `diagnose.py <EP>`
   - `insights.py recompute`
   截图里有、表里没有的数，用 `--set` 补上，并在 `--source` 写明出处。
4. 把 diagnose 的结果讲给用户：掉人最多的几秒对应哪句话、哪个镜头，和账号均值比怎么样，下期改哪里。样本不够就直说，不下结论。
5. 发布满 24 小时且有链接：跑 `harvest_comments.py <EP>`，把追更候选报给用户，下期选题用。
6. 定时任务「科普账号数据周报」每周一跑 `weekly_report.py`，告诉用户周报和下周选题建议。
7. 只用真实数据，每条都写来源，不估不编；我们不替用户发布。

## 需要用户明确批准
选题、创意方向、「文案通过」、配音听审、逐段预览和成片；付费服务、换付费 TTS 或音色、外部账号设置、删除重要文件、发布。PC 上的每条命令都在批准卡上点。不索要密码或 Cookie，密钥只走环境变量。
