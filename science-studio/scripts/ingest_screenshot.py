#!/usr/bin/env python3
"""创作者中心截图 → 结构化数据（qoder Flash OCR）→ 人工可核 review → 确认后入库（verified）。
  1) 抽取（不写指标，只建「待核」记录）：
     python3 scripts/ingest_screenshot.py extract <图片...> [--work <EP>] [--checkpoint auto|24h|72h] [--captured-at '2026-10-21 10:51']
         [--map '行标题片段=EP或id' ...]      # 作品列表页一图多条时，把行对到作品；不给就按标题/发布时间自动匹配
     → inbox/screenshots/_ocr/<时间>/ocr_raw_*.json + review_<时间>.md，screenshot_extractions(status=待核)
  2) 人工读数对照（可选，强烈建议）：
     python3 scripts/ingest_screenshot.py check <extraction_id> --expect plays=722 likes=13 completion_rate=5.33% ...
     → 每个字段 OCR vs 人工：一致/不一致/OCR缺/人工缺；全部一致 → 可 confirm；有不一致 → status=有出入，必须人工改值后再 confirm
  3) 确认入库：
     python3 scripts/ingest_screenshot.py confirm <extraction_id> [--by 用户] [--set plays=13000 ...] [--precision 'plays=界面显示1.3万，取整到千']
     → metrics_snapshots（verified=1、age_h、missing_fields、precision_note）+ metric_values（字段级出处）+ traffic_terms + retention_curve
  其它：list [--status 待核]；void <id>（作废，不删）。
规则：不编数。OCR 读不出就是缺失；百分比/万/秒按原文换算；「1.3万」这类取整值必须写 precision。
qoder 每次 ≤5 张图；统计截止时间优先用页面显示，没有就记 NULL 并以截图时间作 captured_at。"""
import sys, os, re, json, argparse, pathlib, subprocess, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
from ingest_metrics import num, store, COLS
PROMPT = pathlib.Path(__file__).parent / "prompts" / "ocr_creator_center.txt"
MODEL = os.environ.get("QODER_MODEL", "Qwen3.8-Flash")
OUT = pathlib.Path(os.environ.get("STUDIO_SHOTS") or db.ROOT / "inbox" / "screenshots") / "_ocr"
# OCR 字段名 → (库字段, 类型)；库外字段（点赞率等）进 metric_values/raw_json
MAP = {"播放量": ("plays", "int"), "点赞量": ("likes", "int"), "评论量": ("comments", "int"), "分享量": ("shares", "int"), "收藏量": ("favorites", "int"),
       "完播率": ("completion_rate", "rate"), "5s完播率": ("completion_5s", "rate"), "2s跳出率": ("bounce_2s", "rate"), "平均播放时长": ("avg_watch_s", "sec"),
       "平均播放占比": ("avg_watch_ratio", "rate"), "封面点击率": ("cover_ctr", "rate"), "粉丝增量": ("follows_gained", "int"), "掉粉量": ("unfollows", "int"), "粉丝播放占比": ("fan_play_share", "rate"), "吸粉量": ("follows_gained", "int"), "涨粉": ("follows_gained", "int"), "主页访问量": ("profile_visits", "int"),
       "点赞率": ("like_rate", "rate"), "评论率": ("comment_rate", "rate"), "分享率": ("share_rate", "rate"), "收藏率": ("favorite_rate", "rate"),
       "弹幕量": ("danmaku", "int"), "不感兴趣率": ("not_interested_rate", "rate")}
KIND = {f: k for f, k in MAP.values()}
KIND.update(plays='int')
CORE = ["plays", "likes", "comments", "shares", "favorites", "completion_rate", "completion_5s", "bounce_2s", "avg_watch_s", "avg_watch_ratio", "follows_gained"]

def rate_raw(s):
    """比率原文：OCR 给的一律是界面显示值。'5.33%'→0.0533；无 % 的数值按百分数处理（界面不会显示 0.0533）。"""
    if s is None: return None
    t = str(s).strip()
    if t in ("", "-", "--", "—"): return None
    v = num(t.rstrip("%") + "%", "rate"); return v

