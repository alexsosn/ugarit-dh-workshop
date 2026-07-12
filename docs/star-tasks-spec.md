# ⭐ Star Tasks — Spec for Advanced Participants

> **Living spec. Advanced track; implementation remains partial.** Built after the notice
> that experienced programmers (non-historians) would join the otherwise
> non-coder cohort. Sections tagged **[settled]**, **[draft]**, **[open]**.

---

## 1. Purpose **[settled]**

Add an optional, harder track — **"tasks with a star," for the smart kids** —
so experienced programmers stay engaged without changing the workshop's
non-coder-first character. Inspiration: **Rosalind.info** / a "Ugaritic
HackerRank" — a dataset goes in, a known answer comes out, and the participant's
solution is **auto-checked against a predefined result**.

Difficulty may come from **linguistics** (parsing real Ugaritic formulae,
morphology, decipherment), from **data** (edge-cases, the graph corpus, scale),
or simply from being a **more time-consuming algorithm** than the guided cell
above it.

## 2. Delivery model **[settled]**

- **Inline, optional, segregated.** Each star task is an appended section at the
  **foot of the relevant existing notebook**, under a clear `## ⭐ Star task
  (optional)` heading, after the beginner `## ✍️ Your turn`. Non-coders simply
  stop before it; nobody switches files.
- **Self-contained + auto-graded offline.** Each task ends with a self-check that
  prints ✅ / ❌. No server, no internet beyond the corpus download the notebook
  already did. Colab-safe.
- **Tiered**, so a participant can pick their level:

  | Tier | Meaning |
  |------|---------|
  | ⭐ | Extend / harden an existing cell. ~10–20 min. |
  | ⭐⭐ | Build an algorithm from scratch, match a reference output. ~20–40 min. |
  | ⭐⭐⭐ | Research-grade or open-ended, graded against a measurable target. Take-home. |

## 3. Grading convention **[draft — confirm at build]**

Two interchangeable check styles; pick per task:

```python
# (a) exact value / structure
assert answer == EXPECTED, f"got {answer!r}"

# (b) hash, when EXPECTED is bulky or we don't want to reveal it
import hashlib, json
got = hashlib.sha256(json.dumps(answer, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
assert got == EXPECTED_SHA256, "not matched yet — keep going"

# (c) numeric within tolerance (stats/ML tasks)
assert abs(answer - EXPECTED) < TOL
```

**Optional shared helper (recommended).** Add `star_check(problem_id, answer)` to
`data/loader.py` (or a small `data/star.py`) backed by `data/star_answers.json`,
so every inline cell ends with one tidy line and a friendly ✅/❌. Self-contained
fallback: inline the `EXPECTED` constant directly in the cell.

> **⚠️ Source-of-truth rule [settled].** The bundled loader reads the
> HuggingFace CUC Parquet export and returns **279 tablets**. **All offline
> expected answers MUST be precomputed from the workshop's `data.loader` and the
> same downloaded/cached CUC Parquet file** that participants use. The Boss task
> (§5) is the only one graded against the MCP.

## 4. The tasks **[draft]**

Available data API (all in `data/loader.py`): `load_texts`, `texts_by_genre`,
`token_counts`, `all_tokens`, `corpus_as_documents`, `text_as_string`,
`clean_tokens`, `load_alphabet`, `sign_counts`, `load_catalog_titles`,
`load_omen_tree`, `load_omen_text`, `load_babylonian_izbu_tree`,
`load_babylonian_foetus_tree`, `load_babylonian_celestial_tree`,
`load_ugaritic_lunar_tree`, `load_ugaritic_dream_tree`. Each tablet dict:
`ktu, title, name, genre, language, lines, ugaritic, refs, tokens, source`.

---

### S1a — Re-implement the tokenizer  ⭐⭐
- **Lives in:** `1b_alphabet_hypothesis.ipynb` (tokenization now belongs to the
  text-facing notebook, not the object-metadata notebook 1a)
- **Difficulty:** data / edge-cases
- **Input:** the `lines` (Latin transliteration) of all 279 tablets.
- **Task:** write your own `my_clean_tokens(line)` from the KTU conventions —
  strip word dividers `.`, restorations `[ ]`, excisions `< >`, uncertainty
  marks, and broken signs (`x`, `xx`, …) — **without calling `clean_tokens`**.
