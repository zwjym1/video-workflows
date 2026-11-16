# 依赖、来源与许可（恢复制作时必读）

## 已包含、可在本包内阅读或运行（在有媒体的前提下）

制作脚本主要在 `football-demo/full-phase-production/`：

- `build_script.py`、`build_assets.py`、`assemble_timing.py`、`gen_voice.py`
- `render/render_film.py`、`render/mix_final.py`、`render/quality_check.py`、`render/finalize_delivery.py`

常见第三方库（需本地/CI 自行安装，本包不附带 site-packages）：`numpy`、`Pillow`、`scipy`。外部程序：`ffmpeg`、`ffprobe`。

知识库构建脚本：`football-knowledge-base/build_kb_v1.py`、`finish_local_kb.py`。

## 未包含、但脚本会引用

- `gen_voice.py` 会向历史路径 `football-demo/manutd-tactics/src` 查找 TTS 辅助模块。该路径属于其他主题工程，**没有**打进本快照，避免把其他项目与可能的服务配置带进 Git。重配音不要复制凭据进仓库。
- `render/source/` 下的逐帧源图、QC `encoded/` 大图、成片 mp4、长 wav/mp3：见 `MEDIA_ON_DRIVE.md`。
- 对标原片与分离音轨：仅私有学习，不是本项目版权资产。

## 许可与使用边界

- 两份对标原片、逐镜截图、参考分离 BGM：**私有学习存档**，不得当作可对外发布的原创素材或正版母带。
- 包内 `audio/sfx_original/` 与 new-reference 对应目录中的短 wav 是项目**原创近似音效**，可随源码保存；不要与参考原声切片混淆。
- 知识库中的 GitHub/数据条款（尤其 StatsBomb 公开数据用户协议）仍然有效：代码许可证不等于数据或教材可自由商用。
- 不要提交 `.env`、cookie、token 或账单。

## 新方案尚未发生的服务调用

新版稿未走配音服务，也未渲染。不要把 `NEW_TIMELINE_BUDGET.json` 的预算秒数写成已交付成片。
