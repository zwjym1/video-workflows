# 录屏链路（「让 AI 动手」所有期通用）· 2026-11-02 (UTC+8)

## 0. 先决定这一镜要不要录
只录「真东西比手绘更有说服力」的：真实产品界面、官方原话或数据页、真实的光标和点击、授权弹窗。比喻、痛点、金句这些镜头还是手绘。全片录屏尽量 ≤30%–40%。每期写一份 `<ep>/screen_record_plan.md`，表格格式是 `| 编号 | 镜(逗号分隔) | A/B | 录什么 | 时长 | 合成 |`，`tools/review_table.py` 会读这张表，自动填「录屏?」一列。

## 1. 谁来录
- **A 盒子（我）**：Linux 桌面 DISPLAY=:5（屏幕 1920×1200）。浏览器或智能体在桌面上操作，`record_box.sh` 用 ffmpeg x11grab 录 1920×1080 / 30fps / H.264 CRF18，同时每 50 ms 记一次光标坐标（`.cursor.tsv`）。只用公开网页和本地布景页，不登录用户的账号。
- **B 用户电脑**：凡是需要你账号的应用（Copilot app / Cursor / ChatGPT·Codex 的 Computer Use）都在这类。OBS：显示器采集，1920×1080，30fps，录鼠标，mp4 格式；或者 Win+Alt+R。录之前关通知、用测试数据，录完交给我（CopyToBox → `<ep>/rec/`）。

## 2. 盒子录制命令
```bash
S=/workspace/science-studio/tools/screen_record/record_box.sh
bash $S once  <ep_dir> <名字> <秒>        # 定时录
bash $S start <ep_dir> <名字>             # 开始（后台）
bash $S stop  <ep_dir> <名字>             # 停止
OFF=0,60 SIZE=1920x1080 bash $S once ...  # 指定录制区域（例如跳过顶栏）
```
输出：`<ep>/rec/<名字>.mp4` + `<名字>.cursor.tsv`（时间戳、X、Y）。注意要用 `bash` 调用（这个目录挂载时禁止直接执行脚本，所以 `./record_box.sh` 会报“权限不够”）。点击时间不在 tsv 里，从智能体的操作日志或布景页的 console 里取。

## 3. 布景页（A 类常用）
在 `<ep>/rec/stage/` 下放本地 HTML（仿表单、带「翻车模式」：按钮漂移、广告弹窗），在浏览器里用 `file://` 打开，让智能体真的去操作它。这样画面是真的，又不碰任何账号或隐私。

## 4. 合成（ffmpeg，统一 1920×1080 30fps）
1. 裁剪：`crop=W:H:X:Y` 去掉浏览器地址栏和任务栏 → `scale` 缩到版式区域（R 版式左侧 65%，约 1180×700）。
2. 窗口框：圆角白边 + 标题栏贴图（和 keyframes 里的 win() 同款），倾斜 −3° 到 2°。
3. 放大：放大到原文或按钮，`zoompan` 或 `crop+scale` 用表达式在 0.25 s 里拉到 1.4–1.6 倍；放大冲击只用在痛点和反转句。
4. 光标强调：读 `.cursor.tsv` 拿到点击时刻和坐标，叠 `assets/fx_lib/clips/click_ripple.webm` 或 `cursor_click.webm`（overlay，`enable=between(t,a,b)`，坐标要换算到版式区域里）。
5. 节奏：录屏可以 1.25 到 1.5 倍速；每 3–4 s 必须有一次画面变化（高亮、放大或弹出元素），不然审核表会标「无画面变化」。
6. 字幕最后叠，与 EP1 v5 `build_video.sh` 相同。

## 5. 审核
`python3 tools/review_table.py <ep> --risk ...` → 表里多一列「录屏?」（A / B / —），用户按表一次过审。
