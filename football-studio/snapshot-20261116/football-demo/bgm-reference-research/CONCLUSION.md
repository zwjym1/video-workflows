# BGM 结论（空间阅读者）

工具：[douyin-bgm-extract](https://github.com/zwjym1/douyin-bgm-extract)（文档 [SKILL.md](https://github.com/zwjym1/douyin-bgm-extract/blob/main/SKILL.md)）。按本地音轨入口处理，未再下载同视频；未克隆仓库。识别来自 Shazam 多段交叉，不是听感。

## 识别到两首不同的歌

1. **主床（约 0–146 秒）**：《人生志在一博》/ 李富贵，专辑《超速进行曲 - EP》，ISRC `QZNMZ2630446`，官方时长 112.953 秒。15 段以上窗口及官方 30 秒预览均指向同一 Shazam 曲目。片中从官方开头对齐，约 111.83 秒处循环一次（比目录时长短约 1.12 秒，需拿到完整正版后再校）。
2. **结尾（约 147–171 秒）**：《passion》原速 / silent anthem & heart embrace，ISRC `DGA0P2461646`，官方时长 132.466 秒。不要用 Speed Up / Slowed。Shazam 偏移粗略对应官方约 0:14–0:38，未与 30 秒预览波形对齐，入口点需用完整正版复核。

76–82 秒的 NO MATCH 夹在同一主曲命中之间，不当成换歌。

## 可用文件

- 混音提取（有解说，不能当原版无损）：`tracks/Rookie_空间阅读者_source.m4a`（HE-AACv2 ~60.7 kbps，171.038 秒）
- 官方 30 秒预览（不是完整可混成片）：`official_previews/人生志在一博_李富贵_itunes_preview.m4a`、`official_previews/passion_silent-anthem_heart-embrace_itunes_preview.m4a`（AAC ~260 kbps，各 30 秒）
- **完整正版母带：未取得。** 不要用合成垫乐冒充。

## 正版取得方式（未购买、未登录绕过）

- Apple Music：《人生志在一博》https://music.apple.com/us/album/人生志在一博/6822056782?i=6822056789 ；《passion》https://music.apple.com/us/album/passion/1773323113?i=1773323114
- 网易云：https://music.163.com/song?id=3447281999 、https://music.163.com/song?id=2635437250（主曲 fee=8，非免费下载）
- 发行页：https://unitedmasters.com/m/chao-su-jin-xing-qu
- 技能首选：剪映音乐库搜「人生志在一博」「passion silent anthem」（本轮未打开剪映，是否在库未核）

详细命中表与 cue 见 `evidence.json`。
