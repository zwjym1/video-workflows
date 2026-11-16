# GitHub 公开足球资源核验报告

核验日期：2026-11-16 Asia/Shanghai（UTC+8）。  
方法：通过 GitHub 官方 API 读取公开仓库的 README、LICENSE、目录与文档，并用默认分支 `list_commits` 核验最新提交时间；不 clone、不安装、不运行模型、不下载整库数据。`hudl/open-data` 的 `LICENSE.pdf` 另行抽取全文。ReadTheDocs 与 kloppy 文档站用公开网页核验可访问。所有提交时间先记录 UTC，再换算为 Asia/Shanghai。

机器可读清单见同目录 `github_resources.json`。导入建议见 `IMPORT_VS_TOOLS.md`。

## 总结论

本轮核验的8个项目中，没有能直接当作完整教练教材的；未穷尽GitHub。公开仓库真正站得住的，是三类东西：

1. 可核验的比赛案例数据，以及事件/360/样本 tracking 的标注规范；
2. 动作估值与空间控制的**研究口径**（SPADL、VAEP、xT、pitch control、EPV），能让讲解更专业，但不是教练课；
3. 把数据读标准、把图画得像专业分析片的工具。

因此：**战术理论、训练原则、以及「教普通人看懂」的课程结构，应主要来自主线处理的 FIFA / UEFA / 官方教练资料**，不要为了凑一个开源知识库去虚构完美仓库，也不要把 StatsBomb、mplsoccer 或 SoccerNet 写成完整战术教材。

下面 8 个项目都是本次实际核验过、链接可打开、许可条款读过原文的。线索里提到的 Friends-of-Tracking、socceraction、kloppy、StatsBomb/open-data、mplsoccer 均存在，但用途边界必须分开写。

## 这些材料怎样提高解释的专业性

面向普通观众、又要看起来专业，GitHub 资源的价值不在「把理论抄进知识库」，而在三处约束：

- **术语可核对。** StatsBomb 事件规格、Metrica 事件定义、SPADL 动作类型，能把「压迫、接应、直塞」对到可复查的事件字段，减少口头发明。
- **画面有证据。** 用公开比赛事件，或 Metrica 少数场同步 tracking，支撑「这一脚发生了什么」，而不是只画抽象阵型。需要讲无球跑位或空间时，应优先用 tracking 样本，而不是把事件库说成 22 人全程跟踪。
- **图符合专业视觉语法。** mplsoccer 的球场、传球网络、射门冻结画面、360 示意图，能把职责和跑位画成观众一眼能看懂的板。socceraction / LaurieOnTracking 提供 xT、VAEP、球场控制等可引用的分析语言，但必须标明这是模型估计。

## 证据与使用限制（必须一起告诉观众或写进知识卡）

- 事件数据记录的是有球动作和部分上下文，**不是** 22 人全程无球 tracking。
- StatsBomb 360 是事件时刻的冻结画面，**不能**当成全场跟踪。
- Metrica 样本只有少数匿名场次，不能外推为联赛或某俱乐部规律。
- xT、VAEP、EPV、pitch control 都是分析模型，受数据定义和样本限制，不是官方战术评价。
- Friends of Tracking 教程代码的默认分支已多年无实质更新。
- 开源代码许可证**不自动覆盖**教材、视频或数据集。
- StatsBomb 公开数据受《Public Data User Agreement》（LICENSE.pdf，文末标注 last updated 8 September 2023）约束：不得向第三方分发原始数据；**不得商业利用该数据或由此产生的分析**；公开引用须署名并使用 StatsBomb logo。这对面向观众的内容尤其关键，不能只看「数据在 GitHub 上」。
- SoccerNet 的 MIT 只管软件包；部分视频与标注需登录审批或 NDA。

## 已核验项目

分类约定（每条只归一类主标签，socceraction / LaurieOnTracking / Soccermatics 在文中说明其「方法论」副标签）：

- **可验证案例数据**
- **分析工具 + 部分方法论**（不是教练课程）
- **仅绘图 / 统计 / 数据工具**

