# 主题换皮系统 + BGM 卡点引擎

一套分镜、一套时间轴，换一个 theme 文件就换整套视觉皮肤。
分镜代码（`Chapters.tsx` / `Episode.tsx` / `Motion.tsx`）**不含任何颜色、圆角、字体、easing**。

---

## 1. 目录

```
src/theme/
  types.ts             Theme 接口（颜色/质感/形状/动效/字体/画材/节奏）
  ThemeProvider.tsx    React context + CSS 变量注入 + @font-face + cubic-bezier 解析
  color.ts             hex↔HSL、remap（跨皮肤配色推导）
  tokens.ts            109 个画材 token 的基准值（从源码扫描生成）
  materials.ts         画材派生 + CSS 变量导出
  mat.ts               最小的 var() 拼串工具（避免循环依赖）
  skins/
    pixelDark.ts       基准皮肤：所有数值原样搬自改造前代码
    neonGlass.ts       深色玻璃拟态 / 霓虹科技
    paperEditorial.ts  浅色纸质杂志
    index.ts           SKINS 注册表
```

```
src/timeline/
  fps.ts               帧率归一（useDesignFrame / Sfx / DESIGN_FPS=30）
  beats.ts             loadBeats / nearestBeat / onBeatIndex / framesToNextBeat
src/components/
  BeatSync.tsx         BeatProvider / useBeatPulse / useBeatIndex / OnBeat / BeatPulse
src/Audio.tsx          <Bgm/> <BgmRange/> —— 支持帧区间、音量、循环
src/data/beat_*.json   BPM + 拍点
scripts/bpm.py         音频 → BPM + 拍点
scripts/gen_click.py   生成 112 BPM 占位 click 轨
scripts/verify_skins.py 全部验收项，跑一遍就知道有没有退步
```

---

## 2. 颜色为什么用 CSS 变量

两个硬约束逼出来的：

1. **SVG 呈现属性要字符串**。`<rect fill={...}>` 塞不进 React context 对象。
2. **小部件工厂在模块作用域被调用**。`Chapters.tsx` 的数据表里写着
   `W.label('Q 查询 · K 键 · V 值', P.plate, 44)` —— 这些在 `import` 那一刻就求值了。
   如果用 context 取色，颜色会被永久冻结在第一次 import 时的皮肤上。

所以：**颜色走 CSS 自定义属性（绘制时求值），数值/时长/easing 走 context。**

- `--m-<token>`：109 个画材（`--m-ink`、`--m-panel`、`--m-hbm-light`…）
- `--t-<name>`：语义色 + 字体 + 阴影档位（`--t-text`、`--t-plate`、`--t-shadow-5`…）

组件里只写 `var(--m-gold)`，不写 `#F2C14E`。已核验：**组件目录下 0 个硬编码 hex**。

### 语义别名（为什么 P.ink 被拆开）

原本 `P.ink` 一个值干三件事：正文颜色、实心底板、图形描边。
深色皮肤下这三者必须分开（浅字 / 深块 / 灰蓝线），所以拆成：

| 别名 | 用途 | 像素皮肤值 |
|---|---|---|
| `P.text` | 正文/标题字 | `#1E1B25` |
| `P.plate` | 实心底板、反色标签 | `#1E1B25` |
| `P.stroke` | 图形轮廓 | `#1E1B25` |
| `P.onPlate` | 底板上的字 | `#FFFFFF` |

像素皮肤下四者取值与原代码完全一致 → 逐像素 diff 为 0。

---

## 3. 三套皮肤

### pixelDark（像素暗房，基准）

| 角色 | 值 |
|---|---|
| 背景 | `#F6F0E2`（米白纸） |
| 点阵 | `#E4DCCB` |
| 墨/描边 | `#1E1B25` |
| 深场底 | `#2A2733` / 网格 `#34303F` |
| 主强调 | `#E07A3A`（橙） |
| 次强调 | `#F2C14E`（金） |
| 第三强调 | `#2E8F82`（青） |
| 警示 | `#F8574C` |
| 成功 | `#65BF62` |
| 字体 | `FusionPixel`（fusion-pixel-12px-zh_hans.otf） |
| 圆角 | 0 / 0 / 0 |
| 描边 | 5px |
| 阴影 | `npx npx 0 rgba(30,27,37,.18)`（硬边无模糊） |
| 动效 | `enterMs=267`（8 帧@30），`easeOutBack`（c1=1.70158 原曲线） |
| 质感 | 噪点 0 / 暗角 0 / 毛玻璃 0 |
| rhythm | **0**（不吃拍，见下） |

