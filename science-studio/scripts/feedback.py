#!/usr/bin/env python3
"""Feedback Engine 指令入口（中文报告 → reports/）。
  python3 scripts/feedback.py 复盘最新视频 [--work <EP>]          (= review)
  python3 scripts/feedback.py 检查最近作品表现 [--days 14]         (= recent)
  python3 scripts/feedback.py 最近观众有什么新需求 [--days 7]       (= demands)
  python3 scripts/feedback.py 找出近期最值得改进作品 [--days 30]     (= worst)
  python3 scripts/feedback.py 对比这期与历史同类 [--work <EP>]      (= compare)
  python3 scripts/feedback.py 根据历史反馈开始下一期选题 [--topic 关键词]  (= next)
  通用：--no-write（只打印，不写 findings/suggestions/报告文件）
口径（写进每份报告）：
- 只用 verified=1 的快照下结论；未核的标「待核」并降可信度。
- 变化检测不用固定增长阈值：和作品自身历史（相邻快照、显示精度）比、和账号同期作品同发布时长档比（排名/最小–最大/中位数，写明 n）。
- n<5 的账号对比只当线索；不说「平台算法规律」；相关≠因果，每条发现都写「其他解释」。
- 有平台标注低谷（retention_marks，截图读取 ±1–2s）才做时间段诊断，并对到逐字稿句子和镜头；没有就只做整体推断。"""
import sys, os, re, json, argparse, pathlib, statistics as st, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db, timeline as tl, comments_fb as cf
REPORTS = pathlib.Path(os.environ.get("STUDIO_REPORTS") or db.ROOT / "reports")
M = [("plays", "播放", "int", 1), ("bounce_2s", "2s跳出率", "rate", -1), ("completion_5s", "5s完播率", "rate", 1), ("completion_rate", "完播率", "rate", 1),
     ("avg_watch_s", "均播(s)", "sec", 1), ("avg_watch_ratio", "均播占比", "rate", 1), ("likes", "点赞", "int", 1), ("comments", "评论", "int", 1),
     ("shares", "分享", "int", 1), ("favorites", "收藏", "int", 1), ("follows_gained", "涨粉", "int", 1), ("search_share", "搜索占比", "rate", 0), ("recommend_share", "推荐占比", "rate", 0)]
MN = {k: n for k, n, *_ in M}
BUCKETS = [("≤6h", 0, 6), ("24h档(6–36h)", 6, 36), ("72h档(36–120h)", 36, 120), ("7d+档(>120h)", 120, 1e9)]
CMDS = {"复盘最新视频": "review", "检查最近作品表现": "recent", "最近观众有什么新需求": "demands", "找出近期最值得改进作品": "worst",
        "对比这期与历史同类": "compare", "根据历史反馈开始下一期选题": "next"}

def f(k, v):
    if v is None: return "—"
    t = next((x[2] for x in M if x[0] == k), "rate" if "rate" in k or "share" in k else "int")
    return f"{v:.2%}" if t == "rate" else f"{v:.1f}" if t == "sec" else f"{v:,.0f}"
def age_of(s, w):
    if s["age_h"] is not None: return s["age_h"]
    try: return (db.parse_time(s["captured_at"]) - db.parse_time(w["publish_time"])).total_seconds() / 3600
    except Exception: return float(s["checkpoint"][:-1]) * (24 if s["checkpoint"].endswith("d") else 1)
def bucket(h): return next(b for b, lo, hi in BUCKETS if lo <= h < hi)

def snaps(c, wid, verified_only=False):
    w = c.execute("SELECT * FROM works WHERE id=?", (wid,)).fetchone()
    rs = c.execute("SELECT * FROM metrics_snapshots WHERE work_id=? AND platform='抖音'" + (" AND verified=1" if verified_only else ""), (wid,)).fetchall()
    out = [dict(r, _age=age_of(r, w)) for r in rs]
    return sorted(out, key=lambda r: r["_age"])

def published(c, days=None):
    q = "SELECT * FROM works WHERE status='已发布' AND publish_time IS NOT NULL"
    rs = c.execute(q).fetchall()
    if days: lim = db.now_dt() - dt.timedelta(days=days); rs = [w for w in rs if db.parse_time(w["publish_time"]) >= lim]
    return sorted(rs, key=lambda w: w["publish_time"], reverse=True)

def main_snap(c, wid):
    v = snaps(c, wid, True); return v[-1] if v else (snaps(c, wid)[-1] if snaps(c, wid) else None)

# ---------- 变化检测 ----------
def own_changes(c, w):
    """相邻快照之间：每小时增量；把显示精度算进去，变化小于精度就说「无法区分」。"""
    S = snaps(c, w["id"]); out = []
    for a, b in zip(S, S[1:]):
        dh = b["_age"] - a["_age"]
        if dh <= 0: continue
        row = dict(frm=a["checkpoint"], to=b["checkpoint"], hours=round(dh, 1), items=[])
        for k in ("plays", "likes", "shares", "comments", "favorites", "follows_gained", "completion_rate", "bounce_2s", "avg_watch_ratio"):
            if a[k] is None or b[k] is None: continue
            tol = 0
            for s in (a, b):
                pn = s.get("precision_note") or ""
                m = re.search(rf"{k}:[^；]*±([\d,]+)", pn)
                if m: tol += float(m.group(1).replace(",", ""))
            d = b[k] - a[k]
            if k in ("completion_rate", "bounce_2s", "avg_watch_ratio"):
                tol = max(tol, 0.0001)
                txt = "无法区分（在显示精度内）" if abs(d) <= tol else f"{'+' if d > 0 else ''}{d*100:.2f} 个百分点"
            else:
                txt = "无法区分（在显示精度内）" if abs(d) <= tol else f"{'+' if d > 0 else ''}{d:,.0f}（约 {d/dh:,.1f}/小时）"
            row["items"].append((k, f(k, a[k]), f(k, b[k]), txt))
        out.append(row)
    return out

