# 发布前审片系统（原型）

职责：只回答「这条能不能发、发之前改什么」。选题、对标、热点归 **知赏**；审片不改选题，只在返修单里提示风险。

## 一条片子怎么审（运行说明）

**重计算在 PC，PC 不在线时回退到盒上；qoder-flash 看片永远在盒上跑。**

1. 抽帧（重活）——优先 PC（机器 `0376e70a-…`，PowerShell 7）：
   - 在 `C:\Users\Administrator\Downloads\` 下 **新建** 目录（如 `review_tmp_YYYYMMDD\`），把 `pc/pc_frames.ps1` 和 `jobs.csv`（`id,成片绝对路径`，UTF-8 无表头）放进去；
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File pc_frames.ps1 -List jobs.csv -Out <新目录>\frames`（只读原片，不改任何已有文件、不碰仓库）；
   - CopyToBox 取回 `frames.zip` → 解压到 `pc/frames/<id>/`。
   - 实测：PC 约 3.3 秒/条（9 条并行），盒上 ffmpeg 约 18 秒/条。
   - **PC 不在线 / CopyToBox 失败**：跳过本步，`review.py` 不传 `--frames-dir`，`sheets.py` 自动用盒上 ffmpeg（`sheets.json` 里 `frames_source` 记录用了哪条路）。
2. 盒上一键：
   ```bash
   cd /workspace/science-studio/tools/review
   ./review.py --id EP-20261028-02 --video 成片.mp4 --srt 字幕.srt \
     --facts ../../projects/EP-…/research/facts.md --cover 封面.png --publish 发布文案.md \
     --beats storyboard/beat_map.json --ai --frames-dir pc/frames/EP-20261028-02 --runs 2
   ```
   产物：`out/<id>/objective.json`、`sheets/hook_3s.jpg`、`sheets/contact.jpg`、`subjective_r1/r2.json`、`verdict.json`、`返修单.md`、`timing.json`。
3. 发布前：`./ledger.py predict <id>` 记下预测。发布后用户发后台截图 → 看图读数 → `./ledger.py actual <id> --hours 24 --bounce2s 25.1 --stay5s .. --completion .. --shares .. --shot 截图路径`。
4. 每新增 ≥5 条真实数据：`./calibrate.py` → 看 `out/calibration.md`，按规则改 `config/rubric.json` 并把 `version` 加一。

## 分模块
| 脚本 | 做什么 | 在哪跑 |
|---|---|---|
| `lib/asr.py` | VAD 分段 + faster-whisper small 离线转写；有 SRT 时直接用 SRT（优先） | 盒（PC 有 GPU 时可迁移） |
| `lib/objective.py` | 13 项客观检测（首帧、前 3 秒、切点、字幕、安全区、响度、卡点、BGM、口播密度/术语/信息间隔、结尾、事实、合规、封面） | 盒（OCR 最耗时，30–90 秒/条） |
| `lib/sheets.py` | 两张给评审团看的拼图 | PC 抽帧 / 盒回退 |
| `lib/subjective.py` + `prompts/persona_review.md` | qoder-flash 5 人设盲审，结构化 JSON | **只在盒上** |
| `lib/merge.py` + `config/rubric.json` | 打分、否决、偏好过滤、返修单 | 盒 |
| `calibrate.py` | Spearman + 留一法 | 盒 |
| `ledger.py` | 预测/真实台账 | 盒 |

## 时间与成本（2–3 条/天）
- 每条：抽帧 PC 3 秒（盒 18 秒）+ 客观层 0.5–1.5 分钟 + qoder 2 轮各 1.5–4.5 分钟（可并行）≈ **6–10 分钟/条**，全在后台跑。
- qoder-flash 走用户国内版 Qoder 免费模型（DeepSeek-Flash，max 推理）；`--list-models` 目前不显示积分列，**免费状态需每周人工在 Qoder 里确认一次**。其余全部本地、零费用。
- 不登录任何平台、不发布；真实数据只来自用户截图。

## v2（2026-10-28）新增：剪辑质量 / BGM 契合 / 分段精审 / 假阳性校验（向后兼容）
- 旧命令照跑：`review.py` 参数不变，只是默认多跑两步（cutquality、bgmfit），任一失败只打印 `!!` 不中断；`merge.py --legacy` 出与 v1 完全相同的总分。
- **重计算在 PC，PC 不在线时回退到盒上**：
  1. 盒上写 `jobs.csv`（id,path，path 用 PC 上原片路径）→ `CopyFromBox` 把 `pc/pc_proxy.ps1`+jobs.csv 放到 PC 的 `Downloads\review_proxytool_<日期>\`（新目录，不碰原片/仓库）
  2. PC 上 `pwsh -NoProfile -ExecutionPolicy Bypass -File pc_proxy.ps1 -List jobs.csv -Out %USERPROFILE%\Downloads\review_proxy_<日期>`（目录已存在就拒绝运行）→ 出 `<id>\proxy.mp4(180×320/30fps)`、`audio.flac`、zip
  3. `CopyToBox` 拿回 zip → 解压到 `pc/proxy/` → `review.py ... --proxy-dir pc/proxy/<id>`
  4. PC 不在线：不传 `--proxy-dir`，cutquality/bgmfit 自动用盒上 ffmpeg 解原片。qoder-flash 永远在盒上。
- 单独跑：
  - `lib/cutquality.py --video X --out out/<id>/cutquality.json --asr A --objective O [--proxy P] [--design-cuts ShotsV2.tsx --style-truth ShotsV2.tsx]`
  - `/workspace/.venv-dy/bin/python lib/bgmfit.py --video X --out out/<id>/bgmfit.json --asr A --objective O [--audio P.flac] [--bgm-stem 纯BGM.wav]`
  - `lib/focus_run.py --id <id> --video X --asr A [--from 3 --to 末尾 --seg 12] [--design-cuts ..] [--cutq out/<id>/cutquality_design.json] --timeout 300 --retries 3 --parallel 2`
    （按切点分段、每段独立缓存、超时杀进程组、指数退避、最后一次换 qoder-flash-qwen；`--dry` 只出拼图不调模型；`--force` 忽略缓存）
  - `lib/focus_validate.py --focus out/<id>/focus_run/focus_run.json --cutq .. --objective .. --asr .. --out out/<id>/focus_validated.json`（focus_run 结束会自动调）
  - `lib/merge.py --id <id> [--legacy]`；`calibrate_v2.py`（旧 calibrate.py 不动）
- 批量重算语料：`run_edit_bgm_corpus.py [--proxy-dir pc/proxy] [--ids a,b] [--only cut|bgm]`
- 总分 v2 = 0.40 钩子 + 0.25 主体 + 0.20 剪辑质量 + 0.15 收获；剪辑质量 = 0.7×cutquality + 0.3×精审分（无精审时用主观画面分）+ 假阳性返还；放行多一条：剪辑质量 ≥ 55。
