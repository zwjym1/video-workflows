# IphoneFakeV3 素材来源与许可（public/v3）

## BGM
- `audio/bgm_281.wav`：**Complicated — Arulo**（Mixkit 免费音乐 #281，Hip Hop / Trap，约 107.7 BPM，原长 1:49）
  - 下载：https://assets.mixkit.co/music/281/281.mp3 （与 `vo/bgm/cand_v3/mk_281.mp3` 的 MD5 一致）
  - 许可：Mixkit Stock Music Free License（https://mixkit.co/license/#musicFree）。可用于网络视频、社交平台，不要求署名；条款不允许用于 CD/DVD、电子游戏、电视或电台广播。
  - 处理：从原曲 23.84s（强拍）起截取 73.5s，用线性增益调到 −22 LUFS（未闪避时），无压缩。口播时由 Remotion 闪避 −9 dB（见 `src/v3/theme.ts`）。

## 音效（`sfx/*.wav`，由 `assets/sfx_v3/raw` 裁短、去头部静音、统一峰值）
| 文件 | 源文件 | Mixkit ID / 原名 |
|---|---|---|
| whoosh_c.wav | whoosh_c.mp3 | 166 Fast small sweep transition |
| whoosh_d.wav | whoosh_d.mp3 | 175 Short transition sweep |
| whoosh_e.wav | whoosh_e.mp3 | 3115 Fast transitions swoosh |
| whoosh_f.wav | whoosh_f.mp3 | 3120 Technology transition slide |
| pop_a.wav | pop_a.mp3 | 3005 Explainer video pops whoosh light pop |
| pop_b.wav | pop_b.mp3 | 2364 Hard pop click |
| pop_c.wav | pop_c.mp3 | 2356 Dry pop up notification alert |
| click_b.wav | click_b.mp3 | 2568 Cool interface click tone |
| click_c.wav | click_c.mp3 | 1120 Modern click box check |
| hit_d.wav | hit_d.mp3 | 2180 Exciting fast hit |
| hit_c.wav | hit_c.mp3 | 2303 Futuristic bass hit |
许可均为 Mixkit Sound Effects Free License（免费商用、无需署名）。详细对照见 `assets/sfx_v3/SOURCES.md`。

## 画面
- BBC Verify 视频截帧和片段（c52e9zwd2vx8o，2026-10-16）、X 网传视频、评论截图、Annahar / Hive 截图：评论引用，画面角标写明出处，评论头像昵称已打码。来源见 `facts.md`。
- 照片：沿用 `assets/photos/SOURCES.md`（飞机 CC BY 4.0 4300streetcar；货轮 CC0 Martin Dörsch；手推车 CC0 Abraham / Wikimedia Commons）。署名打在画面角标上。
- 小官形象 / 贴纸：品牌自有（/workspace/brand/v2/qban）。
- 字体：Noto Sans CJK SC Bold（SIL OFL 1.1），按片中用字子集化为 `fonts/NotoSansSC-Bold-v3.otf`。
