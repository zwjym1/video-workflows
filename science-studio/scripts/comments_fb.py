#!/usr/bin/env python3
"""评论与需求分析（Feedback Engine）：去重 → 分类 → 聚类 → 与需求库交叉 → 「过去未做、最近重现」。
  python3 scripts/comments_fb.py analyze [--work <EP>] [--collection <id>] [--since 2026-10-14] [--report 路径]
  python3 scripts/comments_fb.py add-shot <EP> --text "评论原文" [--likes 3] [--time ..] [--source 截图文件名]   # 截图里的评论（人工/OCR 转录）
  python3 scripts/comments_fb.py revived [--old-days 14] [--recent-days 7]
分类（规则词表，按优先级）：科学错误质疑 > 理解障碍 > 新选题需求 > 真实疑问 > 情绪反馈 > 其他。规则分类有误差，报告只给数量和代表评论，不当精确统计。
评论来源分两种，报告里分开：own=自己作品的评论（harvest_comments 或截图）；topic=同题他人视频的评论（ingest_field 采集，代表题目需求，不代表本账号观众）。
相关搜索（search_sug / page_suggest_words / comment_top_rec 等游客态联想）≠ 作品真实搜索来源（traffic_terms，创作者中心数据），两者分开列。"""
import sys, re, json, argparse, pathlib, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
CATS = [
 ("科学错误质疑", r"(这|也|根本|压根)(也)?没(飞|起飞)|不算.{0,4}(飞|高科技)|就是(一个|个)?.{0,4}(滑行|跳|变轨)|只是.{0,6}(跳|滑|喷)|不叫飞|错了|不对吧?|不是这样|胡说|瞎说|误导|扯淡|乱讲|不科学|违反.{0,4}(定律|物理)|物理.{0,3}(不及格|没学)|原理.{0,3}(错|不对)|根本不是|假的吧|并不是|纠正|说反了|外行"),
 ("理解障碍", r"没看懂|看不懂|听不懂|没听懂|不太懂|没明白|不明白|什么意思|啥意思|讲得太快|太快了|跟不上|绕晕|懵"),
 ("新选题需求", r"讲讲|讲一下|出一期|做一期|求科普|科普一下|能不能讲|下期|想看|拆一下|说说.{0,6}(吧|呗)|期待.{0,4}(下一|续)|再讲|分析一下|解释一下"),
]
EMO = r"哈哈|笑死|牛|厉害|绝了|离谱|卧槽|666|太强|震撼|帅|酷|支持|好看|赞|期待|爱了|服了|可怕|吓人|恐怖|无语|呵呵|智商税|割韭菜|作秀|画饼|吹牛"
STOP = set("的了是吗呢啊吧在有和就都也还这那个我你他她它们么什没不")

RHET = r"有没有想过|无所谓|难道|何干|舔"
THEMES = [("价格/量产/能否买", r"量产|售价|价格|多少钱|买得起|万美元|交付|订"), ("能否上路/实用性", r"上路|实用|家用|合法|法规|驾照|普通人|穷人"),
          ("原理：怎么飞/下压/喷气", r"原理|怎么飞|喷|推力|下压|吸|风扇|气压|火箭|冷气|变轨|滑行|起飞"), ("安全/风险", r"安全|危险|沙子|石子|事故|伤|撞"),
          ("真假/特效/营销", r"真的假|特效|AI|作秀|营销|画饼|吹牛|骗|割韭菜|股价|市值"), ("人物/马斯克", r"马斯克|老马|埃隆")]
def theme(t):
    return next((n for n, rx in THEMES if re.search(rx, t or "", re.I)), None)

def classify(t):
    t = t or ""
    if re.search(RHET, t) and not re.search(CATS[0][1], t): return "情绪反馈"
    for name, rx in CATS:
        if re.search(rx, t): return name
    if db.is_question(t): return "真实疑问"
    n = db.norm(t)
    if re.search(EMO, t) or len(n) <= 4: return "情绪反馈"
    return "其他"

