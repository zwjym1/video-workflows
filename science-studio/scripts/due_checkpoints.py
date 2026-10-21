#!/usr/bin/env python3
"""现在（Asia/Shanghai）该提醒什么，输出 JSON：python3 scripts/due_checkpoints.py [--mark-asked] [--pretty]
提醒类型：
- checkpoint：已发布作品的 2h/24h/72h 已到点但没导入数据（可补导；若更晚的检查点已做，早的自动跳过）。
- harvest_comments：发布满 24h、有 video_url、还没采评论。
- need_url：发布满 24h、没有 video_url（采评论要链接）。
- need_publish_time：标了已发布但没有发布时间（无法排检查点）。
- ask_published：待发布作品计划时间已过 3h 以上、还没问过；--mark-asked 把这些记为已问（每条只问一次）。
环境变量 STUDIO_NOW='2026-10-22 21:00' 可固定「现在」（测试用）。"""
import sys, json, pathlib, argparse, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
CKS = [("2h", 2), ("24h", 24), ("72h", 72)]
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--mark-asked", action="store_true"); ap.add_argument("--pretty", action="store_true")
a = ap.parse_args(); c = db.connect(); now = db.now_dt(); R = []
H = lambda x: round(x.total_seconds() / 3600, 1)
for w in c.execute("SELECT * FROM works WHERE status='已发布' AND publish_time IS NOT NULL"):
    pt = db.parse_time(w["publish_time"]); done = db.jlist(w["checkpoints_done"]); age = now - pt
    hours = lambda k: int(k[:-1]) * (24 if k.endswith("d") else 1)
    latest_done = max([hours(k) for k in done] or [0])
    due = [(k, h) for k, h in CKS if k not in done and age >= dt.timedelta(hours=h) and h > latest_done]
    if due:
        k, h = due[-1]; skipped = [x for x, _ in due[:-1]]
        R.append(dict(type="checkpoint", work_id=w["id"], episode=w["episode"], title=w["title"], checkpoint=k,
                      due_at=(pt + dt.timedelta(hours=h)).isoformat(timespec="minutes"), overdue_h=H(age - dt.timedelta(hours=h)), skipped_earlier=skipped,
                      message=f"《{w['title'][:20]}》发布已 {H(age)} 小时，到 {k} 复盘点了：请在抖音创作者中心导出这条作品的数据（xlsx，最好带「观众留存」），发我就行。"
                              + (f"（{'/'.join(skipped)} 已错过，直接按 {k} 记）" if skipped else ""),
                      command=f"python3 scripts/ingest_metrics.py <xlsx> --work {w['id']} --checkpoint {k} && python3 scripts/diagnose.py {w['id']} --checkpoint {k}"))
    if age >= dt.timedelta(hours=24) and not w["comments_harvested"]:
        if w["video_url"]:
            R.append(dict(type="harvest_comments", work_id=w["id"], episode=w["episode"], title=w["title"], overdue_h=H(age - dt.timedelta(hours=24)),
                          message="发布满 24 小时，可以采评论和看后搜了（免登录、无需用户操作）。", command=f"python3 scripts/harvest_comments.py {w['id']}"))
        else:
            R.append(dict(type="need_url", work_id=w["id"], episode=w["episode"], title=w["title"],
                          message=f"《{w['title'][:20]}》要采评论区，需要这条视频的抖音链接（分享→复制链接）。",
                          command=f"python3 scripts/mark_published.py {w['id']} --time '{pt.strftime('%Y-%m-%d %H:%M')}' --url <链接>"))
for w in c.execute("SELECT * FROM works WHERE status='已发布' AND publish_time IS NULL"):
    R.append(dict(type="need_publish_time", work_id=w["id"], episode=w["episode"], title=w["title"],
                  message=f"《{w['title'][:20]}》已发布但没记发布时间，告诉我大概几点发的（和链接），我才能按检查点提醒。",
                  command=f"python3 scripts/mark_published.py {w['id']} --time 'YYYY-MM-DD HH:MM' --url <链接>"))
asked = []
for w in c.execute("SELECT * FROM works WHERE status='待发布' AND planned_publish_time IS NOT NULL AND COALESCE(publish_asked,0)=0"):
    pt = db.parse_time(w["planned_publish_time"])
    if now - pt > dt.timedelta(hours=3):
        R.append(dict(type="ask_published", work_id=w["id"], episode=w["episode"], title=w["title"], planned=pt.isoformat(timespec="minutes"),
                      overdue_h=H(now - pt), message=f"《{w['title'][:20]}》原计划 {pt.strftime('%m-%d %H:%M')} 发布，发了吗？发了的话告诉我实际时间和链接，我开始记数据。",
                      command=f"python3 scripts/mark_published.py {w['id']} --time 'YYYY-MM-DD HH:MM' --url <链接>"))
        asked.append(w["id"])
if a.mark_asked and asked:
    c.executemany("UPDATE works SET publish_asked=1 WHERE id=?", [(i,) for i in asked]); c.commit()
print(json.dumps(dict(now=now.isoformat(timespec="minutes"), count=len(R), marked_asked=asked if a.mark_asked else [], reminders=R),
                 ensure_ascii=False, indent=1 if a.pretty else None))
