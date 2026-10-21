<!-- 粘贴到 skills/final/SKILL.md：替换阶段 1/2 开头、阶段 8，并新增「发布后」阶段 -->
### 阶段 1、2 开头（新增第 0 步）
0. 先读数据规律：`python3 scripts/search.py insights`。「已验证」的规律当依据（在选题理由或稿件说明里写引用了哪条）；「验证中」的只当线索，要用就写明是试验。也看 `weekly_report.py` 的追更候选（`follow_up_of` 需求）。

### 阶段 8 归档（追加）
- 归档时给 content_dna 填上 hook_class / topic_class / duration_s，供分组统计。
- 定好发布时间就跑：`python3 scripts/mark_published.py <EP> --plan 'YYYY-MM-DD HH:MM'`

### 9 发布后（数据闭环）　【用户只需：告诉发布时间和链接、导出数据】
1. 用户说发了：`mark_published.py <EP> --time '实际时间' --url <链接> --search-first yes|no`
2. 每次对话开头或定时任务跑一次 `python3 scripts/due_checkpoints.py`，只把 reminders 里的 message 转述给用户，每条只提醒一次：
   - 2h/24h/72h 到了：请用户导出数据。
   - 缺链接或缺发布时间：问一次。
   - 计划时间过了 3 小时还没发：问一次，然后跑 `--mark-asked`。
3. 收到导出表后依次跑：
   - `ingest_metrics.py <xlsx> --work <EP> --checkpoint 24h`
   - `diagnose.py <EP>`
   - `insights.py recompute`
   截图里有、表里没有的数，用 `--set` 补上，并在 `--source` 写明出处。
4. 把 diagnose 的结果讲给用户：掉人最多的几秒对应哪句话、哪个镜头，和账号均值比怎么样，下期改哪里。样本不够就直说，不下结论。
5. 发布满 24 小时且有链接：跑 `harvest_comments.py <EP>`，把追更候选报给用户，下期选题用。
6. 每周跑一次 `weekly_report.py`，告诉用户周报路径和下周选题建议。
7. 只用真实数据，每条都写来源，不估不编；我们不替用户发布。
