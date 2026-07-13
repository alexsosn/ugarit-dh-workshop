"""
Data loader for the Ugarit DH workshop — backed by the REAL corpus.
===================================================================

The notebooks use the **Copenhagen Ugaritic Corpus (CUC)** through the Parquet
snapshot bundled under ``data/cuc/``. Set ``UGARIT_CUC_DIR`` to use another
local Parquet directory. No corpus download is required at notebook runtime.
Every notebook calls ``load_texts()`` and gets a uniform list of tablets back.

  Source : CUC, CACCHT project (DT-UCPH/cuc), Text-Fabric export → Parquet
           https://huggingface.co/datasets/AlexWalhai/CUC
  Licence: Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0).
           Educational / non-commercial use only — see data/README.md.

Each tablet is returned as a dictionary with the same keys:

    {
        "ktu":      "1.3",                 # KTU text number
        "title":    "KTU 1.3",             # label
        "name":     "Baal Myth Third Tablet",   # descriptive title (catalogue) or KTU fallback
        "genre":    "myth",                # see GENRE notes below
        "language": "ugaritic",
        "lines":    ["bʿl . sid . zbl . bʿl", ...],   # Latin transliteration
        "ugaritic": ["𐎁𐎓𐎍 𐎟 𐎒𐎛𐎄 ...", ...],         # cuneiform unicode
        "refs":     ["KTU 1.3 I 3", ...],  # per-line reference
        "tokens":   ["bʿl", "sid", ...],   # cleaned word forms (added by loader)
        "source":   "cuc",
    }

Genre labels are **heuristic**: coarse by KTU number (1 = literary/religious,
2 = letter, 3 = legal/economic), refined for well-known tablets via FINE_GENRE.
They are teaching labels, not a scholarly classification — discuss the caveats.

Quick start (inside a notebook):

    import sys; sys.path.append("..")
    from workshop_tools.loader import load_texts
    texts = load_texts()
    print(len(texts), "tablets")
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path

try:
    import pyarrow.parquet as pq
except ImportError:
    pq = None

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = _REPO_ROOT / "data"
_BUNDLED_CUC_DIR = Path(os.environ.get("UGARIT_CUC_DIR", _DATA_DIR / "cuc")).expanduser()
_ALPHABET_PATH = _DATA_DIR / "alphabet.json"
_CATALOG_PATH = _DATA_DIR / "ugaritic_texts_catalog.tsv"
_OMEN_PATH = _DATA_DIR / "omens" / "sheep_birth_omens.json"
_OMEN_TEXT_PATH = _DATA_DIR / "omens" / "ugaritic_birth_omens.txt"
_BABYLONIAN_IZBU_PATH = _DATA_DIR / "omens" / "babylonian_izbu_omens.json"
_BABYLONIAN_FOETUS_PATH = _DATA_DIR / "omens" / "babylonian_foetus_omens.json"
_BABYLONIAN_CELESTIAL_PATH = _DATA_DIR / "omens" / "babylonian_celestial_omens.json"
_UGARITIC_LUNAR_PATH = _DATA_DIR / "omens" / "ugaritic_lunar_omens.json"
_UGARITIC_DREAM_PATH = _DATA_DIR / "omens" / "ugaritic_dream_omens.json"

# Characters that are not part of a word form (restorations, breaks, dividers).
_STRIP_CHARS = "[]()<>!?*/\\"
_DIVIDER = "."          # Ugaritic word divider in the Latin transliteration
_BROKEN = re.compile(r"^x+$", re.IGNORECASE)   # x, xx, xxxxx … = broken signs
_KTU_RE = re.compile(r"\bKTU\s+(\d+\.\d+)", re.IGNORECASE)
_KTU_ANY_RE = re.compile(r"\b(\d+\.\d+)\b")


# ---------------------------------------------------------------------------
# Genre heuristics
# ---------------------------------------------------------------------------
# Coarse genre from the leading KTU digit.
_COARSE = {"1": "literary/religious", "2": "letter", "3": "legal/economic"}

# Finer labels for securely identified tablets (not exhaustive; conservative).
FINE_GENRE = {
    # Myth / epic
    **{f"1.{n}": "myth" for n in (1, 2, 3, 4, 5, 6, 10, 12, 23, 24, 92, 96, 100, 114)},
    **{f"1.{n}": "epic" for n in (14, 15, 16, 17, 18, 19, 20, 21, 22)},
    # Ritual / liturgy
    **{f"1.{n}": "ritual" for n in (39, 40, 41, 43, 46, 87, 105, 106, 109,
                                    112, 119, 130, 132, 148, 161, 168)},
    # Divination / omens
    **{f"1.{n}": "divination" for n in (78, 103, 124, 140, 141, 142, 143,
                                        155, 163, 164)},
    # God lists / pantheon
    **{f"1.{n}": "god-list" for n in (47, 102, 118)},
}


def _genre_for(ktu: str) -> str:
    if ktu in FINE_GENRE:
        return FINE_GENRE[ktu]
    return _COARSE.get(ktu.split(".")[0], "other")


# ---------------------------------------------------------------------------
# Tokenisation
# ---------------------------------------------------------------------------

def clean_tokens(latin_line: str):
    """Turn a Latin transliteration line into a list of clean word forms.

    Word dividers ('.'), restoration brackets and broken-sign markers ('x')
    are removed; diacritics (š ḥ ʿ ʾ ġ ṯ …) are kept.
    """
    out = []
    for raw in latin_line.replace(_DIVIDER, " ").split():
        tok = raw.strip(_STRIP_CHARS)
        tok = tok.replace("[", "").replace("]", "")
        if not tok or _BROKEN.match(tok):
            continue
        out.append(tok)
    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _parquet_paths():
    """Return bundled/local CUC Parquet paths and a source label."""
    local = sorted(_BUNDLED_CUC_DIR.glob("*.parquet"))
    if local:
        source = (
            "bundled data/cuc"
            if _BUNDLED_CUC_DIR == _DATA_DIR / "cuc"
            else str(_BUNDLED_CUC_DIR)
        )
        return local, source
    raise FileNotFoundError(
        f"No CUC Parquet snapshot found under {_BUNDLED_CUC_DIR}. "
        "Re-clone the workshop repository or set UGARIT_CUC_DIR."
    )


def _string(value) -> str:
    """Coerce optional scalar Parquet values to plain strings."""
    return "" if value is None else str(value)


def _as_list(value) -> list:
    """Coerce optional scalar/list Parquet values to a Python list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _normalize_ktu(value) -> str:
    """Extract a bare KTU number from values such as 'KTU 1.1' or '1.1'."""
    text = _string(value).strip()
    match = _KTU_RE.search(text)
    if match:
        return match.group(1)
    match = _KTU_ANY_RE.search(text)
    return match.group(1) if match else text


