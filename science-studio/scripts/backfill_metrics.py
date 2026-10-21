#!/usr/bin/env python3
"""一次性回填（2026-10-21，幂等）：把文件里已有的真实数据写进 v2 表。只用文件里的真数，逐条写来源；没有的留空。
来源：
 A /workspace/douyin-growth/data/roadster_export_2026-10-18.xlsx（创作者中心导出，13:23 收到）
 B /workspace/douyin-growth/reviews/roadster_24h_2026-10-18.md（约 8.5h 页面数据；13:26 后台截图转录：流量来源、平均播放占比、搜索词、看后搜、章节点击；B站 48h）
 C 发布时间：A 的「发布时间」列（Roadster）；works.published_at（广交会，用户告知 19:05）
 D 时长：ffprobe 盒上成片（广交会 v6c、iPhone V3f、光遗传学 v1p 混音同长）；Roadster V4 成片不在盒上 → 均播÷均播占比推算，标「推算」"""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db, ingest_metrics as im
c = db.connect(); X = "/workspace/douyin-growth/data/roadster_export_2026-10-18.xlsx"; RV = "/workspace/douyin-growth/reviews/roadster_24h_2026-10-18.md"
# Roadster
c.execute("UPDATE works SET publish_time=? WHERE id=1", (db.iso("2026-10-17 12:58:53"),))
r = im.parse(X)
im.store(c, 1, "24h", "抖音", r["metrics"], [], f"创作者中心导出 xlsx {X}（10-18 13:23 收到）", db.iso("2026-10-18 13:23"),
         dict(file=X, meta=r["meta"], sheets=r["extras"]))
im.store(c, 1, "24h", "抖音", dict(search_share=0.80, recommend_share=0.192, avg_watch_ratio=0.1893),
         [], f"后台截图 /workspace/douyin-growth/data/roadster_dashboard_2026-10-18.png（10-18 13:26），转录见 {RV}", None,
         dict(screenshot={"流量来源": {"搜索": 0.80, "推荐": 0.192, "其他": 0.005}, "平均播放占比": 0.1893,
              "搜索词": {"特斯拉Roadster为什么会飞": 0.572, "特斯拉飞行汽车": 0.265, "为啥能够原地起飞": 0.088},
              "看后常搜": {"roadster2飞行": 0.429, "为啥能够原地起飞": 0.333, "roadster怎么下压": 0.238},
              "章节点击": {"01:15 量产与售价": 0.595, "00:00 引言": 0.378, "00:15 飞行原理": 0.027}}))
im.store(c, 1, "8h", "抖音", dict(plays=13000, completion_rate=0.0719, bounce_2s=0.4071), [],
         f"{RV}「约 8.5h 数据」（播放为界面显示的「1.3万」，取整值）", None, dict(note="约 8.5h；播放显示 1.3万"))
im.store(c, 1, "48h", "B站", dict(plays=18, follows_gained=0), [], f"B站后台截图 /workspace/shared/roadster_bilibili_48h.png（10-18 10:21），转录见 {RV}", db.iso("2026-10-18 10:21"), {})
# 其它已发布作品：只有发布时间/时长，没有数据
c.execute("UPDATE works SET publish_time=? WHERE id=3", (db.iso("2026-10-19 19:05"),))
c.execute("UPDATE works SET planned_publish_time=?, publish_asked=0 WHERE id=7", (db.iso("2026-10-21 20:00"),))
DNA = {1: dict(hook_class="铺垫式", topic_class="科技热点+原理", duration_s=89.6, duration_note="推算：均播 16.96s ÷ 均播占比 18.93%（V4 成片不在盒上）"),
       2: dict(hook_class="奇观首帧+提问", topic_class="AI造假核查（时事）", duration_s=75.76, duration_note="ffprobe V3f 1080p（发布版）"),
       3: dict(hook_class="动作奇观", topic_class="展会新闻+原理", duration_s=33.87, duration_note="ffprobe 广交会 1080p 成片"),
       7: dict(hook_class="反差提问", topic_class="科学大事+原理（诺奖）", duration_s=174.9, duration_note="成片 174.9s")}
for wid, d in DNA.items():
    c.execute("INSERT INTO content_dna(work_id,updated_at) VALUES(?,?) ON CONFLICT(work_id) DO NOTHING", (wid, db.now()))
    c.execute("UPDATE content_dna SET hook_class=?, topic_class=?, duration_s=COALESCE(duration_s,?), duration_note=?, updated_at=? WHERE work_id=?",
              (d["hook_class"], d["topic_class"], d["duration_s"], d["duration_note"], db.now(), wid))
c.execute("UPDATE meta SET v=? WHERE k='schema_version'", ("2",)); c.execute("INSERT OR REPLACE INTO meta VALUES('backfill_v2', ?)", (db.now(),))
c.commit()
for r in c.execute("SELECT work_id,platform,checkpoint,plays,bounce_2s,completion_rate,search_share,source FROM metrics_snapshots ORDER BY work_id"): print(dict(r))
for r in c.execute("SELECT id,episode,status,publish_time,planned_publish_time,checkpoints_done FROM works WHERE id IN (1,2,3,7)"): print(dict(r))
