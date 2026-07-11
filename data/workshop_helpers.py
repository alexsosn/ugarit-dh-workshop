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


def metadata_bar(counts: pd.Series, title: str, n: int = 12, color: str = "#4c78a8"):
    """Interactive horizontal bar chart of a count Series (e.g. a value_counts()).

    The notebook does the *counting* in a visible cell (``value_counts()``) and
    passes the result here; this helper only handles the Plotly styling so the
    teaching cell stays about the numbers, not the plotting syntax.
    """
    import plotly.express as px

    top = counts.head(n)[::-1]                       # largest bar on top
    fig = px.bar(x=top.values, y=top.index, orientation="h", title=title,
                 color_discrete_sequence=[color])
    fig.update_layout(height=380, width=760, xaxis_title="texts", yaxis_title="",
                      margin=dict(l=210, r=40, t=50, b=30),
                      paper_bgcolor="white", plot_bgcolor="white")
    return fig


def metadata_stacked_bar(table: pd.DataFrame, title: str, top_cols: int = 8,
                         height=470):
    """Interactive stacked horizontal bars from a crosstab (rows × categories).

    ``table`` is a ``pd.crosstab`` (e.g. archive × language) built in the
    notebook; this helper only styles it. Archives are ordered by total size and
    rare categories fold into "other" so the legend stays readable — the point is
    the *composition* of each location, which a point-map cannot show.
    """
    import plotly.express as px

    tbl = table.copy()
    if tbl.shape[1] > top_cols:                       # fold the long tail
        keep = tbl.sum().sort_values(ascending=False).head(top_cols).index
        other = tbl.drop(columns=keep).sum(axis=1)
        tbl = tbl[keep]
        tbl["other"] = other
    tbl = tbl.loc[tbl.sum(axis=1).sort_values().index]      # largest on top
    long = tbl.reset_index().melt(id_vars=tbl.index.name or "index",
                                  var_name="category", value_name="texts")
    ycol = tbl.index.name or "index"
    fig = px.bar(long, x="texts", y=ycol, color="category", orientation="h",
                 title=title)
    fig.update_layout(barmode="stack", height=height, width=900,
                      yaxis_title="", xaxis_title="texts",
                      margin=dict(l=215, r=30, t=50, b=40),
                      paper_bgcolor="white", plot_bgcolor="white")
    return fig


def tablet_size_scatter(udb_texts: pd.DataFrame, color: str = "genre",
                        top: int = 8, height=520):
    """Scatter of tablet width vs height (cm), coloured by genre — from UDB.

    Uses the ``height``/``width`` columns of the locally-built UDB ``texts``
    table. Non-numeric or missing measurements are dropped. Only the ``top``
    most common genres are coloured; the rest fold into "other" so the legend
    stays readable.
    """
    import plotly.express as px

    df = udb_texts.copy()
    for col in ("height", "width"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["height", "width"])
    df = df[(df["height"] > 0) & (df["width"] > 0)]
    df[color] = df[color].fillna("").astype(str).str.strip().replace("", "unlabelled")
    keep = df[color].value_counts().head(top).index
    df["_c"] = df[color].where(df[color].isin(keep), "other")

    fig = px.scatter(
        df, x="width", y="height", color="_c",
        hover_data={"tablet": True, "ktu": True, "_c": False},
        title=f"Ugarit tablets: width vs height  ({len(df)} measured, coloured by {color})",
    )
    fig.update_traces(marker=dict(size=8, opacity=0.8))
    fig.update_layout(height=height, xaxis_title="width (cm)", yaxis_title="height (cm)",
                      legend_title_text=color,
                      paper_bgcolor="white", plot_bgcolor="white")
    return fig


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


_UGARITIC_FONT = None


def enable_ugaritic_font():
    """Let matplotlib render Ugaritic cuneiform signs (U+10380-U+1039F).

    matplotlib's default DejaVu Sans has no cuneiform glyphs, so any plot that
    labels points with the sign characters shows empty boxes (and warns about
    "missing glyph"). This registers a Ugaritic-capable font — the bundled
    ``data/fonts/NotoSansUgaritic-Regular.ttf`` (SIL OFL), or one already
    installed — and sets it as a fallback after DejaVu Sans, so Latin text and
    numbers are unaffected. Safe to call repeatedly; returns the font name used
    (or None if none was found).
    """
    global _UGARITIC_FONT
    if _UGARITIC_FONT:
        return _UGARITIC_FONT

    import matplotlib
    from matplotlib import font_manager as fm

    name = None
    bundled = DATA_DIR / "fonts" / "NotoSansUgaritic-Regular.ttf"
    if bundled.exists():
        fm.fontManager.addfont(str(bundled))
        name = fm.FontProperties(fname=str(bundled)).get_name()
    else:                                   # fall back to an installed font
        try:
            from fontTools.ttLib import TTFont
            for f in fm.fontManager.ttflist:
                try:
                    tt = TTFont(f.fname, fontNumber=0, lazy=True)
                    if any(0x10380 in tb.cmap for tb in tt["cmap"].tables):
                        name = f.name
                        break
                except Exception:
                    continue
        except Exception:
            name = None
    if not name:
        return None

    matplotlib.rcParams["font.family"] = ["DejaVu Sans", name]
    matplotlib.rcParams["axes.unicode_minus"] = False
    _UGARITIC_FONT = name
    return name


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
        plt.annotate(row.char, (row.complexity, row.frequency))
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