- **Output:** for each tablet, the list of word forms.
- **Check:** your tokens equal the loader's `text["tokens"]` for **every** line of
  **every** tablet. `EXPECTED` is the loader output, computed at runtime.
- **Pitfalls:** diacritics (š ḥ ʿ ʾ ġ ṯ …) are kept; empty tokens dropped; the `x`
  rule is case-insensitive and whole-token only.
- **Lite variant (⭐) — KTU gap map:** from the loaded `ktu` numbers, list every
  KTU number absent within the contiguous ranges 1.1–1.180 / 2.1–2.113 / 3.1–3.35.
  Output a sorted list; `EXPECTED` precomputed. (Teaching point: a "gap" is a
  coverage artifact, not necessarily a non-existent tablet.)

### S1b — From correlation to significance  ⭐⭐
- **Lives in:** `1b_alphabet_hypothesis.ipynb`
- **Difficulty:** statistics
- **Input:** `load_alphabet()` (position, complexity per sign) + `sign_counts()`.
- **Task:** the guided cell computes a Pearson *r*. Replace it with **Spearman ρ
  and a permutation-test p-value** for both claims — *Claim A:* earlier signs are
  more frequent; *Claim B:* frequent signs are simpler.
- **Output:** `(rho_A, p_A, rho_B, p_B)`.
- **Check:** ρ exact to 3 dp; p within tolerance. **Determinism:** spec fixes
  `np.random.seed(0)` and `N_PERM = 10_000` so p is reproducible.
- **Stretch (⭐⭐⭐) — blind frequency cryptanalysis:** given **only** the cuneiform
  column (`ugaritic`), rank signs by frequency and recover the sign→translit map
  by matching against the known abecedary frequency profile; **score = exact
  matches / 30**. Target a realistic threshold (e.g. ≥ 12/30). Forbid using the
  parallel transliteration.

### S2a — TF-IDF from scratch  ⭐⭐
- **Lives in:** `2_similarity_clustering.ipynb`
- **Difficulty:** algorithm (match a reference exactly)
- **Input:** `corpus_as_documents(texts)`; target tablet **KTU 1.4**.
- **Task:** implement TF-IDF by hand (term counts → tf → idf → weight → L2 norm),
  **no `sklearn`**, and reproduce the top-10 keywords of KTU 1.4.
- **Output:** ordered list of 10 `(word, score)`.
- **Check:** ranked word list equals `sklearn`'s. **Must replicate the exact
  `TfidfVectorizer` params used in 2a** (vocabulary, `norm`, `smooth_idf`,
  `sublinear_tf`) — surfacing those defaults is the lesson. `EXPECTED` precomputed.
- **Variant (⭐⭐) — keyness:** Dunning **log-likelihood G²** for "myth vs. rest";
  return the top-15 over-represented forms. Deterministic.

### S2b — Does the genre map actually know the genres?  ⭐⭐
- **Lives in:** `2_similarity_clustering.ipynb` *(the headline notebook)*
- **Difficulty:** ML evaluation
- **Input:** the 4-genre TF-IDF sample already built in 2b (myth, letter, ritual,
  divination).
- **Task:** (1) **leave-one-out kNN** over cosine distance → classification
  accuracy + confusion matrix; (2) **adjusted Rand index** and **V-measure**
  between the KMeans clusters and the true genre labels; sweep k for best
  silhouette.
- **Output:** `(loo_accuracy, adjusted_rand, v_measure, best_k)`.
- **Check:** each numeric within tolerance. **Determinism:** spec fixes `k`
  (kNN), `KMeans(random_state=0, n_init=10)`, and the silhouette sweep range.
- **Why it matters:** turns the "wow" picture into a *measured* claim — exactly
  the confidence-building beat, leveled up.

### S3a — Longest shared formula  ⭐⭐
- **Lives in:** `3a_ngrams_formulas.ipynb`
- **Difficulty:** algorithm
- **Input:** `tokens` per tablet.
- **Task:** find the **longest word n-gram attested in ≥ 2 different tablets**.
  Naive is O(n²); a suffix-array / suffix-automaton makes it genuinely advanced.
- **Output:** `(phrase, sorted_list_of_tablet_ktus)`.
- **Check:** exact. **Tie-break [open]:** if several n-grams share the max length,
  return the lexicographically smallest (confirm at build).
- **Stretch (⭐⭐⭐) — frame–slot extractor:** define a "formula template" as a
  fixed frame with one variable slot (`w1 _ w3`); rank frames by productivity
  (distinct fillers × total count); return the top frame and its fillers.

