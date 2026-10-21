#!/usr/bin/env python3
"""跨作品规律：python3 scripts/insights.py [recompute]   重算并写 insights（缺省先重算再打印）
                 python3 scripts/insights.py show          只打印当前简报（选题、写稿阶段先读）
口径：只用「已发布」作品、抖音、每条作品取一个主快照（优先 24h，其次 72h/48h/8h/2h/7d；都没有时取最接近 24h 的已核快照，如 40h/47h）。
状态：任一组 n<3 或总 n<6 → 验证中（写明样本不够）；样本够且差距超过阈值 → 已验证；
      以前「已验证」、现在结论方向反了 → 已推翻。每次状态或结论变化都记 insights_history。"""
import sys, json, pathlib, statistics as st
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
PREF = ["24h", "72h", "48h", "8h", "2h", "7d"]; MIN_G, MIN_N = 3, 6

def primary(c):
    out = {}
    for w in c.execute("""SELECT w.id, w.episode, w.title, d.hook_class, d.topic_class, d.title_search_first, d.duration_s
                          FROM works w LEFT JOIN content_dna d ON d.work_id=w.id WHERE w.status='已发布'"""):
        snaps = {r["checkpoint"]: r for r in c.execute("SELECT * FROM metrics_snapshots WHERE work_id=? AND platform='抖音'", (w["id"],))}
        ck = next((k for k in PREF if k in snaps), None)
        if not ck and snaps:   # v3：截图按实际小时数记（如 40h/47h/94h）→ 取最接近 24h 的已核快照
            hrs = lambda k: int(k[:-1]) * (24 if k.endswith("d") else 1)
            ver = [k for k, r in snaps.items() if r["verified"]] or list(snaps)
            ck = min(ver, key=lambda k: abs(hrs(k) - 24))
        if ck: out[w["id"]] = dict(w=dict(w), s=snaps[ck], ck=ck)
    return out

def groups(P, gkey, mkey):
    g = {}
    for wid, x in P.items():
        k = gkey(x); v = x["s"][mkey]
        if k is None or v is None: continue
        g.setdefault(k, []).append((wid, v))
    return g

def judge(g, thresh, lower_better, fmt, label, metric):
    n = sum(len(v) for v in g.values()); ev = sorted(w for v in g.values() for w, _ in v)
    if not g: return dict(statement=f"暂无可比数据（{label} 或 {metric} 缺，n=0）。", n=0, ev=ev, direction=None, enough=False, basis={})
    means = {k: st.mean(x for _, x in v) for k, v in g.items()}
    parts = "；".join(f"{k}：{fmt(means[k])}（n={len(g[k])}）" for k in sorted(means, key=means.get, reverse=not lower_better))
    best = (min if lower_better else max)(means, key=means.get)
    enough = len(g) >= 2 and all(len(v) >= MIN_G for v in g.values()) and n >= MIN_N
    if len(g) < 2: s = f"{metric}按{label}只有一组数据：{parts}。还不能比较。"
    elif not enough: s = f"{metric}按{label}：{parts}。样本不足（每组需≥{MIN_G}、总≥{MIN_N}），只作线索。"
    else:
        gap = abs(means[best] - (max if lower_better else min)(means.values()))
        s = f"{metric}按{label}：{parts}。" + (f"「{best}」明显更好（差 {fmt(gap)}）。" if gap >= thresh else "各组差距不大，暂无规律。")
        if gap < thresh: best = None
    return dict(statement=s, n=n, ev=ev, direction=best if enough else None, enough=enough, basis=dict(means=means, metric=metric))

def bucket_dur(d):
    if d is None: return None
    return "≤60s" if d <= 60 else "60–120s" if d <= 120 else ">120s"

