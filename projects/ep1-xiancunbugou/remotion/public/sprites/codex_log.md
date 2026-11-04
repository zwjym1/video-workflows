# codex_log.md — T09 像素素材

工具：codex exec -m gpt-6-luna 内置 image_gen，3 路并行（props1/props2/chars），-i keyframes_vllm_1.jpg。
取图：从各自 log 中的 session id 定位 ~/.codex/generated_images/<session>/ 最新 PNG（不取全局最新）。
来源：
- props1: /home/box/.codex/generated_images/01a1a227-35d7-7861-bfe0-ad1f66c30c37/exec-c4cbcbce-5f20-4541-8236-51e5f19d3acd.png
- props2: /home/box/.codex/generated_images/01a1a227-35d7-7ee3-a438-4c99e1fdd397/exec-0a08ef60-1a50-436f-85cf-61c3ff4f0a54.png
- chars: /home/box/.codex/generated_images/01a1a227-35d7-7252-bf6a-416ac7fe283e/exec-9761c7b3-f2ef-4733-8a6d-9922610ed4e1.png

后处理（_sprite_work/post.py）：洋红抠图→连通域切分→每个原始像素先量化到色板(6 基色+明暗阶共18色)→按目标格子取众数(mode)下采样→alpha 半数阈值→最近邻放大(≥24格×16，<24格×32)。
程序生成：matrix_score_grid（AI 版格子不齐，改为脚本画 8×8 热力格）、bg_compute_grid_1920x1080（240×135 格 ×8）。
色板：F6F0E2 D9CFBA FBF7EA 1E1B25 2B2735 3A3546 FF8236 C9601F FFB07A F2C14E B88F2A F8DC8E 65BF62 3F8A3D A3DCA0 F8574C B53A32 FB9A92
格子尺寸(w,h,放大倍数)：
- props1_count: 4
- gpu_card: [32, 21, 16]
- server_rack: [18, 32, 16]
- gpu_row: [48, 11, 16]
- question_block: [16, 16, 32]
- props2_count: 6
- warehouse_hbm: [32, 22, 16]
- workbench_sram: [24, 19, 16]
- matrix_score_grid: [27, 27, 16]
- token_q_orange: [16, 16, 32]
- token_k_green: [16, 16, 32]
- token_v_gold: [16, 16, 32]
- chars_count: 3
- hero_stand: [21, 48, 16]
- hero_point: [31, 48, 16]
- hero_think: [19, 48, 16]

## props1 prompt
Use case: game-sprite-sheet
Asset type: one raster sprite sheet
Primary request: Create a 2x2 layout of four separate pixel sprites. Top-left: a side-view graphics card (GPU), dark body, two round cooling fans, gold connector teeth along the bottom edge, and an orange accent stripe. Top-right: a tall dark server rack cabinet with stacked units and tiny green and orange status LED pixels. Bottom-left: one long connected strip showing a row of four identical small graphics cards side by side, touching each other. Bottom-right: a golden question-mark block like a classic game item block, with darker gold edges and a cream question-mark shape.
Scene/backdrop: perfectly flat pure magenta #FF00FF across the entire image, with no ground or shadows. Four sprites separated by large magenta gaps; objects never touch except the four cards in the bottom-left connected strip.
Style/medium: clean retro 16-bit pixel art sprites with a cream-and-dark pixel infographic, pixel-debug look; crisp large square pixels, each sprite drawn on a coarse grid of roughly 16-32 pixels across; solid 1-pixel dark outline #1E1B25; flat fills; at most one highlight and one shadow tone per color; absolutely no anti-aliasing, gradients, soft shadows, or glow.
Composition/framing: clear, balanced 2x2 grid, all four sprites fully visible and distinct.
Color palette: strictly limited to cream #F6F0E2, dark #1E1B25, lighter dark grey-purple #3A3546, orange #FF8236, golden yellow #F2C14E, green #65BF62, red #F8574C, and pure magenta #FF00FF background only.
Text (verbatim): none. The sole symbol permitted is the cream question-mark shape on the bottom-right block.
Constraints: no text, letters, numbers, other symbols, logos, labels, or watermark anywhere. Do not introduce any colors outside the specified palette.
Avoid: texture, noise, dithering, anti-aliasing, gradients, transparency, shadows, glow, extra objects, overlapping sprites, framing elements.


## props2 prompt
Create ONE image: a 3-column by 2-row sprite sheet, six separate retro 16-bit pixel art sprites, all fully visible, centered in their own grid cells with large perfectly flat pure magenta #FF00FF gaps between objects and around the edges. Strictly crisp chunky square pixels on a coarse grid (each object constructed from roughly 16–32 pixels across), solid dark outline #1E1B25, flat fills, at most one highlight and one shadow tone per color. No anti-aliasing, no gradients, no soft shadows, no glow. Use only this palette: cream #F6F0E2, dark #1E1B25, dark grey-purple #3A3546, orange #FF8236, golden yellow #F2C14E, green #65BF62, red #F8574C, plus the required pure magenta background #FF00FF. Background must be uniformly pure magenta with no floor or ground shadow. Objects never touch. Do not include any text, letters, numbers, symbols, logos, labels or decoration; only the described sprite shapes. Top-left: a large wide warehouse building, viewed straight on, with cream walls, dark outline, simple roof and one prominent orange roll-up door, conveying a huge distant structure. Top-middle: a small compact handy workbench desk, golden yellow top, dark legs, with a few tiny tools on top including one green tool. Top-right: a square 8 by 8 matrix scoring grid inside a dark frame, exactly 64 small square cells, varied cream, orange and golden yellow fills arranged like a heatmap. Bottom row: three separate small square token cubes, identical rounded pixel-square shape, dark outline, blank faces, each with a single 1-pixel highlight; left cube orange, middle cube green, right cube golden yellow. Keep the sprites distinct and visually balanced in their respective 3x2 cells.