### S3b — Robust address parser → correspondence graph  ⭐⭐
- **Lives in:** `3b_letter_networks.ipynb`
- **Difficulty:** linguistics (real formula parsing) + graph
- **Input:** the 105 tablets currently labelled `letter` by `data.loader`.
- **Task:** parse the Ugaritic epistolary address formula — `tḥm PN l PN`
  ("message of SENDER to RECIPIENT") and the `l PN rgm` / `tḥm PN` variants —
  more robustly than the guided cell, build the **directed sender→recipient
  graph**, and rank actors by **PageRank**.
- **Output:** top-5 `(name, pagerank)`.
- **Check:** edge multiset + ranked top-5. `EXPECTED` precomputed. **The
  difficulty is the philological parsing, not the graph.**
- **Pitfalls / [open]:** PN normalization, broken/partial addresses (many tablets
  are fragmentary), rounding and tie-break for the ranking.
- **Stretch (⭐⭐⭐):** betweenness-centrality brokers + community detection via
  `networkx.greedy_modularity_communities` (no extra dependency) → report
  modularity. Deterministic by fixing the algorithm.

### S3c — Quantify two divination traditions  ⭐⭐
- **Lives in:** `3c_divination_trees.ipynb`
- **Difficulty:** recursion / algorithm
- **Input:** all six omen trees — Ugaritic `sheep`, `lunar`, `dream`; Babylonian
  `izbu`, `foetus`, `celestial`.
- **Task:** recursively compute, per tree, **max depth, leaf count, internal-node
  count, mean branching factor** (leaves = apodosis strings; internal = dicts).
- **Output:** a table keyed by tree → the four metrics.
- **Check:** per-tree numbers exact. Deterministic.
- **Stretch (⭐⭐⭐) — tree-edit distance:** Zhang–Shasha distance between the
  Ugaritic `sheep`-birth and Babylonian `izbu` trees — put a number on "the same
  logic, two cultures." Reference implementation provided or `pip install zss`;
  grade within tolerance. **[open]:** dependency-free reference vs. `zss`.
- **Variant (⭐⭐) — pipeline agreement:** **Cohen's κ** between the pass-1 keyword
  labels and pass-2 LLM refinement. Align all **175 records by corpus + ordinal**,
  never by outcome text (repeated outcomes are not unique IDs). Output κ plus the
  confusion matrix; explain why dependent stages are not independent annotators.

---

## 5. Boss level — query the graph yourself  ⭐⭐⭐ **[settled as optional]**
- **Lives in:** Hour-3 toolkit segment / `docs/hour3-mcp-demo.md`; bridges the
  "watch AI build a research tool" finale.
- **Difficulty:** data at the layer the Parquet loader **cannot** reach.
- **Task:** the bundled loader has no sign-level annotation. Using the
  ContextFabric **MCP** (or Text-Fabric `use("DT-UCPH/cuc")`), compute the
  **per-tablet emendation rate** from the sign features `emen` and `cert`, and
  return the top-N most-restored tablets.
- **Output:** top-N `(tablet, % emended signs)`.
- **Check:** graded against the **MCP** (not the loader — see §3 source rule);
  `EXPECTED` precomputed by the presenter.
- **Message for the room:** the same corpus, asked a deeper question, through an
  agent — *you could commission this yourself.*

---

## 6. Open questions for the build phase **[open]**

1. **Shared helper or fully inline?** Add `star_check()` + `star_answers.json`, or
   inline each `EXPECTED` constant per cell (more self-contained, more clutter)?
2. **⭐⭐⭐ grading:** exact match, or pass/threshold against a target score?
3. **Determinism details** to lock: kNN `k`, permutation seed/N, KMeans
   `random_state`, S3a tie-break, S3b name-normalization rules.
4. **Hints:** ship a collapsed hint per task (Rosalind gives none; a workshop
   probably should)?
5. **Pointers:** when building, add a one-line "⭐ optional" note to `README.md`
   and `SPEC.md` so presenters know the track exists.

## 7. Coverage check **[settled]**

One starred task per workshop section, every hour represented:

