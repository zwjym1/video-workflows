# ep01 幻觉 · 资产清单 · 2026-11-03（UTC+8）
规则：字幕最后单独叠最上层（OneLineSubtitles.tsx 最后一层）；动效用开源库（盒上 fx_lib = Kenney CC0 + 自制、Remotion，可加 Lottie 开源动画）；学习阶段可用他人素材（发布前再核版权）。
## 已有资产
| 类别 | 路径 | 备注 |
|---|---|---|
| 主持 O 立绘 | /workspace/handoff/AI-01/imagegen/host_distinctive_v4/gemini_out/host_o_star_sleep.png（及 contact_sheet.png） | 只有 1 张正面；`host_o_mouth_v5/out` 为空（口型未出图），`host_o_poses_v2` 只有 raw |
| 说话驱动 | /workspace/showcase/ai-video-portfolio/01-sprite-talk（sprite_talk 包）、02-host-o-pose-swap | 口型/换姿态工作流 |
| 大肥鱼立绘（用户定的原版咔哒大肥鱼） | /workspace/science-studio/hosts/host_a/sidekick_dafeiyu/original/（dafeiyu_hmph_*.png、pose_hmph.png）；参考 hosts/host_v2/aning_sit_prototype/refs/dafeiyu_hmph.png | **只有“哼/叉腰”一种姿态**。Look A/B/C 那套已被用户否决，勿用 |
| 动效 | /workspace/science-studio/assets/fx_lib/clips/*.webm（38 个：sparkle_burst、impact_star、marker_highlight、cross_draw、check_draw、pop_question、dust_poof、smoke_puff、sweat_drop、speed_lines、confetti、click_ripple…）+ fxkit.py 7 种转场 | catalog.md |
| 音效 | /workspace/science-studio/assets/audio_lib/sfx/（impact_punch、pop_ui、whoosh_trans、ding_success、comedy_fail、tech_digital） | 均可商用 |
| BGM | audio_lib/bgm/happy_arcade_tune.mp3（117 BPM，主选，CC-BY 需署名） | 符合 112–118 BPM |
| 字幕组件 | /workspace/science-studio/lib/remotion/OneLineSubtitles.tsx | 最上层 |
| 新闻截图 | ../assets/news/（见 SOURCES.md） | |

## 缺口（需新做）
- **O 姿态**：冷脸“没用。”、摇头、抬手“等等”、拿手机、点头“这次算你的” → 5 张 + 口型 viseme（mouth_v5 未出）。
- **大肥鱼姿态**（只有 hmph）：扑入举攻略卷轴(2)、戴墨镜拍桌(8)、抱头(10)、探头摊手(12)、嘴里飞字卡(19)、学士帽/摘帽发呆(27/28)、举手机(30)、指自己(31)、叉腰得意(34，可用 hmph)、从标尺滑落(38)、挥支票(39/40)、打字认真(45)、举“不知道”牌(46)、抱道具探头(49) → 约 13 张 + 说话口型。走 gpt-imagegen-handoff。
- **道具/插画**：攻略卷轴、中国地图红点、步行计时器、施工围挡站牌、登机牌翻面、术语卡×3、问号槽 ①②、章节 tab ①–④、书架✗/接龙卡✓、逐字生成+概率条（代码动画）、脑袋剖面+空相框、拼图、剪贴拼景点、网红店招牌、空水库、考卷、日历转盘、0 分章、计分板、ABCD 涂卡、新计分规则卡、手机、裂屏、地图标尺、¥100,000 支票+“无效”章、法槌、判决卡、⚠️提示框、接龙文字链、计数器「翻车 N｜技能 N」、片尾系列卡、手机/地图 App 框（48）。大部分可 Remotion 代码画，插画类（地图、店招、水库、法槌）需出图或开源图标（如 Twemoji/OpenMoji CC-BY）。
- **音效缺**：计时器滚动、施工“哐”、翻牌、剪刀、塞拼图咯吱、纸张落下、转盘 tick、盖章、涂卡沙沙、橡皮擦、电击、钱币、法槌咚、打字连续音 → 可从 audio_lib/_raw（100-CC0-SFX、80-CC0-RPG、Digital/UI 套装）挑，或 freesound CC0。
- 央视视频动态画面（镜 1 可选）未下载。

## 逐镜对照（立绘 / 动效 / 音效）
| 镜 | 立绘 | 动效 | 音效 | 状态 |
|---|---|---|---|---|
| 1 | — | 截图推拉、大字卡砸下、impact_star | impact_punch/slam_a、pop_switch_hard | 截图有，字卡待做 |
| 2 | 鱼扑入举卷轴 | sparkle_burst、twinkle | pop_plop、sparkle_synth | 缺鱼姿态、卷轴 |
| 3 | O 冷脸 | pop_question×N、计数器 | BGM 空拍、pop_click | 缺 O 姿态、计数器 |
| 4 | — | 地图红点 | pop_ui | 缺地图 |
| 5 | — | 计时器滚动 | 滚动音(缺)、slam_a | 缺 |
| 6 | — | 围挡落下 | 施工哐(缺) | 缺 |
| 7 | — | 登机牌翻面 | 翻牌(缺) | 缺 |
| 8 | 鱼墨镜拍桌 | pop_exclaim | pop_ui×2 | 缺鱼 |
| 9 | — | 术语卡、marker_highlight、缩放冲击 | thunk_synth | 代码 |
| 10 | 鱼抱头 | sweat_drop | — | 缺鱼 |
| 11 | O 摇头 | 槽位①②、tab 滑入 | ding_bell | 缺 O |
| 12 | 鱼摊手 | tab | whoosh_synth、pop_plop | 缺鱼 |
| 13 | — | cross_draw/check_draw、缩放 | impact | 代码 |
| 14 | — | 逐字生成+概率条 | 打字 tick(tech_digital/beep) | 代码 |
| 15 | 鱼剖面 | 文字云 | 空洞咚(thunk) | 缺插画 |
| 16–17 | 鱼塞拼图(17) | 拼图 | pop_ui、咯吱(缺) | 缺 |
| 18 | — | 剪贴拼 | 剪刀(缺) | 缺 |
| 19 | 鱼吐字卡 | 字卡飞入拼招牌 | ding_coin×3、powerup | 缺鱼、招牌 |
| 20 | — | dust_poof、截图角标 | puff_synth | 缺水库图 |
| 21–22 | 鱼叉腰(hmph ✓) | 考卷落下 | whoosh、纸落(paper_swipe) | 考卷缺 |
| 23 | — | 截图角标、转盘 | tick→ding | 转盘代码 |
| 24 | — | 0 分章、缩放 | 盖章(缺)/slam_a | 代码 |
| 25–26 | — | 计分板、涂卡 | pop_ui、沙沙(缺) | 代码 |
| 27–28 | 鱼学士帽/摘帽 | pop_question | ding_success | 缺鱼 |
| 29 | 鱼擦答案 | 规则卡×3 | pop_ui×3、橡皮(缺) | 缺鱼 |
| 30–31 | 鱼举手机/指自己 | tab | paper_swipe、whoosh | 缺鱼 |
| 32–33 | — | 录屏窗口框、marker_highlight | 打字(typewriter)、ding | 待录 R6/R7 |
| 34 | 鱼叉腰(hmph ✓) | — | — | 有 |
| 35–36 | O 抬手 | 裂屏、zap | whoosh、zap | 缺 O |
| 37 | — | 地图标尺、缩放 | 拉伸(phaser_up) | 待录 R9 |
| 38 | 鱼滑落 | 计数器 | boing_spring | 缺鱼 |
| 39–41 | 鱼挥支票 | 支票、“无效”章 | ding_coin、盖章 | 缺鱼、支票 |
| 42–43 | — | 法槌、三格、判决卡、截图角标 | pop_ui×3、法槌(gong/thunk) | 缺法槌 |
| 44 | O 拿手机 | 支票飘走 | — | 缺 O |
| 45 | 鱼打字 | ⚠️框打字 | typewriter→ding_success | 缺鱼 |
| 46 | 鱼举“不知道”牌 + O 点头 | 文字链、spotlight | ding_bell，BGM +3 dB | 缺 |
| 47 | — | 计数卡、confetti | ding | 代码 |
| 48 | — | 手机框录屏、✓/✗ | ding / fall_lowdown | 待录 R11 |
| 49 | 鱼抱道具探头 | 预告卡、评论条 | whoosh | 缺鱼 |
| 50 | — | 片尾系列卡 | BGM 淡出 | 代码 |
