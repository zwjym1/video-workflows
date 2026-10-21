# science-studio · 秘书丞 AI 科普视频总导演

只放规范、配置、状态和索引；素材和工程留在原处（见 assets/INDEX.md）。

- config/workflow_spec.md　工作规范（维护版，用户 2026-10-20 修改已并入）
- config/production_config.md　渲染路由、TTS、ASR、看片、规格、响度
- config/account.md　账号定位　｜　config/resume.md　「继续上一期」步骤
- state/template/state.json　每期状态模板
- scripts/new_episode.py　新建一期　｜　scripts/state.py　更新/查看状态
- projects/　每期 EP-YYYYMMDD-NN（INDEX.md 自动生成，LEGACY.md 旧项目）
- data/　采集缓存　｜　assets/INDEX.md　资产与旧规范索引（含已废止标注）
- reviews/　偏好、发布数据、经验、每期复盘　｜　skills/final/SKILL.md　入口 Skill 定稿（skills/AI科普视频全流程制作/ 为已废止草稿）
- 数据闭环：scripts/mark_published.py｜due_checkpoints.py｜ingest_metrics.py｜diagnose.py｜harvest_comments.py｜insights.py｜weekly_report.py（见 production_config「数据闭环」；周报 reviews/weekly/）
- db/studio.db　资产库（需求/选题/BGM/动画资产/作品/经验 + 关系，FTS 中文检索）；说明 db/README.md；入口 scripts/search.py
- env_report.md　环境实测　｜　first_test_plan.md　首期完整测试方案

启动：「开始新一期科普视频」
