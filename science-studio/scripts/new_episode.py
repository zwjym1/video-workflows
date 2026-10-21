#!/usr/bin/env python3
"""新建一期：python3 new_episode.py [--tier daily|premium] [--title 标题] [--adopt 旧目录] [--root 测试用根目录]
生成 projects/EP-YYYYMMDD-NN/{state.json,STATE.md,research/field,creative,script,storyboard,vo,assets,render,review,delivery}"""
import argparse, json, datetime, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import stateutil as su
a = argparse.ArgumentParser(); a.add_argument("--tier", default="daily", choices=["daily", "premium"])
a.add_argument("--title", default=""); a.add_argument("--adopt", default=None); a.add_argument("--root", default=str(su.ROOT))
o = a.parse_args(); root = pathlib.Path(o.root); proj = root/"projects"; proj.mkdir(parents=True, exist_ok=True)
day = datetime.datetime.now(su.TZ).strftime("%Y%m%d"); n = 1
while (proj/f"EP-{day}-{n:02d}").exists(): n += 1
ep = proj/f"EP-{day}-{n:02d}"
for d in ["research/field", "creative", "script", "storyboard", "vo", "assets", "render/pc_pack", "review", "delivery"]:
    (ep/d).mkdir(parents=True, exist_ok=True)
s = json.loads((su.ROOT/"state/template/state.json").read_text(encoding="utf-8"))
s.update(id=ep.name, title=o.title, tier=o.tier, created_at=su.now())
if o.adopt:
    s["adopted_from"] = o.adopt; s["project_paths"]["legacy_dir"] = o.adopt
    s["next_action"] = f"读旧目录 {o.adopt}，把已有稿/分镜/配音/镜头状态登记进 state（不搬文件）"
(ep/"assets/SOURCES.md").write_text("# 素材来源与 AI 标识\n\n| 素材 | 来源/生成方式 | 授权 | 片中标识 |\n|---|---|---|---|\n", encoding="utf-8")
(ep/"review/changes.md").write_text("# 修改记录（每次修订：意见→镜头→改了什么→新版本文件→旧版本位置）\n", encoding="utf-8")
s["log"].append(f"{su.now()} 建档（{o.tier}）")
su.save(ep, s); print(ep)
