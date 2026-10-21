"""science-studio 资产库：SQLite 连接、建表、通用工具。
DB 只在盒上：/workspace/science-studio/db/studio.db（不要放进任何同步目录；Drive 只放 backup.py 生成的快照）。
中文全文检索：FTS5 trigram 分词（≥3 字走 MATCH，1–2 字词自动退化为 LIKE），无需 jieba。"""
import sqlite3, hashlib, json, re, os, datetime, pathlib, unicodedata
ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = pathlib.Path(os.environ.get("STUDIO_DB") or ROOT / "db" / "studio.db")
TZ = datetime.timezone(datetime.timedelta(hours=8))
def now(): return datetime.datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")

SCHEMA = r"""
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
-- 文件登记（任何库引用的文件都在这里，sha256 去重，记 Drive 副本）
CREATE TABLE IF NOT EXISTS files(
  id INTEGER PRIMARY KEY, path TEXT UNIQUE, sha256 TEXT, size INTEGER, mtime TEXT, kind TEXT,
  drive_file_id TEXT, drive_folder TEXT, drive_name TEXT, uploaded_at TEXT);
CREATE INDEX IF NOT EXISTS files_sha ON files(sha256);
-- 采集批次（一次 douyin-field-collect 运行/目录）
CREATE TABLE IF NOT EXISTS collections(
  id INTEGER PRIMARY KEY, source_path TEXT UNIQUE, label TEXT, topic_hint TEXT, collected_at TEXT, ingested_at TEXT, n_items INTEGER);
-- 1 观众需求库：去重后的「需求文本」；每次看到记一条 sighting
CREATE TABLE IF NOT EXISTS demands(
  id INTEGER PRIMARY KEY, text TEXT NOT NULL, norm TEXT NOT NULL, kind TEXT NOT NULL,   -- kind: question(评论疑问) | search(搜索词/推荐词)
  first_seen TEXT, last_seen TEXT, seen_count INTEGER DEFAULT 0, max_likes INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT '待研究' CHECK(status IN ('待研究','值得制作','暂缓','已制作','不适合')),
  note TEXT, hash TEXT UNIQUE NOT NULL, updated_at TEXT);
CREATE TABLE IF NOT EXISTS demand_sightings(
  id INTEGER PRIMARY KEY, demand_id INTEGER NOT NULL REFERENCES demands(id) ON DELETE CASCADE,
  collection_id INTEGER REFERENCES collections(id), seen_at TEXT NOT NULL,   -- 采集时间（我们看到它的时间）
  source_kind TEXT,      -- comment / comment_reply / search_sug / search_page_related / comment_top_rec / feed_bottom_rec / page_suggest_words / related_chips ...
  source_ref TEXT,       -- 视频 ID 或关键词
  keyword TEXT, likes INTEGER, posted_at TEXT, raw_text TEXT,
  UNIQUE(demand_id, collection_id, source_kind, source_ref, raw_text));
-- 原始评论（非疑问也留，供检索；不当作需求）
CREATE TABLE IF NOT EXISTS comments(
  id INTEGER PRIMARY KEY, cid TEXT UNIQUE, video_id TEXT, parent TEXT, text TEXT, likes INTEGER, posted_at TEXT, ip TEXT,
  collection_id INTEGER REFERENCES collections(id), is_question INTEGER);
-- 同题/竞品视频
CREATE TABLE IF NOT EXISTS ref_videos(
  id INTEGER PRIMARY KEY, platform TEXT, video_id TEXT, url TEXT, title TEXT, author TEXT,
  likes INTEGER, comments INTEGER, collects INTEGER, shares INTEGER, duration_s REAL, published TEXT,
  keyword TEXT, bgm TEXT, first_seen TEXT, last_seen TEXT, collection_id INTEGER, UNIQUE(platform, video_id));
-- 2 选题机会库
CREATE TABLE IF NOT EXISTS topics(
  id INTEGER PRIMARY KEY, title TEXT NOT NULL, core_question TEXT,
  status TEXT NOT NULL DEFAULT '候选' CHECK(status IN ('候选','研究中','已选','制作中','已制作','暂缓','放弃')),
  score REAL, score_note TEXT, why_not_made TEXT, competition TEXT, angle TEXT, anim_type TEXT,
  first_seen TEXT, last_seen TEXT, source_path TEXT, note TEXT, hash TEXT UNIQUE NOT NULL, updated_at TEXT);
-- 3 BGM 与音效库（好听≠可用：评分和授权分开存）
CREATE TABLE IF NOT EXISTS bgm(
  id INTEGER PRIMARY KEY, kind TEXT NOT NULL DEFAULT 'bgm' CHECK(kind IN ('bgm','sfx')), title TEXT, artist TEXT,
  category TEXT, mood TEXT, bpm REAL, duration_s REAL, energy_curve TEXT, segments TEXT,   -- energy_curve/segments: JSON
  use_case TEXT, file_id INTEGER REFERENCES files(id), file_path TEXT, source_url TEXT, source_note TEXT,
  user_rating INTEGER, notes TEXT, hash TEXT UNIQUE NOT NULL, updated_at TEXT);
CREATE TABLE IF NOT EXISTS bgm_license(
  id INTEGER PRIMARY KEY, bgm_id INTEGER NOT NULL REFERENCES bgm(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,   -- douyin / bilibili / all / youtube ...
  scope TEXT NOT NULL CHECK(scope IN ('允许商用','允许(需署名)','仅平台内','仅参考','禁止','未核实')),
  license_name TEXT, evidence TEXT, checked_at TEXT, UNIQUE(bgm_id, platform));
-- 4 动画资产库
CREATE TABLE IF NOT EXISTS anim_assets(
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL,  -- component/shot/scene3d/model/footage/image/brand/font/template/tool/project
  project TEXT, path TEXT, tech TEXT, tags TEXT, description TEXT, reusable_notes TEXT,
  license TEXT, ai_generated INTEGER DEFAULT 0, file_id INTEGER REFERENCES files(id), hash TEXT UNIQUE NOT NULL, updated_at TEXT);
-- 5 视频作品库
CREATE TABLE IF NOT EXISTS works(
  id INTEGER PRIMARY KEY, episode TEXT UNIQUE, title TEXT, platform TEXT,
  status TEXT CHECK(status IN ('已发布','待发布','制作中','已取消','停档','样例')), published_at TEXT,
  project_dir TEXT, final_video TEXT, script TEXT, srt TEXT, storyboard TEXT, cover TEXT, publish_caption TEXT,
  drive_folder_id TEXT, notes TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS work_metrics(   -- 只放真实数据（用户提供的创作者中心导出/截图）
  id INTEGER PRIMARY KEY, work_id INTEGER NOT NULL REFERENCES works(id) ON DELETE CASCADE, platform TEXT,
  captured_at TEXT, window TEXT, source TEXT NOT NULL,
  plays INTEGER, completion_rate REAL, completion_5s REAL, bounce_2s REAL, avg_watch_s REAL, avg_watch_ratio REAL,
  likes INTEGER, shares INTEGER, comments INTEGER, collects INTEGER, profile_visits INTEGER, followers_gained INTEGER,
  cover_ctr REAL, traffic_sources TEXT, search_terms TEXT, raw TEXT, UNIQUE(work_id, platform, captured_at, source));
CREATE TABLE IF NOT EXISTS content_dna(
  work_id INTEGER PRIMARY KEY REFERENCES works(id) ON DELETE CASCADE,
  topic_type TEXT, hook_type TEXT, structure TEXT, style TEXT, voice TEXT, music TEXT, key_visuals TEXT, duration_s REAL,
  metrics_note TEXT,     -- 只引用 work_metrics 的真实数据；无数据写「待用户导出」
  filled_by TEXT, updated_at TEXT);
-- 6 创作经验库
CREATE TABLE IF NOT EXISTS lessons(
  id INTEGER PRIMARY KEY, text TEXT NOT NULL,
  type TEXT NOT NULL CHECK(type IN ('长期偏好','单期意见','真实数据','未验证推测')),
  work_id INTEGER REFERENCES works(id), source TEXT, created_at TEXT, superseded INTEGER DEFAULT 0, hash TEXT UNIQUE NOT NULL);
-- 通用关系表：任意两条记录之间的关系
CREATE TABLE IF NOT EXISTS links(
  from_type TEXT NOT NULL, from_id INTEGER NOT NULL, rel TEXT NOT NULL, to_type TEXT NOT NULL, to_id INTEGER NOT NULL,
  note TEXT, created_at TEXT, PRIMARY KEY(from_type, from_id, rel, to_type, to_id));
CREATE INDEX IF NOT EXISTS links_to ON links(to_type, to_id);
-- 全文索引（trigram：中文子串可搜）
CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(lib UNINDEXED, ref_id UNINDEXED, title, body, tags, tokenize='trigram');
"""

