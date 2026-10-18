# 这些iPhone是假的？ V2 · Remotion 工程

- 合成：`IphoneFakeV2`，1920×1080 / 30fps / 2529 帧（= vo_master 84.29s）
- 画面：每镜底板 `public/plates/<镜>.webp` 由 `../preview/compose.py` 导出（无字幕、无占位注、视频窗口挖空）；
  「先信后揭」的红标单独成层 `<镜>_beat.webp`，在配音说到那个字的帧弹出（时间来自 vo/words.json）。
- 视频：`public/clips/*.mp4` 预裁好的静音片段（原声全部去掉），放在窗口位置下面。
- 字幕：`src/data/subs.json`（≤10 字/条，粗白黑描边，y≥900）。音效：`src/data/sfx.json`（assets/sfx，Mixkit）。无 BGM。
- 品牌：开场印章盖下→右上角标（60%）。无片尾卡，无「其一/其二」。

## 重新导出素材（盒子上）
    python3 scripts/export_assets.py && python3 scripts/gen_subs.py && python3 scripts/gen_sfx.py

## 检查
    npm i && npx tsc --noEmit
    node scripts/stills.mjs ../preview/remotion_stills && python3 scripts/layout_check.py

## 渲染（PC）
    set REMOTION_BROWSER_EXECUTABLE=C:\Program Files\Google\Chrome\Application\chrome.exe
    npx remotion render src/index.ts IphoneFakeV2 out\这些iPhone是假的_秘书丞_V2_1080p.mp4 --crf=18 --audio-bitrate=320k --gl=angle --concurrency=8

## V3（IphoneFakeV3，2026-10-18）
- V2 原样保留（`IphoneFakeV2` 照常可渲）；改动前备份在 `_v2_backup/`
- 数据：`/workspace/.venv-dy/bin/python scripts/v3/prep_audio.py` → `scripts/v3/build_v3.py`（生成 `public/v3/*` 和 `src/v3/data/v3.json`）→ `python3 scripts/v3/font_v3.py`（字幕/文字改了就要重跑）
- 预览：`npx remotion render src/index.ts IphoneFakeV3 ../preview/v3_preview_540p.mp4 --scale=0.5`
- 实测：`/workspace/.venv-dy/bin/python scripts/v3/measure_v3.py`；拼图：`node scripts/v3/stills_v3.mjs /tmp/st3 0.5 $(python3 scripts/v3/sheet_v3.py frames) && python3 scripts/v3/sheet_v3.py /tmp/st3 ../preview/sheets/v3_check.png`
- 音量常量在 `src/v3/theme.ts`；素材来源与许可见 `public/v3/SOURCES.md`