| Notebook | Star task | Tier | Difficulty source |
|----------|-----------|------|-------------------|
| 1b | Re-implement the tokenizer (+ KTU gap map) | ⭐⭐ / ⭐ | data |
| 1b | Significance test (+ blind cryptanalysis) | ⭐⭐ / ⭐⭐⭐ | statistics / linguistics |
| 2 | TF-IDF from scratch (+ keyness G²) | ⭐⭐ | algorithm |
| 2 | Genre map, measured (kNN / ARI) | ⭐⭐ | ML evaluation |
| 3a | Longest shared formula (+ frame–slot) | ⭐⭐ / ⭐⭐⭐ | algorithm |
| 3b | Address parser → network | ⭐⭐ / ⭐⭐⭐ | linguistics + graph |
| 3c | Tree metrics (+ edit distance / κ) | ⭐⭐ / ⭐⭐⭐ | recursion |
| Hour 3 | Boss level — graph emendation rates | ⭐⭐⭐ | data (MCP) |

---

## 8. Round 2 — author's additions **[draft]**

Four more, from the author. Verdicts after a data check against the bundled files
and the MCP. Same input → output → check → tier format.

### S-MAP — Measure spatial clustering across the tell  ⭐⭐
- **Lives in:** `1a_corpora_and_data.ipynb` (extends its implemented public-layer
  find-spot map from visual exploration to a measured spatial question).
- **Difficulty:** spatial statistics + a messy RS-number join.
- **Data reality [settled]:** `UGARIT_TEXTS_DATABASE.csv` has named areas but no
  coordinates. Notebook 1a now joins it to the public ArcGIS-derived
  `ugarit_find_spots.csv` (4,757 geolocated finds) and site-plan GeoJSON via RS IDs.
- **Task:** quantify whether one predeclared language or genre contrast is more
  spatially clustered than a label-permutation baseline. Choose and document a
  distance statistic before looking at the result.
- **Output (gradable):** observed statistic, 1,000-permutation null distribution,
  and p-value.
- **Check:** deterministic seed and tolerance against a reference implementation.
- **Payoff:** turns an attractive map into a falsifiable claim about scribal and
  archival geography.

### S-SHAPE — Cluster tablets by shape  ⭐⭐
- **Lives in:** `2_similarity_clustering.ipynb` (a deliberate foil to S2b: cluster
  by *what tablets look like*, not *what they say*).
- **Difficulty:** data (parsing) + clustering.
- **Input:** `Size` column of `UGARIT_TEXTS_DATABASE.csv` — physical dimensions in
  mm, `"W x H"` or `"W x H x thickness"`, 4,028 distinct, messy (`?`, ranges,
  blanks). Join to genre via `KTU3`.
- **Task:** parse `Size` → `(width, height, thickness, aspect_ratio)`; cluster
  (KMeans / DBSCAN) and interpret (e.g. small near-square economic tags vs. tall
  multi-column literary tablets); cross-tabulate clusters against genre.
- **Output:** cluster labels + `(n_clusters, silhouette)` or ARI-vs-genre.
- **Check:** numeric within tolerance; `KMeans(random_state=0)` for determinism.
- **Variant (⭐⭐) — layout shape:** instead of physical mm, use corpus-native
  format features — #columns, #lines (1–447, median 17), signs/line, signs/tablet
  — and cluster. Ties tightly to genre (a 1-column 6-line letter vs. a 4-column
  myth).
- **Stretch (⭐⭐⭐) — image shape:** from tablet photographs (`images/`, full set via
  InscriptiFact/USC), segment the outline and cluster on shape descriptors (Hu
  moments, aspect ratio). Heavy CV; take-home.

### S-COG — Hebrew cognate generator from sound correspondences  ⭐⭐⭐
- **Lives in:** Hour-1 language segment (`docs/03-alphabet-and-language.md` / a cell
  in `1b`) **and** bridges directly to the Hour-3 MCP demo (Ugaritic ↔ Hebrew).
- **Difficulty:** linguistics (the headline comparative-Semitics task).
- **Premise:** Ugaritic preserves Proto-Semitic consonants that Hebrew **merged**.
  The regular correspondences (Ugaritic → Hebrew):

  | Ugaritic | → Hebrew | example |
  |----------|----------|---------|
  | ṯ (𐎘) | š (שׁ) | ṯlṯ → šlš "three"; ṯr → šôr "bull" |
  | ḏ (𐎏) | z (ז) | ḏhb → zhb "gold" |
  | ḫ (𐎃) | ḥ (ח) | ḫmš → ḥmš "five" |
  | ġ (𐎙) | ʿ (ע) | ġrb → ʿrb "evening/west" |
  | ẓ (𐎑) | ṣ (צ) | ẓhr → ṣhr "noon" |
  | ṣ / ḍ | ṣ (צ) | arṣ → ʾrṣ "earth" |
  | ʾa/ʾi/ʾu | ʾ (א) | all three alephs merge |
  | (b g d h w z ḥ ṭ y k l m n s ʿ p q r t š) | 1 : 1 | bʿl → bʿl, mlk → mlk |

