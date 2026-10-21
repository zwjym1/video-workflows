#!/usr/bin/env python3
"""单条作品数据诊断：python3 scripts/diagnose.py <EP|work_id> [--checkpoint 24h] [--platform 抖音] [--top 5] [--no-write]
- 取该检查点快照（缺省取最新），和账号其它作品同检查点均值对比；
- 有留存曲线时：按 1 秒重采样，找掉人最多的 N 个时刻，对到当时那句口播/字幕卡和镜头（时间轴见 timeline.py）；
- 写进 reviews/<EP>*复盘*.md 的「数据」段（<!-- DATA:START/END --> 之间，可重复覆盖），加一条 lessons（真实数据），回填 content_dna.metrics_note。
环境变量 STUDIO_REVIEWS 可改复盘目录（测试用）。"""
import sys, os, json, pathlib, argparse, statistics as st
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db, timeline as tl
M = [("plays","播放",lambda v:f"{v:,.0f}"),("bounce_2s","2s跳出",lambda v:f"{v:.1%}"),("completion_5s","5s完播",lambda v:f"{v:.1%}"),
     ("completion_rate","完播率",lambda v:f"{v:.2%}"),("avg_watch_s","均播(s)",lambda v:f"{v:.1f}"),("avg_watch_ratio","均播占比",lambda v:f"{v:.1%}"),
     ("likes","点赞",lambda v:f"{v:.0f}"),("comments","评论",lambda v:f"{v:.0f}"),("shares","分享",lambda v:f"{v:.0f}"),("favorites","收藏",lambda v:f"{v:.0f}"),
     ("follows_gained","涨粉",lambda v:f"{v:.0f}"),("search_share","搜索占比",lambda v:f"{v:.1%}"),("recommend_share","推荐占比",lambda v:f"{v:.1%}")]
ORDER = lambda x: int(x[:-1]) * (24 if x.endswith("d") else 1)

def resample(pts):
    pts = sorted(pts); T = int(pts[-1][0]); out = []
    for s in range(0, T + 1):
        for (t0, r0), (t1, r1) in zip(pts, pts[1:]):
            if t0 <= s <= t1: out.append(r0 + (r1 - r0) * ((s - t0) / (t1 - t0) if t1 > t0 else 0)); break
        else: out.append(pts[0][1] if s < pts[0][0] else pts[-1][1])
    return out

def drops(curve, top):
    d = [(s, curve[s-1] - curve[s]) for s in range(1, len(curve))]
    d.sort(key=lambda x: -x[1]); pick = []
    for s, v in d:
        if v <= 0: break
        if all(abs(s - p) > 2 for p, _ in pick): pick.append((s, v))
        if len(pick) >= top: break
    return sorted(pick)

