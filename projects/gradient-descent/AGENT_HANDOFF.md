# 视频项目交接：供 Opus 5.5 或其他 Agent 接手

## 当前状态（先读）

工作目录：`D:/编程/项目/口播`，Windows / PowerShell。

用户最新指令：**先不制作下一版，整理交接，准备换其他 Agent 试做。** 本次没有继续修改视频，也没有启动其他 Agent。接手后按用户的新指令行动。

最新成片：`output/gradient-descent-story-master.mp4`，约40.4秒，1080×1920、30fps。
对应源码：`src/gradient-story/`，Composition：`GradientStory`。

用户评价：整体还不错，但3D段观看视角不清晰，理解原理仍然困难。下一轮的重点是**教学视角、坐标对应、方向与高度的区分**，不是增加装饰动效或持续运镜。

## 用户目标与偏好

- 希望做类似浙大猫学长《AI到底怎么画出一张图》的原理解释视频，画面有设计感、空间感，动效自然引导理解。
- 用户多次认可之前纸片/对象接力版本的灵动感；不要为了3D丢掉对象变化与镜头叙事。
- 动作要干脆、衔接连续，避免慢吞吞、机械等间隔、长时间静止全景。
- 口播重音、对象动作、镜头和轻音效应配合。音画同步需要逐词事件，不只对齐整句。
- 讨厌生硬系统TTS。当前使用Fish Audio `s2.1-pro-free`。旧Edge云希+10%曾用于测试。
- 喜欢自主完成、少反复问确认。保留旧版本，新增版本用独立文件与名称。
- 不要虚称完整耳听/逐帧观看；讲清实际检验方法。不要根据参考封面猜整片风格。
- 当前想节省额度，建议先做8–12秒关键段验证视角，再决定是否扩展全片；这是建议，尚未制作。

## 最重要的输入与参考

- 原参考片：`C:/Users/Administrator/Downloads/浙大.mp4`，226.3467秒、720×960、30fps。
- 若使用交接ZIP在其他目录/机器接手，原参考片在`reference/reference-video.mp4`；以解压后的根目录替代本文工作目录。包内未带node_modules及完整抽帧缓存，需要时运行`npm ci`并从原片重新抽帧。音频、源码、最新词边界、最新成片和代表性旧成片已包含。
- 分享链接：`https://v.douyin.com/0JAY6vWwXUI/`，解析到`https://www.douyin.com/video/7694642902038859043`。
- 完整拆解：`参考研究/浙大参考片逐段拆解与改进.md`。
- 音轨分析：`参考研究/reference-audio-report.md`。
- 全片ASR：`参考研究/reference-transcript.{json,srt,txt}`；有“流行/造神/T度”等专业词错识别，不可直接当正式字幕。
- 抽帧与证据：`output/reference-analysis/`。全片每2秒114帧，0–4、40–52、142–154秒每秒4帧加密。音轨转录覆盖0.08–224.23秒；这不是直接耳听音效音色。
- 历史制作方法研究：`参考研究/Vibe-Motion制作方法笔记.md`。相关组织中有社区贡献，不能全说成博主个人方法。

### 从原片核实到的手法

- 0:00–0:05：像素数值→向量→空间点，同一信息连续转表示。
- 0:41–0:51：纸团→薄纸→面积×理想厚度0→体积0，对象形变参与论证。
- 1:43–1:55：图片加噪与曲线扩散同时发生，让抽象分布对应具体图片。
- 2:24–2:34：单点/单箭头→整个向量场，镜头相对稳定，运动来自对象。
- 3:34–3:42：猫狗两组同时去噪，上方图片与下方路径相互解释。
- 风格有黑金粒子、明亮纸团空间、金属仪表、浅色坐标、深绿向量场和暗红生成面板，绝非单一纸面或黑金。
- 不应简单增加镜头数量：每次画面变化要引入新理解，先实例后术语，结果处留短暂停顿。

## 最新待解决问题（已和用户讨论，尚未实施）