### 1. hudl/open-data — 可验证案例数据（兼事件标注规范）

- 仓库：https://github.com/hudl/open-data  
  旧地址 https://github.com/statsbomb/open-data 本次用 API 查询，返回同一仓库。
- 作者 / 组织：Hudl。数据品牌与用户协议主体为 StatsBomb / StatsBomb Services Ltd（英格兰及威尔士公司编号 10377735）。
- 许可：GitHub SPDX 为 `NOASSERTION`。实际文件是 https://github.com/hudl/open-data/blob/master/LICENSE.pdf ，标题 **StatsBomb Public Data User Agreement**，不是 MIT/Apache。条款要点：允许用于分析与研究；禁止向第三方分发、复制、出售数据；禁止商业利用数据或衍生分析；公开发布须使用 StatsBomb 品牌 logo；协议中的仓库地址仍写 statsbomb/open-data；建议在 https://statsbomb.com/resource-centre/ 登记。知识产权归 StatsBomb。
- 主要内容：特定联赛的公开事件、阵容、比赛元数据，以及部分比赛的 360 冻结画面。目录：`data/competitions.json`、`data/matches/`、`data/events/`、`data/lineups/`、`data/three-sixty/`。
- 实际读到、可打开的文档：
  - https://github.com/hudl/open-data/blob/master/README.md
  - https://github.com/hudl/open-data/blob/master/LICENSE.pdf
  - https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Events%20v4.0.0.pdf
  - https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20360%20Frames%20v1.0.0%20(1).pdf
  - https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Lineups%20v2.0.0.pdf
  - https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Matches%20v3.0.0.pdf
  - https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Competitions%20v2.0.0.pdf
  - https://github.com/hudl/open-data/blob/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf
  - https://github.com/hudl/open-data/blob/master/data/competitions.json
- 对本任务：可导入事件术语和少量可核验案例；不能当教材；不能把 events / 360 说成全程 tracking；不能整库搬运或再分发 JSON。mplsoccer 等工具的 MIT **不覆盖**这批数据。
- 维护（默认分支 master 最新提交，非记忆）：`4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`，2026-09-07 16:27 UTC，即 **2026-09-08 00:27 Asia/Shanghai**，说明为 `chore: add required labels check (#79)`。仓库 `pushed_at` 还有 2026-11-12 的记录，不代表 master 数据本身在 11 月更新。

### 2. metrica-sports/sample-data — 可验证案例数据（少量真正的 tracking）

- 仓库：https://github.com/metrica-sports/sample-data
- 作者 / 组织：Metrica Sports。README 与最新提交联系人署名为 Bruno（bruno@metrica-sports.com）。
- 许可：**根目录无 LICENSE 文件**（GitHub `license` 为 null），不能默认为可自由复用或再分发。条款只写在 README 的 Legal stuff：须负责任使用；若公开使用须 acknowledge the source。数据已匿名化。
- 主要内容：两场 CSV 的同步 tracking + event，另加 Sample Game 3（EPTS FIFA tracking / JSON events）。场地 105×68 米，坐标 0–1，(0,0) 在左上。这是少数公开的、包含全体球员位置轨迹的样本，不能和 StatsBomb 事件库混为一谈。
- 实际读到的文档：
  - https://github.com/metrica-sports/sample-data/blob/master/README.md
  - https://github.com/metrica-sports/sample-data/blob/master/documentation/events-definitions.pdf
  - https://github.com/metrica-sports/sample-data/tree/master/data
- 对本任务：需要讲无球跑位、队形或球场控制时，优先用这份样本。公开使用须致谢。不要假设可以打包进自己的知识库再分发。本次未整库下载。
- 维护：`e706dd506b360d69d9d123d5b8026e7294b13996`，2021-04-15 16:34 UTC，即 **2021-04-16 00:34 Asia/Shanghai**，说明为 Added Sample Game 3。作为样本快照仍是常见出处，但仓库已长期不再更新。

### 3. ML-KULeuven/socceraction — 分析工具 + 部分方法论（不是教练课程）

