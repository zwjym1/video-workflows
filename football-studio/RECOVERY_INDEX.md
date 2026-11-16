# 恢复索引（2026-11-16 足球战术源码快照）

导入位置：`football-studio/snapshot-20261116/`  
来源附件：`football-tactics-source-snapshot.zip`，992079 字节，SHA256 `0f95245a217143aa7424c5b5a197bb917d087ed0945978561282cf4fa95851ba`。  
Drive 上的同一份 zip：文件 ID `1t2THxsfdPmc9Ej8RJsoCQe97YDj0F22H`，父文件夹 `1ESUqsHNUNQJTGpkROGVv_QLL-ub4FKbz`。元数据大小为 992079 字节。远程字节的 SHA256 没有在本次重新下载计算。

快照生成于 2026-11-16 19:16:22 Asia/Shanghai。它记录的是制作机上的工作树，不是当时已经存在的 Git 分支。

## 状态

| 对象 | 事实 |
| --- | --- |
| 旧方案成片 | 已渲染。`qc/arsenal_full_phase_main_ffprobe.json` 的 `format.duration` 为 99.360000 秒。mp4 本身在 Drive，不在 Git。 |
| 新方案 | `two-reference-refinement/VALIDATION.json` 状态为 `proposal_only_no_new_render_TTS_or_global_changes`。415 是不含标点的朗读字符；`NEW_VOICEOVER.txt` 汉字数为 415，文件总字符数是 483。101.6 秒来自 `NEW_TIMELINE_BUDGET.json` 的 `estimated_total_s`。 |
| 新版配音 / 新版成片 | 没有生成，没有渲染。 |
| 旧片可编辑板 | `full-phase-production/assets/B1_STAGED.svg` 至 `B6_STAGED.svg`，共 6 张，属于已渲旧片工程。 |
| 新方案问题板 | 文档中的 5 张问题板，见分镜预算与 `BOARD_RELATION_EXECUTION_MAP.json`。没有新的成片画面。 |

## 路径对照

包内相对路径等于 `MANIFEST.json` 的 `archive_path`。放到本仓库后，前面多一层：

`football-studio/snapshot-20261116/` + `archive_path`

`original_path` 全部写成制作机上的 `/workspace/football-demo/...` 或 `/workspace/football-knowledge-base/...`。那些路径是档案记录。在本仓库、另一台机器或另一个目录里，不能直接拿来打开文件。

| 快照内路径 | 内容 |
| --- | --- |
| `football-knowledge-base/` | 36 张概念卡（`concepts.jsonl`，ID 唯一）、20 条来源（`source_registry.jsonl` 与 `sources/notes/` 的 C01–C04、F01–F13、U01–U03 一一对应）、8 个已核验 GitHub 项目 |
| `football-demo/full-phase-production/` | 已渲 99.36 秒成片的脚本、6 张 SVG、时轴、字幕、配置、小型 QC JSON、交接说明 |
| `football-demo/two-reference-refinement/` | 新版 415 字稿、五板关系、分镜预算、KB 检索与声画规范 |
| `football-demo/full-phase-new-reference/` | 新对标的文字分析、逐镜音效文字、4 个短原创近似音效 |
| `football-demo/audit-20261116/`、`reference-content-map/` | 旧对标逐镜文字。截图不在本包 |
| `football-demo/bgm-reference-research/` | BGM 识别结论和目录对照。分离音频和工具环境不在本包 |
| `README.md`、`CURRENT_BRANCH_INDEX.md`、`MEDIA_ON_DRIVE.md`、`DEPENDENCIES_AND_LICENSE.md`、`MANIFEST.json` | 快照自带说明与清单 |

知识库资源文件 `resources/github_resources.json` 的 `projects` 有 8 条：`hudl/open-data`、`metrica-sports/sample-data`、`ML-KULeuven/socceraction`、`PySport/kloppy`、`andrewRowlinson/mplsoccer`、`Friends-of-Tracking-Data-FoTD/LaurieOnTracking`、`Friends-of-Tracking-Data-FoTD/SoccermaticsForPython`、`SoccerNet/SoccerNet`。同文件另有 5 条标成未选用或仅作指针，不算这 8 个已核验项目。

卡片的 `source_refs` 都能对上来源 ID。`sources/card_source_crosswalk.csv` 覆盖 36 张卡和 20 个来源。该 CSV 带 UTF-8 BOM，严格解析时第一列表头会是 `\ufeffcard`。文件按原字节保留，没有为了表头去改清单哈希。

## Git 与 Drive 的分工

Git 负责可 diff 的源码和文档，以及下面 4 个短音效的两份副本（新对标目录与旧片 `audio/sfx_original/`，SHA256 两两相同）：

- `cut_hit_low_muted.wav`（0.200 秒）
- `ui_tick_soft.wav`（0.160 秒）
- `whoosh_line_short.wav`（0.280 秒）
- `circle_lock_soft.wav`（0.200 秒）

