"""words.json + compose 字幕关键词 → src/data/subs.json（每条 ≤10 字，按词时间码）"""
import json, re
V2 = "/workspace/iphone-fake/v2"
W = json.load(open(f"{V2}/vo/words.json"))
SL = json.load(open("scripts/sublog.json"))
SHOT_OF = {s: [s] for s in [f"{i:02d}" for i in range(1, 31)]}; SHOT_OF["12"] = ["12a", "12b"]
MAXU = 10
PUNCT_BREAK = "，。？！：；、"
def units(s):
    u = 0
    for ch in s:
        if ch == " ": continue
        u += 0.5 if ord(ch) < 128 else 1
    return u

def keywords(sid):
    kw = {}
    for sh in SHOT_OF[sid]:
        for e in SL.get(sh, []):
            for k, v in e["keywords"].items():
                kw[k.replace(" ", "")] = v
    return kw

cues = []
for s in W["sentences"]:
    sid = s["id"]; text = s["text"]
    toks = [w for w in W["words"] if w["id"] == sid]
    # 字符流 → 时间：每个非空白非标点字符对应 token 的某个字符
    norm = [c for c in text if c not in PUNCT_BREAK and c != " " and c not in "@"]
    tchars = []
    for t in toks:
        for c in t["text"]:
            tchars.append((c, t["start"], t["end"]))
    # 对齐（容错：按顺序贪婪匹配，不同则前进）
    times = []; j = 0
    for c in norm:
        k = j
        while k < len(tchars) and tchars[k][0].lower() != c.lower(): k += 1
        if k < len(tchars): times.append((tchars[k][1], tchars[k][2])); j = k + 1
        else: times.append(times[-1] if times else (s["start"], s["end"]))
    # 分句：按标点切成小句，再按 ≤10 字切
    clauses, cur = [], ""
    for c in text:
        if c in PUNCT_BREAK:
            if cur.strip(): clauses.append((cur.strip(), c))
            cur = ""
        else: cur += c
    if cur.strip(): clauses.append((cur.strip(), ""))
    pieces = []
    for cl, p in clauses:
        keep = "？" if p == "？" else ""
        if units(cl) <= MAXU: pieces.append(cl + keep); continue
        # 先按空格/中英边界切，再合并到 ≤10
        toks2 = re.findall(r"[A-Za-z@0-9]+|[^\sA-Za-z@0-9]", cl)
        line = ""
        for t in toks2:
            cand = (line + (" " if line and (t[0].isascii() and t[0].isalnum() or line[-1].isascii() and line[-1].isalnum()) else "") + t)
            if units(cand) > MAXU and line:
                pieces.append(line); line = t
            else: line = cand
        if line: pieces.append(line + keep)
        # 尾巴太短（<3 字）→ 按 token 边界重新二等分
        if units(line) < 3 and len(pieces) >= 2:
            pieces.pop(); pieces.pop()
            tot = units(cl); best = None
            for cut in range(1, len(toks2)):
                l = ""; 
                for t in toks2[:cut]: l += ((" " if l and (t[0].isascii() and t[0].isalnum() or l[-1].isascii() and l[-1].isalnum()) else "") + t)
                r = ""
                for t in toks2[cut:]: r += ((" " if r and (t[0].isascii() and t[0].isalnum() or r[-1].isascii() and r[-1].isalnum()) else "") + t)
                if units(l) <= MAXU and units(r) <= MAXU:
                    sc = abs(units(l) - units(r))
                    if best is None or sc < best[0]: best = (sc, l, r)
            pieces += [best[1], best[2] + keep]
    # 防止只剩 1~2 字的尾巴：与前一条均分
    # 关键词着色：在句子字符流上打标
    kw = keywords(sid if sid != "12" else "12")
    flat = "".join(norm)
    color = [None] * len(flat)
    for k, v in kw.items():
        k2 = k.replace("@", "")
        for m in re.finditer(re.escape(k2), flat):
            for q in range(m.start(), m.end()): color[q] = v
    pos = 0
    for pc in pieces:
        segs = []
        n0 = pos
        for c in pc:
            if c in " ？@":
                segs.append([c, None if c != "@" else (color[pos] if pos < len(color) else None)]); continue
            col = color[pos] if pos < len(color) else None
            segs.append([c, col]); pos += 1
        # 合并同色
        merged = []
        for c, col in segs:
            if merged and merged[-1][1] == col: merged[-1][0] += c
            else: merged.append([c, col])
        t0 = times[n0][0] if n0 < len(times) else s["start"]
        t1 = times[pos - 1][1] if pos - 1 < len(times) else s["end"]
        cues.append({"sid": sid, "start": round(max(0, t0), 3), "end": round(t1, 3), "text": pc, "segs": merged})
# 结束时间：延到下一条开始（间隔<0.7s），否则 +0.3
for i, c in enumerate(cues):
    nxt = cues[i + 1]["start"] if i + 1 < len(cues) else W["total_sec"]
    c["end"] = round(nxt if nxt - c["end"] < 0.7 else c["end"] + 0.3, 3)
    c["start"] = round(max(0, c["start"] - 0.05), 3)
json.dump(cues, open("src/data/subs.json", "w"), ensure_ascii=False, indent=1)
for c in cues: print(c["sid"], c["start"], c["end"], units(c["text"]), c["text"], [s for s in c["segs"] if s[1]])
