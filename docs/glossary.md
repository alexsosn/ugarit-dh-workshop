# Glossary — technical terms in plain language

For historians and philologists. Every computational term used in this workshop,
explained in a sentence or two, with a Ugaritic example where it helps. No prior
coding knowledge assumed. Grouped to follow the workshop's arc; skim or search.

> Rule of thumb: most of these are **ordinary research moves with a technical
> name**. "Count the words" becomes "frequency analysis"; "which texts look alike"
> becomes "similarity". The idea is usually familiar; only the label is new.

---

## The basics

**DH — Digital Humanities.** Using computational methods (counting, searching,
mapping, modelling) to study humanities material — here, ancient texts.

**Corpus.** A body of texts treated as data. Our corpus is **CUC**, 278 Ugaritic
tablets. Crucially, a digital corpus is *not* an e-book: it is a structured set of
objects (tablets, lines, words, signs) you can query, not just read.

**Token.** One word-occurrence in a text. The line *bʿl . sid . zbl . bʿl* has
four tokens (and *bʿl* occurs twice). "Tokenising" just means splitting a line
into its words and dropping the dividers/brackets.

**Word form vs lemma.** A **form** is the word exactly as written (*ytn*, *ttn*);
the **lemma** is its dictionary headword (the root/verb "to give"). CUC currently
has forms but **no lemmas**, so our counts treat *ytn* and *ttn* as different
words — a caveat to keep in mind.

**Part of speech (POS).** The grammatical class of a word: noun, verb, particle,
divine name, etc.

**Morphological tagging.** Labelling each word with its lemma, part of speech, and
features (person, number, stem…). It is the slow, expert layer that makes every
later analysis sharper; CUC does not yet have it.

**Hapax (hapax legomenon).** A word that occurs only **once** in the corpus.
Hapaxes are interesting precisely because they're rare — often loanwords, names,
or hard-to-read spots.

---

## Counting and weighting words

**Frequency.** How often something occurs. The whole alphabet exercise (notebook
`1b`) is frequency analysis: count each sign, compare to the alphabet order.

**n-gram.** A run of *n* adjacent words. A **bigram** is two words (*aliyn bʿl*,
"Mighty Baal"); a **trigram** is three (*kṯr w ḫss*, the god Kothar-wa-Hasis).
Frequent n-grams are how we find **formulas** automatically (notebook `3a`).

**TF-IDF (term frequency–inverse document frequency).** A way to find the words
that *characterise* one text. It rewards words that are frequent **in that tablet**
but rare **across the whole corpus**, and down-weights words that are everywhere
(*w* "and", *l* "to"). The result is each tablet's "signature vocabulary"
(notebook `2a`). Think of it as: *distinctive = common here, but not common
generally.*

**Keyword (TF-IDF sense).** Not a hashtag — just the top-scoring words from TF-IDF
for a given text.

---

## Comparing and grouping texts

**Vector.** A list of numbers standing for a text — e.g. how much each vocabulary
item weighs in it (its TF-IDF scores). Turning texts into vectors lets a computer
compare them by arithmetic.

**Vector space.** The imaginary multi-dimensional space those vectors live in.
"Near" in that space ≈ "similar vocabulary".

**Cosine similarity.** A 0-to-1 score for how alike two text-vectors are: 1 =
identical vocabulary, 0 = nothing shared. It's the measure behind "nearest tablets"
(notebook `2b`).

**Clustering.** Letting the computer **group** texts by similarity *without being
told the genres*. If the groups line up with the philologists' genres, the
vocabulary alone "knew" the genre.

**k-means.** One common clustering method; the *k* is how many groups you ask for
(we use 4). It is "blind" — it never sees the genre labels, which is exactly why
matching them is striking.

**Dimensionality reduction (PCA · UMAP · SVD).** Vocabulary space has thousands of
dimensions; we can't see that. These methods **squash it down to 2-D** so we can
plot each tablet as a dot, keeping similar tablets near each other. **UMAP** is the
one behind the interactive genre map; **PCA** is a simpler fallback. (You don't
need the maths — just "flatten many dimensions to a readable picture".)

---

## Networks (graphs)

**Graph / network.** Dots joined by lines, used to model relationships — here, who
wrote to whom (notebook `3b`). (Not a "graph" in the chart sense.)

**Node.** A dot — a person, place, or institution.

**Edge.** A line joining two nodes — e.g. "X wrote to Y". A **directed** edge has
an arrow (sender → recipient).

