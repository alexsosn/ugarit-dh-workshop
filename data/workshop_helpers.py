"""Small teaching helpers used by the workshop notebooks.

The notebooks should foreground the research question. These functions keep
repeated data preparation and plotting details out of beginner-facing cells.
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from data import analyse
from data.loader import load_alphabet, sign_counts, texts_by_genre

DATA_DIR = Path(__file__).resolve().parent
UGARIT_DATABASE = DATA_DIR / "UGARIT_TEXTS_DATABASE.csv"

SOUTH_SEMITIC_ORDER = [
    "h", "l", "ḥ", "m", "q", "w", "š", "r", "t", "s",
    "k", "n", "ḫ", "b", "p", "a", "ʿ", "ẓ", "g", "d",
    "ġ", "ṭ", "z", "ḏ", "y", "ṯ", "ṣ", "i", "u", "s2",
]


def find_tablet(texts: list[dict], ktu: str) -> dict:
    """Return the tablet with this KTU number."""
    return next(text for text in texts if text["ktu"] == ktu)


def corpus_counts(texts: list[dict]) -> pd.Series:
    """Count the object types introduced in notebook 1a."""
    return pd.Series({
        "tablets": len(texts),
        "lines": sum(len(text["lines"]) for text in texts),
        "words": sum(len(text["tokens"]) for text in texts),
        "signs": sum(sign_counts(texts).values()),
    })


def genre_table(texts: list[dict]) -> pd.DataFrame:
    """Table of CUC genre counts with a few example KTU numbers."""
    rows = []
    for genre, items in texts_by_genre(texts).items():
        rows.append({
            "genre": genre,
            "tablets": len(items),
            "examples": ", ".join(text["ktu"] for text in items[:5]),
        })
    return (
        pd.DataFrame(rows)
        .sort_values("tablets", ascending=False)
        .reset_index(drop=True)
    )


def tablets_with_word(texts: list[dict], word: str) -> list[str]:
    """KTU numbers of tablets containing a cleaned word form."""
    return [text["ktu"] for text in texts if word in text["tokens"]]


def lines_with_word(text: dict, word: str) -> list[tuple[str, str]]:
    """Reference and line pairs where a tablet contains a word form."""
    hits = []
    for ref, line in zip(text["refs"], text["lines"]):
        if word in line.replace(".", " ").split():
            hits.append((ref, line))
    return hits


def load_ugarit_database() -> pd.DataFrame:
    """Load the broader Ugarit Texts Database used for the 1a zoom-out."""
    return pd.read_csv(
        UGARIT_DATABASE,
        encoding="utf-8",
        delimiter=";",
        dtype=str,
        index_col=0,
    )


def _ktu_genre(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    match = re.match(r"\d+", value.strip().split(".")[0])
    if not match:
        return None
    return analyse.ktu_classification.get(int(match.group()))


def excavated_metadata(db: pd.DataFrame) -> pd.DataFrame:
    """Return simplified genre/language/archive columns for the larger database."""
    archive = db["Archive/General area"].fillna(db["SAU Archive/General area"])
    return pd.DataFrame({
        "genre": db["KTU3"].map(_ktu_genre),
        "language": db["UTDB Language"]
        .map(lambda value: analyse.normalise_lang(value, use_multilingual=True))
        .replace("", "unknown/unassigned"),
        "archive": archive.fillna("Other/unknown"),
    })


def top_counts(meta: pd.DataFrame, column: str) -> pd.Series:
    """Most common values in one metadata column."""
    return meta[column].dropna().value_counts()


def barh(series: pd.Series, title: str, n: int = 12):
    """Simple horizontal bar chart for count Series."""
    _, ax = plt.subplots(figsize=(8, 4))
    series.head(n).sort_values().plot.barh(ax=ax, title=title)
    ax.set_xlabel("texts")
    ax.set_ylabel("")
    plt.tight_layout()
    return ax


def archive_by(meta: pd.DataFrame, column: str, top: int = 10) -> pd.DataFrame:
    """Cross-tabulate the main archives by language or genre."""
    main_archives = meta["archive"].value_counts().head(top).index
    small = meta[meta["archive"].isin(main_archives)]
    return pd.crosstab(small["archive"], small[column])


def stacked_barh(table: pd.DataFrame, title: str):
    """Simple stacked horizontal bar chart for a cross-tab table."""
    _, ax = plt.subplots(figsize=(10, 5))
    table.loc[table.sum(axis=1).sort_values().index].plot.barh(
        ax=ax,
        stacked=True,
        title=title,
    )
    ax.set_xlabel("texts")
    ax.set_ylabel("")
    plt.tight_layout()


def alphabet_frequency_table(texts: list[dict]) -> pd.DataFrame:
    """Alphabet table plus sign frequency from the loaded corpus."""
    alpha = pd.DataFrame(load_alphabet())
    counts = sign_counts(texts)
    alpha["frequency"] = alpha["sign"].map(counts).fillna(0).astype(int)
    return alpha


def plot_sign_frequency(alpha: pd.DataFrame, order_col: str = "position"):
    """Bar chart of sign frequency in the current alphabet order."""
    ordered = alpha.sort_values(order_col)
    plt.figure(figsize=(11, 4))
    plt.bar(ordered["sign"], ordered["frequency"])
    plt.xlabel("sign order")
    plt.ylabel("frequency")
    plt.title("Ugaritic sign frequency")
    plt.show()


def plot_complexity(alpha: pd.DataFrame):
    """Scatter plot for complexity vs. frequency."""
    plt.figure(figsize=(7, 5))
    plt.scatter(alpha["complexity"], alpha["frequency"])
    for row in alpha.itertuples():
        plt.annotate(row.sign, (row.complexity, row.frequency))
    plt.xlabel("complexity (wedges + turns)")
    plt.ylabel("frequency")
    plt.title("Are frequent signs simpler?")
    plt.show()


def apply_south_order(alpha: pd.DataFrame, south_order: list[str]) -> pd.DataFrame:
    """Add South Semitic alphabet positions after validating a learner list."""
    missing = sorted(set(alpha["sign"]) - set(south_order))
    extra = sorted(set(south_order) - set(alpha["sign"]) - {"TODO"})
    duplicates = sorted({
        sign for sign in south_order
        if sign != "TODO" and south_order.count(sign) > 1
    })
    todos = [i for i, sign in enumerate(south_order, start=1) if sign == "TODO"]
    if todos or missing or extra or duplicates or len(south_order) != len(alpha):
        raise ValueError(
            "Check the South Semitic list: "
            f"TODO positions={todos}, missing={missing}, "
            f"extra={extra}, duplicates={duplicates}."
        )

    positions = {sign: pos for pos, sign in enumerate(south_order, start=1)}
    south = alpha.copy()
    south["south_position"] = south["sign"].map(positions)
    return south.sort_values("south_position")


def genre_alphabet_test(texts: list[dict], genre: str, alpha: pd.DataFrame) -> pd.Series:
    """Correlation check for one CUC genre."""
    subset = [text for text in texts if text["genre"] == genre]
    counts = sign_counts(subset)
    frequency = alpha["sign"].map(counts).fillna(0).astype(int)
    return pd.Series({
        "tablets": len(subset),
        "position_vs_frequency": alpha["position"].corr(frequency),
        "complexity_vs_frequency": alpha["complexity"].corr(frequency),
    })
