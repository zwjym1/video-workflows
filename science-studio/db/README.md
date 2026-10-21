# 资产库 studio.db（第一阶段，2026-10-20）

SQLite 数据库，只放在盒上。Drive 上只存 `backup.py` 生成的带日期快照，不实时同步。检索入口是 `scripts/search.py`。

## 六库 + 关系
| 库 | 表 | 要点 |
|---|---|---|
| 观众需求 | demands（去重后的需求）、demand_sightings（每次看到记一条：采集时间、来源类型、视频/关键词、赞数、评论原始时间）、comments（全部原始评论）、ref_videos（同题/竞品视频） | kind：question=评论疑问，search=搜索词/推荐词。status：待研究/值得制作/暂缓/已制作/不适合 |
| 选题机会 | topics | 状态、未制作原因、角度、来源文件 |
| BGM 与音效 | bgm、bgm_license | 好听和能用分开存：user_rating 是用户评分，bgm_license 按平台分开记授权范围（允许商用/仅参考/未核实……）。bpm、energy_curve、segments 字段已留好 |
| 动画资产 | anim_assets | project/component/scene3d/footage/image/brand/font/tool；包括路径、标签、复用说明、授权、是否 AI 生成 |
| 视频作品 | works、work_metrics、content_dna | 指标只放用户提供的创作者中心导出或截图数据，并注明来源 |
| 创作经验 | lessons | type：长期偏好/单期意见/真实数据/未验证推测 |
| 关系 | links(from_type,from_id,rel,to_type,to_id) | demand→topic seen_in；topic→work made_as；asset→work used_in；asset→asset part_of；bgm→work used_in |
| 文件 | files | sha256 去重，记录 Drive 文件 id（备份去重用） |

## 常用命令
```bash
python3 scripts/ingest_field.py <采集输出目录> --topic "选题名"      # 每次采集后执行
python3 scripts/search.py q "治疗 抑郁"                               # 跨库检索
python3 scripts/search.py q "提示词" --lib demand --status 待研究
python3 scripts/search.py radar                                       # 需求复活雷达（默认：14 天前见过、近 7 天又出现、≥2 批采集、未制作）
python3 scripts/search.py bgm "whoosh" --platform douyin --usable     # 只列已核实可商用的
python3 scripts/search.py show work 1 ; python3 scripts/search.py status 3 值得制作 --note "..."
python3 scripts/ingest_seed.py                                        # 存量重登记（幂等）
python3 scripts/backup.py plan --with-works                           # 生成快照和上传清单（Drive HOLD 时只出清单）
```
中文检索：trigram 分词，3 个字及以上走 MATCH（bm25 排序），1–2 个字的词自动改用 LIKE。不需要装 jieba。

## schema v2（2026-10-21 数据闭环）
迁移在 `scripts/db.py` 的 `migrate()`：只加列、加表，每次 connect 时幂等执行。迁移前的备份在 `backup/pre_dataloop_20261021/studio.db`。
- 新表：
  - `metrics_snapshots`、`retention_curve`：存作品数据快照和留存曲线。
  - `insights`、`insights_history`：存跨作品规律及其状态变化。
- 新列：
  - works：发布时间、计划时间、链接、检查点、评论回采标记。
  - content_dna：分组用的类别字段。
- 旧表 `work_metrics` 保留不再写，新数据只进 `metrics_snapshots`。
- 回填脚本 `scripts/backfill_metrics.py`，所有数据都有来源，见脚本头注释。

## schema v3（2026-10-21 Feedback Engine）
迁移由 `db.connect()` 里的 `migrate_v3()` 完成，可重复执行。具体表和列见 `docs/feedback_engine.md` §2。
- 只有 verified=1 的快照才能用来下结论，每个数的出处查 `metric_values`。
- `traffic_terms` 存作品后台的真实搜索来源，游客态拿到的相关搜索存在 `demand_sightings`，这两类不要混在一起。
- `suggestions` 里的建议只有用户批准后才写进 lessons（type 为「已批改进」）。
- 恢复操作见 `docs/feedback_engine.md` §8。
