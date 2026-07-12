"""High-level tools for divine-name proximity networks in the Baal Cycle.

This module deliberately hides file discovery, TSV parsing, entity
normalisation, provenance bookkeeping, and the HTML/JavaScript renderer.  The
teaching notebook can therefore foreground the philological model:

    corpus = load_baal_cycle()
    graph = build_divine_name_graph(corpus, max_distance=3)
    show_divine_name_network(graph)
    find_maximal_cliques(graph)

The public functions retain auditable dataframes and KTU references so the
convenient API does not turn the analysis into a black box.
"""

from __future__ import annotations

import html
import json
import re
import warnings
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable, Mapping

import networkx as nx
import pandas as pd

from workshop_tools.network_viz import vis_network_javascript


_REPO_ROOT = Path(__file__).resolve().parent.parent
_BUNDLED_SOURCE = _REPO_ROOT / "data" / "baal_cycle"
_BUNDLED_OVERRIDES = _BUNDLED_SOURCE / "onomastic_gloss_overrides.tsv"
_REF_RE = re.compile(
    r"^KTU (?P<tablet>\d+\.\d+) (?P<column>[IVX]+):(?P<line>\d+)[a-z]?$"
)
_DN_RE = re.compile(r"(?<!\w)DN(?!\w)")


DEFAULT_ALIASES = {
    # Baal / Haddu and attached or titular forms
    "bˤlm": "bˤl", "lbˤl": "bˤl", "hd": "bˤl", "hdxt": "bˤl",
    "dmrn": "bˤl", "ˤlm": "bˤl",
    # El
    "ilk": "il", "ilxx": "il", "id": "il",
    # Athirat
    "aṯ": "aṯrt", "rt": "aṯrt", "aṯtrt": "aṯrt",
    # Yammu / Naharu
    "ymm": "ym", "nhr": "ym", "nhrm": "ym", "yw": "ym",
    # Kothar-wa-Hasis
    "kṯrm": "kṯr", "ḫss": "kṯr", "wḫss": "kṯr", "hyn": "kṯr",
    # Minor orthographic/attached variants
    "tṭly": "ṭly", "šnnm": "šnm", "ṣpˤn": "ṣpn",
}

DEFAULT_DROP = frozenset({"", "b", "h", "p", "yn", "ilm"})


@dataclass(frozen=True)
class DivineNameCorpus:
    """Parsed and documented DN occurrences, ready for network analysis."""

    occurrences: pd.DataFrame
    lines: pd.DataFrame
    name_summary: pd.DataFrame
    normalization_changes: pd.DataFrame
    source_dir: Path
    descriptions_path: Path | None

    def overview(self) -> pd.Series:
        """Small corpus summary suitable for direct display in a notebook."""
        return pd.Series({
            "tablets": int(self.occurrences["tablet"].nunique()),
            "DN occurrences": int(len(self.occurrences)),
            "normalized names": int(self.occurrences["deity"].nunique()),
            "names with onomastic descriptions": int(
                (self.name_summary["description_source"] == "onomastic override").sum()
            ),
        })


def _expected_files(tablets: Iterable[str]) -> list[str]:
    return [f"KTU {tablet}.tsv" for tablet in tablets]


def _has_files(directory: Path, filenames: Iterable[str]) -> bool:
    return all((directory / filename).is_file() for filename in filenames)


def _find_source_dir(
    tablets: tuple[str, ...], data_dir: str | Path | None,
) -> Path:
    filenames = _expected_files(tablets)
    candidates: list[Path] = []
    if data_dir is not None:
        candidates.append(Path(data_dir).expanduser())
    candidates.append(_BUNDLED_SOURCE)
    for candidate in candidates:
        if _has_files(candidate, filenames):
            return candidate
    raise FileNotFoundError(
        "The bundled Baal Cycle annotation is incomplete under "
        f"{_BUNDLED_SOURCE}. Re-clone the workshop repository."
    )


def _find_overrides(
    source_dir: Path, overrides_path: str | Path | None,
) -> Path | None:
    candidates: list[Path] = []
    if overrides_path is not None:
        candidates.append(Path(overrides_path).expanduser())
    candidates.extend([
        source_dir / "onomastic_gloss_overrides.tsv",
        _BUNDLED_OVERRIDES,
    ])
    return next((path for path in candidates if path.is_file()), None)


def _canonical_dulat_key(value: object) -> str:
    value = str(value).strip().translate(str.maketrans({
        "ả": "a", "ỉ": "i", "ủ": "u", "ʕ": "ˤ",
    }))
    return re.sub(r"\s*\([IVX]+\)\s*$", "", value).strip()


