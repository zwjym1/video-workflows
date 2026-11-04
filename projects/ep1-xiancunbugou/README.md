# EP1《FlashAttention 是什么》—「显存不够」像素风科普

「显存不够」系列的第一期，也是这套像素风动画生产线的**参考实现**。
全片 398 秒，1920×1080 横屏 30fps，Remotion 代码驱动，无实拍。

## 这一期真正解决的问题：画面填充度

我们最早的版本被判定「看着呆板」。第一次诊断走错了方向——以为是动效太少，
于是给每个元素叠了浮动、旋转、呼吸和每 0.7 秒一次的随机小动作。
**这是错的**，而且被用户当场指出来（「为什么画面元素要晃来晃去」）。

用同一把尺子量对标（小白debug 的 vLLM 与 DeepInfer 两期）才发现真相：

| 片 | 静止帧占比 | 动作事件/秒 | 非背景像素占比 | 边缘能量 |
|---|---|---|---|---|
| 对标 vLLM (788s) | **63.5%** | 1.07 | **25.6%** | **6.04** |
| 对标 DeepInfer (680s) | **47.9%** | 1.14 | **25.1%** | **6.80** |
| 我们 v1 | 45.8% | 1.30 | 16.9% | 4.89 |
| 我们「提速版」（堆微动效） | 8.6% | 1.59 | 16.5% | 4.73 |

**对标比我们更静止。** 我们动得更多、更碎，却看着更空。
差距在填充度，不在动效密度。把动作密度从 0.8 拉到 1.59 只让片子更吵，没让它更好看。

更关键的是落差，不是均值。按 2fps 算内容占比的分位数：

| 片 | P10 | P50 | P75 | P90 | P99 | 最高 |
|---|---|---|---|---|---|---|
| 对标 vLLM | 0.122 | 0.234 | 0.310 | 0.408 | **0.957** | 0.977 |
| 对标 DeepInfer | 0.129 | 0.231 | 0.292 | 0.369 | **0.960** | 0.986 |
| 我们 v1 | 0.108 | 0.165 | 0.205 | 0.256 | **0.282** | 0.302 |
| **本期成片** | — | **0.286** | 0.370 | 0.451 | **0.883** | 0.922 |

对标在 0.13 ↔ 0.96 之间大幅摆动，我们原来全程卡在 0.11–0.30 的窄带里，永远没有满屏砸过来的峰。
所谓「节奏」，本质是**留白与塞满的落差**。

完整规范见 [`docs/DENSITY_SPEC.md`](docs/DENSITY_SPEC.md)。

## 动效硬规矩（这一期最重要的产出）

**动效只能来自信息本身的变化。** 数字滚动、格子点亮、进度推进、有语义的入场与变形——这些可以动。
元素浮动、旋转、呼吸、随机 idle、闪烁、按拍脉动、背景扫光带——一律不许，那是「晃」，不是「动」。

判断标准一句话：**这个动作让观众多知道了什么？** 答不上来就删掉。

本期为了这句话拆了 13 处装饰性微动。拆除后全片静止帧占比 9.6% → 56.2%，
落在两个对标（63.5% / 47.9%）中间，填充度与边缘能量反而略有上升（6.31 → 6.45）。

## 项目结构

```
remotion/          Remotion 工程（TypeScript + React）
  src/
    Root.tsx       合成注册：EP1v3 为本片，Episode/Final 为早期版本
    Chapters.tsx   分镜主体：9 个章节 × 共 86 句口播，逐镜元素与走位
    Motion.tsx     通用动画原语（MPop/Pop/Pulse/Card/Kid/FanLayer/ProgCtx）
    W.tsx          图表与图解件（Token、QKV、天平、问号方块、check 等）
    Dense.tsx      全屏信息墙（矩阵墙 / 数字墙 / GPU 阵列 / 章节大字卡）
    kit.tsx        场景底色、HUD、字幕条、主题材质适配
    Sprite.tsx     像素精灵加载
    sprites.tsx    程序化粒子（星尘、尘埃）
    Cover.tsx      封面（9:16 与 4:3）
    theme/         皮肤系统：pixelDark / neonGlass / paperEditorial
    timeline/      120 BPM 节拍网格
    components/    BeatSync
    vo.json        86 句口播的逐字时间轴（Fish TTS s2.1-pro-free 输出）
  public/
    sprites/       像素素材（入库，渲染必需）
    fonts/         子集化字体（Noto SC / Inter / IBM Plex Mono / 缝合像素）
    sfx/           音效（入库）
    vo/ bgm/       不入库，见「重新生成」
tools/             质检脚本
docs/              规范与对标分析
```

