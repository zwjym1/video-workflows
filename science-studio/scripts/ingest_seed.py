#!/usr/bin/env python3
"""一次性（可重复执行）把已有作品、工程、素材、经验登记进资产库。只登记盒上真实存在的路径；指标只取用户提供的创作者中心数据。"""
import sys, json, re, csv, pathlib, subprocess
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
W = "/workspace"
c = db.connect()
def ex(p): return p if p and pathlib.Path(p).exists() else None
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True).stdout.strip())
    except Exception: return None

# ---------- works ----------
WORKS = [
 dict(episode="LEGACY-roadster-v4", title="特斯拉新跑车真能飞？ 马斯克没吹牛吗？一分钟讲清它靠什么飞", platform="抖音+B站", status="已发布",
      published_at="2026-10-17 12:58:53", project_dir=f"{W}/topics/tesla-roadster", final_video=None,
      script=f"{W}/topics/tesla-roadster/voice/v3/script.txt", cover=f"{W}/brand/deliver/品牌/封面_Roadster/Roadster封面_E5_竖版3x4.png",
      notes="V4 成片与 V4 源码不在盒上（在用户 PC），script 指向 V3 稿。复盘：/workspace/douyin-growth/reviews/roadster_24h_2026-10-18.md"),
 dict(episode="LEGACY-iphone-fake", title="这些iPhone是假的（满海免费 iPhone，AI 造假核查）", platform="抖音", status="已发布", published_at=None,
      project_dir=f"{W}/iphone-fake", final_video=f"{W}/iphone-fake/v2/remotion/out/满海iPhone是假的_秘书丞_V3f_1080p.mp4",
      script=f"{W}/iphone-fake/v2/script_v3.md", storyboard=f"{W}/iphone-fake/v2/storyboard.md",
      cover=f"{W}/brand/deliver/品牌/封面_iPhone假/iPhone假封面_B_3x4_1080x1440.png", publish_caption=f"{W}/iphone-fake/v2/publish_caption.md",
      notes="发布版=V3f 无组件版（替代旧 v2 1080p）。发布时间未记录，待用户补。"),
 dict(episode="LEGACY-canton-robot", title="广交会乒乓球机器人「一看·二算·三打」", platform="抖音", status="已发布", published_at="2026-10-19 19:05",
      project_dir=f"{W}/canton-robot", final_video=f"{W}/canton-robot/out/广交会机器人_一看二算三打_1080p.mp4",
      script=f"{W}/canton-robot/script.md", cover=f"{W}/canton-robot/out/封面/封面_竖_1080x1920.png",
      publish_caption=f"{W}/canton-robot/out/发布文案.txt", notes="成片=v6 头 + v5 尾拼接"),
 dict(episode="LEGACY-zhangxue-water", title="张雪机车水上漂：它没漂，它在滑", platform="抖音", status="已取消", project_dir=f"{W}/zhangxue-water",
      final_video=f"{W}/zhangxue-water/out/张雪机车水上漂_不漂是滑_v3_1080p.mp4", script=f"{W}/zhangxue-water/script.md",
      storyboard=f"{W}/zhangxue-water/SHOTS.md", cover=f"{W}/zhangxue-water/out/封面/封面_竖_1080x1920.png",
      publish_caption=f"{W}/zhangxue-water/out/发布文案.txt", notes="2026-10-20 用户取消晚槽，工程保留；有 1080 成片未发布"),
 dict(episode="LEGACY-roadster-downforce", title="Roadster 下压起飞（续集）", platform="抖音", status="停档", project_dir=f"{W}/roadster-downforce",
      script=f"{W}/roadster-downforce/script/script.md", storyboard=f"{W}/roadster-downforce/storyboard/storyboard.md", notes="停档，工程保留"),
 dict(episode="LEGACY-deepseek-noon", title="DeepSeek V4.1 动画实测（午槽）", platform="抖音", status="已取消", project_dir=f"{W}/topics/deepseek_v41_noon",
      script=f"{W}/topics/deepseek_v41_noon/script.md", notes="用户 10-20 取消"),
 dict(episode="LEGACY-optogenetics", title="池塘里的绿藻，凭什么帮人类「用光控制大脑」？（2026 诺奖光遗传学）", platform="抖音", status="制作中",
      project_dir=f"{W}/optogenetics", script=f"{W}/optogenetics/script_original.md", storyboard=f"{W}/optogenetics/storyboard_2d.md",
      notes="2D Remotion 分段制作中；配音 vo/vo_master.wav（用户定稿第一版）"),
 dict(episode="SAMPLE-pi", title="圆周率小学课程（讲题样例）", platform="—", status="样例", project_dir=f"{W}/pi",
      script=f"{W}/pi/step3-script-final.md", storyboard=f"{W}/pi/step4-storyboard.md"),
 dict(episode="SAMPLE-gradient-descent", title="梯度下降科普（样例）", platform="—", status="样例", project_dir=f"{W}/video-workflows/projects/gradient-descent"),
]
wid = {}
for w in WORKS:
    for k in ("final_video","script","storyboard","cover","publish_caption","srt"): w[k] = ex(w.get(k))
    cols = ["episode","title","platform","status","published_at","project_dir","final_video","script","srt","storyboard","cover","publish_caption","notes"]
    c.execute(f"INSERT INTO works({','.join(cols)},updated_at) VALUES({','.join('?'*len(cols))},?) ON CONFLICT(episode) DO UPDATE SET "
              + ",".join(f"{k}=excluded.{k}" for k in cols[1:]) + ",updated_at=excluded.updated_at", [w.get(k) for k in cols] + [db.now()])
    wid[w["episode"]] = c.execute("SELECT id FROM works WHERE episode=?", (w["episode"],)).fetchone()[0]
    for k in ("final_video","script","storyboard","cover","publish_caption"):
        if w[k]: db.register_file(c, w[k], k)

