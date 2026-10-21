#!/usr/bin/env python3
"""state.py latest | show EP | stage EP <阶段键> <状态> [下一步] | set EP <点路径> <JSON或字符串> | log EP "<文字>" | approve EP "<决策>"
例：state.py stage EP-20261021-01 C_script done "D 自动分镜"；state.py set EP-20261021-01 script.latest script/v2_edit.md"""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import stateutil as su
P = su.ROOT/"projects"; c = sys.argv[1] if len(sys.argv) > 1 else "latest"
if c == "latest":
    eps = sorted(P.glob("EP-*/state.json"), key=lambda p: json.loads(p.read_text())["updated_at"])
    if not eps: print("还没有 EP 项目；旧项目见 projects/LEGACY.md"); sys.exit()
    s = json.loads(eps[-1].read_text()); print(eps[-1].parent, s["stage"], s["stage_status"], "→", s["next_action"]); sys.exit()
ep = P/sys.argv[2]; s = su.load(ep)
if c == "show": print((ep/"STATE.md").read_text()); sys.exit()
if c == "stage":
    k, st = sys.argv[3], sys.argv[4]; s["stages"][k] = st; s["stage"] = k; s["stage_status"] = st
    if st == "done":
        s["completed"].append(f"{su.now()} {su.STAGE_CN[k]} 完成"); ks = list(s["stages"]); i = ks.index(k)
        if i + 1 < len(ks): s["stage"] = ks[i+1]; s["stage_status"] = s["stages"][ks[i+1]] = "in_progress"
    if len(sys.argv) > 5: s["next_action"] = sys.argv[5]
elif c == "set":
    path, v = sys.argv[3].split("."), sys.argv[4]
    try: v = json.loads(v)
    except Exception: pass
    d = s
    for x in path[:-1]: d = d.setdefault(x, {})
    d[path[-1]] = v
elif c == "approve": s["approved_decisions"].append({"at": su.now(), "what": sys.argv[3]})
elif c != "log": sys.exit("未知命令")
s["log"].append(f"{su.now()} {c} {' '.join(sys.argv[3:])}"); su.save(ep, s); print("ok", ep.name, s["stage"], s["stage_status"])
