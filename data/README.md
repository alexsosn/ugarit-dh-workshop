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

## The "one tablet, many forms" problem

A single Ugaritic tablet exists simultaneously as: a museum object, a photograph,
a transliteration, a translation, a commentary, dictionary references, a catalogue
entry, a corpus record, and a bibliography. The first DH task is **integrating**
these scattered representations. The minimal record we use:

```json
{
  "ktu": "1.23",
  "museum_id": "...",
  "genre": "ritual",
  "language": "ugaritic",
  "lines": ["...", "..."],
  "transliteration": "...",
  "translation": "...",
  "photos": [],
  "bibliography": [],
  "lexical_links": [],
  "notes": []
}
```

## Primary data sources & citation map

| Resource | What it is | How to get it |
|----------|-----------|---------------|
| **CUC — Cuneiform Ugaritic Corpus** | Work-in-progress Text-Fabric dataset, 278 KTU tablets, CACCHT project, CC BY-NC 4.0 | Original: `DT-UCPH/cuc` on GitHub; JSONL mirror used here: `AlexWalhai/cuc` on HuggingFace |
| **ContextFabric** | Graph corpus engine on the Text-Fabric model; `cfabric-mcp` MCP server for LLM/agents | `Context-Fabric` on GitHub |
| **UDB — Ugaritic Data Bank** | Spanish-team corpus of CAT texts, mostly with the same numbers; Latin transliteration + bibliography + commentary. Cite Cunchillos, Vita, and Zamora 2003. | Licensed Accordance package; UDB texts and concordance PDFs are listed on Juan-Pablo Vita's Academia page: <https://csic.academia.edu/JuanPabloVita> |
| **KTU** | *Die keilalphabetischen Texte aus Ugarit* — standard numbering | print + mapped in digital editions |
| **DUL / DULAT** | *Dictionary of the Ugaritic Language in the Alphabetic Tradition* | print / licensed digital |
| **Oracc (UGA)** | Open Richly Annotated Cuneiform Corpus, Ugaritic annotation | oracc.museum.upenn.edu |
| **USC Digital Library / InscriptiFact** | High-resolution tablet images produced by Bruce Zuckerman and the West Semitic Research Project | Formerly `inscriptifact.com`; now surfaced through USC Digital Library, e.g. <https://digitallibrary.usc.edu/asset-management/2A3BF1OL6PW?&WS=SearchResults&Flat=FP> |

Reference schemes (KTU / CTA / UT) are cross-mapped in the major digital editions,
so texts can be cited and linked regardless of the original scheme.

> **TODO for organizers:** confirm licenses before redistributing any primary
> data. The repo does not ship CUC JSONL files; it points to the original CUC
> source and the HuggingFace JSONL mirror.

## Licenses

Workshop-authored material follows the root `LICENSE`. **Primary corpus data is
not covered by it** — each source keeps its provider's license. Check before
redistributing.
