#!/usr/bin/env python3
"""记录「已发布」：python3 scripts/mark_published.py <EP|work_id> --time 'YYYY-MM-DD HH:MM' [--url 抖音链接] [--platform 抖音]
      [--title 实际发布标题] [--search-first yes|no]
      python3 scripts/mark_published.py <EP|work_id> --plan 'YYYY-MM-DD HH:MM'     # 只设计划发布时间（待发布）
时间按 Asia/Shanghai。同时更新 state.json（若有 EP 项目目录）。之后检查点由 due_checkpoints.py 提醒。"""
import sys, json, pathlib, argparse
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("work"); ap.add_argument("--time"); ap.add_argument("--plan"); ap.add_argument("--url"); ap.add_argument("--platform")
ap.add_argument("--title"); ap.add_argument("--search-first", choices=["yes", "no"])
a = ap.parse_args()
if not (a.time or a.plan): sys.exit("要给 --time（已发布）或 --plan（计划时间）")
c = db.connect(); w = db.find_work(c, a.work)
if a.plan:
    c.execute("UPDATE works SET planned_publish_time=?, publish_asked=0, updated_at=? WHERE id=?", (db.iso(a.plan), db.now(), w["id"]))
if a.time:
    t = db.iso(a.time)
    c.execute("""UPDATE works SET status='已发布', publish_time=?, published_at=?, video_url=COALESCE(?,video_url),
                 platform=COALESCE(?,platform), title=COALESCE(?,title), updated_at=? WHERE id=?""",
              (t, t[:16].replace("T", " "), a.url, a.platform, a.title, db.now(), w["id"]))
if a.search_first:
    c.execute("INSERT INTO content_dna(work_id,updated_at) VALUES(?,?) ON CONFLICT(work_id) DO NOTHING", (w["id"], db.now()))
    c.execute("UPDATE content_dna SET title_search_first=? WHERE work_id=?", (1 if a.search_first == "yes" else 0, w["id"]))
c.commit()
ep = db.ROOT / "projects" / w["episode"]
if (ep / "state.json").exists():
    import stateutil as su
    s = su.load(ep)
    if a.time:
        s["stage_status"] = "已发布"; s["stages"]["H_delivery"] = "done"
        s["next_action"] = "发布后：按 due_checkpoints.py 提醒导出 2h/24h/72h 数据 → ingest_metrics → diagnose；24h 后 harvest_comments"
        s["project_paths"]["video_url"] = a.url or s["project_paths"].get("video_url")
        s["log"].append(f"{su.now()} 已发布 {db.iso(a.time)} {a.url or ''}")
    if a.plan: s["project_paths"]["planned_publish_time"] = db.iso(a.plan); s["log"].append(f"{su.now()} 计划发布 {db.iso(a.plan)}")
    su.save(ep, s)
r = c.execute("SELECT id,episode,status,publish_time,planned_publish_time,video_url FROM works WHERE id=?", (w["id"],)).fetchone()
print(json.dumps(dict(r), ensure_ascii=False))
