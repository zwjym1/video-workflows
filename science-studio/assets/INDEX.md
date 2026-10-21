# 资产与规范索引（只指向，不复制）

## 现有 Skill（由新总入口路由调用）
| Skill | 路径 | 新系统里的角色 |
|---|---|---|
| douyin-field-collect | /home/box/agent-data/workflows/douyin-field-collect/SKILL.md（脚本 /workspace/skill_pkg/douyin-field-collect/scripts） | 阶段 A 采集（唯一采集入口） |
| skill-1792258671706 科技短视频前期调研与核查（选题闸门） | /home/box/agent-data/workflows/skill-1792258671706/SKILL.md | 阶段 A/B 的事实表、素材溯源、红线参考；其中「抖音权重 40%」「通政使交包为硬门槛」「万能壳禁令」已废止 |
| skill-1792258650910 科普短视频（猫学长 2D Remotion） | /home/box/agent-data/workflows/skill-1792258650910/SKILL.md | 阶段 D–F 的 2D 制作方法（时间戳驱动、分区防遮挡、5 帧布局检查、审核图集、PC 渲染）；§2 钩子公式、§3 句式要求、§5 逐句配音已废止 |
| skill-1792258664507 小学讲题课程视频 | /home/box/agent-data/workflows/skill-1792258664507/SKILL.md | 讲题/课程类选题时替代猫学长路线 |
| GitHub 仓库 video-workflows | /workspace/video-workflows（= /workspace/vw 副本），最新 97923ab | 上述 skill 的版本存档、两套模板 workflows/hot-science-roadster、ai-debunk-iphone |

## 文档
| 文档 | 路径 | 状态 |
|---|---|---|
| 选题采集系统 v2 | /workspace/topics/workflow/选题采集系统_v2.md | 部分有效：S1 热榜初筛、字段状态写法可参考；**打分权重、通政使分工、日更两更硬规则 → 已废止** |
| 选题采集·抖音实地硬规则 2026-10-20 | /workspace/topics/workflow/选题采集_抖音实地硬规则_2026-10-20.md | **已废止**（权重、分工、加厚标准）；采集改由 douyin-field-collect 执行 |
| 实地包模板 | /workspace/topics/workflow/field_douyin.template.md | 可作 A 阶段报告格式参考，非强制 |
| 前期制作工作流 | /workspace/topics/workflow/preproduction_workflow.md | 参考（S4 事实表、S5 素材溯源、S6 红线仍有用）；S1.5 硬门槛、时长预算 → 已废止 |
| 文案系统 v2 | /workspace/topics/workflow/文案系统_v2.md | **已废止为规则**（「本条声音」、万能壳/句式禁令、对标开头结构），仅作经验参考 |
| 口播自检清单 | /workspace/topics/workflow/口播_自检清单.md | **已废止为闸门**（B 段万能壳整段重写等）；E 红线可参考 |
| 配乐规则 / 上头曲库 | /workspace/research/bgm_配乐规则_科普竖屏_20261020.md、bgm_上头曲库_科普_20261020.md、bgm_素材库_20261019.* | **规则已废止**；曲库可作选曲素材（核授权） |
| 运营系统 | /workspace/douyin-growth/运营系统.md、checklists/ | 参考；发布动作仍需用户批准 |
| 配音配置 | /workspace/video-workflows/docs/VOICE-CONFIG.md | 有效（音色 ID 与调用） |
| 方向纠偏 | /workspace/topics/direction_reset_2026-10-20.md | 历史记录 |

## 品牌
- /workspace/brand/v2/：README.md（规范）、avatar_1_朱印丞.png（**全片角标**）、fonts/（得意黑、思源）、cover_template_16x9_blank.png、qban/（Q 版小官、贴纸 思考/惊讶/点赞/盖章、poses/、transparent/）。
- /workspace/brand/deliver/品牌/：已发封面（Roadster、iPhone）。

## 可复用 Remotion 工程（盒上已装 node_modules，Remotion 4.0.536）
| 工程 | 用途参考 |
|---|---|
| /workspace/optogenetics/remotion | 最新 2D 科普（字幕卡、印章、时间戳驱动；EP-20261021-01 定稿工程，复制使用，勿改原件） |
| /workspace/zhangxue-water/remotion | 2D + @remotion/three 3D 竖屏；2026-10-20 环境实测用它渲 1 s |
| /workspace/canton-robot/remotion | 实拍+动画竖屏 |
| /workspace/iphone-fake/v2/remotion | 截图证据+贴纸+小官 |
| /workspace/roadster-downforce/remotion、rv1 | 物理示意 |
| /workspace/topics/tesla-roadster/remotion | 横屏 B 站 |
| /workspace/pi/remotion | 小学课程 |
| /workspace/video-workflows/projects/gradient-descent | 科普样例 |
新一期：复制最接近的工程源码（不含 node_modules，可软链 node_modules）到 `projects/<EP>/remotion/`。

## 工具
| 工具 | 路径 |
|---|---|
| 看视频（链接/本地 → 元数据、逐字稿、拼图、评论） | /workspace/tools/watch.py |
| qoder 批量看片 | /workspace/tools/qoder_job.sh |
| Fish TTS 合成+时间戳 | /workspace/zhangxue-water/vo/fish.py（synth） |
| ASR 重转 | /workspace/tools/reasr.py |
| 超分 / 人脸检测模型 | /workspace/models/（RealESRGAN_x4plus、yunet） |
| PC 参数化渲染脚本（现行模板） | /workspace/optogenetics/pc_pack/render_film_pc.ps1（-Mode 720/1080/both，-Frames 单段）|
| 旧 PC 渲染脚本（已被上行替代） | /workspace/optogenetics/pc_pack/render_pc.ps1、/workspace/pcsync/render_v3.ps1 |

## 3D
- 盒上无 Blender、无 GPU；3D 目前只有 Remotion @remotion/three（zhangxue-water 有实例）。
- 用户 PC 是否有 Blender 工程/模型：**待用户告知路径**。

## 可检索索引
上面所列工程、组件、Commons 实拍、品牌素材、音效（含 Mixkit 授权）都已登记进 `db/studio.db`（anim_assets/bgm），可用 `python3 scripts/search.py q "<描述>" --lib asset` 或 `search.py bgm "<感觉>"` 查找。