**Degree / betweenness centrality.** Two ways to measure how "important" a node is.
**Degree** = how many connections it has; **betweenness** = how often it sits on
the path between others (a broker/hub). High-centrality nodes in the letters are
often titles (*mlk* "king", *umy* "my lady") — a caveat, since a title isn't one
person.

**Component.** A connected island in the network; fragments that don't link to the
rest form separate components — often an artefact of broken tablets.

---

## Structures and data formats

**Decision tree.** A branching "if → then" diagram. Omen texts (*if the foetus
lacks X → the land will…*) are already decision trees in prose; notebook `3c` just
draws them out.

**JSON.** A simple, human-readable text format for structured data — labelled
fields nested inside braces `{ }`. We use it to write an omen down as
`{"sign": …, "outcome": …, "polarity": …}`.

**JSONL ("JSON lines").** A file with one JSON record per line. The CUC corpus
ships this way: one line = one tablet-line, with its transliteration and reference.

**Parquet.** A compact, columnar file format for tabular data; the HuggingFace
copy of CUC uses it so it can be queried fast.

**SQL · SQLite · DuckDB.** **SQL** is the standard language for asking questions of
a table ("how many lines mention *mlk*?"). **SQLite** and **DuckDB** are
lightweight databases that understand SQL — the Hour-3 demo builds a SQLite from a
PDF, then asks it questions.

**Schema.** The shape of a database: which tables exist and what columns they have
(e.g. `tablets(udb_id, ref, text)`).

---

## Infrastructure and tools

**Text-Fabric / ContextFabric.** Software for storing a text **as a graph of
objects and features** (tablet → line → word → sign) and querying it. CUC is a
Text-Fabric dataset; **ContextFabric** is a newer engine built on the same model.

**HuggingFace.** A popular website for sharing datasets and AI models; our CUC
copy lives there.

**Repository ("repo") · GitHub.** A repo is a versioned project folder (code +
data + docs). **GitHub** hosts repos online; the workshop repo lives there.

**Jupyter notebook · cell.** A document that mixes text and runnable code in
**cells** you execute one at a time by pressing ▶. The `.ipynb` files are
notebooks.

**Google Colab · Binder.** Free services that run a notebook **in your browser**,
so nothing is installed on your machine. The "Open in Colab" badges launch them.

**Python · package · import.** **Python** is the programming language we use.
A **package** is a reusable bundle of code (e.g. `pandas` for tables); `import`
loads one into a notebook.

**Regular expression ("regex").** A compact pattern for searching text — e.g. a
pattern that matches any three-consonant root avoiding the weak letters. Powerful,
but terse-looking.

**API.** A defined way for one program to request something from another (e.g.
fetch the list of CUC files). You rarely see it directly; it works behind a button.

**Unicode.** The universal character standard. Ugaritic cuneiform signs (𐎀 𐎁 𐎂…)
have official Unicode codepoints, so they display and sort like any other text.

---

## Artificial intelligence

**LLM — Large Language Model.** An AI trained on huge amounts of text that
predicts and generates language (ChatGPT, Claude, Gemini are LLMs). Useful for
drafting, extracting structure, and explaining — but it can be confidently wrong.

**Agent / coding agent.** An LLM allowed to *take actions in steps* — read files,
write and run code, check results — to accomplish a goal. The Hour-3 demo uses a
coding agent to build a database from a PDF.

**MCP — Model Context Protocol.** A common "plug" standard that lets an AI
assistant connect to outside tools and data sources (a corpus, a dictionary, a
search index). "ContextFabric MCP" means: the corpus is exposed so an AI agent can
query it directly.

**Embedding · FastText · gensim.** An **embedding** turns a word (or text) into a
vector of numbers that captures meaning, so "similar" words sit near each other.
**FastText** is one method for making word embeddings; **gensim** is a Python
library that does this. (UgaritLab uses these for semantic search — finding
related words beyond exact matches.)

**Hallucination.** When an LLM states something fluent but **false** — e.g.
filling a broken `[…]` spot in an omen with an invented reading. This is the core
caution of Hour 3: the model is a powerful assistant, not an authority.

**Custom GPT.** A version of ChatGPT preconfigured for one task or dataset (e.g.
"UgaritGPT"). Requires a paid account to build, which is why Hour 3 leans on free
tools for the live demo.

---

*See also: `00-resources.md` (corpora & tools), `08-modern-toolkit.md` (how these
fit together), and the notebooks, where each method is run on real data.*
