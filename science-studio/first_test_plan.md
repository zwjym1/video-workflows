# 首期完整测试方案（等用户说「开始新一期科普视频」后执行）

目标：用一期**日常档**真实作品跑通 A–H，验证规范、状态、渲染路由、质检和交付，再把流程定稿成 Skill「AI科普视频全流程制作」。不另外做演示片。

| 步 | 做什么 | 验证点 | 产出 |
|---|---|---|---|
| 0 | `new_episode.py --tier daily` 建 EP | state.json/STATE.md/INDEX 自动生成 | projects/EP-…/ |
| A | douyin-field-collect：先 `dy_search`+`sug` 低成本筛 6–10 个候选，再对入选 3 个各跑 2–3 条 `video`（评论 200 条、推荐词）；结果缓存 data/field | 字段状态写清；不编造数据；耗时 | research/topics.md（2–3 个） → **用户选题** |
| B | 事实表（权威来源）+ 2 个明显不同方向，推荐 1 个 | 方向差异是否真的明显 | creative/directions.md → **用户定方向** |
| C | 初稿 → 一轮深编，两版都留 | 锁定段机制；「文案通过」才往下 | script/v1_draft.md、v2_edit.md → **文案通过** |
| D | 自动分镜（11 字段）+ shots.json + 连续性自检 | 无 PPT 卡；镜头可执行 | storyboard/v1.md |
| E1 | 先做开头 2–3 个镜头风格帧（静帧，不交无声骨架视频） | 风格对不对 | 风格帧图 |
| E2 | Fish s2.1-pro-free 整篇配音 + ASR 核对 | 读音、时长 | vo/ → **用户听审** |
| E3 | 复用最接近的 Remotion 工程，按时间戳对齐，字幕一句一卡，「丞」角标 | 5 帧布局检查 | remotion/ |
| E4 | 渲染：PC 在线→PC（每条命令批准，记录并发/耗时）；离线→盒子 720p | 渲染路由真跑通 | render/ |
| F | blackdetect/freezedetect/帧数/响度/字幕比对/镜头覆盖 + qoder flash 抽帧 + 我抽查 | 报告如实写「未确认」项 | review/qc_v1.md |
| G | 带声 720p 预览给用户；按意见只改不合格段 | 版本保留可恢复 | review/changes.md |
| H | 1080 母版、srt、终稿、分镜、封面、标题简介、项目记录、经验；不发布 | 交付清单齐 | delivery/ |
| 收尾 | 把实测数据写回 production_config / env_report；Skill 草稿定稿并安装（用户确认后） | — | skills/ |

## 成功标准
- 每个用户闸门都停下等确认；没有无声骨架预览；6 条硬规则全满足。
- 「继续上一期」能从 state 准确续上（中途至少用一次）。
- 局部修改时只重渲受影响段。

## 风险
- 采集被验证码拦：如实记录，停该项，改用公开榜/用户截图。
- PC 不在线：盒上 CPU 渲 1080 全片较慢，先出 720p 预览。
- 免费 TTS 情感有限：用户已知并选择默认免费。