def account_avg(c, wid, ck, platform):
    rows = c.execute("""SELECT m.* FROM metrics_snapshots m JOIN works w ON w.id=m.work_id
                        WHERE m.work_id<>? AND m.checkpoint=? AND m.platform=? AND w.status='已发布'""", (wid, ck, platform)).fetchall()
    out = {}
    for k, *_ in M:
        v = [r[k] for r in rows if r[k] is not None]
        if v: out[k] = (st.mean(v), len(v))
    return out, len(rows)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("work"); ap.add_argument("--checkpoint"); ap.add_argument("--platform", default="抖音"); ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--timeline"); ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(); c = db.connect(); w = db.find_work(c, a.work)
    snaps = c.execute("SELECT * FROM metrics_snapshots WHERE work_id=? AND platform=?", (w["id"], a.platform)).fetchall()
    if not snaps: sys.exit(f"作品 #{w['id']} 在{a.platform}还没有数据快照；先跑 ingest_metrics.py")
    snaps = sorted(snaps, key=lambda r: ORDER(r["checkpoint"]))
    snap = next((r for r in snaps if r["checkpoint"] == a.checkpoint), None) if a.checkpoint else snaps[-1]
    if not snap: sys.exit(f"没有 {a.checkpoint} 快照；已有：{[r['checkpoint'] for r in snaps]}")
    ck = snap["checkpoint"]; avg, n_other = account_avg(c, w["id"], ck, a.platform)
    dna = c.execute("SELECT * FROM content_dna WHERE work_id=?", (w["id"],)).fetchone()
    L = [f"### {a.platform} · {ck} 检查点（采集 {snap['captured_at'] or '?'}；来源：{snap['source']}）", "",
         "| 指标 | 本条 | 账号其它作品同检查点均值 | 对比 |", "|---|---|---|---|"]
    for k, name, f in M:
        v = snap[k]
        if v is None and k not in avg: continue
        av = avg.get(k); cmp_ = ""
        if v is not None and av and av[0]:
            r = v / av[0] - 1; better = (r < 0) if k == "bounce_2s" else (r > 0)
            cmp_ = "持平" if abs(r) < 0.02 else f"{'好' if better else '差'} {abs(r):.0%}"
        L.append(f"| {name} | {f(v) if v is not None else '—'} | {f(av[0]) + f'（n={av[1]}）' if av else '无同检查点数据'} | {cmp_} |")
    if n_other < 3: L += ["", f"> 对比样本只有 {n_other} 条作品，均值仅供参考，不下结论。"]
    curve_rows = c.execute("SELECT t_sec, retention FROM retention_curve WHERE work_id=? AND platform=? AND checkpoint=? ORDER BY t_sec",
                           (w["id"], a.platform, ck)).fetchall()
    lesson_bits = [f"{name}{f(snap[k])}" for k, name, f in M[:6] if snap[k] is not None]
    if curve_rows:
        curve = resample([(r[0], r[1]) for r in curve_rows]); T = tl.load(w["project_dir"], a.timeline or w["timeline_path"], db.ROOT / "projects" / w["episode"])
        L += ["", f"**留存曲线**：{len(curve_rows)} 点，2s {curve[min(2,len(curve)-1)]:.0%}｜5s {curve[min(5,len(curve)-1)]:.0%}｜"
              + (f"30s {curve[30]:.0%}｜" if len(curve) > 30 else "") + f"末尾 {curve[-1]:.0%}"]
        half = next((s for s, v in enumerate(curve) if v < 0.5), None)
        if half is not None: L.append(f"留存跌破 50% 在第 {half} 秒。")
        L += ["", f"**掉人最多的 {a.top} 个时刻**（每秒跌幅；时间轴：{'、'.join(T['files']) or '未找到，只给秒数'}）", "",
              "| 秒 | 跌幅 | 当时口播/字幕 | 段 | 镜头 |", "|---|---|---|---|---|"]
        top = drops(curve, a.top)
        for s, v in top:
            se = tl.at(T["sentences"], s - 0.5) if T["sentences"] else None; sh = tl.at(T["shots"], s - 0.5) if T["shots"] else None
            L.append(f"| {s} | −{v:.1%} | {(se['id'] + ' ' + se['text'][:28]) if se else '—'} | {(se or {}).get('seg') or '—'} | {(sh['text'] if sh else '—')} |")
        if top:
            s0, v0 = max(top, key=lambda x: x[1]); se0 = tl.at(T["sentences"], s0 - 0.5) if T["sentences"] else None
            lesson_bits.append(f"最大掉点第{s0}秒−{v0:.1%}" + (f"（{se0['text'][:20]}）" if se0 else ""))
        if T["files"] and w["episode"].startswith("LEGACY"): L.append("\n> 旧项目时间轴可能不是发布版（例如 Roadster 只有 V3 工程），对句子前先核对版本。")
    else:
        L += ["", "**留存曲线**：本次导出没有逐秒留存，无法定位掉人的句子。下次在创作者中心「作品分析 → 观众留存」导出或截图。"]
    L += ["", "**判读顺序**（运营系统）：先看 2s 跳出（开头）→ 5s 完播（前 5 秒承诺）→ 均播/完播（中段）→ 互动与搜索占比。结论写在下面「要改进的」，此段只放数据。"]
    body = "\n".join(L)
    print(body)
    if a.no_write: return
    rdir = pathlib.Path(os.environ.get("STUDIO_REVIEWS") or db.ROOT / "reviews"); rdir.mkdir(parents=True, exist_ok=True)
    files = sorted(rdir.glob(f"{w['episode']}*复盘*.md")); rf = files[0] if files else rdir / f"{w['episode']}_复盘.md"
    txt = rf.read_text(encoding="utf-8") if rf.exists() else f"# {w['episode']} · {w['title']} · 复盘\n\n"
    tag_a, tag_b = f"<!-- DATA:{a.platform}:{ck}:START -->", f"<!-- DATA:{a.platform}:{ck}:END -->"
    block = f"{tag_a}\n{body}\n{tag_b}"
    if tag_a in txt: txt = txt[:txt.index(tag_a)] + block + txt[txt.index(tag_b) + len(tag_b):]
    else:
        import re
        m = re.search(r"^## 发布后数据.*?$", txt, re.M) or re.search(r"^## 数据\s*$", txt, re.M)
        if m and "<!-- DATA:" not in txt:   # 第一次：把 TBD 段换成「数据」段
            nxt = re.search(r"^## ", txt[m.end():], re.M); end = m.end() + nxt.start() if nxt else len(txt)
            txt = txt[:m.start()] + "## 数据\n\n" + block + "\n\n" + txt[end:]
        elif "## 数据" in txt:
            i = txt.index("## 数据") + len("## 数据"); txt = txt[:i] + "\n\n" + block + txt[i:]
        else: txt = txt.rstrip() + "\n\n## 数据\n\n" + block + "\n"
    rf.write_text(txt, encoding="utf-8")
    src = f"diagnose:{w['id']}:{a.platform}:{ck}"
    c.execute("UPDATE lessons SET superseded=1 WHERE source=? ", (src,))
    text = f"{w['episode']}（{a.platform} {ck}）：" + "，".join(lesson_bits) + "。来源：" + (snap["source"] or "")[:80]
    c.execute("INSERT INTO lessons(text,type,work_id,source,created_at,hash) VALUES(?,?,?,?,?,?) ON CONFLICT(hash) DO UPDATE SET superseded=0",
              (text, "真实数据", w["id"], src, db.now(), db.h("lesson", db.norm(text))))
    note = f"见 metrics_snapshots（{a.platform} {ck}）：" + "，".join(lesson_bits)
    c.execute("INSERT INTO content_dna(work_id,metrics_note,updated_at) VALUES(?,?,?) ON CONFLICT(work_id) DO UPDATE SET metrics_note=excluded.metrics_note,updated_at=excluded.updated_at",
              (w["id"], note, db.now()))
    db.reindex(c); c.commit(); print(f"\n已写入 {rf}；lessons +1（真实数据）；content_dna.metrics_note 已更新")

if __name__ == "__main__": main()
