# football-studio

这是 2026-11-16 足球战术制作方向的**可恢复源码档案**。它独立放在本目录，没有登记进现有科普流程。

现有入口仍是仓库根目录 `README.md` 里的 `agent-skills/`、`topics-workflow/`、`science-studio/`、`skills/`、`workflows/` 和 `projects/`。本目录没有 `SKILL.md`，也没有写入那些目录。快照里的 `football-knowledge-base/PARENT_RULES_TO_SAVE.md` 只作为当时的备忘保留，这次提交没有把它装进全局技能或制作规则。

## 状态

- 已渲染成片是旧方案 `arsenal_full_phase_main.mp4`，ffprobe 记录时长 **99.36 秒**。成片、源帧和长音频在 Google Drive，不在本 Git 树。
- 新方案在 `snapshot-20261116/football-demo/two-reference-refinement/`。`NEW_TIMELINE_BUDGET.json` 的状态是 `proposal_only_no_new_TTS_or_render`：朗读字符 **415**（不含标点），预算总长 **101.6 秒**。新版配音没有生成，新版成片没有渲染。101.6 秒是预算，不是成片时长。
- 本目录不能一键重渲。脚本里的盒上绝对路径、缺席的字体/配音模块，以及 Drive 上的大媒体，都还要另行准备。这次没有为了“能上传”去改渲染工程。

## 怎么读

1. 本文件。
2. [RECOVERY_INDEX.md](RECOVERY_INDEX.md)：路径对照、Git/Drive 分工、验证结果、离线无法确认的事项。
3. [snapshot-20261116/README.md](snapshot-20261116/README.md)：快照自身说明。包内相对路径保持 zip 里的 `archive_path`，没有改名。
4. [snapshot-20261116/CURRENT_BRANCH_INDEX.md](snapshot-20261116/CURRENT_BRANCH_INDEX.md)、[MEDIA_ON_DRIVE.md](snapshot-20261116/MEDIA_ON_DRIVE.md)、[DEPENDENCIES_AND_LICENSE.md](snapshot-20261116/DEPENDENCIES_AND_LICENSE.md)。

`snapshot-20261116/` 下 245 个文件与附件 zip 逐字节一致，`MANIFEST.json` 里 244 条 sha256 在导入后复核通过。`MANIFEST.json` 自己是第 245 个文件，不在 `files` 数组里。请不要改这些文件，否则清单哈希会失效。

## 网盘

总目录（私有）：<https://drive.google.com/drive/folders/1ESUqsHNUNQJTGpkROGVv_QLL-ub4FKbz>

本次完整源码 zip（私有，文件名 `06_当前新分支源码快照_football-tactics-source-snapshot.zip`，992079 字节）：<https://drive.google.com/file/d/1t2THxsfdPmc9Ej8RJsoCQe97YDj0F22H/view>

2026-11-16 只读取了上述两个对象的元数据：大小与附件一致，父文件夹正确，`shared` 仍为 false。没有改权限，没有把共享范围扩大，也没有把大媒体再下载进 Git。

## 仓库里有什么、没有什么

Git 收的是文本源码、可编辑 SVG、脚本、时轴、字幕、配置、小型 QC 记录、知识库，以及 4 个很短的原创近似音效（两处目录各一份，共 8 个 wav）。根目录 `.gitignore` 会忽略 `*.csv` 和 `*.wav`；这 15 个 csv 和 8 个 wav 是快照正文，已用强制纳入的方式跟踪。其余被忽略的大媒体类型没有放进来。

成片 mp4、源帧、长配音、对标原片、分离 BGM、证据大图仍以 Drive 文件 ID 为准，见快照内 `MEDIA_ON_DRIVE.md` 和 `MANIFEST.json` 的 `exclusions_summary`。
