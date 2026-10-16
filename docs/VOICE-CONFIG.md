# 配音（Fish TTS）配置教程

这份教程面向新手，跟着步骤一步步做就能生成配音。**API Key 绝不能写进代码或提交到 GitHub**，只能放在环境变量里。

## 1. 用到的音色 ID（reference_id）

| 项目 | 音色 | reference_id | 说明 |
|---|---|---|---|
| 小学讲题 · π 的历史（`projects/pi-lesson`） | 几何女声 | `cf71d823861b4e0eadff1672d646da36` | 年轻女声，清晰、亲切，像年轻老师。试音 8 句拼音全对，**选用** |
| 科普短视频 · 梯度下降 v4（`projects/gradient-descent`） | 影视解说（男声） | `b4bdf5dc66004241a21ff2df165bf442` | 男声解说，全片固定这一个 |

试过但没选的音色（只记录了 ID 前缀）：女教师温柔版 `32ea6ed2…`、温柔男声·讲故事 `d99547e2…`、仔仔熊 `a70777db…`、另一个影视解说 `39ea…`、嘉岚 3.0、央视配音。
> 一定要指定固定的 reference_id。不指定的话，每句话的音色会像换了个人。

## 2. 模型和参数

- 接口：`POST https://api.fish.audio/v1/tts/stream/with-timestamp`（会同时返回音频和逐字时间戳，用于字幕对齐）
- 模型：请求头 `model: s2.1-pro-free`
- 请求体：`format: mp3`、`latency: normal`、`prosody.volume: 0`
- `temperature`：π 课用 0.7，梯度下降用 0.65
- 语速 `prosody.speed`：
  - π 课：普通句 1.0，问句 0.96，"想一想" 0.94，古文 0.88；全片再乘 0.95（环境变量 `SPEED_SCALE=0.95`）
  - 梯度下降：默认 1.08
- 情绪提示：每句开头加 S2 方括号提示，比如 `[warm, friendly, like explaining to a classmate]`、`[curious, warm]`
- π 在送 TTS 时写成"派"
- 每句生成两遍（fa/fb），挑拼音错误最少、音高起伏更大的那一遍

## 3. 读音规则：「量」

- **量作动词读 liáng（第二声）**：量一量、量周长、测量、我量了一下、"量总有误差"
- **只有名词才读 liàng（第四声）**：数量、质量、大量
- 让 TTS 读对的两种方法，**只改送 TTS 的文本，字幕和文案不改**：
  1. 音素标签：`<|phoneme_start|>liang2<|phoneme_end|>` 替换句子里的"量"
  2. 同音字：在 TTS 文本里把"量"写成"粮"
- Whisper 听不出声调，所以每句带"量"的话都要用 `tone_dtw.py` 检查音高（见第 5 步）

## 4. 设置 FISH_API_KEY（环境变量）

在 https://fish.audio 登录后，到 API Keys 页面创建一个 Key。

**Windows PowerShell（只对当前窗口有效）：**
```powershell
$env:FISH_API_KEY="把你的key粘贴到这里"
```
**Windows 永久设置**（设置完要重开终端）：
```powershell
setx FISH_API_KEY "把你的key粘贴到这里"
```
**Linux / macOS：**
```bash
export FISH_API_KEY="把你的key粘贴到这里"
```
也可以把仓库根目录的 `.env.example` 复制成 `.env` 再填值。`.env` 已经写进 `.gitignore`，不会被提交。
> Key 一旦被贴到聊天、截图或代码里，就去 Fish 后台删掉，重新生成一个。

## 5. 运行配音脚本（π 课，`projects/pi-lesson/voice/scripts/`）

先装依赖：
```bash
pip install requests numpy librosa faster-whisper pypinyin
```
注意：脚本里写的是云端工作目录 `/workspace/pi/voice/...`，在自己电脑上运行时，把脚本里的这个路径改成你本地的 `voice` 文件夹路径。

1. **生成逐句文本**：`build_sentences.py` → 输出 `sentences.json`（每句有 `cue` 情绪提示、`tts` 文本、`speed` 语速）
2. **合成配音**：
   ```bash
   # 用法：fish.py <标签> <reference_id> <句号列表|all>
   SPEED_SCALE=0.95 python fish.py fa cf71d823861b4e0eadff1672d646da36 all
   SPEED_SCALE=0.95 python fish.py fb cf71d823861b4e0eadff1672d646da36 all
   ```
   每句输出 `takes/fa-00.mp3` 和对应的时间戳 `.json`
3. **识别打分**：`eval.py` / `score.py` 用 Whisper 听写，比较拼音错误率，选出每句最好的一遍 → `selection.json`
4. **检查「量」的声调**：
   ```bash
   # 先用同一音色合成对照句：把"量"换成"梁"(liáng) 存为 takes/c2a-<句号>.mp3、c2b-<句号>.mp3，
   # 换成"亮"(liàng) 存为 takes/c4a-<句号>.mp3、c4b-<句号>.mp3
   python tone_dtw.py 15 takes/fa-15.mp3 takes/fb-15.mp3
   ```
   它会把每遍里"量"的音高曲线和"梁/亮"对照做 DTW 比较，**只保留更接近"梁"的那一遍**
5. **拼接成整条音轨**：`stitch.py` 按句插入停顿（句间 0.35 秒、冒号后 0.25 秒、章末 1.0 秒、[停顿2秒] 处 2 秒静音），输出 `pi-lesson-voice.mp3` 和对齐文件，放到 `remotion/public/`
6. **最终复查**：`final_asr.py` 对整条音轨做一次识别

梯度下降项目的脚本在 `projects/gradient-descent/scripts/narration-fish-v4.py`，用法：
```bash
python narration-fish-v4.py <标签> b4bdf5dc66004241a21ff2df165bf442 all [语速系数]
```
拼接用 `v4-stitch.py`。

更多细节见 `projects/pi-lesson/voice/VOICE-NOTES.md`。
