"""Build a local SQLite database from a participant-supplied UDB PDF.

This module contains no UDB source text and performs no network downloads.
Participants must supply a lawfully obtained PDF and keep the generated
database local unless they have separate permission to distribute it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
if str(VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(VENDOR_DIR))

from udb.udb_parser import (  # noqa: E402
    _extract_text_from_pdf,
    _tablets_to_models,
    normalize_comment,
    parse_udb_text,
)

MEASUREMENTS_RE = re.compile(
    r"^\s*(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\.?\s*$",
    re.I,
)
VERSE_REF_RE = re.compile(
    r"^(?P<base>\d+(?:\.\d+)*)(?:\s+(?P<col>[IVXLCDM]+[a-z]?))?"
    r"(?::\s*(?P<line>.+?))?\s*$"
)


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE tablets (
    tablet         TEXT PRIMARY KEY,
    ktu            TEXT,
    genre          TEXT,
    museum         TEXT,
    provenance     TEXT,
    height         INTEGER,
    width          INTEGER,
    thickness      INTEGER,
    correspondences TEXT
);

CREATE TABLE readings (
    reading_id INTEGER PRIMARY KEY,
    tablet     TEXT NOT NULL REFERENCES tablets(tablet),
    column_ref TEXT,
    line_ref   TEXT,
    ref        TEXT NOT NULL,
    reader     TEXT NOT NULL,
    text       TEXT NOT NULL,
    comment    TEXT NOT NULL DEFAULT '',
    UNIQUE(tablet, ref, reader)
);

CREATE TABLE sources (
    source_id  INTEGER PRIMARY KEY,
    tablet     TEXT NOT NULL REFERENCES tablets(tablet),
    reader     TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    citation   TEXT NOT NULL
);

CREATE TABLE literature (
    literature_id      INTEGER PRIMARY KEY,
    tablet             TEXT NOT NULL REFERENCES tablets(tablet),
    scope_type         TEXT NOT NULL,
    scope              TEXT,
    column_start       TEXT,
    column_end         TEXT,
    line_start         TEXT,
    line_end           TEXT,
    citation_type      TEXT NOT NULL,
    authors_json       TEXT NOT NULL,
    title              TEXT,
    container_title    TEXT,
    volume_issue       TEXT,
    publication_place  TEXT,
    publication_details TEXT,
    years_json         TEXT NOT NULL,
    pages_json         TEXT NOT NULL,
    categories_json    TEXT NOT NULL,
    citation           TEXT NOT NULL
);

CREATE TABLE tablet_comments (
    comment_id    INTEGER PRIMARY KEY,
    tablet       TEXT NOT NULL REFERENCES tablets(tablet),
    comment_order INTEGER NOT NULL,
    text         TEXT NOT NULL,
    UNIQUE(tablet, comment_order)
);

CREATE INDEX readings_ref_idx ON readings(tablet, ref);
CREATE INDEX readings_text_idx ON readings(text);
CREATE INDEX literature_scope_idx ON literature(tablet, scope_type);
"""


def natural_tablet_key(tablet: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", tablet or "")
    return tuple(int(part) for part in parts) if parts else (0,)


def split_measurements(
    value: str | None,
) -> tuple[int | None, int | None, int | None]:
    if value is None or not value.strip():
        return None, None, None
    match = MEASUREMENTS_RE.fullmatch(value)
    if not match:
        raise ValueError(f"unsupported measurements value: {value!r}")
    return tuple(int(part) for part in match.groups())


def split_verse_ref(
    tablet: str,
    verse_ref: str,
) -> tuple[str | None, str | None, str]:
    match = VERSE_REF_RE.match(verse_ref or "")
    if not match:
        full_ref = f"{tablet} {verse_ref}".strip() if verse_ref else tablet
        return None, None, full_ref
    column = match.group("col")
    line = match.group("line")
    parts = [tablet] + ([column] if column else []) + ([line] if line else [])
    return column, line, " ".join(parts)


def extract_ktu(correspondences: dict[str, str]) -> str | None:
    value = correspondences.get("KTU")
    return value.strip() if value else None


def _prepare_output(output_path: Path, overwrite: bool) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"{output_path} already exists; pass overwrite=True or --overwrite"
        )
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    return temporary


