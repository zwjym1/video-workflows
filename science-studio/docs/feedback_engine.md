# Feedback Engine（内容反馈与持续优化引擎）v1 · 2026-10-21

在现有「数据闭环」（schema v2：mark_published / due_checkpoints / ingest_metrics / diagnose / harvest_comments / insights / weekly_report）上做的增量。采集器、Remotion 动画、项目管理和 Drive 资产库都没有重做。
改动前的备份在 `backup/pre_feedback_20261021/`，里面有 studio.db、scripts/、config/、两份 README 和 skills_final。

## 1. 数据源（实测结论）
| 来源 | 状态 | 用法 |
|---|---|---|
| 抖音开放平台 video.list / video.data / data.external.item / item.comment | **不接**：用户确认个人号申请不到 | `adapters/douyin_openapi.py` 只是 stub，调用一律抛 `NotAuthorized`。拿到授权后再实现，令牌只从环境变量读 |
| 创作者中心截图（作品列表、作品分析、总览） | **正式数据源** | `ingest_screenshot.py`：qoder Flash OCR → 核对单 → 与人工读数对照 → confirm 才入库（verified=1） |
| 创作者中心 xlsx 导出 | 正式数据源 | `ingest_metrics.py`（原有）。xlsx 数值比截图精确时优先保留 xlsx |
| douyin-field-collect（免登录） | 能采**有链接**的公开视频评论（实测某同题视频取到 6/10 条）。采**自己作品**评论现在做不到：库里 3 条已发布作品都没链接；so.douyin.com 游客搜索用标题、账号名搜了 3 次都找不到本账号作品 | 有链接后用 `harvest_comments.py`；没链接就让用户截评论区图，再跑 `comments_fb.py add-shot` |
| 同题他人视频评论 | 可采 | 用 ingest_field 入库，在报告里标「同题评论（不是本账号观众）」 |

## 2. 新表（schema v3，`db.py: migrate_v3()`，幂等；只加列加表，lessons 重建一次以放宽 type）
- `metrics_snapshots` 新增列：
  - `age_h`：真实的发布后小时数。
  - `stat_cutoff`、`missing_fields`、`verified`、`verify_note`。
  - `precision_note`：例如「1.3万 ±500」「17秒 ±0.5s」。
- `metric_values`：字段级出处，记每个数从哪张图、哪个 xlsx 来，用的什么方法（xlsx / screenshot_ocr / manual_read），精度多少，是否核过。
- `screenshot_extractions`：每张图 × 每条作品一次 OCR。状态有 待核 / 已确认 / 有出入 / 作废。
- `screenshot_files`：图片登记。sha256 查字节重复；dhash（256 位感知哈希，距离 ≤8）查**内容重复**。
- `traffic_terms`：作品后台的**真实**数据，包括搜索来源词、看后常搜、流量来源、章节点击。
  - 游客态拿到的「相关搜索」（search_sug、page_suggest_words、comment_top_rec 等）仍放在 `demand_sightings.source_kind`，两边分表，不混。
- `retention_marks`：平台在留存图上标的低谷（时间段，截图读出，±1–2s），以及和「同类作品」参考线的定性对比。
- `hourly_plays`：每小时播放，读图得到，是近似值。
- `comment_labels` / `comment_clusters`：评论分类和聚类结果。
- `findings`：诊断六项。
- `suggestions`：状态有 待批 / 已批 / 拒绝。
- `hypotheses`：状态有 未验证 / 验证中 / 已支持 / 已否定，否定的也保留。
- `lesson_outcomes`：已批经验在后续作品上的真实表现。
- `backups`：Drive 备份记录，包括 sha256、size、md5、回读校验结果。
- `lessons.type` 新增「已批改进」，同时加了 `suggestion_id` 和 `stage` 两列。
- `works` 新增 `publish_title`、`douyin_item_id`、`duration_label`。