## chars prompt
Create ONE image: a clean retro 16-bit pixel art sprite sheet, with exactly THREE full-body poses of the SAME original male university student character arranged side by side in one horizontal row, evenly spaced with large gaps. Each sprite is about 24 coarse square pixels wide by 32 pixels tall, front 3/4 view, same scale, same face and outfit. He has short dark hair, round glasses, simple dot eyes, a cream hoodie with orange accents, and dark trousers. LEFT pose: standing neutrally. MIDDLE pose: pointing to the right with one arm extended. RIGHT pose: thinking, one hand on chin. Crisp large square pixels, coarse grid, solid one-pixel dark outline #1E1B25, flat fills, at most one highlight and one shadow tone per color, no anti-aliasing, no gradients, no soft shadows, no glow. Strict palette only: cream #F6F0E2, dark #1E1B25, slightly lighter dark grey-purple #3A3546, orange #FF8236, golden yellow #F2C14E, green #65BF62, red #F8574C, and background pure magenta #FF00FF. Background must be perfectly flat pure magenta everywhere, no ground or shadow. Objects never touch; generous magenta gaps around and between all three poses. No text, letters, numbers, symbols, logos, or other marks. Original design; do not copy any reference character.



## v2 重画（4 张，3 路并行）
- gpu session: session id: 01a1a22f-dbae-7a52-b9d6-6c212a987fa3
- wh session: session id: 01a1a22f-dbb1-7da3-960c-695ad2006c05
- hero session: session id: 01a1a22f-dbaf-7470-8494-e9ffcca4b8f9
后处理：_sprite_work_v2/post2.py（72格/人物80格高，mode 下采样，边界亮像素强制 #1E1B25 描边，×8 放大；hero 发中绿色杂点替换为 #3A3546）。逐张核对通过，未重跑。
### gpu prompt
Create ONE image only: a single graphics card (GPU) sprite seen from the side, centered and fully in frame. Detailed retro PIXEL ART, crisp square pixels, sprite drawn on a grid of about 64–80 pixels across with fine detail. NO anti-aliasing, NO gradients, NO glow. One continuous solid dark outline #1E1B25 all around the GPU (never a light/cream outline), plus pixel bevel: 1-pixel lighter highlight on top/left inner edges and 1-pixel darker shade on bottom/right inner edges. Strict palette only: cream #F6F0E2, dark #1E1B25, dark grey-purple #2B2735 and #3A3546, orange #FF8236 (shade #C9601F, light #FFB07A), golden #F2C14E (shade #B88F2A, light #F8DC8E), green #65BF62 (shade #3F8A3D), red #F8574C. Background perfectly flat pure magenta #FF00FF, no ground shadow, no floor. No text, letters, numbers, logos, extra objects, or decorative elements. GPU content: dark grey-purple body with TWO large round cooling fans, each showing exactly 7 curved blades, a hub cap, and fan ring rim with pixel highlight; visible heatsink fin lines between the fans; orange accent stripe along the top; gold PCIe connector teeth along the bottom edge; small bracket at left side in dark grey with dark outline, no cream specks on the left edge. Make the full silhouette clearly separated from the magenta background, no cropping. Preserve chunky square pixel geometry throughout.
### wh prompt
Single pixel art warehouse sprite, cream building dark outlined, grey pitched roof, orange striped roll-up door, open right side with shelves and golden/orange boxes, small windows, magenta flat background, crisp square pixels, no text.
### hero prompt
Create ONE horizontal sprite sheet image with exactly two full-body poses of the same original male university student, side by side with a wide gap. Left pose thinking, hand on chin and other arm across body. Right pose pointing right with one arm extended horizontally at natural length, other hand relaxed. Same face, outfit, height. Front 3/4 view, short messy dark hair, clearly visible round black glasses with two round rims, bridge, eyes visible inside. Cream hoodie, orange drawstrings and cuffs, dark trousers, orange-and-cream sneakers, no backpack. Retro detailed pixel art, crisp square pixels, no anti-aliasing, gradients or glow. Continuous solid dark outline #1E1B25, pixel bevel with lighter top/left inner edges and darker bottom/right. Palette only: #F6F0E2 #1E1B25 #2B2735 #3A3546 #FF8236 #C9601F #FFB07A #F2C14E #B88F2A #F8DC8E #65BF62 #3F8A3D #F8574C. Flat pure magenta background #FF00FF, no shadows or floor. Two sprites approx 48x80 pixels. No text or logos.