# ---------- v2：数据闭环（2026-10-21）。只加列/加表，不改旧数据；connect() 时幂等执行 ----------
WORKS_V2_COLS = {  # 列名: 类型
    "publish_time": "TEXT",            # ISO 8601 带 +08:00，例 2026-10-21T20:00:00+08:00
    "planned_publish_time": "TEXT",    # 计划发布时间（待发布用）
    "publish_asked": "INTEGER DEFAULT 0",   # 计划时间过 3h 已问过用户「发了没」
    "video_url": "TEXT",
    "checkpoints_done": "TEXT DEFAULT '[]'",  # JSON 列表，如 ["2h","24h"]
    "comments_harvested": "INTEGER DEFAULT 0",
    "comments_harvested_at": "TEXT",
    "timeline_path": "TEXT",           # 可选：诊断用时间轴 json（缺省自动在 project_dir 里找）
}
DNA_V2_COLS = {"hook_class": "TEXT", "topic_class": "TEXT", "title_search_first": "INTEGER", "duration_note": "TEXT"}
SCHEMA_V2 = r"""
CREATE TABLE IF NOT EXISTS metrics_snapshots(   -- 只放真实数据（创作者中心导出/截图转录），source 必填
  id INTEGER PRIMARY KEY, work_id INTEGER NOT NULL REFERENCES works(id) ON DELETE CASCADE,
  platform TEXT NOT NULL DEFAULT '抖音', checkpoint TEXT NOT NULL,   -- 2h/24h/72h/7d（回填可有 8h/48h 等）
  captured_at TEXT, plays INTEGER, completion_5s REAL, avg_watch_s REAL, avg_watch_ratio REAL, bounce_2s REAL, completion_rate REAL,
  likes INTEGER, comments INTEGER, shares INTEGER, favorites INTEGER, follows_gained INTEGER, profile_visits INTEGER, cover_ctr REAL,
  search_share REAL, recommend_share REAL, source TEXT NOT NULL, raw_json TEXT, ingested_at TEXT,
  UNIQUE(work_id, platform, checkpoint));
CREATE TABLE IF NOT EXISTS retention_curve(
  work_id INTEGER NOT NULL REFERENCES works(id) ON DELETE CASCADE, platform TEXT NOT NULL DEFAULT '抖音',
  checkpoint TEXT NOT NULL, t_sec REAL NOT NULL, retention REAL NOT NULL,     -- retention 0–1
  PRIMARY KEY(work_id, platform, checkpoint, t_sec));
CREATE TABLE IF NOT EXISTS insights(
  id INTEGER PRIMARY KEY, key TEXT UNIQUE NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('开头','标题','时长','选题','段落')),
  statement TEXT NOT NULL, evidence_work_ids TEXT, metric_basis TEXT,
  n INTEGER DEFAULT 0, status TEXT NOT NULL DEFAULT '验证中' CHECK(status IN ('验证中','已验证','已推翻')), updated_at TEXT);
CREATE TABLE IF NOT EXISTS insights_history(
  id INTEGER PRIMARY KEY, insight_id INTEGER REFERENCES insights(id) ON DELETE CASCADE, at TEXT, status TEXT, statement TEXT, n INTEGER);
"""

