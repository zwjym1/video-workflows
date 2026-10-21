#!/usr/bin/env python3
"""把抖音创作者中心导出（xlsx/csv）灌进 metrics_snapshots + retention_curve，并把检查点记为已完成。
  python3 scripts/ingest_metrics.py <导出.xlsx|csv> --work <id|EP|标题片段> --checkpoint 2h|24h|72h|7d
        [--platform 抖音] [--row <作品名片段>] [--captured-at '2026-10-22 20:10'] [--source '说明'] [--set search_share=0.8 ...] [--dry-run]
解析规则（列名嗅探，中文表头，容错）：
- 每个 sheet 先找表头行（含 ≥2 个已知指标名的行），也支持「指标｜数值」两列竖排。
- 多行作品时按 --row 或作品标题匹配；只有一行就用它。
- 百分数：「7.27%」→0.0727；比率列 >1 视为百分数；时长「16.9s」「00:16」→秒；「-」「--」空 → NULL。
- 留存曲线：任一 sheet 有「时间/秒/进度」列 + 「留存/观看占比/人数占比」列，即存 retention_curve（0–1）。
- 流量来源（来源｜占比）→ search_share/recommend_share；其它 sheet（看后搜、搜索词、章节点击…）原样进 raw_json。
--set 用来补截图里有但导出表没有的数（必须是真实数据，并在 --source 写明来源）。"""
import sys, re, json, csv, pathlib, argparse, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db

FIELDS = [  # (字段, 匹配正则, 类型)  顺序有意义：先具体后宽泛
 ("completion_5s", r"^(5s|5秒|五秒)完播", "rate"), ("bounce_2s", r"^(2s|2秒|两秒)跳出", "rate"),
 ("completion_rate", r"^完播率$|^整体完播", "rate"), ("avg_watch_ratio", r"平均播放占比|平均观看占比|播放进度", "rate"),
 ("avg_watch_s", r"平均(播放|观看)时长|人均(播放|观看)时长", "sec"), ("cover_ctr", r"封面点击率", "rate"),
 ("plays", r"^播放(量|次数)?$|^观看(量|次数)$|^总播放", "int"), ("likes", r"^点赞", "int"), ("comments", r"^评论", "int"),
 ("shares", r"^(分享|转发)", "int"), ("favorites", r"^收藏", "int"), ("follows_gained", r"粉丝增量|涨粉|新增粉丝|净增粉丝", "int"),
 ("profile_visits", r"主页访问", "int"), ("search_share", r"^搜索(流量)?(占比)?$", "rate"), ("recommend_share", r"^推荐(流量)?(占比)?$|^推荐页", "rate"),
]
META = {"作品名称": "title", "标题": "title", "作品": "title", "发布时间": "publish_time"}
T_COL = re.compile(r"^(时间|时刻|秒|秒数|播放时间|视频时间|进度|时间点|t|time)(\(s\)|（秒）|\(秒\)|/s)?$", re.I)
R_COL = re.compile(r"留存|观看(人数)?占比|人数占比|在看比例|retention", re.I)
SRC_NAME = re.compile(r"来源|渠道"); SRC_VAL = re.compile(r"占比|比例|百分比")

def num(v, kind):
    if v is None: return None
    s = str(v).strip().replace(",", "").replace("，", "")
    if s in ("", "-", "--", "—", "/", "N/A", "nan", "None"): return None
    pct = s.endswith("%"); s2 = s.rstrip("%")
    m = re.match(r"^(\d+):(\d{2})(?::(\d{2}))?$", s2)
    if m and kind == "sec":
        a = [int(x) for x in m.groups() if x is not None]; return float(a[0]*3600+a[1]*60+a[2] if len(a) == 3 else a[0]*60+a[1])
    mult = 1
    if s2.endswith("万"): mult, s2 = 1e4, s2[:-1]
    elif s2.endswith("亿"): mult, s2 = 1e8, s2[:-1]
    s2 = re.sub(r"(s|秒|次|人)$", "", s2)
    try: x = float(s2) * mult
    except ValueError: return None
    if kind == "rate": return x / 100 if (pct or x > 1) else x
    if kind == "int": return int(round(x))
    return x

def tsec(v):
    if v is None: return None
    s = str(v).strip().lower()
    m = re.match(r"^(\d+):(\d{2})(?:\.(\d+))?$", s)
    if m: return int(m.group(1))*60 + int(m.group(2)) + (float("0."+m.group(3)) if m.group(3) else 0)
    s = re.sub(r"(s|秒|sec)$", "", s)
    try: return float(s)
    except ValueError: return None

