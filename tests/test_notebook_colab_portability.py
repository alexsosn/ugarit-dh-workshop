import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
INTERNAL_IMPORT = re.compile(
    r"(?:from|import)\s+workshop_tools|[\"']\.\./(?:data|images|docs)/"
)
REPO_PATH = re.compile(
    r"[\"'](?P<path>\.\./(?:data|images|docs|workshop_tools)/[^\"']+)[\"']"
)


class NotebookColabPortabilityTests(unittest.TestCase):
    def _cells(self, path: Path):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        return [
            (index, "".join(cell.get("source", [])))
            for index, cell in enumerate(notebook["cells"])
            if cell["cell_type"] == "code"
        ]

    def test_every_notebook_bootstraps_repository_before_internal_imports(self):
        for path in sorted(NOTEBOOKS.glob("*.ipynb")):
            with self.subTest(notebook=path.name):
                cells = self._cells(path)
                setup = next(
                    ((index, source) for index, source in cells
                     if "google.colab" in source),
                    None,
                )
                first_internal = next(
                    ((index, source) for index, source in cells
                     if INTERNAL_IMPORT.search(source)),
                    None,
                )
                self.assertIsNotNone(setup, "missing Colab setup cell")
                self.assertIsNotNone(first_internal, "no internal dependency found")
                self.assertLessEqual(setup[0], first_internal[0])
                self.assertIn("git", setup[1])
                self.assertIn("clone", setup[1])
                self.assertIn("chdir", setup[1])
                self.assertIn("sys.path.insert", setup[1])

    def test_direct_repository_data_paths_exist(self):
        for path in sorted(NOTEBOOKS.glob("*.ipynb")):
            for _, source in self._cells(path):
                for match in REPO_PATH.finditer(source):
                    target = (path.parent / match.group("path")).resolve()
                    with self.subTest(notebook=path.name, path=str(target)):
                        self.assertTrue(target.exists())

    def test_notebook_source_has_no_developer_machine_paths(self):
        machine_prefix = "/" + "Users" + "/"
        for path in sorted(NOTEBOOKS.glob("*.ipynb")):
            source = "\n".join(code for _, code in self._cells(path))
            with self.subTest(notebook=path.name):
                self.assertNotIn(machine_prefix, source)

        for path in sorted((ROOT / "workshop_tools").rglob("*.py")):
            with self.subTest(module=str(path.relative_to(ROOT))):
                self.assertNotIn(
                    machine_prefix, path.read_text(encoding="utf-8")
                )

    def test_bundled_corpus_assets_exist(self):
        self.assertTrue((ROOT / "data/cuc/cuc.parquet").is_file())
        baal = ROOT / "data/baal_cycle"
        for number in range(1, 7):
            self.assertTrue((baal / f"KTU 1.{number}.tsv").is_file())
        self.assertTrue((baal / "onomastic_gloss_overrides.tsv").is_file())
        self.assertTrue(
            (ROOT / "workshop_tools/vendor/vis-network/vis-network.min.js").is_file()
        )

    def test_default_loaders_use_bundled_corpora(self):
        from workshop_tools.divine_networks import load_baal_cycle
        from workshop_tools.loader import load_texts

        self.assertEqual(len(load_texts(verbose=False)), 279)
        corpus = load_baal_cycle()
        self.assertEqual(corpus.source_dir, ROOT / "data/baal_cycle")
        self.assertEqual(len(corpus.occurrences), 612)


if __name__ == "__main__":
    unittest.main()