- 仓库：https://github.com/ML-KULeuven/socceraction
- 作者 / 组织：KU Leuven Machine Learning Research Group（LICENSE.rst 版权人）。相关论文作者包括 Tom Decroos、Lotte Bransen、Jan Van Haaren、Jesse Davis、Maaike Van Roy、Pieter Robberechts。
- 许可：https://github.com/ML-KULeuven/socceraction/blob/master/LICENSE.rst ，MIT，Copyright (c) 2019 KU Leuven Machine Learning Research Group。只覆盖软件和随附文档，**不覆盖**经该库加载的 StatsBomb / Wyscout / Opta 数据。
- 主要内容：把多源事件流转为 SPADL / atomic-SPADL，并实现 xT、VAEP、Atomic-VAEP。README 写明主要用于研究可复现，且 **not actively developed**。
- 实际读到、可打开的文档与示例：
  - https://github.com/ML-KULeuven/socceraction/blob/master/README.md
  - https://socceraction.readthedocs.io/en/latest/（本次网页可访问）
  - https://socceraction.readthedocs.io/en/latest/documentation/spadl/index.html
  - https://github.com/ML-KULeuven/socceraction/blob/master/docs/documentation/spadl/SPADL_definitions.rst
  - https://socceraction.readthedocs.io/en/latest/documentation/valuing_actions/vaep.html
  - https://socceraction.readthedocs.io/en/latest/documentation/valuing_actions/xT.html
  - https://github.com/ML-KULeuven/socceraction/tree/master/public-notebooks
  - https://github.com/ML-KULeuven/socceraction/blob/master/public-notebooks/1-load-and-convert-statsbomb-data.ipynb
- 对本任务：可导入「动作如何被定义和估值」的专业口径。向普通人讲解应先用白话（这脚增加了得分可能），再注明这是公开研究模型。不能用来规定压迫或阵型职责；不要把由 StatsBomb 数据算出的结果做商业分析发布（见数据协议 1.2.2）。本次不安装。
- 维护：默认分支 master 最新提交 `93a1242d46c104889205753accaabadb00c45c6d`，2026-01-07 08:40 UTC，即 **2026-01-07 16:40 Asia/Shanghai**，说明为 `docs: add FAIR acknowledgment`。仓库 2026-10-18 仍有推送，但多在 dependabot / dev 分支，与 README「非积极开发」并不矛盾。

### 4. PySport/kloppy — 仅数据标准化工具

- 仓库：https://github.com/PySport/kloppy  
  文档站：https://kloppy.pysport.org/
- 作者 / 组织：PySport（非营利；LICENSE 版权人 PySport；README 标注 RSIN: 866294211）。
- 许可：https://github.com/PySport/kloppy/blob/master/LICENSE ，BSD-3-Clause，Copyright (c) 2020, PySport。不覆盖各供应商数据。
- 主要内容：把多家事件与 tracking 读入统一模型，做过滤、坐标/朝向变换，导出 DataFrame 或 SportsCode XML。本身不提供战术理论。
- 实际读到的文档：
  - https://github.com/PySport/kloppy/blob/master/README.md
  - https://kloppy.pysport.org/（本次可访问，页上标明 kloppy 3.19.1）
  - https://kloppy.pysport.org/user-guide/loading-data/statsbomb
  - https://kloppy.pysport.org/user-guide/loading-data/metrica
  - https://github.com/PySport/kloppy/tree/master/examples
- 对本任务：以后若要对齐坐标系或读取公开数据做案例图，把它当作读取层。不是知识库。本次不安装、不下载数据。
- 维护：`a9651eba7c4dbbe2d2fc6d4cffb4aea63fadac11`，2026-11-06 11:59 UTC，即 **2026-11-06 19:59 Asia/Shanghai**，说明为 bump ruff（#660）。默认分支仍在维护，但该笔最新提交是依赖更新。

### 5. andrewRowlinson/mplsoccer — 仅绘图工具