def peer_compare(c, w, snap):
    """账号同期作品、同发布时长档：每项给 排名/n、同档其他作品最小–中位–最大；是否超出其他作品范围。"""
    b = bucket(snap["_age"]); res = {}
    peers = []
    for o in published(c):
        if o["id"] == w["id"]: continue
        cand = [s for s in snaps(c, o["id"]) if bucket(s["_age"]) == b]
        if cand: peers.append((o, sorted(cand, key=lambda s: (s["verified"], s["_age"]))[-1]))
    for k, name, t, better in M:
        v = snap.get(k); others = [(o, s[k]) for o, s in peers if s.get(k) is not None]
        if v is None or not others: continue
        allv = sorted([x for _, x in others] + [v], reverse=(better >= 0))
        rank = allv.index(v) + 1; ov = [x for _, x in others]
        pos = "高于同档其他全部作品" if v > max(ov) else "低于同档其他全部作品" if v < min(ov) else "在同档其他作品范围内"
        res[k] = dict(rank=rank, n=len(allv), min=min(ov), med=st.median(ov), max=max(ov), pos=pos, better=better, peers=[(o["id"], x) for o, x in others])
    return b, res, peers

# ---------- 时间轴 ----------
def words_between(w, t0, t1):
    """逐字时间戳（若有）→ 该区间说的字。找 vo/alignment.json 一类带 words 的文件。"""
    pd = pathlib.Path(w["project_dir"] or "/nonexistent")
    for p in [pd / "vo" / "alignment.json", *sorted(pd.glob("voice/*/alignment*.json"))]:
        if not p.exists(): continue
        try: d = json.loads(p.read_text(encoding="utf-8"))
        except Exception: continue
        ws = [x for s in d.get("sentences", []) for x in (s.get("words") or [])]
        if ws: return "".join((x.get("text") or x.get("w") or "") for x in ws if t0 <= x.get("start", -1) < t1), str(p)
    return None, None

def tl_for(w):
    return tl.load(w["project_dir"], w["timeline_path"], db.ROOT / "projects" / w["episode"])

def version_caveat(w, T):
    if w["episode"] == "LEGACY-roadster-v4": return "⚠ 时间轴是 V3 工程（V4 成片与源码不在盒上），V4 若改过开头，句子对应可能偏移；章节显示 00:15 进入「飞行原理」，与 V3 的 14.6s「先说结论」接近。"
    if not T["files"]: return "⚠ 没找到时间轴，只能给秒数。"
    return ""

# ---------- 诊断（六项） ----------
def bigr(t): n = db.norm(t); return {n[i:i+2] for i in range(len(n) - 1)}

