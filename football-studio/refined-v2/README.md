# 精修 v2 关系板

同一套正俯视关系板，改由场次包驱动。画法沿用网盘精修源码（`vendor/render_v2.py`、`vendor/core.py`）：1280×720、25fps、图形 2 倍超采样后再缩回，黄实线是球路，绿虚线是跑动，红虚线是防守，右上角是同方向的小地图，一块板一个短问句。

这里不执行 vendor 里的原文件。那两份源码在导入时就绑定 2018 阿森纳对莱斯特的球员、旁白词和脚点。

## 现在能渲染的

| 场次 | 是什么 | 不是什么 |
| --- | --- | --- |
| `episodes/arsenal-2018-regression` | 已确认关系几何的视觉回归 | 不是新比赛，仓库里没有实拍帧，所以没有并排画面 |
| `episodes/sample-not-a-match` | 接口样例，坐标是编的 | 不是 2020-08-14 穆勒回合，也不是任何一场的真实板 |

没有核实过的穆勒坐标。缺了场次包、坐标、时间或证据指针，程序直接拒绝，不会把阿森纳的人和词填进去。

## 准备

```bash
cd football-studio/refined-v2
python -m pip install -r requirements.txt
```

字体优先用包内 `fonts/NotoSansSC-700.ttf`。找不到时才用系统字体，并在清单里写明没有对齐。若要换字体：

```bash
export REFINED_V2_FONT=/path/to/NotoSansSC-700.ttf
```

不调用配音，不下载比赛画面，不渲染音轨。

## 检查

```bash
cd football-studio/refined-v2
python -m unittest discover -s tests -v
```

## 出图

```bash
python -m refined_v2 episodes/arsenal-2018-regression --out demo/arsenal
python -m refined_v2 episodes/sample-not-a-match --out demo/sample
```

每块板按分层时间写出 PNG 和进度条。样例另外有一张占位证据图的并排 QC，图上标着原生尺寸。回归包的 Q4 有前后对照和一段无声 mp4。画面底部有「回归」或「样例」字样。

输出是原生 1280×720。2 倍超采样只为抗锯齿，缩回以后仍然是 1280×720，不是高清修复。

## 下一场怎么接

新建目录，放一份 `episode.json`。`claim` 用 `evidence_locked`。每个球员、附加点、位移和线段都要有 `evidence_id`，并且 `evidence_frames` 里的文件要真实存在、尺寸和声明一致。

坐标用 0–100 的手工关系 uv。若采集时攻门在右，把 `input_attack` 设为 `right`，程序会对全部 `uv` / `frm` / `to` 做同一次 `u' = 100 - u`。像素脚点不会跟着翻。标了 `intent: forward` 的球路，翻转之后终点的 u 必须更小。

有字级旁白时把 `timing_basis` 设为 `word_clock`，并给出 `clock.scenes`。找不到那个词就拒绝，不会去旧旁白里借。

实拍圈只能定格，而且要同时有脚点像素和 mask。没有逐帧脚点就不能做动圈。

`episode_id` 不要用 `arsenal-2018-regression` 或 `sample-not-a-match`。这两份是固定夹具。

`episodes/bayern-20200814-mueller-open-lock-draft/` 是 2020-08-14 首球。坐标在 1280×720 审阅代理上对照过，接触图来自 1080p 的同一时刻。`geometry_verified` 为 true 只表示这三块板和这些证据帧对过，并写出了源帧|板帧。俯视仍是 `schematic_shared_window`，不是场地测绘。

能连续播放的画面是三段，合计 8.8 秒：实况裁切 9.0–12.0，回放 A 21.8–24.6，回放 B 24.8–27.8。讲解稿里的 84 秒要等配音，这里不凑。源 56–58 秒的中圈开球不能拼进来。

巴萨 5 号按裁切 9.6 秒重标，不再用 (150, 720)。实况两名白衣标成「回做点」「接应点」，不写「无号码」，也不标 9 或 25。18 号只在门后右缘，不进入回做，也没有为它补一条跑动。门将背上的数字在这份 720p 代理里不够清楚，不标 1。球路只用同一机位上两个已看过的点，从 9.6 秒长到 10.2 秒。

观众成片走 `python -m refined_v2.film`。核验戳只留在 QC。示例成片静音，字幕是样例，不是最终母带。回实拍是 5 帧交叠。详见 `EDL_SCHEMA.md`。

## 已生成的图

回归板和接口样例仍标着「回归」或「样例」。首球观众示例不烧核验戳，文件名和 QC 目录写明它不是母带。

- `demo/arsenal/`：Q1–Q5 分层静帧、进度条、Q4 前后对照、`Q4_LAYERS.mp4`
- `demo/sample/`：接口样例
- `demo/bayern-lock-draft/`：三块板的分层短片和源帧|板帧 QC
- `demo/audience-example.mp4`：静音观众示例，约 17.7 秒
- `TEST_RESULTS.txt`：测试记录

根目录 `.gitignore` 忽略 png 和 mp4。这两项目录里的演示文件是单独纳入版本库的，方便把图拷回制作机。
