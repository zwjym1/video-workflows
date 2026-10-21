#!/usr/bin/env python3
"""把 douyin-field-collect（及旧采集目录）的输出灌进资产库：评论疑问/推荐词 → demands，视频 → ref_videos，评论 → comments。
用法：
  python3 scripts/ingest_field.py <采集目录或json> [更多路径] [--topic "选题名"] [--label 说明] [--at "2026-10-20 22:48"]
  每次 douyin-field-collect 跑完立刻执行（阶段 A 硬步骤）。重复执行安全（按 hash/唯一键去重，只追加新 sighting）。
识别的文件：douyin_<id>/collect.json、douyin_<id>/comments.json、dy_search 输出（{keyword,videos} 或视频列表）、
           related_searches.json（[{keyword,chips,suggest}]）、dy_collect sug 输出（{search_sug,search_page_related}）、抖音原始 sug（sug_list）。"""
import sys, json, re, pathlib, argparse, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db

def mtime(p): return datetime.datetime.fromtimestamp(pathlib.Path(p).stat().st_mtime, db.TZ).strftime("%Y-%m-%d %H:%M:%S")
def clean_ts(s):
    if not s: return None
    m = re.match(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})(:\d{2})?", s)
    return f"{m.group(1)} {m.group(2)}{m.group(3) or ':00'}" if m else s