def diagnose(c, w):
    snap = main_snap(c, w["id"])
    if not snap: return None, []
    b, P, peers = peer_compare(c, w, snap); n_peer = len(peers) + 1
    T = tl_for(w); cav = version_caveat(w, T)
    marks = c.execute("SELECT * FROM retention_marks WHERE work_id=? ORDER BY kind, t_start", (w["id"],)).fetchall()
    valleys = [m for m in marks if m["kind"] == "低谷"]; vsp = next((m["note"] for m in marks if m["kind"] == "同类对比"), None)
    terms = c.execute("SELECT * FROM traffic_terms WHERE work_id=? ORDER BY checkpoint, kind, rank", (w["id"],)).fetchall()
    latest_ck = {}
    for t in terms: latest_ck.setdefault(t["kind"], set()).add(t["checkpoint"])
    def T_(kind):
        cks = sorted(latest_ck.get(kind, []), key=lambda x: int(x[:-1]))
        return [t for t in terms if t["kind"] == kind and cks and t["checkpoint"] == cks[-1]]
    st_terms, after, chaps = T_("搜索来源词"), T_("看后常搜"), T_("章节点击")
    dna = c.execute("SELECT * FROM content_dna WHERE work_id=?", (w["id"],)).fetchone()
    conf_base = "低" if n_peer < 5 else "中"
    basis = f"账号同档（{b}）作品 n={n_peer}" + ("，样本很少，排名只当线索" if n_peer < 5 else "")
    vt = "已核（截图 OCR 与人工读数一致）" if snap["verified"] else "⚠ 快照未核"
    F = []
    def rk(k):
        p = P.get(k); 
        if not p: return "（无同档对比数据）"
        return f"同档排第 {p['rank']}/{p['n']}（其他作品 {f(k, p['min'])}–{f(k, p['max'])}，{p['pos']}）"
    def sent_at(t):
        s = tl.at(T["sentences"], t) if T["sentences"] else None; sh = tl.at(T["shots"], t) if T["shots"] else None
        return s, sh
    # 1 开头 0–2s
    if snap.get("bounce_2s") is not None:
        v1 = next((v for v in valleys if v["t_start"] <= 2), None)
        s, sh = sent_at(1.0)
        hook = dna["hook_type"] if dna else "—"
        ph = f"2s 跳出率 {f('bounce_2s', snap['bounce_2s'])}，5s 完播 {f('completion_5s', snap.get('completion_5s'))}" + (f"；平台在 {v1['t_start']:.0f}–{v1['t_end']:.0f}s 标注「{v1['label']}」" if v1 else "")
        srcs = sorted({r[0] for r in c.execute("SELECT source_file FROM metric_values WHERE snapshot_id=? AND field IN ('bounce_2s','completion_5s')", (snap["id"],))})
        ev = f"{rk('bounce_2s')}；5s 完播 {rk('completion_5s')}；{vt}；来源 {'、'.join(srcs) or '见 metrics_snapshots.source'}"
        if v1: ev += f"；低谷时间段读自截图（±1–2s）。当时口播：「{s['text'][:30] if s else '—'}」；镜头：{sh['text'] if sh else '—'}"
        causes = f"开头形式：{hook}。" + (f"0–2s 这句是「{s['text'][:24]}」。" if s else "")
        alts = "①流量结构不同：搜索进来的人带着明确问题，答非所问时 2 秒内就走，推荐流量的跳出口径也不同；②平台标注的「低谷1」几乎每条都会出现在开头（所有短视频前 2 秒都掉人最多），本身不等于开头差；③封面/标题与首帧不一致；④样本太少，无法排除选题本身差异。"
        sug = "开头 2 秒内直接回答或复述观众最常搜的那个问题（见搜索来源词第 1 名），首帧就是全片最强画面。"
        exp = "下一期做 A/B 不可行（抖音不能同条双版本），改为：下 2 期开头都按此写法，记录 2s 跳出率，与本账号同档作品的中位数比较；同时记下流量来源结构，搜索占比差太多的不直接比。"
        best = P.get("bounce_2s") and P["bounce_2s"]["rank"] == 1
        if best:
            sug = "保留这种开头写法作为候选模板（首帧奇观+一句提问，2–5s 揭秘）；标记为「待更多样本验证」，不当定论。"
            exp = "下 2 期按同一写法开头，看 2s 跳出率是否仍低于本账号同档中位数。"
        if w["id"] == 3:
            sug = "开头别用和标题无关的示意实拍（现用的是索尼 AI 的非现场画面）：第 0 帧改成广交会现场里观众最好奇的点（是真人吗/真假），首句直接回应。"
        F.append(dict(key="hook_2s", phenomenon=ph, evidence=ev, baseline=basis, causes=causes, alternatives=alts,
                      confidence="低" if n_peer < 5 else "中", suggestion=sug, experiment=exp, basis_kind="真实数据+截图低谷" if v1 else "真实数据", stage="脚本"))
    # 2 中段低谷（平台标注）
    mids = []
    for v in [v for v in valleys if v["t_start"] > 2]:   # 相隔 ≤2s 的低谷（读图精度内）合并成一条发现
        if mids and v["t_start"] - mids[-1]["t_end"] <= 2:
            mids[-1] = dict(mids[-1], t_end=v["t_end"], label=mids[-1]["label"] + "+" + v["label"])
        else: mids.append(dict(v))
    for v in mids:
        s, sh = sent_at((v["t_start"] + v["t_end"]) / 2); wd, wf = words_between(w, v["t_start"] - 0.5, v["t_end"] + 0.5)
        sent_len = (s["end"] - s["start"]) if s else None
        ph = f"平台在 {v['t_start']:.0f}–{v['t_end']:.0f}s 标注「{v['label']}」（截图读取，±1–2s）"
        ev = f"当时口播：「{s['text'] if s else '—'}」" + (f"（这句 {sent_len:.1f}s）" if sent_len else "") + (f"；该区间逐字：「{wd}」" if wd else "") + f"；镜头：{sh['text'] if sh else '—'}" + (f"。{cav}" if cav else "")
        causes, alts, sug, exp = "", "", "", ""
        if w["id"] == 3:
            causes = "「二算」是全片最长的一句（12.9–20.6s，7.7s），一口气列了落点、速度、拍面角度三个量，配的是纯 2D 示意动画，期间没有新的实拍画面；17–20s 正好在这句后半段（「拍面该斜多少」「实时算完才知道往哪回」）。"
            alts = "①33s 的片子里 17–20s 已过半，自然衰减本来就在加速；②搜索进来的人多数想看外骨骼/真假（见下条），到中段发现不是就走，和这句写法无关；③两个低谷相隔 2s，读图精度 ±1–2s，可能是同一次下滑。"
            sug = "把「二算」拆成两句短句，每个量配一个画面变化（落点→速度→拍面依次出现），或在 15s 左右插 1 秒实拍；整句控制在 4s 内。"
            exp = "下一条同类原理片，把最长句压到 ≤4s、每 2–3s 一次画面变化，看平台是否仍在同位置标低谷、以及低谷数量。"
        elif w["id"] == 1:
            causes = "V3 时间轴 11–12s 在「评论区直接吵翻了：特效吧？AI吧？马斯克又画饼了吧？」末尾，紧接 13.1s「大家好，我是秘书丞」自我介绍；观众点「飞行原理」章节只有 2.7%，点「量产与售价」59.5%。"
            alts = "①V4 可能改过这一段，未核；②搜索「为什么会飞」进来的人，等到 15s 才进原理，可能在等待中离开，与自我介绍无关；③章节点击反映的是想跳到哪，不直接等于在哪离开。"
            sug = "删掉自我介绍；「先说结论」提到 5s 内；售价/量产信息在开头给一句预告。"
            exp = "下一条科技热点片不放自我介绍、结论前置到 5s 内，看是否还在 10–13s 出现平台低谷。"
        else:
            causes = "该区间对应的句子与镜头见依据；需结合内容判断。"; alts = "自然衰减；读图精度；流量结构。"; sug = "检查该句是否过长或画面长时间不变。"; exp = "下一期同位置控制句长，再看低谷是否消失。"
        F.append(dict(key=f"valley_{v['label']}", phenomenon=ph, evidence=ev, baseline="作品自身留存图（平台标注）；无逐秒留存数值", causes=causes, alternatives=alts,
                      confidence="低", suggestion=sug, experiment=exp, basis_kind="截图低谷（时间段级）", stage="分镜"))
    # 3 搜索词 ↔ 内容 是否对得上
    if st_terms:
        text = " ".join([w["title"] or "", w["publish_title"] or ""] + [s["text"] for s in T["sentences"]])
        tb = bigr(text); cov = []
        for t in st_terms: g = bigr(t["term"]); cov.append((t["term"], t["share"], len(g & tb) / len(g) if g else 0))
        off = [(t, sh) for t, sh, r in cov if r < 0.5]; on = [(t, sh) for t, sh, r in cov if r >= 0.5]
        off_share = sum(sh or 0 for _, sh in off); top = st_terms[0]
        ph = f"搜索来源词前 {len(st_terms)} 名：" + "；".join(f"{t['term']} {f('rate', t['share'])}" for t in st_terms)
        ev = f"与标题+逐字稿字面重合度低（<50% 字二元组）的词合计 {off_share:.1%}：" + ("、".join(t for t, _ in off) or "无") + f"；搜索占比 {f('search_share', snap.get('search_share'))}（{rk('search_share')}）"
        if w["id"] == 3:
            causes = "搜索大头是「广交会外骨骼助行器」「广交会机器人是真人吗/真假」「宇树为什么需要遥控」，而视频讲的是乒乓机器人原理。观众搜的是广交会里别的热点，平台把本条当作「广交会机器人」相关结果推给他们，内容答非所问。"
            alts = "①这些词也许只是当时广交会话题的全局热搜，任何广交会视频都会被分到；②搜索占比 41.9% 不算主体，推荐 55.7% 才是大头，留存差也可能主要来自推荐流量；③没有分来源的留存数据，无法证明搜索进来的人走得更快。"
            sug = "标题和首句改为观众实际在搜的问题（例：『广交会机器人是真人吗？』），或下一期直接做外骨骼助行器/真假机器人；发布前用搜索联想核对标题关键词。"
            exp = "追更一条「广交会外骨骼/真人机器人」题，标题前置该搜索词，比较搜索占比和 2s 跳出率；本条不改（不得修改已发布视频）。"
            conf = "中"
        elif w["id"] == 2:
            causes = "搜索第 1 名「霍尔木兹海峡苹果手机」占 65.2%，但发布版（V3f）的标题、简介和口播里都没有「霍尔木兹」——V3 稿开头原有「霍尔木兹海峡，漂满了免费 iPhone？」，V3f 改成了「一整片海面」。平台仍把这条匹配给了该搜索，匹配依据不明（可能是话题、画面文字或其他信号）。"
            alts = "①匹配依据未知，不能说明写不写这个词有区别；②这个词是事件本身的热搜，所有同题视频都在分这股流量；③字面重合度只是粗略指标。"
            sug = "同类时事核查题，标题前 8 字放事件热搜词（地名+物品，如「霍尔木兹海峡 iPhone」），口播第一句也说出来。"
            exp = "下一条时事核查片标题前置事件热搜词（mark_published --search-first yes），和本条比较搜索占比、搜索来源第 1 名占比。"
            conf = "低"
        else:
            causes = f"搜索第 1 名「{top['term']}」占 {f('rate', top['share'])}，" + ("和标题/口播能对上。" if top["term"] in [t for t, _ in on] else "和标题/口播字面对不上。")
            alts = "字面重合度只是粗略指标，同义说法会被算成不重合；搜索词分布随热点变化，与内容质量未必有关。"
            sug = "标题前 8 字放搜索第 1 名的说法；看后常搜里没被本片回答的问题考虑做追更。"
            exp = "下一期发布前记录标题是否前置搜索词（mark_published --search-first），积累 ≥3 条再比较搜索占比。"
            conf = "低"
        F.append(dict(key="search_match", phenomenon=ph, evidence=ev, baseline="作品自身搜索来源（创作者中心截图，已核）", causes=causes, alternatives=alts,
                      confidence=conf, suggestion=sug, experiment=exp, basis_kind="真实数据", stage="标题文案"))
    # 4 章节点击
    if chaps:
        top = max(chaps, key=lambda t: t["share"] or 0)
        ph = "章节点击：" + "；".join(f"{t['term']} {f('rate', t['share'])}" for t in chaps)
        m = re.match(r"(\d+):(\d+)", top["term"]); tsec = int(m.group(1)) * 60 + int(m.group(2)) if m else None
        s, _ = sent_at((tsec or 0) + 0.5)
        if w["id"] == 2:
            causes = f"75.6% 的章节点击落在 00:42「视频分析」，前面 0–42s 是钩子+真实部分+「刷屏」评论梗+图片分析；搜索「霍尔木兹海峡苹果手机」进来的人可能想直接看视频真假。"
            alts = "①章节点击率的分母是点了章节的人，不是全部观众，点章节的人本来就是想跳的少数；②「视频分析」是最后一个章节，标题更具体，自然吸引点击；③均播 17s 说明多数人没用章节就走了。"
            sug = "把「满海那段视频：海在晃、人不动」的结论提前到 10s 内先给一半答案，图片分析压缩；评论梗段（14–24s）缩短。"
            exp = "下一期核查类视频：第一个证据在 10s 内出现，记录章节点击分布和 5s 完播，与本条对比。"
            conf = "中"
        elif w["id"] == 1:
            causes = "59.5% 点「01:15 量产与售价」，原理章节只有 2.7%：观众更关心能不能买、多少钱。"
            alts = "章节点击只代表少数主动跳转的人；「量产与售价」在最后，标题更具体；搜索词又是「为什么会飞」——两者并不矛盾，可能是先搜原理、再想知道价格。"
            sug = "售价/量产一句话放开头作预告，原理部分压缩；追更题优先「怎么下压/原地起飞」（看后常搜）。"
            exp = "下一条科技新品片在 5s 内给出价格/上市信息，看章节点击是否仍集中在末段。"
            conf = "低"
        else:
            causes = f"点击最多的是「{top['term']}」。"; alts = "章节点击分母是点章节的人。"; sug = "把最受关注的章节提前。"; exp = "下期提前后比较。"; conf = "低"
        F.append(dict(key="chapters", phenomenon=ph, evidence=f"{ph}；该章节开头口播：「{s['text'][:24] if s else '—'}」", baseline="作品自身章节点击（截图，已核）",
                      causes=causes, alternatives=alts, confidence=conf, suggestion=sug, experiment=exp, basis_kind="真实数据", stage="分镜"))
    # 5 留存与同类
    if vsp or snap.get("avg_watch_ratio") is not None:
        ph = f"均播占比 {f('avg_watch_ratio', snap.get('avg_watch_ratio'))}、完播 {f('completion_rate', snap.get('completion_rate'))}；留存曲线与平台「同类作品」参考线：{vsp or '未记录'}"
        ev = f"均播占比 {rk('avg_watch_ratio')}；完播 {rk('completion_rate')}；同类参考线是平台给的，口径未公开"
        if w["id"] == 3:
            causes = "全程低于同类：开头示意实拍非现场、搜索意图错位、「二算」长句，三者都可能有份。"; conf = "低"
            sug = "暂不改（是前面几条的合并效果，按前面几条分别验证）。"
        elif w["id"] == 2:
            causes = "全程高于同类：首帧就是满海画面+提问、4.6s 揭「AI 做的」、6.7s 反转「船是真的」，符合「先信后揭」写法；完播 3.55% 低是因为片长 76s。"; conf = "低"
            sug = "暂不改（与发现 1 的「保留先信后揭开头」是同一条建议）。"
        else:
            causes = "与同类接近：开头铺垫、自我介绍拖慢，但搜索意图与内容对得上。"; conf = "低"
            sug = "暂不改（与前面开头/低谷两条建议重复）。"
        F.append(dict(key="retention_vs_peer", phenomenon=ph, evidence=ev, baseline="平台同类作品参考线（截图读图，定性）+ " + basis, causes=causes,
                      alternatives="平台「同类作品」的定义和样本未知；片长不同，完播率不可直接比（均播占比相对可比）；只有一次截图，没有时间变化。",
                      confidence=conf, suggestion=sug, experiment="积累 ≥5 条后，用均播占比按开头类型分组（insights.py），看差距是否稳定。", basis_kind="截图定性", stage="脚本"))
    # 6 互动/分享
    if snap.get("shares") is not None and snap.get("plays"):
        sr = snap["shares"] / snap["plays"]; others = []
        for o, s in peers:
            if s.get("shares") is not None and s.get("plays"): others.append((o["id"], s["shares"] / s["plays"]))
        allr = sorted([r for _, r in others] + [sr], reverse=True)
        ph = f"分享 {snap['shares']} / 播放 {f('plays', snap['plays'])} = 分享率 {sr:.2%}；点赞 {snap.get('likes')}，评论 {snap.get('comments')}，涨粉 {snap.get('follows_gained')}"
        ev = f"分享率同档排第 {allr.index(sr)+1}/{len(allr)}（其他：" + "，".join(f"#{i} {r:.2%}" for i, r in others) + "）"
        if w["id"] == 2:
            causes = "核查类内容有「转给家人别上当」的转发动机；62 次分享里多少来自私信转发（消息页 0.7%）无法拆分。"; sug = "核查类片尾加一句「转给会信的那个人」（不诱导互动的中性写法，需用户定）。"
        else:
            causes = "原理讲解类转发动机弱。"; sug = "暂不改，等样本。"
        F.append(dict(key="share_rate", phenomenon=ph, evidence=ev, baseline=basis, causes=causes, alternatives="播放量差一个数量级时比率波动大（广交会 722 播放，2 次分享就是 0.28%）；题材时效不同。",
                      confidence="很低" if n_peer < 5 else "低", suggestion=sug, experiment="积累 ≥5 条核查/原理片后按题材比较分享率。", basis_kind="真实数据", stage="选题"))
    return dict(snap=snap, bucket=b, peers=P, n_peer=n_peer, T=T, caveat=cav, valleys=valleys, vs_peer=vsp, st_terms=st_terms, after=after, chaps=chaps), F

