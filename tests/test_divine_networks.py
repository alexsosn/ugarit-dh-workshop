import tempfile
import unittest
from pathlib import Path

from workshop_tools.divine_networks import (
    build_divine_name_graph,
    edge_evidence,
    filter_divine_name_graph,
    find_maximal_cliques,
    graph_sensitivity,
    load_baal_cycle,
    local_name_windows,
    show_divine_name_network,
)


def _row(token_id: int, surface: str, pos: str, gloss: str) -> str:
    return "\t".join([
        str(token_id), surface, surface, surface, surface, pos, gloss, "",
    ])


class DivineNetworkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        fixtures = {
            "1.1": [
                "# KTU 1.1 I:1",
                _row(1, "bˤl", "DN m.", "fallback Baal"),
                "# KTU 1.1 I:3",
                _row(2, "ym", "DN m.", "fallback Sea"),
                "# KTU 1.1 I:4",
                _row(3, "ˤnt", "DN f.", "fallback Anat"),
            ],
            "1.2": [
                "# KTU 1.2 I:1",
                _row(4, "nhr", "DN m.", "River"),
            ],
        }
        for number in ("1.1", "1.2", "1.3", "1.4", "1.5", "1.6"):
            lines = fixtures.get(number, [
                f"# KTU {number} I:1",
                _row(10, "w", "conj.", "and"),
            ])
            (self.root / f"KTU {number}.tsv").write_text(
                "\n".join(lines) + "\n", encoding="utf-8"
            )
        self.overrides = self.root / "onomastic.tsv"
        self.overrides.write_text(
            "dulat\tPOS\tgloss\n"
            "bʕl (II)\tDN m.\tBaal from onomastic glossary\n"
            "ym\tDN m.\tYammu from onomastic glossary\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_loads_normalizes_and_documents_names(self):
        corpus = load_baal_cycle(
            data_dir=self.root, overrides_path=self.overrides
        )
        self.assertEqual(len(corpus.occurrences), 4)
        self.assertEqual(corpus.name_summary.loc["ym", "mentions"], 2)
        self.assertEqual(
            corpus.name_summary.loc["bˤl", "description"],
            "Baal from onomastic glossary",
        )
        self.assertIn("nhr", set(corpus.normalization_changes["surface"]))

    def test_graph_cliques_provenance_and_renderer(self):
        corpus = load_baal_cycle(
            data_dir=self.root, overrides_path=self.overrides
        )
        graph = build_divine_name_graph(corpus, max_distance=3)
        self.assertTrue(graph.has_edge("bˤl", "ym"))
        self.assertEqual(len(edge_evidence(graph, "bˤl", "ym")), 1)
        strict = filter_divine_name_graph(graph, min_tablets=2)
        self.assertFalse(strict.has_edge("bˤl", "ym"))

        cliques = find_maximal_cliques(
            graph, min_mentions=1, min_size=3
        )
        self.assertEqual(cliques.iloc[0]["members"], ("bˤl", "ym", "ˤnt"))

        local = local_name_windows(
            corpus, max_distance=3, min_mentions=1, min_size=3
        )
        self.assertEqual(local.iloc[0]["size"], 3)

        sensitivity = graph_sensitivity(
            corpus, distances=(0, 3), min_mentions=1
        )
        self.assertGreater(
            sensitivity.iloc[1]["edges"], sensitivity.iloc[0]["edges"]
        )

        rendered = show_divine_name_network(
            graph, min_mentions=1, min_weight=1
        ).data
        self.assertIn("vis-network", rendered)
        self.assertIn("dragNodes", rendered)
        self.assertIn("background:#fff", rendered)


if __name__ == "__main__":
    unittest.main()
