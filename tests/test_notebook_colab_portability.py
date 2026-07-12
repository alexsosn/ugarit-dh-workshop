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
        for path in sorted(NOTEBOOKS.glob("*.ipynb")):
            source = "\n".join(code for _, code in self._cells(path))
            with self.subTest(notebook=path.name):
                self.assertNotIn("/Users/", source)


if __name__ == "__main__":
    unittest.main()
