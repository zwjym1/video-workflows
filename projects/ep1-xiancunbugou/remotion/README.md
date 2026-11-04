# T09 像素信息图复刻工程（原型，只出静帧，不渲染成片）
预览：在本目录运行 `npx remotion studio src/index.ts`。
出静帧：`npx remotion still src/index.ts K1 out/K1.png --frame=80`。
node_modules 是软链接，指向 T08 工程（Remotion 4.0.538）。

## 复用来源
| 来源 | 许可证 | 复用了什么 |
|---|---|---|
| [Azure12355/weilanx-claude-videos](https://github.com/Azure12355/weilanx-claude-videos) | MIT | `src/lib/cues.ts`（按 SRT 句号对齐帧：cf/ce/cw）、`src/lib/anim.ts`（缓动与 rand）、`src/lib/PixelBuddy.tsx`、`types.ts`、`Accessories.tsx`（像素小人）。`theme.ts` 精简成只剩色板。整仓库在 `../methods/weilanx-claude-videos`，它的 `weilanx-creator-distill-video` 和 `pixel-video` 两个 skill 可以当方法参考 |
| [TakWolf/fusion-pixel-font](https://github.com/TakWolf/fusion-pixel-font) 2026.10.25 | OFL-1.1（见 `public/fonts/OFL.txt`） | 12px 中文像素字体 |
| 自制 | — | `src/kit.tsx`：米白点阵底、星空底、取景框+进度条+HUD、短语字幕、积木弹入 Pop、Label、Token、像素 GPU、问号方块；`src/Root.tsx`：K1–K4 四个分镜 |

HUD 上的名字是账号名“显存不够”。角色是 PixelBuddy 青绿色加眼镜，不是对标的角色。

## v2（11-04 00:1x）
- 新增 `src/sprites.tsx`，自制像素道具库，按格逐个着色：GpuSprite 32×14（风扇叶片随帧转）、RackSprite 16×32（LED 闪烁）、WarehouseSprite 32×24、BenchSprite 24×14、BoltSprite、ClockSprite、KidSprite 16×20（自制角色，戴耳机和眼镜、穿卫衣，会眨眼、会挥手）、Cell（带倒角的格子）、NeuralNet、Dust。
- `kit.tsx` 新增 DarkGridBg（#2A2733 底，#34303F 网格线，82px 一格），K4 改用这个底。
- 静帧：`out/K*_v2.png`。

## 素材接口（v3，codex 出图）
- 用法：`<Sprite name="gpu" w={352} />`，背景用 `<SpriteBg name="bg_dark_grid" fallback={<DarkGridBg/>} />`（`src/Sprite.tsx`）。
- 找 PNG 的规则：如果存在 `public/sprites/<name>.png`，就加载它，按宽度 w 等比缩放，用 `image-rendering: pixelated` 保持硬边；没有这张图就回落到 `sprites.tsx` 里的代码占位。不认识的名字会显示橙色虚线框，框里写着文件名。
- 场景里现在用到的文件名：`gpu`、`rack`、`warehouse`、`bench`、`bolt`、`kid`、`kid_wave`、`bg_paper`、`bg_dark_grid`，都是透明底 PNG，背景图建议 1920×1080。
- 显示宽度（1920 画布）：gpu 352 / 96（小图标）、rack 96、warehouse 448、bench 312、bolt 56、kid 96–128。
- 已验证：放一张 gpu.png 进去，渲染时会被加载；删掉后自动回落到占位。