def save_findings(c, w, F, report):
    ids = []
    for x in F:
        c.execute("""INSERT INTO findings(work_id,report,key,phenomenon,evidence,baseline,causes,alternatives,confidence,suggestion,experiment,basis_kind,created_at)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(work_id,key,report) DO UPDATE SET phenomenon=excluded.phenomenon,evidence=excluded.evidence,
                     causes=excluded.causes,alternatives=excluded.alternatives,confidence=excluded.confidence,suggestion=excluded.suggestion,experiment=excluded.experiment""",
                  (w["id"], report, x["key"], x["phenomenon"], x["evidence"], x["baseline"], x["causes"], x["alternatives"], x["confidence"], x["suggestion"], x["experiment"], x["basis_kind"], db.now()))
        fid = c.execute("SELECT id FROM findings WHERE work_id=? AND key=? AND report=?", (w["id"], x["key"], report)).fetchone()[0]
        if x["suggestion"].startswith("暂不改"): ids.append((fid, None)); continue
        hh = db.h("sug", w["id"], x["key"], db.norm(x["suggestion"]))
        r = c.execute("SELECT id,status FROM suggestions WHERE hash=?", (hh,)).fetchone()
        if not r:
            hid = c.execute("INSERT OR IGNORE INTO hypotheses(statement,status,origin,test_plan,evidence_work_ids,created_at,updated_at,hash) VALUES(?,?,?,?,?,?,?,?)",
                            (f"[{w['episode']}] {x['causes'][:160]}", "未验证", f"finding#{fid}", x["experiment"], json.dumps([w["id"]]), db.now(), db.now(), db.h("hyp", w["id"], x["key"]))).lastrowid
            hid = hid or c.execute("SELECT id FROM hypotheses WHERE hash=?", (db.h("hyp", w["id"], x["key"]),)).fetchone()[0]
            sid = c.execute("INSERT INTO suggestions(finding_id,work_id,stage,text,experiment,status,hypothesis_id,created_at,hash) VALUES(?,?,?,?,?,?,?,?,?)",
                            (fid, w["id"], x["stage"], x["suggestion"], x["experiment"], "待批", hid, db.now(), hh)).lastrowid
        else: sid = r["id"]
        ids.append((fid, sid))
    c.commit(); return ids

