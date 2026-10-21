#!/usr/bin/env python3
"""资产库检索入口。
  python3 scripts/search.py q "绿藻 光" [--lib demand,bgm,asset,work,topic,lesson,comment,video] [--status 待研究] [--since 2026-10-01] [-n 20]
  python3 scripts/search.py radar [--old-days 14] [--recent-days 7] [--min-seen 2]     # 需求复活雷达
  python3 scripts/search.py bgm "神秘 渐强" [--platform douyin] [--usable]              # 只看已核授权
  python3 scripts/search.py show <lib> <id>       python3 scripts/search.py status <demand_id> 值得制作 [--note ..]
  python3 scripts/search.py stats
  python3 scripts/search.py insights              # 数据规律简报（选题/写稿前读）
  python3 scripts/search.py feedback "开头 跳出"     # 历史反馈检索：findings/建议/假设/经验/真实搜索词（选题·脚本·分镜阶段必查）
检索规则：空格分词、AND；≥3 字的词走 FTS5 trigram MATCH（bm25 排序），1–2 字的词用 LIKE 子串匹配。"""
import sys, json, pathlib, argparse, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db

def fts_query(c, q, libs=None, n=20):
    terms = [t for t in q.split() if t]
    long_ = [t for t in terms if len(t) >= 3]; short = [t for t in terms if len(t) < 3]
    where, args = [], []
    if long_:
        where.append("fts MATCH ?"); args.append(" AND ".join('"' + t.replace('"', '""') + '"' for t in long_))
    for t in short:
        where.append("(title LIKE ? OR body LIKE ? OR tags LIKE ?)"); args += [f"%{t}%"] * 3
    if libs:
        where.append("lib IN (%s)" % ",".join("?" * len(libs))); args += libs
    order = "bm25(fts)" if long_ else "lib"
    sql = f"SELECT lib, ref_id, title, substr(body,1,120) body, tags FROM fts WHERE {' AND '.join(where) or '1'} ORDER BY {order} LIMIT ?"
    return c.execute(sql, args + [n * 5]).fetchall()

def enrich(c, r):
    lib, i = r["lib"], r["ref_id"]
    if lib == "demand":
        d = c.execute("SELECT kind,status,first_seen,last_seen,seen_count,max_likes FROM demands WHERE id=?", (i,)).fetchone()
        return d, f"[{d['kind']}|{d['status']}] 见{d['seen_count']}次 赞≤{d['max_likes']} {d['first_seen'][:10]}→{d['last_seen'][:10]}"
    if lib == "bgm":
        lic = c.execute("SELECT platform||':'||scope FROM bgm_license WHERE bgm_id=?", (i,)).fetchall()
        b = c.execute("SELECT kind,file_path,source_url FROM bgm WHERE id=?", (i,)).fetchone()
        return b, f"[{b['kind']}] 授权 {' '.join(x[0] for x in lic)} {b['file_path'] or b['source_url'] or ''}"
    if lib == "asset":
        a = c.execute("SELECT kind,path FROM anim_assets WHERE id=?", (i,)).fetchone(); return a, f"[{a['kind']}] {a['path']}"
    if lib == "work":
        w = c.execute("SELECT status,published_at,final_video FROM works WHERE id=?", (i,)).fetchone(); return w, f"[{w['status']}] {w['published_at'] or ''} {w['final_video'] or ''}"
    if lib == "topic":
        t = c.execute("SELECT status,why_not_made FROM topics WHERE id=?", (i,)).fetchone(); return t, f"[{t['status']}] {t['why_not_made'] or ''}"
    if lib == "video":
        v = c.execute("SELECT likes,url,first_seen FROM ref_videos WHERE id=?", (i,)).fetchone(); return v, f"赞{v['likes']} {v['url']}"
    if lib == "comment":
        m = c.execute("SELECT likes,posted_at,video_id FROM comments WHERE id=?", (i,)).fetchone(); return m, f"赞{m['likes']} {m['posted_at']} 视频{m['video_id']}"
    return None, ""

