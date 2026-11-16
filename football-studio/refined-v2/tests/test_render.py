import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image

from refined_v2.board import render_board
from refined_v2.episode import load_episode
from refined_v2.legacy import find_legacy
from refined_v2.qc import side_by_side

ROOT = Path(__file__).resolve().parents[1]


class RenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = load_episode(ROOT / "episodes" / "sample-not-a-match")
        cls.regression = load_episode(ROOT / "episodes" / "arsenal-2018-regression")

    def test_sample_frame_has_no_legacy_and_is_native(self):
        board = self.sample["boards"][0]
        image, state = render_board(self.sample, board, 2.6)
        self.assertEqual(image.size, (1280, 720))
        self.assertFalse(state["upscaled"])
        self.assertEqual(state["supersample"], 2)
        self.assertIsNone(state["audio"])
        self.assertIn("样例", state["stamp"])
        self.assertIn("不是2020-08-14穆勒回合", state["stamp"])
        self.assertEqual(find_legacy(json.dumps(state, ensure_ascii=False)), [])
        self.assertEqual(set(state["ids"]), {"P7", "P11", "D4", "D5", "D8"})
        self.assertIn("D8", state["visible_ids"])
        self.assertFalse(state["font"]["spec_match"])
        self.assertIn("不是", state["font"]["note"])

    def test_sample_render_does_not_open_the_arsenal_package(self):
        opened = []
        real_open = open

        def guard(file, *args, **kwargs):
            opened.append(str(file))
            if "arsenal-2018-regression" in str(file) or "BOARD_RELATIONS" in str(file):
                raise AssertionError(file)
            return real_open(file, *args, **kwargs)

        import builtins

        builtins.open = guard
        try:
            image, state = render_board(self.sample, self.sample["boards"][0], 1.0)
        finally:
            builtins.open = real_open
        self.assertEqual(image.size, (1280, 720))
        self.assertNotIn("A34", state["ids"])

    def test_route_and_run_follow_the_clock(self):
        board = self.sample["boards"][0]
        _, early = render_board(self.sample, board, 0.4)
        _, late = render_board(self.sample, board, 2.6)
        self.assertEqual(early["route_progress"]["P7-P11"], 0)
        self.assertEqual(late["route_progress"]["P7-P11"], 1)
        _, quarter = render_board(self.sample, board, 0.51)
        self.assertAlmostEqual(quarter["motion_progress"]["P7"], 0.10352, places=3)
        self.assertLess(quarter["motion_progress"]["P7"], 0.2)

    def test_ball_pixels_appear_only_after_the_route_starts(self):
        board = self.sample["boards"][0]
        before, _ = render_board(self.sample, board, 0.4)
        after, _ = render_board(self.sample, board, 2.6)

        def yellow(image):
            count = 0
            for red, green, blue in image.get_flattened_data():
                if red > 200 and green > 170 and blue < 150:
                    count += 1
            return count

        self.assertGreater(yellow(after), yellow(before) + 30)

    def test_regression_q4_keeps_its_identity_and_size(self):
        board = next(item for item in self.regression["boards"] if item["id"] == "Q4")
        early, early_state = render_board(self.regression, board, 1.0)
        late, late_state = render_board(self.regression, board, 4.4)
        self.assertEqual(early.size, (1280, 720))
        self.assertEqual(late.size, (1280, 720))
        self.assertIn("回归", early_state["stamp"])
        self.assertIn("非新场次", early_state["stamp"])
        self.assertEqual(early_state["route_progress"]["A2-A10_origin-A9"], 0)
        self.assertEqual(late_state["route_progress"]["A9-A10_next"], 1)
        self.assertEqual(late_state["motion_progress"]["A10"], 1)
        self.assertIn("A10", early_state["visible_ids"])
        self.assertLess(early_state["motion_progress"]["A10"], 0.01)

    def test_side_by_side_never_upscales(self):
        image, _ = render_board(self.sample, self.sample["boards"][0], 2.6)
        evidence = Image.new("RGB", (480, 270), (30, 50, 40))
        sheet, meta = side_by_side(image, evidence, "版式检查")
        self.assertEqual(sheet.size, (1280, 720))
        self.assertEqual(meta["evidence_native"], [480, 270])
        self.assertEqual(meta["evidence_drawn"], [480, 270])
        self.assertFalse(meta["upscaled"])
        wide = Image.new("RGB", (1920, 1080), (30, 50, 40))
        _, meta = side_by_side(image, wide, "版式检查")
        self.assertLess(meta["evidence_drawn"][0], 1920)
        self.assertFalse(meta["upscaled"])


if __name__ == "__main__":
    unittest.main()