def _description_map(
    overrides_path: Path | None, aliases: Mapping[str, str],
) -> dict[str, str]:
    if overrides_path is None:
        return {}
    overrides = pd.read_csv(overrides_path, sep="\t", dtype=str)
    overrides = overrides.dropna(subset=["gloss"]).copy()
    overrides["key"] = overrides["dulat"].map(_canonical_dulat_key)
    overrides["deity"] = overrides["key"].map(
        lambda name: aliases.get(name, name)
    )
    # Prefer the base-name description over an allonym's description when both
    # collapse to one graph node (e.g. bʕl over hd(d), ym over nhr).
    overrides["is_base_name"] = overrides["key"] == overrides["deity"]
    preferred = (
        overrides.sort_values("is_base_name")
        .drop_duplicates("deity", keep="last")
    )
    return dict(zip(preferred["deity"], preferred["gloss"]))


def load_baal_cycle(
    data_dir: str | Path | None = None,
    overrides_path: str | Path | None = None,
    *,
    tablets: Iterable[str] = ("1.1", "1.2", "1.3", "1.4", "1.5", "1.6"),
    aliases: Mapping[str, str] | None = None,
    drop: Iterable[str] = DEFAULT_DROP,
) -> DivineNameCorpus:
    """Load and normalize DN-tagged names in KTU 1.1–1.6.

    ``aliases`` and ``drop`` expose the two philological decisions worth
    challenging in class.  File-format details remain internal.
    """
    tablet_ids = tuple(tablets)
    source_dir = _find_source_dir(tablet_ids, data_dir)
    descriptions_path = _find_overrides(source_dir, overrides_path)
    alias_map = dict(DEFAULT_ALIASES if aliases is None else aliases)
    dropped = set(drop)

    dn_records: list[dict] = []
    token_records: list[dict] = []
    unparsed_headers: list[tuple[str, str]] = []

    for filename in _expected_files(tablet_ids):
        path = source_dir / filename
        ref: dict | None = None
        for raw in path.read_text(encoding="utf-8-sig").splitlines():
            if raw.startswith("#"):
                header = raw[1:].strip()
                match = _REF_RE.fullmatch(header)
                if not match:
                    unparsed_headers.append((path.name, header))
                    ref = None
                else:
                    ref = match.groupdict()
                    ref["line"] = int(ref["line"])
                continue

            fields = raw.split("\t")
            if (
                not ref or not raw.strip() or fields[0] == "id"
                or len(fields) < 7
            ):
                continue
            record = {
                **ref,
                "token_id": fields[0].strip(),
                "surface": fields[1].strip(),
                "pos": fields[5].strip(),
                "gloss": fields[6].strip(),
                "source_file": path.name,
            }
            token_records.append(record)
            if _DN_RE.search(record["pos"]):
                dn_records.append(record.copy())

    if unparsed_headers:
        raise ValueError(f"Unparsed line headers: {unparsed_headers[:5]}")
    if not dn_records:
        raise ValueError(f"No DN-tagged records found under {source_dir}")

    occurrences = pd.DataFrame(dn_records)
    tokens = pd.DataFrame(token_records)
    lines = (
        tokens.groupby(["tablet", "column", "line"], sort=False)["surface"]
        .apply(lambda words: " ".join(word for word in words if word))
        .rename("text")
        .reset_index()
    )

    occurrences["deity"] = occurrences["surface"].map(
        lambda name: alias_map.get(name, name)
    )
    occurrences = occurrences.loc[
        ~occurrences["deity"].isin(dropped)
    ].copy()

    fallback_descriptions = (
        occurrences.groupby("deity")["gloss"]
        .agg(lambda values: values.value_counts().index[0])
    )
    descriptions = _description_map(descriptions_path, alias_map)
    occurrences["description"] = occurrences["deity"].map(descriptions)
    occurrences["description_source"] = (
        occurrences["description"].notna().map({
            True: "onomastic override", False: "annotation gloss",
        })
    )
    occurrences["description"] = occurrences["description"].fillna(
        occurrences["deity"].map(fallback_descriptions)
    )

    counts = occurrences["deity"].value_counts().rename("mentions")
    name_summary = (
        occurrences[["deity", "description", "description_source"]]
        .drop_duplicates("deity")
        .set_index("deity")
        .join(counts)
        [["mentions", "description", "description_source"]]
        .sort_values("mentions", ascending=False)
    )
    normalization_changes = (
        occurrences.loc[
            occurrences["surface"] != occurrences["deity"],
            ["surface", "deity", "gloss"],
        ]
        .drop_duplicates()
        .sort_values(["deity", "surface"])
        .reset_index(drop=True)
    )
    return DivineNameCorpus(
        occurrences=occurrences.reset_index(drop=True),
        lines=lines,
        name_summary=name_summary,
        normalization_changes=normalization_changes,
        source_dir=source_dir,
        descriptions_path=descriptions_path,
    )