def migrate(c):
    c.executescript(SCHEMA_V2)
    for tb, cols in (("works", WORKS_V2_COLS), ("content_dna", DNA_V2_COLS)):
        have = {r[1] for r in c.execute(f"PRAGMA table_info({tb})")}
        for k, t in cols.items():
            if k not in have: c.execute(f"ALTER TABLE {tb} ADD COLUMN {k} {t}")
    c.execute("INSERT OR IGNORE INTO meta VALUES('schema_version','2')"); c.execute("UPDATE meta SET v='2' WHERE k='schema_version' AND CAST(v AS INT)<2"); c.commit()


# ---------- v3：Feedback Engine（2026-10-21）。只加列/加表；lessons 重建一次以放宽 type ----------
SNAP_V3_COLS = {
    "age_h": "REAL",               # 发布→截图/导出的实际小时数（checkpoint 标签只是近似档）
    "stat_cutoff": "TEXT",         # 页面显示的统计截止时间（原文；没有就 NULL）
    "missing_fields": "TEXT",      # JSON：这次来源里拿不到的字段
    "verified": "INTEGER DEFAULT 0",   # 1=导出表原值或用户确认/人工读数一致；0=待核
    "verify_note": "TEXT",
    "precision_note": "TEXT",      # 如「播放 1.3万 为界面取整，±500」
}
WORKS_V3_COLS = {"publish_title": "TEXT", "douyin_item_id": "TEXT", "duration_label": "TEXT"}
SCHEMA_V3 = r"""
CREATE TABLE IF NOT EXISTS screenshot_extractions(      -- 每张截图 × 每个作品 一次 OCR 抽取（qoder Flash）
  id INTEGER PRIMARY KEY, file TEXT NOT NULL, sha256 TEXT NOT NULL, work_id INTEGER REFERENCES works(id),
  page_kind TEXT, row_label TEXT, checkpoint TEXT, age_h REAL, captured_at TEXT, stat_cutoff TEXT,
  ocr_model TEXT, ocr_json TEXT, parsed_json TEXT, review_path TEXT,
  status TEXT NOT NULL DEFAULT '待核' CHECK(status IN ('待核','已确认','有出入','作废')),
  check_json TEXT, snapshot_id INTEGER REFERENCES metrics_snapshots(id), created_at TEXT, confirmed_at TEXT,
  UNIQUE(sha256, work_id));
CREATE TABLE IF NOT EXISTS metric_values(               -- 字段级出处：每个数从哪来、精度、是否核过
  snapshot_id INTEGER NOT NULL REFERENCES metrics_snapshots(id) ON DELETE CASCADE, field TEXT NOT NULL,
  value REAL, raw_text TEXT, source_kind TEXT NOT NULL,  -- xlsx / screenshot_ocr / manual_transcribe / manual_read
  source_file TEXT, precision TEXT, verified INTEGER DEFAULT 0, verify_note TEXT, extraction_id INTEGER, at TEXT,
  PRIMARY KEY(snapshot_id, field, source_kind, source_file));
CREATE TABLE IF NOT EXISTS traffic_terms(               -- 作品真实流量数据（创作者中心）：搜索来源词/看后搜/流量来源/章节点击
  id INTEGER PRIMARY KEY, work_id INTEGER NOT NULL REFERENCES works(id) ON DELETE CASCADE, checkpoint TEXT,
  kind TEXT NOT NULL CHECK(kind IN ('搜索来源词','看后常搜','流量来源','章节点击')),
  rank INTEGER, term TEXT NOT NULL, share REAL, delta TEXT, source TEXT NOT NULL, extraction_id INTEGER, verified INTEGER DEFAULT 0, captured_at TEXT,
  UNIQUE(work_id, checkpoint, kind, term));
-- 注意：搜索框联想（search_sug）、页面看后搜联想（page_suggest_words）、大家都在搜（comment_top_rec）来自游客采集，
--       是「相关搜索」，在 demand_sightings.source_kind 里；traffic_terms 只放作品后台的真实来源数据，两者不混。
CREATE TABLE IF NOT EXISTS comment_labels(              -- 评论分类/聚类结果
  comment_key TEXT PRIMARY KEY,                         -- comments.cid 或 'shot:'+sha1(截图评论)
  work_id INTEGER REFERENCES works(id), text TEXT, norm TEXT, likes INTEGER, posted_at TEXT, source TEXT,
  category TEXT NOT NULL CHECK(category IN ('真实疑问','科学错误质疑','理解障碍','情绪反馈','新选题需求','其他')),
  cluster_id INTEGER, demand_id INTEGER REFERENCES demands(id), method TEXT, labeled_at TEXT);
CREATE TABLE IF NOT EXISTS comment_clusters(
  id INTEGER PRIMARY KEY, work_id INTEGER, category TEXT, label TEXT, size INTEGER, sample TEXT, demand_id INTEGER, updated_at TEXT);
CREATE TABLE IF NOT EXISTS findings(                    -- 诊断六项
  id INTEGER PRIMARY KEY, work_id INTEGER REFERENCES works(id), report TEXT, key TEXT,
  phenomenon TEXT NOT NULL, evidence TEXT NOT NULL, baseline TEXT, causes TEXT, alternatives TEXT,
  confidence TEXT CHECK(confidence IN ('高','中','低','很低')), suggestion TEXT, experiment TEXT,
  basis_kind TEXT,                                      -- 真实数据 / 推断（无留存曲线时只能推断）
  created_at TEXT, UNIQUE(work_id, key, report));
CREATE TABLE IF NOT EXISTS suggestions(                 -- 改进建议：只有用户批准的才进 lessons
  id INTEGER PRIMARY KEY, finding_id INTEGER REFERENCES findings(id), work_id INTEGER REFERENCES works(id),
  stage TEXT CHECK(stage IN ('选题','脚本','分镜','标题文案','封面','发布','配音','其他')),
  text TEXT NOT NULL, experiment TEXT, status TEXT NOT NULL DEFAULT '待批' CHECK(status IN ('待批','已批','拒绝')),
  decided_at TEXT, decision_note TEXT, lesson_id INTEGER, hypothesis_id INTEGER, created_at TEXT, hash TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS hypotheses(                  -- 假设：未验证 / 验证中 / 已支持 / 已否定（否定的也保留）
  id INTEGER PRIMARY KEY, statement TEXT NOT NULL, status TEXT NOT NULL DEFAULT '未验证' CHECK(status IN ('未验证','验证中','已支持','已否定')),
  origin TEXT, test_plan TEXT, result TEXT, evidence_work_ids TEXT, created_at TEXT, updated_at TEXT, hash TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS lesson_outcomes(             -- 已批经验在后续作品上的真实表现
  id INTEGER PRIMARY KEY, lesson_id INTEGER NOT NULL REFERENCES lessons(id), work_id INTEGER REFERENCES works(id),
  metric TEXT, value REAL, baseline REAL, baseline_desc TEXT, note TEXT, at TEXT, UNIQUE(lesson_id, work_id, metric));
CREATE TABLE IF NOT EXISTS backups(                     -- Drive 备份记录（sha256 去重，上传后回读校验）
  id INTEGER PRIMARY KEY, local_path TEXT NOT NULL, kind TEXT, sha256 TEXT NOT NULL, size INTEGER,
  drive_folder_id TEXT, drive_file_id TEXT, drive_name TEXT, drive_size INTEGER, drive_md5 TEXT, local_md5 TEXT,
  status TEXT NOT NULL DEFAULT '待传' CHECK(status IN ('待传','已传','已校验','校验失败','跳过重复')),
  planned_at TEXT, uploaded_at TEXT, verified_at TEXT, note TEXT, UNIQUE(sha256, drive_folder_id));
CREATE TABLE IF NOT EXISTS screenshot_files(            -- 截图登记：sha256 判字节重复，dhash（256 位感知哈希）判内容重复
  sha256 TEXT PRIMARY KEY, path TEXT, phash TEXT, width INTEGER, height INTEGER, dup_of TEXT, registered_at TEXT);
CREATE TABLE IF NOT EXISTS retention_marks(             -- 平台在留存图上标的低谷/高峰（截图读出，精度约 ±1s），以及与同类作品对比的定性描述
  id INTEGER PRIMARY KEY, work_id INTEGER NOT NULL REFERENCES works(id) ON DELETE CASCADE, checkpoint TEXT,
  kind TEXT NOT NULL CHECK(kind IN ('低谷','高峰','同类对比')), label TEXT, t_start REAL, t_end REAL, note TEXT,
  source TEXT NOT NULL, precision TEXT, extraction_id INTEGER, verified INTEGER DEFAULT 0, captured_at TEXT,
  UNIQUE(work_id, checkpoint, kind, label));
CREATE TABLE IF NOT EXISTS hourly_plays(                -- 截图里的每小时播放（读图，近似）
  work_id INTEGER NOT NULL REFERENCES works(id) ON DELETE CASCADE, hour TEXT NOT NULL, plays REAL, approx INTEGER DEFAULT 1,
  source TEXT, extraction_id INTEGER, PRIMARY KEY(work_id, hour));
"""
LESSON_TYPES = ('长期偏好','单期意见','真实数据','未验证推测','已批改进')