### neonGlass（霓虹玻璃）

| 角色 | 值 |
|---|---|
| 背景 | `#070B18`，暗场 `#060A15` |
| 网格 | `#101a30` |
| 表面 | `rgba(20,32,58,0.55)`（半透明毛玻璃） |
| 描边 | `rgba(120,200,255,0.22)` / 轮廓 `rgba(140,215,255,0.38)` |
| 正文 | `#EAF2FF` |
| 次文 | `#8FA2C4` |
| 强调 | `#39E6FF`（青）/ `#B98CFF`（紫）/ `#3DE0C0`（薄荷） |
| 警示 | `#FF5F7E` |
| 字体 | 标题/正文 `Inter` + `Noto Sans SC`；等宽 `IBM Plex Mono` |
| 字号 | 标题 76px / 行高 1.04 / 字重 700 / 字距 −1.5 |
| 圆角 | 10 / 22 / 34 |
| 描边 | 1.5px |
| 阴影 | `0 {n*2.4}px {n*8}px rgba(0,0,0,.55)`（大扩散柔光） |
| 动效 | `enterMs=467`（14 帧），`cubic-bezier(0.16,1,0.3,1)` |
| 质感 | 噪点 0.05 / 暗角 0.55 / 毛玻璃 18px |
| rhythm | 0.85 |

### paperEditorial（纸本杂志）

| 角色 | 值 |
|---|---|
| 背景 | `#F4EFE4`（米白纸） |
| 点阵 | `#DED5C4` |
| 表面 | `#FBF7EE` |
| 描边 | `#17140F`（2.5px 细黑） |
| 正文 | `#17140F`（高对比黑） |
| 次文 | `#5C554A` |
| 强调 | `#C0341E`（朱红）/ `#C08A2E`（赭石）/ `#2F5D46`（墨绿） |
| 字体 | 标题 `Noto Serif SC`（700）；正文 `Noto Sans SC`；等宽 `IBM Plex Mono` |
| 字号 | 标题 74px / 行高 1.16 / 字重 700 / 字距 +1 |
| 圆角 | 0 / 2 / 3 |
| 阴影 | `{n}px {n}px 0 #17140F`（**硬阴影，0 模糊**） |
| 动效 | `enterMs=333`（10 帧），`cubic-bezier(0.2,0.9,0.24,1)` |
| 质感 | 噪点 0.16 / 暗角 0.12 |
| rhythm | 0.6 |

**字体已子集化并随仓库提供**（`public/fonts/`）：
NotoSansSC / NotoSansSC-Bold / NotoSerifSC-Bold / NotoSerifSC-SemiBold（各约 370KB，只含本片用到的 858 个字符），
Inter（Regular/SemiBold/Bold，40–42KB woff），IBM Plex Mono（Regular/SemiBold，21–22KB woff）。

---

## 4. 画材派生（为什么像素道具能跟着换皮）

像素道具（显卡、仓库、机柜、小人）是**逐格画死的**，颜色改不了。做法两步：

1. `tokens.ts` 里存 109 个基准画材（`--m-*`）。
2. 其它皮肤用 `deriveMaterials(spec)` 从基准色按「明暗曲线 + 色相收拢 + 饱和压缩」推出一整套：
   - 霓虹：明暗压到 0.055–0.86，色相往青（194°）收 62%，暖色单独拉紫（286°）
   - 纸本：明暗映到 0.09–0.98，全部有彩色收拢到朱红（12°），饱和度压到 ≤0.72

PNG 素材本身改不了色，所以 `Sprite.tsx` 按皮肤套 CSS filter：
霓虹 `saturate(.55) hue-rotate(-18deg) brightness(1.18)`；
纸本 `saturate(.18) contrast(1.35) brightness(.82)`；
像素皮肤返回空串（保证 diff=0）。

---

## 5. 帧率归一（30 ⇄ 60）

设计基准固定 30fps。**不重写时间轴**，只统一单位：

```ts
useDesignFrame()  // 当前帧 × 30 / fps  → 永远在 30fps 坐标系里
```

