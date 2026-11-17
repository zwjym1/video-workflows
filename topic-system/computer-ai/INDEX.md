# 电脑与 AI 选题系统

轻量文档 / JSON 题库。电脑与人工智能是主方向，题型不固定。

| 文件 | 作用 |
|---|---|
| [SYSTEM.md](SYSTEM.md) | 现行规则（v2026.11.17.7）：先发现再筛选；需求、竞争、未满足机会与传播四块证据；参考优先近期作品并核对现状适用性；定题后再做同题深调研（底线 8、目标 10，未满实报） |
| [USER_FLOW.md](USER_FLOW.md) | 用户可见流程（选题到制作三门的交接，制作细节以已批准工作流为准） |
| [topics.json](topics.json) | 题库总表 |
| [TODAY_20261117_expanded.md](TODAY_20261117_expanded.md) | 2026-11-17 扩大选题后的正式候选（5 题）；用户已选「为什么 AI 聊久了，会忘记之前的设定」 |
| [TODAY_20261117_demand_competition.md](TODAY_20261117_demand_competition.md) | 同日 17:51 按需求与竞争重核后的记录（当时 2 条，现已让位，仅保留） |
| [TODAY_20261117_evening.md](TODAY_20261117_evening.md) | 同日 17:16 晚间短名单记录（已被后续轮次取代，仅保留） |
| [TODAY_20261117.md](TODAY_20261117.md) | 同日早市候选记录（已让位；CPU 随后暂停） |
| [topic_cards/](topic_cards/) | 每题一张 JSON 卡片 |
| [templates/topic_card.json](templates/topic_card.json) | 新题卡片模板 |
| [templates/CANDIDATE_BRIEF.template.md](templates/CANDIDATE_BRIEF.template.md) | 每轮交给用户的可读候选简报 |
| [templates/postmortem.json](templates/postmortem.json) | 发布后表现，空着等真实数据 |
| [OLD_SYSTEM_COMPARISON.md](OLD_SYSTEM_COMPARISON.md) | 与旧 topics-workflow 原文的对照（含 GitHub 路径） |
| [CHANGES.md](CHANGES.md) | 本选题系统规则与题库的变更说明 |
| [README.md](README.md) | 目录说明 |

规则版本：v2026.11.17.7。题库现为 18 题（原完整库 13 题，加上扩大选题轮 5 道新卡）。2026-11-17 当前状态：用户已选定「为什么 AI 聊久了，会忘记之前的设定」；CPU 核心数旧稿保持暂停、未删除。本周期仍不选盐、鱼，不重复芯片分档，不把未核原义热词写成技术热点。制作与核验成本不参与推荐排序。

每轮先交用户可读候选，不等把同题 8 条看完再交列表；但未满 8 条必须标明，不能把未观看当成完整调研。选定后再走制作工作流 v2026.11.17.1（选版后先审静态帧和逐镜 → 通过后带声关键段 → 全片发布包），不在这里直接写完整稿或做视频。同题内容依据与跨题形式参考要分账；参考优先近期作品，并记录发布时间和现状适用性；看图记录保留原模型标签。
