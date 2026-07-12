import json
import unittest
from pathlib import Path


DATA = Path(__file__).resolve().parents[1] / "data" / "sound_correspondences.json"


class SoundCorrespondenceDataTests(unittest.TestCase):
    def test_aggregate_snapshot_is_consistent_and_contains_no_lexical_records(self):
        payload = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(set(payload["order"]), set(payload["languages"]))
        self.assertIn("ś", payload["uga_order"])
        self.assertNotIn("s2", payload["uga_order"])

        for code, language in payload["languages"].items():
            self.assertGreater(language["n"], 0, code)
            targets = set(language["tgt_order"]) | {"-"}
            sources = set(payload["uga_order"]) | {"-"}
            for edge in language["edges"]:
                self.assertEqual(set(edge), {"u", "h", "type", "count"})
                self.assertIn(edge["u"], sources)
                self.assertIn(edge["h"], targets)
                self.assertIn(edge["type"], {"id", "merge", "ins", "del"})
                self.assertGreater(edge["count"], 0)

    def test_renderer_accepts_every_language_with_or_without_gaps(self):
        from data.workshop_helpers import sound_correspondence_figure

        payload = json.loads(DATA.read_text(encoding="utf-8"))
        for code in payload["order"]:
            for show_gaps in (False, True):
                figure = sound_correspondence_figure(code, show_gaps=show_gaps)
                self.assertTrue(figure.data, (code, show_gaps))


if __name__ == "__main__":
    unittest.main()