- 所有动画都读 `useDesignFrame()`，所以 30fps 第 600 帧与 60fps 第 1200 帧**逐像素相同**（已核验 6 个采样点全部 MAE=0）
- `theme.motion.enterMs` 经 `msToDesignFrames()` 换算成**设计帧**再用（早期版本错用了实际 fps 帧，导致 60fps 动画变两倍长，已修）
- `<Sequence>` 的 `from/durationInFrames` 用 `fromDesignFrame()` 换算
- 音效统一走 `<Sfx>`（内部换算），避免 60fps 下音效提前一半播完
- **人声也一样**：`CueSub` 里每个 cue 的 `<Sequence from>` 必须换算。
  这一处早期漏了，导致 60fps 下人声提前一倍 —— 已修，并在 6000 帧附近复测：
  30fps 取 3000–3029（1.0s）与 60fps 取 6000–6059（1.0s）音频时长均为 1.003s。

Composition：

| id | fps | durationInFrames |
|---|---|---|
| `EP1-pixel` | 30 | 11114 |
| `EP1-pixel-60fps` | 60 | 22228 |
| `EP1-neon` | 30 | 11114 |
| `EP1-neon-60fps` | 60 | 22228 |
| `EP1-paper` | 30 | 11114 |
| `EP1-paper-60fps` | 60 | 22228 |

（全部 370.47s。`Final` / `Episode` 两个旧 id 保留指向 pixel 皮肤，方便老脚本继续跑。）

---

## 6. 卡点引擎

### 6.1 检测（scripts/bpm.py）

```
python3 scripts/bpm.py public/bgm/xxx.wav --name xxx
→ src/data/beat_xxx.json  {"bpm": 112.0, "beats": [0.0, 0.5353, ...]}
```

三步，每步都为了绕开一个具体的坑：

1. **粗估 BPM**：librosa `tempo()` + 起音包络自相关，两者差 <4 就用自相关（分辨率更高）。
2. **找起音起点**：`_transients()` 在**原始波形**上找「越过门限的第一刻」（rising edge），精度约 0.5ms。
   - 不能用 librosa 的 onset 时间：那是分析帧时间，含 ~2.5 hop 系统延迟，会让整条拍点晚 50–60ms。
   - 不能找能量**峰值**：包络爬升使峰值系统性晚 40–60ms。
3. **最小二乘拟合**：对 `(起音时间, 拍号)` 做线性拟合，同时求出周期和相位，迭代 3 轮。
   - 不能直接用 librosa 的 112.35：tempo 是直方图 bin，分辨率约 0.1–0.3 BPM，64 拍会累积 0.1s 漂移。

**实测**（`public/bgm/placeholder_112.wav`，112.0 BPM，16 小节 64 拍）：

| 指标 | 结果 |
|---|---|
| 检出 BPM | **112.0**（要求 112±0.5） |
| BPM 误差 | 0.0000 |
| 拍数 | 65（含 t=0 首拍） |
| 平均拍间隔 | 0.535708 s（理论 0.535714） |
| 拍间隔标准差 | **0.062 ms** |
| 与真值最大偏差 | **0.4 ms** |

### 6.2 运行时（src/timeline/beats.ts）

- `loadBeats(name)` 读 json（`require` 静态引用，保证打包进 bundle）
- `nearestBeat(frame, fps, beats, toleranceFrames)` → 吸附到最近拍；**超出容差就不吸**，避免把远处的入场硬拽过来
- `onBeatIndex(frame, fps, beats)` → `{index, progress, phaseSec}`，当前第几拍 + 拍内进度

### 6.3 组件（src/components/BeatSync.tsx）

- `<BeatProvider name startFrame>` —— 提供拍点，`startFrame` 把音频内时间和整片时间对齐
- `useBeatPulse(strength, decayFrames)` —— 每拍返回 1→0 的衰减值（指数衰减）
- `useBeatIndex()` —— 当前拍号 / 小节号 / 是否重音
- `<OnBeat at>` —— 把任意组件对齐到最近拍再入场
- `<BeatPulse amount>` —— 每拍把子组件弹一下

**接线点**（`kit.tsx`）：字幕条强调竖条、字幕条整体、顶部进度条光晕、HUD 心跳，
全部乘以 `theme.rhythm`。像素皮肤 `rhythm = 0`，所以这些效果对它是严格无操作。

