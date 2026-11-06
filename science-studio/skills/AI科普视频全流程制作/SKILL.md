---
name: AI科普视频全流程制作
description: >-
  （已废止草稿 2026-10-21，定稿见 skills/final/SKILL.md）用户说「开始新一期科普视频」「开始新一期精品科普视频」「继续上一期」时使用：
  秘书丞抖音/B站中文科普视频从选题到交付的总入口，按阶段路由到现有 skill，状态存 /workspace/science-studio。
---
# AI 科普视频全流程制作（总入口 · 路由器）

规范全文：`/workspace/science-studio/config/workflow_spec.md`；配置：`config/production_config.md`。本 skill 只做路由和状态，不重复写各 skill 的方法。

## 启动
- 「开始新一期科普视频」→ `python3 /workspace/science-studio/scripts/new_episode.py --tier daily`
- 「开始新一期精品科普视频」→ `--tier premium`
- 「继续上一期」→ 按 `config/resume.md`

## 硬规则（仅 6 条）
字幕一句一卡｜全片统一「丞」朱印角标｜发布不挂无关组件和定位｜不做 PPT 式示意图卡，用连续运动画面｜文案通过才配音、配音听审通过才对齐画面、不交无声骨架预览｜改稿按段验收，只改不合格段，不全片重渲。

## 路由
| 阶段 | 调用 | 用户闸门 |
|---|---|---|
| A 选题 | douyin-field-collect 采集 → 两级筛 → `research/topics.md`（日常 2–3 个/精品 5 个） | 选题 |
| B 创意 | skill-1792258671706 的事实表/素材溯源/红线部分 → `creative/directions.md`（≥2 个明显不同方向，推荐 1 个） | 方向 |
| C 逐字稿 | 本规范 §C（初稿+一轮深编，两版都留；锁定段不改） | 「文案通过」 |
| D 分镜 | 本规范 §D 11 字段 | 无（自检连续性） |
| E 制作 | 科普短片 → skill-1792258650910（猫学长 2D Remotion 的制作方法部分）；讲题/课程 → skill-1792258664507；3D 重渲染 → 用户 PC | 配音听审；风格帧 |
| F 质检 | 脚本检查 + qoder flash 抽帧初筛 + 我抽查 | 无 |
| G 审片 | 定位镜头 → 局部改 → 新版本 | 成片确认 |
| H 交付 | 清单见规范 §H；不发布 | 发布需另批 |

每步结束：`scripts/state.py stage|set|log|approve`。

## 渲染
短片默认在盒子上渲；传到 PC 的只有定稿成片和两张封面。~~PC 在线（ListMachines）→ PC，否则盒子~~【已废止 2026-10-29】。步骤见 production_config。本 skill 草稿已废止，以 `skills/final/SKILL.md` 和 `config/workflow_spec.md` 为准。

## 待首期验证后补
- PC 实测并发/耗时、PC 端 ffmpeg/Blender 情况
- qoder 看片提示词模板定稿
- A 阶段报告模板定稿
