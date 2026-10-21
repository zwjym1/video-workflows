#!/usr/bin/env python3
"""资产库备份到 Google Drive（「AI科学内容资产中心」）。
脚本本身不能调 Drive；它负责本地快照、哈希、去重、出上传清单；上传由 Bot 用 UploadFile 工具执行，再用 record 回写 Drive id。
  python3 scripts/backup.py plan [--with-works] [--dry-run]   # 1) 生成 db 快照(.backup API)+文本文档 zip，写 backup/<日期>/manifest.json
  → Bot 逐条 UploadFile(connection=<config/drive.json 的 namespace>, sourcePath=item.path, destination.folderId=item.folder_id, name=item.name)
  python3 scripts/backup.py record <本地路径> <drive_file_id>  # 2) 每传完一个回写 files 表（以后同 sha256 自动跳过）
  python3 scripts/backup.py verify <快照.db>                   # 校验快照 integrity_check + 行数
规则：DB 只在盒上读写，Drive 只存快照；中间渲染（预览/temp/silent/_splice 等）不传；按 sha256 去重；Drive 版本历史不可靠（30 天/100 版），所以快照按日期命名、不覆盖。"""
import sys, json, pathlib, argparse, sqlite3, zipfile, datetime, re
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
ROOT = db.ROOT; CFG = ROOT / "config" / "drive.json"
TEXT_DOCS = ["README.md", "config", "reviews", "assets/INDEX.md", "projects/INDEX.md", "projects/LEGACY.md", "skills", "env_report.md", "first_test_plan.md", "scripts"]
SKIP_RE = re.compile(r"预览|preview|_tmp|temp|silent|_splice|作废|draft|backup", re.I)

def cfg():
    d = json.load(open(CFG, encoding="utf-8"))
    if not d.get("status", "").startswith("ACTIVE") or not d.get("namespace"):
        return None, d
    return d, d

def snapshot(dst):
    src = sqlite3.connect(db.DB); out = sqlite3.connect(dst); src.backup(out); out.close(); src.close()
    return db.sha256_file(dst)

def cmd_plan(a):
    conf, raw = cfg()
    stamp = datetime.datetime.now(db.TZ).strftime("%Y%m%d_%H%M")
    base = (pathlib.Path("/tmp/studio_backup_dry") if a.dry_run else ROOT / "backup") / stamp; base.mkdir(parents=True, exist_ok=True)
    c = db.connect(); items = []
    snap = base / f"studio_{stamp}.db"; sh = snapshot(snap)
    items.append(dict(path=str(snap), folder="08_索引与数据库备份", name=snap.name, sha256=sh, kind="db_snapshot"))
    z = base / f"studio_docs_{stamp}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in TEXT_DOCS:
            p = ROOT / d
            for f in ([p] if p.is_file() else sorted(p.rglob("*")) if p.exists() else []):
                if f.is_file() and "__pycache__" not in f.parts: zf.write(f, f.relative_to(ROOT))
    items.append(dict(path=str(z), folder="08_索引与数据库备份", name=z.name, sha256=db.sha256_file(z), kind="docs_zip"))
    if a.with_works:
        for w in c.execute("SELECT * FROM works WHERE status='已发布'"):
            for k in ("final_video", "script", "storyboard", "cover", "publish_caption", "srt"):
                p = w[k]
                if not p or not pathlib.Path(p).is_file() or (k == "final_video" and SKIP_RE.search(pathlib.Path(p).name)): continue
                fid = db.register_file(c, p, k); r = c.execute("SELECT sha256 FROM files WHERE id=?", (fid,)).fetchone()
                items.append(dict(path=p, folder="06_视频项目", subfolder=w["episode"], name=f"{w['episode']}__{pathlib.Path(p).name}", sha256=r["sha256"], kind=k, work_id=w["id"]))
    c.commit()
    plan = []
    for it in items:   # 去重：同 sha256 已在 Drive 的跳过
        hit = c.execute("SELECT drive_file_id FROM files WHERE sha256=? AND drive_file_id IS NOT NULL", (it["sha256"],)).fetchone()
        it["skip"] = bool(hit); it["existing_drive_id"] = hit[0] if hit else None
        if conf: it["folder_id"] = (conf.get("episode_folders") or {}).get(it.get("subfolder")) or conf["folders"].get(it["folder"])
        if conf and it.get("subfolder") and it.get("subfolder") not in (conf.get("episode_folders") or {}): it["todo"] = "先在 06 下建子文件夹并写入 drive.json episode_folders"
        it["size"] = pathlib.Path(it["path"]).stat().st_size; plan.append(it)
    man = dict(created=db.now(), namespace=(conf or {}).get("namespace"), hold=None if conf else raw.get("status"), items=plan,
               total_bytes=sum(i["size"] for i in plan if not i["skip"]))
    (base / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: man[k] for k in ("namespace", "hold", "total_bytes")}, ensure_ascii=False))
    for i in plan: print(("SKIP " if i["skip"] else "UP   ") + f"{i['size']/1e6:8.2f}MB {i['folder']}/{i.get('subfolder','')} {i['name']}")
    print("manifest:", base / "manifest.json")

def cmd_record(a):
    c = db.connect(); conf, _ = cfg(); fid = db.register_file(c, a.path)
    c.execute("UPDATE files SET drive_file_id=?, drive_folder=?, drive_name=?, uploaded_at=? WHERE id=?",
              (a.drive_id, a.folder, pathlib.Path(a.path).name, db.now(), fid)); c.commit(); print("recorded", fid)

def cmd_verify(a):
    c = sqlite3.connect(a.snapshot); print("integrity:", c.execute("PRAGMA integrity_check").fetchone()[0])
    for t in ("demands", "topics", "bgm", "anim_assets", "works", "lessons", "links"): print(t, c.execute(f"SELECT count(*) FROM {t}").fetchone()[0])

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); sp = ap.add_subparsers(dest="cmd", required=True)
p = sp.add_parser("plan"); p.add_argument("--with-works", action="store_true"); p.add_argument("--dry-run", action="store_true")
p = sp.add_parser("record"); p.add_argument("path"); p.add_argument("drive_id"); p.add_argument("--folder")
p = sp.add_parser("verify"); p.add_argument("snapshot")
a = ap.parse_args(); {"plan": cmd_plan, "record": cmd_record, "verify": cmd_verify}[a.cmd](a)