1. 地形两个轴与斜率a/截距b对应不明确；当前彩色边线缺少直接轴标签与位置参照。
2. 斜视压缩参数方向，前后运动和高度下降混在一起，观众需自行脑补空间。
3. 大块地形占画面，局部点、截线和箭头太小；放大没有真正聚焦到解释区域。
4. 两分量与合成箭头沿曲面弯曲，难看出参数平面里的直向量相加。参数平面向量与曲面高度变化应区分。
5. 误差降低主要靠数字，缺固定高度参照。

### 建议下一轮视觉方案

- 俯视参数平面：横轴斜率a、纵轴截距b，两个旋钮分别驱动同一点沿相应方向移动。
- 抬升曲面时保留底板，垂直投影线连接同一个参数位置，明确“位置=参数，高度=误差”。
- 方向段切局部俯视：两根直分量箭头、虚线平行四边形，最后留下合成负梯度箭头；周围地形弱化。
- 高度段切侧面截线：参数点更新时高度条缩短，专门解释为什么误差更小。
- 步长比较固定俯视角、尺度、起点与更新次数，避免换侧视角和遮挡。
- 每镜头只回答一个问题：俯视看方向、侧视看高低，三维全景连接二者。

## 最新版数学：必须保持一套模型

`src/gradient-story/model.ts`：

- 数据x=[−1,−.5,0,.5,1]，真实y=.8x+.5；预测y=ax+b。
- 参数偏差p=[a−.8,b−.5]；MSE=.5p₀²+p₁²；梯度=[p₀,2p₁]。
- 更新p←p−η∇L(p)。高度只显示`0.65*MSE`，误差读数仍为原MSE。
- 开场p=[1.7,1.7]，旋钮先调到[1.2,1.7]，再到[1.2,1.2]，连续接地图。
- 地形从p=[1.2,1.2]开始，初始MSE=2.16。
- 小步η=.06，三步MSE=1.165448。
- 大步η=1.05，三步MSE=2.551048，末p₁=−1.5972，在地形内。
- 合适η=.35，三步MSE=.055351，之后继续到9步，最终参数带回预测直线。
- 误差显示三位小数；最终0.000是四舍五入，不是严格0。
- 球代表参数状态，不模拟重力。不把凸线性回归示例说成所有神经网络都单调下降或一定全局最优。
- 数值检查已验证样本MSE=闭式公式，有限差分梯度误差约2.46e−11。

注意：旧`src/gradient/model.ts`是另一套玩具二次函数，**不能不加说明地混用到新直线模型**。

## 工程、配音与命令

本机已装Node/npm、FFmpeg/ffprobe；项目node_modules可直接使用。Remotion4.0.535，React19，Three0.186.1、@react-three/fiber9.8.2、@remotion/three4.0.535。

```powershell
Set-Location 'D:/编程/项目/口播'
npm run studio
npm run check
python scripts/build-gradient-story.py
npm run render:gradient-story
```

- `remotion.config.ts`指定本机Chrome：`C:/Program Files/Google/Chrome/Application/chrome.exe`。可用`REMOTION_BROWSER_EXECUTABLE`覆盖。
- Windows上渲染3D使用`--concurrency=2 --gl=angle`，已有npm命令。不要重新下载Remotion浏览器；之前下载会卡住。
- ThreeCanvas使用帧驱动位置/相机/动画；不要用useFrame、CSS动画或不确定的实时物理。
- 字体Microsoft YaHei、SimSun，本机可用。
- 有的Python启动方式落到Hermes虚拟环境，有的落到uv运行时；先确认解释器依赖，不要盲目重复安装。

### Fish旁白