这 8 个 wav 都是 16-bit PCM、44100 Hz、双声道，单文件 28–49 KB。它们是项目原创近似音效。对标原声、分离 BGM 和长混音不在其中。

Drive 总目录负责大媒体和完整工程包。稳定入口仍是快照内 `MEDIA_ON_DRIVE.md`：

- 文件夹：<https://drive.google.com/drive/folders/1ESUqsHNUNQJTGpkROGVv_QLL-ub4FKbz>
- 99.36 秒成片：文件 ID `1KCp9qu0lL_n6golZMOgn0lJRfOSr2yz1`
- 知识库媒体 zip：文件 ID `1FZKelr76kFXfOFFt6rQ2-CxtWqXuMlwP`
- 制作工程与对标资料是 90 MiB 分卷，合并后按该文件中的 SHA256 校验
- 本次源码 zip：文件 ID `1t2THxsfdPmc9Ej8RJsoCQe97YDj0F22H`

`MANIFEST.json` 的 `exclusions_summary` 写明了留在网盘的源帧、证据图、对标原片、参考原声、逐镜大图和 BGM 分轨。那些文件没有补进本次提交。

## 盒上绝对路径

脚本和 JSON 里保留着制作机路径，换机器不能直接跑。出现过的根包括：

- `/workspace/football-demo/`
- `/workspace/football-knowledge-base`
- `/workspace/football-demo/manutd-tactics/`（另一主题工程；字体 `src/fonts/NotoSansSC-700.ttf` 和 `gen_voice.py` 要找的 TTS 辅助模块都在这里，本快照故意没带）
- `/workspace/douyin-download-parser/`（对标片下载目录，未导入）
- `/home/box/.cache/huggingface/hub/models--Systran--faster-whisper-small/...`（本机 ASR 缓存）

`gen_voice.py` 会去 `football-demo/manutd-tactics/src` 找语音合成辅助模块。该模块和任何账号凭据都不在本快照里。重配旧稿或给新稿配音时，由操作者自己提供等价函数，密钥只放环境变量或私密配置。

## 依赖、来源和许可

制作脚本常见依赖是本机自行安装的 Python 3、numpy、Pillow、SciPy，以及外部程序 ffmpeg/ffprobe。快照不带 site-packages，也不带这些程序。

对标原片、逐镜截图和参考分离 BGM 是私有学习存档，不是本项目可以再发布的母版。StatsBomb 等数据条款以知识库原文为准：代码许可证不覆盖数据、教材或比赛视频。本次没有导入原始比赛视频，也没有导入受限数据集。

公开仓库笔记里保留了资源 README 自带的维护者联系邮箱。扫描没有发现密钥、cookie、`.env`、私钥或凭据文件名。数字串里看似手机号的片段来自 SHA256 十六进制和曲库 `mark` 字段。

## 本次轻量验证

验证只检查档案能不能读、清单是否自洽。没有运行渲染、配音、下载或第三方素材获取。

- 附件大小 992079，SHA256 与用户给出的值一致；zip 列表 245 个文件。
- 导入副本与 `MANIFEST.json` 的 244 条记录在字节数和 SHA256 上全部一致；没有缺文件，没有多出的快照文件。`file_count: 245` 含清单本身。清单里的 `zip.bytes` / `zip.sha256` 仍是生成时留下的 `null`。
- JSON 130 个、JSONL 3 个（36 卡、20 来源、2484 条帧映射）、CSV 15 个、Python 24 个（`ast.parse`）、SVG 6 个、SRT 1 个（55 条字幕）语法检查通过。CSV 列数整齐。
- 8 个 wav 可由标准库 `wave` 打开。
- 知识库卡片、来源笔记、交叉表和 8 个 GitHub 项目记录数量一致；卡片来源引用没有悬空 ID。
- Drive 只读了文件夹和源码 zip 的元数据：名称、大小、父级匹配，且 `shared` 为 false。没有修改共享。

## 离线不能确认的事项

- Drive 上成片、分卷工程、对标原片和证据图的字节是否仍与 `MEDIA_ON_DRIVE.md` 里的 SHA256 一致。本次没有下载它们。源码 zip 也只核对了元数据大小，没有重新下载后计算远程 SHA256。
- 99.36 秒来自已保存的 ffprobe JSON，不是这次对 mp4 重新探测。
- 101.6 秒没有成片可以探测。
- numpy、Pillow、SciPy、ffmpeg、Noto 字体、TTS 模块、Fish 或等价语音服务、HuggingFace ASR 缓存都没有在本环境安装或调用。
- 曲库识别 JSON 没有重新请求 Deezer、iTunes、MusicBrainz 或网易接口。
- 对标网页和公开数据仓库是否仍然可访问，没有复检。
- 制作机上的 `/workspace` 与 `/home/box` 路径现在是否还存在，没有登录那台机器。

## 这次没有做的事

没有改根目录说明、`.gitignore`、旧技能、旧工作流、旧示例工程和 `science-studio`。没有合并主分支，没有强推，没有删除既有文件。没有启动制作、购买、生成配音、联网下载第三方素材，也没有把新规则装进旧系统。