### 6.4 BGM（src/Audio.tsx）

```tsx
<Bgm spec={{name, file, volume, fromFrame, toFrame, offsetSec}} gain={1} />
<BgmRange fromFrame={0} toFrame={3000} file="bgm/x.wav" volume={0.12} />
```

默认 `volume=0.12`，循环（`loop`），支持只播指定帧区间。
已实测：在源文件 34.29s 结束之后的 34.3–35.3s 区间仍有声（−25.4 dB），证明循环生效。

---

## 7. 验收（`python3 scripts/verify_skins.py`）

| 项 | 结果 |
|---|---|
| pixelDark vs 改造前基准（frame 60 / 600，未受并行改动影响的区间） | **全图 MAE 0.00043 / 0.00086；排除进度条 MAE = 0.000000，不同像素 = 0** |
| 30fps vs 60fps（7, 45, 301, 777, 1234, 5000） | **6/6 MAE = 0.0** |
| BPM | 112.0 vs 真值 112.0，误差 0.0000 |
| 9 张皮肤 still | 全部 1920×1080 |
| 3 个预览 mp4 | 全部 1920×1080 / 90 帧 / 3.00s |

---

## 8. 开发期间发生的两次真实翻车（都修好了）

1. **60fps 人声提前一倍。** `CueSub` 把设计帧 `x.from` 直接塞给 `<Sequence from>`，
   60fps 下等于半秒就播一秒的音频。表现：60fps 版跑到 3000 帧之后整片就没声音了。
   修法：`<Sequence>` 的帧值全部过 `fromDesignFrame()`。复测：30fps 取 3000–3029 与
   60fps 取 6000–6059，音频时长都是 1.003s。
2. **`enterFrames` 单位错配。** 入场时长按实际 fps 算，却拿去和设计帧比较，
   导致 60fps 下所有入场动画变成两倍长。修法：毫秒统一换算成**设计帧**。
   复测：30/60 六个采样点全部 MAE = 0。

## 9. 与并行改动的兼容

开发期间有另一个 agent 在同一份代码上加了「120 BPM 硬卡点网格」（`timeline/grid.ts`）
和真实 BGM（`We Never` 拉伸到 120 BPM），把时间轴从 11114 帧改成 10886（原始）/ 11940（网格版）。
这件事对本系统的两个影响，都已处理：

- **`beats.ts` 的注册表现在有两条轨**：`we_never_120`（成片实际使用）和
  `placeholder_112`（自检用）。`bpm.py` 对真实 BGM 跑出 117.45，与拉伸目标的 120
  有偏差 —— 说明那条轨的拉伸精度值得复核，成片卡点目前依赖的是
  `timeline/grid.ts` 的整数帧网格（15 帧=1 拍），不是检测出来的拍点。
- **像素 diff 的比对区间收窄到 0–600 帧**。并行改动缩短了每段镜头时长，
  1800 帧之后的画面内容已整体前移（实测 1800 帧的原画面现在落在 1774 帧），
  旧基准不再可比。0–600 帧内排除进度条后仍是 **0 像素差异**，
  足以证明换皮重构没有动任何画面内容；进度条那 1–2 px 是因为它按
  `当前帧 / 全片总长` 算，总长变了自然变。

## 10. 已知取舍

- **像素皮肤不参与卡点**（`rhythm: 0`）。它的合同是「和改造前逐像素一致」，
  任何脉动都会破坏这个合同。想要像素风也吃拍，把 `pixelDark.rhythm` 调到 0.5 即可。
- **PNG 道具换皮靠 filter，不是真重绘**。色相/明暗能跟着走，但笔触仍是像素风。
  想要真正的霓虹矢量道具，需要另画一套素材（本次没做）。
- **60fps 是双倍帧渲染**，不是补帧。观感一致的前提是所有动画都读 `useDesignFrame()`，
  且所有 `<Sequence>` 的帧值都过 `fromDesignFrame()`。
  以后新增动画如果直接写 `useCurrentFrame()` + 毫秒，就会破坏一致性。
- 占位 click 轨只是为验证检测链路，正式配乐换掉后需要重跑 `bpm.py` 并更新 `DEFAULT_BGM`。