def build_database(
    pdf_path: str | Path,
    output_path: str | Path,
    *,
    overwrite: bool = True,
) -> dict[str, int]:
    """Parse ``pdf_path`` and atomically create a local SQLite database."""
    source = Path(pdf_path).expanduser().resolve()
    destination = Path(output_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"PDF not found: {source}")

    temporary = _prepare_output(destination, overwrite)
    raw_text = _extract_text_from_pdf(str(source))
    if not raw_text:
        raise RuntimeError(f"PDF text extraction returned no text: {source}")
    models = _tablets_to_models(parse_udb_text(raw_text))
    models.sort(key=lambda model: natural_tablet_key(model.udb_id))

    counts = {
        "tablets": 0,
        "readings": 0,
        "sources": 0,
        "literature": 0,
        "tablet_comments": 0,
    }

    try:
        with sqlite3.connect(temporary) as connection:
            connection.executescript(SCHEMA)
            for model in models:
                metadata = model.metadata or {}
                height, width, thickness = split_measurements(
                    metadata.get("measurements")
                )
                connection.execute(
                    """
                    INSERT INTO tablets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        model.udb_id,
                        extract_ktu(model.correspondences or {}),
                        metadata.get("genre"),
                        metadata.get("museum"),
                        metadata.get("provenance"),
                        height,
                        width,
                        thickness,
                        metadata.get("correspondences_line"),
                    ),
                )
                counts["tablets"] += 1

                for verse in model.verses:
                    column, line, ref = split_verse_ref(model.udb_id, verse.ref)
                    comments = verse.comments or {}
                    for reader, text in (verse.readings or {}).items():
                        connection.execute(
                            """
                            INSERT INTO readings
                            (reading_id, tablet, column_ref, line_ref, ref,
                             reader, text, comment)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                counts["readings"],
                                model.udb_id,
                                column,
                                line,
                                ref,
                                reader,
                                text or "",
                                normalize_comment(comments.get(reader, "")),
                            ),
                        )
                        counts["readings"] += 1

                for source_row in metadata.get("sources", []):
                    connection.execute(
                        "INSERT INTO sources VALUES (?, ?, ?, ?, ?)",
                        (
                            counts["sources"],
                            model.udb_id,
                            source_row["reader"],
                            source_row["source_ref"],
                            source_row["citation"],
                        ),
                    )
                    counts["sources"] += 1

                for item in metadata.get("literature", []):
                    connection.execute(
                        """
                        INSERT INTO literature VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?
                        )
                        """,
                        (
                            counts["literature"],
                            model.udb_id,
                            item["scope_type"],
                            item.get("scope"),
                            item.get("column_start"),
                            item.get("column_end"),
                            item.get("line_start"),
                            item.get("line_end"),
                            item["citation_type"],
                            json.dumps(item.get("authors", []), ensure_ascii=False),
                            item.get("title"),
                            item.get("container_title"),
                            item.get("volume_issue"),
                            item.get("publication_place"),
                            item.get("publication_details"),
                            json.dumps(item.get("years", []), ensure_ascii=False),
                            json.dumps(item.get("pages", []), ensure_ascii=False),
                            json.dumps(
                                item.get("categories", []),
                                ensure_ascii=False,
                            ),
                            item["citation"],
                        ),
                    )
                    counts["literature"] += 1

                for comment_order, comment in enumerate(
                    metadata.get("tablet_comments", [])
                ):
                    connection.execute(
                        "INSERT INTO tablet_comments VALUES (?, ?, ?, ?)",
                        (
                            counts["tablet_comments"],
                            model.udb_id,
                            comment_order,
                            normalize_comment(comment),
                        ),
                    )
                    counts["tablet_comments"] += 1

            connection.execute("PRAGMA optimize")
            connection.commit()
        os.replace(temporary, destination)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pdf",
        nargs="?",
        default="local_data/Ugaritic_data_bank.pdf",
        help="participant-supplied UDB PDF",
    )
    parser.add_argument(
        "--output",
        default="local_data/udb.sqlite",
        help="local SQLite output path",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace an existing output database",
    )
    args = parser.parse_args()

    print(
        "Local-use reminder: do not commit or redistribute the source PDF or "
        "generated database without separate authorization."
    )
    counts = build_database(
        args.pdf,
        args.output,
        overwrite=args.overwrite,
    )
    print(f"Created {Path(args.output).resolve()}")
    for table, count in counts.items():
        print(f"{table}: {count}")


if __name__ == "__main__":
    main()