- 最新整段音频：`public/fish-gradient-story.mp3`，40.17625秒。
- 完整逐词/字对齐：`output/fish-gradient-story-alignment.json`，186个时间片，文本匹配、时间戳单调已验证。
- 文案：`参考研究/梯度下降新版口播.txt`。
- 生成脚本：`scripts/narration-fish.py`，`synthesize('story', text)`会覆盖同名音频；新版本请换新index/文件名。
- 调用`https://api.fish.audio/v1/tts/stream/with-timestamp`，请求头`model: s2.1-pro-free`。音频字段是流式片段，需拼接；alignment是每个chunk的累计快照，不能每条快照重复累加。
- 单次整段生成避免分段默认音色不一致。语速1.08、temperature.65。中文文本应从UTF-8文件读，不要依赖Windows管道内联中文，曾产生乱码。
- 密钥只从`FISH_API_KEY`环境变量读。**交接文件不包含密钥，先前只在临时进程提供，当前不保证环境变量仍存在。现有音频可直接复用，不需要密钥。** 不要从聊天记录复制凭证到源码或日志。
- 本机代理曾让Fish TLS握手失败；脚本当前`Session.trust_env=False`直连可工作。
- `scripts/build-gradient-story.py`从原对齐JSON构建`src/gradient-story/timing.json`，按短语找事件，缺词/对齐不符/窗口不足应报错。
- 复用`public/sync-{paper,arrow,tap,sweep}.wav`轻音效，无BGM。声画使用同一整数帧事件表。

### 导出和母版

`npm run render:gradient-story`生成`output/gradient-descent-story.mp4`，不是最终响度母版。最新交付为`output/gradient-descent-story-master.mp4`，图像相同，音轨做过响度处理。

母版流程：先FFmpeg loudnorm第一遍测I/TP/LRA/threshold/offset，再用实测值第二遍处理，`-c:v copy`保持画面，AAC48k/192k，目标约−16LUFS、峰值约−1.5dBTP。使用新临时输出名，避免输入输出同文件。

```powershell
ffmpeg -hide_banner -i 'output/NEW.mp4' -af 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json' -f null -
ffmpeg -v error -i 'output/NEW-master.mp4' -f null -
ffprobe -v error -show_entries format=duration:stream=width,height,nb_frames -of json 'output/NEW-master.mp4'
```

## 检查标准与已知不足

- 类型检查、数学断言、完整音视频解码、尺寸帧数检查。
- 全片总览之外，重点加密检查旋钮到地图、分量合成、比较重置、结尾回图表等交界，不只挑好看静帧。
- 标签按同一相机投影；检查物体遮挡、文字与路径冲突、点是否越界。
- 切换表示时保留同一个点的身份，避免半透明球与正在移动的接力点同时出现两个对象。
- 图表clipPath避免预测线穿标题；开场预测最高y≈4.7，延长线还更高，坐标范围需容纳。
- 合适步长与图表参数/残差必须同步，不能视觉复位后继续沿另一套数值。
- 软件验证不等于审美通过。最新片技术检查通过，但用户仍明确认为3D教学视角不够好。

## 历史文件：不要误认当前版本

| 文件 | 用户反馈/用途 |
| --- | --- |
| output/concept-study.mp4 | 8秒左右纸片接力概念样片，用户明显认可灵动感 |
| output/story-full.mp4 | 24秒纸片/网页完整故事，用户认可 |
| output/gradient-descent.mp4 | 第一版真实3D，但用户认为失去灵动与镜头 |
| output/gradient-descent-dynamic.mp4 | 网格抬升、跟随、换侧 |
| output/gradient-descent-focus.mp4 | 局部高亮、误差线、三步比较 |
| output/gradient-descent-sync-master.mp4 | 27秒Fish配音、逐词/音效同步 |
| output/gradient-descent-story-master.mp4 | **最新40秒，当前接手基线** |

## 可选下载技能

已安装`C:/Users/Administrator/.codex/skills/video-downloader`（dudachun/video-downloader），独立依赖`./.venv/Scripts/python.exe -m yt_dlp`，Git Bash位于`C:/Program Files/Git/bin/bash.exe`。
帮助命令测试通过，原抖音链接模拟提取返回HTTP403、要求fresh cookies，未成功下载。不要声称“安装skill就保证解决下载”。本地原参考片已在，无需重复折腾网络。

## 接手方式

优先在同一目录用用户选择的Agent/模型打开本文件，先看最新成片与参考拆解，再处理最新视角问题。无需迁移聊天记录，不要传递历史密钥。
本交接不假定你拥有Codex专用工具；普通文件读写、Node、Python、FFmpeg足以继续制作。