def _record_for(records: dict, ktu: str) -> dict:
    return records.setdefault(ktu, {"lines": [], "ugaritic": [], "refs": []})


def _add_line_table_rows(records: dict, rows: list[dict]) -> None:
    """Add HuggingFace CUC line-table rows to tablet records."""
    for row in rows:
        ktu = _normalize_ktu(row.get("tablet"))
        if not ktu:
            continue
        record = _record_for(records, ktu)
        record["lines"].append(_string(row.get("text")))
        record["ugaritic"].append(_string(row.get("ugaritic_text")))
        record["refs"].append(_string(row.get("ref")))


def _add_tablet_rows(records: dict, rows: list[dict]) -> None:
    """Add tablet-level parquet rows to tablet records."""
    for row in rows:
        ktu = _normalize_ktu(row.get("ktu") or row.get("tablet"))
        if not ktu:
            continue
        record = _record_for(records, ktu)
        record["lines"].extend(_string(value) for value in _as_list(row.get("lines")))
        record["ugaritic"].extend(
            _string(value)
            for value in _as_list(row.get("ugaritic") or row.get("ugaritic_text"))
        )
        record["refs"].extend(_string(value) for value in _as_list(row.get("refs")))


_CATALOG_TITLES = None


def load_catalog_titles():
    """Return ``{ktu: descriptive title}`` parsed from the texts-catalogue TSV.

    The KTU number is embedded in the catalogue's publication-number note
    (e.g. ``"KTU 1.1; CTA 1; …"``); the human-readable name is in
    ``text_descriptive_title``. Result is cached after the first read; tablets
    with no catalogue entry simply fall back to their KTU number in ``load_texts``.
    """
    global _CATALOG_TITLES
    if _CATALOG_TITLES is not None:
        return _CATALOG_TITLES
    import csv
    titles = {}
    if _CATALOG_PATH.exists():
        with open(_CATALOG_PATH, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                title = (row.get("text_descriptive_title") or "").strip()
                if not title:
                    continue
                for ktu in _KTU_RE.findall(row.get("text_or_publication_number_note", "")):
                    titles.setdefault(ktu, title)
    _CATALOG_TITLES = titles
    return titles


_PUB_ALIASES = None


def load_publication_aliases():
    """Return ``{normalized_siglum: ktu}`` parsed from the texts-catalogue TSV.

    Each tablet's catalogue note lists every publication/excavation siglum it is
    known by (e.g. ``"KTU 1.4; CAT 1.4; CTU 1.4; RS 3.341; RS 3.347; ..."``).
    This maps each of those sigla — RS excavation numbers, CTU/CAT/CTA editions,
    museum numbers — to the tablet's KTU number, so a tablet can be looked up by
    whichever label a reader has in hand. Sigla are upper-cased and their
    internal whitespace collapsed, so ``"rs 3.341"`` and ``"RS  3.341"`` both
    match. Cached after the first read.
    """
    global _PUB_ALIASES
    if _PUB_ALIASES is not None:
        return _PUB_ALIASES
    import csv
    aliases = {}
    if _CATALOG_PATH.exists():
        with open(_CATALOG_PATH, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                note = row.get("text_or_publication_number_note", "")
                match = _KTU_RE.search(note)
                if not match:
                    continue
                ktu = match.group(1)
                for part in note.split(";"):
                    key = " ".join(part.split()).upper()
                    if key:
                        aliases.setdefault(key, ktu)
    _PUB_ALIASES = aliases
    return aliases


def resolve_to_ktu(query):
    """Best-effort: turn a tablet reference a user typed into its KTU number.

    Accepts a bare KTU number (``"1.4"``), a KTU-family siglum (``"KTU 1.4"``,
    ``"CAT 1.4"``, ``"CTU 1.4"``), or any catalogued excavation/museum number
    (``"RS 3.341"``). Returns the KTU number string (``"1.4"``), or ``None`` if
    nothing matches. Lookup is case- and spacing-insensitive.
    """
    if not query:
        return None
    q = " ".join(str(query).split()).upper()
    if re.fullmatch(r"\d+\.\d+", q):          # already a bare KTU number
        return q
    aliases = load_publication_aliases()
    if q in aliases:                          # a known siglum (RS 3.341, CAT 1.4, …)
        return aliases[q]
    ktu_family = re.fullmatch(r"(?:KTU\d?|CAT|CTU|CTA)\s+(\d+\.\d+)", q)
    if ktu_family:                            # an edition siglum we can read directly
        return ktu_family.group(1)
    return None


def load_texts(genres=None, min_tokens=1, verbose=True):
    """Load the CUC corpus as a list of tablet dictionaries.

    genres:     optional iterable of genre labels to keep (e.g. ["letter", "myth"]).
    min_tokens: drop tablets with fewer than this many word tokens (skip scraps).
    verbose:    print a one-line summary.
    """
    if pq is None:
        raise RuntimeError(
            "pyarrow is required to load CUC parquet files. "
            "Install it with: pip install pyarrow"
        )

    paths, source = _parquet_paths()
    records = {}
    texts = []
    titles = load_catalog_titles()

    for parquet_path in paths:
        try:
            table = pq.read_table(parquet_path)
            rows = table.to_pylist()
        except Exception as e:
            raise RuntimeError(
                f"Failed to read parquet file {parquet_path}: {e}"
            ) from e

        columns = set(table.schema.names)
        if {"tablet", "text"}.issubset(columns):
            _add_line_table_rows(records, rows)
        elif (
            {"ktu", "lines"}.issubset(columns)
            or {"tablet", "lines"}.issubset(columns)
        ):
            _add_tablet_rows(records, rows)
        else:
            raise RuntimeError(
                f"Unsupported CUC parquet schema in {parquet_path}. "
                "Expected line-level columns 'tablet' and 'text', or "
                f"tablet-level columns 'ktu' and 'lines'. Found: {sorted(columns)}"
            )

    for ktu, record in records.items():
        lines = record["lines"]
        tokens = []
        for line in lines:
            if isinstance(line, str):
                tokens.extend(clean_tokens(line))

        if len(tokens) < min_tokens:
            continue

        texts.append({
            "ktu": ktu,
            "title": f"KTU {ktu}",
            "name": titles.get(ktu, f"KTU {ktu}"),
            "genre": _genre_for(ktu),
            "language": "ugaritic",
            "lines": lines,
            "ugaritic": record["ugaritic"],
            "refs": record["refs"],
            "tokens": tokens,
            "source": "cuc",
        })

    if genres is not None:
        wanted = set(genres)
        texts = [t for t in texts if t["genre"] in wanted]

    if verbose:
        n_tok = sum(len(t["tokens"]) for t in texts)
        print(f"[loader] Loaded {len(texts)} CUC tablets, {n_tok} word tokens "
              f"(source: {source}, licence: CC BY-NC 4.0).")
    return texts


def texts_by_genre(texts):
    """Group a text list into {genre: [texts]}."""
    grouped = {}
    for t in texts:
        grouped.setdefault(t["genre"], []).append(t)
    return grouped


def without_broken_tokens(tokens):
    """Drop corpus tokens containing ``x`` (the broken-sign convention)."""
    return [token for token in tokens if "x" not in token.lower()]


def all_tokens(texts, exclude_broken=False):
    """Flatten every word token from every tablet into one list."""
    out = []
    for t in texts:
        tokens = t["tokens"]
        out.extend(without_broken_tokens(tokens) if exclude_broken else tokens)
    return out


def token_counts(texts, exclude_broken=False):
    """collections.Counter of word-form frequencies across the corpus."""
    return Counter(all_tokens(texts, exclude_broken=exclude_broken))


def text_as_string(text, exclude_broken=False):
    """One tablet's word tokens as a single space-separated string (for TF-IDF)."""
    tokens = text["tokens"]
    if exclude_broken:
        tokens = without_broken_tokens(tokens)
    return " ".join(tokens)


def corpus_as_documents(texts, exclude_broken=True):
    """Return (labels, documents) parallel lists for TF-IDF / clustering.

    Tokens containing ``x`` are excluded by default because CUC uses ``x`` for
    broken signs; they are preservation noise rather than lexical evidence.

    labels — KTU numbers; documents — one cleaned string per tablet.
    """
    labels = [t["ktu"] for t in texts]
    documents = [
        text_as_string(t, exclude_broken=exclude_broken) for t in texts
    ]
    return labels, documents


# ---------------------------------------------------------------------------
# Alphabet (for the “optimal design” hypothesis, notebook 1b)
# ---------------------------------------------------------------------------

def load_alphabet():
    """Return the alphabet table: list of dicts with
    position, sign, char (cuneiform), wedges, turns, complexity.
    """
    with open(_ALPHABET_PATH, encoding="utf-8") as f:
        return json.load(f)["alphabet"]


# ---------------------------------------------------------------------------
# Ugarit map data (notebooks 1a / 1b) — public ArcGIS find spots + site plan.
# Rebuild the two files with: python -m workshop_tools.build_ugarit_map
# ---------------------------------------------------------------------------

_FIND_SPOTS_PATH = _DATA_DIR / "ugarit_find_spots.csv"
_SITE_PLAN_PATH = _DATA_DIR / "ugarit_site_plan.geojson"
_UDB_TEXTS_PATH = _REPO_ROOT / "local_data" / "udb" / "texts.parquet"

_RS_RE = re.compile(r"RS\s*\.?\s*(\d+)\s*\.?\s*\[?(\d+[A-Za-z]?)\]?")


def _rs_key(text):
    """Normalise an RS excavation number, e.g. 'RS 1.001' -> '1.001'."""
    m = _RS_RE.search(str(text or ""))
    return f"{int(m.group(1))}.{m.group(2)}" if m else None


def load_site_plan():
    """Return the Ugarit excavation site plan as a GeoJSON dict (432 polygons).

    Coordinates are WGS84 lon/lat, ready for plotly / any web map.
    """
    with open(_SITE_PLAN_PATH, encoding="utf-8") as f:
        return json.load(f)


def _udb_genre_by_rs():
    """Map RS excavation number -> UDB genre, from the local UDB tables.

    Returns {} (with a hint) when the participant has not built UDB yet.
    """
    import pandas as pd

    if not _UDB_TEXTS_PATH.exists():
        print("UDB genres not found. Build them first with:\n"
              "  python -m workshop_tools.build_udb_parquet --pdf <your UDB pdf>")
        return {}
    texts = pd.read_parquet(_UDB_TEXTS_PATH)
    genre_by_rs = {}
    for genre, corr in zip(texts["genre"], texts["correspondences"]):
        if not isinstance(genre, str) or not genre.strip():
            continue
        for major, minor in _RS_RE.findall(str(corr)):
            genre_by_rs[f"{int(major)}.{minor}"] = genre
    return genre_by_rs


def _udb_ktu_by_rs():
    """Map RS excavation number -> UDB/KTU number, from the local UDB tables."""
    import pandas as pd

    if not _UDB_TEXTS_PATH.exists():
        return {}
    texts = pd.read_parquet(_UDB_TEXTS_PATH)
    ktu_by_rs = {}
    for ktu, corr in zip(texts["ktu"], texts["correspondences"]):
        if not isinstance(ktu, str) or not ktu.strip():
            continue
        label = ktu if ktu.upper().startswith("KTU") else f"KTU {ktu}"
        for major, minor in _RS_RE.findall(str(corr)):
            ktu_by_rs[f"{int(major)}.{minor}"] = label
    return ktu_by_rs


def load_find_spots(with_genre=False):
    """Return one row per tablet find spot as a DataFrame.

    Columns: name, lon, lat, language, script, area, uuid — the public ArcGIS
    fields the labs use. With ``with_genre=True`` a ``genre`` column is joined
    from the participant's local UDB tables (blank where unknown).
    """
    import pandas as pd

    df = pd.read_csv(_FIND_SPOTS_PATH, dtype=str)
    df["lon"] = df["lon"].astype(float)
    df["lat"] = df["lat"].astype(float)
    if with_genre:
        genre_by_rs = _udb_genre_by_rs()
        df["genre"] = df["name"].map(lambda n: genre_by_rs.get(_rs_key(n), ""))
    return df


_LOUVRE_PATH = _DATA_DIR / "Louvre_artifacts.csv"


def load_louvre():
    """Return the Louvre Ras Shamra/Ugarit catalogue as a DataFrame.

    1515 objects (tablets, vases, seals, figurines, ...) exported from
    collections.louvre.fr. Each row has an ``ARK`` id used to fetch the object
    page and its photos. An ``rs`` column with the RS excavation number is added
    where present, so Louvre objects can be joined to the find-spot data.
    """
    import pandas as pd

    df = pd.read_csv(_LOUVRE_PATH, sep=";", dtype=str, encoding="utf-8-sig").fillna("")
    df.columns = [c.strip() for c in df.columns]
    df["rs"] = df["Inventory number"].str.extract(
        r"(RS\s*\d+[.\s]\d+[A-Za-z']*)", expand=False)
    return df


def rs_keys(text):
    """All RS excavation numbers in a string, normalised to '<major>.<minor>'."""
    return {f"{int(a)}.{b}" for a, b in _RS_RE.findall(str(text or ""))}


_CATALOG_INDEX = None


def load_texts_catalog_index():
    """Map RS excavation number -> catalogue entry for quick tablet lookups.

    Each value is ``{ktu, title, description, category}`` parsed from the ISF
    ``ugaritic_texts_catalog.tsv`` (whose note field lists every siglum a tablet
    is known by, including its RS number). Lets any RS-bearing record — e.g. a
    Louvre object — be annotated with its KTU number, descriptive title, and a
    one-line description. Cached after the first read.
    """
    global _CATALOG_INDEX
    if _CATALOG_INDEX is not None:
        return _CATALOG_INDEX
    import csv

    index = {}
    if _CATALOG_PATH.exists():
        with open(_CATALOG_PATH, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                note = row.get("text_or_publication_number_note", "")
                m = _KTU_RE.search(note)
                info = {
                    "ktu": f"KTU {m.group(1)}" if m else "",
                    "title": (row.get("text_descriptive_title") or "").strip(),
                    "description": (row.get("text_description") or "").strip(),
                    "category": (row.get("category") or "").strip(),
                }
                for key in rs_keys(note):
                    index.setdefault(key, info)
    _CATALOG_INDEX = index
    return index


def sign_counts(texts):
    """Count cuneiform signs across the corpus (exact, from the unicode text).

    Returns a Counter keyed by the *Latin* sign label (e.g. 'b', 'ʿ', 'ṯ'),
    using the cuneiform codepoints so word dividers / breaks are excluded
    automatically.
    """
    alphabet = load_alphabet()
    char2sign = {row["char"]: row["sign"] for row in alphabet}
    counts = Counter()
    for t in texts:
        for line in t["ugaritic"]:
            for ch in line:
                if ch in char2sign:
                    counts[char2sign[ch]] += 1
    return counts


# ---------------------------------------------------------------------------
# Divination (notebook 3c)
# ---------------------------------------------------------------------------

def load_omen_tree():
    """Return the sheep-birth omen tree as a nested dict (KTU 1.103 material)."""
    with open(_OMEN_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_omen_text():
    """Return the teaching excerpt of the Ugaritic birth-omen text."""
    return _OMEN_TEXT_PATH.read_text(encoding="utf-8")


def load_babylonian_izbu_tree():
    """Return Šumma izbu Tablet I (human-birth omens) as a nested dict.

    The Babylonian "parent" of the Ugaritic sheep-birth omens
    (``load_omen_tree``). Transcribed from the Neo-/Late Babylonian exemplar
    MS 1808, ed. A. R. George, *Babylonian Divinatory Texts Chiefly in the
    Schøyen Collection* (CUSAS 18), 2013, no. 35, pp. 259-261.
    """
    with open(_BABYLONIAN_IZBU_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_babylonian_foetus_tree():
    """Return the Old Babylonian miscarried-foetus teratomancy omens (George
    2013, no. 12) as a nested dict.

    Organized by body feature; the *closest* genre parallel to the Ugaritic
    sheep-birth omens (both read an anomalous newborn body → fate of king and
    land). Sourced from the companion ``omens`` project.
    """
    with open(_BABYLONIAN_FOETUS_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_babylonian_celestial_tree():
    """Return the Babylonian lunar-eclipse (celestial) omens as a nested dict.

    Enūma Anu Enlil tradition (cf. George 2013, nos. 13-14); parallels the
    Ugaritic lunar omens (``load_ugaritic_lunar_tree``). Sourced from the
    companion ``omens`` project.
    """
    with open(_BABYLONIAN_CELESTIAL_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_ugaritic_lunar_tree():
    """Return the Ugaritic lunar omens as a nested dict.

    Pardee, *Ritual and Cult at Ugarit* (2002), text 44 = RIH 78/14
    (KTU 1.163) — a *different* tablet from the animal birth-omens in
    ``load_omen_tree``.
    """
    with open(_UGARITIC_LUNAR_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_ugaritic_dream_tree():
    """Return the Ugaritic dream omens (oneiromancy) as a nested dict.

    Pardee, *Ritual and Cult at Ugarit* (2002), text 45 = RS 18.041 —
    fragmentary; the meaning of items/animals seen in a dream.
    """
    with open(_UGARITIC_DREAM_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# `python -m workshop_tools.loader` → quick sanity check
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    texts = load_texts()
    by_genre = texts_by_genre(texts)
    print("\nTablets per genre:")
    for genre, items in sorted(by_genre.items(), key=lambda kv: -len(kv[1])):
        print(f"  {genre:20s} {len(items):3d}")
    counts = token_counts(texts)
    print(f"\nUnique word forms: {len(counts)}; top 10: {counts.most_common(10)}")
    sc = sign_counts(texts)
    print(f"\nMost frequent signs: {sc.most_common(8)}")
    print(f"Alphabet signs loaded: {len(load_alphabet())}")
