# 观众版 EDL

装配命令：

```bash
python -m refined_v2.film \
  --episode episodes/bayern-20200814-mueller-open-lock-draft \
  --edl episodes/bayern-20200814-mueller-open-lock-draft/audience_example.edl.json \
  --source /path/to/720p-proxy.mp4 \
  --out demo/audience-example.mp4 \
  --qc demo/audience-qc
```

`master` 必须缺省或为 false。`output.fps` 是成片时钟，板的每一帧按这个时钟现画，不用 25fps 成片去硬套 30fps。源片小于输出尺寸时拒绝放大。`1920x1080` 只有在源片本身达到这个尺寸时才允许，板从超采样缓冲缩到 1080p，不是把 720p 成片拉大。1920×1080 只说明文件尺寸，不是无压缩广播母带。

镜头 `kind` 为 `live` 或 `board`。`live` 用源片时间 `src_in`/`src_out`。`board` 用板上的 `t0`/`t1`，板号必须在场次包里。回到实拍用 `dissolve_frames` 4、5 或 6，不另做特效。

字幕来自 `captions`，是已经写好的句子。本工具不调用配音。没有音轨就是静音。字幕不能写「无号码」「25号」或内部核验戳。1080p 底边留白超过 60px，720p 按同一比例。

示例 EDL 的字幕是样例，不是最终旁白。赛报可以在叙述里说进球人是穆勒，射门画面上不标 25。