def grams(t):
    n = "".join(ch for ch in db.norm(t) if ch not in STOP)
    return {n[i:i+2] for i in range(len(n) - 1)} or ({n} if n else set())
def jac(a, b): return len(a & b) / len(a | b) if a and b else 0.0

def cluster(items, th=0.25):
    """贪心单遍聚类（字二元组 Jaccard）。items: [(key,text,likes)] → [[...]]"""
    cl = []
    for it in sorted(items, key=lambda x: -(x[2] or 0)):
        g = grams(it[1]); best = None; bs = 0
        for c in cl:
            s = jac(g, c["g"])
            if s > bs: best, bs = c, s
        if best and bs >= th: best["items"].append(it); best["g"] |= g
        else: cl.append(dict(g=set(g), items=[it]))
    return [c["items"] for c in cl]

def own_video_ids(c, wid):
    """作品自己的视频 id（从 video_url/douyin_item_id 解析）。没有链接就是空集——采不到自己评论时要说明。"""
    w = c.execute("SELECT video_url, douyin_item_id FROM works WHERE id=?", (wid,)).fetchone()
    ids = set()
    for s in (w["video_url"], w["douyin_item_id"]):
        m = re.search(r"(\d{15,20})", s or "")
        if m: ids.add(m.group(1))
    return ids

def gather(c, work=None, collection=None, since=None):
    """→ list of dict(key,text,likes,posted_at,source,scope,video_id)"""
    out = []
    q = "SELECT c.* , col.label clabel FROM comments c LEFT JOIN collections col ON col.id=c.collection_id WHERE 1"
    args = []
    if collection: q += " AND c.collection_id=?"; args.append(collection)
    own = own_video_ids(c, work["id"]) if work else set()
    for r in c.execute(q, args):
        scope = "own" if r["video_id"] in own else "topic"
        if work and not collection and scope != "own":
            continue
        if since and (r["posted_at"] or "9999") < since: continue
        out.append(dict(key=r["cid"] or f"c{r['id']}", text=r["text"], likes=r["likes"], posted_at=r["posted_at"], source=f"采集 {r['clabel']}", scope=scope, video_id=r["video_id"]))
    for r in c.execute("SELECT * FROM comment_labels WHERE comment_key LIKE 'shot:%'" + (" AND work_id=?" if work else ""), ((work["id"],) if work else ())):
        out.append(dict(key=r["comment_key"], text=r["text"], likes=r["likes"], posted_at=r["posted_at"], source=r["source"], scope="own", video_id=None))
    # 去重：同一 norm 文本只留赞最多的一条
    seen = {}
    for x in out:
        n = db.norm(x["text"])
        if len(n) < 2: continue
        if n not in seen or (x["likes"] or 0) > (seen[n]["likes"] or 0): seen[n] = x
    return list(seen.values()), len(out)

def match_demand(c, text):
    n = db.norm(text)
    r = c.execute("SELECT id,status FROM demands WHERE norm=?", (n,)).fetchone()
    return r