def cmd_q(c, a):
    rows = fts_query(c, a.query, a.lib.split(",") if a.lib else None, a.n); out = 0
    for r in rows:
        rec, info = enrich(c, r)
        if a.status and r["lib"] == "demand" and rec["status"] != a.status: continue
        if a.since and r["lib"] == "demand" and rec["last_seen"] < a.since: continue
        label = (r['body'] if r['lib'] in ('comment','lesson') else r['title']) or ''
        print(f"{r['lib']:7} #{r['ref_id']:<5} {label[:50]!s:52} {info}")
        out += 1
        if out >= a.n: break
    print(f"-- {out} 条（查询：{a.query}）")

def cmd_radar(c, a):
    """旧需求复活：首次见到早于 old-days 天前，最近 recent-days 天又出现，状态不是 已制作/不适合，且未关联到已发布作品。"""
    now = datetime.datetime.now(db.TZ)
    old = (now - datetime.timedelta(days=a.old_days)).strftime("%Y-%m-%d %H:%M:%S")
    rec = (now - datetime.timedelta(days=a.recent_days)).strftime("%Y-%m-%d %H:%M:%S")
    sql = """SELECT d.id, d.text, d.kind, d.status, d.first_seen, d.last_seen, d.seen_count, d.max_likes,
              (SELECT count(*) FROM demand_sightings s WHERE s.demand_id=d.id AND s.seen_at>=?) recent_n,
              (SELECT count(DISTINCT collection_id) FROM demand_sightings s WHERE s.demand_id=d.id) n_coll,
              (SELECT group_concat(DISTINCT t.title) FROM links l JOIN topics t ON t.id=l.to_id WHERE l.from_type='demand' AND l.from_id=d.id AND l.to_type='topic') topics
             FROM demands d WHERE d.status NOT IN ('已制作','不适合') AND d.first_seen < ? AND d.last_seen >= ?
             AND (SELECT count(DISTINCT collection_id) FROM demand_sightings s WHERE s.demand_id=d.id) >= ?
             ORDER BY recent_n DESC, d.max_likes DESC LIMIT ?"""
    rows = c.execute(sql, (rec, old, rec, a.min_seen, a.n)).fetchall()
    print(f"需求复活雷达：首见早于 {old[:16]}，{rec[:16]} 后再次出现，≥{a.min_seen} 次不同采集，未制作")
    for r in rows:
        print(f"#{r['id']:<5} [{r['kind']}|{r['status']}] {r['text'][:40]:42} 首见{r['first_seen'][:10]} 最近{r['last_seen'][:10]} 近期{r['recent_n']}次/共{r['n_coll']}批 赞≤{r['max_likes']} 选题:{r['topics'] or '-'}")
    print(f"-- {len(rows)} 条")

def cmd_bgm(c, a):
    rows = fts_query(c, a.query, ["bgm"], a.n * 3); out = 0
    for r in rows:
        lic = {x["platform"]: x["scope"] for x in c.execute("SELECT platform,scope FROM bgm_license WHERE bgm_id=?", (r["ref_id"],))}
        sc = lic.get(a.platform) or lic.get("all") or "未核实"
        if a.usable and sc not in ("允许商用", "允许(需署名)"): continue
        b = c.execute("SELECT * FROM bgm WHERE id=?", (r["ref_id"],)).fetchone()
        used = c.execute("SELECT group_concat(w.title,' / ') FROM links l JOIN works w ON w.id=l.to_id WHERE l.from_type='bgm' AND l.from_id=? AND l.to_type='work'", (b["id"],)).fetchone()[0]
        print(f"#{b['id']:<4}[{b['kind']}] {b['title'][:46]:48} {a.platform}:{sc} 评分:{b['user_rating'] or '-'} 时长:{b['duration_s'] and round(b['duration_s'],1)} 用过:{used or '-'} {b['file_path'] or b['source_url'] or ''}")
        out += 1
        if out >= a.n: break
    print(f"-- {out} 条")