def compute(c):
    P = primary(c); R = []
    R.append(("hook_vs_bounce2s", "开头", judge(groups(P, lambda x: x["w"]["hook_class"], "bounce_2s"), 0.05, True, lambda v: f"{v:.1%}", "开头类型", "2s跳出")))
    R.append(("title_search_first_vs_search_share", "标题", judge(groups(P, lambda x: None if x["w"]["title_search_first"] is None else ("搜索词前置" if x["w"]["title_search_first"] else "非前置"), "search_share"),
                                                                  0.10, False, lambda v: f"{v:.0%}", "标题是否搜索词前置", "搜索流量占比")))
    R.append(("duration_vs_completion", "时长", judge(groups(P, lambda x: bucket_dur(x["w"]["duration_s"]), "completion_rate"), 0.03, False, lambda v: f"{v:.1%}", "时长档", "完播率")))
    R.append(("topic_vs_plays", "选题", judge(groups(P, lambda x: x["w"]["topic_class"], "plays"), 0, False, lambda v: f"{v:,.0f}", "选题类别", "播放")))
    # 段落：最大掉点（≥3s 起）落在全片的前/中/后 1/3
    seg = {}
    for wid, x in P.items():
        cur = c.execute("SELECT t_sec,retention FROM retention_curve WHERE work_id=? AND platform='抖音' AND checkpoint=? ORDER BY t_sec", (wid, x["ck"])).fetchall()
        D = x["w"]["duration_s"] or (cur[-1][0] if cur else None)
        if len(cur) < 3 or not D: continue
        dd = [(cur[i][0], cur[i-1][1] - cur[i][1]) for i in range(1, len(cur)) if cur[i][0] >= 3]
        if not dd: continue
        t = max(dd, key=lambda z: z[1])[0]; pos = "前1/3" if t < D/3 else "中1/3" if t < 2*D/3 else "后1/3"
        seg.setdefault(pos, []).append((wid, 1))
    n = sum(len(v) for v in seg.values())
    s = ("暂无留存曲线（n=0），等导出含「观众留存」的数据。" if not n else
         "3 秒后最大掉点位置：" + "；".join(f"{k} {len(v)} 条" for k, v in seg.items()) + (f"。样本不足（n={n}）。" if n < MIN_N else "。"))
    R.append(("biggest_drop_position", "段落", dict(statement=s, n=n, ev=sorted(w for v in seg.values() for w, _ in v),
             direction=(max(seg, key=lambda k: len(seg[k])) if n >= MIN_N else None), enough=n >= MIN_N, basis={k: len(v) for k, v in seg.items()})))
    return R, P

def write(c, R):
    changed = []
    for key, kind, r in R:
        old = c.execute("SELECT * FROM insights WHERE key=?", (key,)).fetchone()
        status = "已验证" if r["enough"] and r["direction"] else "验证中"
        if old and old["status"] == "已验证":
            od = json.loads(old["metric_basis"] or "{}").get("direction")
            if r["enough"] and od and r["direction"] != od: status = "已推翻"
        basis = json.dumps(dict(r["basis"], direction=r["direction"], n=r["n"]), ensure_ascii=False, default=str)
        if old:
            c.execute("UPDATE insights SET statement=?,evidence_work_ids=?,metric_basis=?,n=?,status=?,updated_at=? WHERE id=?",
                      (r["statement"], json.dumps(r["ev"]), basis, r["n"], status, db.now(), old["id"])); iid = old["id"]
        else:
            iid = c.execute("INSERT INTO insights(key,kind,statement,evidence_work_ids,metric_basis,n,status,updated_at) VALUES(?,?,?,?,?,?,?,?)",
                            (key, kind, r["statement"], json.dumps(r["ev"]), basis, r["n"], status, db.now())).lastrowid
        if not old or old["status"] != status or old["statement"] != r["statement"]:
            c.execute("INSERT INTO insights_history(insight_id,at,status,statement,n) VALUES(?,?,?,?,?)", (iid, db.now(), status, r["statement"], r["n"]))
            changed.append((kind, (old["status"] if old else "新建"), status))
    c.commit(); return changed

def show(c):
    rows = c.execute("SELECT * FROM insights ORDER BY CASE status WHEN '已验证' THEN 0 WHEN '验证中' THEN 1 ELSE 2 END, kind").fetchall()
    npub = c.execute("SELECT count(*) FROM works WHERE status='已发布'").fetchone()[0]
    nsnap = c.execute("SELECT count(DISTINCT work_id) FROM metrics_snapshots WHERE platform='抖音'").fetchone()[0]
    print(f"# 数据规律简报（{db.now()}；已发布 {npub} 条，有抖音数据 {nsnap} 条）\n")
    if not rows: print("还没有 insights，先跑 python3 scripts/insights.py recompute"); return
    for r in rows: print(f"- [{r['status']}｜{r['kind']}｜n={r['n']}] {r['statement']}")
    print("\n读法：只有「已验证」可当依据；「验证中」只当线索，写稿/选题时可以试，但要说明是试验。")

if __name__ == "__main__":
    c = db.connect(); cmd = sys.argv[1] if len(sys.argv) > 1 else "recompute"
    if cmd == "recompute":
        R, P = compute(c); ch = write(c, R)
        print(f"重算完成：主快照 {len(P)} 条作品；变化 {ch or '无'}\n"); show(c)
    elif cmd == "show": show(c)
    else: sys.exit(__doc__)
