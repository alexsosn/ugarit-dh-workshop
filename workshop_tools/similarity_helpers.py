"""Reusable helpers for the similarity and genre-map notebooks."""

from __future__ import annotations

import re

import pandas as pd
import plotly.graph_objects as go

from workshop_tools.loader import load_catalog_titles, resolve_to_ktu

HOVER_FIELDS = ["title", "genre", "ktu_genre", "words", "preview"]
HOVER_LABELS = {
    "title": "Title",
    "genre": "Genre",
    "ktu_genre": "KTU genre",
    "words": "Words",
    "preview": "Text",
}
MISSING = "-"


def hover_config(z: bool = False) -> dict:
    """Uniform Plotly hover settings for every genre map."""
    hover_data = {"x": False, "y": False}
    if z:
        hover_data["z"] = False
    for field in HOVER_FIELDS:
        hover_data[field] = True
    return {
        "hover_name": "label",
        "hover_data": hover_data,
        "labels": HOVER_LABELS,
    }


def _ktu_num(value) -> str | None:
    """Pull the bare KTU number from values such as 'KTU 1.4'."""
    match = re.search(r"\d+\.\d+", str(value))
    return match.group(0) if match else None


def _preview(refs, lines: list[str], n: int = 3, width: int = 140) -> str:
    """Return a short hover-card text preview."""
    if refs:
        snippet = "<br>".join(f"{ref}: {line}" for ref, line in zip(refs[:n], lines[:n]))
        return snippet or MISSING

    text = " ".join(lines) if lines else ""
    if len(text) > width:
        return text[:width] + "..."
    return text or MISSING


def cuc_frame(sample: list[dict], **coords) -> pd.DataFrame:
    """Build standard map/hover columns from CUC tablet dictionaries."""
    frame = {
        "label": [f"KTU {text['ktu']}" for text in sample],
        "KTU": [text["ktu"] for text in sample],
        "title": [text["name"] for text in sample],
        "genre": [text["genre"] for text in sample],
        "ktu_genre": [text["genre"] for text in sample],
        "words": [len(text["tokens"]) for text in sample],
        "preview": [_preview(text["refs"], text["lines"]) for text in sample],
    }
    frame.update(coords)
    return pd.DataFrame(frame)


def udb_frame(udb: pd.DataFrame, **coords) -> pd.DataFrame:
    """Build the same standard map/hover columns from UDB tablet rows."""
    titles = load_catalog_titles()
    ktu_numbers = [_ktu_num(ktu) for ktu in udb["ktu"]]
    frame = {
        "label": [
            f"UDB {tablet}" + (f" = KTU {ktu}" if ktu else "")
            for tablet, ktu in zip(udb["tablet"], ktu_numbers)
        ],
        "KTU": [ktu or MISSING for ktu in ktu_numbers],
        "UDB": list(udb["tablet"]),
        "title": [titles.get(ktu, MISSING) for ktu in ktu_numbers],
        "genre": list(udb["genre"]),
        "ktu_genre": list(udb["ktu_genre"]),
        "words": list(udb["n_tokens"]),
        "preview": [_preview(None, [text], width=30) for text in udb["text"]],
    }
    frame.update(coords)
    return pd.DataFrame(frame)


def spotlight(fig, df: pd.DataFrame, query, coords: tuple[str, ...] = ("x", "y")):
    """Ring and label tablets matching a KTU, UDB, siglum, or title query."""
    query_text = str(query).strip()
    mask = pd.Series(False, index=df.index)

    ktu = resolve_to_ktu(query_text)
    if ktu and "KTU" in df.columns:
        mask |= df["KTU"].astype(str).str.strip() == ktu

    for column in ("KTU", "UDB"):
        if column in df.columns:
            mask |= df[column].astype(str).str.strip().str.lower() == query_text.lower()

    if "title" in df.columns:
        mask |= df["title"].astype(str).str.contains(
            re.escape(query_text),
            case=False,
            na=False,
        )

    hits = df[mask]
    if hits.empty:
        print(
            f"Warning: {query!r} is not on this map. It may be absent from this "
            "corpus or have fewer than 30 words."
        )
        return hits

    tag = hits["KTU"].astype(str) if "KTU" in hits.columns else hits["label"].astype(str)
    if "UDB" in hits.columns:
        tag = tag.where(tag != MISSING, "UDB " + hits["UDB"].astype(str))

    is_3d = len(coords) == 3
    marker = (
        {"size": 10, "color": "black", "symbol": "circle-open", "line": {"width": 2}}
        if is_3d
        else {"size": 20, "color": "rgba(0,0,0,0)", "line": {"width": 3, "color": "black"}}
    )
    scatter = go.Scatter3d if is_3d else go.Scatter
    fig.add_trace(
        scatter(
            mode="markers+text",
            name=f"* {query}",
            marker=marker,
            text=tag,
            textposition="top center",
            textfont={"size": 12, "color": "black"},
            hoverinfo="skip",
            showlegend=True,
            **{coord: hits[coord] for coord in coords},
        )
    )
    print(f"Highlighted {len(hits)} tablet(s): {', '.join(tag)}")
    return hits