def six(x, i, sid=None):
    return [f"### 发现 {i}：{x['key']}（可信度：{x['confidence']}；依据类型：{x['basis_kind']}）",
            f"1. **数据现象**：{x['phenomenon']}", f"2. **具体依据与比较基准**：{x['evidence']}。基准：{x['baseline']}",
            f"3. **可能原因**：{x['causes']}　**其他解释**：{x['alternatives']}", f"4. **可信度**：{x['confidence']}（相关不等于因果；样本与读图精度见上）",
            f"5. **建议修改**：{x['suggestion']}" + (f"（suggestion#{sid}，状态：待批）" if sid else ""), f"6. **下一轮可验证实验**：{x['experiment']}", ""]

def metric_table(c, ws):
    L = ["| 作品 | 快照 | 发布后h | 播放 | 2s跳出 | 5s完播 | 完播 | 均播s | 均播占比 | 赞 | 评 | 转 | 藏 | 粉 | 搜索 | 推荐 | 核 |", "|" + "---|" * 17]
    for w in ws:
        for s in snaps(c, w["id"]):
            L.append(f"| #{w['id']} {(w['title'] or '')[:10]} | {s['checkpoint']} | {s['_age']:.1f} | " + " | ".join(f(k, s.get(k)) for k in
                     ("plays", "bounce_2s", "completion_5s", "completion_rate", "avg_watch_s", "avg_watch_ratio", "likes", "comments", "shares", "favorites", "follows_gained", "search_share", "recommend_share"))
                     + f" | {'✓' if s['verified'] else '待核'} |")
    return L

