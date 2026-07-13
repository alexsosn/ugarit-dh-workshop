# Resources

A triaged index of the collected resources, sorted by type and mapped to the
hours / notebooks they feed.

> **New term?** *Parquet, DuckDB, MCP, UMAP, FastText, embedding* and other
> computational terms are unpacked in plain language in [glossary.md](glossary.md).

---

## 1. Live corpus data — the backbone ▶️

| Resource | What it is | Use |
|----------|-----------|-----|
| **`DT-UCPH/cuc`** (GitHub / Text-Fabric) ✅▶️ | Source CUC Text-Fabric dataset, 279 KTU tablets, CACCHT project, CC BY-NC 4.0. The notebooks use the `AlexWalhai/CUC` HuggingFace Parquet export. | Primary data source used by `workshop_tools/loader.py`. Full graph features in Text-Fabric: tablet, column, line, side, `g_cons`, trailer, language, sign, `emen`, `cert`, `cont`, `alt`. |
| **UDB — Ugaritic Data Bank** 🔑⚖️ | Spanish-team electronic corpus, mostly using CAT/KTU numbers; see Cunchillos, Vita, and Zamora 2003. Generate Parquet tables locally using `python -m workshop_tools.build_udb_parquet`. | Workshop provides parser code only. Participants must obtain the PDF through an authorized channel and generate tables locally. |
| **ContextFabric** + `cfabric-mcp` | Graph engine + MCP server. Tested locally with Python 3.13 in `~/projects/mcp-demo/`. | Hour 3 closing: LLM/agent access to CUC + BHSA. |

> ⚖️ **Licence note:** the CUC Text-Fabric data is **CC BY-NC 4.0**
> (`@licence` in the `.tf` headers, and the `cuc` repo README).
> **Attribution required; non-commercial use only.** The workshop repo notes this in
> `LICENSE` and `data/README.md`.
>
> **CACCHT:** CUC is developed by Christian Canu Højgaard, Martijn Naaijer,
> Martin Ehrensvärd, Robert Rezetko, Oliver Glanz, and Willem van Peursen as
> part of *Creating Annotated Corpora of Classical Hebrew Texts*.

### What CUC contains (and does not)

CUC is the **Copenhagen Ugaritic Corpus**, a work-in-progress Text-Fabric dataset
of KTU texts from the CACCHT project (*Creating Annotated Corpora of Classical
Hebrew Texts*). CACCHT is a collaboration of Christian Canu Højgaard, Martijn
Naaijer, Martin Ehrensvärd, Robert Rezetko, Oliver Glanz, and Willem van Peursen.
The underlying corpus license is **CC BY-NC 4.0**.

CUC currently contains **279 tablets** from KTU 1.x-3.x. Coverage includes:

```text
KTU 1.1-1.7, 1.14-1.25, 1.27-1.29, 1.31, 1.38-1.41, 1.43,
1.45-1.50, 1.54-1.58, 1.61-1.63, 1.65, 1.67, 1.69, 1.71-1.76,
1.78-1.98, 1.100-1.109, 1.111-1.119, 1.121-1.122, 1.124,
1.126-1.127, 1.129-1.130, 1.132-1.134, 1.136-1.144,
1.146-1.147, 1.149, 1.153-1.156, 1.158-1.177, 1.179-1.180;
KTU 2.1, 2.3-2.18, 2.20-2.27, 2.30-2.44, 2.46-2.75,
2.77-2.80, 2.82-2.105, 2.107-2.113;
KTU 3.1-3.35.
```

CUC annotates: **tablet, column, line, side, word (`g_cons` = consonantal form),
trailer** (word spacing/dividers), **language**, **sign**, **emen** (emendations,
including reconstructed, missing, excised, or redundant signs/letters), **cert**
(certainty, corresponding to KTU italics), **cont** (line continuation), and
**alt** (alternative reading). It does **not** (yet) carry lemma or part-of-speech
tags — so the TF-IDF / similarity notebooks work on **word forms**, not lemmas.
Flag this when discussing homographs.

> **Genre labels are heuristic** (KTU number + a curated list of well-known
> tablets in `loader.py:FINE_GENRE`), not a scholarly classification.


### CUC data analysis notes

Students can analyze CUC using the downloaded Parquet table in pandas, DuckDB, or
other data tools. Example queries for the exercises:

