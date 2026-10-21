#!/usr/bin/env python3
"""改进建议审批与经验回写（只有用户明确批准的建议才进 lessons）。
  python3 scripts/approve_suggestion.py list [--status 待批]
  python3 scripts/approve_suggestion.py approve <id> [--note "用户原话/日期"] [--text "改写后的经验表述"]   # → lessons(type=已批改进)，假设→验证中
  python3 scripts/approve_suggestion.py reject <id> [--note ...]                                           # 拒绝：建议保留，假设不动
  python3 scripts/approve_suggestion.py hyp <hyp_id> 已否定|已支持|验证中|未验证 --result "依据"            # 实验结论（否定的也保留）
  python3 scripts/approve_suggestion.py track [--dry-run]     # 给已批经验挂后续真实表现：经验批准之后发布、且有已核快照的作品
规则：approve/reject 只能在用户明确表态后执行（Bot 不得自批）；--note 写用户原话与时间。"""
import sys, json, argparse, pathlib, statistics as st
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
TRACK = [("bounce_2s", "2s跳出率", -1), ("completion_5s", "5s完播率", 1), ("avg_watch_ratio", "均播占比", 1), ("search_share", "搜索占比", 0)]

def cmd_list(c, a):
    for r in c.execute("SELECT s.*, w.episode FROM suggestions s LEFT JOIN works w ON w.id=s.work_id" + (" WHERE s.status=?" if a.status else "") + " ORDER BY s.id", ((a.status,) if a.status else ())):
        print(f"#{r['id']:<3}[{r['status']}｜{r['stage']}] {r['episode']}：{r['text']}" + (f"  → lesson#{r['lesson_id']}" if r["lesson_id"] else ""))

def cmd_decide(c, a, status):
    s = c.execute("SELECT * FROM suggestions WHERE id=?", (a.id,)).fetchone()
    if not s: sys.exit("没有这条建议")
    if s["status"] != "待批" and not a.force: sys.exit(f"已是「{s['status']}」；要改用 --force")
    c.execute("UPDATE suggestions SET status=?, decided_at=?, decision_note=? WHERE id=?", (status, db.now(), a.note, a.id))
    if status == "已批":
        w = c.execute("SELECT episode FROM works WHERE id=?", (s["work_id"],)).fetchone()
        text = a.text or s["text"]; text = f"{text}（来自 {w['episode'] if w else '?'} suggestion#{s['id']}；实验：{s['experiment'] or '—'}）"
        lid = c.execute("INSERT INTO lessons(text,type,work_id,source,created_at,hash,suggestion_id,stage) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(hash) DO UPDATE SET superseded=0",
                        (text, "已批改进", s["work_id"], f"用户批准 {db.now()} {a.note or ''}".strip(), db.now(), db.h("lesson", "sug", s["id"]), s["id"], s["stage"])).lastrowid
        lid = lid or c.execute("SELECT id FROM lessons WHERE hash=?", (db.h("lesson", "sug", s["id"]),)).fetchone()[0]
        c.execute("UPDATE suggestions SET lesson_id=? WHERE id=?", (lid, a.id))
        if s["hypothesis_id"]: c.execute("UPDATE hypotheses SET status='验证中', updated_at=? WHERE id=? AND status='未验证'", (db.now(), s["hypothesis_id"]))
        print(f"已批 → lesson#{lid}")
    else: print("已拒绝（建议与假设保留）")
    db.reindex(c); c.commit()

def cmd_hyp(c, a):
    c.execute("UPDATE hypotheses SET status=?, result=?, updated_at=? WHERE id=?", (a.status, a.result, db.now(), a.id)); c.commit(); print("ok")

def cmd_track(c, a):
    import feedback as fb
    n = 0
    for l in c.execute("SELECT * FROM lessons WHERE type='已批改进' AND superseded=0").fetchall():
        for w in fb.published(c):
            if not w["publish_time"] or db.parse_time(w["publish_time"]) <= db.parse_time(l["created_at"]): continue
            s = fb.main_snap(c, w["id"])
            if not s or not s["verified"]: continue
            b, P, peers = fb.peer_compare(c, w, s)
            for k, name, _ in TRACK:
                if s.get(k) is None: continue
                p = P.get(k); desc = f"批准前同档作品中位数 {p['med']:.4f}（n={p['n']-1}），本条排第 {p['rank']}/{p['n']}" if p else "无同档基准"
                if a.dry_run: print(l["id"], w["id"], k, s[k], desc); continue
                c.execute("INSERT OR REPLACE INTO lesson_outcomes(lesson_id,work_id,metric,value,baseline,baseline_desc,note,at) VALUES(?,?,?,?,?,?,?,?)",
                          (l["id"], w["id"], name, s[k], p["med"] if p else None, desc, f"快照 {s['checkpoint']}（已核）；是否真按经验执行需人工确认", db.now())); n += 1
    c.commit(); print(f"挂接 {n} 条后续表现")

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); sp = ap.add_subparsers(dest="cmd", required=True)
p = sp.add_parser("list"); p.add_argument("--status")
for k in ("approve", "reject"):
    p = sp.add_parser(k); p.add_argument("id", type=int); p.add_argument("--note"); p.add_argument("--text"); p.add_argument("--force", action="store_true")
p = sp.add_parser("hyp"); p.add_argument("id", type=int); p.add_argument("status", choices=["未验证", "验证中", "已支持", "已否定"]); p.add_argument("--result", required=True)
p = sp.add_parser("track"); p.add_argument("--dry-run", action="store_true")
a = ap.parse_args(); c = db.connect()
{"list": cmd_list, "approve": lambda c, a: cmd_decide(c, a, "已批"), "reject": lambda c, a: cmd_decide(c, a, "拒绝"), "hyp": cmd_hyp, "track": cmd_track}[a.cmd](c, a)
