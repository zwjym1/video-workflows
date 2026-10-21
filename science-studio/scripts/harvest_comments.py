#!/usr/bin/env python3
"""发布后回采本作品评论区和看后搜（免登录，douyin-field-collect）：
  python3 scripts/harvest_comments.py <EP|work_id> [-n 300] [--from-dir 已有采集目录] [--top 10] [--no-browse]
流程：dy_collect.py video <video_url> --replies --browse → ingest_field.Ingest 入库（demands/comments）→ 本次见到的需求关联到作品（seen_in work）
      → 选出追更候选（评论疑问按点赞、看后搜/大家都在搜）关联 follow_up_of → works.comments_harvested=1 → 写 harvest_report.md。
追更候选只是线索：不改 demands.status，由选题阶段决定。"""
import sys, os, json, pathlib, argparse, subprocess
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
from ingest_field import Ingest
PY = "/workspace/.venv-dy/bin/python"; SK = "/workspace/skill_pkg/douyin-field-collect/scripts"
SEARCH_KINDS = ("comment_top_rec", "page_suggest_words", "feed_bottom_rec", "detail_suggest_words", "related_search", "search_page_related")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("work"); ap.add_argument("-n", type=int, default=300); ap.add_argument("--from-dir"); ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--no-browse", action="store_true"); ap.add_argument("--url", help="临时指定链接（不写库）")
    a = ap.parse_args(); c = db.connect(); w = db.find_work(c, a.work); url = a.url or w["video_url"]
    stamp = db.now_dt().strftime("%Y%m%d_%H%M")
    if a.from_dir: out = pathlib.Path(a.from_dir).resolve()
    else:
        if not url: sys.exit(f"作品 #{w['id']} 没有 video_url；先 mark_published.py {w['id']} --time ... --url <链接>")
        out = (pathlib.Path(os.environ.get("STUDIO_FIELD") or db.ROOT / "data" / "field") / "harvest" / f"work{w['id']}_{stamp}").resolve(); out.mkdir(parents=True, exist_ok=True)
        cmd = [PY, "dy_collect.py", "video", url, "-o", str(out), "-n", str(a.n), "--replies", "--reply-n", "20"] + ([] if a.no_browse else ["--browse"])
        print("运行：", " ".join(cmd), flush=True)
        p = subprocess.run(cmd, cwd=SK, capture_output=True, text=True, timeout=900)
        (out / "collect.log").write_text(p.stdout + "\n--- stderr ---\n" + p.stderr, encoding="utf-8")
        if p.returncode != 0 or not list(out.rglob("collect.json")):
            sys.exit(f"采集失败（退出码 {p.returncode}），日志 {out/'collect.log'}；没有改库。")
    cj = next(out.rglob("collect.json"), None); status = {}
    if cj:
        d = json.loads(cj.read_text(encoding="utf-8"))
        status = {k: (v.get("status") if isinstance(v, dict) else None) for k, v in d.items() if isinstance(v, dict) and "status" in v}
        status.update({f"rec.{k}": v.get("status") for k, v in (d.get("recommendations") or {}).items() if isinstance(v, dict)})
    ing = Ingest(c, out, None, f"作品#{w['id']} {w['episode']} 发布后评论回采"); n = ing.run(); coll = ing.coll
    dids = [r[0] for r in c.execute("SELECT DISTINCT demand_id FROM demand_sightings WHERE collection_id=?", (coll,))]
    for d in dids: db.link(c, "demand", d, "seen_in", "work", w["id"])
    q = c.execute(f"""SELECT d.id, d.text, max(COALESCE(s.likes,0)) lk, group_concat(DISTINCT s.source_kind) kinds FROM demands d JOIN demand_sightings s ON s.demand_id=d.id
                    WHERE s.collection_id=? AND d.kind='question' AND s.source_kind LIKE 'comment%' GROUP BY d.id ORDER BY lk DESC, length(d.text) DESC LIMIT ?""", (coll, a.top)).fetchall()
    sw = c.execute(f"""SELECT d.id, d.text, group_concat(DISTINCT s.source_kind) kinds FROM demands d JOIN demand_sightings s ON s.demand_id=d.id
                     WHERE s.collection_id=? AND d.kind='search' GROUP BY d.id ORDER BY d.seen_count DESC LIMIT ?""", (coll, a.top)).fetchall()
    for r in list(q) + list(sw): db.link(c, "demand", r["id"], "follow_up_of", "work", w["id"], f"回采 {stamp}")
    c.execute("UPDATE works SET comments_harvested=1, comments_harvested_at=?, updated_at=? WHERE id=?", (db.iso(db.now_dt()), db.now(), w["id"]))
    db.reindex(c); c.commit()
    L = [f"# 评论回采 · #{w['id']} {w['episode']}《{w['title']}》", f"- 时间：{db.now()}　目录：{out}", f"- 入库：{json.dumps(n, ensure_ascii=False)}；本次见到需求 {len(dids)} 条（已关联作品）",
         f"- 字段状态：{json.dumps(status, ensure_ascii=False)}", "", "## 追更候选 · 评论疑问（按点赞）", ""]
    L += [f"- demand#{r['id']}（赞 {r['lk']}）{r['text'][:60]}" for r in q] or ["- （无：评论里没有疑问句，或评论没采到——看上面字段状态）"]
    L += ["", "## 追更候选 · 看后搜 / 大家都在搜", ""] + ([f"- demand#{r['id']}［{r['kinds']}］{r['text']}" for r in sw] or ["- （无：游客态常拿不到，看字段状态）"])
    L += ["", "选题阶段用：`python3 scripts/search.py show demand <id>`；做了就 `search.py status <id> 已制作`。"]
    (out / "harvest_report.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))

if __name__ == "__main__": main()
