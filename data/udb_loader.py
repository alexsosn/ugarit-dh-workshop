"""Load locally-built UDB Parquet tables.

The Ugaritic Data Bank (UDB) cannot be redistributed, so this loader downloads
nothing and the repository ships no UDB data. Build the tables once from your
own lawfully obtained copy of the PDF:

    python -m workshop_tools.build_udb_parquet --pdf local_data/Ugaritic_data_bank.pdf

That writes five Parquet tables under ``local_data/udb/`` (git-ignored). The
functions here read them and return ``pandas`` DataFrames. See
``workshop_tools/README.md`` for how to obtain the PDF.

Tables (all joinable on ``tablet``):
    texts            one row per tablet: tablet, ktu, genre, museum,
                     provenance, height, width, thickness, correspondences
    readings         one row per reading: row_id, tablet, column, line, ref,
                     reader, text, comment
    sources          reader/edition citations
    literature       scoped bibliography entries
    tablet_comments  tablet-level prose comments
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
_UDB_DIR = _REPO_ROOT / "local_data" / "udb"
_PN_PATH = _REPO_ROOT / "data" / "ugaritic_pn.txt"

_TABLES = ("texts", "readings", "sources", "literature", "tablet_comments")

_BUILD_HINT = (
    "Local UDB Parquet tables were not found under local_data/udb/.\n"
    "The UDB data is not redistributable, so build it once from your own PDF:\n"
    "    python -m workshop_tools.build_udb_parquet "
    "--pdf local_data/Ugaritic_data_bank.pdf\n"
    "(See workshop_tools/README.md for how to obtain the PDF.)"
)


def udb_available() -> bool:
    """Return True when the local UDB Parquet tables have been built."""
    return all((_UDB_DIR / f"{name}.parquet").exists() for name in _TABLES)


def _read(name: str) -> pd.DataFrame:
    path = _UDB_DIR / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(_BUILD_HINT)
    return pd.read_parquet(path)


def load_udb_texts() -> pd.DataFrame:
    """One row per UDB tablet, with the tablet-level metadata (incl. ``genre``)."""
    return _read("texts")


def load_udb_readings() -> pd.DataFrame:
    """One row per reading (every edition's reading of every line)."""
    return _read("readings")


def load_udb_sources() -> pd.DataFrame:
    """Reader/edition citations (which scholarly edition each reader code is)."""
    return _read("sources")


def load_udb_literature() -> pd.DataFrame:
    """Scoped bibliography entries parsed from each tablet's info block."""
    return _read("literature")


def load_udb_tablet_comments() -> pd.DataFrame:
    """Tablet-level prose comments parsed from each tablet's info block."""
    return _read("tablet_comments")


def udb_lines(reader: str = "00") -> pd.DataFrame:
    """One line per ``(tablet, ref)`` for a single edition (default ``"00"``).

    Picks a single reader code so the result is a flat, CUC-like line corpus
    suitable for keyword / n-gram / network analysis. Pass another code (e.g.
    ``"10"``, ``"R1"``) to use a different edition; see ``load_udb_sources()``
    for what each code is.
    """
    readings = load_udb_readings()
    lines = readings[readings["reader"] == reader]
    return lines[["tablet", "column", "line", "ref", "text"]].reset_index(drop=True)


def udb_genre_counts() -> pd.Series:
    """Tablet counts per UDB genre (richer than the KTU-chapter heuristic)."""
    genres = load_udb_texts()["genre"].fillna("(unlabelled)")
    return genres.value_counts()


def load_pn_gazetteer() -> set[str]:
    """Known Ugaritic personal-name forms, for recognising names in letters.

    Bare normalized transliteration forms of the ``PN``-tagged entries in the CUC
    lexicon, built by ``workshop_tools.build_pn_gazetteer`` into
    ``data/ugaritic_pn.txt``. Returns an empty set if that file is absent. Lets
    you tell personal names (``ydrm``, ``iwrḏr``) from formula words (``pʿn``,
    ``yšlm``) that the address-formula parser cannot distinguish.
    """
    if not _PN_PATH.exists():
        return set()
    return {
        line.strip()
        for line in _PN_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


# ---------------------------------------------------------------------------
# Tokenisation & genre helpers (reuse the CUC loader so UDB and CUC are
# tokenised and genre-labelled the same way)
# ---------------------------------------------------------------------------

_MARK_RE = re.compile(r"</?mark>")
_KTU_NUM_RE = re.compile(r"(\d+\.\d+)")
_NONWORD_RE = re.compile(r"^[\W_]+$")  # tokens with no letters/digits (dividers, fills)


def udb_clean_tokens(text: str) -> list[str]:
    """Tokenise a UDB reading into clean word forms.

    UDB transliterations carry ``<mark>…</mark>`` tags (tentative signs) and
    ``…`` gaps; these are removed, then the shared CUC tokeniser strips
    dividers/brackets/broken-sign markers while keeping diacritics.
    """
    from data.loader import clean_tokens

    if not isinstance(text, str):
        return []
    cleaned = _MARK_RE.sub("", text).replace("…", " ").replace("_", " ")
    return [t for t in clean_tokens(cleaned) if not _NONWORD_RE.match(t)]


def ktu_chapter_genre(ktu: str | None) -> str:
    """KTU-derived genre for a UDB text, using the CUC loader's heuristic.

    The UDB ``ktu`` field looks like ``"KTU 1.1"``; this maps it to the same
    coarse/fine genre labels CUC uses, so a UDB tablet can carry *both* its own
    curated ``genre`` and a comparable KTU genre.
    """
    from data.loader import _genre_for

    if not isinstance(ktu, str):
        return "other"
    m = _KTU_NUM_RE.search(ktu)
    return _genre_for(m.group(1)) if m else "other"


def udb_tablet_corpus(reader: str = "00") -> pd.DataFrame:
    """One row per tablet for a single edition, ready for corpus analysis.

    Columns: ``tablet``, ``ktu``, ``genre`` (UDB's own), ``ktu_genre`` (CUC
    heuristic), ``text`` (the edition's lines joined), ``tokens`` (cleaned word
    list), ``n_tokens``. Tablets with no lines for ``reader`` are kept with
    empty text.
    """
    lines = udb_lines(reader)
    joined = (
        lines.groupby("tablet")["text"]
        .apply(lambda s: " ".join(x for x in s if x))
        .reset_index()
    )
    texts = load_udb_texts()[["tablet", "ktu", "genre"]]
    df = texts.merge(joined, on="tablet", how="left")
    df["text"] = df["text"].fillna("")
    df["tokens"] = df["text"].map(udb_clean_tokens)
    df["n_tokens"] = df["tokens"].map(len)
    df["ktu_genre"] = df["ktu"].map(ktu_chapter_genre)
    return df[["tablet", "ktu", "genre", "ktu_genre", "text", "tokens", "n_tokens"]]
