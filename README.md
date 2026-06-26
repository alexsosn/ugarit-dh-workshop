# Ugarit & Digital Humanities — A 3-Hour Workshop

Workshop materials for studying ancient texts with data science and digital
humanities methods, using the Late Bronze Age corpus of **Ugarit** as a case
study. The path we follow: **clay tablet → corpus → statistics → text similarity
→ data structures → research hypotheses.**

All materials are in English. The repository combines short historical/philological
readings (Markdown), illustrations, and runnable Jupyter notebooks. Notebooks are
written for **participants with little or no coding experience**: you mostly run
cells in order and read the comments.

---

## Run it now (no install) ☁️

Click a **Colab** badge to open a notebook in your browser — the first cell clones
this repo and downloads the corpus automatically. Nothing to install.

| Hour | Notebook | Open |
|------|----------|------|
| 1 | Corpora and data | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/main/notebooks/1a_corpora_and_data.ipynb) |
| 1 | Alphabet hypothesis | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/main/notebooks/1b_alphabet_hypothesis.ipynb) |
| 2 | Keywords & TF-IDF | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/main/notebooks/2a_tfidf_keywords.ipynb) |
| 2 | **The genre map** ⭐ | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/main/notebooks/2b_similarity_clustering.ipynb) |
| 3 | Formulas (n-grams) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/main/notebooks/3a_ngrams_formulas.ipynb) |
| 3 | Letter networks | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/main/notebooks/3b_letter_networks.ipynb) |
| 3 | Divination trees | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/main/notebooks/3c_divination_trees.ipynb) |
| 3 | PDF → local SQLite | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexsosn/ugarit-dh-workshop/blob/main/notebooks/3d_udb_pdf_to_sqlite.ipynb) |

Prefer the full repo in-browser? [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/alexsosn/ugarit-dh-workshop/main)
launches everything on Binder. Each notebook also carries its own Colab + Binder
badges at the top.

> **Presenters:** the badges point at `github.com/alexsosn/ugarit-dh-workshop`,
> `main` branch. They go live once the repo is pushed there.

---

## Workshop structure

| Hour | Theme | Readings | Notebooks |
|------|-------|----------|-----------|
| **1** | Ugarit: corpora and data | `docs/01`–`03` | `notebooks/1a_corpora_and_data`, `notebooks/1b_alphabet_hypothesis` |
| **2** | From words to genres | `docs/04` | `notebooks/2a_tfidf_keywords`, `notebooks/2b_similarity_clustering` |
| **3** | From texts to structures | `docs/05`–`08` | `notebooks/3a_ngrams_formulas`, `notebooks/3b_letter_networks`, `notebooks/3c_divination_trees`, optional `notebooks/3d_udb_pdf_to_sqlite` |

### Hour 1 — Ugarit: corpora and data (60 min)
- *20 min* — Ugarit: historical context of the Late Bronze Age, excavations, tablets, publications.
- *15 min* — Corpora and data: ContextFabric / CUC, UDB, and others.
- *10 min* — The Ugaritic alphabet and language in its Semitic context.
- *15 min* — Testing a philological hypothesis: Jared Diamond and the "optimal design" of the alphabet.

### Hour 2 — From words to genres (60 min)
- *10 min* — Genres of Ugaritic texts (KTU, UDB, etc.).
- *15 min* — Keywords and TF-IDF.
- *10 min* — Text similarity, clustering, and visualization.
- *5 min* — Formulaic language in Ugaritic and biblical poetry.
- *15 min* — Finding formulas: bigrams and trigrams.

### Hour 3 — From texts to structures (60 min)
- *10 min* — Social networks in Ugaritic texts.
- *10 min* — Network analysis of letters and name lists.
- *10 min* — Divination as ancient algorithms.
- *10 min* — Visualizing decision trees.
- *20 min* — The modern philologist's toolkit and the future of DH: CUC morphological tagging, other corpora, LLMs and agents.

---

## Repository layout

```
.
├── README.md              ← you are here
├── requirements.txt       ← Python dependencies
├── data/
│   ├── loader.py          ← CUC JSONL loader backed by HuggingFace cache
│   └── README.md          ← data sources and citation map
├── docs/                  ← readings (Markdown); 00-resources.md = resource catalogue, glossary.md = jargon unpacked
├── notebooks/             ← Jupyter notebooks, one per exercise
├── workshop_tools/        ← code-only UDB parser + local SQLite builder
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

The notebooks use the **real Copenhagen Ugaritic Corpus (CUC)** via JSONL files
hosted at HuggingFace (`AlexWalhai/cuc`). The first `load_texts()` call downloads
the corpus into a local cache; later calls reuse the cache. No API keys are
needed.

The optional PDF-to-SQLite exercise uses a participant-supplied UDB PDF. The
repository does not contain or download that PDF and does not contain a derived
UDB database. Both remain under ignored `local_data/` (or in the participant's
temporary Colab runtime).

### Optional — full Text-Fabric features
The HuggingFace JSONL has transliteration + cuneiform + line references. For
sign-level features (emendation, certainty, alternative readings) or to query the
corpus as a graph, install Text-Fabric and use the original upstream dataset:

```bash
pip install text-fabric        # then, in a notebook:  use("DT-UCPH/cuc")
```

---

## Data sources (overview)

- **CUC — Cuneiform Ugaritic Corpus**: Text-Fabric dataset of the Ugaritic corpus (`DT-UCPH/cuc`), CACCHT project.
- **AlexWalhai/cuc**: HuggingFace mirror of CUC line-level JSONL files used by the workshop loader.
- **ContextFabric**: graph-based corpus engine on the Text-Fabric data model, with an MCP server (`cfabric-mcp`) for LLM/agent tools.
- **UDB — Ugaritic Data Bank**: corpus by Jesús-Luis Cunchillos, Juan-Pablo
  Vita, José-Ángel Zamora, and Raquel Cervigón. The source notice requires
  citation and reserves reproduction, computerized processing, and
  distribution without written authorization. The workshop publishes parser
  code only; participants supply and process any source locally at their own
  responsibility.
- **USC Digital Library / InscriptiFact**: high-resolution tablet photographs from Bruce Zuckerman and the West Semitic Research Project; formerly at `inscriptifact.com`, now surfaced through USC Digital Library.
- **KTU**: *Die keilalphabetischen Texte aus Ugarit* — the standard text-numbering scheme used throughout.
- **DUL / DULAT**: *A Dictionary of the Ugaritic Language in the Alphabetic Tradition*.

Full citation map and links: `data/README.md`.

---

## License

See `LICENSE`. Workshop text and code are intended for educational use; primary
corpus data remains under the licenses of its original providers (see `data/README.md`).