def parse_val(field, raw):
    k = KIND.get(field, "rate")
    if raw is None: return None
    if k == "rate": return rate_raw(raw)
    return num(raw, k)

def precision_of(field, raw):
    if raw is None: return None
    t = str(raw)
    m = re.match(r"^\s*([\d.]+)\s*(万|w|W)\s*$", t)
    if m:
        dec = len(m.group(1).split(".")[1]) if "." in m.group(1) else 0
        unit = 10000 / (10 ** dec); return f"界面显示「{t}」，取整到 {unit:,.0f}（±{unit/2:,.0f}）"
    if KIND.get(field) == "sec" and re.match(r"^\s*\d+\s*秒?\s*$", t): return f"界面显示「{t}」，取整到秒（±0.5s）"
    return None

def shot_time(p):
    m = re.search(r"(\d{4}-\d{2}-\d{2})[_ T](\d{2})(\d{2})", p.name)
    if m: return db.parse_time(f"{m.group(1)} {m.group(2)}:{m.group(3)}")
    return dt.datetime.fromtimestamp(p.stat().st_mtime, db.TZ)

def dhash(p, n=16):
    from PIL import Image
    im = Image.open(p).convert("L").resize((n + 1, n)); px = im.tobytes()
    bits = "".join("1" if px[r*(n+1)+c] > px[r*(n+1)+c+1] else "0" for r in range(n) for c in range(n))
    return f"{int(bits, 2):064x}", Image.open(p).size

def hamming(a, b): return bin(int(a, 16) ^ int(b, 16)).count("1")

def register_shot(c, p, max_dist=8):
    """登记截图；返回 (sha256, dup_of_path或None)。dup：字节相同，或尺寸相同且 dhash 距离 ≤ max_dist（256 位）。"""
    sha = db.sha256_file(p); ph, (w, h) = dhash(p)
    r = c.execute("SELECT * FROM screenshot_files WHERE sha256=?", (sha,)).fetchone()
    if r: return sha, (r["dup_of"] or (r["path"] if r["path"] != str(p) else None))
    dup = None
    for x in c.execute("SELECT * FROM screenshot_files WHERE width=? AND height=? AND dup_of IS NULL", (w, h)):
        if hamming(x["phash"], ph) <= max_dist: dup = x["path"]; break
    c.execute("INSERT INTO screenshot_files VALUES(?,?,?,?,?,?,?)", (sha, str(p), ph, w, h, dup, db.now())); return sha, dup

