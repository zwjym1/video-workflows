#!/usr/bin/env python3
"""一次性：EP-20261021-01 光遗传学归档入库（works 迁移加「待发布」、资产、经验、content_dna）。幂等。"""
import sys, pathlib, glob
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import db
c = db.connect()
# 1) works.status CHECK 加「待发布」（SQLite 需重建表）
sql = c.execute("SELECT sql FROM sqlite_master WHERE name='works'").fetchone()[0]
if "待发布" not in sql:
    c.commit(); c.execute("PRAGMA foreign_keys=OFF"); c.execute("BEGIN")
    c.execute(sql.replace("CREATE TABLE works(", "CREATE TABLE works_new(").replace("'已发布','制作中'", "'已发布','待发布','制作中'"))
    c.execute("INSERT INTO works_new SELECT * FROM works"); c.execute("DROP TABLE works")
    c.execute("ALTER TABLE works_new RENAME TO works")
    c.execute("COMMIT"); c.execute("PRAGMA foreign_keys=ON")
    assert not c.execute("PRAGMA foreign_key_check").fetchall()
before = {t: c.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in ("works","anim_assets","lessons","content_dna","links","files")}
EP = "EP-20261021-01"; O = "/workspace/optogenetics"; PC = r"D:\编程\项目\视频制作\作品\2026-10-21_光遗传学"
row = c.execute("SELECT id FROM works WHERE episode IN ('LEGACY-optogenetics',?)", (EP,)).fetchone()
vals = dict(episode=EP, title="池塘里的绿藻，凭什么帮人类「用光控制大脑」？（2026 诺奖光遗传学）", platform="抖音（B站可同发）", status="待发布",
  project_dir=O, final_video=PC + r"\out\光遗传学_成片_v1p_1080.mp4", script=f"{O}/script_original.md", storyboard=f"{O}/storyboard_2d.md",
  cover=f"{O}/publish/covers/cover_A_9x16_1080x1920.png", publish_caption=f"{O}/publish/publish_pack.md",
  notes="首期完整跑通（science-studio）。1080×1920 30fps 174.9 s，Remotion OptoFilm 5246 帧，PC 13 分钟渲完；成片在 PC（291MB，不传 Drive）。配音 vo_master.wav + 4 句 B 重配（v1p）。发布包已备，用户自行发布。state：science-studio/projects/EP-20261021-01", updated_at=db.now())
if row:
    wid = row[0]; c.execute("UPDATE works SET " + ",".join(f"{k}=?" for k in vals) + " WHERE id=?", (*vals.values(), wid))
else:
    wid = c.execute("INSERT INTO works(" + ",".join(vals) + ") VALUES(" + ",".join("?"*len(vals)) + ")", tuple(vals.values())).lastrowid
c.execute("""INSERT INTO content_dna(work_id,topic_type,hook_type,structure,style,voice,music,key_visuals,duration_s,metrics_note,filled_by,updated_at)
 VALUES(?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(work_id) DO UPDATE SET topic_type=excluded.topic_type,hook_type=excluded.hook_type,structure=excluded.structure,
 style=excluded.style,voice=excluded.voice,music=excluded.music,key_visuals=excluded.key_visuals,duration_s=excluded.duration_s,metrics_note=excluded.metrics_note,updated_at=excluded.updated_at""",
 (wid, "诺奖/科学大事+原理（时效）", "反差提问：池塘绿藻 × 用光控制大脑（14 s 内进源头）",
  "提问→源头衣藻→揪出 ChR2→装进大脑（小鼠醒/僵）→跟你有关→临床试验（6 段，章节化）",
  "竖屏 2D Remotion 连续运动 + CC 显微实拍 + 圆裁人物照 + 4 处 AI 生成画面；一句一卡字幕；丞印角标",
  "Fish s2.1-pro-free 整篇配音（cfd828…）+ 4 句重配", "垫乐 −9 dB 闪避，自制少量音效，母版 −16 LUFS",
  "衣藻显微、通道开关、狙击式点亮神经元、小鼠醒来/僵住、易拉罐、盲人抓杯", 174.9, "待用户导出", "archive_ep01.py（据工程与对话）", db.now()))
