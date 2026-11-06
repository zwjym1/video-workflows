# opto_film_v1 PC 渲染包

短片不走这个包。2026-10-29 起，约 60 秒及以内的片子在盒子上渲，只把成片和两张封面传到 `发布\`。下面是光遗传学长片用的 PC 包。
- opto_film_v1_src.zip（31.8MB）：remotion 工程（src 去 .bak、public、package.json+package-lock.json 锁版本 4.0.536、PC 版 remotion.config.ts）+ audio/film_mix_v1.wav + render_film_pc.ps1
- render_film_pc.ps1：放在 zip 同目录运行。默认 1080（H.264 High ~14Mbps，AAC 320k）；-Mode 720 / both；-Frames a-b 按段返修；-Force 重渲。
- 段帧区间：hook 0-443 | seg2 444-1430 | seg3 1431-2254 | seg4 2255-3457 | seg5 3458-4327 | seg6 4328-5245
- 音频来源：audio/film_mix.py（/workspace/.venv-dy/bin/python），接缝检查 audio/film/join_check.txt