# ---------------------------------------------------------------------------
# Interactive Ugarit map (notebooks 1a / 1b)
# ---------------------------------------------------------------------------

# Esri World Imagery — the same satellite tiles the online RSTI viewer uses.
# Free to use, no API key/token required.
_ESRI_IMAGERY = ("https://server.arcgisonline.com/ArcGIS/rest/services/"
                 "World_Imagery/MapServer/tile/{z}/{y}/{x}")


def _plan_outline(site_plan: dict) -> tuple[list, list]:
    """Flatten every polygon ring into lon/lat lists, separated by None.

    One None-separated trace draws all 432 excavation outlines at once.
    """
    lons: list = []
    lats: list = []
    for feature in site_plan.get("features", []):
        geom = feature.get("geometry") or {}
        polys = geom.get("coordinates", [])
        if geom.get("type") == "Polygon":
            polys = [polys]
        for poly in polys:
            for ring in poly:
                for lon, lat in ring:
                    lons.append(lon)
                    lats.append(lat)
                lons.append(None)      # break between rings
                lats.append(None)
    return lons, lats


# Standard hover for every find-spot map (no coordinates). Fields, in order:
# KTU/UDB number · area · language · script · genre · name + description.
_HOVER_FIELDS = ["_ktu", "area", "language", "script", "_genre", "_detail"]
_HOVER_TEMPLATE = (
    "<b>%{customdata[0]}</b><br>"
    "Area: %{customdata[1]}<br>"
    "Language: %{customdata[2]}<br>"
    "Script: %{customdata[3]}<br>"
    "Genre: %{customdata[4]}<br>"
    "%{customdata[5]}"
    "<extra></extra>")


def _with_hover_cols(find_spots):
    """Attach the columns the standard find-spot tooltip needs.

    Adds ``ktu`` (from the ISF catalogue, falling back to UDB), ``genre`` (from
    UDB) and the catalogue's descriptive **title** and **description**, plus
    display versions with an em-dash for blanks. Existing ``genre``/``ktu``
    columns are kept, so ``load_find_spots(with_genre=True)`` still works.
    """
    from data.loader import (load_texts_catalog_index, _rs_key,
                             _udb_genre_by_rs, _udb_ktu_by_rs, _UDB_TEXTS_PATH)

    df = find_spots.copy()
    have_udb = _UDB_TEXTS_PATH.exists()
    catalog = load_texts_catalog_index()
    keys = df["name"].map(_rs_key)

    if "ktu" not in df.columns:
        udb_ktu = _udb_ktu_by_rs() if have_udb else {}
        df["ktu"] = keys.map(
            lambda k: (catalog.get(k) or {}).get("ktu") or udb_ktu.get(k) or "")
    if "genre" not in df.columns:
        genre_by_rs = _udb_genre_by_rs() if have_udb else {}
        df["genre"] = keys.map(lambda k: genre_by_rs.get(k, ""))

    # Descriptive title + one-line description from the ISF texts catalogue.
    df["title"] = keys.map(lambda k: (catalog.get(k) or {}).get("title", ""))
    df["description"] = keys.map(lambda k: (catalog.get(k) or {}).get("description", ""))

    for col in ("area", "language", "script"):
        if col not in df.columns:
            df[col] = ""
    df["_ktu"] = df["ktu"].fillna("").replace("", "—")
    df["_genre"] = df["genre"].fillna("").replace("", "—")

    def _clean(value):
        # Plotly hover renders a few tags (<br>, <b>, <i>) but not HTML
        # entities, so keep literal text and just neutralise stray angle
        # brackets that would otherwise be read as tags.
        return str(value or "").replace("<", "(").replace(">", ")")

    def _detail(row):
        # Bottom of the tooltip: find number, catalogue name, description.
        line = _clean(row["name"])
        title = _clean(row["title"])
        desc = _clean(row["description"])
        if title:
            line += " — " + title
        if desc:
            line += "<br><i>" + desc + "</i>"
        return line

    df["_detail"] = df.apply(_detail, axis=1)
    return df