def migrate_v3(c):
    c.executescript(SCHEMA_V3)
    for tb, cols in (("metrics_snapshots", SNAP_V3_COLS), ("works", WORKS_V3_COLS), ("comment_clusters", {"collection_id": "INTEGER"})):
        have = {r[1] for r in c.execute(f"PRAGMA table_info({tb})")}
        for k, t in cols.items():
            if k not in have: c.execute(f"ALTER TABLE {tb} ADD COLUMN {k} {t}")
    sql = c.execute("SELECT sql FROM sqlite_master WHERE name='lessons'").fetchone()[0]
    if "已批改进" not in sql:   # 重建 lessons：放宽 type，加 suggestion_id；id 保持不变
        c.commit(); c.execute("PRAGMA foreign_keys=OFF")
        c.executescript("""
        CREATE TABLE lessons_v3(
          id INTEGER PRIMARY KEY, text TEXT NOT NULL,
          type TEXT NOT NULL CHECK(type IN ('长期偏好','单期意见','真实数据','未验证推测','已批改进')),
          work_id INTEGER REFERENCES works(id), source TEXT, created_at TEXT, superseded INTEGER DEFAULT 0, hash TEXT UNIQUE NOT NULL,
          suggestion_id INTEGER, stage TEXT);
        INSERT INTO lessons_v3(id,text,type,work_id,source,created_at,superseded,hash) SELECT id,text,type,work_id,source,created_at,superseded,hash FROM lessons;
        DROP TABLE lessons; ALTER TABLE lessons_v3 RENAME TO lessons;""")
        c.execute("PRAGMA foreign_keys=ON")
    c.execute("INSERT OR REPLACE INTO meta VALUES('schema_version','3')"); c.commit()

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    c.executescript(SCHEMA)
    c.execute("INSERT OR IGNORE INTO meta VALUES('schema_version','1')")
    migrate(c)
    migrate_v3(c)
    return c