def build_divine_name_graph(
    corpus: DivineNameCorpus, max_distance: int = 3,
) -> nx.Graph:
    """Connect different divine names attested within ``max_distance`` lines."""
    if max_distance < 0:
        raise ValueError("max_distance must be non-negative")
    table = corpus.occurrences
    evidence: defaultdict[tuple[str, str], set[tuple]] = defaultdict(set)
    for (tablet, column), group in table.groupby(
        ["tablet", "column"], sort=False
    ):
        rows = group.to_dict("records")
        for left, right in combinations(rows, 2):
            if left["deity"] == right["deity"]:
                continue
            if abs(left["line"] - right["line"]) <= max_distance:
                pair = tuple(sorted((left["deity"], right["deity"])))
                evidence[pair].add((
                    tablet,
                    column,
                    min(left["line"], right["line"]),
                    max(left["line"], right["line"]),
                ))

    graph = nx.Graph(distance=max_distance)
    for deity, row in corpus.name_summary.iterrows():
        graph.add_node(
            deity,
            mentions=int(row["mentions"]),
            description=row["description"],
            description_source=row["description_source"],
        )
    for (left, right), windows in evidence.items():
        graph.add_edge(
            left, right, weight=len(windows), evidence=sorted(windows)
        )
    return graph


def graph_overview(graph: nx.Graph) -> pd.Series:
    """Return the basic graph quantities used in the discussion."""
    return pd.Series({
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": round(nx.density(graph), 3),
        "line distance": graph.graph.get("distance"),
    })


def filter_divine_name_graph(
    graph: nx.Graph,
    *,
    min_weight: int = 1,
    min_tablets: int = 1,
) -> nx.Graph:
    """Keep only edges with enough passages and independent tablet witnesses."""
    filtered = nx.Graph(**graph.graph)
    filtered.add_nodes_from(graph.nodes(data=True))
    for left, right, data in graph.edges(data=True):
        tablets = {window[0] for window in data["evidence"]}
        if data["weight"] >= min_weight and len(tablets) >= min_tablets:
            filtered.add_edge(left, right, **data)
    return filtered


def format_window(window: tuple) -> str:
    """Format stored edge provenance as a KTU reference."""
    tablet, column, first, last = window
    if first == last:
        return f"KTU {tablet} {column}:{first}"
    return f"KTU {tablet} {column}:{first}–{last}"


def edge_evidence(
    graph: nx.Graph, left: str, right: str,
) -> pd.DataFrame:
    """All line-pair windows supporting one graph edge."""
    data = graph.get_edge_data(left, right)
    if data is None:
        return pd.DataFrame(columns=["reference", "tablet", "column", "first", "last"])
    return pd.DataFrame([
        {
            "reference": format_window(window),
            "tablet": window[0], "column": window[1],
            "first": window[2], "last": window[3],
        }
        for window in data["evidence"]
    ])


def passage(
    corpus: DivineNameCorpus, reference: tuple, padding: int = 0,
) -> pd.DataFrame:
    """Reconstruct the transliterated lines around one evidential window."""
    tablet, column, first, last = reference
    rows = corpus.lines.loc[
        (corpus.lines["tablet"] == tablet)
        & (corpus.lines["column"] == column)
        & corpus.lines["line"].between(first - padding, last + padding)
    ].copy()
    rows.insert(
        0,
        "reference",
        rows.apply(
            lambda row: f"KTU {row['tablet']} {row['column']}:{row['line']}",
            axis=1,
        ),
    )
    return rows[["reference", "text"]].reset_index(drop=True)


def edge_passages(
    corpus: DivineNameCorpus,
    graph: nx.Graph,
    left: str,
    right: str,
    *,
    limit: int = 3,
    padding: int = 1,
) -> pd.DataFrame:
    """Reconstruct a few passages supporting one edge."""
    data = graph.get_edge_data(left, right)
    if data is None:
        return pd.DataFrame(columns=["edge_window", "reference", "text"])
    frames = []
    for window in data["evidence"][:limit]:
        frame = passage(corpus, window, padding=padding)
        frame.insert(0, "edge_window", format_window(window))
        frames.append(frame)
    if not frames:
        return pd.DataFrame(columns=["edge_window", "reference", "text"])
    return pd.concat(frames, ignore_index=True)


