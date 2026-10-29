# PC 传输步骤（PC 上线后执行；只新建、不删除、不碰仓库）
版本：v6h 最终版（2026-10-29 05:00 UTC+8 重切；成片 26428493 字节，4 块）。
约定：$w = D:\编程\项目\视频制作\作品\2026-10-29_火箭水母云 ，$d = $w\发布
目标：D:\编程\项目\视频制作\作品\2026-10-29_火箭水母云\发布\
1. PC: New-Item -ItemType Directory -Force "D:\编程\项目\视频制作\作品\2026-10-29_火箭水母云\out\_parts"
2. CopyFromBox：/workspace/xfer_jelly/part_00..part_03 → out\_parts\part_0N
   两张封面直接复制：/workspace/xfer_jelly/火箭水母云_封面_竖9x16_1080x1920.png、火箭水母云_封面_横4x3_1440x1080.png → 发布\
3. 每块复制后在 PC 上校验 Get-FileHash -Algorithm SHA256，对照 SUMS.txt
4. 合并：$o=[IO.File]::Create("$d\火箭水母云_成片_1080x1920.mp4"); foreach($p in 0..3){$b=[IO.File]::ReadAllBytes("$w\out\_parts\part_0$p");$o.Write($b,0,$b.Length)}; $o.Close()
5. 成片 sha256 应为 ca9c1936d3ced4026d2a6c66c0efbfdf9a104480b6ee0123af82c3c9bdd129a5
6. 校验通过后，分块放在 out\_parts，不进 发布\；发布\ 只有成片+2封面。