TBL = {"demand": "demands", "topic": "topics", "bgm": "bgm", "asset": "anim_assets", "work": "works", "lesson": "lessons", "comment": "comments", "video": "ref_videos"}
def cmd_show(c, a):
    r = c.execute(f"SELECT * FROM {TBL[a.lib]} WHERE id=?", (a.id,)).fetchone(); print(json.dumps(dict(r), ensure_ascii=False, indent=1))
    if a.lib == "demand":
        for s in c.execute("SELECT seen_at,source_kind,source_ref,keyword,likes,posted_at FROM demand_sightings WHERE demand_id=? ORDER BY seen_at", (a.id,)): print(" 见于", tuple(s))
    if a.lib == "work":
        for m in c.execute("SELECT * FROM work_metrics WHERE work_id=?", (a.id,)): print(" 指标", {k: m[k] for k in m.keys() if m[k] is not None and k != "raw"})
        d = c.execute("SELECT * FROM content_dna WHERE work_id=?", (a.id,)).fetchone()
        if d: print(" DNA", dict(d))
    for l in c.execute("SELECT * FROM links WHERE (from_type=? AND from_id=?) OR (to_type=? AND to_id=?) LIMIT 30", (a.lib, a.id, a.lib, a.id)): print(" 关系", tuple(l)[:5])

def cmd_status(c, a):
    c.execute("UPDATE demands SET status=?, note=COALESCE(?,note), updated_at=? WHERE id=?", (a.value, a.note, db.now(), a.id)); db.reindex(c); c.commit(); print("ok")

def cmd_stats(c, a):
    for tb in ("demands","demand_sightings","comments","ref_videos","topics","bgm","bgm_license","anim_assets","works","work_metrics","content_dna","lessons","links","files","collections"):
        print(f"{tb:18}{c.execute(f'SELECT count(*) FROM {tb}').fetchone()[0]}")
    print("需求状态", dict(c.execute("SELECT status,count(*) FROM demands GROUP BY status").fetchall()))

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); sp = ap.add_subparsers(dest="cmd", required=True)
p = sp.add_parser("q"); p.add_argument("query"); p.add_argument("--lib"); p.add_argument("--status"); p.add_argument("--since"); p.add_argument("-n", type=int, default=20)
p = sp.add_parser("radar"); p.add_argument("--old-days", type=float, default=14); p.add_argument("--recent-days", type=float, default=7); p.add_argument("--min-seen", type=int, default=2); p.add_argument("-n", type=int, default=30)
p = sp.add_parser("bgm"); p.add_argument("query"); p.add_argument("--platform", default="douyin"); p.add_argument("--usable", action="store_true"); p.add_argument("-n", type=int, default=15)
p = sp.add_parser("show"); p.add_argument("lib", choices=TBL); p.add_argument("id", type=int)
p = sp.add_parser("status"); p.add_argument("id", type=int); p.add_argument("value", choices=["待研究","值得制作","暂缓","已制作","不适合"]); p.add_argument("--note")
sp.add_parser("stats")
sp.add_parser("insights", help="数据规律简报（= insights.py show）")
p = sp.add_parser("feedback", help="历史反馈检索"); p.add_argument("query")
def cmd_feedback(c, a):
    import feedback as fb; print("\n".join(fb.feedback_search(c, a.query)))
def cmd_insights(c, a):
    import insights; insights.show(c)
a = ap.parse_args(); c = db.connect()
{"q": cmd_q, "radar": cmd_radar, "bgm": cmd_bgm, "show": cmd_show, "status": cmd_status, "stats": cmd_stats, "insights": cmd_insights, "feedback": cmd_feedback}[a.cmd](c, a)
