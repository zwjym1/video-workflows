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
from refined_v2.film import assemble, captions_from_words, load_edl, subtitle_margin

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "episodes" / "bayern-20200814-mueller-open-lock-draft"


def _color_clip(path, seconds=2.0):
    subprocess.check_call(
        [
            "ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x14302a:s=1280x720:d={seconds}:r=25",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path),
        ]
    )


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
            self.assertEqual(Image.open(decoded).size, (1280, 720))

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