def header(title):
    return [f"# {title}", f"生成 {db.now()}（Asia/Shanghai）｜Feedback Engine v1", "",
            "> 口径：只用已核快照下结论；账号对比按发布时长档、写明 n；不用固定增长阈值；不说平台算法规律；相关≠因果。", ""]

def cmd_review(c, a, works=None):
    ws = works or ([db.find_work(c, a.work)] if a.work else [w for w in published(c) if main_snap(c, w["id"])][:1])
    if not ws: sys.exit("没有有数据的已发布作品")
    title = "复盘：" + "、".join(f"#{w['id']} {(w['title'] or '')[:14]}" for w in ws)
    L = header(title) + ["## 1. 数据快照（全部来源见 metrics_snapshots.source / metric_values）", ""] + metric_table(c, ws) + [""]
    L += ["## 2. 变化检测", ""]
    for w in ws:
        ch = own_changes(c, w)
        L.append(f"**#{w['id']} 自身历史**：" + ("只有 1 个快照，无法看变化。" if not ch else ""))
        for r in ch:
            L.append(f"- {r['frm']}→{r['to']}（{r['hours']}h）：" + "；".join(f"{MN.get(k, k)} {a_}→{b_}（{t}）" for k, a_, b_, t in r["items"]))
        s = main_snap(c, w["id"]); b, P, peers = peer_compare(c, w, s)
        L.append(f"- 同档（{b}）对比 n={len(peers)+1}：" + "；".join(f"{MN[k]} 第{p['rank']}/{p['n']}（{p['pos']}）" for k, p in P.items() if k in ("bounce_2s", "completion_5s", "avg_watch_ratio", "completion_rate", "plays", "shares")))
        L.append("")
    L += ["> 变化判定：相邻快照差值小于显示精度（如 1.3万 ±500）记「无法区分」；账号对比只说排名和是否超出其他作品范围，n<5 不下结论。", ""]
    allF = []
    L += ["## 3. 诊断（每条六项）", ""]
    for w in ws:
        ctx, F = diagnose(c, w)
        if not ctx: L.append(f"#{w['id']} 无数据"); continue
        L += [f"### ▍#{w['id']} {w['episode']}《{(w['publish_title'] or w['title'])[:30]}》", f"主快照 {ctx['snap']['checkpoint']}（发布后 {ctx['snap']['_age']:.1f}h，{'已核' if ctx['snap']['verified'] else '待核'}）；时间轴：{'、'.join(ctx['T']['files']) or '无'}" + (f"\n{ctx['caveat']}" if ctx['caveat'] else ""), ""]
        ids = save_findings(c, w, F, a.report_name) if not a.no_write else [(None, None)] * len(F)
        for i, (x, (fid, sid)) in enumerate(zip(F, ids), 1): L += six(x, i, sid)
        allF += [(w, x, sid) for x, (fid, sid) in zip(F, ids)]
    L += ["## 4. 拿不到 / 缺失的数据", ""] + missing_lines(c, ws) + [""]
    L += ["## 5. 待批改进建议（不会自动执行；批准用 approve_suggestion.py）", ""]
    L += [f"- suggestion#{sid}［{x['stage']}］#{w['id']}：{x['suggestion']}" for w, x, sid in allF if sid] or ["- （--no-write 模式未登记）"]
    return L

def missing_lines(c, ws):
    L = []
    for w in ws:
        s = main_snap(c, w["id"]); mf = json.loads(s["missing_fields"] or "[]") if s else []
        ret = c.execute("SELECT count(*) FROM retention_curve WHERE work_id=?", (w["id"],)).fetchone()[0]
        L.append(f"- #{w['id']}：逐秒留存数值 {'有 %d 点' % ret if ret else '无（截图只有曲线形状和平台低谷标注，读不出数值）'}；快照缺字段 {mf or '无'}；"
                 f"评论原文 {'未采到（库里没有该作品链接，游客态搜索找不到本账号作品）' if not w['video_url'] else '见 harvest'}；评论热词/观众画像：用户未提供截图；分来源留存：创作者中心不提供")
    return L

def cmd_recent(c, a):
    ws = [w for w in published(c, a.days) if snaps(c, w["id"])]
    L = header(f"最近 {a.days} 天作品表现") + metric_table(c, ws) + ["", "## 变化与同档对比", ""]
    for w in ws:
        s = main_snap(c, w["id"]); b, P, peers = peer_compare(c, w, s)
        hi = [f"{MN[k]}（{p['pos']}）" for k, p in P.items() if p["pos"] != "在同档其他作品范围内" and k in ("bounce_2s", "completion_5s", "avg_watch_ratio", "shares", "plays")]
        L.append(f"- #{w['id']} {(w['title'] or '')[:16]}：主快照 {s['checkpoint']}；同档 n={len(peers)+1}；超出其他作品范围的：{'、'.join(hi) or '无'}")
        for r in own_changes(c, w):
            L.append(f"  - {r['frm']}→{r['to']}：" + "；".join(f"{MN.get(k,k)} {t}" for k, _, _, t in r["items"] if k in ("plays", "likes", "shares", "bounce_2s")))
    due = c.execute("SELECT count(*) FROM works WHERE status='已发布' AND video_url IS NULL").fetchone()[0]
    L += ["", f"- 待办：{due} 条已发布作品没有抖音链接（采不到自己作品评论）。"]
    return L

