# Data — sources, structure, and citation map

This folder holds the data layer for the workshop. Notebooks never read raw
files directly; they call `loader.py`, which returns a uniform list of tablets.
The notebooks use the real CUC corpus through a downloaded HuggingFace Parquet
cache and UDB through locally-generated Parquet tables.

## Files

- **`loader.py`** — downloads/caches the line-level CUC Parquet file from the
  HuggingFace dataset `AlexWalhai/CUC` and returns tablet dicts. If `data/cuc/`
  or `UGARIT_CUC_DIR` contains Parquet files, those local files are used instead.
  The Parquet is exported from the Text-Fabric dataset `DT-UCPH/cuc`.
  **Underlying corpus licence: CC BY-NC 4.0** — educational / non-commercial use,
  attribution required. API: `load_texts`, `texts_by_genre`, `token_counts`,
  `corpus_as_documents`,
  `load_alphabet`, `sign_counts`, `load_omen_tree`.
- **`udb_loader.py`** — loads UDB data from locally-generated Parquet tables in
  `../local_data/udb/`. Students must generate these tables by running
  `python -m workshop_tools.build_udb_parquet` with a locally-supplied PDF.
  See setup instructions below.
- **`alphabet.json`** — the 30 signs in abecedary order with cuneiform codepoints
  and a **complexity** score (wedges + turns), for the alphabet hypothesis (`1b`).
- **`sound_correspondences.json`** — aggregate aligned-consonant counts exported
  from the DULAT app for the comparative diagram in `1b`. The source pipeline
  aligns consonantal cognate forms with Needleman–Wunsch and iteratively refines
  the alignment scores. This workshop snapshot omits lexical examples and DULAT
  entry identifiers; edge weight is an aligned-column count, not a probability.
- **`ugaritic_wiktionary.json`** — an offline snapshot of 792 English Wiktionary
  Ugaritic records (731 unique cuneiform headwords), including POS, definitions,
  and source-page URLs. Used only for the dictionary-audit exercise in `3a`.
- **`fonts/NotoSansUgaritic-Regular.ttf`** — bundled Ugaritic glyph fallback,
  distributed under the SIL Open Font License in `fonts/OFL.txt`.
- **`omens/`** — a real Ugaritic birth-omen text + a hand-built decision tree
  (`sheep_birth_omens.json`) and rendered image, for the divination notebook (`3c`).

## Setup instructions

### CUC Parquet files

1. Run any notebook; `loader.py` downloads `data/cuc.parquet` from
   <https://huggingface.co/datasets/AlexWalhai/CUC> into
   `data/_cache/cuc-parquet/`.
2. Optional offline setup: place one or more CUC Parquet files in `data/cuc/`, or
   set `UGARIT_CUC_DIR` to a directory containing them.
3. Do not use the older JSONL cache; the loader reads Parquet only.

### UDB Parquet tables

1. Obtain the Ugaritic Data Bank PDF through an authorized channel
2. Save it as `local_data/Ugaritic_data_bank.pdf` (relative to the repo root)
3. Run: `python -m workshop_tools.build_udb_parquet`
4. This generates Parquet tables in `local_data/udb/`
5. Notebooks will automatically find and use these tables

## Primary data sources & citation map

| Resource | What it is | How to get it |
|----------|-----------|---------------|
| **CUC — Cuneiform Ugaritic Corpus** | Work-in-progress Text-Fabric dataset, 279 KTU tablets, CACCHT project, CC BY-NC 4.0 | Original: `DT-UCPH/cuc` on GitHub; HuggingFace Parquet export used here: `AlexWalhai/CUC` |
| **ContextFabric** | Graph corpus engine on the Text-Fabric model; `cfabric-mcp` MCP server for LLM/agents | `Context-Fabric` on GitHub |
| **UDB — Ugaritic Data Bank** | Corpus by Jesús-Luis Cunchillos, Juan-Pablo Vita, José-Ángel Zamora, and Raquel Cervigón; Latin transliteration + bibliography + commentary. The 2003 source notice requires citation and reserves reproduction, computerized processing, and distribution without written authorization. | The workshop distributes parser code only. Participants must obtain the PDF through an authorized channel and generate Parquet tables locally using `python -m workshop_tools.build_udb_parquet`. Do not share the PDF or derived data. |
| **KTU** | *Die keilalphabetischen Texte aus Ugarit* — standard numbering | print + mapped in digital editions |
| **DULAT** | *Dictionary of the Ugaritic Language in the Alphabetic Tradition* | print / licensed digital |
| **Oracc (UGA)** | Open Richly Annotated Cuneiform Corpus, Ugaritic annotation | oracc.museum.upenn.edu |
| **USC Digital Library / InscriptiFact** | High-resolution tablet images produced by Bruce Zuckerman and the West Semitic Research Project | Formerly `inscriptifact.com`; now surfaced through USC Digital Library, e.g. <https://digitallibrary.usc.edu/asset-management/2A3BF1OL6PW?&WS=SearchResults&Flat=FP> |
| **English Wiktionary — Ugaritic entries** | Offline teaching snapshot of lemma and non-lemma pages; incomplete by design, so exact lookup misses must remain visible | `data/ugaritic_wiktionary.json`; every record retains its English Wiktionary URL |

Reference schemes (KTU / CTA / UT) are cross-mapped in the major digital editions,
so texts can be cited and linked regardless of the original scheme.

The repo does not ship CUC Parquet files, a UDB PDF, or derived UDB database
files. CUC is downloaded into an ignored cache; UDB must be generated locally
from each participant's own PDF.

## Licenses

Workshop-authored material follows the root `LICENSE`. **Primary corpus data is
not covered by it** — each source keeps its provider's license. Check before
redistributing. The bundled Noto font remains under the SIL Open Font License.
The Wiktionary snapshot remains subject to Wiktionary/Wikimedia licensing and
attribution requirements; preserve its record-level source URLs when reusing it.
