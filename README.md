# 视频工作流（video-workflows）

赵伟健的两套 AI 视频制作工作流，以及示例项目。

## 两条路线
1. **科普短视频**（`skills/kepu-short-video/`）：浙大学长风格的竖屏科普短视频，选题 → 钩子 → 文案 → 分镜 → 配音 → 渲染。
2. **小学讲题课程视频**（`skills/primary-lesson-video/`）：给小学生讲知识点的横屏课程视频，强调童趣画风、准确读音和逐句核对。

两套技能规则互相独立，互不影响。

## 目录结构
```
skills/
  kepu-short-video/SKILL.md        科普短视频技能
  primary-lesson-video/SKILL.md    小学讲题课程视频技能
projects/
  pi-lesson/                       示例：圆周率 π 小学课程视频
    step3-script-final.md          定稿文案
    step4-storyboard.md            分镜与视觉方案
    assets/SOURCES.md              素材来源
    style-frames/                  效果图及生成脚本 make.py
    remotion/                      Remotion 源码（WINDOWS-RENDER.md 为渲染指南）
    voice/                         配音记录和脚本
  gradient-descent/                科普示例：梯度下降 v4 源码和配音脚本
docs/VOICE-CONFIG.md               配音（Fish TTS）音色 ID 和配置教程
VERSIONS.md                        版本标签和回退方法
.env.example                       环境变量模板（只有占位符）
```

成片视频和大体积素材未入库；密钥只放环境变量，不入库。
