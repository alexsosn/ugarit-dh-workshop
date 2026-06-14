# 2. Excavations, tablets, and corpora as data

*Hour 1 · ~15 min · presenter reading, leads into notebook `1a`*

> **Status:** outline stub.

## Excavations and archives
- Excavations: **1928-1939**, resumed **1950-2008**. The Ras Shamra mound was
  identified after remains were exposed near Minet el-Beida; French excavations
  under Claude F.A. Schaeffer began in **1929**.
- Ugarit's best-documented phase is the Late Bronze Age, c. **1450-1200 BCE**:
  royal palaces, temples, shrines, an acropolis library, family/private archives,
  and administrative records.
- Royal, temple, palatial, and private **archives and libraries** preserve clay
  tablets in alphabetic Ugaritic cuneiform and other scripts/languages.
- The tablets cover political, social, economic, religious, and cultural life,
  which is why Ugarit works so well as a compact DH corpus.

*Background source: Encyclopaedia Britannica,
["Ugarit"](https://www.britannica.com/place/Ugarit).*

## One tablet, many forms
A single tablet exists at once as a **museum object, photograph, transliteration,
translation, commentary, dictionary references, catalogue entry, corpus record,
and bibliography.**

> **Central idea:** the DH task *begins* with integrating these scattered
> representations into normalized, queryable data.

![KTU 1.1, first tablet of the Baal Myth, Louvre AO 16641.](../images/0000215274_OG.JPG)

*Figure: **KTU 1.1**, the first tablet of the Baal Myth. Local corpus links:
[KTU 1.1](http://localhost:8000/texts/page/?ref=KTU%201.1) /
[Baal Myth First Tablet](http://localhost:8000/texts/page/?ref=KTU%201.1).
Louvre, AO 16641; source:
[Louvre collections](https://collections.louvre.fr/en/ark:/53355/cl010141446).
Image © 2004 GrandPalaisRmn (musée du Louvre) / Franck Raux.*

This is the same object seen through several lenses: museum object, photograph,
KTU number, literary label, digital corpus page, transliteration, and eventually
tokens in a notebook. A corpus is useful precisely because it keeps those layers
linked.

## From book to corpus
A digital corpus is **not an e-book**. It is a **graph of objects and features**:
text → line → word → morphological unit, each carrying features (form, lemma,
part of speech, …).

## The main resources (detail in `../data/README.md`)
- **CUC — Cuneiform Ugaritic Corpus**: original Text-Fabric dataset, 278 KTU
  tablets (CACCHT), plus the `AlexWalhai/cuc` HuggingFace JSONL mirror used by
  the notebooks. It is a work-in-progress digital corpus from the CACCHT project
  (Christian Canu Højgaard, Martijn Naaijer, Martin Ehrensvärd, Robert Rezetko,
  Oliver Glanz, Willem van Peursen), licensed **CC BY-NC 4.0**.
- **CUC coverage:** 278 KTU tablets, currently in ranges **KTU 1.1-1.180**,
  **KTU 2.1-2.113**, and **KTU 3.1-3.35**; not every number in those ranges is
  present.
- **CUC features:** tablet, column, line, side, consonantal word form
  (`g_cons`), word divider/trailer, language, sign, emendation (`emen`),
  certainty (`cert`), line continuation (`cont`), and alternative reading
  (`alt`).
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