def asset(name, kind, path, tech, tags, desc, notes=None, lic=None, ai=0, project=f"{O}/remotion"):
    hh = db.h("asset", path or name)
    fid = db.register_file(c, path, kind) if path and pathlib.Path(path).is_file() else None
    c.execute("""INSERT INTO anim_assets(name,kind,project,path,tech,tags,description,reusable_notes,license,ai_generated,file_id,hash,updated_at)
       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(hash) DO UPDATE SET name=excluded.name,tags=excluded.tags,description=excluded.description,
       reusable_notes=excluded.reusable_notes,license=COALESCE(excluded.license,license),ai_generated=excluded.ai_generated,file_id=excluded.file_id,updated_at=excluded.updated_at""",
       (name, kind, project, path, tech, tags, desc, notes, lic, ai, fid, hh, db.now()))
    aid = c.execute("SELECT id FROM anim_assets WHERE hash=?", (hh,)).fetchone()[0]; db.link(c, "asset", aid, "used_in", "work", wid); return aid
F = f"{O}/remotion/src/film"; R = "Remotion 4.0.536 TSX"; T = "2D 科普 竖屏 时间戳驱动 光遗传学"
new = []
new.append(asset("Seg3 揪出光控开关（ChR2）", "component", f"{F}/Seg3.tsx", R, T+" 通道蛋白 细胞膜 离子", "③段：从衣藻眼点到通道视紫红质-2，蓝光开通道、离子流入的连续运动", "通道开关类原理可复用"))
for fn, d in [("Seg4.tsx","④段总装：狙击式点亮神经元→小鼠醒来/恐惧僵住"),("Seg4a.tsx","④段上半 4-1～4-5"),("Seg4b.tsx","④段下半 4-6～4-10：网络→小鼠镜头切换"),
              ("common4.tsx","④段共用：配色、一句一卡字幕组件、角标签、脑内网络世界、小鼠、DNA 螺旋"),("net4.ts","脑内神经网络节点/脉冲数据（程序化生成）"),
              ("plan_s4.ts","④段时间轴与镜头参数（按母带逐字时间戳）"),("entry.tsx","单段独立预览入口（不改总 Root，便于并行）"),("check_seg4.ts","布局/出框自检脚本")]:
    new.append(asset(f"seg4/{fn}（optogenetics）", "component", f"{F}/seg4/{fn}", R, T+" 神经元 小鼠 大脑 网络", d))
for fn, d in [("Seg5.tsx","⑤段：跟你有关（代糖、心跳）"),("plan.ts","⑤段时间轴"),("preview.tsx","⑤段独立预览入口"),("check.ts","⑤段自检")]:
    new.append(asset(f"seg5/{fn}（optogenetics）", "component", f"{F}/seg5/{fn}", R, T+" 代糖 易拉罐 心跳", d))
for fn, d in [("Seg6.tsx","⑥段：临床试验替盲人找回一点光（主观镜头+抓杯）"),("plan6.ts","⑥段时间轴"),("index6.tsx","⑥段独立渲染入口"),("check6.ts","⑥段自检")]:
    new.append(asset(f"seg6/{fn}（optogenetics）", "component", f"{F}/seg6/{fn}", R, T+" 视网膜 盲人 临床", d))
AI = f"{O}/remotion/public/ai"
for stem, d in [("dish_b","戴蓝手套的手托起发绿光的培养皿（含 fg/bg 分层）"),("can","无品牌银色易拉罐开罐微距（含 fg 分层）"),("corridor","老胶片走廊（历史回溯过场）"),
                ("cup_hand","盲人主观视角伸手抓杯（含 fg 分层）"),("cup_plate","木桌白杯无手版（分层底图）")]:
    for f in sorted(glob.glob(f"{AI}/{stem}*")):
        new.append(asset(f"AI图 {pathlib.Path(f).name}", "image", f, "AI 生成（提示词见 ai_prompts_2d.md）", "AI生成 2.5D视差 竖屏 "+stem, d,
                         "片中须标「AI 生成」；提示词 /workspace/optogenetics/ai_prompts_2d.md", "AI 生成（自有）", 1))
FT = f"{O}/remotion/public/footage"
new.append(asset("衣藻游动显微帧序列 qin_00–11", "footage", FT+"/qin_*.jpg", "jpg 序列（放大+颗粒）", "显微 衣藻 鞭毛 实拍", "Qin 2015 Sci Rep 衣藻摆鞭毛，截取放大为 12 帧序列",
                 "署名：Qin B, Gopinath A, Yang J, Gollub J, Arratia P, Scientific Reports 2015", "CC BY 4.0"))
new.append(asset("小鼠神经元显微帧序列 kh_00–11", "footage", FT+"/kh_*.jpg", "jpg 序列", "显微 荧光 神经元 小鼠 实拍", "Kuhlman & Huang 2008 PLoS ONE 小鼠荧光神经元 z 扫描，截取 12 帧",
                 "署名：Kuhlman S, Huang ZJ, PLoS ONE 2008", "CC BY 2.5"))