def finds_map(find_spots, color="language", site_plan=None, basemap="satellite",
              title=None, top=8, drop_blank=True, zoom=15.2, height=560):
    """Interactive map of Ugarit tablet find spots, coloured by one column.

    Parameters
    ----------
    find_spots : DataFrame from ``loader.load_find_spots()`` (needs lon, lat,
        name and the ``color`` column).
    color      : which column decides the point colour — "language", "script",
        "area", or "genre" (load with ``with_genre=True`` first).
    site_plan  : optional GeoJSON from ``loader.load_site_plan()`` to draw the
        excavation outlines under the points.
    basemap    : "satellite" (Esri imagery) or "light" (plain Carto map).

    Returns a plotly figure — call ``.show()`` on it.
    """
    import plotly.express as px
    import plotly.graph_objects as go

    data = _with_hover_cols(find_spots)
    data[color] = data[color].fillna("").astype(str).str.strip()
    if drop_blank:
        data = data[data[color] != ""]
    # Fold the long tail into "other" in a *separate* column, so the tooltip
    # still shows each point's real language/script/genre.
    keep = data[color].value_counts().head(top).index
    data["_color"] = data[color].where(data[color].isin(keep), "other")

    fig = px.scatter_map(
        data, lat="lat", lon="lon", color="_color",
        custom_data=_HOVER_FIELDS,
        center=dict(lat=data["lat"].mean(), lon=data["lon"].mean()),
        zoom=zoom, height=height,
        title=title or f"Ugarit find spots by {color}  ({len(data)} tablets)",
    )
    fig.update_traces(marker=dict(size=7, opacity=0.85),
                      hovertemplate=_HOVER_TEMPLATE)

    if site_plan is not None:
        lons, lats = _plan_outline(site_plan)
        fig.add_trace(go.Scattermap(
            lon=lons, lat=lats, mode="lines", name="excavation plan",
            line=dict(width=1, color="rgba(255,235,180,0.7)"),
            hoverinfo="skip"))

    # Basemap: satellite imagery, or a plain light map (switch with basemap=).
    if basemap == "satellite":
        fig.update_layout(map=dict(style="white-bg", layers=[dict(
            below="traces", sourcetype="raster", source=[_ESRI_IMAGERY],
            sourceattribution="Esri, Maxar, Earthstar Geographics")]))
    else:
        fig.update_layout(map=dict(style="carto-positron"))

    fig.update_layout(legend_title_text=color,
                      margin=dict(l=0, r=0, t=45, b=0))
    return fig


def _campaign_of(name: str):
    """RS excavation number -> campaign label, e.g. 'RS 16.201' -> 16.

    The first component of an RS number is the excavation campaign. Early
    campaigns are counted 1, 2, 3, ...; later ones switch to the two- or
    four-digit year (RS 94.xxxx = 1994, RS 2000.xxxx = 2000). Sorting these
    integers ascending still gives the correct chronological order.
    """
    m = re.match(r"\s*RS\s+(\d+)\.", str(name or ""))
    return int(m.group(1)) if m else None


def _campaign_year(campaign) -> int:
    """RS campaign number -> calendar year (approximate for post-war campaigns).

    Ras Shamra was dug annually 1929-1939 (campaigns 1-11), interrupted by the
    war, then resumed in 1948 (campaigns 12-34, C.F.A. Schaeffer, to ~1970).
    Later excavation numbers are already the year: RS 75 = 1975 ... RS 94 = 1994
    (Maison d'Ourtenou), and RS 2000-2002 are literal years.
    """
    c = int(campaign)
    if c >= 1000:          # already a four-digit year (RS 2000, 2001, 2002)
        return c
    if c >= 75:            # two-digit year form: RS 75 = 1975 ... RS 99 = 1999
        return 1900 + c
    if c <= 11:            # 1st-11th campaigns, 1929-1939 (annual, pre-war)
        return 1928 + c
    return 1936 + c        # post-war resumption in 1948 (campaign 12); approx