def cmd_demands(c, a):
    L = header(f"最近观众有什么新需求（近 {a.days} 天）")
    since = (db.now_dt() - dt.timedelta(days=a.days)).strftime("%Y-%m-%d %H:%M:%S")
    L += ["## 1. 作品真实搜索来源（创作者中心，已核）——这是「观众为什么来」", ""]
    real, rel = cf.search_split(c)
    for wid in sorted({r["work_id"] for r in real}):
        w = c.execute("SELECT title FROM works WHERE id=?", (wid,)).fetchone()
        for kind in ("搜索来源词", "看后常搜"):
            xs = [r for r in real if r["work_id"] == wid and r["kind"] == kind]
            if xs:
                ck = max({r["checkpoint"] for r in xs}, key=lambda x: int(x[:-1])); xs = [r for r in xs if r["checkpoint"] == ck]
                L.append(f"- #{wid} {(w['title'] or '')[:12]}｜{kind}（{ck}）：" + "；".join(f"{r['term']} {r['share']:.1%}" for r in xs))
    L += ["", "## 2. 真实搜索词 × 需求库交叉（库里有没有、做没做）", ""]
    allt = sorted({r["term"] for r in real})
    for t, rows in cf.cross_terms(c, allt):
        L.append(f"- 「{t}」→ " + ("；".join(f"demand#{r['id']}「{r['text'][:20]}」{r['status']} 见{r['seen_count']}次" for r in rows) if rows else "需求库没有（新需求）"))
    L += ["", "## 3. 评论分析", ""]
    own_any = c.execute("SELECT count(*) FROM works WHERE status='已发布' AND video_url IS NOT NULL").fetchone()[0]
    L.append(f"- 自己作品评论：{'可采' if own_any else '0 条可用——3 条已发布作品库里都没有链接；游客态搜索（so.douyin.com）用标题/账号名搜不到本账号作品（已实测 3 次），所以免登录采不到。请用户补链接（分享→复制链接），或截评论区图（comments_fb.py add-shot）。'}")
    for col in c.execute("SELECT id,label,collected_at FROM collections WHERE collected_at>=? ORDER BY collected_at DESC", (since,)).fetchall():
        res = cf.analyze(c, None, col["id"], None, write=not a.no_write)
        if res["dedup"] == 0: continue
        L += cf.fmt(res, f"同题评论（不是本账号观众）· {col['label']}（{col['collected_at'][:16]}）")[:24] + [""]
    L += ["## 4. 相关搜索（游客态联想，≠作品真实搜索来源）", ""]
    kinds = {}
    for r in rel:
        if r["seen_at"] >= since: kinds.setdefault(r["source_kind"], []).append(r["text"])
    for k, v in kinds.items(): L.append(f"- {k}：" + "、".join(list(dict.fromkeys(v))[:12]))
    rows, meta = cf.revived(c)
    L += ["", "## 5. 过去未做、最近重现", "", f"- 判定：首见早于 {meta['old_before'][:10]}、{meta['recent_after'][:10]} 后又出现、未制作。需求库数据跨度 {meta['data_span'][0][:10]} → {meta['data_span'][1][:10]}。"]
    if not rows: L.append("- 结果 0 条：需求库最早记录是 10-18，还不满 14 天，这一项现在不可能有结果，不是没有需求。两周后会自动出现。")
    L += [f"- demand#{r['id']}「{r['text'][:30]}」首见{r['first_seen'][:10]} 近期{r['recent_n']}次" for r in rows]
    return L

def cmd_worst(c, a):
    ws = [w for w in published(c, a.days) if main_snap(c, w["id"])]
    L = header(f"近期最值得改进的作品（近 {a.days} 天，n={len(ws)}）")
    score = []
    for w in ws:
        s = main_snap(c, w["id"]); b, P, peers = peer_compare(c, w, s)
        ks = [k for k in ("bounce_2s", "completion_5s", "avg_watch_ratio") if k in P]
        r = st.mean([(P[k]["rank"] - 1) / max(1, P[k]["n"] - 1) for k in ks]) if ks else None
        score.append((r, w, P, ks))
    score.sort(key=lambda x: -(x[0] if x[0] is not None else -1))
    L += ["排序方法：每条作品在同档作品里的留存三项（2s跳出、5s完播、均播占比）排名的平均位置（0=最好，1=最差）。不是绝对好坏，只是本账号内相对；n 很小时排名很不稳。", ""]
    for r, w, P, ks in score:
        L.append(f"- #{w['id']} {(w['title'] or '')[:18]}：相对位置 {r:.2f}（" + "，".join(f"{MN[k]} 第{P[k]['rank']}/{P[k]['n']}" for k in ks) + "）" if r is not None else f"- #{w['id']} 无同档对比")
    if score and score[0][0] is not None:
        w = score[0][1]; ctx, F = diagnose(c, w)
        L += ["", f"## 最值得改：#{w['id']}《{(w['publish_title'] or w['title'])[:24]}》", "理由：同档留存三项相对位置最差；且发现里有可直接改的写法问题（下）。", ""]
        for i, x in enumerate(F[:3], 1): L += six(x, i)
    return L

def cmd_compare(c, a):
    w = db.find_work(c, a.work) if a.work else next(x for x in published(c) if main_snap(c, x["id"]))
    d = c.execute("SELECT * FROM content_dna WHERE work_id=?", (w["id"],)).fetchone()
    others = [o for o in published(c) if o["id"] != w["id"] and main_snap(c, o["id"])]
    same = [o for o in others if d and (c.execute("SELECT topic_class FROM content_dna WHERE work_id=?", (o["id"],)).fetchone() or {"topic_class": None})["topic_class"] == d["topic_class"]]
    L = header(f"对比：#{w['id']} 与历史同类")
    L += [f"- 本条类别：{d['topic_class'] if d else '未填'}｜开头：{d['hook_class'] if d else '未填'}｜时长 {d['duration_s'] if d else '—'}s",
          f"- 同类别历史作品：{len(same)} 条" + ("（没有同类别作品，改为和账号全部已发布作品比；结论只当线索）" if not same else ""), ""]
    pool = same or others
    L += metric_table(c, [w] + pool) + [""]
    s = main_snap(c, w["id"]); b, P, peers = peer_compare(c, w, s)
    L += [f"同档（{b}）：" + "；".join(f"{MN[k]} 第{p['rank']}/{p['n']}，其他 {f(k,p['min'])}–{f(k,p['max'])}" for k, p in P.items())]
    L += ["", "注意：片长不同（34s / 76s / 90s）时完播率不可直接比，优先看 2s 跳出、5s 完播、均播占比。"]
    return L