| Query | Workshop slot |
|-------|---------------|
| Frequency of verb **mḫṣ** forms | Hour 1 `1a` (forms/queries); Hour 3 morphology close |
| **Duplicate lines** | Hour 3 `3a` formulas / parallelism |
| **Hapax** forms | Hour 2 `2a` (lexical stats, rare words) |
| Frequent **trigrams** (divine epithets) | Hour 3 `3a` formula search |
| Frequent **bigrams** | Hour 3 `3a` formula search |
| N-grams **with references** | Hour 3 `3a` (cite the formula's attestations) |
| "Similar places" search | Hour 3 `3b` name/place graph |

These can be implemented as notebook cells using pandas `.query()`, groupby, or
DuckDB via the locally-loaded Parquet files.

---

## 2. Tablet images ⚖️

All require attribution; most require manual download. Confirm reuse terms before
putting any in slides.

| Source | Notes |
|--------|-------|
| **USC Digital Library / InscriptiFact** 🔑⚖️ | High-res tablet images produced by Bruce Zuckerman and the West Semitic Research Project. Formerly at `inscriptifact.com`; now in the USC Digital Library, e.g. [this Ugaritic collection/search entry](https://digitallibrary.usc.edu/asset-management/2A3BF1OL6PW?&WS=SearchResults&Flat=FP). Check account, permission, and reuse terms. |
| **OCHRE — Ugarit Tablet Inventory** (UChicago) ⚖️ | Inventory + images; good for provenance. |
| **Louvre — collections** (`?q=Ugarit`) ⚖️ | Many objects; check each item's licence (some open). |
| **Syria journal 1956 vol. 33** (Persée) ✅ | Open archival photos/plans — good, citable, low-friction. |
| **Del Olmo Lete — Photographic Archive of Canaanite Religion** (Academia) 🔑 | Religion/ritual imagery; login. |

**Pick for slides:** Persée (open) for site/plans; one Louvre object if licence is
clear; USC/InscriptiFact only where you have permission. Drop chosen files into
`../images/` and log credit per the `images/README.md`.

---

## 3. Tablet metadata & inventories

| Source | Use |
|--------|-----|
| **CDLI** (`language=Ugaritic`) ✅ | Canonical IDs, transliterations, provenance — the "many forms of one tablet" point in notebook [`1a`](../notebooks/1a_corpora_and_data.ipynb). |
| **Ras Shamra Tablet Inventory (RSTI / OCHRE)** ✅ | Excavation-level inventory; ties KTU ↔ RS numbers ↔ findspot. |

These two are the backbone for the **"one tablet → nine representations"** diagram.

---

## 4. Translations (for readings & glosses)

| Source | Use |
|--------|-----|
| **EUPT — Kirta** (Göttingen) ✅ | Scholarly edition + translation; Hour 2 genre/myth examples. |
| **Sapiru — Baal Cycle pt. I** ✅ | Accessible English Baal-vs-Yam; quotable in `01`/`04` slides. |
| **Interbible / intertextual.bible (KTU)** ✅ | KTU ↔ Bible cross-links; supports the "background to biblical tradition" thread (`01`, `05`). |

---

## 5. Tools & cross-references (Hour 3 close)

| Resource | Use |
|----------|-----|
| **UgaritGPT** (custom GPT) | Hour 3 LLM demo — and a live example of the "where LLMs mislead" caution (`07`/`08`). |
| **Regex: strong roots** `r"[^ʔʕyhwḥḫ]-[^ʔʕyhwḥḫ]-[^ʔʕyhwḥḫ]"` | Hour 2/3: finding tri-consonantal roots without weak radicals — a neat morphology mini-demo. |
| **ContextFabric MCP / Sefaria Texts MCP** | Verified Hour 3 demo: local CUC+BHSA via `cfabric-mcp`; hosted Sefaria at `https://mcp.sefaria.org/sse`. |

---


### UDB access note

The **Ugaritic Data Bank** was produced by a Spanish team of scholars and includes
the texts in CAT, mostly under the same numbers; cite Cunchillos, Vita, and
Zamora 2003. For the workshop pipeline, do not download or redistribute UDB data
from HuggingFace or any repository. Participants must obtain the PDF through an
authorized channel, run `python -m workshop_tools.build_udb_parquet`, and keep the
PDF plus generated Parquet tables local.

---

## 7. Gaps & recommended next actions

Done in this pass: ✅ real CUC loader wired to the HuggingFace Parquet export; ✅
all 7 notebooks now run on real CUC data after automatic cache download; ✅ UDB
parser generates Parquet tables from PDF; ✅ alphabet complexity and omen tree extracted; ✅ licence/feature
facts corrected. Remaining:

1. **Set up CUC locally.** Usually no manual setup is needed; first notebook run
   reads the bundled `data/cuc/cuc.parquet` snapshot. For
   offline use, place CUC Parquet files in `data/cuc/`.
2. **Set up UDB locally.** Students must obtain the UDB PDF through an authorized
   channel and run `python -m workshop_tools.build_udb_parquet` to generate Parquet
   tables in `local_data/udb/`.
3. **Implement CUC queries as notebook cells.** Add pandas/DuckDB queries to the
   notebooks for mḫṣ forms, duplicate lines, hapax, n-grams-with-refs (mapped to
   the exercises above).
   the abecedary figure and any Latin↔cuneiform conversion in slides.
4. **Lock image licences.** Decide the 3–5 slide images now (Persée is safest);
   record credit lines in `images/README.md`.
5. **Refine genre labels.** `loader.py:FINE_GENRE` is a conservative starter; extend
   it from KTU's own classification if you want sharper Hour-2 clustering.
