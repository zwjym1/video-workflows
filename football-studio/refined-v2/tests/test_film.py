import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image

from refined_v2.board import render_board
from refined_v2.episode import load_episode
from refined_v2.errors import EpisodeRejected
from refined_v2.film import _validate_bed, assemble, captions_from_words, load_edl, plan_timeline, subtitle_margin

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "episodes" / "bayern-20200814-mueller-open-lock-draft"


def _color_clip(path, seconds=2.0, size="1280x720"):
    subprocess.check_call(
        [
            "ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x14302a:s={size}:d={seconds}:r=25",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path),
        ]
    )


def _beep_then_silence(path):
    subprocess.check_call(
        [
            "ffmpeg", "-v", "error", "-y",
            "-f", "lavfi", "-i", "color=c=0x14302a:s=1280x720:d=4:r=25",
            "-f", "lavfi", "-i", "sine=frequency=1800:sample_rate=48000:duration=0.5",
            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono:d=3.5",
            "-filter_complex", "[1:a][2:a]concat=n=2:v=0:a=1[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
            str(path),
        ]
    )


def _mean_db(path, start, duration):
    raw = subprocess.run(
        ["ffmpeg", "-v", "info", "-ss", f"{start:.3f}", "-t", f"{duration:.3f}", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    ).stdout
    for line in raw.splitlines():
        if "mean_volume:" in line:
            token = line.split("mean_volume:")[1].strip().split()[0]
            return -99.0 if token == "-inf" else float(token)
    raise AssertionError(raw)


class FilmTest(unittest.TestCase):
    def test_audience_film_moves_the_ball_and_hides_the_stamp(self):
        episode = load_episode(EP)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "proxy.mp4"
            _color_clip(source)
            edl = {
                "version": 1,
                "master": False,
                "output": {"width": 1280, "height": 720, "fps": 25},
                "shots": [
                    {"kind": "live", "src_in": 0.0, "src_out": 0.4},
                    {"kind": "board", "board": "N2", "t0": 3.4, "t1": 5.8, "dissolve_frames": 5},
                    {"kind": "live", "src_in": 0.4, "src_out": 1.0, "dissolve_frames": 5},
                ],
                "captions": [{"start_s": 0.8, "end_s": 2.0, "text": "回做点把球交向球门这一侧。"}],
            }
            out = Path(directory) / "film.mp4"
            report = assemble(episode, edl, source, out, audience=True)
            self.assertFalse(report["master"])
            self.assertIsNone(report["audio"])
            self.assertGreater(report["subtitle_margin_px"], 40)
            self.assertFalse(report["upscaled"])
            board_states = [state for state in report["states"] if state.get("kind") == "board"]
            progresses = [state["route_progress"].get("ball_96-ball_102", 0) for state in board_states]
            self.assertLess(progresses[0], 0.2)
            self.assertGreater(progresses[-1], 0.8)
            self.assertTrue(any(state.get("kind") == "dissolve" for state in report["states"]))
            self.assertTrue(all(state.get("stamp_burned") is False for state in board_states))
            self.assertNotIn("无号码", json.dumps([state.get("labels") for state in board_states], ensure_ascii=False))
            early = next(state for state in board_states if state["route_progress"].get("ball_96-ball_102", 0) < 0.05)
            late = next(state for state in board_states if state["route_progress"].get("ball_96-ball_102", 0) > 0.8)
            self.assertNotEqual(early["t"], late["t"])
            decoded = Path(directory) / "late.png"
            subprocess.check_call(
                ["ffmpeg", "-v", "error", "-y", "-ss", f"{late['output_s']:.3f}", "-i", str(out), "-frames:v", "1", str(decoded)]
            )
            with Image.open(decoded) as frame:
                self.assertEqual(frame.size, (1280, 720))

    def test_caption_cannot_invent_a_shirt_number(self):
        edl = load_edl(EP / "audience_example.edl.json")
        self.assertFalse(edl["master"])
        episode = load_episode(EP)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "proxy.mp4"
            _color_clip(source, 1.0)
            edl = {
                "version": 1,
                "output": {"width": 1280, "height": 720, "fps": 25},
                "shots": [{"kind": "live", "src_in": 0.0, "src_out": 0.4}],
                "captions": [{"start_s": 0.0, "end_s": 0.3, "text": "射门帧上是25号"}],
            }
            with self.assertRaises(EpisodeRejected):
                assemble(episode, edl, source, Path(directory) / "no.mp4")

    def test_short_caption_is_given_a_readable_window(self):
        cues = captions_from_words(
            [{"id": "N00", "words": [
                {"text": "先", "offset": 0.08, "duration": 0.2},
                {"text": "看", "offset": 0.32, "duration": 0.16},
                {"text": "这个球", "offset": 0.5, "duration": 0.2},
                {"text": "。", "offset": 0.7, "duration": 0.1},
                {"text": "左边路", "offset": 1.2, "duration": 0.4},
                {"text": "。", "offset": 1.6, "duration": 0.1},
            ]}],
            {"N00": 0.0},
        )
        self.assertGreaterEqual(cues[0]["end_s"] - cues[0]["start_s"], 0.8)
        self.assertIn("先", cues[0]["text"])
        self.assertNotIn("25", cues[0]["text"])

    def test_present_1080_comes_from_the_supersample(self):
        episode = load_episode(EP)
        board = episode["boards"][0]
        image, state = render_board(episode, board, 1.0, show_stamp=False, present=(1920, 1080))
        self.assertEqual(image.size, (1920, 1080))
        self.assertTrue(state["present_from_supersample"])
        self.assertFalse(state["upscaled"])

    def test_margin_matches_the_1080_rule(self):
        self.assertGreater(subtitle_margin(1080), 60)
        self.assertGreater(subtitle_margin(720), 40)

    def test_live_audio_follows_the_edl_window_not_file_zero(self):
        episode = load_episode(EP)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "beep.mp4"
            _beep_then_silence(source)
            edl = {
                "version": 1,
                "output": {"width": 1280, "height": 720, "fps": 25},
                "audio": {"source_gain_db": -6},
                "shots": [{"kind": "live", "src_in": 1.2, "src_out": 1.7}],
            }
            out = Path(directory) / "quiet.mp4"
            assemble(episode, edl, source, out)
            quiet = _mean_db(out, 0.0, 0.35)
            self.assertLess(quiet, -35)
            loud = {
                "version": 1,
                "output": {"width": 1280, "height": 720, "fps": 25},
                "audio": {"source_gain_db": -6},
                "shots": [{"kind": "live", "src_in": 0.0, "src_out": 0.45}],
            }
            loud_out = Path(directory) / "loud.mp4"
            assemble(episode, loud, source, loud_out)
            heard = _mean_db(loud_out, 0.0, 0.3)
            self.assertGreater(heard, quiet + 8)

    def test_board_bed_needs_authorization_and_avoids_the_centre_circle(self):
        episode = load_episode(EP)
        forbidden = episode["forbidden_clip_s"]
        self.assertEqual(forbidden, [[6.0, 8.0]])
        with self.assertRaises(EpisodeRejected) as caught:
            _validate_bed({"audio": {"board_bed": {"src_in": 1.0, "src_out": 1.4}}}, forbidden)
        self.assertIn("authorized", str(caught.exception))
        with self.assertRaises(EpisodeRejected) as caught:
            _validate_bed(
                {"audio": {"board_bed": {"authorized": True, "src_in": 6.2, "src_out": 7.4}}},
                forbidden,
            )
        self.assertEqual(caught.exception.code, "continuity")
        with self.assertRaises(EpisodeRejected):
            plan_timeline(episode, {
                "version": 1,
                "output": {"fps": 25},
                "shots": [{"kind": "live", "src_in": 6.4, "src_out": 7.2}],
            })

    def test_v4_timeline_is_the_full_length_and_skips_the_centre_circle(self):
        episode = load_episode(EP)
        edl = load_edl(EP / "v4_audience.edl.json")
        frames, placements = plan_timeline(episode, edl)
        self.assertEqual(frames, 1346)
        self.assertAlmostEqual(frames / 25, 53.84, places=2)
        self.assertFalse(edl["master"])
        lives = [item for item in placements if item["kind"] == "live"]
        self.assertTrue(lives)
        self.assertTrue(all(item["src_in"] >= 9 for item in lives))
        self.assertEqual(sum(1 for item in placements if item["kind"] == "board"), 3)

    def test_long_1080_stream_stays_under_a_gigabyte(self):
        episode = load_episode(EP)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "hd.mp4"
            _color_clip(source, 20, "1920x1080")
            edl = {
                "version": 1,
                "output": {"width": 1920, "height": 1080, "fps": 25},
                "shots": [
                    {"kind": "live", "src_in": 9.0, "src_out": 17.0},
                    {"kind": "board", "board": "R1", "t0": 0.0, "t1": 0.4, "dissolve_frames": 5},
                    {"kind": "live", "src_in": 17.0, "src_out": 19.0, "dissolve_frames": 5},
                ],
            }
            out = Path(directory) / "out.mp4"
            report = assemble(episode, edl, source, out)
            self.assertEqual(report["width"], 1920)
            self.assertEqual(report["frames"], 250)
            self.assertLess(report["peak_rss_kib"], 800 * 1024, msg=str(report["peak_rss_kib"]))
            self.assertFalse(report["master"])

    def test_qc_stamp_is_absent_on_the_audience_board(self):
        episode = load_episode(EP)
        board = next(item for item in episode["boards"] if item["id"] == "N2")
        audience, _ = render_board(episode, board, 2.4, show_stamp=False)
        qc, _ = render_board(episode, board, 2.4, show_stamp=True)
        box = (40, 610, 520, 660)
        audience_crop = list(audience.crop(box).get_flattened_data())
        qc_crop = list(qc.crop(box).get_flattened_data())
        self.assertNotEqual(audience_crop, qc_crop)


if __name__ == "__main__":
    unittest.main()
