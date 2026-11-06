# EP-20261029-01 事实表 · 火箭水母云（2026-10-29 00:40 UTC+8 核对）

| # | 稿中说法 | 事实 | 来源 |
|---|---|---|---|
| F1 | 10月23号傍晚六点一刻，长征六号改从太原起飞 | 2026-10-23 18:15（北京时间），太原卫星发射中心，长征六号改运载火箭发射遥感五十号03星，成功；长征系列第672次飞行 | 新华社 https://www.news.cn/20261023/5218f73077a64aa89a8da18d258c6bb6/c.html ；中新网 https://www.chinanews.com.cn/gn/2026/10-23/10719916.shtml |
| F1a | （不在稿中）网上很多视频写成「长征六号甲」 | 官方通稿均为「长征六号改」；抖音热门视频标签多写「长征六号甲」，属误写 | 同上；抖音搜索结果（research/field/search_jelly.json） |
| F2 | 北京、山西、山东好多人看见 | 「北京、山西、山东等多地网友都拍到了」；IT之家：山西、北京、山东、河北 | 山东宣传网 https://www.sdxc.gov.cn/sy/tp/202610/t20261025_18237014.htm ；IT之家/凤凰 https://tech.ifeng.com/c/8xUTDQ8ktm4 |
| F3 | 不是UFO | 央视《24小时》：不明飞行物「夜光水母」是火箭云 | 央视网 https://tv.cctv.com/2026/10/24/VIDEAF3kI5Vb0MLSrwwj5cIZ261024.shtml |
| F4 | 太阳已经落山半个多小时（示意图标注「太阳已落山 30 多分钟」） | 代码复算（NOAA 近似公式，research/sun_calc.py）：太原 10-23 日落约 17:40–17:43，18:15 太阳在地平线下 7.0–7.2°（落山后 32–35 分钟，两种近似）；济南 18:20 在地平线下 11.4–11.6°（落山后约 54 分钟） | 本地计算；与北京日报「日出前或日落后30分钟左右」一致 https://news.bjd.com.cn/2026/10/24/12005521.shtml |
| F5 | 几十到上百公里的高空太阳还没落 | IT之家：「地面已经变暗，但几十到上百公里的高空仍被阳光照亮」；复算：太阳在地平线下 d 度时，头顶地影高度 h=R(1/cos d−1)：7.2°→50 km，10°→98 km，11.6°→133 km | IT之家/凤凰同上；本地计算 |
| F6 | 地面在地球的影子里 | 晨昏时观测者已在地影中，高空羽流仍被阳光照到（APOD 2026-03-19：photographer was still in the dark） | NASA APOD https://science.nasa.gov/image-article/apod-2026-march-19-launch-plume-spacex-jellyfish/ |
| F7 | 到一百公里，气压不到地面的百万分之一 | 美国标准大气 1976：100 km 处 3.2012×10⁻² Pa；海平面 1.01325×10⁵ Pa；比值 3.16×10⁻⁷（约三百万分之一） | https://www.pdas.com/bigtables.html （U.S. Standard Atmosphere 1976） |
| F8 | 尾气一出喷口就向四周胀开（水母伞盖） | 高空环境压力远低于喷口出口压力（欠膨胀），尾气离开喷口立即膨胀扩散成大伞状 | Live Science https://www.livescience.com/space-jellyfish-spacex ；FIU https://web.eng.fiu.edu/allstar/rocket3.htm ；北京日报同上 |
| F9 | 在地面，尾焰被空气压着只有细细一条 | 低空环境压力高，羽流被约束、较窄；Space.com：plume grew substantially wider than the rocket as it climbed into thinner air | https://www.space.com/space-exploration/launches-spacecraft/spacex-rocket-launch-creates-incredible-space-jellyfish-visible-throughout-us-east-coast-photos |
| F10 | 水汽在零下八十多度直接冻成冰晶 | 北京日报：外界温度低至大约零下90°C，高温水蒸气直接凝华成冰晶；标准大气 85 km 188.9 K（−84 °C）、90 km 186.9 K（−86 °C） | 北京日报同上；pdas 表 |
| F11 | 液氧煤油，尾气有大量水汽 | 长六改芯级液氧煤油发动机 + 四枚固体助推器；燃烧产物主要为水蒸气、二氧化碳等 | 北京日报；山东宣传网 |
| F12 | 冰晶散射阳光所以亮 | 冰晶散射阳光呈现泛白柔光 | IT之家/凤凰同上；Chernouss 2012 https://archive.geophysica.fi/pdf/geophysica_2012_48_1-2_065_chernouss.pdf |
| F13 | 三个条件：晨昏发射、高空无强风、航线上方无厚云 | 央视新闻梳理三个同时成立的前提 | 山东宣传网；IT之家/凤凰 |
| F14 | 少一样，同一次发射天上什么也看不见 | 「任何一条不满足，同样的发射也可能只是一次安静的夜空飞行」 | IT之家/凤凰 |

| F15 | 示意图读数「高度 N km」「气压 = 地面的 1/N」，100 km 处到 1/316万 | 美国标准大气 1976 表按高度插值：100 km 0.03201 Pa / 101325 Pa = 1/316.5万；稿中说「不到百万分之一」成立 | pdas 表（同 F7）；remotion/src/Shots.tsx D2 插值表 |
| F16 | −80 °C 标注 | 标准大气 85–90 km −84～−86 °C；北京日报「约零下90°C」；标注写「−80 °C」为保守下限，对应口播「零下八十多度」 | 同 F10 |

不确定性：F4 为近似算法（±1 min）；各城市观测时刻不同，稿里只说「半个多小时」（以太原发射时刻为准）。