def read_sheets(path):
    p = pathlib.Path(path)
    if p.suffix.lower() in (".csv", ".tsv", ".txt"):
        raw = p.read_bytes()
        for enc in ("utf-8-sig", "gb18030", "utf-16"):
            try: txt = raw.decode(enc); break
            except UnicodeDecodeError: continue
        dl = "\t" if p.suffix.lower() == ".tsv" or txt.count("\t") > txt.count(",") else ","
        return {p.stem: [list(r) for r in csv.reader(txt.splitlines(), delimiter=dl)]}
    import openpyxl, warnings
    warnings.filterwarnings("ignore")
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    out = {}
    for ws in wb.worksheets:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        rows = [r for r in rows if any(x not in (None, "") for x in r)]
        if rows: out[ws.title] = rows
    return out

def hdr_name(h): return re.sub(r"\s+", "", str(h or ""))
def field_of(h):
    h = hdr_name(h)
    for f, rx, k in FIELDS:
        if re.search(rx, h): return f, k
    return None, None

def parse(path, row_hint=None, title_hint=None):
    """→ dict(metrics={...}, retention=[(t,r)], meta={...}, extras={sheet: rows}, notes=[...])"""
    sheets = read_sheets(path); res = dict(metrics={}, retention=[], meta={}, extras={}, notes=[])
    for name, rows in sheets.items():
        used = False
        # 1) 留存曲线
        for hi, hr in enumerate(rows[:5]):
            tc = [i for i, h in enumerate(hr) if T_COL.match(hdr_name(h))]; rc = [i for i, h in enumerate(hr) if R_COL.search(hdr_name(h))]
            if tc and rc:
                pts = []
                for r in rows[hi+1:]:
                    t = tsec(r[tc[0]] if tc[0] < len(r) else None); v = num(r[rc[0]] if rc[0] < len(r) else None, "rate")
                    if t is not None and v is not None: pts.append((t, v))
                if len(pts) >= 3:
                    res["retention"] = sorted(pts); res["notes"].append(f"sheet「{name}」→ 留存曲线 {len(pts)} 点"); used = True
                break
        if used: continue
        # 2) 流量来源（来源｜占比）
        if rows and len(rows[0]) >= 2 and SRC_NAME.search(hdr_name(rows[0][0])) and SRC_VAL.search(hdr_name(rows[0][1])):
            d = {str(r[0]).strip(): num(r[1], "rate") for r in rows[1:] if r and r[0]}
            res["extras"][name] = d
            for k, v in d.items():
                if re.search(r"搜索", k): res["metrics"]["search_share"] = v
                elif re.search(r"推荐", k): res["metrics"]["recommend_share"] = v
            res["notes"].append(f"sheet「{name}」→ 流量来源"); continue
        # 3) 横排表头
        best = None
        for hi, hr in enumerate(rows[:10]):
            hits = sum(1 for h in hr if field_of(h)[0])
            if hits >= 2 and (best is None or hits > best[1]): best = (hi, hits)
        if best:
            hi = best[0]; hr = [hdr_name(h) for h in rows[hi]]; data = [r for r in rows[hi+1:] if any(x not in (None, "") for x in r)]
            if not data: continue
            pick = data[0]
            if len(data) > 1:
                ti = next((i for i, h in enumerate(hr) if META.get(h) == "title"), None); key = row_hint or title_hint
                cand = [r for r in data if ti is not None and key and db.norm(key)[:12] in db.norm(str(r[ti]))] if key else []
                if len(cand) == 1: pick = cand[0]
                else: raise SystemExit(f"sheet「{name}」有 {len(data)} 行作品，用 --row <作品名片段> 指定（当前匹配 {len(cand)} 行）")
            rec = {hr[i]: (pick[i] if i < len(pick) else None) for i in range(len(hr)) if hr[i]}
            res["extras"][name] = {k: (str(v) if v is not None else None) for k, v in rec.items()}
            for h, v in rec.items():
                f, k = field_of(h)
                if f and f not in res["metrics"]: res["metrics"][f] = num(v, k)
                if META.get(h): res["meta"][META[h]] = str(v) if v is not None else None
            res["notes"].append(f"sheet「{name}」→ 指标行（表头第 {hi+1} 行）"); continue
        # 4) 竖排「指标｜数值」
        kv = {hdr_name(r[0]): r[1] for r in rows if len(r) >= 2 and r[0] not in (None, "")}
        hits = {h: field_of(h) for h in kv if field_of(h)[0]}
        if len(hits) >= 2:
            for h, (f, k) in hits.items(): res["metrics"].setdefault(f, num(kv[h], k))
            for h, v in kv.items():
                if META.get(h): res["meta"][META[h]] = str(v)
            res["extras"][name] = {k: (str(v) if v is not None else None) for k, v in kv.items()}
            res["notes"].append(f"sheet「{name}」→ 竖排指标"); continue
        res["extras"][name] = rows[:200]; res["notes"].append(f"sheet「{name}」未识别，原样存 raw_json")
    return res

COLS = ["plays","completion_5s","avg_watch_s","avg_watch_ratio","bounce_2s","completion_rate","likes","comments","shares","favorites",
        "follows_gained","profile_visits","cover_ctr","search_share","recommend_share"]
CK = re.compile(r"^\d+(h|d)$")