def excavation_animation(find_spots, basemap="satellite", height=600):
    """Animated map of tablet discovery, campaign by campaign.

    Each frame adds the tablets found in one RS campaign: points found in the
    current campaign are highlighted, everything found earlier stays on the map
    dimmed — so pressing ▶ "fills up" the tell as the excavation progresses.

    Only find spots with a readable RS campaign number are shown (Varia / Ras
    Ibn Hani have no campaign in their number and are left out).
    """
    import plotly.graph_objects as go

    df = _with_hover_cols(find_spots)
    df["campaign"] = df["name"].map(_campaign_of)
    df = df.dropna(subset=["campaign"]).astype({"campaign": int})
    df["year"] = df["campaign"].map(_campaign_year)
    campaigns = sorted(df["campaign"].unique())
    year_of = {c: _campaign_year(c) for c in campaigns}

    earlier_rgba, new_rgba = "rgba(37,99,235,0.75)", "#e4572e"  # blue past, red new

    def snapshot(current):
        """One frame: every tablet found so far; this campaign highlighted."""
        seen = df[df["campaign"] <= current]
        is_new = seen["campaign"] == current
        return go.Scattermap(
            lat=seen["lat"], lon=seen["lon"], mode="markers",
            marker=dict(size=[12 if n else 6 for n in is_new],
                        color=[new_rgba if n else earlier_rgba for n in is_new]),
            customdata=seen[_HOVER_FIELDS].to_numpy(),
            hovertemplate=_HOVER_TEMPLATE, showlegend=False)

    # One point-trace we redraw each frame + two static legend swatches. Keeping
    # the point data in a single trace avoids plotly's animation trace-mismatch
    # when a category (e.g. "found earlier") is absent from the first frame.
    def swatch(color, label):
        return go.Scattermap(lat=[None], lon=[None], mode="markers",
                             marker=dict(size=11, color=color), name=label)

    fig = go.Figure(
        data=[snapshot(campaigns[0]),
              swatch(earlier_rgba, "found earlier"),
              swatch(new_rgba, "this season")],
        frames=[go.Frame(name=str(year_of[c]), data=[snapshot(c)], traces=[0])
                for c in campaigns],
    )

    play = dict(frame=dict(duration=700, redraw=True), fromcurrent=True,
                transition=dict(duration=300))
    stop = dict(frame=dict(duration=0, redraw=False), mode="immediate")
    steps = [dict(method="animate", label=str(year_of[c]),
                  args=[[str(year_of[c])], dict(mode="immediate",
                        frame=dict(duration=0, redraw=True),
                        transition=dict(duration=0))])
             for c in campaigns]

    fig.update_layout(
        height=height, title="Excavation of Ugarit, season by season  (press ▶)",
        margin=dict(l=0, r=0, t=45, b=0),
        legend=dict(x=0.99, y=0.99, xanchor="right", yanchor="top",
                    bgcolor="rgba(255,255,255,0.7)"),
        updatemenus=[dict(type="buttons", direction="left", showactive=False,
            x=0.02, y=0.05, xanchor="left", yanchor="bottom",
            buttons=[dict(label="▶ Play", method="animate", args=[None, play]),
                     dict(label="⏸ Pause", method="animate", args=[[None], stop])])],
        sliders=[dict(active=0, x=0.12, len=0.86, y=0.04,
                      currentvalue=dict(prefix="Year "), steps=steps)],
    )

    map_kw = dict(center=dict(lat=df["lat"].mean(), lon=df["lon"].mean()), zoom=15)
    if basemap == "satellite":
        map_kw.update(style="white-bg", layers=[dict(
            below="traces", sourcetype="raster", source=[_ESRI_IMAGERY],
            sourceattribution="Esri, Maxar, Earthstar Geographics")])
    else:
        map_kw.update(style="carto-positron")
    fig.update_layout(map=map_kw)
    return fig


def excavation_curve(find_spots):
    """Cumulative count of tablets discovered, season by season (line chart).

    A simple companion to ``excavation_animation`` — the same story as a curve.
    """
    import plotly.express as px

    df = find_spots.copy()
    df["campaign"] = df["name"].map(_campaign_of)
    df = df.dropna(subset=["campaign"]).astype({"campaign": int})
    df["year"] = df["campaign"].map(_campaign_year)
    per = df.groupby("year").size().sort_index().rename("found")
    out = per.reset_index()
    out["cumulative"] = per.cumsum().values

    fig = px.area(out, x="year", y="cumulative", markers=True,
                  title="Tablets discovered at Ugarit (cumulative, by season)")
    fig.update_layout(height=380, xaxis_title="excavation year",
                      yaxis_title="tablets found (running total)",
                      margin=dict(l=60, r=20, t=50, b=50),
                      paper_bgcolor="white", plot_bgcolor="white")
    return fig


# ---------------------------------------------------------------------------
# Louvre object gallery (notebook 1a) — photographs from collections.louvre.fr
# ---------------------------------------------------------------------------