- 仓库：https://github.com/andrewRowlinson/mplsoccer
- 作者：Andrew Rowlinson；LICENSE 版权人为 Anmol Durgapal, Andrew Rowlinson（2025）。
- 许可：https://github.com/andrewRowlinson/mplsoccer/blob/main/LICENSE ，MIT。若加载 StatsBomb 公开数据，数据条款另计。
- 主要内容：Matplotlib 球场、雷达/披萨图、热图、传球网络、阵型、Sonar、StatsBomb 360 冻结画面等。gallery 里的「Heatmap Juego de Posición」只是分区画法，不是位置打法教材。
- 实际读到的文档：
  - https://github.com/andrewRowlinson/mplsoccer/blob/main/README.md
  - https://github.com/andrewRowlinson/mplsoccer/blob/main/CHANGELOG.md（默认分支是 **main**；不要用 README 里可能过时的 `blob/master/CHANGELOG.md`）
  - https://mplsoccer.readthedocs.io/
  - https://mplsoccer.readthedocs.io/en/latest/gallery/index.html（本次可访问）
- 对本任务：给观众看的战术板、传球图、热区，优先用这类规范球场图。不能替代教练理论。本次不安装。
- 维护：`150be3f5d891526506a4c35b03256f173a70a14a`，2026-09-14 18:54 UTC，即 **2026-09-15 02:54 Asia/Shanghai**，说明为 changelog。CHANGELOG 顶部版本为 1.8.1。仓库 `pushed_at` 另有 2026-10-27 记录。

### 6. Friends-of-Tracking-Data-FoTD/LaurieOnTracking — 教学代码 + 部分分析概念

- 仓库：https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking
- 作者 / 组织：Friends-of-Tracking-Data-FoTD。README 说明为 Laurie Shaw（Sports Analytics Lab, Harvard University）的代码。LICENSE 版权人为该组织。
- 许可：https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking/blob/master/LICENSE ，MIT，Copyright (c) 2021 Friends-of-Tracking-Data-FoTD。Metrica 数据与 YouTube 讲座不在该许可内。
- 主要内容：读取 Metrica tracking/event，以及 pitch control（README 写明基于 Will Spearman 的模型）和 EPV 教程（Tutorial1–4）。数据在 metrica-sports/sample-data，不在本仓库。
- 实际读到的文件：
  - https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking/blob/master/README.md
  - https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking/blob/master/Tutorial3_PitchControl.py
  - https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking/blob/master/Tutorial4_EPV.py
- 对本任务：从「谁在控球」讲到「这个空间是否可接应」时，可引用 Tutorial3/4 的概念定义，并用 Metrica 样本做示意。必须标明球场控制是概率模型。不是 FIFA/UEFA 课程。代码可能与当前环境不兼容；本次未运行。
- 维护：默认分支最新提交 `7ed3ff857940d3f4611be55f3c08c79525c32171`，2021-06-15 08:40 UTC，即 **2021-06-15 16:40 Asia/Shanghai**，说明为合并 LICENSE。组织搜索里的 `pushed_at`（2022-11-03）不能代替默认分支提交；按提交判断，已长期停滞。

### 7. Friends-of-Tracking-Data-FoTD/SoccermaticsForPython — 入门分析脚本，不是理论全书

- 仓库：https://github.com/Friends-of-Tracking-Data-FoTD/SoccermaticsForPython
- 作者 / 组织：Friends-of-Tracking-Data-FoTD。README 写明概念来自 David Sumpter 的书 *Soccermatics*（2016）及 Friends of Tracking YouTube。最新提交作者显示为 David Sumpter（david@twelve.football）。
- 许可：https://github.com/Friends-of-Tracking-Data-FoTD/SoccermaticsForPython/blob/master/LICENSE ，MIT，Copyright (c) 2020 Friends-of-Tracking-Data-FoTD。只覆盖脚本。原书、讲座、以及需自行放入的 StatsBomb / Wyscout 数据都不在该 LICENSE 内。
- 主要内容：`0helloworld.py` 到 `15PointsMovingAverage.py`，包括加载数据、传球/射门图、xG、传球热图等。README 仍写 “more coming soon”，与已有脚本不同步。
- 实际读到的文件：
  - https://github.com/Friends-of-Tracking-Data-FoTD/SoccermaticsForPython/blob/master/README.md
  - https://github.com/Friends-of-Tracking-Data-FoTD/SoccermaticsForPython/blob/master/1LoadInData.py
  - https://github.com/Friends-of-Tracking-Data-FoTD/SoccermaticsForPython/blob/master/3xGModel.py
  - https://github.com/Friends-of-Tracking-Data-FoTD/SoccermaticsForPython/blob/master/7PassHeatMap.py