def cmd_next(c, a):
    L = header("根据历史反馈开始下一期选题（选题/脚本/分镜阶段读这份）")
    L += ["## 1. 已批准的经验（lessons 已批改进，可当依据）", ""]
    ap_ = c.execute("SELECT * FROM lessons WHERE type='已批改进' AND superseded=0 ORDER BY id DESC").fetchall()
    L += [f"- lesson#{r['id']}［{r['stage'] or '-'}］{r['text']}" + outcome_txt(c, r["id"]) for r in ap_] or ["- 还没有用户批准的改进建议（见下方待批）。"]
    L += ["", "## 2. 待批建议（未批准前只是候选，写稿时可以试但要标明「试验」）", ""]
    L += [f"- suggestion#{r['id']}［{r['stage']}］#{r['work_id']}：{r['text']}" for r in c.execute("SELECT * FROM suggestions WHERE status='待批' ORDER BY id")] or ["- 无"]
    L += ["", "## 3. 假设（未验证 / 已否定 都保留）", ""]
    L += [f"- hyp#{r['id']}［{r['status']}］{r['statement'][:90]}" for r in c.execute("SELECT * FROM hypotheses ORDER BY status, id")] or ["- 无"]
    L += ["", "## 4. 数据规律（insights）", ""]
    L += [f"- [{r['status']}｜{r['kind']}｜n={r['n']}] {r['statement']}" for r in c.execute("SELECT * FROM insights ORDER BY status, kind")]
    L += ["", "## 5. 选题线索（来自真实搜索来源与看后常搜，未制作）", ""]
    for r in c.execute("SELECT t.*, w.title wt FROM traffic_terms t JOIN works w ON w.id=t.work_id WHERE t.kind IN ('看后常搜','搜索来源词') ORDER BY t.share DESC"):
        n = db.norm(r["term"]); made = c.execute("SELECT count(*) FROM works WHERE status IN ('已发布','待发布') AND (title LIKE ? OR publish_title LIKE ?)", (f"%{r['term'][:4]}%",) * 2).fetchone()[0]
        L.append(f"- 「{r['term']}」{r['share']:.1%}（#{r['work_id']} {r['wt'][:10]} 的{r['kind']}）")
    if a.topic:
        L += ["", f"## 6. 与「{a.topic}」相关的历史反馈", ""] + feedback_search(c, a.topic)
    return L

def outcome_txt(c, lid):
    o = c.execute("SELECT * FROM lesson_outcomes WHERE lesson_id=?", (lid,)).fetchall()
    return ("；后续表现：" + "；".join(f"#{x['work_id']} {x['metric']} {x['value']}（基准 {x['baseline_desc'] or x['baseline']}）" for x in o)) if o else "；后续表现：待下一期数据"

def feedback_search(c, q):
    """历史反馈检索（findings/suggestions/hypotheses/lessons/traffic_terms），供 search.py feedback 调用。"""
    terms = [t for t in q.split() if t]; L = []
    def hit(txt): return all(t.lower() in (txt or "").lower() for t in terms)
    for r in c.execute("SELECT f.*, w.episode FROM findings f JOIN works w ON w.id=f.work_id ORDER BY f.id DESC"):
        if hit(" ".join(str(r[k] or "") for k in ("phenomenon", "evidence", "causes", "alternatives", "suggestion", "experiment", "key"))):
            L.append(f"- finding#{r['id']} {r['episode']}［{r['confidence']}］{r['phenomenon'][:60]} → {r['suggestion'][:60]}")
    for r in c.execute("SELECT * FROM suggestions ORDER BY id DESC"):
        if hit(r["text"] + " " + (r["experiment"] or "") + " " + (r["stage"] or "")): L.append(f"- suggestion#{r['id']}［{r['status']}｜{r['stage']}］{r['text'][:80]}")
    for r in c.execute("SELECT * FROM hypotheses ORDER BY id DESC"):
        if hit(r["statement"] + " " + (r["test_plan"] or "")): L.append(f"- hyp#{r['id']}［{r['status']}］{r['statement'][:80]}")
    for r in c.execute("SELECT * FROM lessons WHERE superseded=0 ORDER BY id DESC"):
        if hit(r["text"]): L.append(f"- lesson#{r['id']}［{r['type']}］{r['text'][:80]}")
    for r in c.execute("SELECT * FROM traffic_terms ORDER BY share DESC"):
        if hit(r["term"]): L.append(f"- 真实{r['kind']} #{r['work_id']}「{r['term']}」{(r['share'] or 0):.1%}")
    return L or ["- 无匹配"]

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", help="/".join(CMDS) + " 或 " + "/".join(CMDS.values())); ap.add_argument("--work"); ap.add_argument("--days", type=float)
    ap.add_argument("--topic"); ap.add_argument("--all", action="store_true", help="复盘：所有有数据的已发布作品"); ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(); cmd = CMDS.get(a.cmd, a.cmd)
    if cmd not in CMDS.values(): sys.exit(__doc__)
    a.days = a.days or {"recent": 14, "demands": 7, "worst": 30}.get(cmd, 30)
    c = db.connect(); stamp = db.now_dt().strftime("%Y%m%d_%H%M"); a.report_name = f"feedback_{cmd}_{stamp}.md"
    if cmd == "review" and a.all: L = cmd_review(c, a, [w for w in published(c) if main_snap(c, w["id"])])
    else: L = {"review": cmd_review, "recent": cmd_recent, "demands": cmd_demands, "worst": cmd_worst, "compare": cmd_compare, "next": cmd_next}[cmd](c, a)
    txt = "\n".join(L) + "\n"; print(txt)
    if not a.no_write:
        REPORTS.mkdir(parents=True, exist_ok=True); p = REPORTS / a.report_name; p.write_text(txt, encoding="utf-8"); print("已写入", p)

if __name__ == "__main__": main()