def run_qoder(imgs, odir):
    """≤5 张一批调 qoder Flash；返回 {文件名: image_json}。原始输出全部落盘。"""
    res = {}
    for i in range(0, len(imgs), 5):
        batch = imgs[i:i+5]; atts = sum((["--attachment", str(p)] for p in batch), [])
        q = PROMPT.read_text(encoding="utf-8") + "\n本批文件：" + "、".join(p.name for p in batch)
        out = None
        for attempt in range(2):
            r = subprocess.run(["timeout", "480", "qoderclicn", "-p", "-m", MODEL, "--permission-mode", "bypass_permissions", *atts, q],
                               capture_output=True, text=True, cwd=str(odir))
            (odir / f"ocr_raw_{i//5}_{attempt}.txt").write_text(r.stdout + "\n--- stderr ---\n" + r.stderr[-3000:], encoding="utf-8")
            m = re.search(r"\{.*\}", r.stdout, re.S)
            if r.returncode == 0 and m:
                try: out = json.loads(m.group(0)); break
                except json.JSONDecodeError: pass
        if not out: raise SystemExit(f"qoder 没返回可解析 JSON，原始输出见 {odir}")
        (odir / f"ocr_raw_{i//5}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        imgs_j = out.get("images") or []
        for k, p in enumerate(batch):
            j = next((x for x in imgs_j if x.get("file") and pathlib.Path(x["file"]).name == p.name), None) or (imgs_j[k] if k < len(imgs_j) else None)
            res[p.name] = j or {}
    return res

def ocr_time(t):
    """'2026年10月19日 19:05 已发布' / '2026-10-19 19:05' → datetime；看不懂返回 None。"""
    m = re.search(r"(\d{4})\D(\d{1,2})\D(\d{1,2})\D*?\s*(\d{1,2}):(\d{2})", t or "")
    return db.parse_time(f"{m.group(1)}-{m.group(2)}-{m.group(3)} {m.group(4)}:{m.group(5)}") if m else None

def match_work(c, row, hint=None):
    if hint: return db.find_work(c, hint)
    t = db.norm(row.get("title") or "")
    best = None
    for w in c.execute("SELECT * FROM works WHERE status IN ('已发布','待发布')"):
        for cand in (w["publish_title"], w["title"]):
            n = db.norm(cand or "")
            if t and n and (t[:8] in n or n[:8] in t): best = w; break
        if best: break
        pt = ocr_time(row.get("publish_time"))
        if pt and w["publish_time"] and abs((pt - db.parse_time(w["publish_time"])).total_seconds()) < 120: best = w; break
    return best

def ck_label(age_h, given):
    if given and given != "auto": return given
    return f"{max(1, round(age_h))}h"

def cmd_extract(a):
    c = db.connect(); imgs = [pathlib.Path(x).resolve() for x in a.images]
    for p in imgs:
        if not p.is_file(): sys.exit(f"找不到图片：{p}")
    stamp = db.now_dt().strftime("%Y%m%d_%H%M%S"); odir = OUT / stamp; odir.mkdir(parents=True, exist_ok=True)
    maps = dict(m.split("=", 1) for m in a.map); keep = []
    for p in imgs:
        sha, dup = register_shot(c, p)
        if dup: print(f"= {p.name} 与 {pathlib.Path(dup).name} 内容相同（感知哈希），不重复 OCR/入库")
        else: keep.append(p)
    c.commit(); imgs = keep
    if not imgs: print("没有新内容的截图"); return
    ocr = run_qoder(imgs, odir); made = []
    for p in imgs:
        j = ocr.get(p.name) or {}; sha = db.sha256_file(p)
        cap = db.parse_time(a.captured_at) if a.captured_at else shot_time(p)
        rows = j.get("works") or [{}]
        for row in rows:
            hint = a.work or next((v for k, v in maps.items() if db.norm(k) in db.norm(row.get("title") or "")), None)
            w = match_work(c, row, hint)
            if not w: print(f"⚠ {p.name}：行「{(row.get('title') or '')[:24]}」对不上作品，跳过（用 --map 指定）"); continue
            age = (cap - db.parse_time(w["publish_time"])).total_seconds() / 3600 if w["publish_time"] else None
            ck = ck_label(age, a.checkpoint) if age is not None else (a.checkpoint if a.checkpoint != "auto" else None)
            if not ck: print(f"⚠ #{w['id']} 没有发布时间，不能自动定检查点；先 mark_published 或给 --checkpoint"); continue
            parsed = {}
            for name, raw in (row.get("metrics") or {}).items():
                if name in MAP and raw not in (None, ""):
                    f = MAP[name][0]; parsed[f] = dict(value=parse_val(f, raw), raw=str(raw), precision=precision_of(f, raw))
            missing = [f for f in CORE if f not in parsed]
            extra = {k: j.get(k) for k in ("traffic_sources", "search_terms_in", "search_after", "chapters", "retention_curve", "hourly_plays", "comments", "uncertain", "stat_cutoff", "page_kind")}
            if len(rows) > 1:   # 列表页：流量/搜索词等块不属于某一行
                extra = {k: v for k, v in extra.items() if k in ("uncertain", "stat_cutoff", "page_kind")}
            pj = dict(metrics=parsed, missing=missing, row=row, **extra)
            ex = c.execute("SELECT id,status FROM screenshot_extractions WHERE sha256=? AND work_id=?", (sha, w["id"])).fetchone()
            if ex and ex["status"] == "已确认": print(f"= {p.name} → #{w['id']} 已确认过（extraction#{ex['id']}），sha256 相同，跳过"); continue
            vals = (str(p), sha, w["id"], j.get("page_kind"), row.get("title"), ck, round(age, 2) if age is not None else None, cap.isoformat(timespec="seconds"),
                    j.get("stat_cutoff"), MODEL, json.dumps(j, ensure_ascii=False), json.dumps(pj, ensure_ascii=False), db.now())
            if ex:
                c.execute("""UPDATE screenshot_extractions SET file=?,sha256=?,work_id=?,page_kind=?,row_label=?,checkpoint=?,age_h=?,captured_at=?,stat_cutoff=?,
                             ocr_model=?,ocr_json=?,parsed_json=?,created_at=?,status='待核',check_json=NULL WHERE id=?""", (*vals, ex["id"])); eid = ex["id"]
            else:
                eid = c.execute("""INSERT INTO screenshot_extractions(file,sha256,work_id,page_kind,row_label,checkpoint,age_h,captured_at,stat_cutoff,ocr_model,ocr_json,parsed_json,created_at)
                                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""", vals).lastrowid
            made.append(eid)
    c.commit()
    rp = odir / f"review_{stamp}.md"; write_review(c, made, rp)
    c.executemany("UPDATE screenshot_extractions SET review_path=? WHERE id=?", [(str(rp), i) for i in made]); c.commit()
    print(f"抽取 {len(made)} 条（待核）：{made}\n人工核对文件：{rp}\n下一步：check <id> --expect ... 或直接让用户看 review 后 confirm <id>")

def fmtv(f, v):
    if v is None: return "—"
    k = KIND.get(f, "int")
    return f"{v:.2%}" if k == "rate" else (f"{v:.1f}s" if k == "sec" else f"{v:,.0f}")

def write_review(c, ids, rp):
    L = [f"# 截图抽取核对单（{db.now()}，OCR：qoder {MODEL}）", "", "请逐项对照原图：对的打 ✓，错的写正确值。确认后才会入库（verified=1）。", ""]
    for eid in ids:
        e = c.execute("SELECT x.*, w.episode, w.title wt, w.publish_time FROM screenshot_extractions x JOIN works w ON w.id=x.work_id WHERE x.id=?", (eid,)).fetchone()
        pj = json.loads(e["parsed_json"])
        L += [f"## extraction#{eid} · #{e['work_id']} {e['episode']}《{(e['wt'] or '')[:24]}》", f"- 截图：`{e['file']}`（行：{e['row_label'] or '—'}）",
              f"- 截图时间 {e['captured_at']}｜发布 {e['publish_time']}｜发布后 {e['age_h']} 小时 → 检查点 **{e['checkpoint']}**｜页面统计截止：{e['stat_cutoff'] or '页面未显示'}", "",
              "| 字段 | 截图原文 | 换算值 | 精度 | 核对 |", "|---|---|---|---|---|"]
        for f, d in pj["metrics"].items(): L.append(f"| {f} | {d['raw']} | {fmtv(f, d['value'])} | {d['precision'] or '原值'} | ☐ |")
        L += ["", f"- 缺失字段（这张图里没有）：{', '.join(pj['missing']) or '无'}"]
        for k, name in (("traffic_sources", "流量来源"), ("search_terms_in", "搜索来源词"), ("search_after", "看后常搜"), ("chapters", "章节点击")):
            if pj.get(k): L.append(f"- {name}：" + "；".join(f"{x.get('term') or x.get('name') or x.get('title')} {x.get('share') or x.get('click_rate')}" for x in pj[k]))
        rc = pj.get("retention_curve") or {}
        if rc: L.append(f"- 留存曲线：{'读到 %d 点' % len(rc.get('points') or []) if rc.get('points') else '无可读数值点（' + str(rc.get('note') or '图里没有刻度点') + '）'}"
                        + (f"；平台标注：" + "、".join(f"{v.get('label')} {v.get('range')}" for v in rc.get('valleys') or []) if rc.get('valleys') else "")
                        + (f"；与同类：{rc.get('vs_peer')}" if rc.get('vs_peer') else ""))
        if pj.get("hourly_plays"): L.append("- 每小时播放：" + "；".join(f"{x.get('time')} {x.get('plays')}" for x in pj["hourly_plays"] if x.get("plays") not in (None, "")))
        if pj.get("uncertain"): L.append("- OCR 自报不确定：" + "；".join(pj["uncertain"]))
        if e["check_json"]:
            ck = json.loads(e["check_json"]); L += ["", "**与人工读数对照**：" + "；".join(f"{f} {r['result']}" for f, r in ck.items())]
        L.append("")
    rp.write_text("\n".join(L), encoding="utf-8")

def parse_expect(items):
    out = {}
    for kv in items:
        f, v = kv.split("=", 1)
        if f not in KIND: sys.exit(f"不认识的字段 {f}；可用：{', '.join(KIND)}")
        out[f] = (parse_val(f, v), v)
    return out

def same(f, a, b):
    if a is None or b is None: return False
    return abs(a - b) < (1e-6 if KIND.get(f) == "rate" else 0.51)

TERM_KEYS = {"term": None, "src": "流量来源", "chap": "章节点击"}
TERM_BLOCK = {"搜索来源词": "search_terms_in", "看后常搜": "search_after", "流量来源": "traffic_sources", "章节点击": "chapters"}

def cmd_check(a):
    c = db.connect(); e = c.execute("SELECT * FROM screenshot_extractions WHERE id=?", (a.id,)).fetchone()
    if not e: sys.exit("没有这条 extraction")
    pj = json.loads(e["parsed_json"]); res = {}
    texp = [x for x in a.expect if x.split(":", 1)[0] in TERM_KEYS]; exp = parse_expect([x for x in a.expect if x not in texp])
    for x in texp:   # term:搜索来源词:词=23.9%  /  src:搜索=41.9%  /  chap:00:42 视频分析=75.6%
        pre, rest = x.split(":", 1); kind = TERM_KEYS[pre]
        if pre == "term": kind, rest = rest.split(":", 1)
        term, v = rest.rsplit("=", 1); got = None
        for item in pj.get(TERM_BLOCK[kind]) or []:
            name = item.get("term") or item.get("name") or f"{item.get('time')} {item.get('title')}"
            if db.norm(name) == db.norm(term): got = item.get("share") or item.get("click_rate"); break
        mv = rate_raw(v); ov = rate_raw(got)
        r = "一致" if (ov is not None and abs(ov - mv) < 1e-6) else (f"OCR 缺（人工 {v}）" if got is None else f"不一致（OCR {got} / 人工 {v}）")
        res[f"{kind}:{term}"] = dict(result=r, ocr=got, manual=v)
    for f in sorted(set(pj["metrics"]) | set(exp)):
        o = pj["metrics"].get(f); m = exp.get(f)
        if o and m: r = "一致" if same(f, o["value"], m[0]) else f"不一致（OCR {o['raw']} / 人工 {m[1]}）"
        elif o: r = f"人工未读（OCR {o['raw']}）"
        else: r = f"OCR 缺（人工 {m[1]}）"
        res[f] = dict(result=r, ocr=o and o["raw"], manual=m and m[1])
    bad = [f for f, r in res.items() if r["result"].startswith(("不一致", "OCR 缺"))]
    st = "有出入" if bad else "待核"
    c.execute("UPDATE screenshot_extractions SET check_json=?, status=? WHERE id=?", (json.dumps(res, ensure_ascii=False), st, a.id)); c.commit()
    if e["review_path"]:
        ids = [r[0] for r in c.execute("SELECT id FROM screenshot_extractions WHERE review_path=?", (e["review_path"],))]; write_review(c, ids, pathlib.Path(e["review_path"]))
    for f, r in res.items(): print(f"  {f:16} {r['result']}")
    print(f"extraction#{a.id}：{'全部一致，可 confirm' if not bad else '有出入：' + ', '.join(bad) + ' —— 改值后用 confirm --set 写入'}")

def merge_prec(old, new):
    d = {}
    for part in (old or "").split("；"):
        if ":" in part: k, v = part.split(":", 1); d[k] = v
    d.update(new)
    return "；".join(f"{k}:{v}" for k, v in d.items()) or None

def cmd_confirm(a):
    c = db.connect(); e = c.execute("SELECT * FROM screenshot_extractions WHERE id=?", (a.id,)).fetchone()
    if not e: sys.exit("没有这条 extraction")
    if e["status"] == "作废": sys.exit("已作废")
    if e["status"] == "有出入" and not a.set and not a.term and not a.force: sys.exit("这条 OCR 与人工读数有出入；用 --set 写正确值，或 --force（不建议）")
    pj = json.loads(e["parsed_json"]); m = {f: d["value"] for f, d in pj["metrics"].items()}; prec = {f: d["precision"] for f, d in pj["metrics"].items() if d["precision"]}
    manual = parse_expect(a.set)
    for f, (v, raw) in manual.items(): m[f] = v
    for kv in a.precision: f, t = kv.split("=", 1); prec[f] = t
    ck = json.loads(e["check_json"] or "{}")
    fname = pathlib.Path(e["file"]).name; src = f"截图 {fname}（qoder OCR extraction#{e['id']}；{a.by}确认 {db.now()}）"
    raw = dict(screenshot=dict(file=e["file"], extraction=e["id"], age_h=e["age_h"], stat_cutoff=e["stat_cutoff"], other_rates={f: m[f] for f in m if f not in COLS},
                               traffic_sources=pj.get("traffic_sources"), search_terms_in=pj.get("search_terms_in"), search_after=pj.get("search_after"), chapters=pj.get("chapters")))
    for x in pj.get("traffic_sources") or []:   # 流量来源 → search_share / recommend_share
        nm = x.get("name") or ""; v = rate_raw(x.get("share"))
        if re.fullmatch(r"搜索(页)?", nm): m["search_share"] = v
        elif re.fullmatch(r"推荐(页)?", nm): m["recommend_share"] = v
    ret = []
    rc = pj.get("retention_curve") or {}
    if rc.get("present") and rc.get("points"):
        from ingest_metrics import tsec
        ret = [(tsec(p["t"]), rate_raw(p["v"])) for p in rc["points"] if tsec(p["t"]) is not None and rate_raw(p["v"]) is not None]
    prev = c.execute("SELECT * FROM metrics_snapshots WHERE work_id=? AND platform='抖音' AND checkpoint=?", (e["work_id"], e["checkpoint"])).fetchone()
    kept = []
    if prev:   # 已有更精确的值（如 xlsx 0.072664）且与截图显示值在显示精度内一致 → 保留原值，不用取整值覆盖
        for f in list(m):
            if f in COLS and prev[f] is not None and m[f] is not None:
                k = KIND.get(f); tol = 0.00006 if k == "rate" else 0.51 if k == "sec" else (500 if "万" in str((pj["metrics"].get(f) or {}).get("raw") or "") else 0)
                if abs(prev[f] - m[f]) <= tol and prev[f] != m[f]: kept.append(f"{f}: 保留原值 {prev[f]}（截图 {m[f]} 在显示精度内一致）"); m[f] = prev[f]; prec.pop(f, None)
    sid = store(c, e["work_id"], e["checkpoint"], "抖音", {k: m.get(k) for k in COLS}, ret if len(ret) >= 3 else None, src, e["captured_at"], raw)
    allok = all(r["result"] == "一致" for r in ck.values()) if ck else False
    if kept: print("；".join(kept))
    vnote = (f"{a.by}确认；OCR 与人工读数逐项一致（{len(ck)} 项）" if allok else f"{a.by}确认；" + ("；".join(f"{f}:{r['result']}" for f, r in ck.items() if r['result'] != '一致') or "未做人工对照"))
    if prev and prev["verify_note"] and prev["verify_note"] not in vnote: vnote = prev["verify_note"] + "｜" + f"extraction#{e['id']}：" + vnote
    c.execute("UPDATE metrics_snapshots SET age_h=?, stat_cutoff=?, missing_fields=?, verified=?, verify_note=?, precision_note=? WHERE id=?",
              (e["age_h"], e["stat_cutoff"], json.dumps(pj["missing"], ensure_ascii=False), 1, vnote, merge_prec((prev["precision_note"] if prev else None), prec), sid))
    for f, v in m.items():
        r0 = pj["metrics"].get(f, {}).get("raw"); r1 = manual.get(f, (None, None))[1]
        c.execute("INSERT OR REPLACE INTO metric_values VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                  (sid, f, v, r1 or r0, "manual_read" if r1 else "screenshot_ocr", fname, prec.get(f), 1,
                   (ck.get(f) or {}).get("result") or ("人工改值" if r1 else "未人工对照"), e["id"], db.now()))
    for tc in a.term or []:   # 人工改正：'搜索来源词:特斯拉Roadster为什么会飞=57.2%'
        kind, rest = tc.split(":", 1); term, v = rest.rsplit("=", 1); blk = pj.setdefault(TERM_BLOCK[kind], [])
        it = next((x for x in blk if db.norm(x.get("term") or x.get("name") or "") == db.norm(term)), None)
        if it: it["share"] = v; it["manual"] = True
        else: blk.append(dict(term=term, share=v, manual=True))
    for k, kind in (("search_terms_in", "搜索来源词"), ("search_after", "看后常搜"), ("traffic_sources", "流量来源"), ("chapters", "章节点击")):
        for i, x in enumerate(pj.get(k) or []):
            term = x.get("term") or x.get("name") or (f"{x.get('time')} {x.get('title')}" if x.get("title") else None)
            if not term: continue
            c.execute("""INSERT INTO traffic_terms(work_id,checkpoint,kind,rank,term,share,delta,source,extraction_id,verified,captured_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)
                         ON CONFLICT(work_id,checkpoint,kind,term) DO UPDATE SET share=excluded.share,rank=excluded.rank,source=excluded.source,extraction_id=excluded.extraction_id,verified=1""",
                      (e["work_id"], e["checkpoint"], kind, x.get("rank") or i + 1, term, rate_raw(x.get("share") or x.get("click_rate")), x.get("delta"), src, e["id"], 1, e["captured_at"]))
    def rng(t):
        m = re.findall(r"(\d{1,2}):(\d{2})", t or "")
        return [int(a)*60 + int(b) for a, b in m] if m else []
    marks = a.marks or [f"{v.get('label')}={v.get('range')}" for v in (rc.get("valleys") or []) if v.get("range")]
    for mk in marks:
        lab, r = mk.split("=", 1); ts = rng(r)
        if not ts: continue
        c.execute("""INSERT INTO retention_marks(work_id,checkpoint,kind,label,t_start,t_end,source,precision,extraction_id,verified,captured_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)
                     ON CONFLICT(work_id,checkpoint,kind,label) DO UPDATE SET t_start=excluded.t_start,t_end=excluded.t_end,source=excluded.source,extraction_id=excluded.extraction_id,verified=1""",
                  (e["work_id"], e["checkpoint"], "低谷", lab, ts[0], ts[-1] if len(ts) > 1 else ts[0] + 1, "screenshot_ocr " + src + ("" if a.marks is None else "；时间段为人工读图"), "平台标注时间段，截图读取，约 ±1s", e["id"], 1 if (a.marks is None or a.marks_verified) else 0, e["captured_at"]))
    vp = a.vs_peer or rc.get("vs_peer")
    if vp:
        c.execute("""INSERT INTO retention_marks(work_id,checkpoint,kind,label,note,source,precision,extraction_id,verified,captured_at) VALUES(?,?,?,?,?,?,?,?,?,?)
                     ON CONFLICT(work_id,checkpoint,kind,label) DO UPDATE SET note=excluded.note,source=excluded.source,verified=1""",
                  (e["work_id"], e["checkpoint"], "同类对比", "同类作品参考线", vp, "screenshot_ocr " + src, "定性，读图", e["id"], 1, e["captured_at"]))
    for x in pj.get("hourly_plays") or []:
        v = num(x.get("plays"), "int") if x.get("plays") not in (None, "") else None
        if v is not None and x.get("time"):
            c.execute("INSERT OR REPLACE INTO hourly_plays VALUES(?,?,?,?,?,?)", (e["work_id"], x["time"], v, 1, "screenshot_ocr " + src, e["id"]))
    if ret and len(ret) >= 3:
        c.execute("UPDATE metrics_snapshots SET precision_note=COALESCE(precision_note||'；','')||? WHERE id=?",
                  (f"留存曲线 {len(ret)} 点为截图读图（source=screenshot_ocr），精度受图表分辨率限制，约 ±2 个百分点", sid))
    snap = c.execute("SELECT * FROM metrics_snapshots WHERE id=?", (sid,)).fetchone()
    c.execute("UPDATE metrics_snapshots SET missing_fields=? WHERE id=?", (json.dumps([f for f in CORE if snap[f] is None], ensure_ascii=False), sid))
    c.execute("UPDATE screenshot_extractions SET status='已确认', confirmed_at=?, snapshot_id=?, parsed_json=? WHERE id=?", (db.now(), sid, json.dumps(pj, ensure_ascii=False), e["id"]))
    c.commit(); print(f"extraction#{e['id']} → metrics_snapshots#{sid}（#{e['work_id']} {e['checkpoint']}，verified=1，合并后仍缺 {[f for f in CORE if snap[f] is None]}）")