def _analytical_subgraph(graph: nx.Graph, min_mentions: int) -> nx.Graph:
    nodes = [
        node for node, data in graph.nodes(data=True)
        if data.get("mentions", 0) >= min_mentions
    ]
    return graph.subgraph(nodes).copy()


def find_maximal_cliques(
    graph: nx.Graph, *, min_mentions: int = 2, min_size: int = 3,
) -> pd.DataFrame:
    """Find and rank maximal cliques in the aggregated proximity graph."""
    analytical = _analytical_subgraph(graph, min_mentions)

    def total_weight(members: list[str]) -> int:
        return sum(
            analytical[left][right]["weight"]
            for left, right in combinations(members, 2)
        )

    cliques = [
        sorted(members) for members in nx.find_cliques(analytical)
        if len(members) >= min_size
    ]
    cliques.sort(
        key=lambda members: (-len(members), -total_weight(members), members)
    )
    return pd.DataFrame([
        {
            "size": len(members),
            "pair_weight_sum": total_weight(members),
            "names": ", ".join(members),
            "members": tuple(members),
        }
        for members in cliques
    ])


def clique_evidence(
    graph: nx.Graph, members: Iterable[str], examples: int = 4,
) -> pd.DataFrame:
    """Expand a clique into its pairwise claims and sample KTU references."""
    rows = []
    for left, right in combinations(sorted(members), 2):
        edge = graph[left][right]
        refs = [format_window(window) for window in edge["evidence"]]
        rows.append({
            "pair": f"{left} — {right}",
            "weight": edge["weight"],
            "example_windows": "; ".join(refs[:examples]),
        })
    return pd.DataFrame(rows).sort_values(["weight", "pair"]).reset_index(drop=True)


def local_name_windows(
    corpus: DivineNameCorpus,
    *,
    max_distance: int = 3,
    min_mentions: int = 2,
    min_size: int = 3,
) -> pd.DataFrame:
    """Name groups genuinely contained in one local line window."""
    counts = corpus.occurrences["deity"].value_counts()
    keep = set(counts[counts >= min_mentions].index)
    table = corpus.occurrences.loc[
        corpus.occurrences["deity"].isin(keep)
    ]
    windows = []
    for (tablet, column), group in table.groupby(
        ["tablet", "column"], sort=False
    ):
        for start in sorted(group["line"].unique()):
            members = frozenset(
                group.loc[
                    group["line"].between(start, start + max_distance),
                    "deity",
                ]
            )
            if len(members) >= min_size:
                windows.append({
                    "size": len(members),
                    "reference": f"KTU {tablet} {column}:{start}–{start + max_distance}",
                    "names": ", ".join(sorted(members)),
                    "members": tuple(sorted(members)),
                })
    if not windows:
        return pd.DataFrame(columns=["size", "reference", "names", "members"])
    return (
        pd.DataFrame(windows)
        .drop_duplicates()
        .sort_values(["size", "reference"], ascending=[False, True])
        .reset_index(drop=True)
    )


def graph_sensitivity(
    corpus: DivineNameCorpus,
    distances: Iterable[int] = range(0, 6),
    *,
    min_mentions: int = 2,
) -> pd.DataFrame:
    """Rebuild the graph at several line distances."""
    rows = []
    for distance in distances:
        graph = build_divine_name_graph(corpus, max_distance=distance)
        analytical = _analytical_subgraph(graph, min_mentions)
        cliques = list(nx.find_cliques(analytical))
        rows.append({
            "distance": distance,
            "nodes": analytical.number_of_nodes(),
            "edges": analytical.number_of_edges(),
            "density": nx.density(analytical),
            "largest_clique": max(map(len, cliques), default=0),
        })
    return pd.DataFrame(rows)


def plot_graph_sensitivity(table: pd.DataFrame):
    """Plot density and maximum clique size against the distance rule."""
    import plotly.graph_objects as go

    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=table["distance"], y=table["density"],
        mode="lines+markers", name="density", yaxis="y1",
    ))
    figure.add_trace(go.Bar(
        x=table["distance"], y=table["largest_clique"],
        name="largest clique", opacity=0.35, yaxis="y2",
    ))
    figure.update_layout(
        title="Sensitivity to the line-distance threshold",
        xaxis_title="maximum line distance",
        yaxis={"title": "graph density", "rangemode": "tozero"},
        yaxis2={
            "title": "largest clique", "overlaying": "y",
            "side": "right", "rangemode": "tozero",
        },
        template="plotly_white", height=430,
    )
    return figure


