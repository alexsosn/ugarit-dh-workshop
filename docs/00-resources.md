# Resources

A triaged index of the collected resources, sorted by type and mapped to the
hours / notebooks they feed.

> **New term?** *Parquet, DuckDB, MCP, UMAP, FastText, embedding* and other
> computational terms are unpacked in plain language in [glossary.md](glossary.md).

---

## 1. Live corpus data — the backbone ▶️

| Resource | What it is | Use |
|----------|-----------|-----|
| **`AlexWalhai/cuc`** (HuggingFace) ✅▶️ | 278 tablets, Parquet: Latin + cuneiform + refs. | Primary data source used by `data/loader.py`. |
| **`DT-UCPH/cuc`** (GitHub / Text-Fabric) ✅ | Source CUC Text-Fabric dataset, 278 KTU tablets, CACCHT project, CC BY-NC 4.0. | Full graph features: tablet, column, line, side, `g_cons`, trailer, language, sign, `emen`, `cert`, `cont`, `alt`. |
| **UDB — Ugaritic Data Bank** 🔑⚖️ | Spanish-team electronic corpus, mostly using CAT/KTU numbers; see Cunchillos, Vita, and Zamora 2003. | Licensed package in Accordance; UDB PDFs and concordance files are listed on Juan-Pablo Vita's [Academia page](https://csic.academia.edu/JuanPabloVita).|
| **ContextFabric** + `cfabric-mcp` | Graph engine + MCP server. Tested locally with Python 3.13 in `~/projects/mcp-demo/`. | Hour 3 closing: LLM/agent access to CUC + BHSA. |

> ⚖️ **Licence correction:** the CUC Text-Fabric data is **CC BY-NC 4.0**
> (`@licence` in the `.tf` headers, and the `cuc` repo README). The HuggingFace
> page tags the *packaging* as MIT — the **underlying corpus is CC BY-NC 4.0**, so
> treat the data as non-commercial + attribution. The workshop repo notes this in
> `LICENSE` and `data/README.md`.
>
> ⚙️ **Feature correction:** CUC 0.1.x has **no lemma / part-of-speech** layer —
> only `g_cons` (consonantal word form) and sign-level features. The TF-IDF /
> similarity notebooks therefore work on **forms, not lemmas** (homographs blur
> the signal). "Morphological tagging" in `08-modern-toolkit.md` is the *future*
> goal, not current CUC.
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

CUC currently contains **278 tablets** from KTU 1.x-3.x. Coverage includes:

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


### Saved CUC SQL-console queries (DuckDB) — ready-made demos 🔑*(share-links)*

These map directly onto exercises. Re-create them as notebook cells against the
HF Parquet so they don't depend on the share-link surviving.

| Query | Workshop slot |
|-------|---------------|
| Frequency of verb **mḫṣ** forms | Hour 1 `1a` (forms/queries); Hour 3 morphology close |
| **Duplicate lines** | Hour 3 `3a` formulas / parallelism |
| **Hapax** forms | Hour 2 `2a` (lexical stats, rare words) |
| Frequent **trigrams** (divine epithets) | Hour 3 `3a` formula search |
| Frequent **bigrams** | Hour 3 `3a` formula search |
| N-grams **with references** | Hour 3 `3a` (cite the formula's attestations) |
| "Similar places" search | Hour 3 `3b` name/place graph |

> The share-token URLs (`…/sql-console/<id>`) are personal/session links — keep the
> **SQL text** in the repo, not just the link.

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
| **CDLI** (`language=Ugaritic`) ✅ | Canonical IDs, transliterations, provenance — the "many forms of one tablet" point in `02-corpora-and-data.md`. |
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
Zamora 2003. It was formerly accessible online, but is now distributed commercially
as an Accordance Bible Software package. For the workshop/demo pipeline, do not
redistribute UDB data: direct participants to Juan-Pablo Vita's
[Academia page](https://csic.academia.edu/JuanPabloVita), where PDF files of the
UDB texts and concordance are listed.

---

## 7. Gaps & recommended next actions

Done in this pass: ✅ real CUC loader wired to HuggingFace JSONL; ✅ all 7
notebooks now run on real data after the first cache fill; ✅ alphabet complexity
and omen tree extracted; ✅ licence/feature facts corrected. Remaining:

1. **Persist the SQL queries.** Copy the DuckDB query *text* (mḫṣ forms, duplicate
   lines, hapax, n-grams-with-refs) into the relevant notebooks so the live session
   doesn't depend on HuggingFace share-link tokens.
3. **Port `script_translator.py`** maps into a small `data/translit.py` helper for
   the abecedary figure and any Latin↔cuneiform conversion in slides.
4. **Lock image licences.** Decide the 3–5 slide images now (Persée is safest);
   record credit lines in `images/README.md`.
5. **Refine genre labels.** `loader.py:FINE_GENRE` is a conservative starter; extend
   it from KTU's own classification if you want sharper Hour-2 clustering.

