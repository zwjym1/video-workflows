# RoadsterShortV3 — 音效 / 配乐清单

全部音效和配乐都是本地用代码合成的原创素材（numpy / ffmpeg 生成）。没有用任何第三方采样，可免版税使用。

| 文件 | 用途 | 生成方式 |
|---|---|---|
| public/v3/bgm_A.wav | 前段配乐：Am-F-C-G，112 BPM，pad + 琶音 + 轻鼓 | scripts/make_bgm_v3.py |
| public/v3/bgm_B.wav | 从「那真正把它送上天的」起：完整鼓组 + 贝斯 | scripts/make_bgm_v3.py |
| public/v3/sting.wav | 秘书丞频道卡提示音 | scripts/make_bgm_v3.py |
| sfx/boom.wav ×2 | 开场 + 起飞「飞」 | 沿用 v2，自制 |
| sfx/whoosh.wav ×6 | 只用在真正的转场：飞行镜头切入、评论区、拆解报道、Q 切飞行、总结 | 自制 |
| sfx/ding.wav ×3 | 只给 2 倍 / 2028 / 25 万美元 | 自制 |
| click ×4, shutter ×2, fanhum, jet, hiss, puff ×3 | 评论卡、两次定格、风扇/喷气拟音 | 自制 |

混音（scripts/mix_v3.py）：
- A→B 两段配乐在「那真正」处交叉淡化
- 配乐用 sidechaincompress 以人声为触发做闪避，人声始终压过配乐
- 最后做 loudnorm，目标 I=-16 LUFS、TP=-1.5

## 素材来源
- 画面：Tesla 发布会 / 官方片
- 新闻截图：TechCrunch、Engadget
- 评论（原文引用）：
  - 抖音 @JiangJiang，douyin.com/video/7697078448158649082
  - B 站 BV1zcJS6sEXT
  - B 站 BV1j9JQ6oEeE