# ---------- 真实指标（用户提供的创作者中心导出/截图） ----------
import openpyxl, warnings; warnings.filterwarnings("ignore")
x = f"{W}/douyin-growth/data/roadster_export_2026-10-18.xlsx"
ws = openpyxl.load_workbook(x).active; hdr = [h.value for h in ws[1]]
for row in ws.iter_rows(min_row=2, values_only=True):
    if not row[0]: continue
    r = dict(zip(hdr, row)); f = lambda k: None if r.get(k) in (None, "-") else float(r[k])
    c.execute("""INSERT OR REPLACE INTO work_metrics(work_id,platform,captured_at,window,source,plays,completion_rate,completion_5s,bounce_2s,avg_watch_s,
        likes,shares,comments,collects,profile_visits,followers_gained,cover_ctr,raw) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (wid["LEGACY-roadster-v4"], "抖音", "2026-10-18 13:23", "发布后约24h", f"创作者中心导出 xlsx：{x}", int(f("播放量")), f("完播率"), f("5s完播率"),
         f("2s跳出率"), f("平均播放时长"), int(f("点赞量")), int(f("分享量")), int(f("评论量")), int(f("收藏量")), int(f("主页访问量")), int(f("粉丝增量")),
         f("封面点击率"), json.dumps(r, ensure_ascii=False, default=str)))
    db.register_file(c, x, "metrics")
c.execute("""INSERT OR REPLACE INTO work_metrics(work_id,platform,captured_at,window,source,avg_watch_ratio,traffic_sources,search_terms,raw) VALUES(?,?,?,?,?,?,?,?,?)""",
    (wid["LEGACY-roadster-v4"], "抖音", "2026-10-18 13:26", "发布后约24h", f"创作者中心截图（用户提供）：{W}/douyin-growth/data/roadster_dashboard_2026-10-18.png，转录见 reviews/roadster_24h_2026-10-18.md",
     0.1893, json.dumps({"搜索":0.80,"推荐":0.192,"其他":0.005}, ensure_ascii=False),
     json.dumps({"搜索词":{"特斯拉Roadster为什么会飞":0.572,"特斯拉飞行汽车":0.265,"为啥能够原地起飞":0.088},
                 "看后常搜":{"roadster2飞行":0.429,"为啥能够原地起飞":0.333,"roadster怎么下压":0.238},
                 "章节点击":{"01:15 量产与售价":0.595,"00:00 引言":0.378,"00:15 飞行原理":0.027}}, ensure_ascii=False), None))
db.register_file(c, f"{W}/douyin-growth/data/roadster_dashboard_2026-10-18.png", "metrics")
c.execute("""INSERT OR REPLACE INTO work_metrics(work_id,platform,captured_at,window,source,plays,followers_gained) VALUES(?,?,?,?,?,?,?)""",
    (wid["LEGACY-roadster-v4"], "B站", "2026-10-18 10:21", "约48h", "B站后台截图（用户提供）/workspace/shared/roadster_bilibili_48h.png，转录见 roadster_24h 复盘", 18, 0))

# ---------- 内容 DNA（结构字段来自稿件/复盘文档；指标只引用 work_metrics） ----------
DNA = {
 "LEGACY-roadster-v4": dict(topic_type="科技热点+原理（发布会奇观）", hook_type="品牌名+否定句铺垫（「最出圈的不是加速，是这一下」），奇观 3.6s 才出现",
    structure="奇观→评论质疑→结论→两套系统（吸/喷）拆解→量产与售价", style="16:9 横屏 Remotion 2D+3D 示意+发布会实拍", voice="Fish TTS 男声",
    key_visuals="飞越 Semi、车底风扇、喷口", metrics_note="见 work_metrics：播放 13320、2s 跳出 40.81%、完播 7.27%、搜索 80%"),
 "LEGACY-iphone-fake": dict(topic_type="AI 造假核查（时事）", hook_type="第 0 帧满海 iPhone 画面 + 一句提问，4.5s 揭「AI 做的」，6.9s 反转「船是真沉了」",
    structure="先信后揭→真假逐条对照→识别方法", style="竖屏截图证据+贴纸+Q 版小官", voice="Fish 科普男声", key_visuals="满海漂盒、BBC 核查、Hive 99.9%",
    metrics_note="待用户导出创作者中心数据"),
 "LEGACY-canton-robot": dict(topic_type="展会新闻+原理", hook_type="球飞来→机器人回球（动作奇观）", structure="一看·二算·三打 三段原理",
    style="竖屏 实拍+动画", voice="Fish TTS", key_visuals="乒乓球轨迹、相机识别、预测落点", metrics_note="待用户导出创作者中心数据"),
}
for ep, d in DNA.items():
    c.execute("INSERT OR REPLACE INTO content_dna(work_id,topic_type,hook_type,structure,style,voice,key_visuals,metrics_note,filled_by,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
              (wid[ep], d["topic_type"], d["hook_type"], d["structure"], d["style"], d["voice"], d["key_visuals"], d["metrics_note"], "ingest_seed（据稿件与复盘文档）", db.now()))

# ---------- 选题库 ----------
def topic(title, status, note=None, src=None, why=None, q=None):
    hh = db.h("topic", db.norm(title))
    c.execute("""INSERT INTO topics(title,core_question,status,why_not_made,first_seen,last_seen,source_path,note,hash,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)
       ON CONFLICT(hash) DO UPDATE SET status=excluded.status, why_not_made=COALESCE(excluded.why_not_made,why_not_made),
       note=COALESCE(excluded.note,note), source_path=COALESCE(source_path,excluded.source_path), core_question=COALESCE(excluded.core_question,core_question), updated_at=excluded.updated_at""",
       (title, q, status, why, "2026-10-19", db.now()[:10], src, note, hh, db.now()))
    return c.execute("SELECT id FROM topics WHERE hash=?", (hh,)).fetchone()[0]
T = {
 "光遗传学（2026诺奖）": ("制作中", "LEGACY-optogenetics", None),
 "DeepSeek V4.1 动画实测": ("暂缓", "LEGACY-deepseek-noon", "用户 10-20 取消午槽"),
 "张雪机车水上漂": ("暂缓", "LEGACY-zhangxue-water", "用户 10-20 取消晚槽；1080 成片已做未发"),
 "这些iPhone是假的": ("已制作", "LEGACY-iphone-fake", None),
 "特斯拉 Roadster 为什么会飞": ("已制作", "LEGACY-roadster-v4", None),
 "Roadster 下压 + 原地起飞（续集）": ("暂缓", "LEGACY-roadster-downforce", "停档；搜索数据显示「为啥能够原地起飞」「roadster怎么下压」是看后常搜"),
 "广交会机器人「一看二算三打」": ("已制作", "LEGACY-canton-robot", None),
}
for t, (st, ep, why) in T.items():
    tid = topic(t, st, why=why); db.link(c, "topic", tid, "made_as", "work", wid[ep])
for f in (f"{W}/research/选题线索_20261019.md", f"{W}/topics/next_topics_2026-10-19.md"):
    for m in re.finditer(r"^## (?:主推|备选|候选) ?\d｜(.+)$", open(f, encoding="utf-8").read(), re.M):
        t = re.sub(r"（.*?）\s*$", "", m.group(1)).strip()
        if any(k in t for k in ("广交会", "DeepSeek", "Roadster 续集")): continue
        topic(t, "候选", note=f"来自 {pathlib.Path(f).name}", src=f, why="当时排期未选")

# ---------- 动画资产库 ----------
def asset(name, kind, project, path, tech, tags, desc, notes=None, lic=None, ai=0):
    hh = db.h("asset", path or name)
    fid = db.register_file(c, path, kind) if path and pathlib.Path(path).is_file() and pathlib.Path(path).stat().st_size < 200e6 else None
    c.execute("""INSERT INTO anim_assets(name,kind,project,path,tech,tags,description,reusable_notes,license,ai_generated,file_id,hash,updated_at)
       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(hash) DO UPDATE SET name=excluded.name,tags=excluded.tags,description=excluded.description,
       reusable_notes=COALESCE(excluded.reusable_notes,reusable_notes),license=COALESCE(excluded.license,license),file_id=excluded.file_id,updated_at=excluded.updated_at""",
       (name, kind, project, path, tech, tags, desc, notes, lic, ai, fid, hh, db.now()))
    return c.execute("SELECT id FROM anim_assets WHERE hash=?", (hh,)).fetchone()[0]
PROJ = {  # 工程 → (work, 标签)
 f"{W}/optogenetics/remotion": ("LEGACY-optogenetics", "2D 科普 字幕卡 时间戳驱动 印章 显微 绿藻 神经元 光"),
 f"{W}/zhangxue-water/remotion": ("LEGACY-zhangxue-water", "3D three.js 水面 摩托 竖屏 实拍+3D"),
 f"{W}/canton-robot/remotion": ("LEGACY-canton-robot", "实拍+动画 竖屏 3D 乒乓球 轨迹"),
 f"{W}/iphone-fake/v2/remotion": ("LEGACY-iphone-fake", "截图证据 贴纸 弹幕 小官 字幕 核查"),
 f"{W}/roadster-downforce/remotion": ("LEGACY-roadster-downforce", "物理示意 下压力 竖屏"),
 f"{W}/roadster-downforce/rv1": ("LEGACY-roadster-downforce", "汽车 3D 转场 warp 下压 风扇 音效"),
 f"{W}/topics/tesla-roadster/remotion": ("LEGACY-roadster-v4", "汽车 3D 横屏 B站 转场 飞行"),
 f"{W}/pi/remotion": ("SAMPLE-pi", "数学 圆周率 课程 几何 小学 讲题"),
 f"{W}/video-workflows/projects/gradient-descent": ("SAMPLE-gradient-descent", "数学 梯度下降 图表 粉笔 教学 AI 原理"),
}
for proj, (ep, tags) in PROJ.items():
    pid = asset(pathlib.Path(proj).parent.name + "/" + pathlib.Path(proj).name, "project", proj, proj, "Remotion 4.0.536", tags,
                f"Remotion 工程（{ep}）", "复制源码到 projects/<EP>/remotion/，软链 node_modules")
    db.link(c, "asset", pid, "used_in", "work", wid[ep])
    for f in sorted(pathlib.Path(proj).rglob("*.ts*")):
        if "node_modules" in f.parts or "_v2_backup" in f.parts or f.suffix not in (".ts", ".tsx") or f.name.endswith(".d.ts"): continue
        src = f.read_text(encoding="utf-8", errors="ignore")
        exps = sorted(set(re.findall(r"export (?:const|function|default function|class) (\w+)", src)))
        if not exps: continue
        three = "@remotion/three" in src or "three" in re.findall(r"from ['\"]([^'\"]+)", src)
        aid = asset(f"{f.stem}（{pathlib.Path(proj).parent.name}）", "scene3d" if three else "component", proj, str(f), "Remotion" + (" + three" if three else ""),
                    tags, f"导出：{', '.join(exps[:12])}；{len(src.splitlines())} 行")
        db.link(c, "asset", aid, "part_of", "asset", pid)
CUR = [  # 精选：最值得复用的
 ("「丞」朱印角标", "brand", f"{W}/brand/v2/avatar_1_朱印丞.png", "印章 角标 品牌 水印", "全片统一角标（硬规则 2）", "按 brand/v2/README.md 规范放置"),
 ("Q 版小官贴纸 思考/惊讶/点赞/盖章", "image", f"{W}/brand/v2/qban", "小官 贴纸 表情 Q版 角色", "品牌 Q 版角色与贴纸；透明底在 qban/transparent", None),
 ("得意黑/思源字体", "font", f"{W}/brand/v2/fonts", "字体 字幕 标题", "品牌字体", None),
 ("封面模板 16:9 空白", "template", f"{W}/brand/v2/cover_template_16x9_blank.png", "封面 模板", "横版封面底", None),
 ("光遗传学 Commons 实拍证据片段", "footage", f"{W}/optogenetics/source/commons", "显微 绿藻 衣藻 线虫 小鼠 斑马鱼 神经元 光刺激 实拍",
  "Wikimedia Commons 科研实拍（各自 CC 授权，见 optogenetics/refs/commons_meta.json）", "1 秒级证据镜头；分辨率低，放大会糊；须署名"),
 ("看片工具 watch.py", "tool", f"{W}/tools/watch.py", "看视频 逐字稿 拼图 评论", "链接/本地视频→元数据、逐字稿、拼图", None),
 ("Fish TTS 合成+时间戳", "tool", f"{W}/zhangxue-water/vo/fish.py", "配音 TTS 时间戳", "Fish 合成脚本", "默认模型 s2.1-pro-free"),
]
for n, k, p, tags, d, notes in CUR:
    if ex(p): asset(n, k, None, p, None, tags, d, notes)
meta = json.load(open(f"{W}/optogenetics/refs/commons_meta.json", encoding="utf-8"))
for m in meta:
    loc = m.get("local"); p = None
    if loc:
        for cand in (f"{W}/optogenetics/source/commons/{loc}",):
            p = ex(cand)
    if not p: continue
    artist = re.sub(r"<[^>]+>", "", m.get("artist") or "")
    asset(m["title"].replace("File:", ""), "footage" if p.endswith((".mp4", ".gif")) else "image", f"{W}/optogenetics", p, None,
          "光遗传学 科研 实拍 Commons", re.sub(r"<[^>]+>", "", m.get("desc") or "")[:300], f"署名：{artist}；原址 {m.get('url','').split('?')[0]}", m.get("lic"))
for f in sorted(pathlib.Path(f"{W}/optogenetics/source/commons").glob("*.mp4")):
    asset(f.stem, "footage", f"{W}/optogenetics", str(f), None, "光遗传学 科研 实拍 Commons 显微",
          "科研实拍片段（授权见 optogenetics/source/README.md 与 refs/commons_meta.json）", "1 秒级证据镜头", "CC（逐条见来源文件，未逐条核）")

# ---------- BGM 与音效库 ----------
def bgm(kind, title, artist=None, category=None, use=None, path=None, url=None, src_note=None, notes=None, lic=None):
    hh = db.h("bgm", kind, path or url or title, title)
    fid = db.register_file(c, path, kind) if path else None
    c.execute("""INSERT INTO bgm(kind,title,artist,category,use_case,duration_s,file_id,file_path,source_url,source_note,notes,hash,updated_at)
       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(hash) DO UPDATE SET category=excluded.category,use_case=excluded.use_case,notes=excluded.notes,updated_at=excluded.updated_at""",
       (kind, title, artist, category, use, dur(path) if path else None, fid, path, url, src_note, notes, hh, db.now()))
    bid = c.execute("SELECT id FROM bgm WHERE hash=?", (hh,)).fetchone()[0]
    for plat, scope, name, ev in (lic or []):
        c.execute("INSERT OR REPLACE INTO bgm_license(bgm_id,platform,scope,license_name,evidence,checked_at) VALUES(?,?,?,?,?,?)", (bid, plat, scope, name, ev, db.now()[:10]))
    return bid
for r in csv.DictReader(open(f"{W}/research/bgm_素材库_20261019.csv", encoding="utf-8-sig")):
    bgm("bgm", r["曲名"], r["作者"], r["分类"], f'{r["用法"]}；适合：{r["适合"]}', None, r["来源链接"], "抖音同类爆款视频用曲（对标观察）", r["版权注意"],
        [("douyin", "未核实", None, f'对标视频在用≠授权；{r["版权注意"]}'), ("bilibili", "未核实", None, "未查")])
for srcmd in (f"{W}/iphone-fake/v2/assets/sfx/SOURCES.md", f"{W}/iphone-fake/v2/assets/sfx_v3/SOURCES.md"):
    base = pathlib.Path(srcmd).parent
    for line in open(srcmd, encoding="utf-8"):
        m = re.match(r"\|\s*([\w.]+\.(?:wav|mp3))\s*\|(.+)\|\s*$", line)
        if not m: continue
        cells = [x.strip() for x in m.group(2).split("|")]
        p = ex(str(base / m.group(1))) or ex(str(base / "raw" / m.group(1)))
        url = next((re.search(r"https?://\S+?/", x).group(0) for x in cells if "http" in x), None)
        title = cells[-1] if len(cells) == 3 else (cells[1] if len(cells) > 1 else m.group(1))
        ok = "Mixkit" in m.group(2) and "未核实" not in m.group(2)
        bgm("sfx", f"{m.group(1)} — {title}", "Mixkit", "音效", None, p, url, f"来源记录 {srcmd}",
            ("V3 在用" if "在用" in m.group(2) else None),
            [("all", "允许商用" if ok else "未核实", "Mixkit Sound Effects Free License" if ok else None, srcmd)])
for d in (f"{W}/canton-robot/remotion/public/sfx", f"{W}/roadster-downforce/rv1/public/sfx"):
    for f in sorted(pathlib.Path(d).glob("*.wav")):
        bgm("bgm" if f.stem.startswith(("bgm", "bed")) else "sfx", f"{f.name}（{pathlib.Path(d).parts[2]}）", None, "工程内音频", None, str(f), None,
            f"工程目录 {d}；来源未记录", None, [("all", "未核实", None, "工程内无来源记录")])

# ---------- 创作经验库 ----------
L = [
 ("长期偏好", "硬规则 6 条：字幕一句一卡；全片统一「丞」朱印角标；发布不挂无关组件和定位；画面不做 PPT 式示意图卡，用连续运动画面带；文案通过才配音、配音听审通过才对齐画面、不交无声骨架预览；改稿按段验收不全片重渲。", None, "用户 2026-10-20，config/workflow_spec.md §1"),
 ("长期偏好", "默认 TTS 用 Fish s2.1-pro-free；PC 开着就在 PC 渲染；抽帧看片交 qoder flash 省额度；创意/文案建议路由 Opus 5.5（非硬性）。", None, "用户 2026-10-20"),
 ("长期偏好", "采集只走 skill douyin-field-collect。", None, "用户 2026-10-20"),
 ("单期意见", "光遗传学：用户更喜欢第一版整篇配音 vo_master.wav + v3 开头动画做法，不再改配音；拒绝事实修正与压缩，按原稿逐字。", "LEGACY-optogenetics", "用户 2026-10-20"),
 ("单期意见", "光遗传学：不用 3D，走 2D 动画 + 1 秒级实拍证据 + 少量标注「AI 生成」镜头。", "LEGACY-optogenetics", "用户 2026-10-20"),
 ("真实数据", "Roadster V4 抖音约 24h：播放 13320，2s 跳出率 40.81%，5s 完播 46.40%，完播率 7.27%，平均播放 16.96s；流量来源搜索 80%、推荐 19.2%；推荐约 10-17 21:00 停止。", "LEGACY-roadster-v4", "创作者中心导出 xlsx + 截图（用户提供）"),
 ("真实数据", "Roadster 观众搜索词与看后搜：「为什么会飞」57.2%；看后搜「为啥能够原地起飞」33.3%、「roadster怎么下压」23.8%；章节点击「量产与售价」59.5% 最高。", "LEGACY-roadster-v4", "创作者中心截图（用户提供）"),
 ("真实数据", "Roadster B 站约 48h：18 播放、0 涨粉。", "LEGACY-roadster-v4", "B站后台截图（用户提供）"),
 ("未验证推测", "Roadster 前 2 秒流失主因可能是：奇观 3.6s 才出现、首句铺垫式、横屏在竖屏流里主体太小、13s 自我介绍（基于 V3 工程推断，V4 未核）。", "LEGACY-roadster-v4", "reviews/roadster_24h_2026-10-18.md"),
 ("未验证推测", "主要靠搜索流量时，标题/文案前置搜索词可能更有效（单条数据，不下定论）。", "LEGACY-roadster-v4", "roadster 复盘"),
]
for t, text, ep, src in L:
    c.execute("INSERT OR IGNORE INTO lessons(text,type,work_id,source,created_at,hash) VALUES(?,?,?,?,?,?)",
              (text, t, wid.get(ep), src, db.now(), db.h("lesson", db.norm(text))))

# ---------- 关系：需求 → 已制作选题 ----------
for t, st in c.execute("SELECT id,status FROM topics").fetchall():
    if st == "已制作":
        c.execute("""UPDATE demands SET status='已制作', updated_at=? WHERE status='待研究' AND id IN
                     (SELECT from_id FROM links WHERE from_type='demand' AND rel='seen_in' AND to_type='topic' AND to_id=?)""", (db.now(), t))
db.reindex(c); c.commit()
for tb in ("works","work_metrics","content_dna","topics","demands","demand_sightings","comments","ref_videos","bgm","bgm_license","anim_assets","lessons","links","files","collections"):
    print(tb, c.execute(f"SELECT count(*) FROM {tb}").fetchone()[0])
