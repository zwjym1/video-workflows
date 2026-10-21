"""共用：读写 state.json、刷新 STATE.md、维护 projects/INDEX.md。"""
import json, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
TZ = datetime.timezone(datetime.timedelta(hours=8))
STAGE_CN = {"A_topic":"A 选题","B_creative":"B 创意","C_script":"C 逐字稿","D_storyboard":"D 分镜",
            "E_production":"E 制作","F_qc":"F 质检","G_review":"G 审片","H_delivery":"H 交付"}
def now(): return datetime.datetime.now(TZ).strftime("%Y-%m-%d %H:%M (UTC+8)")
def load(ep_dir): return json.loads((pathlib.Path(ep_dir)/"state.json").read_text(encoding="utf-8"))
def save(ep_dir, s):
    ep_dir = pathlib.Path(ep_dir); s["updated_at"] = now()
    (ep_dir/"state.json").write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    (ep_dir/"STATE.md").write_text(render_md(s), encoding="utf-8")
    update_index(ep_dir.parent)
def render_md(s):
    L = [f"# {s['id']} · {s.get('title') or '（未定题）'}", "",
         f"- 档位：{'精品' if s['tier']=='premium' else '日常'}　更新：{s['updated_at']}",
         f"- **当前阶段：{STAGE_CN.get(s['stage'], s['stage'])}（{s['stage_status']}）**",
         f"- **下一步：{s['next_action']}**", "", "## 阶段", ""]
    L += [f"- {STAGE_CN[k]}：{v}" for k, v in s["stages"].items()]
    def sec(t, items):
        L.extend(["", f"## {t}", ""]); L.extend([f"- {i}" for i in items] or ["- （无）"])
    sec("已批准决策", [f"{d.get('at','')} {d.get('what','')}" if isinstance(d, dict) else str(d) for d in s["approved_decisions"]])
    sec("已完成", s["completed"])
    sec("稿件与分镜", [f"逐字稿最新：{s['script']['latest']}（通过：{s['script']['approved']}；锁定段：{s['script']['locked_paragraphs']}）",
                     f"配音：{s['vo']['latest']}（{s['vo']['model']}；听审通过：{s['vo']['listen_approved']}）",
                     f"分镜最新：{s['storyboard']['latest']}"])
    sec("镜头状态", [f"{x.get('id')} {x.get('status')} {x.get('note','')}" for x in s["shots"]])
    sec("工程与输出", [f"{k}: {v}" for k, v in s["project_paths"].items()] + [str(r) for r in s["renders"]])
    sec("失败与恢复", [str(f) for f in s["failures"]])
    sec("未解决问题", [str(i) for i in s["open_issues"]])
    sec("日志（最近 15 条）", s["log"][-15:])
    return "\n".join(L) + "\n"
def update_index(projects_dir):
    projects_dir = pathlib.Path(projects_dir); rows = []
    for p in sorted(projects_dir.glob("EP-*/state.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        rows.append(f"| {s['id']} | {s.get('title') or ''} | {s['tier']} | {STAGE_CN.get(s['stage'])} | {s['updated_at']} | {s.get('adopted_from') or ''} |")
    legacy = (projects_dir/"LEGACY.md").read_text(encoding="utf-8") if (projects_dir/"LEGACY.md").exists() else ""
    (projects_dir/"INDEX.md").write_text("# 项目索引（脚本自动生成，勿手改；旧项目见 LEGACY.md）\n\n| 编号 | 标题 | 档位 | 阶段 | 更新 | 指向旧目录 |\n|---|---|---|---|---|---|\n"
        + "\n".join(rows) + "\n\n" + legacy, encoding="utf-8")
