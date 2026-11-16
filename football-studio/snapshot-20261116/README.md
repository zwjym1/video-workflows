# 足球战术制作：当前工作树源码快照（2026-11-16）

生成时间：2026-11-16 19:16:22 Asia/Shanghai

这是给后续 CloudAgent 往 GitHub 仓库 **https://github.com/zwjym1/video-workflows** 提交用的**本地源码备份包**，不是一次已经完成的 `git push`，也**不表示该仓库里已经存在对应 Git 分支**。本包制作过程没有 clone、commit、push，也没有改动制作原件。

## 状态（请勿夸大）

- **旧片已渲染完成**：`arsenal_full_phase_main.mp4`，时长 **99.36 秒**。成片、长音频和源帧在 Google Drive 归档中，不在本 Git 快照内。
- **新方案尚未配音、尚未渲染**。`two-reference-refinement/` 里是新版稿、5 板方案、分镜预算、KB 检索与视听规范，不能把预算时长当成已制成片。
- 本 zip 只含可恢复的制作代码、可编辑 SVG、脚本/时轴/字幕/配置、小型 QC 报告、知识库、逐镜与音效**文字数据**，以及体积很小的**原创近似音效** wav。

## 目录

- `football-knowledge-base/`：完整战术知识库（概念卡、来源、GitHub 资源核验、导入建议等）。
- `football-demo/full-phase-production/`：已渲 99.36s 成片的渲染源码、可编辑 SVG、脚本、时轴、字幕、配置、资产清单、小型 QC 报告与交接说明。
- `football-demo/two-reference-refinement/`：当前新方案（新版稿 / 5 板 / 分镜 / KB 检索 / 视听规范）。证据大图见网盘 `05_双对标精修_完整方案与证据.zip`，未打进本包。
- `football-demo/full-phase-new-reference/`：新对标（Foot Studio）分析文字、SFX 依据，以及小型原创近似音效。
- `football-demo/audit-20261116/` 与 `football-demo/reference-content-map/`：旧对标（RooKie《空间阅读者》）逐镜文字（不含截图；不含曼联样片对照媒体）。
- `football-demo/bgm-reference-research/`：旧对标 BGM 识别结论、目录对照与局限说明（不含分离音频与工具环境）。
- `MEDIA_ON_DRIVE.md`：大媒体的稳定 Drive 文件 ID / 链接 / sha256 指针。
- `CURRENT_BRANCH_INDEX.md`：把知识库、原片、成片、新方案串起来的阅读索引。
- `DEPENDENCIES_AND_LICENSE.md`：脚本依赖、外部素材/服务、许可边界。
- `MANIFEST.json`：逐文件原路径、包内路径、大小、sha256。

## 恢复制作还需要（本包故意没有的东西）

1. Google Drive 同文件夹中的成片、源帧、长音频、对标原片（见 `MEDIA_ON_DRIVE.md`）。合并 03/04 分卷后校验 sha256。
2. 系统工具：Python 3、ffmpeg/ffprobe、numpy、Pillow、SciPy。
3. 配音：`gen_voice.py` 历史上通过另一目录中的本地 TTS 辅助模块调用托管语音服务。该模块与**任何账号凭据都没有打进本快照**。若要重配旧稿或为新稿配音，需由操作者自行提供等价合成函数，以及仅放在环境变量/私密配置中的服务授权，**不要把密钥提交到 Git**。
4. 新方案渲染前：按新稿做真实配音、按 `SOUND_AND_VISUAL_SPEC.md` 与五板方案改板/动画，再渲染；当前仓库状态到不了成片。
5. 背景音乐仍受参考分离轨与版权限制，不是可商用正版母带。StatsBomb 等开源数据条款见知识库，禁止把数据或衍生分析当默认可商用材料。

拟提交的 GitHub 仓库由父级通过 CloudAgent 处理：https://github.com/zwjym1/video-workflows。收到本包不等于远程分支已创建。
