# 把模糊不满意变成具体改法

## 8秒视觉叙事实验

`output/concept-study.mp4`：250帧，约8.33秒，1080×1920，30fps。

- `npm run render:concept`；画面入口 `src/concept.tsx`。
- 文案：再高级一点？改颜色，还是改排版？先锁定标题，再明确改法：放大。
- 配音：Edge云希+10%，`scripts/narration-concept.py`，词边界 `src/concept-timing.json`。
- 过程：一句意见分叉为颜色/排版/标题三种可能；两项退出，原来的标题纸片连续移动并放大成为主体；“放大”指令抵达尺寸锚点后才改变字号。
- 不使用原页面窗口，不重播四项框架。代表段用于验证视觉表达，未替换前四版。

## 第三版：节奏与动作衔接

`output/sample-v3.mp4`：24.87 秒，1080×1920，30 fps。

- `npm run render:v3` 重渲染，动画入口 `src/snappy.tsx`。
- 配音为云希 +10%，稿件直接穿进案例，取消先讲框架再重复演示。脚本 `scripts/narration-edge-v3.py`，逐词数据 `src/v3-timings.json`。
- 段尾分别保留 0.12、0.12、0.18、0.7 秒；不是统一加速旧视频。
- 页面移动约 0.47–0.6 秒，字号变化 0.6 秒，说明弱化约 0.33 秒，按钮确认约 0.27 秒。
- 动作用快速启动、短促收住的曲线；下一重点提前约 5–7 帧接应。页面持续存在，旧标注收为小标签，下一标注继续指向同一对象。
- 标题放大和说明弱化分开触发，结尾保留观察前后差异的时间。第一、二版视频与配音保留。

## 新版：连续纸面动效 + Edge TTS

`output/sample-v2.mp4`：35.9 秒，1080×1920，30 fps。原版仍保留。

- 用 `npm run render:v2` 重渲染，编辑入口是 `src/continuous.tsx`。
- `scripts/narration-edge.py` 使用 Edge TTS `zh-CN-YunxiNeural` 云希，语速 +0%。需要 Python、edge-tts 7.3.1、FFmpeg。运行时将本脚本中的口播文本提交给微软语音服务。
- `src/edge-timings.json` 保存实测音频时长、逐词边界与每段 0.5 秒尾停；新版字幕与关键动作按词边界定位。
- 同一张演示页面贯穿模糊反馈、四项标注、原位修改和前后对比。取消整屏淡出，通过对象位移、缩放、描线和状态变化承接。
- 静态方向改为暖纸色、细网格、宋体标题、朱红标注与青绿保留项。参考的是用户指定视频中抽样看到的纸面设计，不是原片完整复刻。
- 配音是 Edge TTS 试听，案例为代码生成界面；未使用原片的画面或声音。

34.47 秒、1920×1080、30 fps 的 Remotion 中文演示样片。

## 运行

```powershell
npm install
npm run studio
npm run check
npm run render
```

输出：`output/sample.mp4`。关键帧：`output/frame-01.png`、`frame-02.png`、`frame-03.png`。

当前配置使用本机已安装的 Google Chrome，避免下载浏览器。换机器时，在 `remotion.config.ts` 修改浏览器路径，或设置 `REMOTION_BROWSER_EXECUTABLE` 环境变量。当前中文字体为 Windows 微软雅黑。

## 修改入口

- `src/video.tsx`：画面、配色、动画、字幕和案例 UI。
- `scripts/narration.ps1`：四段口播文本，使用 Windows Microsoft Huihui Desktop 系统声音生成试听配音。
- `src/timings.json`：每段音频实测时长和开始帧，由配音脚本生成。
- `src/index.tsx`：尺寸、帧率和合成配置。

调整配音后，在项目根目录执行 `./scripts/narration.ps1`，再调整 `src/video.tsx` 中各段字幕和动画的相对帧数。当前动画按现有音频手工对齐，不是自动语音对齐。

## 内容设计