def store(c, wid, checkpoint, platform, metrics, retention, source, captured_at, raw):
    """upsert 一个快照；None 不覆盖已有值（便于先导 xlsx、再补截图数）。"""
    old = c.execute("SELECT * FROM metrics_snapshots WHERE work_id=? AND platform=? AND checkpoint=?", (wid, platform, checkpoint)).fetchone()
    vals = {k: metrics.get(k) for k in COLS}
    if old:
        for k in COLS:
            if vals[k] is None: vals[k] = old[k]
        oraw = json.loads(old["raw_json"] or "{}"); oraw.update(raw or {}); raw = oraw
        src = old["source"] if source in (old["source"] or "") else f"{old['source']}；{source}"
        c.execute("UPDATE metrics_snapshots SET " + ",".join(f"{k}=?" for k in COLS) + ",captured_at=COALESCE(?,captured_at),source=?,raw_json=?,ingested_at=? WHERE id=?",
                  (*vals.values(), captured_at, src, json.dumps(raw, ensure_ascii=False), db.now(), old["id"])); sid = old["id"]
    else:
        sid = c.execute("INSERT INTO metrics_snapshots(work_id,platform,checkpoint,captured_at," + ",".join(COLS) + ",source,raw_json,ingested_at) VALUES(" + ",".join("?"*(len(COLS)+7)) + ")",
                        (wid, platform, checkpoint, captured_at, *vals.values(), source, json.dumps(raw, ensure_ascii=False), db.now())).lastrowid
    if retention:
        c.execute("DELETE FROM retention_curve WHERE work_id=? AND platform=? AND checkpoint=?", (wid, platform, checkpoint))
        c.executemany("INSERT INTO retention_curve VALUES(?,?,?,?,?)", [(wid, platform, checkpoint, t, r) for t, r in retention])
    if platform != "抖音": return sid   # 检查点提醒只按抖音走；B站等只存快照
    w = c.execute("SELECT checkpoints_done FROM works WHERE id=?", (wid,)).fetchone()
    done = db.jlist(w["checkpoints_done"])
    if checkpoint not in done: done.append(checkpoint)
    order = lambda x: int(x[:-1]) * (24 if x.endswith("d") else 1)
    c.execute("UPDATE works SET checkpoints_done=?, updated_at=? WHERE id=?", (json.dumps(sorted(set(done), key=order)), db.now(), wid))
    return sid

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file"); ap.add_argument("--work", required=True); ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--platform", default="抖音"); ap.add_argument("--row"); ap.add_argument("--captured-at")
    ap.add_argument("--source"); ap.add_argument("--set", nargs="*", default=[]); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not CK.match(a.checkpoint): sys.exit("--checkpoint 写成 2h/24h/72h/7d 这种")
    c = db.connect(); w = db.find_work(c, a.work)
    r = parse(a.file, a.row, w["title"])
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in COLS: sys.exit(f"--set 不认识的字段 {k}；可用：{','.join(COLS)}")
        r["metrics"][k] = num(v, "int" if k in ("plays","likes","comments","shares","favorites","follows_gained","profile_visits") else "sec" if k == "avg_watch_s" else "rate")
    if not any(v is not None for v in r["metrics"].values()) and not r["retention"]: sys.exit("没解析出任何指标：" + "；".join(r["notes"]))
    cap = db.iso(a.captured_at) if a.captured_at else datetime.datetime.fromtimestamp(pathlib.Path(a.file).stat().st_mtime, db.TZ).isoformat(timespec="seconds")
    src = a.source or f"创作者中心导出 {pathlib.Path(a.file).resolve()}"
    raw = dict(file=str(pathlib.Path(a.file).resolve()), meta=r["meta"], sheets=r["extras"], notes=r["notes"])
    # 作品名核对（防止导错作品）
    if r["meta"].get("title") and w["title"] and db.norm(w["title"])[:6] not in db.norm(r["meta"]["title"]):
        print(f"⚠ 导出表作品名「{r['meta']['title'][:30]}」与作品 #{w['id']}「{w['title'][:30]}」不像同一条，请核对", file=sys.stderr)
    print(json.dumps(dict(work=w["id"], episode=w["episode"], checkpoint=a.checkpoint, platform=a.platform, metrics=r["metrics"],
                          retention_points=len(r["retention"]), notes=r["notes"]), ensure_ascii=False, indent=1))
    if a.dry_run: print("(dry-run，未写库)"); return
    if r["meta"].get("publish_time") and not w["publish_time"]:
        c.execute("UPDATE works SET publish_time=? WHERE id=?", (db.iso(r["meta"]["publish_time"]), w["id"]))
    sid = store(c, w["id"], a.checkpoint, a.platform, r["metrics"], r["retention"], src, cap, raw); c.commit()
    print(f"已写入 metrics_snapshots#{sid}；检查点 {a.checkpoint} 记为完成。下一步：python3 scripts/diagnose.py {w['id']}")

if __name__ == "__main__": main()