## 运行

```bash
cd remotion
npm install
npx remotion studio                 # 预览
npx remotion render src/index.ts EP1v3 ../out/ep1.mp4 --codec=h264 --crf=18
```

渲染整片约 4 分钟（8 核）。

## 重新生成不入库的资源

配音：`src/vo.json` 存了 86 句的文本、音色 ID（`2abd548310dc4741b73e3ccc69ddc61d`，
s2.1-pro-free「浙大男生书包」）、每句时长和逐字时间轴。按 `file` 字段命名重新合成到
`public/vo/`，时间轴不必重算。口播干声标准 −19.4 LUFS。

BGM：`docs/BGM_GUIDE.md` 有完整选曲与处理流程。本期用的是秋成《We Never(若如初见) Vibe版》
（Hi Noise remix），实测 117.4478 BPM，用 `atempo=1.02173` 拉到 120 BPM（这样节拍/小节/16 拍乐句
在 30fps 下都是整数帧：15 / 60 / 240），循环到 400 秒，再压成 −32.6 LUFS 的底床。
生成脚本 `tools/bgm_slice.py`。

## 质检出片

```bash
python3 tools/qc_density.py <视频> --fps 1     # 填充度 + 边缘能量 + 每 20 秒分段
python3 tools/qc_pct.py    <视频>              # 分位数 P50/P99 与爆点区间
python3 tools/qc_smooth.py <视频>              # 帧差与静止帧占比
```

四条硬指标，不达标不交付：

1. 内容占比 **P50 ≥ 0.23**
2. 内容占比 **P99 ≥ 0.85**，最高 ≥ 0.90
3. 边缘能量 **≥ 6.0**
4. 同屏信息组数 **≥ 3**

爆点是稀有事件：**每 90–120 秒一次，每次 1.5–2 秒**。对标全片占屏 ≥0.80 的时间只有 1.7–1.8%。
不要做成常驻满屏——那是「一直密」，不是「有节奏」。

音频交付标准：**−14.0 ±0.3 LUFS 综合响度，真峰值 ≤ −1.0 dBTP**。

## 对标与规范文档

| 文件 | 内容 |
|---|---|
| [`docs/DENSITY_SPEC.md`](docs/DENSITY_SPEC.md) | 画面填充度规范（本项目的核心方法） |
| [`docs/STYLE_RESEARCH.md`](docs/STYLE_RESEARCH.md) | 9 个同类知识博主的视觉拆解（切镜率、动作事件、入场时长） |
| [`docs/BGM_GUIDE.md`](docs/BGM_GUIDE.md) | BGM 选曲、测 BPM、拉伸对齐、底床压缩 |
| [`docs/REPLICA_SPEC.md`](docs/REPLICA_SPEC.md) | 复刻规范 |
| [`docs/IMITATION_PLAN.md`](docs/IMITATION_PLAN.md) | 逐项模仿计划 |
| [`docs/shots_vLLM.md`](docs/shots_vLLM.md) | 对标 vLLM 一期 64 个镜头表 |
| [`docs/shots_DeepInfer.md`](docs/shots_DeepInfer.md) | 对标 DeepInfer 一期镜头表 |
| [`docs/ANALYSIS.md`](docs/ANALYSIS.md) | DeepInfer 逐帧分析 |

## 已知短板

- 195–220 秒是全片最空的一段（内容占比约 0.23），正在补真实内容。
- 四处全屏爆点全部落在章节卡上，镜头中间还没有爆点。