def analyze(c, work=None, collection=None, since=None, write=True):
    items, raw_n = gather(c, work, collection, since)
    for x in items: x["cat"] = classify(x["text"])
    res = dict(raw=raw_n, dedup=len(items), by_cat={}, clusters=[], work=work and work["id"], themes={})
    for x in items:
        th = theme(x["text"])
        if th: d = res["themes"].setdefault(th, dict(n=0, likes=0, cats={}, top=[])); d["n"] += 1; d["likes"] += x["likes"] or 0; d["cats"][x["cat"]] = d["cats"].get(x["cat"], 0) + 1; d["top"].append((x["likes"] or 0, x["text"][:50]))
    for d in res["themes"].values(): d["top"] = [t for _, t in sorted(d["top"], reverse=True)[:3]]
    for cat in ("科学错误质疑", "理解障碍", "新选题需求", "真实疑问", "情绪反馈", "其他"):
        xs = [x for x in items if x["cat"] == cat]; res["by_cat"][cat] = len(xs)
        if cat in ("情绪反馈", "其他"): continue
        for grp in cluster([(x["key"], x["text"], x["likes"]) for x in xs]):
            top = grp[0]; d = match_demand(c, top[1])
            res["clusters"].append(dict(category=cat, label=top[1][:40], size=len(grp), likes=sum(g[2] or 0 for g in grp),
                                        sample=[g[1][:60] for g in grp[:3]], demand_id=d and d["id"], demand_status=d and d["status"]))
    res["clusters"].sort(key=lambda x: (-x["size"], -x["likes"]))
    if write:
        now = db.now()
        for x in items:
            d = match_demand(c, x["text"])
            c.execute("""INSERT INTO comment_labels(comment_key,work_id,text,norm,likes,posted_at,source,category,demand_id,method,labeled_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)
                         ON CONFLICT(comment_key) DO UPDATE SET category=excluded.category,demand_id=excluded.demand_id,method=excluded.method,labeled_at=excluded.labeled_at""",
                      (x["key"], work and work["id"], x["text"], db.norm(x["text"]), x["likes"], x["posted_at"], x["source"], x["cat"], d and d["id"], "rules_v1", now))
        scope = work["id"] if work else None
        c.execute("DELETE FROM comment_clusters WHERE work_id IS ? AND collection_id IS ?", (scope, collection))
        for k in res["clusters"]:
            c.execute("INSERT INTO comment_clusters(work_id,collection_id,category,label,size,sample,demand_id,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                      (scope, collection, k["category"], k["label"], k["size"], json.dumps(k["sample"], ensure_ascii=False), k["demand_id"], now))
        c.commit()
    return res

def revived(c, old_days=14, recent_days=7, n=20):
    """过去未做、最近重现：首次见到早于 old_days 天前，最近 recent_days 天又见到，状态不是 已制作/不适合，没关联到已发布作品。"""
    now = db.now_dt(); old = (now - dt.timedelta(days=old_days)).strftime("%Y-%m-%d %H:%M:%S"); rec = (now - dt.timedelta(days=recent_days)).strftime("%Y-%m-%d %H:%M:%S")
    rows = c.execute("""SELECT d.*, (SELECT count(*) FROM demand_sightings s WHERE s.demand_id=d.id AND s.seen_at>=?) recent_n,
                        (SELECT count(DISTINCT collection_id) FROM demand_sightings s WHERE s.demand_id=d.id) n_coll
                        FROM demands d WHERE d.status NOT IN ('已制作','不适合') AND d.first_seen < ? AND d.last_seen >= ?
                        AND NOT EXISTS (SELECT 1 FROM links l JOIN works w ON w.id=l.to_id WHERE l.from_type='demand' AND l.from_id=d.id AND l.to_type='work' AND l.rel='made_as' AND w.status='已发布')
                        ORDER BY recent_n DESC, d.max_likes DESC LIMIT ?""", (rec, old, rec, n)).fetchall()
    span = c.execute("SELECT min(seen_at), max(seen_at) FROM demand_sightings").fetchone()
    return rows, dict(old_before=old, recent_after=rec, data_span=tuple(span))

def search_split(c, work_id=None):
    """作品真实搜索来源（traffic_terms）vs 游客态相关搜索（demand_sightings）。"""
    real = c.execute("SELECT work_id, checkpoint, kind, term, share FROM traffic_terms WHERE kind IN ('搜索来源词','看后常搜')" + (" AND work_id=?" if work_id else "") + " ORDER BY work_id, kind, rank",
                     ((work_id,) if work_id else ())).fetchall()
    rel = c.execute("""SELECT d.text, s.source_kind, s.keyword, s.seen_at FROM demand_sightings s JOIN demands d ON d.id=s.demand_id
                       WHERE s.source_kind IN ('search_sug','page_suggest_words','comment_top_rec','feed_bottom_rec','detail_suggest_words','search_page_related','related_chips')
                       ORDER BY s.seen_at DESC LIMIT 400""").fetchall()
    return real, rel

def cross_terms(c, terms):
    """真实搜索来源词 ↔ 需求库：每个词在需求库里有没有、状态如何（trigram/LIKE 子串）。"""
    out = []
    for t in terms:
        g = grams(t); cand = []
        for d in c.execute("SELECT id,text,norm,status,seen_count,first_seen FROM demands"):
            dg = grams(d["text"])
            if not g or not dg: continue
            cov = len(g & dg) / len(g); rev = len(g & dg) / len(dg)
            if cov >= 0.6 or (rev >= 0.8 and len(dg) >= 3): cand.append((cov + rev, d))   # 词的大部分字面出现在需求里，或需求几乎完全包含在词里
        out.append((t, [d for _, d in sorted(cand, key=lambda x: -x[0])[:3]]))
    return out

def cmd_add_shot(a):
    c = db.connect(); w = db.find_work(c, a.work); k = "shot:" + db.h(w["id"], db.norm(a.text))
    c.execute("""INSERT OR REPLACE INTO comment_labels(comment_key,work_id,text,norm,likes,posted_at,source,category,method,labeled_at) VALUES(?,?,?,?,?,?,?,?,?,?)""",
              (k, w["id"], a.text, db.norm(a.text), a.likes, a.time, f"截图 {a.source or ''}".strip(), classify(a.text), "rules_v1", db.now())); c.commit(); print("ok", k)

def fmt(res, title):
    L = [f"## {title}", f"- 原始 {res['raw']} 条 → 去重 {res['dedup']} 条；分类（规则词表，有误差）：" + "，".join(f"{k} {v}" for k, v in res["by_cat"].items()), ""]
    if res.get("themes"):
        L.append("**主题（关键词归类，一条评论只归一个主题）**：")
        for k, d in sorted(res["themes"].items(), key=lambda x: -x[1]["n"]):
            L.append(f"- {k}：{d['n']} 条，赞合计 {d['likes']}；类型 {d['cats']}；高赞例：" + " / ".join(f"「{t}」" for t in d["top"]))
        L.append("")
        L.append("**聚类（同类型内字面相近的合并；只列疑问/质疑/理解障碍/新选题）**：")
    for k in res["clusters"][:15]:
        L.append(f"- [{k['category']}] ×{k['size']}（赞合计 {k['likes']}）「{k['label']}」" + (f" → 需求库 demand#{k['demand_id']}（{k['demand_status']}）" if k["demand_id"] else " → 需求库无同文") +
                 ("；例：" + " / ".join(k["sample"][1:3]) if k["size"] > 1 else ""))
    return L

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("analyze"); p.add_argument("--work"); p.add_argument("--collection", type=int); p.add_argument("--since"); p.add_argument("--no-write", action="store_true")
    p = sp.add_parser("add-shot"); p.add_argument("work"); p.add_argument("--text", required=True); p.add_argument("--likes", type=int); p.add_argument("--time"); p.add_argument("--source")
    p = sp.add_parser("revived"); p.add_argument("--old-days", type=float, default=14); p.add_argument("--recent-days", type=float, default=7)
    a = ap.parse_args(); c = db.connect()
    if a.cmd == "add-shot": cmd_add_shot(a)
    elif a.cmd == "analyze":
        w = db.find_work(c, a.work) if a.work else None
        r = analyze(c, w, a.collection, a.since, not a.no_write); print("\n".join(fmt(r, "评论分析")))
    else:
        rows, meta = revived(c, a.old_days, a.recent_days); print(meta)
        for r in rows: print(f"demand#{r['id']} [{r['kind']}|{r['status']}] {r['text'][:40]} 首见{r['first_seen'][:10]} 近期{r['recent_n']}次")