PH = f"{O}/remotion/public/photos"
for fn, who, lic, cr in [("hegemann.png","彼得·黑格曼","CC BY-SA 4.0","Millencolin / Wikimedia Commons"),("nagel.png","格奥尔格·纳格尔","CC0","Wikimedia Commons"),("deisseroth.png","卡尔·戴塞洛斯","CC BY-SA 4.0","Christopher Michel / Wikimedia Commons")]:
    new.append(asset(f"人物圆裁 {who}", "image", f"{PH}/{fn}", "png 圆形裁切", "人物 科学家 诺奖 光遗传学", f"{who}圆形裁切头像（人名卡用）", f"署名：{cr}（圆形裁切）", lic))
new.append(asset("丞印透明角标 seal_t.png", "brand", f"{O}/remotion/public/brand/seal_t.png", "png", "品牌 丞 朱印 角标", "全片统一「丞」朱印角标的透明版（硬规则 2）", None, "自有"))
new.append(asset("PC 参数化渲染脚本 render_film_pc.ps1", "tool", f"{O}/pc_pack/render_film_pc.ps1", "PowerShell", "渲染 PC RTX3080 Remotion 分段重渲 720p 1080",
                 "幂等解压/依赖、Chrome 冒烟自动降级、-Mode 720|1080|both、-Frames 单段重渲、ffmpeg 合轨+ffprobe 核对；实测 1080 全片 5246 帧 13 分钟",
                 "新一期复制后改 composition/zip/混音文件名，-Root 指 D 盘工程目录", "自有", project=f"{O}/pc_pack"))
new.append(asset("全片混音配方 film_mix_v1p.py", "tool", f"{O}/audio/film_mix_v1p.py", "Python+ffmpeg", "混音 闪避 响度 换声",
                 "整片：配音+垫乐 −9 dB 闪避+自制音效，loudnorm 到 −16 LUFS；支持局部替换句子后重混", None, "自有", project=f"{O}/audio"))
L = [("长期偏好","配音按意思段（3–5 句）带上下文生成、只出一条给用户听；音调靠标点和断句在生成时管住，少用感叹号和「居然」「最让人破防」类易被读成喊的写法。","用户 2026-10-21"),
     ("单期意见","光遗传学：整篇配音有几句开头被整体抬高（像突然喊）；单句重配后硬塞回原时间点（0.85–1.2 倍拉伸+补静音）导致停顿不对、个别字发紧。修法：整段带上下文重配，画面跟新配音时间轴走，只重渲受影响段。","EP-20261021-01 审片"),
     ("长期偏好","PC 在线时所有渲染（含 720p 预览）都在用户 PC；≥30MB 的 CopyFromBox 会失败，按 ≤4MB 分块传+SHA256 核对。","EP-20261021-01 实测"),
     ("长期偏好","渲后质检：ffmpeg 测黑屏/冻帧/响度/接缝，每 5 秒抽 1 帧交 qoder Flash（每次 ≤5 张），我只汇总，不自己读帧，省额度。","用户 2026-10-21"),
     ("长期偏好","PC 上视频文件只放 D:\\编程\\项目\\视频制作\\作品\\<日期_选题>\\（out/发布/工程/预览），不在 C:\\Users\\Administrator 下建目录。","用户 2026-10-21"),
     ("单期意见","Flash 报第 50 秒人名卡/「蛙卵」标签被左边缘截掉，复查是滑出动画中 <0.5 s 的瞬间，不算硬错；可疑帧先抽前后 ±0.5 s 再判。","EP-20261021-01 质检"),
     ("长期偏好","发布包要自动附抖音发布页逐项填写清单（章节、标签、热点、可见、保存、时间、AI 声明），不要等用户来问。","用户 2026-10-21")]
nl = []
for t, text, src in L:
    hh = db.h("lesson", db.norm(text))
    c.execute("INSERT OR IGNORE INTO lessons(text,type,work_id,source,created_at,hash) VALUES(?,?,?,?,?,?)", (text, t, wid, src, db.now(), hh))
    nl.append(c.execute("SELECT id FROM lessons WHERE hash=?", (hh,)).fetchone()[0])
db.reindex(c); c.commit()
after = {t: c.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in before}
print("work_id", wid, "| new asset ids", sorted(set(new)), "| lesson ids", nl)
print({t: after[t]-before[t] for t in before})
