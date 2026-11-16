import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from refined_v2.bayern_lock_fixture import build
from refined_v2.board import render_board
from refined_v2.episode import compile_episode
from refined_v2.errors import EpisodeRejected
from refined_v2.lock_map import CAMERAS, attack_left_pixel, to_uv

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "episodes" / "bayern-20200814-mueller-open-lock-draft" / "episode.json"
LOCK = EP.parent / "FRAME_LOCK_HD.json"


class LockDraftTest(unittest.TestCase):
    def test_file_matches_builder_and_pixels_come_from_the_lock(self):
        data = json.loads(EP.read_text(encoding="utf-8"))
        self.assertEqual(data, build())
        raw = LOCK.read_text(encoding="utf-8")
        for board in data["boards"]:
            for node in board["nodes"]:
                x, y = node["source_px"]
                self.assertIn(f"{x}", raw)
                self.assertIn(f"{y}", raw)

    def test_same_camera_formula_for_every_point(self):
        data = build()
        for board in data["boards"]:
            camera = CAMERAS[board["camera"]]
            for node in board["nodes"]:
                self.assertEqual(node["uv"], to_uv(node["source_px"][0], node["source_px"][1], camera))
        back = CAMERAS["behind_goal_attack_bottom"]
        closer = to_uv(540, 800, back)
        farther = to_uv(540, 200, back)
        self.assertLess(closer[0], farther[0])
        ball = attack_left_pixel(750, 370, back)
        player = attack_left_pixel(750, 400, back)
        self.assertLess(player[0], ball[0])

    def test_numbers_follow_the_lock_and_kickoff_cannot_join(self):
        compiled = compile_episode(build())
        self.assertFalse(compiled["geometry_verified"])
        self.assertIn("未见源帧", compiled["stamp"])
        self.assertIn("未核验", compiled["stamp"])
        by_id = {board["id"]: board for board in compiled["boards"]}
        self.assertEqual({node["number"] for node in by_id["N2"]["nodes"] if node["number"]}, {"20", "5", "2", "3"})
        self.assertEqual({node["number"] for node in by_id["R1"]["nodes"] if node["number"]}, {"14"})
        self.assertEqual({node["number"] for node in by_id["R3"]["nodes"] if node["number"]}, {"9", "21", "18"})
        numbers = [node["number"] for board in compiled["boards"] for node in board["nodes"]]
        self.assertNotIn("25", numbers)
        data = build()
        data["boards"][1]["nodes"][0]["number"] = "9"
        data["boards"][1]["nodes"][0]["number_lock"] = "B2_box_live_t059"
        with self.assertRaises(EpisodeRejected) as caught:
            compile_episode(data)
        self.assertEqual(caught.exception.code, "identity")
        data = build()
        data["boards"][2]["nodes"][4]["number"] = "25"
        data["boards"][2]["nodes"][4]["number_lock"] = "B3_behind_goal_t075_t077"
        with self.assertRaises(EpisodeRejected) as caught:
            compile_episode(data)
        self.assertEqual(caught.exception.code, "identity")
        data = build()
        data["boards"][1]["source_s"] = [56, 61.5]
        with self.assertRaises(EpisodeRejected) as caught:
            compile_episode(data)
        self.assertEqual(caught.exception.code, "continuity")
        data = build()
        data["geometry_verified"] = True
        with self.assertRaises(EpisodeRejected) as caught:
            compile_episode(data)
        self.assertEqual(caught.exception.code, "evidence")

    def test_render_keeps_the_unverified_stamp_and_blank_shirts(self):
        compiled = compile_episode(build())
        board = next(item for item in compiled["boards"] if item["id"] == "N2")
        image, state = render_board(compiled, board, 3.6)
        self.assertEqual(image.size, (1280, 720))
        self.assertIn("几何未核验", state["stamp"])
        self.assertNotIn("9", state["numbers"].values())
        self.assertNotIn("25", state["numbers"].values())
        self.assertIn(None, state["numbers"].values())
        self.assertFalse(state["upscaled"])


if __name__ == "__main__":
    unittest.main()
