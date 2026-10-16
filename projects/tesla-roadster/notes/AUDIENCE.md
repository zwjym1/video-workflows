# 特斯拉新 Roadster 发布会：观众关注点调研（B站）

采集时间：2026-10-16 15:00 前后（北京时间）。原始数据：`audience_raw/bili.json`（视频、评论、弹幕），`audience_raw/topics.json`（分类结果）。

## 采集范围与限制
- **B站**：用 3 个关键词（特斯拉 Roadster 发布会 / Roadster 飞 / 特斯拉 飞行汽车）按播放排序搜索，筛出近 3 天、标题和 Roadster 或“飞”相关的视频共 28 个，取播放量前 15 个。共采到 **140 条评论**（未登录的接口每个视频只返回约 3 条热评，再加上它们的楼中楼）和 **5295 条弹幕**（第 1 个分 P 的弹幕池，单个视频最多 1200 条）。播放和点赞数取自 B站搜索接口。`/x/web-interface/view` 返回 412，所以视频简介也取自搜索结果。
- **抖音**：搜索接口返回 `status_msg: blocked`，**没有采到任何数据**，下文全部是 B站数据。
- 评论样本少，统计以弹幕为主。代表性原话按评论点赞排序，逐字摘录（表情代码保留原样）。

## 视频列表
|#|标题|UP主|播放|点赞|评论|弹幕|
|-|-|-|-|-|-|-|
|1|[特斯拉新一代Roadster震撼发布，美国人能飞](https://www.bilibili.com/video/BV1ZPJS6HEAL)|-通假字-|481329|8033|12|1200|
|2|[特斯拉Roadster真的会飞！非AI画面！](https://www.bilibili.com/video/BV1oMJS6UETx)|极客阿来|298959|8001|10|360|
|3|[特斯拉Roadster飞车展示+一秒内60英里加速展示](https://www.bilibili.com/video/BV1zcJS6sEXT)|车影相册|235947|3889|10|1200|
|4|[特斯拉Roadster会飞！发布会超全总结来了！](https://www.bilibili.com/video/BV1j9JQ6oEeE)|天上一颗大星星|162234|4900|9|335|
|5|[两分钟发布会 特斯拉飞行汽车发布！马斯克能飞 28年量产 Tesla Roadster](https://www.bilibili.com/video/BV1S4JQ65Exj)|科技美学|110402|3202|9|874|
|6|[特斯拉Roadster发布：汽车真的会飞](https://www.bilibili.com/video/BV19fJQ6pE2w)|YouTube精彩视频-|79651|1800|11|156|
|7|[特斯拉Roadster2发布！现场展示悬停+飞跃！这不是AI太震撼了！](https://www.bilibili.com/video/BV1YFJX6XEvb)|三星手机非官方|78031|887|7|236|
|8|[史上最逆天超跑没有之一！一文看懂特斯拉Roadster发布会](https://www.bilibili.com/video/BV1VoJQ69EjX)|纽北之家|62219|1004|9|166|
|9|[特斯拉Roadster2发布活动现场](https://www.bilibili.com/video/BV1KbJS6KENx)|环球新知|60072|624|11|10|
|10|[特斯拉Roadster正式发布！真的会飞！零百加速1秒！](https://www.bilibili.com/video/BV1cZJU64ES1)|极客阿来|48113|622|8|97|
|11|[美国车能飞，美国车能飞特斯拉Roadster依靠推进器平稳着陆](https://www.bilibili.com/video/BV1FZJU64Ez3)|陈哲然Dk|46953|1010|6|55|
|12|[特斯拉Roadster2车能飞，不是AI，不是AI，不是AI](https://www.bilibili.com/video/BV1cZJU64EMg)|Starship_SpaceX|44494|665|11|124|
|13|[【CNET】特斯拉 Roadster 发布会：10分钟回顾精彩瞬间 | 机翻中文](https://www.bilibili.com/video/BV1jGJQ6RE47)|KG-Area21|35231|663|12|337|
|14|[特斯拉Roadster真的能飞？百公里加速0.81秒！这波是工业神迹还是商业作秀？【特斯拉Roadster发布会深度分析】](https://www.bilibili.com/video/BV1ccJQ6AELQ)|达芬奇矩阵|17122|243|6|66|
|15|[特斯拉展示Roadster2跑车，零百加速0.81秒！还能悬停倒着飞！](https://www.bilibili.com/video/BV1CiJQ6MEBB)|极客小冷|20031|590|9|79|

## 话题热度（关键词统计）
统计方法：每个话题配一组关键词正则（见 topics.json 的 pattern 字段）。一条评论或弹幕只要命中一次就记 1；同一条可以同时计入多个话题。这是粗估：比如“万”“AI”“假”会带进一些无关内容，“喷”也会混进“喷人”的意思。

|话题|评论命中|弹幕命中|热度|
|-|-|-|-|
|怎么飞/推进器原理|16|345|高|
|梗/玩笑|10|335|高|
|营销噱头/真假|4|250|高|
|与中国品牌对比|14|206|高|
|价格/交付|18|153|中|
|安全性|12|117|中|
|风扇吸地|2|123|中|
|0.81秒/加速|1|84|低|
|能否上路/合法|2|67|低|

## 各话题代表性原话（逐字）

### 怎么飞/推进器原理
- 评论（666赞）：「旁边的路人：你知道吗？我曾经直面火箭喷射[doge]」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 评论（609赞）：「车辆是玩具，但是姿态控制这一块真是火箭技术下放，炫技来的」 — https://www.bilibili.com/video/BV1oMJS6UETx
- 评论（273赞）：「影视道具车来的说是 他这个纯压缩气体冷喷 量产不可能上 没意义」 — https://www.bilibili.com/video/BV1oMJS6UETx
- 弹幕：「降维打击了属于是，造车的怎么跟造火箭的比」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「都坐下 火箭都回收多少了 一个车而已」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「当你同时拥有全世界最先进的汽车公司和火箭公司be like：」 — https://www.bilibili.com/video/BV1ZPJS6HEAL

### 风扇吸地
- 评论（33赞）：「能实现一半都是无敌存在，就那个逆天吸附力，想象空间太大了」 — https://www.bilibili.com/video/BV1KbJS6KENx
- 评论（23赞）：「应该不是吧，可能展示推进系统的下压力，可以让车压在地面，也就是慢慢开上去，静止在那个顶上吧。不然真飞出去转一圈也太科幻了」 — https://www.bilibili.com/video/BV1KbJS6KENx
- 弹幕：「AI查了一下，就是五十年前布拉汉姆那种风扇车的进化版。」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「什么反向喷射？这个是底盘抽负压」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「反向喷射，产生下压力」 — https://www.bilibili.com/video/BV1ZPJS6HEAL

### 能否上路/合法
- 评论（2赞）：「这个版本不允许上路来着。。。」 — https://www.bilibili.com/video/BV1zcJS6sEXT
- 评论（0赞）：「尊界虽然垃圾到人神共愤，但他能上路，[藏狐]，这个特斯拉我记得跳票了好几年了吧，这次这个炫技大作，能在中国上路吗？上一个赛博皮卡好像都没官方引进吧」 — https://www.bilibili.com/video/BV1jGJQ6RE47
- 弹幕：「我的驾照能开吗」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「space X的技术套个车壳子，这玩意真上路有人敢用吗，别说什么避险真遇险更大概率是轻伤变重伤、重伤变转生」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「技术很厉害，不得不佩服，实用性目前没多少，谁没事开车爬墙，安全性，法律法规都没有」 — https://www.bilibili.com/video/BV1ZPJS6HEAL

### 安全性
- 评论（45赞）：「堵车那喷气一喷，保险不够赔[笑哭]」 — https://www.bilibili.com/video/BV1zcJS6sEXT
- 评论（12赞）：「后悬架能开三指，方向盘能断，安全带能断你说怪不怪」 — https://www.bilibili.com/video/BV1S4JQ65Exj
- 评论（6赞）：「没事  方向盘一断  安全带一断  直接和车一起起飞」 — https://www.bilibili.com/video/BV19fJQ6pE2w
- 弹幕：「好创意，尽快低成本全球普及，可避免高速连环追尾事故和梅大高速道路塌陷类的交通事故，万一遇到地震，就地起飞，可避免地震影响。」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「吓死你们这些盘盘」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「就这。。就算是给你开放购买你也用不上，更何况那个压缩气罐属于死重，拖累续航」 — https://www.bilibili.com/video/BV1ZPJS6HEAL

### 价格/交付
- 评论（1717赞）：「这才是百万豪车啊[妙啊]」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 评论（1492赞）：「特斯拉官网已经支持对Performance版和Thrust版的预订，其中大陆地区可以预订performance版本，意向金¥332,000，thrust版本意向金约合人民币167万元」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 评论（465赞）：「这应该不是量产车，应该是用来展示技术力和搞投资的」 — https://www.bilibili.com/video/BV1oMJS6UETx
- 弹幕：「《1000万以内》」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「这是1000万以内最好的车吗」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「这个底盘太低，进不了我村口，不买了。」 — https://www.bilibili.com/video/BV1ZPJS6HEAL

### 营销噱头/真假
- 评论（11赞）：「比亚迪还是太老实人了，应该也搞这种作秀，国外卖高端车，国内卖普通车，曲线救国，做洋人的严父也不要做国内的朋友。」 — https://www.bilibili.com/video/BV1VoJQ69EjX
- 评论（10赞）：「真正的2077，就算是玩营销噱头都比这些国产厂商高了不止几个档次[大笑]」 — https://www.bilibili.com/video/BV1jGJQ6RE47
- 评论（2赞）：「回复 @刘猫lol :技术上来说是用上了航天技术的一部分，我说个例子你就知道了，十几年前还是多少年前，不是早就有一种单人喷气飞行装置吗，这玩意儿就是这个，只不过是马斯克把它和火箭那个回收系统结合到车上了，所以我说这是马斯克为了拉高股价和应付市场的玩意儿，实用价值聊胜于无，他这些东西单独拆下来应用到各个领域都是好玩意儿，但是拼车上就纯是玩具了。」 — https://www.bilibili.com/video/BV19fJQ6pE2w
- 弹幕：「？？？？？？？？？？？？ai 提示呢」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「这姿态控制太吊了啊，随心所欲」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「AI查了一下，就是五十年前布拉汉姆那种风扇车的进化版。」 — https://www.bilibili.com/video/BV1ZPJS6HEAL

### 0.81秒/加速
- 评论（261赞）：「其实说是没用 小概率还是用的上的 比如你开着roadster在路上 后面突然加速追上来一辆没刹车的尊界」 — https://www.bilibili.com/video/BV1KbJS6KENx
- 弹幕：「不需要加速，吸尘器原理」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「妈妈，我头有点晕」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「g值？不可能。这不是飞机！」 — https://www.bilibili.com/video/BV1ZPJS6HEAL

### 与中国品牌对比
- 评论（1346赞）：「这也是类魂吗？国道上遇到双大运拍门直接一个雷霆大跳闪避」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 评论（65赞）：「[doge]看看这评论区风气多好，要是国产车不得被到处喷」 — https://www.bilibili.com/video/BV1j9JQ6oEeE
- 评论（16赞）：「这个喷气已经脱离汽车范畴了，没点造火箭功底我觉得真造不出来，
当然，我不是在说国产车造不出来哈」 — https://www.bilibili.com/video/BV1j9JQ6oEeE
- 弹幕：「华为牛逼！遥遥领先！」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「国内四家民营航空公司都是有雷军总股份的，国内可能第一个能做到的就是小米了」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「小鹏的几年前就飞了」 — https://www.bilibili.com/video/BV1ZPJS6HEAL

### 梗/玩笑
- 评论（825赞）：「中间这个雷霆大坡道是认真的？难不成要人开车冲上去来个大回旋接一个空中rcs刹车调姿帅气落地，太离谱了，有点难以想象[笑哭][笑哭][笑哭]」 — https://www.bilibili.com/video/BV1KbJS6KENx
- 评论（382赞）：「卧槽真给你猜对了！！真的是雷霆大滚转RCS翻滚落地[灵魂出窍][灵魂出窍][灵魂出窍]」 — https://www.bilibili.com/video/BV1KbJS6KENx
- 评论（123赞）：「这么牛逼的东西还有人非要赢一把」 — https://www.bilibili.com/video/BV1cZJU64ES1
- 弹幕：「钢铁侠式降落」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「华为牛逼！遥遥领先！」 — https://www.bilibili.com/video/BV1ZPJS6HEAL
- 弹幕：「脑机接口，人工智能，汽车工业，火箭技术，星链，，老马的目标是钢铁侠吧，他想自己上天？」 — https://www.bilibili.com/video/BV1ZPJS6HEAL

注意：「特斯拉官网已经支持对Performance版和Thrust版的预订……意向金¥332,000……」是网友评论，**未经核实**，上屏前请对照 /workspace/topics/tesla-2026-10.md 和特斯拉官网。

## 选题空白（观众在问，现有视频标题、简介和热评都没讲清）
对照方式：看这 15 个视频的标题和简介，再看热评里有没有给出答案。现有视频基本都在讲“会飞、不是AI、加速1秒、发布会总结”，原理层面几乎没人讲。
1. **它到底靠什么飞、靠什么吸地？** 弹幕里有人争论“冷喷不是风扇，吸底盘才是”和“反向喷射产生下压力”，有人拿它比布拉汉姆风扇车，还有人问“下压力需要4吨以上……是怎么实现的”。没有视频把冷气推进器（RCS 姿态控制）和底盘负压风扇分开讲清楚。**这是最大的空白**，适合做原理动画。
2. **能上路吗？中国能买能开吗？** 有“我的驾照能开吗”“能在中国上路吗”“这个版本不允许上路”这类问题，但没有视频讲清法规：喷气装置算不算机动车改装、能不能上牌、要不要飞行执照。
3. **演示车和量产车有什么区别？** 观众在问“是不是道具车”“冷喷量产不可能上”“28年量产”是真是假，也关心推进器量产时会不会保留、气瓶是死重会拖累续航。
4. **安全性**：方向盘、安全带、后悬架这些梗（反讽国产车事故）热度很高；另一个关心点是喷气会不会伤到路人和后车，比如“保险不够赔”。这些都没人回答。
5. **0.81 秒是真是假、人能不能扛住**：有“g值？”“头晕”这类问题。字卡上写的是 0-60mph 1 sec（见 REPORT.md），和 0.81 秒口径不一样，可以讲清楚这个数怎么来的、人要承受多大 G 值。

## 给热点视频的建议
- 开头用“这不是AI”和真实画面做钩子，观众的第一反应就是怀疑是不是 AI。
- 主体用 60 秒讲清“喷气翻转 vs 风扇吸地”两套系统，再讲能不能上路、价格和量产时间。
- 中国品牌对比和事故梗弹幕很多，但容易引战，建议轻点一下，不要展开。
## 抖音补充（免登录浏览器采集，10-16 约16:00）
11 条视频，原始数据见 audience_raw/douyin_browser.json。点赞最高：阿凯 5.02万赞/6190评/19.99万分享；Fallx 4.89万赞/8648评；第一财经 2.24万赞/9575评。
免登录每条只能看到 3-5 条热评。高频话题：拿“刹车踏板断裂”事件对比、调侃蔚来李斌和小鹏飞行汽车、“国内一片安静”、质疑“量产版能不能加这个套件”。
示例原话：“惊讶程度不亚于我看到刹车踏板会被踩断”（3226赞）；“现场真实演示，还是量产版能加的套件[捂脸]”（2554赞）。
