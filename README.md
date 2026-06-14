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

## Workshop structure

| Hour | Theme | Readings | Notebooks |
|------|-------|----------|-----------|
| **1** | Ugarit: corpora and data | `docs/01`–`03` | `notebooks/1a_corpora_and_data`, `notebooks/1b_alphabet_hypothesis` |
| **2** | From words to genres | `docs/04` | `notebooks/2a_tfidf_keywords`, `notebooks/2b_similarity_clustering` |
| **3** | From texts to structures | `docs/05`–`08` | `notebooks/3a_ngrams_formulas`, `notebooks/3b_letter_networks`, `notebooks/3c_divination_trees` |

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
│   ├── sample/            ← deprecated placeholder sample data
│   └── README.md          ← data sources and citation map
├── docs/                  ← readings (Markdown); see docs/00-resources.md for the resource catalogue
├── notebooks/             ← Jupyter notebooks, one per exercise
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
- **UDB — Ugaritic Data Bank**: Spanish-team corpus of CAT texts, mostly with the same numbers; now sold as an Accordance package, with UDB/concordance PDFs listed on Juan-Pablo Vita's Academia page.
- **USC Digital Library / InscriptiFact**: high-resolution tablet photographs from Bruce Zuckerman and the West Semitic Research Project; formerly at `inscriptifact.com`, now surfaced through USC Digital Library.
- **KTU**: *Die keilalphabetischen Texte aus Ugarit* — the standard text-numbering scheme used throughout.
- **DUL / DULAT**: *A Dictionary of the Ugaritic Language in the Alphabetic Tradition*.

Full citation map and links: `data/README.md`.

---

## License

See `LICENSE`. Workshop text and code are intended for educational use; primary
corpus data remains under the licenses of its original providers (see `data/README.md`).
