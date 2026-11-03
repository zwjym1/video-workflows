# AI 扫盲（AI101）短视频制作工作流

示例集：`episodes/ai101_ep01_hallucination/`（AI 幻觉）。仓库只收代码/配置/文档，不含视频、音频、图片、生成素材与密钥。

1. **三版脚本**：`script_tzs*.md`（v1→v2→v3）、`script_gpt.md`/`script_gemini.md` 对照；事实核查在 `facts.md`；v3 定稿在 `script_v3/`（`netgan_list.md` 网感清单、`shots_v3.json` 分镜）。
2. **逐镜审核表**：`tools/review_table.py` + `tools/review/`（规则 `config/rules_v2.md`、`lib/rules_v2.py`、`lib/measure_v2.py`，入口 `review.py`）逐镜打分修改。
3. **逐句 Fish 配音**：两角色 reference_id —— O = `ebea2d0931f54cd69ec7d5e88db6b084`，鱼 = `9510b59280f74ad197f10b61eaa5abba`。每句单独合成，过**音高门**，并核对每句 reference_id 与角色一致；“+1” 读作“加一”。Fish API key 走环境变量，不入库。
4. **口型/字幕对齐**：`production/sync_check.py` 检查口型、字幕与音频时间轴一致。
5. **渲染**：`script_v3/cues_full.py` 生成 cue，`build_full.py` 合成。卡拍只用于切镜/弹出/字卡/音效/姿势；人物晃动跟说话走（不跟 BGM 拍）。
6. **字幕最后叠顶层**：所有画面层完成后再烧字幕，避免被遮挡。
7. **成片检查**：`tools/qc/final_check.py` —— 横屏、响度 -14 LUFS 等。
8. **审片官打分**：通过 review 规则打分，不达标回到对应步骤。

录制/素材计划：`production/recording_plan.md`、`production/asset_plan.md`。节奏/语气分析：`knowledge/aning_rhythm_tone.md` 等。
