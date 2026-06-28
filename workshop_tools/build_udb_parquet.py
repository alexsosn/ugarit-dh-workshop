"""Build local UDB Parquet tables from a participant-supplied PDF.

This module contains no UDB source text and performs no network downloads.
Participants must supply a lawfully obtained PDF and keep the generated tables
local unless they have separate permission to distribute them.

The PDF is parsed by the UDB parser vendored under vendor/ (its `udb.udb_parser`
module: pdfminer extraction -> parse_udb_text -> UDBTablet models), which also
extracts text-level metadata. This script runs PDF -> tablets entirely in
memory and writes five normalized tables (joinable on `tablet`) under
``local_data/udb/``:

  texts.parquet    one row per text, tablet-level fields:
                   tablet, ktu, genre, museum, provenance, height, width,
                   thickness, correspondences
  readings.parquet one row per reading (one edition's reading of one verse):
                   row_id, tablet, column, line, ref, reader, text, comment
                   (tablet/column/line/ref mirror the CUC scheme; line is a
                   string because UDB lines include sub-line letters/ranges)
  sources.parquet  one row per reader/edition citation:
                   source_id, tablet, reader, source_ref, citation
  literature.parquet one row per scoped bibliography entry:
                   literature_id, tablet, scope fields, parsed citation fields,
                   categories, citation
  tablet_comments.parquet one row per tablet-level prose comment:
                   comment_id, tablet, comment_order, text

Requirements: pyarrow and pdfminer.six (the parser is vendored, so no other
package is needed).

Usage:
    python -m workshop_tools.build_udb_parquet --pdf local_data/Ugaritic_data_bank.pdf
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
DEFAULT_PDF = "local_data/Ugaritic_data_bank.pdf"
DEFAULT_OUTPUT_DIR = Path("local_data/udb")

KTU_RE = re.compile(r"\bKTU\s+\S+")
READER_RE = re.compile(r"^(?:R\d+|\d{2})$")
MEASUREMENTS_RE = re.compile(
    r"^\s*(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\.?\s*$",
    re.I,
)
PAGE_MARKER_RE = re.compile(r"(?<!\S)-{1,2}\d{1,5}-(?!\S)")

TEXTS_SCHEMA = pa.schema([
    ("tablet", pa.string()),
    ("ktu", pa.string()),
    ("genre", pa.string()),
    ("museum", pa.string()),
    ("provenance", pa.string()),
    ("height", pa.int64()),
    ("width", pa.int64()),
    ("thickness", pa.int64()),
    ("correspondences", pa.string()),
])
READINGS_SCHEMA = pa.schema([
    ("row_id", pa.int64()),
    ("tablet", pa.string()),
    ("column", pa.string()),
    ("line", pa.string()),
    ("ref", pa.string()),
    ("reader", pa.string()),
    ("text", pa.string()),
    ("comment", pa.string()),
])
SOURCES_SCHEMA = pa.schema([
    ("source_id", pa.int64()),
    ("tablet", pa.string()),
    ("reader", pa.string()),
    ("source_ref", pa.string()),
    ("citation", pa.string()),
])
LITERATURE_SCHEMA = pa.schema([
    ("literature_id", pa.int64()),
    ("tablet", pa.string()),
    ("scope_type", pa.string()),
    ("scope", pa.string()),
    ("column_start", pa.string()),
    ("column_end", pa.string()),
    ("line_start", pa.string()),
    ("line_end", pa.string()),
    ("citation_type", pa.string()),
    ("authors", pa.list_(pa.string())),
    ("title", pa.string()),
    ("container_title", pa.string()),
    ("volume_issue", pa.string()),
    ("publication_place", pa.string()),
    ("publication_details", pa.string()),
    ("years", pa.list_(pa.string())),
    ("pages", pa.list_(pa.string())),
    ("categories", pa.list_(pa.string())),
    ("citation", pa.string()),
])
TABLET_COMMENTS_SCHEMA = pa.schema([
    ("comment_id", pa.int64()),
    ("tablet", pa.string()),
    ("comment_order", pa.int64()),
    ("text", pa.string()),
])


def udb_sort_key(udb_id: str):
    """Natural sort: '1.2' before '1.10', chapter-major."""
    parts = re.findall(r"\d+", udb_id or "")
    return tuple(int(p) for p in parts) if parts else (0,)


def extract_ktu(correspondences: dict, corr_line: str | None) -> str | None:
    """Reliable KTU reference: prefer the correspondences map, then the line."""
    if correspondences.get("KTU"):
        return correspondences["KTU"].strip()
    m = KTU_RE.search(corr_line or "")
    return m.group(0).strip() if m else None


def split_measurements(
    value: str | None,
) -> tuple[int | None, int | None, int | None]:
    """Parse UDB dimensions as height, width, and thickness in millimetres."""
    if value is None or not value.strip():
        return None, None, None
    match = MEASUREMENTS_RE.fullmatch(value)
    if not match:
        raise ValueError(f"unsupported measurements value: {value!r}")
    return tuple(int(part) for part in match.groups())


VERSE_REF_RE = re.compile(
    r"^(?P<base>\d+(?:\.\d+)*)(?:\s+(?P<col>[IVXLCDM]+[a-z]?))?"
    r"(?::\s*(?P<line>.+?))?\s*$"
)


def split_verse_ref(tablet: str, verse_ref: str):
    """Decompose a UDB verse ref into (column, line, full_ref), CUC-style.

    The verse ref's own base number echoes the tablet inconsistently, so it is
    discarded in favour of the reliable UDB tablet id. `column` is the Roman
    numeral when present; `line` keeps UDB sub-line letters and ranges (e.g.
    "0a", "10-12"), so it stays a string rather than an int. `ref` mirrors CUC's
    space-separated form, e.g. "1.1 II 3".
    """
    m = VERSE_REF_RE.match(verse_ref or "")
    if not m:
        return None, None, (f"{tablet} {verse_ref}".strip() if verse_ref else tablet)
    col, line = m.group("col"), m.group("line")
    parts = [tablet] + ([col] if col else []) + ([line] if line else [])
    return col, line, " ".join(parts)


def load_tablets(pdf_path: Path):
    """PDF -> List[UDBTablet] using the vendored UDB parser (in memory)."""
    sys.path.insert(0, str(VENDOR_DIR))
    try:
        from udb.udb_parser import (
            _extract_text_from_pdf,
            parse_udb_text,
            _tablets_to_models,
        )
    except ImportError as e:
        raise SystemExit(f"cannot import the vendored UDB parser ({e}); is pdfminer.six installed?")
    text = _extract_text_from_pdf(str(pdf_path))
    if not text:
        raise SystemExit(f"PDF text extraction returned nothing for {pdf_path}")
    return _tablets_to_models(parse_udb_text(text))


def parser_helpers():
    """Load canonicalization helpers from the vendored parser."""
    if str(VENDOR_DIR) not in sys.path:
        sys.path.insert(0, str(VENDOR_DIR))
    from udb.udb_parser import (
        is_editorial_apparatus,
        normalize_comment,
        normalize_reader_code,
    )

    return is_editorial_apparatus, normalize_reader_code, normalize_comment


def canonicalize_readings(rows: list[dict]) -> list[dict]:
    """Remove parser artifacts and assign canonical reader codes and row ids."""
    (
        is_editorial_apparatus,
        normalize_reader_code,
        normalize_comment,
    ) = parser_helpers()
    canonical: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    for source_row in rows:
        row = dict(source_row)
        text = row.get("text") or ""
        if is_editorial_apparatus(text):
            continue
        if row.get("line") is None and not text.strip():
            # Edition/bibliography headers can resemble an empty reading.
            continue

        row["reader"] = normalize_reader_code(str(row.get("reader") or ""))
        row["comment"] = normalize_comment(str(row.get("comment") or ""))
        key = (str(row["tablet"]), str(row["ref"]), row["reader"])
        if key in seen:
            raise ValueError(f"duplicate canonical reading: {key}")
        seen.add(key)
        row["row_id"] = len(canonical)
        canonical.append(row)

    return canonical


def validate_rows(
    text_rows: list[dict],
    reading_rows: list[dict],
    source_rows: list[dict],
    literature_rows: list[dict],
    tablet_comment_rows: list[dict],
) -> None:
    """Fail the build when primary keys, foreign keys, or parser invariants break."""
    is_editorial_apparatus, _, _ = parser_helpers()
    tablet_ids = [str(row["tablet"]) for row in text_rows]
    if len(tablet_ids) != len(set(tablet_ids)):
        raise ValueError("duplicate tablet ids in texts")

    for row in text_rows:
        dimensions = (row["height"], row["width"], row["thickness"])
        if any(value is None for value in dimensions) and not all(
            value is None for value in dimensions
        ):
            raise ValueError(f"partial measurements for tablet {row['tablet']}")
        if any(value is not None and value < 0 for value in dimensions):
            raise ValueError(f"invalid measurements for tablet {row['tablet']}")

    tablets = set(tablet_ids)
    seen: set[tuple[str, str, str]] = set()
    for expected_row_id, row in enumerate(reading_rows):
        if row["row_id"] != expected_row_id:
            raise ValueError("reading row_id values are not contiguous")
        if row["tablet"] not in tablets:
            raise ValueError(f"orphan reading for tablet {row['tablet']}")
        if not READER_RE.fullmatch(row["reader"]):
            raise ValueError(f"non-canonical reader code: {row['reader']}")
        if is_editorial_apparatus(row["text"]):
            raise ValueError(f"editorial apparatus stored as reading: {row['ref']}")
        if row["line"] is None and not row["text"].strip():
            raise ValueError(
                f"empty unnumbered reading: {row['ref']} / {row['reader']}"
            )
        comment = row["comment"]
        if "_" in comment or "\n" in comment or "\r" in comment:
            raise ValueError(f"unnormalized comment: {row['ref']} / {row['reader']}")
        if PAGE_MARKER_RE.search(comment):
            raise ValueError(
                f"page marker stored in comment: {row['ref']} / {row['reader']}"
            )
        key = (row["tablet"], row["ref"], row["reader"])
        if key in seen:
            raise ValueError(f"duplicate reading key: {key}")
        seen.add(key)

    source_keys: set[tuple[str, str]] = set()
    for expected_source_id, row in enumerate(source_rows):
        if row["source_id"] != expected_source_id:
            raise ValueError("source_id values are not contiguous")
        if row["tablet"] not in tablets:
            raise ValueError(f"orphan source for tablet {row['tablet']}")
        if not READER_RE.fullmatch(row["reader"]):
            raise ValueError(f"non-canonical source reader code: {row['reader']}")
        if not row["citation"].strip():
            raise ValueError(f"empty source citation: {row['source_ref']}")
        key = (row["tablet"], row["source_ref"])
        if key in source_keys:
            raise ValueError(f"duplicate source key: {key}")
        source_keys.add(key)

    for expected_literature_id, row in enumerate(literature_rows):
        if row["literature_id"] != expected_literature_id:
            raise ValueError("literature_id values are not contiguous")
        if row["tablet"] not in tablets:
            raise ValueError(f"orphan literature entry for tablet {row['tablet']}")
        if not row["citation"].strip():
            raise ValueError(f"empty literature citation: {row['literature_id']}")
        if row["scope_type"] not in {
            "tablet",
            "tablet_group",
            "column_range",
            "line_range",
            "other",
        }:
            raise ValueError(
                f"invalid literature scope type: {row['scope_type']}"
            )
        if row["citation_type"] not in {
            "literature",
            "first_edition",
            "preliminary_edition",
            "photograph",
            "cross_reference",
        }:
            raise ValueError(
                f"invalid literature citation type: {row['citation_type']}"
            )
        if (
            "_" in row["citation"]
            or "\n" in row["citation"]
            or "\r" in row["citation"]
            or PAGE_MARKER_RE.search(row["citation"])
        ):
            raise ValueError(
                f"unnormalized literature citation: {row['literature_id']}"
            )

    comment_order: dict[str, int] = {}
    for expected_comment_id, row in enumerate(tablet_comment_rows):
        if row["comment_id"] != expected_comment_id:
            raise ValueError("comment_id values are not contiguous")
        if row["tablet"] not in tablets:
            raise ValueError(f"orphan tablet comment for {row['tablet']}")
        expected_order = comment_order.get(row["tablet"], 0)
        if row["comment_order"] != expected_order:
            raise ValueError(f"invalid comment order for tablet {row['tablet']}")
        comment_order[row["tablet"]] = expected_order + 1
        if not row["text"].strip():
            raise ValueError(f"empty tablet comment: {row['comment_id']}")
        if (
            "_" in row["text"]
            or "\n" in row["text"]
            or "\r" in row["text"]
            or PAGE_MARKER_RE.search(row["text"])
        ):
            raise ValueError(f"unnormalized tablet comment: {row['comment_id']}")


def write_tables(
    text_rows: list[dict],
    reading_rows: list[dict],
    source_rows: list[dict],
    literature_rows: list[dict],
    tablet_comment_rows: list[dict],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    texts_path = output_dir / "texts.parquet"
    readings_path = output_dir / "readings.parquet"
    sources_path = output_dir / "sources.parquet"
    literature_path = output_dir / "literature.parquet"
    tablet_comments_path = output_dir / "tablet_comments.parquet"
    pq.write_table(
        pa.Table.from_pylist(text_rows, schema=TEXTS_SCHEMA),
        texts_path,
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(reading_rows, schema=READINGS_SCHEMA),
        readings_path,
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(source_rows, schema=SOURCES_SCHEMA),
        sources_path,
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(literature_rows, schema=LITERATURE_SCHEMA),
        literature_path,
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(
            tablet_comment_rows,
            schema=TABLET_COMMENTS_SCHEMA,
        ),
        tablet_comments_path,
        compression="zstd",
    )
    print(
        f"texts: {len(text_rows)} rows -> {texts_path} "
        f"({texts_path.stat().st_size / 1024:.1f} KiB)"
    )
    print(
        f"readings: {len(reading_rows)} rows -> {readings_path} "
        f"({readings_path.stat().st_size / 1024:.1f} KiB)"
    )
    print(
        f"sources: {len(source_rows)} rows -> {sources_path} "
        f"({sources_path.stat().st_size / 1024:.1f} KiB)"
    )
    print(
        f"literature: {len(literature_rows)} rows -> {literature_path} "
        f"({literature_path.stat().st_size / 1024:.1f} KiB)"
    )
    print(
        f"tablet_comments: {len(tablet_comment_rows)} rows -> "
        f"{tablet_comments_path} "
        f"({tablet_comments_path.stat().st_size / 1024:.1f} KiB)"
    )


def repair_existing_tables(output_dir: Path) -> None:
    """Apply current parser invariants to already-generated Parquet tables."""
    texts_path = output_dir / "texts.parquet"
    readings_path = output_dir / "readings.parquet"
    if not texts_path.exists() or not readings_path.exists():
        raise SystemExit(f"existing Parquet tables not found under {output_dir}")

    text_rows = pq.read_table(texts_path).to_pylist()
    for row in text_rows:
        if "measurements" in row:
            row["height"], row["width"], row["thickness"] = split_measurements(
                row.pop("measurements")
            )
    reading_rows = canonicalize_readings(pq.read_table(readings_path).to_pylist())
    sources_path = output_dir / "sources.parquet"
    source_rows = (
        pq.read_table(sources_path).to_pylist() if sources_path.exists() else []
    )
    literature_path = output_dir / "literature.parquet"
    literature_rows = (
        pq.read_table(literature_path).to_pylist()
        if literature_path.exists()
        else []
    )
    tablet_comments_path = output_dir / "tablet_comments.parquet"
    tablet_comment_rows = (
        pq.read_table(tablet_comments_path).to_pylist()
        if tablet_comments_path.exists()
        else []
    )
    validate_rows(
        text_rows,
        reading_rows,
        source_rows,
        literature_rows,
        tablet_comment_rows,
    )
    write_tables(
        text_rows,
        reading_rows,
        source_rows,
        literature_rows,
        tablet_comment_rows,
        output_dir,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pdf", default=DEFAULT_PDF, help="path to the UDB source PDF")
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="directory for the generated Parquet tables",
    )
    ap.add_argument(
        "--repair-existing",
        action="store_true",
        help="canonicalize existing Parquet tables without reparsing the source PDF",
    )
    args = ap.parse_args()

    print(
        "Local-use reminder: do not commit or redistribute the source PDF or "
        "generated Parquet tables without separate authorization."
    )

    output_dir = args.output_dir.expanduser()
    if args.repair_existing:
        repair_existing_tables(output_dir)
        return

    pdf_path = Path(args.pdf).expanduser()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path} — download it and pass --pdf")

    models = load_tablets(pdf_path)
    models.sort(key=lambda m: udb_sort_key(m.udb_id))

    text_rows: list[dict] = []
    reading_rows: list[dict] = []
    source_rows: list[dict] = []
    literature_rows: list[dict] = []
    tablet_comment_rows: list[dict] = []

    for m in models:
        meta = m.metadata or {}
        height, width, thickness = split_measurements(meta.get("measurements"))
        text_rows.append({
            "tablet": m.udb_id,
            "ktu": extract_ktu(
                m.correspondences or {}, meta.get("correspondences_line")
            ),
            "genre": meta.get("genre"),
            "museum": meta.get("museum"),
            "provenance": meta.get("provenance"),
            "height": height,
            "width": width,
            "thickness": thickness,
            "correspondences": meta.get("correspondences_line"),
        })
        for source in meta.get("sources", []):
            source_rows.append({
                "source_id": len(source_rows),
                "tablet": m.udb_id,
                "reader": source["reader"],
                "source_ref": source["source_ref"],
                "citation": source["citation"],
            })
        for literature in meta.get("literature", []):
            literature_rows.append({
                "literature_id": len(literature_rows),
                "tablet": m.udb_id,
                **literature,
            })
        for comment_order, text in enumerate(
            meta.get("tablet_comments", [])
        ):
            tablet_comment_rows.append({
                "comment_id": len(tablet_comment_rows),
                "tablet": m.udb_id,
                "comment_order": comment_order,
                "text": text,
            })

        for verse in m.verses:
            column, line, ref = split_verse_ref(m.udb_id, verse.ref)
            comments = verse.comments or {}
            for reader, text in (verse.readings or {}).items():
                reading_rows.append({
                    "tablet": m.udb_id,
                    "column": column,
                    "line": line,
                    "ref": ref,
                    "reader": reader,
                    "text": text or "",
                    "comment": comments.get(reader, ""),
                })

    reading_rows = canonicalize_readings(reading_rows)
    validate_rows(
        text_rows,
        reading_rows,
        source_rows,
        literature_rows,
        tablet_comment_rows,
    )
    write_tables(
        text_rows,
        reading_rows,
        source_rows,
        literature_rows,
        tablet_comment_rows,
        output_dir,
    )


if __name__ == "__main__":
    main()
