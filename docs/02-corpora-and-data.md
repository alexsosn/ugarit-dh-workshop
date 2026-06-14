# 2. Excavations, tablets, and corpora as data

*Hour 1 · ~15 min · presenter reading, leads into notebook `1a`*

> **Status:** outline stub.

## Excavations and archives
- Excavations: **1928–1939**, resumed **1950–2008**.
- Royal palace and temple **archives and libraries** preserved thousands of clay
  tablets in alphabetic cuneiform (and other scripts/languages).

## One tablet, many forms
A single tablet exists at once as a **museum object, photograph, transliteration,
translation, commentary, dictionary references, catalogue entry, corpus record,
and bibliography.**

> **Central idea:** the DH task *begins* with integrating these scattered
> representations into normalized, queryable data.

## From book to corpus
A digital corpus is **not an e-book**. It is a **graph of objects and features**:
text → line → word → morphological unit, each carrying features (form, lemma,
part of speech, …).

## The main resources (detail in `../data/README.md`)
- **CUC — Cuneiform Ugaritic Corpus**: original Text-Fabric dataset, 278 KTU
  tablets (CACCHT), plus the `AlexWalhai/cuc` HuggingFace JSONL mirror used by
  the notebooks.
- **ContextFabric**: graph corpus engine + `cfabric-mcp` server for LLMs/agents.
- **UDB — Ugaritic Data Bank**: Spanish-team corpus of CAT texts, mostly under
  the same numbers; now a licensed Accordance package, with UDB/concordance PDFs
  listed on Juan-Pablo Vita's Academia page.
- **USC Digital Library / InscriptiFact**: high-resolution tablet photographs
  from Bruce Zuckerman and the West Semitic Research Project; formerly
  `inscriptifact.com`, now under USC Digital Library access/reuse terms.
- **KTU**: standard text numbering; **DUL/DULAT**: the standard dictionary.
- For comparison: **BHSA** (Hebrew Bible), **DSS** (Dead Sea Scrolls), and other
  Text-Fabric / ContextFabric corpora.

## TODO
- [ ] Add a diagram: "one tablet → nine representations".
- [ ] Add a screenshot of a Text-Fabric corpus structure.
- [ ] Tie explicitly to notebook `1a_corpora_and_data`.