_LOUVRE_CACHE = DATA_DIR / "_cache" / "louvre"


def _louvre_image_url(ark: str, size: str = "small"):
    """Resolve a Louvre ARK id to its first photo URL via the public JSON API.

    Metadata is cached under data/_cache/louvre/ so a re-run hits no network.
    Returns None when the object has no photo. ``size``: 'small' thumbnail or
    'large'.
    """
    import json
    import urllib.request

    _LOUVRE_CACHE.mkdir(parents=True, exist_ok=True)
    cached = _LOUVRE_CACHE / f"{ark}.json"
    if cached.exists():
        data = json.loads(cached.read_text(encoding="utf-8"))
    else:
        url = f"https://collections.louvre.fr/ark:/53355/{ark}.json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (workshop)"})
        try:
            raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
        except Exception:
            return None
        cached.write_text(raw, encoding="utf-8")
        data = json.loads(raw)
    images = data.get("image") or []
    if not images:
        return None
    key = "urlThumbnail" if size == "small" else "urlImage"
    return images[0].get(key)


def louvre_gallery(louvre, query="tablette", n=12, cols=4, seed=0, size="small"):
    """Grid of Louvre object photos — to show the diversity of forms.

    Parameters
    ----------
    louvre : DataFrame from ``loader.load_louvre()``.
    query  : keep only objects whose title contains this word, case-insensitive
             ("tablette", "figurine", "vase", "sceau", ...). None keeps all.
    n      : how many objects to show (a fixed random sample, so the grid is
             varied but reproducible).
    cols   : columns in the grid.

    Each object is annotated, where known, with its KTU number, genre and a
    one-line description (from the ISF texts catalogue and, if built, the local
    UDB genres) — hover over a photo to read it.

    Photos are loaded straight from collections.louvre.fr (needs internet), so
    nothing copyrighted is stored in the repo. Returns an IPython HTML object.
    """
    import html as _html

    from IPython.display import HTML

    from data.loader import (load_texts_catalog_index, rs_keys,
                             _udb_genre_by_rs, _UDB_TEXTS_PATH)

    df = louvre
    if query:
        df = df[df["Object name/Title"].str.contains(query, case=False, na=False)]
    if len(df) > n:
        df = df.sample(n, random_state=seed)

    catalog = load_texts_catalog_index()
    genre_by_rs = _udb_genre_by_rs() if _UDB_TEXTS_PATH.exists() else {}

    cards = []
    for _, row in df.iterrows():
        ark = row["ARK"]
        img = _louvre_image_url(ark, size=size)
        if not img:
            continue
        page = f"https://collections.louvre.fr/en/ark:/53355/{ark}"
        inv = (row.get("Inventory number", "") or "").split(";")[0].strip()
        title = (row.get("Object name/Title", "") or "").strip()

        # Annotate from the RS number(s) in the inventory field.
        keys = rs_keys(row.get("Inventory number", ""))
        entry = next((catalog[k] for k in keys if k in catalog), {})
        ktu = entry.get("ktu", "")
        genre = (next((genre_by_rs[k] for k in keys if k in genre_by_rs), "")
                 or entry.get("category", ""))
        desc = entry.get("description", "") or entry.get("title", "")

        # Multi-line native tooltip (KTU · genre, then description).
        lines = [title]
        tag = " · ".join(x for x in (ktu, genre) if x)
        if tag:
            lines.append(tag)
        if desc:
            lines.append(desc)
        tip = "&#10;".join(_html.escape(x) for x in lines if x)
        caption = inv + (f'<br><span style="color:#777">{_html.escape(ktu)}</span>'
                         if ktu else "")

        cards.append(
            f'<figure style="margin:0;text-align:center">'
            f'<a href="{page}" target="_blank" title="{tip}">'
            f'<img src="{img}" loading="lazy" alt="{_html.escape(inv)}" '
            f'style="width:100%;height:160px;object-fit:contain;'
            f'background:#f4f4f4;border-radius:4px"></a>'
            f'<figcaption style="font-size:11px;color:#333;margin-top:3px">'
            f'{caption}</figcaption>'
            f'</figure>')

    grid = (f'<div style="display:grid;'
            f'grid-template-columns:repeat({cols},1fr);gap:10px">'
            + "".join(cards) + "</div>")
    credit = ('<div style="font-size:10px;color:#888;margin-top:8px">'
              f'{len(cards)} objects from the Mus&eacute;e du Louvre '
              '(&copy; Mus&eacute;e du Louvre / GrandPalaisRmn &mdash; '
              'collections.louvre.fr). '
              'Click a photo to open its catalogue page.</div>')
    return HTML(grid + credit)
