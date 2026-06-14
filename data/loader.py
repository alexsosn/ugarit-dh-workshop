"""
Data loader for the Ugarit DH workshop — backed by the REAL corpus.
===================================================================

The notebooks use the **Copenhagen Ugaritic Corpus (CUC)** through line-level
JSONL files hosted on HuggingFace (``AlexWalhai/cuc``). Every notebook calls
``load_texts()`` and gets a uniform list of tablets back. The first run downloads
the JSONL files into a local cache; later runs reuse that cache.

  Source : CUC, CACCHT project (DT-UCPH/cuc), Text-Fabric export → JSONL
           at https://huggingface.co/datasets/AlexWalhai/cuc.
  Licence: Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0).
           Educational / non-commercial use only — see data/README.md.

Each tablet is returned as a dictionary with the same keys:

    {
        "ktu":      "1.3",                 # KTU text number
        "title":    "KTU 1.3",             # label
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
    from data.loader import load_texts
    texts = load_texts()
    print(len(texts), "tablets")
"""

from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ALPHABET_PATH = _HERE / "alphabet.json"
_OMEN_PATH = _HERE / "omens" / "sheep_birth_omens.json"
_HF_DATASET = "AlexWalhai/cuc"
_HF_API_URL = f"https://huggingface.co/api/datasets/{_HF_DATASET}"
_HF_RAW_BASE = f"https://huggingface.co/datasets/{_HF_DATASET}/resolve/main"
_CACHE_MANIFEST = ".cuc-jsonl-manifest.json"
_CACHE_DIR = Path(
    os.environ.get(
        "UGARIT_CUC_CACHE",
        Path.home() / ".cache" / "ugarit-dh-workshop" / "cuc-jsonl",
    )
)

# Characters that are not part of a word form (restorations, breaks, dividers).
_STRIP_CHARS = "[]()<>!?*/\\"
_DIVIDER = "."          # Ugaritic word divider in the Latin transliteration
_BROKEN = re.compile(r"^x+$", re.IGNORECASE)   # x, xx, xxxxx … = broken signs


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

def _remote_jsonl_filenames():
    """Return the JSONL filenames available in the HuggingFace CUC dataset."""
    try:
        with urlopen(_HF_API_URL, timeout=30) as response:
            meta = json.loads(response.read().decode("utf-8"))
    except URLError as exc:
        raise RuntimeError(
            "Could not fetch the CUC file list from HuggingFace. "
            "Check your internet connection or set UGARIT_CUC_CACHE to a "
            "directory containing the CUC JSONL files."
        ) from exc

    names = [
        item["rfilename"]
        for item in meta.get("siblings", [])
        if item.get("rfilename", "").endswith(".jsonl")
    ]
    if not names:
        raise RuntimeError(f"No JSONL files found in HuggingFace dataset {_HF_DATASET}.")
    return sorted(names)


def _download_jsonl(filename: str, destination: Path):
    """Download one JSONL file from HuggingFace into the local cache."""
    url = f"{_HF_RAW_BASE}/{quote(filename)}"
    try:
        with urlopen(url, timeout=60) as response:
            destination.write_bytes(response.read())
    except URLError as exc:
        raise RuntimeError(f"Could not download CUC file {filename!r} from {url}.") from exc


def _jsonl_paths():
    """Return local cached paths for all remote CUC JSONL files."""
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = _CACHE_DIR / _CACHE_MANIFEST

    names = None
    if manifest_path.exists():
        with open(manifest_path, encoding="utf-8") as f:
            names = json.load(f).get("files", [])
        if names and all((_CACHE_DIR / name).exists() for name in names):
            return [_CACHE_DIR / name for name in names]

    names = _remote_jsonl_filenames()
    missing = [
        name for name in names
        if not (_CACHE_DIR / name).exists() or (_CACHE_DIR / name).stat().st_size == 0
    ]
    if missing:
        with ThreadPoolExecutor(max_workers=16) as pool:
            futures = {
                pool.submit(_download_jsonl, name, _CACHE_DIR / name): name
                for name in missing
            }
            for future in as_completed(futures):
                future.result()

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"dataset": _HF_DATASET, "files": names}, f, indent=2)
    return [_CACHE_DIR / name for name in names]


def load_texts(genres=None, min_tokens=1, verbose=True):
    """Load the CUC corpus as a list of tablet dictionaries.

    genres:     optional iterable of genre labels to keep (e.g. ["letter", "myth"]).
    min_tokens: drop tablets with fewer than this many word tokens (skip scraps).
    verbose:    print a one-line summary.
    """
    texts = []
    for path in _jsonl_paths():
        ktu = path.stem.replace("KTU ", "").strip()
        lines, ugaritic, refs, tokens = [], [], [], []
        with open(path, encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                rec = json.loads(raw)
                latin = rec.get("text", "")
                lines.append(latin)
                ugaritic.append(rec.get("ugaritic_text", ""))
                refs.append(rec.get("ref", ""))
                tokens.extend(clean_tokens(latin))
        if len(tokens) < min_tokens:
            continue
        texts.append({
            "ktu": ktu,
            "title": f"KTU {ktu}",
            "genre": _genre_for(ktu),
            "language": "ugaritic",
            "lines": lines,
            "ugaritic": ugaritic,
            "refs": refs,
            "tokens": tokens,
            "source": "cuc",
        })

    if genres is not None:
        wanted = set(genres)
        texts = [t for t in texts if t["genre"] in wanted]

    if verbose:
        n_tok = sum(len(t["tokens"]) for t in texts)
        print(f"[loader] Loaded {len(texts)} CUC tablets, {n_tok} word tokens "
              f"(source: {_HF_DATASET} JSONL cache, licence: CC BY-NC 4.0).")
    return texts


def texts_by_genre(texts):
    """Group a text list into {genre: [texts]}."""
    grouped = {}
    for t in texts:
        grouped.setdefault(t["genre"], []).append(t)
    return grouped


def all_tokens(texts):
    """Flatten every word token from every tablet into one list."""
    out = []
    for t in texts:
        out.extend(t["tokens"])
    return out


def token_counts(texts):
    """collections.Counter of word-form frequencies across the corpus."""
    return Counter(all_tokens(texts))


def text_as_string(text):
    """One tablet's word tokens as a single space-separated string (for TF-IDF)."""
    return " ".join(text["tokens"])


def corpus_as_documents(texts):
    """Return (labels, documents) parallel lists for TF-IDF / clustering.

    labels    — KTU numbers; documents — one cleaned string per tablet.
    """
    labels = [t["ktu"] for t in texts]
    documents = [text_as_string(t) for t in texts]
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


# ---------------------------------------------------------------------------
# `python data/loader.py` → quick sanity check
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
