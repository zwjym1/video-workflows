#!/usr/bin/env python3
"""Feedback Engine → Google Drive 备份（「AI科学内容资产中心」，文件夹 id 见 config/drive.json）。
脚本不能直接调 Drive：plan 生成文件 + 清单；Bot 用 UploadFile 上传；record 回写 id；verify 用 Drive 元数据（size、md5Checksum）回读校验。
  python3 scripts/fb_backup.py plan            → backup/feedback/<日期时间>/ 下 4 个文件 + manifest.json；sha256 已在同一文件夹「已校验」的自动标「跳过重复」
  python3 scripts/fb_backup.py record <本地路径> <drive_file_id>
  python3 scripts/fb_backup.py verify <本地路径> --size <Drive size> [--md5 <Drive md5Checksum>] [--readback <DownloadFile 回读的副本>]
      # Drive 元数据目前不返回 md5Checksum → 用 DownloadFile 回读副本算 md5；size 和 md5 都一致才「已校验」，否则「校验失败」（保留记录，重传）
  python3 scripts/fb_backup.py status
内容：①报告 reports/*.md → 07_创作经验与数据复盘；②原始快照（metrics_snapshots/metric_values/traffic_terms/retention_marks/hourly_plays/
screenshot_extractions/截图原图/OCR 原始输出）→ 01_原始数据；③项目关联（作品↔工程/时间轴/发布版/资产）→ 06_视频项目；④DB 快照（.backup API + integrity_check）→ 08_索引与数据库备份。"""
import sys, json, hashlib, zipfile, sqlite3, pathlib, argparse
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
CFG = json.loads((db.ROOT / "config" / "drive.json").read_text(encoding="utf-8")); FD = CFG["folders"]
DEST = {"reports": FD["07_创作经验与数据复盘"], "raw": FD["01_原始数据"], "links": FD["06_视频项目"], "db": FD["08_索引与数据库备份"]}
def md5(p):
    x = hashlib.md5()
    with open(p, "rb") as f:
        while b := f.read(1 << 20): x.update(b)
    return x.hexdigest()
