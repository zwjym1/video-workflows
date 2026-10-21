#!/usr/bin/env python3
"""周报：python3 scripts/weekly_report.py [--date 2026-10-25] [--days 7] [--stdout]
内容：近 7 天发布（或近 7 天有新数据）的作品 × 检查点对比表；本周 insights 状态变化（新验证/推翻）；
      下周选题建议（作品回采的追更候选 follow_up_of + 需求复活雷达）；待办提醒（due_checkpoints）。
写 reviews/weekly/YYYY-Www.md（STUDIO_REVIEWS 可改目录）。不估不编：没数据的格子写「—」。"""
import sys, os, json, pathlib, argparse, subprocess, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--date"); ap.add_argument("--days", type=int, default=7); ap.add_argument("--stdout", action="store_true")
a = ap.parse_args(); c = db.connect()
end = db.parse_time(a.date + " 23:59") if a.date else db.now_dt(); start = end - dt.timedelta(days=a.days)
iy, iw, _ = end.isocalendar(); wk = f"{iy}-W{iw:02d}"
S, E = start.isoformat(timespec="seconds"), end.isoformat(timespec="seconds")
pct = lambda v: "—" if v is None else f"{v:.1%}"; num = lambda v: "—" if v is None else f"{v:,.0f}"; sec = lambda v: "—" if v is None else f"{v:.1f}"
works = c.execute("""SELECT DISTINCT w.* FROM works w LEFT JOIN metrics_snapshots m ON m.work_id=w.id
                     WHERE (w.publish_time BETWEEN ? AND ?) OR (m.ingested_at BETWEEN ? AND ?) OR (m.captured_at BETWEEN ? AND ?) ORDER BY w.publish_time""",
                  (S, E, S[:19].replace("T", " "), E[:19].replace("T", " "), S, E)).fetchall()
L = [f"# 周报 {wk}（{start:%m-%d} – {end:%m-%d}，Asia/Shanghai）", "", "## 1. 本周作品与数据", ""]
if works:
    L += ["| 作品 | 发布 | 平台·检查点 | 播放 | 2s跳出 | 5s完播 | 完播率 | 均播s | 点赞 | 分享 | 涨粉 | 搜索占比 |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for w in works:
        snaps = c.execute("SELECT * FROM metrics_snapshots WHERE work_id=? ORDER BY platform, CAST(substr(checkpoint,1,length(checkpoint)-1) AS INT)*(CASE WHEN checkpoint LIKE '%d' THEN 24 ELSE 1 END)", (w["id"],)).fetchall()
        if not snaps: L.append(f"| #{w['id']} {w['title'][:16]} | {(w['publish_time'] or '')[5:16].replace('T',' ')} | 无数据 |" + " — |" * 9)
        for s in snaps:
            L.append(f"| #{w['id']} {w['title'][:16]} | {(w['publish_time'] or '')[5:16].replace('T',' ')} | {s['platform']}·{s['checkpoint']} | {num(s['plays'])} | {pct(s['bounce_2s'])} | {pct(s['completion_5s'])} | "
                     f"{pct(s['completion_rate'])} | {sec(s['avg_watch_s'])} | {num(s['likes'])} | {num(s['shares'])} | {num(s['follows_gained'])} | {pct(s['search_share'])} |")
else: L.append("本周没有发布，也没有导入新数据。")
L += ["", "## 2. 规律变化（insights）", ""]
hist = c.execute("""SELECT h.*, i.kind FROM insights_history h JOIN insights i ON i.id=h.insight_id WHERE h.at BETWEEN ? AND ? ORDER BY h.at""",
                 (S[:16].replace("T", " "), E[:16].replace("T", " ") + "~")).fetchall()
ver = [h for h in hist if h["status"] == "已验证"]; ovr = [h for h in hist if h["status"] == "已推翻"]
L += [f"- 本周新验证：{len(ver)} 条" + "".join(f"\n  - [{h['kind']}] {h['statement']}" for h in ver),
      f"- 本周被推翻：{len(ovr)} 条" + "".join(f"\n  - [{h['kind']}] {h['statement']}" for h in ovr), "- 当前全部："]
L += [f"  - [{r['status']}｜{r['kind']}｜n={r['n']}] {r['statement']}" for r in c.execute("SELECT * FROM insights ORDER BY status, kind")] or ["  - （还没有，跑 insights.py）"]
L += ["", "## 3. 下周选题建议（来自需求库，待选题阶段核实）", ""]
fu = c.execute("""SELECT d.id, d.text, d.kind, d.status, d.max_likes, d.seen_count, w.id wid, w.title wt FROM links l JOIN demands d ON d.id=l.from_id
                  JOIN works w ON w.id=l.to_id WHERE l.from_type='demand' AND l.rel='follow_up_of' AND l.to_type='work'
                  AND d.status NOT IN ('已制作','不适合') ORDER BY d.max_likes DESC, d.seen_count DESC LIMIT 10""").fetchall()
L += [f"- 追更（#{r['wid']} {r['wt'][:12]}）：demand#{r['id']} [{r['kind']}] {r['text'][:50]}（赞≤{r['max_likes']}，见{r['seen_count']}次）" for r in fu] or ["- 追更候选：暂无（作品还没回采评论，见 harvest_comments.py）"]
try:
    rd = subprocess.run([sys.executable, str(pathlib.Path(__file__).parent / "search.py"), "radar", "-n", "5"], capture_output=True, text=True, timeout=60, env=os.environ).stdout.strip()
    L += ["- 需求复活雷达（前 5）：", "```", rd or "（无）", "```"]
except Exception as e: L.append(f"- 雷达未运行：{e}")
L += ["", "## 4. 待办提醒", ""]
try:
    due = json.loads(subprocess.run([sys.executable, str(pathlib.Path(__file__).parent / "due_checkpoints.py")], capture_output=True, text=True, timeout=60, env=os.environ).stdout)
    L += [f"- [{r['type']}] #{r['work_id']} {r['message']}" for r in due["reminders"]] or ["- 无"]
except Exception as e: L.append(f"- 读取失败：{e}")
txt = "\n".join(L) + "\n"
if a.stdout: print(txt); sys.exit()
d = pathlib.Path(os.environ.get("STUDIO_REVIEWS") or db.ROOT / "reviews") / "weekly"; d.mkdir(parents=True, exist_ok=True)
(d / f"{wk}.md").write_text(txt, encoding="utf-8"); print(txt); print("已写入", d / f"{wk}.md")
