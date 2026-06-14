# 4. Genres of Ugaritic texts

*Hour 2 · ~10 min reading + leads into notebooks `2a` / `2b`*

> **Status:** outline stub.

## The main genres
- **Mythological texts** — e.g. the Baal Cycle, Kirta, Aqhat (KTU 1.x).
- **Ritual texts** — sacrifices, calendars, liturgies (KTU 1.4x).
- **Divination texts** — omens (astral, birth, extispicy) with conditional structure.
- **Letters** — diplomatic, administrative, personal (KTU 2.x).
- **Administrative documents** — lists, accounts, rations (KTU 4.x).
- **Lexical / school texts** — abecedaries, vocabularies (KTU 5.x).

## The KTU numbering convention
In CAT/KTU, each text has a unique number consisting of a single digit genre code,
followed by a period, followed by one to three more digits. For example:
`KTU 1.14`, `KTU 3.2`, `KTU 4.143`.

The first digit indicates the genre of the text:
- **1.** literary and religious texts
- **2.** letters
- **3.** legal texts
- **4.** economic or administrative texts
- **5.** scribal exercises
- **6.** inscriptions on seals, labels, ivories, etc.
- **7.** unclassified texts
- **8.** illegible tablets and uninscribed fragments
- **9.** unpublished texts

> **Central question for Hour 2:** *How much of the genre is visible from the
> vocabulary alone?* We test this with TF-IDF keywords (`2a`) and with similarity
> + clustering (`2b`), then compare the machine's grouping to the philologists'.

## Caveats to flag before the exercises
- Word **forms vs lemmas** (no morphological normalization in the sample data).
- **Short** and **damaged** texts distort statistics.
- **Genre formulas** can dominate; watch for **false thematic signals**.

## TODO
- [ ] Note how many texts per genre are in the working corpus.
