"""High-level helpers for finding forms characteristic of corpus genres.

The public functions deliberately expose a word-by-document matrix because that
orientation is convenient for teaching: every column is one document and every
row is one written form.  Scikit-learn expects the transpose internally.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import chi2

from workshop_tools.loader import without_broken_tokens


def build_word_document_matrix(
    corpus: pd.DataFrame,
    *,
    document_column: str = "tablet",
    genre_column: str = "genre",
    tokens_column: str = "tokens",
    min_documents: int = 2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return document metadata and a sparse word-by-document presence matrix.

    Tokens containing ``x`` or ``X`` are excluded.  No stop list or lexical
    filter is applied: numbers and editorial notation remain available to the
    statistical test.  Forms occurring in fewer than ``min_documents`` are
    omitted because a single attestation cannot establish a genre pattern.
    """
    required = {document_column, genre_column, tokens_column}
    missing = required.difference(corpus.columns)
    if missing:
        raise KeyError(f"Missing corpus columns: {', '.join(sorted(missing))}")
    if min_documents < 1:
        raise ValueError("min_documents must be at least 1")

    docs = corpus.loc[
        corpus[genre_column].notna(),
        [document_column, genre_column, tokens_column],
    ].copy()
    docs["analysis_tokens"] = docs[tokens_column].map(without_broken_tokens)
    docs = docs[docs["analysis_tokens"].map(bool)].copy()
    docs[document_column] = docs[document_column].astype(str)
    if docs[document_column].duplicated().any():
        raise ValueError(f"{document_column!r} must uniquely identify documents")

    vectorizer = CountVectorizer(
        analyzer=lambda tokens: tokens,
        binary=True,
        lowercase=False,
        min_df=min_documents,
        dtype=np.int8,
    )
    document_word = vectorizer.fit_transform(docs["analysis_tokens"])
    forms = vectorizer.get_feature_names_out()

    word_document = pd.DataFrame.sparse.from_spmatrix(
        document_word.T,
        index=pd.Index(forms, name="form"),
        columns=pd.Index(docs[document_column], name="document"),
    )
    document_info = docs.set_index(document_column)[[genre_column]].rename(
        columns={genre_column: "genre"}
    )
    return document_info, word_document


def select_genre_features(
    word_document: pd.DataFrame,
    genres: pd.Series,
    *,
    top_n: int = 10,
    min_genre_documents: int = 2,
) -> pd.DataFrame:
    """Select forms associated with each genre using a one-vs-rest chi-square.

    The matrix is binary, so the test compares *document prevalence*, not the
    number of repetitions inside a long document.  Only positive associations
    are returned, and a form must occur in at least ``min_genre_documents`` of
    the genre's documents.
    """
    if top_n < 1:
        raise ValueError("top_n must be at least 1")
    if min_genre_documents < 1:
        raise ValueError("min_genre_documents must be at least 1")

    aligned_genres = genres.reindex(word_document.columns)
    if aligned_genres.isna().any():
        raise ValueError("Every document column must have a genre label")

    document_word = word_document.sparse.to_coo().T.tocsr()
    forms = word_document.index.to_numpy()
    rows: list[dict] = []

    for genre in sorted(aligned_genres.unique()):
        in_genre = aligned_genres.eq(genre).to_numpy()
        outside = ~in_genre
        scores, _ = chi2(document_word, in_genre)
        in_counts = np.asarray(document_word[in_genre].sum(axis=0)).ravel()
        out_counts = np.asarray(document_word[outside].sum(axis=0)).ravel()
        in_prevalence = in_counts / in_genre.sum()
        out_prevalence = out_counts / outside.sum()

        candidates = np.flatnonzero(
            (in_counts >= min_genre_documents)
            & (in_prevalence > out_prevalence)
            & np.isfinite(scores)
        )
        order = candidates[np.argsort(scores[candidates], kind="stable")[::-1]]

        for rank, feature_index in enumerate(order[:top_n], start=1):
            rows.append(
                {
                    "genre": genre,
                    "rank": rank,
                    "form": forms[feature_index],
                    "chi2": float(scores[feature_index]),
                    "genre_documents_with_form": int(in_counts[feature_index]),
                    "genre_documents": int(in_genre.sum()),
                    "prevalence_in_genre": float(in_prevalence[feature_index]),
                    "prevalence_elsewhere": float(out_prevalence[feature_index]),
                }
            )

    return pd.DataFrame(rows)