1. 0–5.13 秒：提出“再高级一点”的模糊反馈。
2. 5.13–16.47 秒：拆成位置、问题、目标、限制。
3. 16.47–28.23 秒：代码界面演示标题放大、说明弱化、按钮保留。
4. 28.23–34.47 秒：前后并排对比。

这是代码生成的讲解案例，画面中已经标注“演示案例”；没有使用真实 AI 操作录屏。配音为本机系统合成试听版本。没有背景音乐，也没有使用抖音原片画面或声音。

## 第四版：镜头跟随与指令驱动

`output/sample-v4.mp4`：沿用第三版云希 +10% 配音和 746 帧时间轴，24.867 秒、1080×1920、30 fps。

- `npm run render:v4` 重渲染，新增画面入口为 `src/guided.tsx`，Composition 为 `Guided`。
- 页面镜头依次聚焦标题、下移到说明、继续下移到按钮，再在前后比较前拉回全貌。固定标题、解说和字幕独立于页面镜头。
- “放大”“弱化”“保留”标签逐个沿曲线从解说区飞向对应对象。标签在对象边缘落下，以短连线连接目标；抵达后再触发字号、透明度或保留描边变化。
- 每次标签旅行约 0.53 秒，页面状态变化约 0.4–0.47 秒；比较前回全貌约 0.6 秒。沿用第三版纸面风格与结尾比较内容。
- 旧版源码、配音和 MP4 均保留，公共 `Page` 组件未改动。
- 关键帧：`output/v4-title.png`、`v4-detail.png`、`v4-button.png`、`v4-ending.png`。

## 完整版：从概念样片接续为完整叙事

`output/story-full.mp4`：24.1 秒、1080×1920、30 fps，723 帧。

- `npm run render:story` 重渲染；入口 `src/story.tsx`，Composition 为 `Story`。
- 前约 8 秒复用已认可概念样片的视觉逻辑、原配音与纸片几何，235 帧后开始衔接。原 `Concept` 源码和音频保持原样。
- 同一张标题纸片原位展开为完整页面，增加说明和青色按钮。先框定按钮颜色不改，再降低说明的视觉权重。
- 结尾用同一页面上的擦除对比揭示修改前后。前后文案与按钮颜色一致，仅标题字号与说明透明度不同；随后拉远收尾。
- 新增两段云希 +10% 配音由 `scripts/narration-story.py` 生成，`src/story-timing.json` 保存实测时长和词边界；开场直接读取现有 concept 音频。
- 末段有 1 秒自然尾停。动画时间轴按三段音频取整，未整体拉伸或加速。
- 关键帧：`output/story-boundary.png`、`story-ending.png`；总览 `output/story-overview.png`。

## 三维原理片：梯度下降

`output/gradient-descent.mp4`：34.2 秒，1080×1920，30 fps。主画面由 Three.js / React Three Fiber 与 `@remotion/three` 的 `ThreeCanvas` 实时渲染；不是二维假透视。所有相机、参数点、路径与箭头都由视频帧驱动，没有物理重力模拟。