def cmd_list(a):
    c = db.connect()
    for r in c.execute("SELECT x.id,x.status,x.work_id,x.checkpoint,x.age_h,x.file,w.episode FROM screenshot_extractions x LEFT JOIN works w ON w.id=x.work_id "
                       + ("WHERE x.status=? " if a.status else "") + "ORDER BY x.id", ((a.status,) if a.status else ())):
        print(f"#{r['id']:<4}[{r['status']}] #{r['work_id']} {r['episode']} {r['checkpoint']}（{r['age_h']}h） {pathlib.Path(r['file']).name}")

def cmd_void(a):
    c = db.connect(); c.execute("UPDATE screenshot_extractions SET status='作废' WHERE id=?", (a.id,)); c.commit(); print("已作废（记录保留）")

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); sp = ap.add_subparsers(dest="cmd", required=True)
p = sp.add_parser("extract"); p.add_argument("images", nargs="+"); p.add_argument("--work"); p.add_argument("--checkpoint", default="auto")
p.add_argument("--captured-at"); p.add_argument("--map", nargs="*", default=[])
p = sp.add_parser("check"); p.add_argument("id", type=int); p.add_argument("--expect", nargs="+", required=True)
p = sp.add_parser("confirm"); p.add_argument("id", type=int); p.add_argument("--by", default="用户"); p.add_argument("--set", nargs="*", default=[])
p.add_argument("--precision", nargs="*", default=[]); p.add_argument("--force", action="store_true")
p.add_argument("--term", nargs="*", help="人工改正的词/来源：'搜索来源词:词=57.2%'")
p.add_argument("--marks-verified", action="store_true", help="低谷时间段已由第二次 OCR/人工交叉核对一致")
p.add_argument("--marks", nargs="*", help="人工改正的平台低谷标注：'低谷1=00:01-00:02' ...（不给就用 OCR 读到的）"); p.add_argument("--vs-peer", help="人工改正的『与同类对比』描述")
p = sp.add_parser("list"); p.add_argument("--status")
p = sp.add_parser("void"); p.add_argument("id", type=int)
if __name__ == "__main__":
    a = ap.parse_args(); {"extract": cmd_extract, "check": cmd_check, "confirm": cmd_confirm, "list": cmd_list, "void": cmd_void}[a.cmd](a)