- 对本任务：可作「如何把公开事件画成传球/射门/xG 图」的入门对照，帮助普通人看懂分析图，不是阵型或训练课大纲。不能把仓库当原书开源全文。
- 维护：`d6ec55b74a14885c525b517a8bc7f8b7ff00aeb9`，2021-03-13 07:38 UTC，即 **2021-03-13 15:38 Asia/Shanghai**，说明为 MovingAverage。已停滞。

### 8. SoccerNet/SoccerNet — 仅计算机视觉数据工具包

- 仓库：https://github.com/SoccerNet/SoccerNet
- 作者 / 组织：SoccerNet。LICENSE 版权人为 SoccerNet（2023）。默认分支最新提交作者为 Silvio Giancola。
- 许可：https://github.com/SoccerNet/SoccerNet/blob/main/LICENSE ，MIT。只覆盖 Python 包。数据在 https://huggingface.co/SoccerNet ，部分公开，部分需登录审批或电子签署 NDA（README 列出 SN-BAS-2024/2025、SN-PCBAS-2026 等为 NDA-gated）。默认分支是 **main**，不要用可能过时的 `blob/master/LICENSE` 徽章。
- 主要内容：动作定位、球员跟踪、镜头标定、球衣号、犯规识别等 CV 任务的数据入口。不是战术板课程。
- 实际读到的文档：
  - https://github.com/SoccerNet/SoccerNet/blob/main/README.md
  - https://github.com/SoccerNet/SoccerNet/blob/main/LICENSE
  - https://huggingface.co/SoccerNet
- 对本任务：仅在明确需要视频层标注时作为入口，并逐项遵守该数据集条款。不要为战术知识库下载整套视频或申请 NDA。广播跟踪不等于官方光学 tracking，也不能当成无球职责的权威记录。
- 维护：`dbf27e0633a11ea10cec048cbe0ebb8bdf80827b`，2026-10-04 12:41 UTC，即 **2026-10-04 20:41 Asia/Shanghai**，说明为更新 NDA 与 Hugging Face 认证下载文档。软件包仍在维护。

## 核验过但未列入主推荐的指针

- https://github.com/Friends-of-Tracking-Data-FoTD/Last-Row ：Metrica README 提到的进球跟踪样本，但仓库无 LICENSE，不能默认可复用，故不推荐导入。
- https://github.com/Friends-of-Tracking-Data-FoTD/mapping-match-events-in-Python ：GPL-3.0，Wyscout 公开事件绘图，与已列项目重叠，不单列。
- https://github.com/SkillCorner/opendata ：仅作为 Metrica README 中的指针（广播源 tracking，无事件、无视频）。本次未完整核验其 LICENSE，不作为主推荐。
- https://figshare.com/collections/Soccer_match_event_dataset/4415000 ：Wyscout 公开事件在 figshare，不是本次 GitHub 主项目。
- 搜索「football tactics / coaching」得到的多为战术板绘图应用，是界面工具而非理论内容库，未列入，避免硬凑开源知识库。

## 后续建议（本执行器不实施）

主线合并知识库时：理论与「教普通人看懂」的课程口径走 FIFA / UEFA / 教练资料；本报告只提供术语规范、案例边界和绘图工具约束。不要安装依赖、不要跑跟踪模型、不要下载整库、不要新建仓库、不要付费或联系第三方。若后续只用公开事件做示意图，必须先过 StatsBomb 用户协议（尤其是禁止商业利用衍生分析、禁止再分发数据、必须署名 logo）。需要讲无球空间时，只用 Metrica 样本并致谢，且不要默认再分发。
