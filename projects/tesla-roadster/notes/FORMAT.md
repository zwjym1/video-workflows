# Roadster「怎么飞」75秒拆解：横屏还是竖屏（只做一版）

## 结论（单选）
**主发 B站，做 16:9 横屏。**
理由：
1. B站 Roadster 热门前15 **15/15 全是横屏**（中位播放 62,219，中位点赞 1,004，中位赞播比 1.67%）。没有竖屏对照样本，竖屏在这个话题上未被验证。
2. 更广的 B站「新车/黑科技/原理拆解」样本（40条，按播放排序搜索）：横屏 33 条，中位播放 48,146，中位点赞 813，赞播比 1.68%；竖屏 7 条，中位播放 92,712，中位点赞 452，赞播比 1.12%。竖屏播放中位数更高但样本小（n=7），点赞率明显更低；拆解/原理类的互动（点赞、三连）横屏更好，而 B站推荐看重三连。
3. 素材是 16:9 发布会实拍，关键信息是横向的：坡道全貌、空中翻转轨迹、飞越 Semi 的车队。中心裁成 9:16 会切掉轨迹和车队，只能靠模糊垫边或上下分屏，画面会变小、显得廉价。3D 原理拆解横屏也更方便左右对照（推进器 vs 车底风扇）。
4. 横屏视频在 B站一样能进 Story Mode 竖屏信息流（界面新闻报道，未经官方核实），所以横屏不会被挡在竖屏流量之外。

代价：抖音竖屏流量吃不到；如果用户以后改主意要上抖音，再从横屏工程里重构图。

## 数据方法
- 用 B站 `/x/player/pagelist` 的 dimension 取宽高（rotate=1 时宽高对调），时长也取自 pagelist；播放和点赞取自搜索接口（2026-10-16 抓取）。
- 广样本搜索词：新车 黑科技 拆解 / 汽车 黑科技 原理 / 新车 发布会 黑科技 / 汽车 技术 拆解 原理（order=click，每词前10条，去重）。
- 抖音：之前已被拦（403），这次没有再抓，没有抖音数据。

## B站横竖屏推荐差异（公开报道，未经官方核实）
- 界面新闻《B站变短，创作者跟不跟？》：Story Mode 不区分横竖屏，任何内容都能进竖屏信息流；Story Mode DAU 渗透超过 20%，点赞占比 30%。https://www.jiemian.com/article/7326460.html
- 腾讯新闻：Story Mode 是 B站核心流量入口之一。https://news.qq.com/rain/a/20260312A08TSP00
- 电商派：B站「SUPER UP」时尚美妆扶持计划写明优先扶持横屏长视频创作者（这是时尚品类，不是科技品类）。https://www.pai.com.cn/p/01jrhz9s4zb6headkq1g482dha
- 品玩：B站推荐看重一键三连（投币、收藏）。https://www.pingwest.com/a/264565
- 没有找到 B站官方文档说明横竖屏的推荐权重差异。

## 16:9 裁 9:16 的取舍（仅作参考，本次只做横屏）
- 中心裁切：只剩约 32% 画面宽度，坡道和飞行轨迹被切掉。
- 模糊垫边：信息完整，但主体只占屏幕约 1/3。
- 上下分屏（实拍+3D）：可行，但每块都小。
- 3D 部分两种画幅都能原生渲染，难点只在实拍。

