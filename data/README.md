# Data — sources, structure, and citation map

This folder holds the data layer for the workshop. Notebooks never read raw
files directly; they call `loader.py`, which returns a uniform list of tablets.
The notebooks use the real CUC corpus through JSONL files hosted on HuggingFace;
the first run downloads them into a local cache.

## Files

- **`loader.py`** — downloads/caches line-level JSONL files from the HuggingFace
  dataset `AlexWalhai/cuc` and returns tablet dicts. The JSONL is exported from
  the Text-Fabric dataset `DT-UCPH/cuc`. **Underlying corpus licence: CC BY-NC
  4.0** — educational / non-commercial use, attribution required. API: `load_texts`,
  `texts_by_genre`, `token_counts`, `corpus_as_documents`, `load_alphabet`,
  `sign_counts`, `load_omen_tree`.
- **`alphabet.json`** — the 30 signs in abecedary order with cuneiform codepoints
  and a **complexity** score (wedges + turns), for the alphabet hypothesis (`1b`).
- **`omens/`** — a real Ugaritic birth-omen text + a hand-built decision tree
  (`sheep_birth_omens.json`) and rendered image, for the divination notebook (`3c`).



## Primary data sources & citation map

| Resource | What it is | How to get it |
|----------|-----------|---------------|
| **CUC — Cuneiform Ugaritic Corpus** | Work-in-progress Text-Fabric dataset, 278 KTU tablets, CACCHT project, CC BY-NC 4.0 | Original: `DT-UCPH/cuc` on GitHub; HuggingFace mirror used here: `AlexWalhai/cuc` |
| **ContextFabric** | Graph corpus engine on the Text-Fabric model; `cfabric-mcp` MCP server for LLM/agents | `Context-Fabric` on GitHub |
| **UDB — Ugaritic Data Bank** | Corpus by Jesús-Luis Cunchillos, Juan-Pablo Vita, José-Ángel Zamora, and Raquel Cervigón; Latin transliteration + bibliography + commentary. The 2003 source notice requires citation and reserves reproduction, computerized processing, and distribution without written authorization. | The workshop distributes parser code only. Participants must obtain any source through an authorized channel, process it locally, and not share the PDF or derived database. |
| **KTU** | *Die keilalphabetischen Texte aus Ugarit* — standard numbering | print + mapped in digital editions |
| **DULAT** | *Dictionary of the Ugaritic Language in the Alphabetic Tradition* | print / licensed digital |
| **Oracc (UGA)** | Open Richly Annotated Cuneiform Corpus, Ugaritic annotation | oracc.museum.upenn.edu |
| **USC Digital Library / InscriptiFact** | High-resolution tablet images produced by Bruce Zuckerman and the West Semitic Research Project | Formerly `inscriptifact.com`; now surfaced through USC Digital Library, e.g. <https://digitallibrary.usc.edu/asset-management/2A3BF1OL6PW?&WS=SearchResults&Flat=FP> |

Reference schemes (KTU / CTA / UT) are cross-mapped in the major digital editions,
so texts can be cited and linked regardless of the original scheme.

The repo does not ship CUC JSONL files; it points to the original CUC source
and the HuggingFace JSONL mirror. It also does not ship a UDB PDF or derived
UDB database.

## Licenses

Workshop-authored material follows the root `LICENSE`. **Primary corpus data is
not covered by it** — each source keeps its provider's license. Check before
redistributing.
