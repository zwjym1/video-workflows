# 可导入知识 / 案例 vs 仅工具（建议清单）

核验日期：2026-11-16 Asia/Shanghai。依据同目录 `github_resources.json` 与 `GITHUB_RESOURCES.md`。本清单只给合并建议，不执行安装、不跑模型、不下载整库、不创建仓库。

**先说结论：** 本轮核验的8个项目中，没有能直接充当完整教练教材的；这不是穷尽GitHub后的结论。知识卡里的阵型原则、训练组织、以及面向普通人的讲解框架，应来自主线的 FIFA / UEFA / 官方教练资料。下面只列出本次核验后，真正值得引用或以后按需使用的材料，并标清不能怎么用。

## A. 可导入的知识或规范（术语、标注、方法论口径）

这些可以写进知识库的「术语 / 方法」层，但必须标注出处与局限，且不能冒充教练教材。

| 材料 | 用什么 | 导入时要注意 |
| --- | --- | --- |
| [hudl/open-data 事件与 360 等规格 PDF](https://github.com/hudl/open-data/tree/master/doc) | 事件类型、360 冻结画面字段、阵容与比赛元数据定义 | 这是标注规范，不是战术课。360 ≠ 全程 tracking。数据本身另有用户协议。 |
| [Metrica events-definitions.pdf](https://github.com/metrica-sports/sample-data/blob/master/documentation/events-definitions.pdf) | 样本事件类型定义 | 只对应该样本格式。仓库无 LICENSE，规范文本也不要默认再分发。 |
| [socceraction SPADL 定义](https://github.com/ML-KULeuven/socceraction/blob/master/docs/documentation/spadl/SPADL_definitions.rst) 与 [VAEP](https://socceraction.readthedocs.io/en/latest/documentation/valuing_actions/vaep.html)、[xT](https://socceraction.readthedocs.io/en/latest/documentation/valuing_actions/xT.html) 文档 | 「这一脚的价值」用什么语言说清楚 | 软件 MIT；输入数据走原厂协议。向观众必须标明这是研究模型。仓库 README 写明非积极开发。 |
| [LaurieOnTracking Tutorial3 / Tutorial4](https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking) 中对 pitch control 与 EPV 的说明 | 从控球讲到「空间是否可接应」的分析概念 | 代码 MIT，默认分支已停滞（最新默认分支提交 2021-06-15 16:40 Asia/Shanghai）。配套讲座与 Metrica 数据版权分开。必须标明概率模型。 |

不要导入：Soccermatics 原书正文、Friends of Tracking 视频成片、SoccerNet 视频、任何仓库里附带的赛事画面。也不要把 mplsoccer gallery 的「Juego de Posición」分区图当成位置打法理论。

## B. 可引用的可验证案例（按场次、按需，不整库搬运）

| 材料 | 适合支撑什么讲解 | 不能怎么用 |
| --- | --- | --- |
| [hudl/open-data](https://github.com/hudl/open-data) 中与主题对应的公开比赛事件 | 「这一脚传球 / 射门 / 压力事件实际发生了什么」 | 不是全程无球 tracking。不得再分发原始 JSON。LICENSE.pdf（2023-09-08 文本）禁止商业利用数据或衍生分析；公开引用须用 StatsBomb logo 署名。代码工具的 MIT 覆盖不到这份数据。 |
| [metrica-sports/sample-data](https://github.com/metrica-sports/sample-data) 少数匿名场次的同步 tracking + event | 无球跑位、队形、球场控制示意 | 只有几场，不能外推为联赛规律。无标准许可证，公开使用须致谢来源，不要默认打包进对外分发的知识库。 |

若讲解必须展示空间，优先用 Metrica 样本，而不是把 StatsBomb 事件或 360 冻结画面说成 22 人跟踪。SkillCorner/opendata、Last-Row 仅作指针：前者本次未完整核验许可，后者无 LICENSE，均不建议导入。

## C. 仅工具（不要写进「知识来源」）

这些提高专业观感或以后做图时有用，但本身不是知识库条目。

| 工具 | 以后可能的用途 | 边界 |
| --- | --- | --- |
| [PySport/kloppy](https://github.com/PySport/kloppy) | 统一读取事件 / tracking、改坐标系 | BSD-3-Clause 只管软件。默认分支仍在维护（最新提交 2026-11-06 19:59 Asia/Shanghai，该笔为依赖更新）。本次不安装。 |
| [andrewRowlinson/mplsoccer](https://github.com/andrewRowlinson/mplsoccer) | 规范球场图、传球网络、热区、360 / 射门冻结画面 | MIT 只管绘图库。默认分支 `main`，changelog 用 [CHANGELOG.md](https://github.com/andrewRowlinson/mplsoccer/blob/main/CHANGELOG.md)。加载公开数据仍受数据协议约束。 |
| socceraction **作为程序** | SPADL 转换、计算 VAEP / xT | 与 A 中文档分开：程序是工具，文档才是可引用方法论。 |
| [SoccerNet/SoccerNet](https://github.com/SoccerNet/SoccerNet) | 仅当需要视频层 CV 标注时的下载入口 | MIT 只管软件包。部分数据 gated / NDA。不是战术教材。本次不申请、不下载。 |
| SoccermaticsForPython **作为脚本** | 入门传球 / 射门 / xG 图的对照实现 | MIT 只管脚本，默认分支停滞（2021-03-13 15:38 Asia/Shanghai）。书与数据另计。 |

战术板类绘图应用（搜索命中的 board / studio 项目）一律视为界面工具，不进入知识来源，也不为凑数列入主项目。

## D. 合并进统一知识库时的推荐顺序

1. 主线放入官方教练理论与面向普通人的讲解框架。
2. 用 A 的规格和方法论文档，给术语和「价值 / 空间」说法加可核对定义，并写清模型局限。
3. 用 B 的少量案例给具体镜头做证据，先过许可（尤其是 StatsBomb 禁止商业利用衍生分析、禁止再分发）。
4. 需要出图时再用 C，且图上的数据来源与许可与 B 一致。
5. 不要新建 GitHub 仓库去「拼一个开源战术 KB」，也不要把本目录写成独立对外入口；交给主线合并为一个统一知识库入口。
