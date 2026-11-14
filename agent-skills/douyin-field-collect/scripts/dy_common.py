"""公共工具：免登录请求、作品 ID 解析、字段状态常量。不带任何账号 cookie，不做签名逆向。"""
import datetime as dt, re, sys, time
try:
    import requests
except ModuleNotFoundError:
    sys.stderr.write(
        "[douyin-field-collect] 缺少 Python 依赖 requests。这是本机环境问题，不是登录失败。\n"
        "在技能目录执行: python3 -m pip install -r requirements.txt\n"
    )
    raise SystemExit(2)

TZ = dt.timezone(dt.timedelta(hours=8))
UA_M = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
UA_PC = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
BASE = {"aid": "581610", "channel": "channel_pc_web", "platform": "PC", "device_platform": "webapp"}
# 每个字段的状态取值（与输出 JSON 的 status 一致）
STATUSES = ("available", "partial", "observed_empty", "missing", "blocked_login",
            "blocked_verification", "error", "not_requested")
S = requests.Session()


def T(sec):
    return dt.datetime.fromtimestamp(int(sec), TZ).strftime("%Y-%m-%d %H:%M") if sec else ""


def now():
    return dt.datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S (UTC+8)")


def log(*a):
    print("[douyin-field-collect]", *a, file=sys.stderr, flush=True)


class Blocked(Exception):
    """没拿到 JSON。status 为 blocked_verification、blocked_login，或 error（网络/程序）。"""
    def __init__(self, status, detail=""):
        super().__init__(f"{status}: {detail}")
        self.status, self.detail = status, detail


def format_exc(e):
    """把异常写成可区分的原因。缺模块/缺可执行文件以 missing_dependency 开头，避免被当成登录失败。"""
    msg = (str(e).strip().splitlines() or [""])[0][:180]
    name = type(e).__name__
    low = msg.lower()
    missing = name in ("ModuleNotFoundError", "ImportError", "FileNotFoundError") or "executable doesn't exist" in low or "no module named" in low
    body = name + (f": {msg}" if msg and msg != name else "")
    return f"missing_dependency: {body}" if missing else body


def classify_non_json(status_code, text):
    """非 JSON 响应分类。403/429 和验证码标记优先于正文里的“登录”，避免把验证页记成登录墙。"""
    sample = (text or "")[:3000]
    low = sample.lower()
    has_verify = ("verify" in low) or ("captcha" in low) or ("验证" in sample)
    has_login = ("login" in low) or ("登录" in sample)
    detail = f"HTTP {status_code} {len(text or '')}B"
    if status_code == 401:
        return "blocked_login", detail
    if status_code in (403, 429) or has_verify:
        return "blocked_verification", detail
    if has_login:
        return "blocked_login", detail
    if not text:
        return "blocked_verification", detail
    return "error", f"HTTP {status_code} 非JSON {len(text)}B"


def preflight():
    """本机依赖检查。不访问网络，不启动浏览器。"""
    import importlib.util, shutil
    mods = {}
    for name in ("requests", "playwright", "PIL", "numpy", "faster_whisper"):
        try:
            mods[name] = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError):
            mods[name] = False
    bins = {b: shutil.which(b) is not None for b in (
        "curl", "ffmpeg", "ffprobe", "yt-dlp", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser")}
    return {
        "python": sys.version.split()[0],
        "modules": mods,
        "binaries": bins,
        "default_video_ready": bool(mods.get("requests")),
        "note": "不访问网络。默认 video 只需 requests。playwright 仅 --browse / --search-rel / dy_search 的 so 源需要；"
                "ffmpeg 仅 --media 截帧；faster-whisper 仅 --asr；yt-dlp 只是下载链最后一级。"
                "缺这些时 status=error 且 reason 以 missing_dependency 开头，不是 blocked_login。",
    }


def get_json(url, params, ref="https://so.douyin.com/", ua=UA_M, tries=2):
    """GET 公开接口。返回 dict；连续拿到非 JSON 时抛 Blocked（不换身份、不硬重试）。"""
    last = ""
    for k in range(tries):
        try:
            r = S.get(url, params=params, headers={"User-Agent": ua, "Referer": ref}, timeout=20)
            t = r.text.strip()
            if t.startswith("{"):
                return r.json()
            st, detail = classify_non_json(r.status_code, t)
            last = f"{st}|{detail}"
        except requests.RequestException as e:
            last = f"error|{format_exc(e)}"
        time.sleep(1.5 * (k + 1))
    st, _, d = last.partition("|")
    raise Blocked(st, d)


def vid_of(s):
    s = s.strip()
    m = re.search(r"https?://\S+", s)
    u = m.group(0) if m else s
    m = re.search(r"(?:video/|modal_id=|note/|aweme_id=)(\d{15,21})", u) or re.fullmatch(r"(\d{15,21})", u)
    if m:
        return m.group(1)
    if "v.douyin.com" in u or "iesdouyin.com" in u:
        try:
            r = S.get(u, headers={"User-Agent": UA_M}, allow_redirects=False, timeout=15)
        except requests.RequestException as e:
            raise SystemExit(f"解析短链失败（网络或本机错误，不是登录失败）：{format_exc(e)}")
        m = re.search(r"/(?:video|note)/(\d{15,21})", r.headers.get("location", ""))
        if m:
            return m.group(1)
    raise SystemExit(f"未识别到作品ID：{s}")


def launch_sync(p):
    """优先用系统 Chrome；没有就用 `playwright install chromium` 装的 Chromium。"""
    try:
        return p.chromium.launch(channel="chrome", headless=True)
    except Exception:
        return p.chromium.launch(headless=True)
