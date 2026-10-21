---
name: douyin-field-collect
description: 需要免登录采集抖音同题视频的实地数据（详情、平台字幕或本地转写、评论与回复、按来源区分的推荐搜索词、开头截帧）并输出带字段状态的 JSON/MD 时使用。
---
# 抖音实地数据采集（免登录）

> 盒上现成副本：`/workspace/skill_pkg/douyin-field-collect/`（先 `cd /workspace/skill_pkg/douyin-field-collect/scripts`；Python 用 `/workspace/.venv-dy/bin/python`，缺依赖再按 requirements.txt 装）。采集全是本地脚本，不调用任何大模型。

## 思路

1. **找同题视频**：`dy_search.py` 关键词搜索。so.douyin.com 主力（无头浏览器像手机一样正常浏览，只读页面自己发出的请求），神马（m.sm.cn）、360 补充。去重后按点赞排序。换 5–10 个说法分别搜，挑角度不重复的 8–10 条。
2. **取详情和字幕**：`dy_collect.py video` 先调 so.douyin.com `aweme/detail`。字幕优先用抖音自带的，字段顺序：
   `interaction_stickers[].auto_video_caption_info.auto_captions[].url` → `video.cla_info.caption_infos[].url` → `video.subtitle_infos` / `subtitle_infos`。
   取到标 `source=platform_caption`（原文）；取不到且加了 `--media --asr` 才走本地 faster-whisper，标 `source=local_asr, needs_review=true`。
3. **评论分页**：`comment/list` 拿一级评论，`comment/list/reply` 展开高赞评论的回复。记录已采唯一数、平台 total、has_more、stop_reason（no_more / limit_reached / empty_page / cursor_stuck / blocked / api_error）。
4. **推荐词按来源分开，不混写**：

   | 键 | 来源 | 含义 |
   |---|---|---|
   | `comment_top_rec` | 详情 suggest_words 中 scene=comment_top_rec | 评论区顶部「大家都在搜」 |
   | `detail_suggest_words` | 详情 suggest_words 其余 scene（feed_bottom_rec=视频下方「相关搜索」等） | 按 scene 分开 |
   | `page_suggest_words` | `--browse` 页面自己请求的 suggest_words | 看后搜/页面级；可能混入别的视频的词 |
   | `related_videos` | `--browse` 页面请求的 `/aweme/related/` | 相关推荐视频 |
   | `search_sug` | `--kw`：www.douyin.com search/sug | 搜索框联想 |
   | `search_page_related` | `--kw --search-rel`：so.douyin.com 结果页 | 「大家还在搜」 |
5. **截帧和转写**：`--media` 下载顺序 iesdouyin 分享页 → dlpanda → snapany → yt-dlp，403 就换下一个。截开头 0–5 秒（每 0.5 秒一帧，`hook_sheet.jpg`）和全片 16 帧（`contact_sheet.jpg`），视频默认用完删除。
6. **输出**：每条视频 `<out>/douyin_<id>/`，含 `collect.json`（全部字段及状态）、`comments.json`、`report.md`、截帧拼图。

### 字段状态
`available` 完整 · `partial` 部分（到上限或中途被拦） · `observed_empty` 请求成功但平台返回空 · `missing` 没有该字段或页面没发出请求 · `blocked_login` 登录墙 · `blocked_verification` 验证码/403/429 · `error` 程序或网络错误 · `not_requested` 未开启。
写结论时把「没取到」和「平台真的没有」分开说。

## 命令

```bash
pip install -r requirements.txt && python -m playwright install chromium   # 一次性
cd scripts
python dy_search.py "XX怎么做" -n 20 --src so,sm --json search.json
python dy_search.py "XX实测" --urls --days 30 > urls.txt
python dy_collect.py video <链接或ID> -o ./out -n 200            # 只调接口，最省
python dy_collect.py video <链接或ID> -o ./out -n 200 --replies --reply-n 20 \
    --kw "同题关键词" --search-rel --browse --media --asr --asr-model small
python dy_collect.py sug "关键词" --rel
```
批量：`while read u; do python dy_collect.py video "$u" -o ./out; done < urls.txt`，每条之间留间隔。

## 限制
- 全程免登录：不带账号 cookie、不做签名逆向、不换身份重试；遇验证码或 403/429 如实记录并停该项。
- www.douyin.com 搜索页有登录墙，只用 so.douyin.com/神马/360，偶尔漏最新视频。
- 很多视频没有平台字幕（`is_subtitled=0`），只能本地转写，必须复核；歌曲/强 BGM 时 VAD 可能判无人声，脚本会关掉 VAD 再跑一次。
- AI 生成标识或禁止下载的作品官方下载会被拒，靠解析站换源；全失败则 `media.status=error`，`tried` 里逐源列原因。
- 游客态 `/aweme/related/` 常不发出（missing）；页面级 suggest_words 看 `attribution` 字段判断归属。
- 同一 IP 短时间大量请求易触发验证，默认每页间隔约 0.8 秒，批量再拉长。
