# Resource catalogue — sorted & mapped to the workshop

A triaged index of the collected resources, sorted by type and mapped to the
hours / notebooks they feed. Verified items are noted; gated or
manual-access items are flagged so nothing surprises you live.

> **Legend:** ✅ verified · 🔑 needs login / manual access · ⚖️ check license before
> redistributing · ▶️ ready to wire into a notebook.

---

## 1. Live corpus data — the backbone ▶️

**DONE:** the real corpus is now bundled in `data/cuc/` (278 KTU tablets, JSONL
exported from your `ugaritic-nb` repo) and wired into `data/loader.py`. Every
notebook runs offline on real data. The fake sample is gone.

| Resource | What it is | Use |
|----------|-----------|-----|
| **`data/cuc/`** (bundled) ✅▶️ | 278 tablets, line-level JSONL: Latin + cuneiform + refs. | Primary data for all notebooks. |
| **`DT-UCPH/cuc`** (GitHub / Text-Fabric) ✅ | Source TF dataset (CACCHT). | Sign-level features (emendation, certainty, alt readings) the JSONL drops. |
| **`AlexWalhai/cuc`** (HuggingFace) ✅ | Same corpus, **7,577 rows**, Parquet, ~3.5 MB. | DuckDB/SQL console; word-level queries. |
| **ContextFabric** + `cfabric-mcp` | Graph engine + MCP server. | Hour 3 closing: LLM/agent access to the corpus. |

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
| **USC Digital Library / InscriptiFact** 🔑⚖️ | High-res tablet images; account/permission for reuse. Best quality. |
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
| **ContextFabric MCP / Sefaria MCP** | Reserve topics in `08-modern-toolkit.md`. |

---

## 6. Your existing experiments → notebook mapping (explored & verified)

I read the actual code. Status: ✅ = methods/data already folded into the bundled
notebooks; ↪ = referenced as the "production version" to port later.

| Your code | What it actually does | Feeds | Status |
|-----------|----------------------|-------|--------|
| `ugaritic-nb/notebooks/letter_frequencies.ipynb` | Loads `DT-UCPH/cuc` via Text-Fabric; counts signs; **has the wedge/turn complexity table** for all 30 signs. | `1b` | ✅ complexity table extracted → `data/alphabet.json`; `1b` rewritten to test frequency vs **complexity** and vs **order**. |
| `ugaritic-nb/cuc/json/*.jsonl` (278 tablets) | Line-level export: Latin + cuneiform + ref. | all | ✅ bundled into `data/cuc/`. |
| Wolfram, *Ugaritic letter frequencies* (UDB) | Same hypothesis on UDB. | `1b` | ↪ "two corpora, same question" comparison slide. |
| `ugaritic-nb/notebooks/script_translator.ipynb` | `unvocalized_to_ugaritic` / Latin↔cuneiform maps. | `03` / images | ↪ port for an abecedary figure + transliteration helper. |
| `ugaritic-nb/notebooks/tf_idf.ipynb` | Hand-rolled TF-IDF over tablet lines. | `2a` | ✅ superseded by the scikit-learn version in `2a`. |
| `omens/sheep_birth_omens.json` + `igaritic_omens.txt` + `ugaritic_omen_tree.png` | Real birth-omen text + nested decision tree + rendered image. | `3c` | ✅ copied to `data/omens/`; `3c` rewritten to load and draw the real tree. |
| `dulat/scripts/build_name_graph.py` | Co-occurrence graph of **PN/DN/TN/RN** names from DULAT, matched in UDB tablets. | `3b` | ↪ production name graph; `3b` ships a simpler address-formula parser. |
| `dulat/scripts/build_semantic_index.py` | **gensim** corpora/models/similarities index over DULAT entries + tablets. | `2b` | ↪ semantic (not just lexical) similarity. |
| `dulat/scripts/semantic_search.py` | **FastText** word-embedding nearest neighbours (handles OOV via sub-words). | `2b` | ↪ embeddings beyond TF-IDF. |
| `dulat/scripts/generate_stats.py` | Precomputes **TF-IDF + UMAP** 2-D/3-D projections + dendrogram + name graph → JSON. | `2a`/`2b` | ↪ the full pipeline `2a`/`2b` gesture at. |

**UgaritLab (`dulat`)** clearly already covers similarity search, clustering,
TF-IDF, and the name graph — Hour 2 and most of `3b` can be *demos of UgaritLab*
rather than from-scratch code.

---

## 7. Gaps & recommended next actions

Done in this pass: ✅ real CUC bundled + loader rewritten; ✅ all 7 notebooks now
run on real data; ✅ alphabet complexity + omen tree extracted; ✅ licence/feature
facts corrected. Remaining:

1. **Persist the SQL queries.** Copy the DuckDB query *text* (mḫṣ forms, duplicate
   lines, hapax, n-grams-with-refs) into the relevant notebooks so the live session
   doesn't depend on HuggingFace share-link tokens.
2. **Port the UgaritLab depth (↪ rows above).** Optional Hour-2/3 "production"
   demos: FastText `semantic_search.py`, gensim/UMAP `generate_stats.py`, and the
   DULAT name graph `build_name_graph.py`. These need the `dulat` env (gensim,
   sqlite DBs) — run them there and export figures/JSON into `images/`.
3. **Port `script_translator.py`** maps into a small `data/translit.py` helper for
   the abecedary figure and any Latin↔cuneiform conversion in slides.
4. **Lock image licences.** Decide the 3–5 slide images now (Persée is safest);
   record credit lines in `images/README.md`.
5. **Refine genre labels.** `loader.py:FINE_GENRE` is a conservative starter; extend
   it from KTU's own classification if you want sharper Hour-2 clustering.

---

*See `data/README.md` for the citation map of CUC / ContextFabric / UDB / KTU /
DUL-DULAT, and `README.md` for the workshop plan.*