- **Task:** apply the rules to Ugaritic consonantal forms → predicted Hebrew
  consonant skeleton (emit in ETCBC ASCII to match BHSA), then **validate against
  attested BHSA lexemes** (`lex` / `g_cons` via the MCP).
- **Output:** per form, predicted Hebrew skeleton + whether it is an attested lexeme.
- **Check:** on a curated gold set (~20 secure cognates: bʿl, arṣ, ṯlṯ, ḏhb, ḫmš,
  šmm, yd, mlk, bn, ym, bt, ṯr, ʿbd …), predicted == attested Hebrew; score =
  matches / total ≥ threshold. `EXPECTED` = the gold pairs (BHSA lookups done at build).
- **Pitfalls / teaching points:** not every Ugaritic word has a cognate; vowels
  aren't written; exclude metathesis/irregulars from the gold set; the ṯ→š, ḏ→z,
  ġ→ʿ, ḫ→ḥ merges are the "aha." Mention the subtle ś: Ug š can also → Heb ś
  (šd → śādeh "field") — keep it out of the graded set.

### S-LUA — Ugaritic inflection module for Wiktionary (Lua)  ⭐⭐⭐
- **Lives in:** Hour-3 toolkit / **take-home** (`docs/08-modern-toolkit.md`). The
  human-written complement to "LLM morphological parsing of CUC."
- **Difficulty:** software engineering + morphology. The most "real contribution"
  task — output could become an actual Wiktionary module.
- **Reference:** the Hebrew inflection modules
  (`en.wiktionary.org/wiki/Category:Hebrew_inflection_modules`, e.g. `Module:he-noun`,
  `Module:he-verb`) — model the Scribunto Lua structure (`export.show`, parameter
  tables) on those. BHSA's morphology features (`nu`, `gn`, `st`, `vs`, `vt`,
  `pfm`, `vbe`, `nme`, `prs`) show the exact feature set a paradigm engine encodes.
- **Linguistics:** Ugaritic **nouns** — three cases (nom **-u**, gen **-i**, acc
  **-a** in the singular), numbers (sg / dual **-ā/-ē + -ma** / plural masc
  **-ū/-ī + -ma**, fem **-āt-**), construct vs. absolute. **Verbs** — G-stem prefix
  & suffix conjugations, derived stems (D, Š, N).
- **Task:** write a Lua module that, given a root/lemma + class, generates the full
  paradigm table the way the Hebrew modules do.
- **Output:** the generated paradigm (table of inflected forms).
- **Check:** **predefined expected forms** — e.g. noun *malku* "king" → nom sg
  *malku*, gen *malki*, acc *malka*, … ; a sample G-stem verb → its prefix/suffix
  paradigm. Module output strings == `EXPECTED`. Run with a `lua` interpreter if
  available; otherwise grade the produced table (language-agnostic) so Python
  solvers can attempt it too.
- **Caveat [settled]:** Ugaritic vocalisation is partly **reconstructed** — restrict
  the graded paradigm to securely reconstructable forms. (This caveat is itself a
  teaching point about the limits of the data.)

### Round-2 coverage

| Task | Lives in | Tier | Difficulty source | Auto-gradable? |
|------|----------|------|-------------------|----------------|
| S-MAP | 1a | ⭐⭐ | data + geo-viz | aggregation yes, map no |
| S-SHAPE | 2b | ⭐⭐ (→⭐⭐⭐) | data + clustering | yes |
| S-COG | 1b ↔ Hour-3 MCP | ⭐⭐⭐ | linguistics | yes (via BHSA) |
| S-LUA | Hour-3 / take-home | ⭐⭐⭐ | engineering + morphology | yes (expected forms) |

> **Note:** S-MAP and S-LUA each have a non-auto-gradable artifact (a map; a Lua
> module). For those, grade a **derived value** (the area→count table; the paradigm
> strings) so the Rosalind-style check still holds.
