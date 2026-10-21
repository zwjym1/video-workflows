# 版本标签说明

每个能用的版本都打了一个 git 标签，以后怎么改都能退回去。

| 标签 | 内容 |
|---|---|
| `pi-lesson-v1` | π 的历史 第一版：首次全片渲染，偏普通 2D 画风 |
| `pi-lesson-v2` | 第二版：改回剪纸/纵深/光影实物风，固定分区不遮挡，转场先退后进 |
| `pi-lesson-v3` | 第三版（已渲染，待审核）：圆形广场新文案、「量」读 liáng 修正、删掉"四分之一"段落、第三章加放大镜；附配音脚本和渲染指南 |
| `gradient-descent-v4` | 梯度下降科普短视频 v4 源码和配音脚本 |
| `roadster-v1` | 特斯拉 Roadster 第一版（合成 RoadsterShort）。v1/v2/v3-preview 是一起首次入库的，这三个标签指向同一提交 |
| `roadster-v2` | 第二版（src/v2，同上一提交） |
| `roadster-v3-preview` | v3 预览：差评君风格重写、新音色、BGM 闪避混音（RoadsterShortV3） |
| `roadster-v3.1` | v3.1：footage-timeline.json 控制镜头、对齐工具、三处画面修正 |
| `roadster-v3.2` | v3.2：自制 BGM +3dB、混音写进 JSON、对齐工具混音台 |
| `roadster-v3` | **v3 定稿**：播放器卡死修复、用户定稿的 footage-timeline.json、render:master / remix-audio；成片 特斯拉Roadster-v3.mp4 |
| `roadster-workflow-v1` | 「热点科普（Roadster 款）」工作流模板冻结版：workflows/hot-science-roadster/（README、params.json、V3 终版源码快照）。原定标签名 roadster-v1 已被 Roadster 第一版占用，所以改用这个名字 |
| `ai-debunk-v1` | 「AI 辟谣拆解（iPhone 款）」工作流模板冻结版：workflows/ai-debunk-iphone/（README、params.json、v3f_naming.md、V3f 源码和打码/OCR/配音脚本快照） |

## 怎么退回某个版本

```bash
git fetch --tags
git tag                      # 看所有版本
git checkout pi-lesson-v2    # 只看/渲染旧版本（只读状态）
git checkout main            # 回到最新
```
想在旧版本基础上继续改：
```bash
git checkout -b fix-from-v2 pi-lesson-v2
```
只恢复某个文件到旧版本：
```bash
git checkout pi-lesson-v2 -- projects/pi-lesson/remotion/src/某文件.tsx
```

## 以后新增版本
确认一版可用后：
```bash
git add -A && git commit -m "说明改了什么"
git tag -a pi-lesson-v4 -m "说明"
git push && git push --tags
```
成片 mp4 不入库，放在 `D:\编程\项目\教学动画\<视频名>\`。

## 文档与技能

| 版本 | 内容 |
|---|---|
| `v-preprod-2026-10-18` | 新增 `skills/tech-preproduction/`（科技短视频前期调研与核查）和 `docs/PREPRODUCTION-WORKFLOW.md`。对照附件核对 `skills/kepu-short-video/SKILL.md` 与 `skills/primary-lesson-video/SKILL.md`，内容一致，未改。 |

## 2026-10-21 全流程入库（workflow-full-2026-10-21）
新增四个目录：
- `agent-skills/`：五个当前在用的 skill。
- `science-studio/`：数据闭环和 Feedback Engine，schema v3。
- `topics-workflow/`：选题、文案和前期 SOP。
- `templates/`：渲染、传输、质检、混音的模板。

回退到上一版：`git checkout 97923ab`。旧目录都没有改动。