## 3. 命令
```bash
# 截图入库（每次 ≤5 张一批调 qoder Flash；内容重复的图自动跳过）
python3 scripts/ingest_screenshot.py extract <图...> [--work EP] [--checkpoint auto] [--captured-at '2026-10-21 10:57']
python3 scripts/ingest_screenshot.py check <id> --expect plays=722 completion_rate=5.33% "term:搜索来源词:广交会外骨骼助行器=23.9%" src:搜索=41.9% "chap:00:42 视频分析=75.6%"
python3 scripts/ingest_screenshot.py confirm <id> [--set ...] [--term '搜索来源词:词=57.2%'] [--marks 低谷1=00:01-00:02 ...] [--marks-verified] [--vs-peer '...']
# 评论/需求
python3 scripts/comments_fb.py analyze --collection <id> | --work <EP>
python3 scripts/comments_fb.py add-shot <EP> --text "评论原文" --likes 3 --source 截图名
# 六个指令入口（中文/英文都行），报告写到 reports/feedback_<cmd>_<时间>.md
python3 scripts/feedback.py 复盘最新视频 [--work EP | --all]
python3 scripts/feedback.py 检查最近作品表现 [--days 14]
python3 scripts/feedback.py 最近观众有什么新需求 [--days 7]
python3 scripts/feedback.py 找出近期最值得改进作品
python3 scripts/feedback.py 对比这期与历史同类 [--work EP]
python3 scripts/feedback.py 根据历史反馈开始下一期选题 [--topic 关键词]
# 经验库（只有用户明确批准才执行 approve；Bot 不得自批）
python3 scripts/approve_suggestion.py list --status 待批
python3 scripts/approve_suggestion.py approve <id> --note "用户原话+时间"   |  reject <id>
python3 scripts/approve_suggestion.py hyp <hyp_id> 已否定 --result "依据"
python3 scripts/approve_suggestion.py track      # 有新快照后：给已批经验挂后续表现
python3 scripts/search.py feedback "开头 跳出"    # 选题/脚本/分镜阶段检索历史反馈
# Drive 备份
python3 scripts/fb_backup.py plan → Bot UploadFile（manifest 里的 folder_id）→ record <路径> <id> → DownloadFile 回读 → verify <路径> --size <Drive size> --readback <副本>
```

## 4. 诊断口径（每份报告开头都会写）
- 只用已核快照（verified=1）下结论；没核的标「待核」并降低可信度。
- **变化检测不用固定增长阈值**：
  - 和作品**自身历史**比：看相邻快照的差值和每小时增量。差值小于显示精度的（如 1.3万 ±500）记「无法区分」。
  - 和**账号同档作品**比：按发布时长分档（≤6h / 6–36h / 36–120h / >120h），给出排名、其他作品的最小–中位–最大值、是否超出其他作品的范围，并写明 n。n<5 只当线索。
  - 不说「平台算法规律」。
- 每条发现都写六项：现象、依据和基准、可能原因与**其他解释**、可信度、建议、可验证的下一轮实验。相关不等于因果。
- 时间段诊断只在有平台标注低谷（retention_marks）时才做，精度到时间段（±1–2s），并对到逐字稿的句子、逐字时间戳和镜头。没有逐秒留存数值，就不说「第 N 秒掉了 X%」。
- 时间轴版本要核对：Roadster 只有 V3 工程（V4 不在盒上），报告里会带上警告。

## 5. 第一版真实运行结果（2026-10-21 10:51–11:14，Asia/Shanghai）
**截图入库**
- 共 8 张图：1 张作品列表、6 张作品详情、1 张 10-18 的 Roadster 旧看板。其中 canton_traffic_dup 与原图内容相同（dhash 距离 0），已跳过。
- 一共 9 条 extraction，全部已确认。截图 OCR 与人工读数逐项一致。
- 唯一缺的是 Roadster 搜索第 1 名的占比：OCR 被悬浮按钮挡住，只看得到「57.2」开头，用人工值补上并在出处里注明。

**OCR 纠错**
- 10-18 人工转录时有两个词被截断，OCR 复核后改为全称：「特斯拉新车为啥能够原地起飞」「特斯拉roadster2飞行」。已更正 lesson#7 和 traffic_terms。

**已核快照**（缺 0 字段）

| 作品 | 时点 | 播放 | 2s 跳出 | 5s 完播 | 均播 | 均播占比 |
|---|---|---|---|---|---|---|
| 广交会 | 40h（39.9h） | 722 | 33.03% | 39.39% | 8s | 22.95% |
| iPhone | 47h（47.4h） | 6945 | 31.34% | 50.26% | 17s | 22.33% |
| Roadster | 94h（94.0h） | 13000 | 40.78% | 46.43% | 17s | 18.98% |
| Roadster | 24h | 13320 | — | — | — | — |

- Roadster 94h 的播放「1.3万」±500。
- Roadster 24h 的数据来自 xlsx，与 OCR 一致；保留 xlsx 的精确值，verified=1。

