# Ugarit & Digital Humanities — A 3-Hour Workshop

Workshop materials for studying ancient texts with data science and digital
humanities methods, using the Late Bronze Age corpus of **Ugarit** as a case
study.

The repository combines short historical/philological readings, illustrations, and runnable Jupyter notebooks. Notebooks are
written for **participants with little or no coding experience**.

---

## Run it now (no install)

Click a **Colab** badge to open a notebook in your browser — the first cell clones
this repo and downloads the corpus automatically. Nothing to install.

| Hour | Notebook | Open |
|------|----------|------|
| 1 | Tablets as objects (metadata) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/master/notebooks/1a_corpora_and_data.ipynb) |
| 1 | Reading the tablets (script & alphabet) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/master/notebooks/1b_alphabet_hypothesis.ipynb) |
| 2 | **From keywords to the genre map** ⭐ | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/master/notebooks/2_similarity_clustering.ipynb) |
| 3 | Formulas (n-grams) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/master/notebooks/3a_ngrams_formulas.ipynb) |
| 3 | Letter networks | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/master/notebooks/3b_letter_networks.ipynb) |
| 3 | Divination trees | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/master/notebooks/3c_divination_trees.ipynb) |
| 3 | PDF → local SQLite | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/master/notebooks/3d_udb_pdf_to_sqlite.ipynb) |

Prefer the full repo in-browser? [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/alexsosn/ugarit-dh-workshop/master)
launches everything on Binder. Each notebook also carries its own Colab + Binder
badges at the top.

---

## Workshop structure

| Hour | Theme | Readings | Notebooks |
|------|-------|----------|-----------|
| **1** | Ugarit: corpora and data | `docs/00`–`01` | `notebooks/1a_corpora_and_data`, `notebooks/1b_alphabet_hypothesis` |
| **2** | From words to genres |  | `notebooks/2_similarity_clustering` |
| **3** | From texts to structures | `docs/08` | `notebooks/3a_ngrams_formulas`, `notebooks/3b_letter_networks`, `notebooks/3c_divination_trees`, optional `notebooks/3d_udb_pdf_to_sqlite` |

Facilitators: start with [`docs/teaching-throughline.md`](docs/teaching-throughline.md).
It aligns every exercise as **source → representation → computation → validation
→ interpretation** and supplies a consistent discussion pattern.

Experienced programmers can use the optional advanced track in
[`docs/star-tasks-spec.md`](docs/star-tasks-spec.md). These extensions are
segregated from the non-coder path and should be introduced only when useful.

### Hour 1 — Ugarit: from objects to texts (60 min)
- *10 min* — Ugarit: historical context of the Late Bronze Age (presenter + `docs/01`).
- *20 min* — **`1a`, tablets as objects:** where the data comes from, building UDB
  metadata from a PDF, genre/language/archive, tablet sizes, find-spot maps, and
  replaying the excavation season by season.
- *30 min* — **`1b`, reading the tablets:** the cuneiform alphabet and
  transliteration, counting signs from the corpus, and testing Jared Diamond's
  "optimal design" claim end to end.
- History is interleaved as short asides beside the relevant cells, not front-loaded.

### Hour 2 — From words to genres (60 min)
- *10 min* — Where genre labels come from; sampling and imbalance.
- *15 min* — TF-IDF keywords and their philological limits.
- *15 min* — Similarity and the interactive UMAP projection.
- *10 min* — Validate the picture: clustering scores and held-out classification.
- *10 min* — Close-read contested/outlying tablets; separate model error from label problems.

### Hour 3 — From texts to structures (60 min)
- *12 min* — Formulaic language: n-grams, dispersion, and concordance.
- *10 min* — Letter networks: extraction, entity ambiguity, and centrality.
- *13 min* — Omen structures: protasis/apodosis, trees, and comparative caution.
- *20 min* — The modern toolkit and the AI build demo, with provenance and validation.
- *5 min* — Synthesis and next steps.

---

## Repository layout

```
.
├── README.md              ← you are here
├── requirements.txt       ← Python dependencies
├── data/
│   ├── loader.py          ← CUC loader backed by HuggingFace Parquet cache
│   └── README.md          ← data sources and citation map
├── docs/                  ← readings (Markdown); 00-resources.md = resource catalogue, glossary.md = jargon unpacked
├── notebooks/             ← Jupyter notebooks, one per exercise
├── workshop_tools/        ← code-only UDB parser + local SQLite/Parquet builders
├── local_data/            ← participant-supplied files; ignored, never committed
├── images/                ← illustrations (maps, tablet photos, diagrams)
└── slides/                ← optional presentation material
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab                       # or: jupyter notebook
```

### Optional — full Text-Fabric features
The HuggingFace CUC Parquet export has transliteration + cuneiform + line references. For
sign-level features (emendation, certainty, alternative readings) or to query the
corpus as a graph, install (Con)Text-Fabric and use the original upstream dataset:

```bash
pip install text-fabric        # then, in a notebook:  use("DT-UCPH/cuc")
```

---

## License

See `LICENSE`. Workshop text and code are intended for educational use; primary
corpus data remains under the licenses of its original providers (see `data/README.md`).
