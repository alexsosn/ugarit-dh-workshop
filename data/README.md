# Data — sources, structure, and citation map

This folder holds the data layer for the workshop. Notebooks never read raw
files directly; they call `loader.py`, which returns a uniform list of tablets.
**The bundled data is the real corpus** — no downloads, runs offline.

## Files

- **`cuc/`** — the **Copenhagen Ugaritic Corpus**, 278 KTU tablets as line-level
  JSONL (Latin transliteration + cuneiform unicode + per-line reference). Exported
  from the Text-Fabric dataset `DT-UCPH/cuc`. **Licence: CC BY-NC 4.0** —
  educational / non-commercial use, attribution required.
- **`loader.py`** — reads `cuc/` and returns tablet dicts. API: `load_texts`,
  `texts_by_genre`, `token_counts`, `corpus_as_documents`, `load_alphabet`,
  `sign_counts`, `load_omen_tree`.
- **`alphabet.json`** — the 30 signs in abecedary order with cuneiform codepoints
  and a **complexity** score (wedges + turns), for the alphabet hypothesis (`1b`).
- **`omens/`** — a real Ugaritic birth-omen text + a hand-built decision tree
  (`sheep_birth_omens.json`) and rendered image, for the divination notebook (`3c`).

### What CUC contains (and does not)

CUC 0.1.x annotates: **tablet, column, line, side, word (`g_cons` = consonantal
form), sign, trailer**, plus sign-level **emendation / certainty / alternative
reading**. It does **not** (yet) carry lemma or part-of-speech tags — so the
TF-IDF / similarity notebooks work on **word forms**, not lemmas. Flag this when
discussing homographs.

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
| **CUC — Cuneiform Ugaritic Corpus** | Text-Fabric dataset, 278 KTU tablets (CACCHT project) | `DT-UCPH/cuc` on GitHub; `pip install text-fabric` |
| **ContextFabric** | Graph corpus engine on the Text-Fabric model; `cfabric-mcp` MCP server for LLM/agents | `Context-Fabric` on GitHub |
| **UDB — Ugaritic Data Bank** | Latin transliteration + bibliography + commentary | via Logos / Accordance editions |
| **KTU** | *Die keilalphabetischen Texte aus Ugarit* — standard numbering | print + mapped in digital editions |
| **DUL / DULAT** | *Dictionary of the Ugaritic Language in the Alphabetic Tradition* | print / licensed digital |
| **Oracc (UGA)** | Open Richly Annotated Cuneiform Corpus, Ugaritic annotation | oracc.museum.upenn.edu |
| **InscriptiFact** | High-resolution tablet images | inscriptifact.com |

Reference schemes (KTU / CTA / UT) are cross-mapped in the major digital editions,
so texts can be cited and linked regardless of the original scheme.

> **TODO for organizers:** decide which real corpus to ship/point to for the live
> session, confirm licenses before redistributing any of the above, and (if using
> CUC) complete the wiring in `loader.py:_try_load_cuc`.

## Licenses

Workshop-authored material follows the root `LICENSE`. **Primary corpus data is
not covered by it** — each source keeps its provider's license. Check before
redistributing.