**变化检测**
- Roadster 24h→94h：播放 13320→1.3万，在显示精度内无法区分；其余指标 ±0.05 个百分点以内。说明 24h 之后基本没有新增流量。

**评论采集**
- 自己作品：0 条，原因见第 1 节。
- 同题评论：3 条 Roadster 高赞同题视频，共 278 条评论，去重后 257 条。
  - 按主题：原理 31 条，能否上路 14 条，价格量产 12 条。
  - 按类型：科学质疑 2 条（如「这也没飞呀，就是一个变轨滑行」）。

**需求交叉**
- 作品真实搜索词里，有 11 个在需求库中没有，例如「广交会外骨骼助行器」「广交会机器人是真人吗」「霍尔木兹海峡苹果手机」「特斯拉新车为啥能够原地起飞」。
- 「过去未做、最近重现」：0 条。需求库最早的记录是 10-18，还不满 14 天窗口，所以这一项目前不可能出结果。

**诊断与建议**
- 16 条 findings，11 条 suggestions（全部「待批」），11 条 hypotheses（全部「未验证」）。见 `reports/feedback_review_20261021_1112.md`。

**Drive 备份**
- 4 个文件已上传并回读校验，size 和 md5 都一致：
  - 报告 zip → 07_创作经验与数据复盘
  - 原始快照 zip → 01_原始数据
  - 项目关联 json → 06_视频项目
  - DB 快照 → 08_索引与数据库备份
- 第二次运行 plan 时，内容没变的 3 个文件被正确标为「跳过重复」。

## 6. 拿不到的指标
| 指标 | 原因 |
|---|---|
| 逐秒留存**数值** | 截图里只有曲线形状、平台低谷标注和同类参考线，没有刻度点；导出 xlsx 里也没有。只能做「平台标注低谷」级别的诊断 |
| 按流量来源分的留存（搜索 vs 推荐） | 创作者中心不提供 |
| 自己作品的评论原文 | 没有作品链接；游客态搜不到本账号作品 |
| 评论热词、观众画像 | 用户这次没截这两页，记为缺失 |
| 封面点击率 | Roadster xlsx 里是「-」；截图里没有 |
| 统计截止时间 | 页面不显示；用截图时间作 captured_at，stat_cutoff 记 NULL |
| 每小时播放精确值 | 图上没有数据标签；hourly_plays 里存的是人工读图的近似峰值（approx=1） |

## 7. 定时监控
现有 routine「发布后数据回收」（每天 14:30 和 22:30，±15min）以及「科普账号数据周报」（周一 09:30）的 prompt，需要**用户或主 Bot 更新**，我改不了 routine。建议的文本见下面，以及交付回报。

## 8. 恢复操作
1. **回到 Feedback Engine 之前**：
   ```bash
   cp backup/pre_feedback_20261021/studio.db db/studio.db
   rm -rf scripts
   cp -a backup/pre_feedback_20261021/scripts scripts
   ```
   注意：旧版 db.py 遇到 v3 的库也能连（只是看不到新表），所以只回退代码、不回退库也能运行。
2. **从 Drive 恢复 DB**：
   1. 在「08_索引与数据库备份」里找最新的 `studio_YYYYMMDD_HHMM.db`，DownloadFile 到 `/workspace/science-studio/db/studio.restore.db`。
   2. 跑 `python3 -c "import sqlite3;print(sqlite3.connect('db/studio.restore.db').execute('pragma integrity_check').fetchone())"`，确认输出 `ok`。
   3. `mv db/studio.db db/studio.broken.db && mv db/studio.restore.db db/studio.db`。
   4. 跑一次 `python3 scripts/search.py stats`，触发迁移并核对行数。
3. **只恢复反馈数据**：解开 `01_原始数据/feedback_raw_*.zip`。tables/*.json 是各表全量，screenshots/ 是原图。重新 `ingest_screenshot.py extract` + `confirm` 可以完全重建；靠 sha256 / dhash 防重复。
4. **截图抽错了**：
   - 还没确认的：`ingest_screenshot.py void <id>`。
   - 已确认的：`confirm <id> --set 字段=正确值` 重新写入（记录保留，出处会写明人工改值）。
5. **建议批错了**：`approve_suggestion.py reject <id> --force`。对应的 lesson 用 `UPDATE lessons SET superseded=1 WHERE suggestion_id=<id>` 作废，不要删。
6. **重算报告**：`feedback.py <指令>` 可重复跑。findings 按「作品 + key + 报告名」去重；suggestions 按内容 hash 去重，不会重复登记。