## 数据表
| 组 | BV | 标题 | 宽x高 | 时长s | 播放 | 点赞 |
|---|---|---|---|---|---|---|
| roadster | [BV1ZPJS6HEAL](https://www.bilibili.com/video/BV1ZPJS6HEAL) | 特斯拉新一代Roadster震撼发布，美国人能飞 | 2400x1080 | 182 | 481329 | 8033 |
| roadster | [BV1oMJS6UETx](https://www.bilibili.com/video/BV1oMJS6UETx) | 特斯拉Roadster真的会飞！非AI画面！ | 1920x1080 | 51 | 298959 | 8001 |
| roadster | [BV1zcJS6sEXT](https://www.bilibili.com/video/BV1zcJS6sEXT) | 特斯拉Roadster飞车展示+一秒内60英里加速展示 | 1920x1080 | 366 | 235947 | 3889 |
| roadster | [BV1j9JQ6oEeE](https://www.bilibili.com/video/BV1j9JQ6oEeE) | 特斯拉Roadster会飞！发布会超全总结来了！ | 1920x1080 | 112 | 162234 | 4900 |
| roadster | [BV1S4JQ65Exj](https://www.bilibili.com/video/BV1S4JQ65Exj) | 两分钟发布会 特斯拉飞行汽车发布！马斯克能飞 28年量产 T | 3840x2160 | 251 | 110402 | 3202 |
| roadster | [BV19fJQ6pE2w](https://www.bilibili.com/video/BV19fJQ6pE2w) | 特斯拉Roadster发布：汽车真的会飞 | 1920x1080 | 65 | 79651 | 1800 |
| roadster | [BV1YFJX6XEvb](https://www.bilibili.com/video/BV1YFJX6XEvb) | 特斯拉Roadster2发布！现场展示悬停+飞跃！这不是AI | 1920x1080 | 136 | 78031 | 887 |
| roadster | [BV1VoJQ69EjX](https://www.bilibili.com/video/BV1VoJQ69EjX) | 史上最逆天超跑没有之一！一文看懂特斯拉Roadster发布会 | 1920x1080 | 146 | 62219 | 1004 |
| roadster | [BV1KbJS6KENx](https://www.bilibili.com/video/BV1KbJS6KENx) | 特斯拉Roadster2发布活动现场 | 3840x2160 | 25 | 60072 | 624 |
| roadster | [BV1cZJU64ES1](https://www.bilibili.com/video/BV1cZJU64ES1) | 特斯拉Roadster正式发布！真的会飞！零百加速1秒！ | 1920x1080 | 130 | 48113 | 622 |
| roadster | [BV1FZJU64Ez3](https://www.bilibili.com/video/BV1FZJU64Ez3) | 美国车能飞，美国车能飞特斯拉Roadster依靠推进器平稳着 | 1920x1080 | 52 | 46953 | 1010 |
| roadster | [BV1cZJU64EMg](https://www.bilibili.com/video/BV1cZJU64EMg) | 特斯拉Roadster2车能飞，不是AI，不是AI，不是AI | 3840x2160 | 150 | 44494 | 665 |
| roadster | [BV1jGJQ6RE47](https://www.bilibili.com/video/BV1jGJQ6RE47) | 【CNET】特斯拉 Roadster 发布会：10分钟回顾精 | 1920x1080 | 615 | 35231 | 663 |
| roadster | [BV1ccJQ6AELQ](https://www.bilibili.com/video/BV1ccJQ6AELQ) | 特斯拉Roadster真的能飞？百公里加速0.81秒！这波是 | 1920x1080 | 1566 | 17122 | 243 |
| roadster | [BV1CiJQ6MEBB](https://www.bilibili.com/video/BV1CiJQ6MEBB) | 特斯拉展示Roadster2跑车，零百加速0.81秒！还能悬 | 1920x1080 | 208 | 20031 | 590 |
| broad | [BV1tCzkBhE16](https://www.bilibili.com/video/BV1tCzkBhE16) | 【双轮实验室】极酷ES85Pro电动摩托车拆解测试报告  最 | 3840x2160 | 292 | 73578 | 1893 |
| broad | [BV1iq4y137uH](https://www.bilibili.com/video/BV1iq4y137uH) | 【硬核拆车】大众ID.3 VS 特斯拉Model3全面拆解， | 1920x1080 | 656 | 48146 | 628 |
| broad | [BV1SGqPBnEAV](https://www.bilibili.com/video/BV1SGqPBnEAV) | 看拆解视频不如看比亚迪公主 | 1088x1920 | 2769 | 16725 | 424 |
| broad | [BV1Tdq1BAEJs](https://www.bilibili.com/video/BV1Tdq1BAEJs) | 拆解小米SU7，这些发现颠覆你的想象！ | 640x480 | 355 | 15304 | 119 |
| broad | [BV1EsqnB7Efu](https://www.bilibili.com/video/BV1EsqnB7Efu) | 豪华旗舰车型-蔚来ET9内饰和座椅拆解篇 | 1920x1080 | 663 | 4307 | 76 |
| broad | [BV1zQFez1ESK](https://www.bilibili.com/video/BV1zQFez1ESK) | 嘉梁解读，理想i8中保研碰撞数据，拆解中保研测试背后的安全技 | 3840x2160 | 444 | 2915 | 48 |
| broad | [BV1feFAzdEBe](https://www.bilibili.com/video/BV1feFAzdEBe) | 吉利银河M9全网首次零部件级拆解，20万级的价格40万级的价 | 1920x1080 | 205 | 2086 | 20 |
| broad | [BV16yFrzeECs](https://www.bilibili.com/video/BV16yFrzeECs) | 蔚来ET9 内饰及座椅讲解 | 1920x1080 | 663 | 2080 | 35 |
| broad | [BV11VGnz7EJr](https://www.bilibili.com/video/BV11VGnz7EJr) | 九号MZ MAX拆解方式和内部做工 | 1080x1920 | 191 | 1966 | 22 |
| broad | [BV1jR2LB9EYm](https://www.bilibili.com/video/BV1jR2LB9EYm) | 新款BOSE S1 Pro+拆解：阵列倾角布局设计，水平覆盖 | 576x1024 | 15 | 1310 | 12 |
| broad | [BV1sRgBzxETV](https://www.bilibili.com/video/BV1sRgBzxETV) | 这是什么原理 | 720x720 | 14 | 515998 | 9808 |
| broad | [BV1USdKBBEqe](https://www.bilibili.com/video/BV1USdKBBEqe) | 什么原理？为什么没有试验成功？ | 1080x1544 | 25 | 509018 | 5982 |
| broad | [BV1Fp6EBQEAN](https://www.bilibili.com/video/BV1Fp6EBQEAN) | 谁能告诉我这是什么原理? | 1080x1920 | 14 | 262444 | 1464 |
| broad | [BV1tL411L7Xi](https://www.bilibili.com/video/BV1tL411L7Xi) | 汽车上天？火箭下地？超离谱的黑科技，靠什么科学原理？是不是“ | 1920x1080 | 647 | 176158 | 10884 |
| broad | [BV17GSqYPE4M](https://www.bilibili.com/video/BV17GSqYPE4M) | 男子用马达带动齿轮，模拟轿车的档位，网友：这是什么变速箱 | 1080x1904 | 16 | 106813 | 452 |
| broad | [BV1MK4y1M7aX](https://www.bilibili.com/video/BV1MK4y1M7aX) | 新能源汽车“接地宝”，到底是高科技还是交了智商税？拆开探究竟 | 1920x1080 | 261 | 96559 | 1652 |
| broad | [BV1t7vqBuEgA](https://www.bilibili.com/video/BV1t7vqBuEgA) | 什么原理？ | 1080x1920 | 28 | 92712 | 2259 |
| broad | [BV1Na4y157zA](https://www.bilibili.com/video/BV1Na4y157zA) | 天才发明-万向轮的工作原理，实现汽车平移与原地掉头 | 1920x1080 | 206 | 91889 | 1317 |
| broad | [BV1j14y1i751](https://www.bilibili.com/video/BV1j14y1i751) | 国外发明汽车拦截神器，轮胎压过就会漏气，这是什么原理？ | 1920x1080 | 63 | 82873 | 28 |
| broad | [BV16P4y1C7yU](https://www.bilibili.com/video/BV16P4y1C7yU) | 豪车上的空气悬挂，气囊一上一下来回运动，原理是什么？ | 1920x1080 | 67 | 70294 | 202 |
| broad | [BV1soQoBwEqd](https://www.bilibili.com/video/BV1soQoBwEqd) | 友商典范：比亚迪与小米的君子之交 | 1920x1080 | 769 | 392955 | 8470 |
| broad | [BV1pX4y1m7P4](https://www.bilibili.com/video/BV1pX4y1m7P4) | 【短的发布会】极限模拟无惧较量？睿蓝7搭载无级DIY化身百变 | 1920x1080 | 186 | 225795 | 20946 |
| broad | [BV13XGPz2EJ9](https://www.bilibili.com/video/BV13XGPz2EJ9) | 【三分半看懂发布会】极氪9X带8大黑科技傍身！3.1秒干翻超 | 1920x1080 | 365 | 119910 | 813 |
| broad | [BV13P411U7cF](https://www.bilibili.com/video/BV13P411U7cF) | 【车的发布会】全是黑科技？开别克E5不走神竟靠发光方向盘？ | 1920x1080 | 249 | 98608 | 4959 |
| broad | [BV1Q4PLz9EJL](https://www.bilibili.com/video/BV1Q4PLz9EJL) | 惊蛰技术发布会，比亚迪又要整什么活？ | 1920x1080 | 761 | 43825 | 1328 |
| broad | [BV1obVSzXEd8](https://www.bilibili.com/video/BV1obVSzXEd8) | 【三分半看懂发布会】11.58万元起，吉利银河星耀8放大招， | 1920x1080 | 208 | 43236 | 356 |
| broad | [BV1yy4y1H7hN](https://www.bilibili.com/video/BV1yy4y1H7hN) | 「趣看发布会」智己汽车品牌发布会总结：汽车也能无线充电？ | 2160x1080 | 255 | 39234 | 2029 |
| broad | [BV11t4y1m7Wk](https://www.bilibili.com/video/BV11t4y1m7Wk) | 【新宝骏发布会】 -- 小哥哥操作演示HUAWEI HiCa | 1920x1080 | 659 | 35591 | 333 |
| broad | [BV1ehq8BPEix](https://www.bilibili.com/video/BV1ehq8BPEix) | 颠覆内燃机一百年！丰田2026氢燃料电池车发布会现场震撼瞬间 | 1920x1080 | 1282 | 29697 | 325 |
| broad | [BV1DCGj6cEHH](https://www.bilibili.com/video/BV1DCGj6cEHH) | 【中配】9分钟看完特斯拉半挂卡车与超跑发布会 - The V | 1920x1080 | 525 | 18418 | 87 |
| broad | [BV1Cb4y1m7cw](https://www.bilibili.com/video/BV1Cb4y1m7cw) | 拆解车载小冰箱，和正常冰箱截然不同的工作原理 | 1920x1080 | 227 | 121831 | 6776 |
| broad | [BV1Vp4y1r7e2](https://www.bilibili.com/video/BV1Vp4y1r7e2) | 拆解发动机上的水泵总成，不了解这个东西，只是好奇打开看看 | 1920x1080 | 343 | 97302 | 4145 |
| broad | [BV1mD4y1X7aq](https://www.bilibili.com/video/BV1mD4y1X7aq) | 汽车胎压检测是如何实现的？拆解两种不同类型的传感器看懂原理 | 1920x1080 | 377 | 89302 | 3410 |
| broad | [BV1Uv411i7yA](https://www.bilibili.com/video/BV1Uv411i7yA) | 拆解汽车应急启动电源，巴掌大小却能输出500A大电流，究竟是 | 1920x1080 | 202 | 55927 | 972 |
| broad | [BV1wg411u7iP](https://www.bilibili.com/video/BV1wg411u7iP) | 汽车的刹车是如何实现的，为什么熄火后刹车会变重？ | 1920x1080 | 586 | 53837 | 2391 |
| broad | [BV1tW4y1E72i](https://www.bilibili.com/video/BV1tW4y1E72i) | 发动机拆装实训课 高考科目 | 1920x1080 | 921 | 27427 | 307 |
| broad | [BV1ot4y1U72q](https://www.bilibili.com/video/BV1ot4y1U72q) | 滤震差？颠簸？进来！！带你看懂减震器的结构和工作原理~丰田R | 1920x1080 | 329 | 27359 | 1593 |
| broad | [BV1Wv4y1f7Et](https://www.bilibili.com/video/BV1Wv4y1f7Et) | 转向拉杆及球头，检查、更换以及暴力拆解看看内部构造原理 | 1920x1080 | 210 | 26424 | 196 |
| broad | [BV1VB4y1H7sG](https://www.bilibili.com/video/BV1VB4y1H7sG) | 汽车ABS系统到底是干嘛的？3D拆解ABS运作原理。 | 1440x1080 | 154 | 25684 | 178 |
| broad | [BV1B85k6XELi](https://www.bilibili.com/video/BV1B85k6XELi) | 【中配】硬核拆解，带你看懂垃圾车内部工作原理-Logic M | 3840x2160 | 603 | 24456 | 279 |

## 抖音补充
11 条抖音同题视频互动远高于 B站同题（头部 5 万赞、20 万分享），但页面上看不出横竖屏，这次没能统计画幅。结论不变：横屏、主发 B站；代价是放弃抖音的热度，抖音传播量明显更大。
