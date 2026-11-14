#!/usr/bin/env python3
"""离线测试。禁止访问抖音或其他网站；套接字一旦 connect 即失败。"""
import io, json, os, shutil, socket, subprocess, sys, tempfile, unittest
from contextlib import redirect_stderr
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

import dy_collect, dy_common, dy_search, media  # noqa: E402

VID = "7600000000000000001"


def _ns(**kw):
    base = dict(target=VID, out="", n=20, replies=False, reply_n=20, kw=None, search_rel=False,
                browse=False, media=False, asr=False, asr_model="small", hook_sec=5.0, keep_video=False)
    base.update(kw)
    return type("A", (), base)()


class Resp:
    def __init__(self, code=200, text="", content=b"", headers=None):
        self.status_code = code
        self.text = text
        self.content = content if content or not text else text.encode("utf-8")
        self.headers = headers or {}

    def json(self):
        return json.loads(self.text)


class Offline(unittest.TestCase):
    def setUp(self):
        self._connect = socket.socket.connect

        def guard(sock, addr):
            raise AssertionError(f"unexpected network connect: {addr}")

        socket.socket.connect = guard

    def tearDown(self):
        socket.socket.connect = self._connect

    def test_classify_403_with_login_word_is_verification(self):
        cases = [
            (403, "<html>验证码</html> 请登录", "blocked_verification"),
            (403, "<html>login required 登录</html>", "blocked_verification"),
            (429, "", "blocked_verification"),
            (401, "please login 验证", "blocked_login"),
            (200, "<html>请登录后继续</html>", "blocked_login"),
            (500, "<html>bad gateway</html>", "error"),
        ]
        for code, text, want in cases:
            with patch.object(dy_common.S, "get", return_value=Resp(code, text)), patch("dy_common.time.sleep"):
                with self.assertRaises(dy_common.Blocked) as cm:
                    dy_common.get_json("https://example.invalid/x", {})
            self.assertEqual(cm.exception.status, want, msg=f"{code} {text[:30]}")

    def test_json_passthrough(self):
        with patch.object(dy_common.S, "get", return_value=Resp(200, '{"status_code":0,"ok":1}')), patch("dy_common.time.sleep"):
            self.assertEqual(dy_common.get_json("https://example.invalid/x", {})["ok"], 1)

    def test_page_loop_network_error_is_not_blocked(self):
        def boom(*a, **k):
            raise dy_common.Blocked("error", "ConnectionError: timed out")

        with patch("dy_collect.get_json", side_effect=boom):
            items, st = dy_collect._page_loop("https://example.invalid/comment", {}, 20)
        self.assertEqual(items, [])
        self.assertEqual(st["status"], "error")
        self.assertEqual(st["stop_reason"], "api_error")

    def test_page_loop_verification_stays_blocked(self):
        def boom(*a, **k):
            raise dy_common.Blocked("blocked_verification", "HTTP 403 10B")

        with patch("dy_collect.get_json", side_effect=boom):
            _, st = dy_collect._page_loop("https://example.invalid/comment", {}, 20)
        self.assertEqual(st["status"], "blocked_verification")
        self.assertEqual(st["stop_reason"], "blocked")

    def test_http_gate_403_is_not_login(self):
        self.assertEqual(dy_collect.http_gate("", [(403, None)], 0), "blocked_verification")
        self.assertEqual(dy_collect.http_gate("", [(429, None)], 0), "blocked_verification")
        self.assertEqual(dy_collect.http_gate("", [(401, None)], 0), "blocked_login")
        self.assertEqual(dy_collect.http_gate("验证码中间页", [(401, None)], 0), "blocked_verification")
        self.assertEqual(dy_collect.http_gate("", [], 0), "missing")
        self.assertEqual(dy_collect.http_gate("", [(200, {})], 0), "observed_empty")
        self.assertEqual(dy_collect.http_gate("", [(403, None)], 2), "available")

    def test_caption_dict_url_uses_string(self):
        body = b"WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nhello\n"
        detail = {"is_subtitled": 1, "video": {"cla_info": {"caption_infos": [
            {"url": {"url_list": ["https://example.invalid/a.vtt"]}, "lang": "zh"}]}}}
        with patch.object(dy_common.S, "get", return_value=Resp(200, content=body)) as g:
            out = dy_collect.platform_subtitle(detail)
        self.assertEqual(g.call_args.args[0], "https://example.invalid/a.vtt")
        self.assertEqual(out["status"], "available")
        self.assertEqual(out["segments"][0]["text"], "hello")

    def test_caption_string_url_unchanged(self):
        detail = {"interaction_stickers": [{"auto_video_caption_info": {"auto_captions": [
            {"url": "https://example.invalid/b.vtt", "language": "zh"}]}}]}
        self.assertEqual(dy_collect.subtitle_source(detail)[0], "https://example.invalid/b.vtt")

    def test_vid_parsing_without_network(self):
        self.assertEqual(dy_common.vid_of(VID), VID)
        self.assertEqual(dy_common.vid_of(f"看看 https://www.douyin.com/video/{VID} 完"), VID)
        self.assertEqual(dy_common.vid_of(f"https://www.iesdouyin.com/share/video/{VID}/"), VID)
        fake = Resp(302, headers={"location": f"https://www.douyin.com/video/{VID}"})
        with patch.object(dy_common.S, "get", return_value=fake) as g:
            self.assertEqual(dy_common.vid_of("https://v.douyin.com/abc/"), VID)
        self.assertTrue(g.called)
        with patch.object(dy_common.S, "get", side_effect=dy_common.requests.ConnectionError("timed out")):
            with self.assertRaises(SystemExit) as cm:
                dy_common.vid_of("https://v.douyin.com/abc/")
        self.assertIn("不是登录失败", str(cm.exception))

    def test_default_video_flags(self):
        with patch.object(sys, "argv", ["dy_collect.py", "video", VID]), patch("dy_collect.collect") as collect:
            dy_collect.main()
        args = collect.call_args.args[0]
        self.assertEqual(args.n, 200)
        self.assertFalse(args.browse)
        self.assertFalse(args.media)
        self.assertFalse(args.asr)
        self.assertFalse(args.replies)

    def test_offline_collect_happy_path(self):
        detail = {"status_code": 0, "aweme_detail": {
            "desc": "demo", "create_time": 1791210997, "duration": 12000,
            "statistics": {"digg_count": 3, "comment_count": 1, "collect_count": 0, "share_count": 0},
            "author": {"nickname": "jia"}, "music": {"title": "bgm", "author": "yi"},
            "text_extra": [{"hashtag_name": "football"}], "video": {"duration": 12000}, "is_subtitled": 0,
            "suggest_words": {"suggest_words": [
                {"scene": "comment_top_rec", "hint_text": "hint", "words": [{"word": "word1"}]},
                {"scene": "feed_bottom_rec", "hint_text": "rel", "words": [{"word": "word2"}]},
            ]},
        }}
        comments = {"status_code": 0, "total": 1, "has_more": 0, "comments": [
            {"cid": "c1", "text": "hello", "digg_count": 2, "create_time": 1791211000,
             "user": {"nickname": "u"}, "ip_label": "bj", "reply_comment_total": 0}
        ]}

        def fake_get(url, params, **k):
            if "aweme/detail" in url:
                return detail
            if "comment/list" in url:
                return comments
            raise AssertionError(url)

        with tempfile.TemporaryDirectory() as td, patch("dy_collect.get_json", side_effect=fake_get):
            dy_collect.collect(_ns(out=td))
            with open(os.path.join(td, f"douyin_{VID}", "collect.json"), encoding="utf-8") as f:
                data = json.load(f)
        self.assertEqual(data["detail"]["status"], "available")
        self.assertEqual(data["detail"]["likes"], 3)
        self.assertEqual(data["subtitle"]["status"], "missing")
        self.assertEqual(data["comments"]["status"], "available")
        self.assertEqual(data["comments"]["stop_reason"], "no_more")
        self.assertEqual(data["recommendations"]["comment_top_rec"]["status"], "available")
        self.assertEqual(data["recommendations"]["page_suggest_words"]["status"], "not_requested")
        self.assertEqual(data["media"]["status"], "not_requested")

    def test_missing_playwright_is_dependency_error(self):
        def fake_get(url, params, **k):
            if "aweme/detail" in url:
                return {"status_code": 0, "aweme_detail": {"desc": "d", "create_time": 1, "statistics": {},
                        "author": {}, "video": {}, "is_subtitled": 0}}
            return {"status_code": 0, "comments": [], "has_more": 0, "total": 0}

        with tempfile.TemporaryDirectory() as td, patch("dy_collect.get_json", side_effect=fake_get):
            dy_collect.collect(_ns(out=td, browse=True, n=1))
            with open(os.path.join(td, f"douyin_{VID}", "collect.json"), encoding="utf-8") as f:
                data = json.load(f)
        reason = data["recommendations"]["page_suggest_words"]["reason"]
        self.assertEqual(data["recommendations"]["page_suggest_words"]["status"], "error")
        self.assertTrue(reason.startswith("missing_dependency"), reason)
        self.assertNotIn("blocked_login", reason)
        self.assertEqual(data["recommendations"]["related_videos"]["status"], "error")

    def test_src_html_block_vs_empty_vs_hit(self):
        vid_page = f'<a href="https://www.douyin.com/video/{VID}">标题在这</a> 登录'
        with patch("dy_search.time.sleep"):
            with patch("dy_search.requests.get", side_effect=[Resp(403, "<html>验证码 请登录</html>")] * 3):
                found, st = dy_search.src_html("kw", "sm")
            self.assertEqual((st, found), ("blocked_verification", {}))
            with patch("dy_search.requests.get", side_effect=[Resp(401, "login")] * 3):
                _, st = dy_search.src_html("kw", "sm")
            self.assertEqual(st, "blocked_login")
            with patch("dy_search.requests.get", side_effect=[Resp(200, "<html><a>登录</a>没有结果</html>")] * 3):
                found, st = dy_search.src_html("kw", "sm")
            self.assertEqual(st, "observed_empty")
            self.assertEqual(found, {})
            with patch("dy_search.requests.get", side_effect=[Resp(403, "验证码"), Resp(200, vid_page), Resp(200, "")]):
                found, st = dy_search.src_html("kw", "sm")
            self.assertEqual(st, "available")
            self.assertIn(VID, found)

    def test_search_so_missing_playwright(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            rows, states = dy_search.search("kw", ("so",), pages=1)
        self.assertEqual(rows, [])
        self.assertEqual(states["so"]["status"], "error")
        self.assertIn("missing_dependency", buf.getvalue())
        self.assertNotIn("blocked_login", buf.getvalue())

    def test_asr_ffmpeg_failure_raises_before_model(self):
        class FF:
            returncode = 1
            stdout = b""
            stderr = b"ffmpeg failed"

        with patch("subprocess.run", return_value=FF()):
            with self.assertRaises(RuntimeError) as cm:
                media.asr("/tmp/no-such.mp4", "/tmp", "small")
        self.assertIn("ffmpeg", str(cm.exception))

    def test_download_missing_ytdlp_is_dependency_and_order_unchanged(self):
        with open(os.path.join(SCRIPTS, "media.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('("iesdouyin_share", src_share_page), ("dlpanda", src_dlpanda), ("snapany", src_snapany), ("yt-dlp", None)', src)
        with tempfile.TemporaryDirectory() as td, \
                patch.object(media, "src_share_page", side_effect=RuntimeError("分享页无 item_list")), \
                patch.object(media, "src_dlpanda", side_effect=RuntimeError("表单 token 未找到")), \
                patch.object(media, "src_snapany", side_effect=RuntimeError("40 秒内页面未出现下载链接")), \
                patch.object(media, "src_ytdlp", side_effect=FileNotFoundError("[Errno 2] No such file or directory: 'yt-dlp'")):
            path, st = media.download_video(VID, td)
        self.assertIsNone(path)
        self.assertEqual(st["status"], "error")
        self.assertEqual([t["source"] for t in st["tried"]], ["iesdouyin_share", "dlpanda", "snapany", "yt-dlp"])
        self.assertEqual(st["tried"][0]["reason"], "分享页无 item_list")
        self.assertTrue(st["tried"][3]["reason"].startswith("missing_dependency"), st["tried"][3]["reason"])

    def test_local_frames(self):
        if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
            self.skipTest("ffmpeg/ffprobe 不在 PATH")
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("未安装 Pillow")
        with tempfile.TemporaryDirectory() as td:
            video = os.path.join(td, "tiny.mp4")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=64x64:d=1",
                            "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono", "-shortest", "-c:v", "libx264",
                            "-c:a", "aac", video], check=True)
            info = media.frames(video, td, hook_sec=0.5, n=2)
        self.assertEqual(info["status"], "available")
        self.assertGreaterEqual(info["hook_frames"], 1)
        self.assertTrue(info["has_audio"])

    def test_check_and_help_do_not_use_network(self):
        script = os.path.join(SCRIPTS, "dy_collect.py")
        help_r = subprocess.run([sys.executable, script, "--help"], capture_output=True, text=True)
        self.assertEqual(help_r.returncode, 0)
        self.assertIn("check", help_r.stdout)
        self.assertIn("video", help_r.stdout)
        check_r = subprocess.run([sys.executable, script, "check"], capture_output=True, text=True)
        self.assertEqual(check_r.returncode, 0, check_r.stderr)
        data = json.loads(check_r.stdout)
        self.assertTrue(data["default_video_ready"])
        self.assertIn("playwright", data["modules"])
        self.assertIn("ffmpeg", data["binaries"])
        self.assertNotIn("http", data["note"])

    def test_missing_requests_message(self):
        helper = r'''
import sys
class Block:
    def find_spec(self, fullname, path, target=None):
        if fullname == "requests" or fullname.startswith("requests."):
            raise ModuleNotFoundError("No module named 'requests'")
        return None
sys.meta_path.insert(0, Block())
import runpy
runpy.run_path(sys.argv[1], run_name="__main__")
'''
        for name in ("dy_collect.py", "dy_search.py"):
            r = subprocess.run([sys.executable, "-c", helper, os.path.join(SCRIPTS, name), "--help"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 2, r.stderr)
            self.assertIn("不是登录失败", r.stderr)
            self.assertIn("requirements.txt", r.stderr)


if __name__ == "__main__":
    unittest.main()
