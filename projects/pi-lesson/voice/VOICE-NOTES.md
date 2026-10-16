# 圆周率学习课 · 配音记录
- **接口**：Fish Audio `s2.1-pro-free`，`/v1/tts/stream/with-timestamp`。密钥只从环境变量 FISH_API_KEY 读取，没有打印。temperature 0.7。
- **音色（全片固定一个）**：**几何女声 `cf71d823861b4e0eadff1672d646da36`**。Fish 声音库的描述是“年轻女声，清晰、专业”，听起来像亲切的年轻老师。
- **试音**：4个声音 × 8句测试句（第1、11、14、40、47、64、70、87句，覆盖量/率/差/背/弥少/算筹）。都不是公众人物克隆。
| 声音 | id | 拼音错（8句） | 音高起伏(半音) | 结论 |
|---|---|---|---|---|
| 女教师温柔版 | 32ea6ed2… | 第47句0.5（“隔着迷信所寻觅上”）、第64句有错 | ~2.7 | 古文读不清，弃用 |
| 温柔男声·讲故事 | d99547e2… | 第40、70句有错 | ~1.9 | 偏平、语速快，弃用 |
| **几何女声** | **cf71d823…** | **8句全为0** | **~3.2** | **选用** |
| 仔仔熊（活力男声） | a70777db… | 4句有错（“谁呆得更多”等） | ~4.6 | 表现力强但太卡通，咬字不稳 |
- **逐句设置**：89句（按句号/问号/冒号切分，π送TTS时写成“派”）。每句开头加一个 S2 情绪提示：
  - 默认：`[warm, friendly, like explaining to a classmate]`，速度 1.0
  - 问句：`[curious, warm]`，速度 0.96
  - 想一想：`[gently asking, inviting the listener to think]`，速度 0.94
  - 古文“割之弥细，所失弥少”：`[slow, reciting an ancient line]`，速度 0.88
  - 结论句（不会、七位、一千年、314万亿、一粒沙子）：`[a little excited, with emphasis]`
  - 全片再乘 0.95 的速度系数，适合小学生。
- **停顿**：[停顿2秒] 处插入**真实的2.0秒静音**；句间0.35秒，冒号后0.25秒，章末1.0秒。
- **两遍择优**：每句生成 fa、fb 两遍；第10、20、27句再加 fc、fd；按“拼音错误率（不计声调）最低 → 音高标准差更大”选择。选中89句拼音错误全部为0。选择结果见 `selection.json`。
- **一处改稿**：第33句“六边形，周长除以直径，是三。”在4遍中都被识别成“处于直径十三”（“是三”和“除以”连读不清），所以改成“六边形，周长，除以直径，结果是三。”，已同步到 `step3-script-final.md`。字幕跟着这句改。
- **时长**：全片 **330.8秒（5分31秒）**，比按4.2字/秒估计的约298秒长，原因是语速放慢到0.95，加上7处2秒停顿和句间停顿。如果要压到5分钟以内，可以把速度系数改回1.0，或者把句间停顿缩到0.25秒。
- **局限**：Whisper 不能检查声调，量/率/弥少 的读音还需要人耳确认；pyin 的音高估计偶尔会跳八度，“音高起伏”只能粗略参考；我没有用耳朵听过。

## Permanent rule: 量 is read liáng (2nd tone)
- 量 used as a verb (量一量, 量周长, 测量, 我量了一下, 量总有误差 meaning "measuring always has error") is read **liáng, 2nd tone**. Only the noun sense (数量, 质量, 大量) is liàng, 4th tone.
- Whisper ignores tones, so ASR cannot catch this. Every 量 sentence gets a pitch check: `scripts/tone_dtw.py <sid> <takes>`.
  - Synthesize same-voice controls in the same sentence position: 梁 (liáng) as `c2a`/`c2b-<sid>` and 亮 (liàng) as `c4a`/`c4b-<sid>`.
  - Compare the pyin pitch contour of 量 (window: syllable −0.15 s to +0.25 s, semitones) against the controls with DTW. Keep a take only if it is closer to 梁.
  - A plain rise/fall slope check is unreliable here. Sentence-final declination and neighbouring tones (我量了, 量一量) fool it.
- Forcing liáng:
  - Use Fish phoneme tags in the TTS text: `<|phoneme_start|>liang2<|phoneme_end|>`. Run `scripts/fixtags.py` on the timestamp JSON afterwards, so the tag tokens collapse back into 量.
  - If that is not enough, substitute the homophone 粮 or 梁 in the TTS text only. Subtitles and timestamps keep 量.
- 2026-10-15:
  - Sentence 1 → lc-01 (phoneme tag).
  - Sentence 5 → pa-05 (TTS 粮一粮).
  - Sentence 15 → lb-15 (phoneme tag).
  - Without a prompt, ASR now hears 凉/良 (liáng). Pinyin error 0 for all three.