class Ingest:
    def __init__(s, c, root, topic=None, label=None, at=None):
        s.c, s.root, s.at_override = c, pathlib.Path(root).resolve(), at
        s.n = {"demand_new": 0, "sighting": 0, "comment": 0, "video": 0, "question": 0}
        s.topic_id = s.topic(topic) if topic else None
        r = c.execute("SELECT id FROM collections WHERE source_path=?", (str(s.root),)).fetchone()
        s.coll = r["id"] if r else c.execute("INSERT INTO collections(source_path,label,topic_hint,collected_at,ingested_at) VALUES(?,?,?,?,?)",
                    (str(s.root), label or s.root.name, topic, at or (mtime(s.root) if s.root.exists() else None), db.now())).lastrowid
        s.coll_at = at or c.execute("SELECT collected_at FROM collections WHERE id=?", (s.coll,)).fetchone()[0]

    def topic(s, title):
        hh = db.h("topic", db.norm(title)); r = s.c.execute("SELECT id FROM topics WHERE hash=?", (hh,)).fetchone()
        if r: return r["id"]
        return s.c.execute("INSERT INTO topics(title,first_seen,last_seen,source_path,hash,updated_at) VALUES(?,?,?,?,?,?)",
                           (title, db.now(), db.now(), str(s.root), hh, db.now())).lastrowid

    def demand(s, text, kind, source_kind, source_ref=None, keyword=None, likes=None, posted_at=None, seen_at=None):
        text = (text or "").strip()
        nm = db.norm(text)
        if len(nm) < 2 or len(nm) > 200: return None
        seen_at = seen_at or s.coll_at or db.now()
        hh = db.h(kind, nm); r = s.c.execute("SELECT id FROM demands WHERE hash=?", (hh,)).fetchone()
        if r: did = r["id"]
        else:
            did = s.c.execute("INSERT INTO demands(text,norm,kind,first_seen,last_seen,hash,updated_at) VALUES(?,?,?,?,?,?,?)",
                              (text, nm, kind, seen_at, seen_at, hh, db.now())).lastrowid; s.n["demand_new"] += 1
        cur = s.c.execute("INSERT OR IGNORE INTO demand_sightings(demand_id,collection_id,seen_at,source_kind,source_ref,keyword,likes,posted_at,raw_text) VALUES(?,?,?,?,?,?,?,?,?)",
                          (did, s.coll, seen_at, source_kind, source_ref, keyword, likes, posted_at, text))
        if cur.rowcount:
            s.n["sighting"] += 1
            s.c.execute("""UPDATE demands SET seen_count=seen_count+1, first_seen=MIN(first_seen,?), last_seen=MAX(last_seen,?),
                           max_likes=MAX(max_likes,COALESCE(?,0)), updated_at=? WHERE id=?""", (seen_at, seen_at, likes, db.now(), did))
        if s.topic_id: db.link(s.c, "demand", did, "seen_in", "topic", s.topic_id)
        return did

    def video(s, v, keyword=None, seen_at=None):
        vid = str(v.get("id") or v.get("video_id") or "")
        if not vid: return
        seen_at = seen_at or s.coll_at
        pub = v.get("published") or v.get("date")
        bgm = v.get("bgm"); bgm = (bgm.get("title") if isinstance(bgm, dict) else bgm) or v.get("bgm_title")
        s.c.execute("""INSERT INTO ref_videos(platform,video_id,url,title,author,likes,comments,collects,shares,duration_s,published,keyword,bgm,first_seen,last_seen,collection_id)
            VALUES('douyin',?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(platform,video_id) DO UPDATE SET
            likes=COALESCE(excluded.likes,likes), comments=COALESCE(excluded.comments,comments), collects=COALESCE(excluded.collects,collects),
            shares=COALESCE(excluded.shares,shares), title=COALESCE(excluded.title,title), bgm=COALESCE(excluded.bgm,bgm),
            keyword=CASE WHEN keyword IS NULL THEN excluded.keyword WHEN excluded.keyword IS NULL OR instr(keyword,excluded.keyword)>0 THEN keyword ELSE keyword||' | '||excluded.keyword END,
            first_seen=MIN(first_seen,excluded.first_seen), last_seen=MAX(last_seen,excluded.last_seen)""",
            (vid, v.get("url") or f"https://www.douyin.com/video/{vid}", v.get("desc"), v.get("author"), v.get("likes"), v.get("comments"),
             v.get("collects"), v.get("shares"), v.get("duration_s") or v.get("dur_s"), pub, keyword, bgm, seen_at, seen_at, s.coll))
        s.n["video"] += 1
        if s.topic_id:
            rid = s.c.execute("SELECT id FROM ref_videos WHERE platform='douyin' AND video_id=?", (vid,)).fetchone()[0]
            db.link(s.c, "video", rid, "seen_in", "topic", s.topic_id)

    def comments(s, path, vid, seen_at=None):
        for cm in json.load(open(path, encoding="utf-8")):
            t = cm.get("text") or ""; q = db.is_question(t)
            s.c.execute("INSERT OR IGNORE INTO comments(cid,video_id,parent,text,likes,posted_at,ip,collection_id,is_question) VALUES(?,?,?,?,?,?,?,?,?)",
                        (cm.get("cid"), vid, cm.get("parent") or "", t, cm.get("like"), clean_ts(cm.get("time")), cm.get("ip"), s.coll, int(q)))
            s.n["comment"] += 1
            if q:
                s.n["question"] += 1
                s.demand(t, "question", "comment_reply" if cm.get("parent") else "comment", vid, None, cm.get("like"), clean_ts(cm.get("time")), seen_at)

    def words(s, words, source_kind, ref=None, keyword=None, seen_at=None):
        for w in words or []:
            if isinstance(w, dict): w = w.get("word") or w.get("content") or w.get("text")
            if not isinstance(w, str): continue
            w = w.split("\n")[0].strip()
            if w.startswith("#") or len(w) > 25 or "|" in w or w.endswith(("。","，")) or w.count("，")>1: continue      # 话题标签、标题/正文碎片不当搜索需求
            s.demand(w, "search", source_kind, ref, keyword, None, None, seen_at)

    def collect_json(s, p):
        d = json.load(open(p, encoding="utf-8")); vid = str(d.get("video_id")); at = clean_ts(d.get("collected_at")) or s.coll_at
        det = d.get("detail") or {}
        if det.get("status") in ("available", "partial"): s.video(det, None, at)
        rec = d.get("recommendations") or {}
        for key, blk in rec.items():
            if not isinstance(blk, dict) or blk.get("status") not in ("available", "partial"): continue
            if key == "detail_suggest_words":
                for scene, b in (blk.get("scenes") or {}).items():
                    if b.get("status") in ("available", "partial"): s.words(b.get("words"), scene, vid, None, at)
            elif key == "related_videos":
                for v in blk.get("videos") or blk.get("items") or []: s.video(v, None, at)
            else: s.words(blk.get("words"), key, vid, blk.get("keyword"), at)
        cf = pathlib.Path(p).parent / "comments.json"
        if cf.exists(): s.comments(cf, vid, at)
        return at

    def any_json(s, p):
        p = pathlib.Path(p)
        try: d = json.load(open(p, encoding="utf-8"))
        except Exception: return
        kw_from_name = p.stem
        if isinstance(d, dict) and "videos" in d:
            for v in d["videos"]: s.video(v, d.get("keyword") or kw_from_name)
        elif isinstance(d, dict) and ("search_sug" in d or "search_page_related" in d):
            for k in ("search_sug", "search_page_related"):
                b = d.get(k) or {}
                if b.get("status") in ("available", "partial"): s.words(b.get("words"), k, b.get("keyword"), b.get("keyword"))
        elif isinstance(d, dict) and "sug_list" in d:
            s.words([x.get("content") for x in d["sug_list"]], "search_sug", None, None)
        elif isinstance(d, list) and d and isinstance(d[0], dict) and "chips" in d[0]:
            for r in d:
                kw = r.get("keyword")
                s.words(r.get("chips"), "search_page_chips", kw, kw); s.words(r.get("suggest"), "search_sug", kw, kw)
        elif isinstance(d, list) and d and isinstance(d[0], dict) and "desc" in d[0] and "id" in d[0]:
            for v in d: s.video(v, kw_from_name)

    def run(s):
        root = s.root; files = [root] if root.is_file() else sorted(root.rglob("*.json"))
        done_comment_dirs = set(); ats = []
        for f in files:
            if any(x in f.parts for x in ("node_modules", "frames", "keyframes", "browser")): continue
            if f.name == "collect.json":
                ats.append(s.collect_json(f)); done_comment_dirs.add(f.parent)
        for f in files:
            if f.name == "comments.json" and f.parent not in done_comment_dirs:
                m = re.search(r"douyin_(\d+)", f.parent.name)
                s.comments(f, m.group(1) if m else f.parent.name)
            elif f.name not in ("collect.json", "comments.json") and not f.name.startswith(("transcript", "snapany", "faceblur")):
                s.any_json(f)
        n = sum(s.n.values())
        s.c.execute("UPDATE collections SET n_items=COALESCE(n_items,0)+?, collected_at=COALESCE(?,collected_at), ingested_at=? WHERE id=?",
                    (n, (min(a for a in ats if a) if any(ats) else None), db.now(), s.coll))
        return s.n

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+"); ap.add_argument("--topic"); ap.add_argument("--label")
    ap.add_argument("--at", help="采集时间（缺省用 collect.json 的 collected_at 或目录修改时间）")
    a = ap.parse_args(); c = db.connect()
    for p in a.paths:
        r = Ingest(c, p, a.topic, a.label, a.at).run(); print(p, json.dumps(r, ensure_ascii=False))
    db.reindex(c); c.commit()

if __name__ == "__main__": main()
