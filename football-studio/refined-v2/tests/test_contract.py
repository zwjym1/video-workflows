import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image

from refined_v2.arsenal_fixture import build
from refined_v2.draw import ease
from refined_v2.episode import _flip_uvs, compile_episode, load_episode
from refined_v2.errors import EpisodeRejected
from refined_v2.legacy import find_legacy

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "episodes" / "sample-not-a-match" / "episode.json"
REGRESSION = ROOT / "episodes" / "arsenal-2018-regression" / "episode.json"
VENDOR = ROOT / "vendor" / "render_v2.py"


def sample_data():
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def compile_any(data):
    return compile_episode(data, base_dir=SAMPLE.parent)


class ContractTest(unittest.TestCase):
    def test_regression_file_matches_fixture_builder(self):
        self.assertEqual(json.loads(REGRESSION.read_text(encoding="utf-8")), build())

    def test_vendor_motion_literals_are_in_the_regression(self):
        source = VENDOR.read_text(encoding="utf-8").replace(" ", "")
        for literal in ("[72,94]", "[65,93]", "[49,66]", "[43,25]", "[34,8]", "[18,56]", "[10,73]", "[8,68]"):
            self.assertIn(literal, source)
        data = json.loads(REGRESSION.read_text(encoding="utf-8"))
        motions = {board["id"]: board["motions"] for board in data["boards"]}
        self.assertEqual(motions["Q1"][0]["frm"], [72, 94])
        self.assertEqual(motions["Q2"][0]["to"], [43, 25])
        self.assertEqual(motions["Q5"][0]["to"], [8, 68])

    def test_q4_does_not_invent_l6(self):
        source = VENDOR.read_text(encoding="utf-8")
        self.assertIn("b['pos']['L6']", source)
        from refined_v2.arsenal_fixture import RELATIONS

        relations = json.loads(RELATIONS.read_text(encoding="utf-8"))
        b5 = next(board for board in relations["boards"] if board["id"] == "B5")
        self.assertNotIn("L6", {node["id"] for node in b5["nodes"]})
        q4 = next(board for board in json.loads(REGRESSION.read_text(encoding="utf-8"))["boards"] if board["id"] == "Q4")
        self.assertNotIn("L6", {node["id"] for node in q4["nodes"]})
        self.assertIn("不补", q4["notes"])

    def test_renderer_source_has_no_board_relations_fallback(self):
        for name in ("episode.py", "board.py", "__main__.py"):
            text = (ROOT / "refined_v2" / name).read_text(encoding="utf-8")
            self.assertNotIn("BOARD_RELATIONS", text)
            self.assertNotIn("arsenal_fixture", text)
            self.assertNotIn("1080p", text)
            self.assertNotIn("高清修复", text)

    def test_missing_episode_refuses(self):
        with self.assertRaises(EpisodeRejected) as caught:
            load_episode(ROOT / "episodes" / "does-not-exist")
        self.assertEqual(caught.exception.code, "missing_episode")
        self.assertIn("不会改用", caught.exception.message)

    def test_empty_boards_do_not_fallback(self):
        data = sample_data()
        data["boards"] = []
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "geometry")

    def test_sample_file_has_no_legacy_identity(self):
        self.assertEqual(find_legacy(SAMPLE.read_text(encoding="utf-8")), [])

    def test_legacy_label_is_rejected(self):
        data = sample_data()
        data["boards"][0]["labels"][0]["text"] = "托雷拉接应"
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "legacy_leak")

    def test_legacy_id_is_rejected(self):
        data = sample_data()
        data["boards"][0]["nodes"][0]["id"] = "A34"
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "legacy_leak")

    def test_coordinate_range(self):
        for value in (120, -0.01, float("nan")):
            data = sample_data()
            data["boards"][0]["nodes"][0]["uv"] = [value, 40]
            with self.assertRaises(EpisodeRejected) as caught:
                compile_any(data)
            self.assertIn(caught.exception.code, ("geometry_range", "timeline"))
        data = sample_data()
        data["boards"][0]["nodes"][0]["uv"] = [0, 100]
        data["boards"][0]["routes"][0]["intent"] = "keep"
        compile_any(data)

    def test_timeline_and_arrow_rules(self):
        data = sample_data()
        data["boards"][0]["motions"][0]["t1"] = 0.1
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "timeline")
        data = sample_data()
        data["boards"][0]["routes"][0]["ids"] = ["P7", "NOBODY"]
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "arrow")
        data = sample_data()
        data["boards"][0]["nodes"][1]["uv"] = data["boards"][0]["nodes"][0]["uv"]
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "arrow")

    def test_forward_rule_uses_attack_left_after_one_flip(self):
        data = sample_data()
        data["boards"][0]["routes"][0]["intent"] = "forward"
        data["boards"][0]["nodes"][0]["uv"] = [40, 32]
        data["boards"][0]["nodes"][1]["uv"] = [70, 58]
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "direction")
        right = sample_data()
        right["input_attack"] = "right"
        right["boards"][0]["nodes"][0]["uv"] = [30, 32]
        right["boards"][0]["nodes"][1]["uv"] = [55, 58]
        right["boards"][0]["motions"][0]["frm"] = [20, 28]
        right["boards"][0]["motions"][0]["to"] = [30, 32]
        right["boards"][0]["motions"][1]["frm"] = [40, 36]
        right["boards"][0]["motions"][1]["to"] = [34, 44]
        right["boards"][0]["annotations"] = [
            {"type": "segment", "frm": [20, 50], "to": [40, 50], "t0": 0.16, "t1": 0.56, "kind": "def"}
        ]
        right["boards"][0]["routes"][0]["intent"] = "forward"
        compiled = compile_any(right)
        board = compiled["boards"][0]
        self.assertEqual(compiled["orientation"]["transform"], "u' = 100 - u")
        self.assertGreaterEqual(len(compiled["orientation"]["paths"]), 7)
        self.assertEqual(board["nodes"][0]["uv"][0], 70)
        self.assertEqual(board["nodes"][1]["uv"][0], 45)
        self.assertEqual(board["motions"][0]["frm"][0], 80)
        self.assertEqual(board["annotations"][0]["frm"], [80, 50])
        self.assertEqual(board["annotations"][0]["to"], [60, 50])
        self.assertEqual(board["routes"][0]["intent"], "forward")

    def test_flip_does_not_touch_pixel_feet(self):
        node = {"uv": [10, 20], "frm": [1, 2], "foot_px": [10, 20], "offset": [8, -4]}
        found = []
        _flip_uvs(node, "$", found)
        self.assertEqual(node["uv"], [90, 20])
        self.assertEqual(node["frm"], [99, 2])
        self.assertEqual(node["foot_px"], [10, 20])
        self.assertEqual(node["offset"], [8, -4])
        self.assertEqual(found, ["$.uv", "$.frm"])

    def test_word_clock_resolves_and_missing_word_refuses(self):
        data = sample_data()
        data["timing_basis"] = "word_clock"
        data["clock"] = {
            "scenes": {
                "S": {
                    "output_start_s": 10,
                    "words": [
                        {"text": "样", "offset": 0.0, "duration": 0.25},
                        {"text": "例", "offset": 0.25, "duration": 0.25},
                        {"text": "接", "offset": 0.5, "duration": 0.25},
                        {"text": "点", "offset": 0.75, "duration": 0.25},
                    ],
                }
            }
        }
        board = data["boards"][0]
        board["scene"] = "S"
        board["output_start_s"] = 10
        board["nodes"][0]["appear_s"] = {"word": "样例"}
        board["nodes"][1]["appear_s"] = {"word": "接点"}
        compiled = compile_any(data)
        nodes = {node["id"]: node for node in compiled["boards"][0]["nodes"]}
        self.assertEqual(nodes["P7"]["appear_s"], 0)
        # 10.5 秒按 25fps 用 Python round（半数到偶数）落到 10.48，板上就是 0.48。
        self.assertEqual(nodes["P11"]["appear_s"], 0.48)
        board["nodes"][0]["appear_s"] = {"word": "不存在"}
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "word_clock")
        plain = sample_data()
        plain["boards"][0]["nodes"][0]["appear_s"] = {"word": "样例"}
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(plain)
        self.assertEqual(caught.exception.code, "word_clock")

    def test_easing_is_not_linear_at_the_quarter(self):
        self.assertAlmostEqual(ease(0.25), 0.103515625)
        self.assertNotAlmostEqual(ease(0.25), 0.25)

    def test_q4_order_rule_rejects_an_early_run(self):
        data = json.loads(REGRESSION.read_text(encoding="utf-8"))
        q4 = next(board for board in data["boards"] if board["id"] == "Q4")
        motion = next(item for item in q4["motions"] if item["id"] == "A10")
        motion["t0"] = 1.4
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "order_rule")
        self.assertIn("拒绝", caught.exception.message)

    def test_evidence_locked_without_frames_or_pointers_refuses(self):
        data = sample_data()
        data["episode_id"] = "future-match"
        data["claim"] = "evidence_locked"
        data["statement"] = "证据还没到，不能当真实板。"
        data["evidence_frames"] = []
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "evidence")
        with tempfile.TemporaryDirectory() as directory:
            frame = Path(directory) / "frame.png"
            Image.new("RGB", (40, 30), (20, 40, 30)).save(frame)
            data["evidence_frames"] = [{"id": "f", "path": str(frame), "native_size": [40, 30]}]
            with self.assertRaises(EpisodeRejected) as caught:
                compile_episode(data, base_dir=directory)
            self.assertEqual(caught.exception.code, "evidence")
            self.assertIn("不会装成真实", caught.exception.message)

    def test_evidence_locked_accepts_only_pointed_coordinates(self):
        with tempfile.TemporaryDirectory() as directory:
            frame = Path(directory) / "frame.png"
            Image.new("RGB", (40, 30), (20, 40, 30)).save(frame)
            data = {
                "episode_id": "future-match",
                "claim": "evidence_locked",
                "statement": "证据指针已齐，仍不是最终发布片。",
                "timing_basis": "board_local_seconds",
                "input_attack": "left",
                "evidence_frames": [{"id": "f", "path": "frame.png", "native_size": [40, 30]}],
                "boards": [
                    {
                        "id": "S1",
                        "question": "证据稿问句",
                        "duration_s": 2,
                        "nodes": [
                            {"id": "P7", "number": "7", "team": "attack", "uv": [60, 40], "focus": True, "appear_s": 0.2, "evidence_id": "f"},
                            {"id": "P11", "number": "11", "team": "attack", "uv": [40, 55], "focus": True, "appear_s": 0.4, "evidence_id": "f"},
                        ],
                        "routes": [{"ids": ["P7", "P11"], "t0": 0.6, "t1": 1.2, "intent": "forward"}],
                    }
                ],
            }
            compiled = compile_episode(data, base_dir=directory)
            self.assertTrue(compiled["stamp"].startswith("证据稿"))
            self.assertEqual(find_legacy(json.dumps(compiled, ensure_ascii=False)), [])
            data["evidence_frames"][0]["native_size"] = [1920, 1080]
            with self.assertRaises(EpisodeRejected) as caught:
                compile_episode(data, base_dir=directory)
            self.assertEqual(caught.exception.code, "evidence")

    def test_moving_ring_and_maskless_ring_refuse(self):
        data = sample_data()
        data["boards"][0]["still_marks"] = [{"moving": True, "foot_px": [10, 10], "mask_polygon": [[1, 1], [2, 2], [1, 2]]}]
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "mask")
        data = sample_data()
        data["boards"][0]["still_marks"] = [{"foot_px": [10, 10]}]
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "mask")

    def test_regression_claim_cannot_be_renamed(self):
        data = json.loads(REGRESSION.read_text(encoding="utf-8"))
        data["episode_id"] = "muller-4min"
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "claim")

    def test_unknown_claim_refuses(self):
        data = sample_data()
        data["claim"] = "real_muller_board"
        with self.assertRaises(EpisodeRejected) as caught:
            compile_any(data)
        self.assertEqual(caught.exception.code, "claim")


if __name__ == "__main__":
    unittest.main()