# ---------- 时间工具（Asia/Shanghai） ----------
def parse_time(s):
    """'2026-10-21 20:00' / '2026-10-21T20:00:00+08:00' / '2026/10/21 20:00:05' → aware datetime（无时区按 UTC+8）。"""
    if not s: return None
    if isinstance(s, datetime.datetime): d = s
    else:
        t = str(s).strip().replace("/", "-").replace("T", " ")
        m = re.match(r"(\d{4}-\d{1,2}-\d{1,2})(?: (\d{1,2}:\d{2})(:\d{2})?)?\s*([+-]\d{2}:?\d{2}|Z)?$", t)
        if not m: raise ValueError(f"看不懂的时间：{s}")
        d = datetime.datetime.strptime(f"{m.group(1)} {m.group(2) or '00:00'}{m.group(3) or ':00'}", "%Y-%m-%d %H:%M:%S")
        if m.group(4):
            z = m.group(4); d = d.replace(tzinfo=datetime.timezone.utc) if z == "Z" else d.replace(tzinfo=datetime.datetime.strptime(z.replace(":", ""), "%z").tzinfo)
    if d.tzinfo is None: d = d.replace(tzinfo=TZ)
    return d.astimezone(TZ)
def iso(d): return parse_time(d).isoformat(timespec="seconds") if d else None
def now_dt():
    o = os.environ.get("STUDIO_NOW")   # 测试用：固定「现在」
    return parse_time(o) if o else datetime.datetime.now(TZ)
