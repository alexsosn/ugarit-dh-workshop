from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from workshop_tools.build_udb_sqlite import (
    build_database,
    split_measurements,
    split_verse_ref,
)


SYNTHETIC_PDF_TEXT = """
UDB 1.1
= RS 1.001 = KTU 1.1
Example Museum
Example archive
60 x 69 x 9.
Myth
00-1. 1: I: 1 abc . def
R1-1. 1: I: 1 abc . dgf
_R1 checks a synthetic reading. -8-_
""".strip()


class UDBWorkshopTests(unittest.TestCase):
    def test_helpers(self) -> None:
        self.assertEqual(split_measurements("60 x 69 x 9."), (60, 69, 9))
        self.assertEqual(
            split_verse_ref("1.1", "1 I:1"),
            ("I", "1", "1.1 I 1"),
        )

    def test_builds_sqlite_from_synthetic_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "synthetic.pdf"
            pdf.write_bytes(b"%PDF synthetic test placeholder")
            database = root / "udb.sqlite"

            with patch(
                "workshop_tools.build_udb_sqlite._extract_text_from_pdf",
                return_value=SYNTHETIC_PDF_TEXT,
            ):
                counts = build_database(pdf, database)

            self.assertEqual(counts["tablets"], 1)
            self.assertEqual(counts["readings"], 2)
            with sqlite3.connect(database) as connection:
                rows = connection.execute(
                    "SELECT reader, text, comment FROM readings ORDER BY reading_id"
                ).fetchall()
            self.assertEqual(rows[0], ("00", "abc . def", ""))
            self.assertEqual(
                rows[1],
                ("R1", "abc . dgf", "R1 checks a synthetic reading."),
            )


if __name__ == "__main__":
    unittest.main()