def plot_genre_feature_scores(features: pd.DataFrame) -> go.Figure:
    """Plot the selected chi-square scores as readable genre small multiples."""
    genres = list(features["genre"].drop_duplicates())
    columns = 2
    rows = math.ceil(len(genres) / columns)
    fig = make_subplots(
        rows=rows,
        cols=columns,
        subplot_titles=genres,
        horizontal_spacing=0.16,
        vertical_spacing=0.12,
    )

    for position, genre in enumerate(genres):
        row = position // columns + 1
        column = position % columns + 1
        subset = features[features["genre"] == genre].sort_values("chi2")
        custom = np.column_stack(
            [
                subset["genre_documents_with_form"],
                subset["genre_documents"],
                100 * subset["prevalence_in_genre"],
                100 * subset["prevalence_elsewhere"],
            ]
        )
        fig.add_trace(
            go.Bar(
                x=subset["chi2"],
                y=subset["form"],
                orientation="h",
                customdata=custom,
                marker_color="#3767a6",
                hovertemplate=(
                    "<b>%{y}</b><br>χ²=%{x:.1f}"
                    "<br>Genre: %{customdata[0]:.0f}/%{customdata[1]:.0f} documents"
                    " (%{customdata[2]:.1f}%)"
                    "<br>Elsewhere: %{customdata[3]:.1f}%<extra></extra>"
                ),
                showlegend=False,
            ),
            row=row,
            col=column,
        )
        fig.update_xaxes(title_text="χ² association", row=row, col=column)

    fig.update_layout(
        template="plotly_white",
        height=max(640, rows * 360),
        title="Forms most strongly associated with each UDB genre",
        margin=dict(l=80, r=30, t=80, b=50),
    )
    return fig


def plot_feature_document_matrix(
    word_document: pd.DataFrame,
    document_info: pd.DataFrame,
    features: pd.DataFrame,
    *,
    forms_per_genre: int = 5,
) -> go.Figure:
    """Show selected forms by individual document; every column is a document."""
    selected = (
        features.sort_values(["genre", "rank"])
        .groupby("genre", sort=False)
        .head(forms_per_genre)
    )
    forms = list(dict.fromkeys(selected["form"]))
    ordered_documents = (
        document_info.reset_index()
        .sort_values(["genre", document_info.index.name])
        .set_index(document_info.index.name)
    )
    document_ids = ordered_documents.index.astype(str).tolist()
    document_genres = ordered_documents["genre"].astype(str).tolist()
    matrix = word_document.loc[forms, document_ids].sparse.to_dense().to_numpy()
    document_labels = [
        f"{document} · {genre}"
        for document, genre in zip(document_ids, document_genres)
    ]

    fig = go.Figure(
        go.Heatmap(
            z=matrix,
            x=document_labels,
            y=forms,
            zmin=0,
            zmax=1,
            colorscale=[[0, "#f1f3f5"], [1, "#3767a6"]],
            showscale=False,
            hovertemplate=(
                "Form: <b>%{y}</b><br>Document · genre: %{x}"
                "<br>Present: %{z}<extra></extra>"
            ),
        )
    )

    start = 0
    for genre, group in ordered_documents.groupby("genre", sort=False):
        end = start + len(group)
        if start:
            fig.add_vline(x=start - 0.5, line_width=1, line_color="#808080")
        fig.add_annotation(
            x=(start + end - 1) / 2,
            y=1.04,
            xref="x",
            yref="paper",
            text=str(genre),
            showarrow=False,
        )
        start = end

    fig.update_layout(
        template="plotly_white",
        title="Selected forms across individual documents",
        xaxis_title="documents (one column each; hover for UDB number)",
        yaxis_title="written forms",
        xaxis=dict(showticklabels=False),
        height=max(650, 22 * len(forms) + 220),
        margin=dict(l=90, r=30, t=100, b=60),
    )
    return fig