def find_work(c, ref):
    """work id、episode 编号（EP-…/LEGACY-…）或标题子串 → works 行。"""
    r = None
    if str(ref).isdigit(): r = c.execute("SELECT * FROM works WHERE id=?", (int(ref),)).fetchone()
    r = r or c.execute("SELECT * FROM works WHERE episode=?", (ref,)).fetchone()
    if not r:
        rs = c.execute("SELECT * FROM works WHERE episode LIKE ? OR title LIKE ?", (f"%{ref}%", f"%{ref}%")).fetchall()
        if len(rs) == 1: r = rs[0]
        elif len(rs) > 1: raise SystemExit(f"「{ref}」匹配到多条作品：" + "，".join(f"#{x['id']} {x['episode']}" for x in rs))
    if not r: raise SystemExit(f"找不到作品：{ref}")
    return r
def jlist(s):
    try: v = json.loads(s or "[]"); return v if isinstance(v, list) else []
    except Exception: return []

_EMO = re.compile(r"\[[^\[\]]{1,8}\]")   # 抖音表情 [捂脸]
def norm(t):
    t = unicodedata.normalize("NFKC", t or "")
    t = _EMO.sub("", t).lower()
    t = re.sub(r"@\S+", "", t)
    return re.sub(r"[\s\W_]+", "", t)
