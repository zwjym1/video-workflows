import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from refined_v2.bayern_lock_fixture import build
from refined_v2.board import render_board
from refined_v2.episode import compile_episode
from refined_v2.errors import EpisodeRejected
from refined_v2.lock_map import CAMERAS, to_uv

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "episodes" / "bayern-20200814-mueller-open-lock-draft" / "episode.json"


class LockDraftTest(unittest.TestCase):
    def test_file_matches_builder(self):
        self.assertEqual(json.loads(EP.read_text(encoding="utf-8")), build())

    def test_number_five_was_moved_off_the_goal_line(self):
        board = next(item for item in build()["boards"] if item["id"] == "N2")
        five = next(node for node in board["nodes"] if node["id"] == "C5")
        self.assertGreater(five["source_px"][0], 300)
        self.assertNotEqual(five["source_px"], [150, 720])
        self.assertEqual(five["source_canvas"], [1280, 720])

    def test_same_camera_formula_and_eighteen_stays_out_of_the_layoff(self):
        data = build()
        for board in data["boards"]:
            camera = CAMERAS[board["camera"]]
            for node in board["nodes"]:
                self.assertEqual(node["uv"], to_uv(*node["source_px"], camera))
            for route in board.get("routes") or []:
                for extra in board.get("extra_points") or []:
                    if extra["id"] in route["ids"]:
                        self.assertEqual(extra["uv"], extra["uv"])
        live = next(board for board in data["boards"] if board["id"] == "N2")
        self.assertNotIn("18", {node["number"] for node in live["nodes"]})
        self.assertNotIn("9", {node["number"] for node in live["nodes"]})
        self.assertTrue(all(node["id"] != "K18" for node in live["nodes"]))
        replay = next(board for board in data["boards"] if board["id"] == "R3")
        self.assertTrue(all("K18" not in route["ids"] for route in replay.get("routes") or []))
        back = CAMERAS["behind_goal_attack_bottom"]
        self.assertLess(to_uv(680, 620, back)[0], to_uv(370, 380, back)[0])

    def test_verified_schematic_rejects_a_padded_runtime_and_the_kickoff(self):
        compiled = compile_episode(build(), base_dir=EP.parent)
        self.assertTrue(compiled["geometry_verified"])
        self.assertIn("俯视示意", compiled["stamp"])
        self.assertIn("非测绘", compiled["stamp"])
        self.assertAlmostEqual(sum(item["duration_s"] for item in build()["segments"]), 8.8)
        data = build()
        data["segments"][0]["duration_s"] = 84
        with self.assertRaises(EpisodeRejected) as caught:
            compile_episode(data, base_dir=EP.parent)
        self.assertEqual(caught.exception.code, "continuity")
        data = build()
        data["boards"][1]["source_s"] = [56, 61.5]
        with self.assertRaises(EpisodeRejected) as caught:
            compile_episode(data, base_dir=EP.parent)
        self.assertEqual(caught.exception.code, "continuity")
        data = build()
        data["boards"][1]["nodes"][0]["number"] = "25"
        data["boards"][1]["nodes"][0]["number_lock"] = "clip_9p6"
        with self.assertRaises(EpisodeRejected) as caught:
            compile_episode(data, base_dir=EP.parent)
        self.assertEqual(caught.exception.code, "identity")
        data = build()
        data["pitch_calibration"] = "surveyed_homography"
        with self.assertRaises(EpisodeRejected) as caught:
            compile_episode(data, base_dir=EP.parent)
        self.assertEqual(caught.exception.code, "evidence")

    def test_render_side_by_side_inputs_exist(self):
        compiled = compile_episode(build(), base_dir=EP.parent)
        board = next(item for item in compiled["boards"] if item["id"] == "N2")
        image, state = render_board(compiled, board, 3.6)
        self.assertEqual(image.size, (1280, 720))
        self.assertTrue(state["font"]["spec_match"])
        self.assertIsNone(state["numbers"]["Kshot"])
        self.assertEqual(state["numbers"]["C5"], "5")
        for frame in compiled["evidence_frames"].values():
            self.assertTrue(Path(frame["path"]).is_file())
            self.assertEqual(frame["native_size"], [1280, 720])


if __name__ == "__main__":
    unittest.main()
