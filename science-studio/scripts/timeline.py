"""作品时间轴：把留存曲线的秒数对到句子/字幕卡/镜头。自动在 project_dir 里找，或用 works.timeline_path。
支持：vo/cards.json（{cards:[{n,seg,text,start,end}]}）、*align*.json（{sentences:[{i,text,start,end}]}）、
footage-timeline.json（{shots:[{id,label,start,end}]}）、subs*.json（[{card,text,a,b}]）、state.json.shots（帧区间 note「帧 a–b」）。"""
import json, pathlib, re
CANDS = ["vo/cards.json", "voice/*/alignment*.json", "remotion/src/*/align.json", "**/alignment*.json", "vo/subs*.json"]
SHOTS = ["remotion/src/*/footage-timeline.json", "**/footage-timeline.json", "storyboard/shots.json"]

def _load_sent(p):
    d = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    if isinstance(d, dict) and isinstance(d.get("cards"), list):
        return [dict(start=x["start"], end=x["end"], text=x.get("text", ""), seg=x.get("seg"), id=f"卡{x.get('n')}") for x in d["cards"]]
    if isinstance(d, dict) and isinstance(d.get("sentences"), list):
        return [dict(start=x["start"], end=x["end"], text=x.get("text", ""), seg=None, id=f"句{x.get('i')}") for x in d["sentences"] if "start" in x]
    if isinstance(d, dict) and isinstance(d.get("timeline"), list):     # Remotion timeline.json（广交会）：每句一条，demo=镜头
        return [dict(start=x["start"], end=x["end"], text=x.get("text", ""), seg=x.get("demo"), id=f"句{x.get('i')}") for x in d["timeline"]]
    if isinstance(d, dict) and isinstance(d.get("subs"), list) and d["subs"] and "start" in d["subs"][0]:   # v3f.json（iPhone）：字幕卡
        return [dict(start=x["start"], end=x["end"], text=x.get("text", ""), seg=None, id=f"卡{x.get('sid')}") for x in d["subs"]]
    if isinstance(d, list) and d and "a" in d[0]:
        return [dict(start=x["a"], end=x["b"], text=x.get("text", ""), seg=None, id=f"卡{x.get('card')}") for x in d]
    return None

def _load_shots(p):
    d = json.loads(pathlib.Path(p).read_text(encoding="utf-8")); fps = d.get("fps", 30) if isinstance(d, dict) else 30
    sh = d.get("shots") if isinstance(d, dict) else d
    if isinstance(d, dict) and isinstance(d.get("timeline"), list):
        return [dict(start=float(x["start"]), end=float(x["end"]), id=x.get("demo"), text=f"{x.get('demo')}（{'实拍' if x.get('src')=='hook' else '2D 动画'}）") for x in d["timeline"]]
    out = []
    for x in sh or []:
        if "t0" in x and "t1" in x: out.append(dict(start=float(x["t0"]), end=float(x["t1"]), id=x.get("id"),
                                                     text=f"{x.get('id')} {(x.get('world') or {}).get('type','')} {pathlib.Path(str((x.get('world') or {}).get('src') or '')).name}".strip())); continue
        if "start" in x and "end" in x: out.append(dict(start=float(x["start"]), end=float(x["end"]), id=x.get("id"), text=x.get("label") or x.get("id")))
    return out or None

def load(project_dir, override=None, ep_dir=None):
    """→ dict(sentences=[...], shots=[...], files=[...])"""
    res = dict(sentences=[], shots=[], files=[])
    if override and pathlib.Path(override).exists():
        s = _load_sent(override) or []; res["sentences"] = s; res["files"].append(str(override))
        try: sh = _load_shots(override)
        except Exception: sh = None
        if sh: res["shots"] = sh
    pd = pathlib.Path(project_dir) if project_dir else None
    if pd and pd.exists() and not res["sentences"]:
        for g in CANDS:
            for p in sorted(pd.glob(g)):
                if "node_modules" in p.parts: continue
                try: s = _load_sent(p)
                except Exception: s = None
                if s: res["sentences"] = s; res["files"].append(str(p)); break
            if res["sentences"]: break
    if pd and pd.exists() and not res["shots"]:
        for g in SHOTS:
            for p in sorted(pd.glob(g)):
                if "node_modules" in p.parts: continue
                try: s = _load_shots(p)
                except Exception: s = None
                if s: res["shots"] = s; res["files"].append(str(p)); break
            if res["shots"]: break
    if not res["shots"] and ep_dir and (pathlib.Path(ep_dir) / "state.json").exists():
        st = json.loads((pathlib.Path(ep_dir) / "state.json").read_text(encoding="utf-8"))
        for x in st.get("shots", []):
            m = re.search(r"(\d+)\s*[–-]\s*(\d+)", x.get("note", ""))
            if m: res["shots"].append(dict(start=int(m.group(1))/30, end=(int(m.group(2))+1)/30, id=x["id"], text=x["id"]))
        if res["shots"]: res["files"].append(str(pathlib.Path(ep_dir) / "state.json") + "（shots 帧区间）")
    return res

def at(items, t):
    """t 秒处正在说/正在放的条目；落在间隙里取刚结束的那条。"""
    cur = None
    for x in items:
        if x["start"] <= t < x["end"]: return x
        if x["start"] <= t: cur = x
    return cur