- 运行：`npm run render:gradient`；预览：`npm run studio` 中选择 `Gradient`；校验：`npm run check`。
- 画面入口：`src/gradient/index.tsx`；三维场景：`scene.tsx`；数学模型：`model.ts`；配音词边界：`timing.json`。
- 新配音脚本：`python scripts/narration-gradient.py`，需要 edge-tts 7.3.1 和 FFmpeg；声音为云希 +10%。
- 玩具损失函数：`L(x,z)=0.35x²+0.8z²+0.18xz`，解析梯度为 `(0.7x+0.18z, 1.6z+0.18x)`，每步更新 `p ← p − η∇L(p)`。两个水平轴是参数，竖直高度使用 `0.32 L` 仅做显示缩放，读数仍为原始 L。
- 各条路径从 `(2.6,1.9)` 出发；合适步长 `η=0.5`，小步长 `0.06`，过大步长 `1.32`。过大只展示3次更新，末点仍在真实曲面范围内，没有裁剪参数或伪造损失。
- 球是参数位置标记，不是自动滚落的实体；路径沿损失曲面采样，每次更新完整移动后停顿。
- 曲面是正定二次函数。这一示例的正常步长降低损失，不表示所有神经网络或随机梯度训练每一步都下降，也不表示一般非凸问题能保证找到全局最优。
- 参考原理：[Google MLCC：超参数](https://developers.google.com/machine-learning/crash-course/linear-regression/hyperparameters)、[Stanford CS231n：优化](https://cs231n.github.io/optimization-1/)。
- 浏览器使用本机 Chrome，渲染启用 ANGLE WebGL；若换机器需相应调整浏览器路径。所有旧作品保留。

## 梯度下降动态镜头版

`output/gradient-descent-dynamic.mp4`：34.2 秒，沿用原版数学、云希音频和1026帧时间轴。

- 新增独立入口 `src/gradient-dynamic/index.tsx` 与场景 `scene.tsx`，旧 `Gradient` 和原MP4保持不变。
- `npm run render:gradient-dynamic` 重渲染，Studio选择 `GradientDynamic`。
- 开场先画参数轴，再展开平面网格；当旁白解释高度时，顶点从0抬升到同一损失函数表面。球的高度与误差高度线同步抬升。
- 局部坡度箭头先出现，参数更新时镜头近景跟随点并平移，竖直误差线随真实损失收短。术语出现时拉远揭示离散轨迹。
- 小步采用短而密的更新；过大步换到另一侧，展示越过低点；换回合适步长后回到原侧并收稳。
- 相机事件过渡16帧左右，参数移动12帧以内，每步完成后停顿；所有动画来自视频帧，无 `useFrame` 或物理滚动。
- `src/gradient/model.ts` 与 `timing.json` 被只读复用；函数、解析梯度、学习率及数学限制同上一节。三维场景为真实 `ThreeCanvas`，坐标标签按同一相机投影定位。
- 关键帧：`output/gradient-dynamic-opening.png`、`gradient-dynamic-follow.png`、`gradient-dynamic-large.png`；总览 `output/gradient-dynamic-overview.png`。

## 梯度下降重点强化版

`output/gradient-descent-focus.mp4`：复用34.2秒原配音、真实三维地形和解析梯度，独立入口 `src/gradient-focus/`，Composition为 `GradientFocus`。`npm run render:gradient-focus` 重渲染。

- 降低全局网格存在感，增大参数球、方向箭头与当前轨迹；首步按局部坡度高亮、方向箭头、参数移动、误差高度线收短的顺序解释更新。
- 步长比较使用同一起点、每种各3次更新，保留原步长0.06、1.32与0.5。第三次更新的实际损失分别为3.699、10.939、0.142，起始损失6.143；过大轨迹没有伪造或裁剪。
- 前一次比较的3步轨迹以浅金淡影保留，当前轨迹使用更粗的青绿或朱红；合适步长比较完成后继续更新至9次再收尾。
- 轻量落点环只在一次更新到位后出现；误差竖线为透视辅助线，允许透过曲面显示，数值仍按真实坐标计算。
- 关键帧 `output/gradient-focus-slope.png`、`gradient-focus-large.png`、`gradient-focus-compare.png`；总览 `output/gradient-focus-overview.png`。旧版本全部保留。

## Fish旁白与事件同步版

输出 `output/gradient-descent-sync.mp4`，独立工程入口 `src/gradient-sync/`，Composition 为 `GradientSync`。使用完整同音色 Fish 旁白 `public/fish-gradient-full.mp3`，音频26.802秒，时间轴810帧/27秒（含收尾），不再使用旧Edge分段时长。

- `python scripts/build-sync-assets.py` 从 `output/fish-gradient-full-alignment.json` 逐字绝对时间戳创建 `src/gradient-sync/timing.json`。缺少关键词、文本不匹配、时间戳不单调或动作时间不足时直接报错。
- 事件表同时驱动视觉与音效：参数轴、网格展开、高度抬升、坡度高亮、方向箭头、首步调整、重新计算、再次调整、梯度下降术语、三种步长比较。首步327–341帧，第二步363–377帧；落点敲击与脉冲同帧。
- 首更新动作前5帧轻推近约2.5%，动作中跟随参数点，落点后6帧收稳；底部依当前事件强调“坡度/更新/重新计算”。
- 音效由numpy/wave本地合成，固定seed，无付费音效服务，无背景音乐。纸感展开、短划、低敲、大步掠过保持低音量，重复更新更轻；旁白音量0.85留混音余量。
- `npm run render:gradient-sync` 渲染；`npm run check` 类型验证。整体事件量化误差最多半帧，音效与对应视觉共享同一整数帧。
- 中段精确重编码短样片 `output/gradient-sync-principle.mp4` 从“根据当前位置”开始，到“梯度下降”词结束后约0.3秒，用于快速检查语音和动作配合。
- 同起点3步步长比较、解析模型、旧版视频/源文件保留。逐字边界为自动对齐数据，非人工逐字听审结果。

## 梯度下降叙事新版：预测直线 → 参数地图 → 更新 → 预测改善

`output/gradient-descent-story.mp4` 使用 `GradientStory` Composition，独立源码 `src/gradient-story/`。Fish旁白40.176秒，1211帧（约40.37秒，含收尾），1080×1920、30fps。所有旧视频、模型与配音保留。

- 重建事件：`python scripts/build-gradient-story.py`，只读取 `output/fish-gradient-story-alignment.json`，不访问网络或密钥；缺词/文本不匹配/时间戳不单调/动作窗口不足时报错。
- 预览：`npm run studio` 选择 `GradientStory`；渲染：`npm run render:gradient-story`；类型验证：`npm run check`。
- 数学统一：5个真实点x=[−1,−.5,0,.5,1]，y=.8x+.5。预测y=ax+b，偏差p=[a−.8,b−.5]，MSE=.5p₀²+p₁²，解析梯度[p₀,2p₁]。同一模型计算直线、残差、旋钮值、地形、箭头和误差读数。
- 开场p=[1.7,1.7]，斜率旋钮先调到[1.2,1.7]、截距再到[1.2,1.2]，之后不跳值地接到参数地图。地形轴是实际参数a/b的位置差值，叠加读数显示实际a/b；高度显示0.65×MSE。
- 斜率/截距两条局部截线与两个负梯度分量构成同一下降方向，不模拟重力。 first两步以“移动一点”“再走一步”关键词驱动。
- 小/大步先分别演示第一步；“用同样的三步”时在同一相机、同一曲面、同一起点同时推进三种步长，每种各3次更新。学习率.06、1.05、.35的3步误差分别1.165448、2.551048、.055351，初始2.16；参数都在地形范围内，不裁剪参数。
- 合适步长继续更新到9次，再把同一最终参数带回最初直线、残差与两旋钮。曲面是线性回归的凸二次示例，不推断一般神经网络每步都下降或保证全局最优。
- 主画面为真实ThreeCanvas三维模型；相机只在表达尺度改变时变换，没有useFrame或反复镜头脉冲。轻音效复用本地sync wav，事件表共享整数帧，旁白音量.85留母版余量；最终响度由主会话统一处理。
- `build-gradient-story.py` 自检：样本MSE和闭式公式一致，解析梯度与中心有限差分一致，三种3步末点不越界。
- 关键帧 `output/gradient-story-opening.png`、`gradient-story-handoff.png`、`gradient-story-components.png`、`gradient-story-compare.png`、`gradient-story-return.png`；总览 `output/gradient-story-overview.png`。
- 显示精度：误差统一保留三位小数。结尾 `0.000` 是四舍五入显示，不代表数学上严格为0；9步后的a约0.82，仍存在很小的真实残差。