def h(*parts): return hashlib.sha1("\x1f".join(str(p) for p in parts).encode()).hexdigest()
def sha256_file(p, buf=1 << 20):
    x = hashlib.sha256()
    with open(p, "rb") as f:
        while b := f.read(buf): x.update(b)
    return x.hexdigest()

def register_file(c, path, kind=None):
    p = pathlib.Path(path)
    if not p.is_file(): return None
    st = p.stat(); mt = datetime.datetime.fromtimestamp(st.st_mtime, TZ).strftime("%Y-%m-%d %H:%M:%S")
    r = c.execute("SELECT id,size,mtime,sha256 FROM files WHERE path=?", (str(p),)).fetchone()
    if r and r["size"] == st.st_size and r["mtime"] == mt: return r["id"]
    sh = sha256_file(p)
    if r:
        c.execute("UPDATE files SET sha256=?,size=?,mtime=?,kind=COALESCE(?,kind) WHERE id=?", (sh, st.st_size, mt, kind, r["id"])); return r["id"]
    return c.execute("INSERT INTO files(path,sha256,size,mtime,kind) VALUES(?,?,?,?,?)", (str(p), sh, st.st_size, mt, kind)).lastrowid

def link(c, ft, fid, rel, tt, tid, note=None):
    c.execute("INSERT OR IGNORE INTO links VALUES(?,?,?,?,?,?,?)", (ft, fid, rel, tt, tid, note, now()))

_Q = re.compile(r"[?？]|吗|呢|怎么|为什么|为啥|什么|能不能|会不会|是不是|有没有|如何|多少|哪|咋|啥|靠谱|真的假的|求|谁能|可以.{0,6}吗")
def is_question(t): return bool(_Q.search(t or ""))

def reindex(c):
    """全量重建 FTS（几千行级别，秒级）。"""
    c.execute("DELETE FROM fts")
    q = {
     "demand": "SELECT id, text, kind||' '||status||' '||COALESCE(note,''), (SELECT group_concat(DISTINCT keyword) FROM demand_sightings s WHERE s.demand_id=d.id) FROM demands d",
     "topic": "SELECT id, title, COALESCE(core_question,'')||' '||COALESCE(angle,'')||' '||COALESCE(note,'')||' '||COALESCE(why_not_made,''), status FROM topics",
     "bgm": "SELECT b.id, COALESCE(title,'')||' '||COALESCE(artist,''), COALESCE(category,'')||' '||COALESCE(mood,'')||' '||COALESCE(use_case,'')||' '||COALESCE(notes,'')||' '||COALESCE(source_note,''), kind||' '||COALESCE((SELECT group_concat(platform||':'||scope,' ') FROM bgm_license l WHERE l.bgm_id=b.id),'') FROM bgm b",
     "asset": "SELECT id, name, COALESCE(description,'')||' '||COALESCE(reusable_notes,'')||' '||COALESCE(path,''), COALESCE(tags,'')||' '||kind||' '||COALESCE(project,'')||' '||COALESCE(tech,'') FROM anim_assets",
     "work": "SELECT id, COALESCE(title,'')||' '||episode, COALESCE(notes,'')||' '||COALESCE(final_video,'')||' '||COALESCE(script,''), COALESCE(status,'')||' '||COALESCE(platform,'') FROM works",
     "lesson": "SELECT id, type, text, COALESCE(source,'') FROM lessons WHERE superseded=0",
     "comment": "SELECT id, video_id, text, CASE is_question WHEN 1 THEN 'question' ELSE '' END FROM comments",
     "video": "SELECT id, COALESCE(title,''), COALESCE(author,'')||' '||COALESCE(bgm,''), COALESCE(keyword,'') FROM ref_videos",
    }
    for lib, sql in q.items():
        c.executemany("INSERT INTO fts(lib,ref_id,title,body,tags) VALUES(?,?,?,?,?)", [(lib, *r) for r in c.execute(sql).fetchall()])
    c.execute("INSERT INTO fts(fts) VALUES('optimize')")