def _network_document(
    graph: nx.Graph, *, min_mentions: int, min_weight: int,
) -> tuple[str, nx.Graph]:
    analytical = _analytical_subgraph(graph, min_mentions)
    displayed = nx.Graph(
        (left, right, data)
        for left, right, data in analytical.edges(data=True)
        if data["weight"] >= min_weight
    )
    for node in displayed:
        displayed.nodes[node].update(graph.nodes[node])

    nodes = [
        {
            "id": node,
            "label": node,
            "value": int(graph.nodes[node]["mentions"]),
            "color": {
                "background": "#60a5fa", "border": "#1e3a5f",
                "highlight": {"background": "#f59e0b", "border": "#78350f"},
            },
            "title": (
                f"{node} — {graph.nodes[node]['description']} — "
                f"{graph.nodes[node]['mentions']} mentions · "
                f"degree {analytical.degree(node)}"
            ),
        }
        for node in displayed.nodes()
    ]
    edges = [
        {
            "from": left,
            "to": right,
            "value": int(data["weight"]),
            "title": (
                f"{left} — {right}: {data['weight']} evidential windows — "
                + "; ".join(format_window(window) for window in data["evidence"][:6])
            ),
        }
        for left, right, data in displayed.edges(data=True)
    ]
    vis_network = vis_network_javascript()
    document = """<!doctype html><html><head>
<script>__VIS_NETWORK__</script>
<style>
html,body{margin:0;height:100%;font-family:system-ui,sans-serif;background:#fff!important;color:#111827!important;color-scheme:light}
#toolbar{height:38px;padding:6px 8px;box-sizing:border-box;background:#f8fafc!important;border-bottom:1px solid #cbd5e1;color:#111827}
#net,#net canvas{height:682px;background:#fff!important}
button{margin-right:6px;padding:4px 9px;background:#fff;color:#111827;border:1px solid #94a3b8;border-radius:4px}
.vis-tooltip{max-width:560px;white-space:normal!important;background:#fff!important;color:#111827!important;border:1px solid #64748b!important;border-radius:4px!important;box-shadow:0 2px 8px rgba(0,0,0,.18)!important;padding:8px!important}
</style></head><body>
<div id="toolbar"><button onclick="freeze()">Freeze layout</button><button onclick="resume()">Resume physics</button><button onclick="network.fit({animation:true})">Fit</button></div>
<div id="net"></div><script>
const data = {nodes:new vis.DataSet(__NODES__),edges:new vis.DataSet(__EDGES__)};
const options={
 nodes:{shape:'dot',scaling:{min:12,max:48},borderWidth:1.5,font:{size:16,face:'system-ui',color:'#111827',strokeWidth:4,strokeColor:'#fff'}},
 edges:{color:{color:'#94a3b8',highlight:'#334155'},scaling:{min:1,max:9},smooth:{type:'continuous'}},
 physics:{barnesHut:{gravitationalConstant:-7000,springLength:145,springConstant:0.035,avoidOverlap:0.35},stabilization:{iterations:300}},
 interaction:{hover:true,dragNodes:true,dragView:true,zoomView:true,tooltipDelay:80}
};
const network=new vis.Network(document.getElementById('net'),data,options);
function freeze(){network.setOptions({physics:{enabled:false}})}
function resume(){network.setOptions({physics:{enabled:true}})}
network.once('stabilizationIterationsDone',freeze);
</script></body></html>"""
    document = document.replace("__VIS_NETWORK__", vis_network)
    document = document.replace("__NODES__", json.dumps(nodes, ensure_ascii=False))
    document = document.replace("__EDGES__", json.dumps(edges, ensure_ascii=False))
    return document, displayed


def show_divine_name_network(
    graph: nx.Graph,
    *,
    min_mentions: int = 2,
    min_weight: int = 3,
    height: int = 730,
):
    """Return a draggable, high-contrast network for notebook display."""
    from IPython.display import HTML

    document, _ = _network_document(
        graph, min_mentions=min_mentions, min_weight=min_weight
    )
    iframe = (
        f'<iframe srcdoc="{html.escape(document, quote=True)}" width="100%" '
        f'height="{height}" style="border:1px solid #cbd5e1;'
        'background:#fff;color-scheme:light"></iframe>'
    )
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="Consider using IPython.display.IFrame instead"
        )
        return HTML(iframe)