def zdet(z, path, arc):   # 固定时间戳 → 内容不变时 zip 字节不变，sha256 去重才有效
    zi = zipfile.ZipInfo(arc, date_time=(2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(zi, pathlib.Path(path).read_bytes() if not isinstance(path, bytes) else path)

def rows(c, sql): return [dict(r) for r in c.execute(sql)]

def plan(a):
    c = db.connect(); stamp = db.now_dt().strftime("%Y%m%d_%H%M"); day = stamp[:8]
    out = db.ROOT / "backup" / "feedback" / stamp; out.mkdir(parents=True, exist_ok=True); items = []
    # ① 报告
    p = out / f"feedback_reports_{day}.zip"
    with zipfile.ZipFile(p, "w") as z:
        for f in sorted((db.ROOT / "reports").glob("*.md")): zdet(z, f, f"reports/{f.name}")
        for f in sorted((db.ROOT / "inbox" / "screenshots" / "_ocr").rglob("review_*.md")): zdet(z, f, f"ocr_review/{f.parent.name}_{f.name}")
    items.append(("reports", p))
    # ② 原始快照
    p = out / f"feedback_raw_{day}.zip"
    tabs = ["metrics_snapshots", "metric_values", "traffic_terms", "retention_marks", "retention_curve", "hourly_plays", "screenshot_extractions", "screenshot_files", "comment_labels", "comment_clusters"]
    with zipfile.ZipFile(p, "w") as z:
        for t in tabs: zdet(z, json.dumps(rows(c, f"SELECT * FROM {t} ORDER BY rowid"), ensure_ascii=False, indent=1).encode(), f"tables/{t}.json")
        for r in c.execute("SELECT path FROM screenshot_files ORDER BY path"):
            if pathlib.Path(r["path"]).exists(): zdet(z, r["path"], f"screenshots/{pathlib.Path(r['path']).name}")
        for f in sorted((db.ROOT / "inbox" / "screenshots" / "_ocr").rglob("*")):
            if f.is_file() and not f.name.startswith("review_"): zdet(z, f, f"ocr_raw/{f.relative_to(db.ROOT / 'inbox' / 'screenshots' / '_ocr')}")
    items.append(("raw", p))
    # ③ 项目关联
    links = []
    for w in c.execute("SELECT * FROM works WHERE status IN ('已发布','待发布') ORDER BY id"):
        links.append(dict(work_id=w["id"], episode=w["episode"], title=w["title"], publish_title=w["publish_title"], publish_time=w["publish_time"], video_url=w["video_url"],
                          project_dir=w["project_dir"], timeline_path=w["timeline_path"], final_video=w["final_video"], script=w["script"], storyboard=w["storyboard"],
                          dna=(dict(d) if (d := c.execute("SELECT * FROM content_dna WHERE work_id=?", (w["id"],)).fetchone()) else None),
                          assets=rows(c, f"SELECT a.id,a.name,a.kind,a.path,l.rel FROM links l JOIN anim_assets a ON a.id=l.from_id WHERE l.from_type='asset' AND l.to_type='work' AND l.to_id={w['id']}"),
                          bgm=rows(c, f"SELECT b.id,b.title,l.rel FROM links l JOIN bgm b ON b.id=l.from_id WHERE l.from_type='bgm' AND l.to_type='work' AND l.to_id={w['id']}"),
                          findings=rows(c, f"SELECT id,key,confidence,report FROM findings WHERE work_id={w['id']}"),
                          suggestions=rows(c, f"SELECT id,stage,status,text FROM suggestions WHERE work_id={w['id']}")))
    p = out / f"feedback_links_{day}.json"; p.write_text(json.dumps(links, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8"); items.append(("links", p))
    # ④ DB 快照
    p = out / f"studio_{stamp}.db"; d = sqlite3.connect(p); c.backup(d); d.close()
    chk = sqlite3.connect(p).execute("PRAGMA integrity_check").fetchone()[0]
    if chk != "ok": sys.exit(f"DB 快照 integrity_check 失败：{chk}")
    items.append(("db", p))
    man = []
    for kind, p in items:
        sh = db.sha256_file(p); fid = DEST[kind]
        dup = c.execute("SELECT * FROM backups WHERE sha256=? AND drive_folder_id=? AND status='已校验'", (sh, fid)).fetchone()
        st_ = "跳过重复" if dup else "待传"
        if dup: man.append(dict(kind=kind, path=str(p), name=p.name, folder_id=fid, sha256=sh, size=p.stat().st_size, md5=md5(p), status=st_, drive_file_id=dup["drive_file_id"], same_as=dup["local_path"])); p.unlink(); continue
        c.execute("""INSERT INTO backups(local_path,kind,sha256,size,drive_folder_id,drive_name,local_md5,status,planned_at,note) VALUES(?,?,?,?,?,?,?,?,?,?)
                     ON CONFLICT(sha256,drive_folder_id) DO UPDATE SET note=COALESCE(note,'')||' 再次计划 '||excluded.planned_at""",
                  (str(p), kind, sh, p.stat().st_size, fid, p.name, md5(p), st_, db.now(), f"与 backup#{dup['id']} 相同" if dup else None))
        man.append(dict(kind=kind, path=str(p), name=p.name, folder_id=fid, sha256=sh, size=p.stat().st_size, md5=md5(p), status=st_, drive_file_id=dup and dup["drive_file_id"]))
    c.commit(); (out / "manifest.json").write_text(json.dumps(dict(namespace=CFG["namespace"], items=man), ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(man, ensure_ascii=False, indent=1)); print(f"清单：{out/'manifest.json'}（DB 快照 integrity_check=ok）")

def record(a):
    c = db.connect(); r = c.execute("SELECT * FROM backups WHERE local_path=? ORDER BY id DESC", (str(pathlib.Path(a.path).resolve()),)).fetchone()
    if not r: sys.exit("清单里没有这个文件")
    c.execute("UPDATE backups SET drive_file_id=?, status='已传', uploaded_at=? WHERE id=?", (a.file_id, db.now(), r["id"])); c.commit(); print("ok")

def verify(a):
    c = db.connect(); r = c.execute("SELECT * FROM backups WHERE local_path=? ORDER BY id DESC", (str(pathlib.Path(a.path).resolve()),)).fetchone()
    if not r: sys.exit("清单里没有这个文件")
    if a.readback: a.md5 = md5(a.readback); rb = pathlib.Path(a.readback); assert rb.stat().st_size == a.size, "回读副本大小与 Drive 元数据不一致"
    if not a.md5: sys.exit("需要 --md5 或 --readback 才能做哈希校验")
    ok = (a.size == r["size"]) and (a.md5 == r["local_md5"])
    c.execute("UPDATE backups SET drive_size=?, drive_md5=?, status=?, verified_at=? WHERE id=?", (a.size, a.md5, "已校验" if ok else "校验失败", db.now(), r["id"]))
    c.execute("UPDATE files SET drive_file_id=?, drive_folder=?, drive_name=?, uploaded_at=? WHERE path=?", (r["drive_file_id"], r["drive_folder_id"], r["drive_name"], db.now(), r["local_path"])) if ok else None
    c.commit(); print("已校验 ✓" if ok else f"校验失败：本地 size={r['size']} md5={r['local_md5']} / Drive size={a.size} md5={a.md5}")

def status(a):
    c = db.connect()
    for r in c.execute("SELECT id,kind,status,size,drive_file_id,local_path FROM backups ORDER BY id"): print(tuple(r))

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); sp = ap.add_subparsers(dest="cmd", required=True)
sp.add_parser("plan"); p = sp.add_parser("record"); p.add_argument("path"); p.add_argument("file_id")
p = sp.add_parser("verify"); p.add_argument("path"); p.add_argument("--size", type=int, required=True); p.add_argument("--md5"); p.add_argument("--readback")
sp.add_parser("status")
a = ap.parse_args(); {"plan": plan, "record": record, "verify": verify, "status": status}[a.cmd](a)
