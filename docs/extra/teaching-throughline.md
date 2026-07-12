# Teaching through-line — from source to claim and back

*Facilitator guide for the three-hour workshop*

The workshop has one method, repeated at increasing scale:

1. **Locate the source.** What object, photograph, edition, catalogue, or corpus
   does the claim depend on?
2. **Name the representation.** What became a row, token, label, coordinate,
   edge, or branch—and what was left out?
3. **Run a transparent operation.** Count, join, weight, compare, cluster, or
   extract with enough code visible that participants can state what happened.
4. **Validate the result.** Check provenance, a baseline, held-out data, a
   concordance, a sample of extracted records, or the relevant edition.
5. **Return to interpretation.** What historical or philological claim is now
   supported, weakened, or newly worth asking?

Use the same five questions after every visual. This is the bridge between
philology and data science: computation proposes a pattern; source criticism
determines what the pattern can mean.

## The argument across three hours

| Stage | Historical / philological question | Digital move | Validation | Transition |
|---|---|---|---|---|
| `1a` objects | What survived, where was it found, and who described it? | Count metadata; cross-tabulate; join by RS number; map find-spots | Trace every field to its source; inspect missing joins and heuristic labels | Metadata conditions what can be read |
| `1b` signs | Does the surviving writing support an "optimal alphabet" story? | Tokenize; count Unicode signs; correlate frequency with order/complexity | Inspect the complexity measure, sample composition, and effect size | From signs to word-forms |
| `2` genres | How much editorial genre structure is visible in vocabulary? | TF-IDF; similarity; UMAP/PCA; KMeans; classification | ARI, silhouette, held-out accuracy, majority baseline, contested texts | From lexical signal to recurring structures |
| `3a` formulae | Which sequences recur, and are they formulae in context? | n-grams; dispersion; KWIC | Require multiple texts and read every occurrence in line context | Repetition can encode relationships and templates |
| `3b` letters | Which relationships can address formulae recover? | Extract sender/recipient; build a directed network; centrality | Audit edges; resolve names/titles; report coverage and uncertainty | A textual formula becomes a social model |
| `3c` omens | How do omen collections organize conditions and consequences? | Normalize protasis/apodosis; JSON; tree/graph; assisted annotation | Preserve gaps; compare with edition; treat LLM output as a proposal | Structured data can support—but not replace—comparison |
| AI build | Can an agent turn a publication into a usable research tool? | PDF extraction; schema; SQLite; natural-language interface | Gold record, page pointers, constraints, regression tests, human adjudication | A tool is trustworthy only while its evidence remains inspectable |

## Three distinctions to repeat aloud

### Source, edition, dataset

A tablet is not its transliteration, and a transliteration is not a clean token
list. Keep at least these layers verbally distinct:

> archaeological object → image/drawing → reading and restoration → normalized
> transliteration → tokenized/labelled dataset → model output → interpretation

An error or omission at an earlier layer propagates. A polished graph cannot
repair a doubtful sign reading.

### Observation, inference, interpretation

- **Observation:** “This export contains 54 sampled texts labelled `letter`.”
- **Inference:** “Vocabulary predicts the teaching labels above baseline.”
- **Interpretation:** “Address formulae and recurring epistolary vocabulary help
  distinguish letters in this corpus.”

Do not jump from the observation directly to “the machine discovered ancient
genres.” Labels are editorial, the sample is preserved/selected, and genre can
be mixed or disputed.

### Exploration, measurement, confirmation

- A coloured UMAP is **exploration**: it helps participants notice neighbours
  and outliers.
- ARI, silhouette, and held-out accuracy are **measurement**: they quantify
  different questions.
- Reading KTU 1.96, checking a KWIC list, or auditing network edges is
  **confirmation**: it reconnects the model to textual evidence.

No single step substitutes for the others.

## A consistent discussion pattern

After each result, ask one question from each column:

| Read the result | Challenge the representation | Return to the source |
|---|---|---|
| What pattern do you see? | What had to become a number or category? | Which record or line should we inspect first? |
| How large is the effect? | What is missing or unevenly preserved? | Does the edition support the reading? |
| Does it survive a baseline or parameter change? | Is the label observed, inferred, or editorial? | What alternative explanation remains? |

This keeps critique constructive: the goal is not to discredit a method, but to
identify the conditions under which its output becomes evidence.

## Minimum reproducibility standard

Every live result should make these visible or easy to retrieve:

- corpus/export name and licence;
- inclusion rule (for example, tablets with at least 30 tokens);
- normalization/tokenization rule;
- editorial or heuristic origin of labels;
- fixed random seed where an algorithm is stochastic;
- baseline or comparison metric;
- at least one source-level audit trail (KTU/RS reference, line, PDF page, or
  catalogue record).

For the agent demo, add the prompt/model version and preserve the extracted
record beside its PDF page. Do not use a confident natural-language answer as
the only record of a result.

## Closing synthesis

Participants should leave able to complete this sentence:

> “The computer helped me **find or measure** ___; I trust it to the extent that
> ___; to make a historical claim, I still need to check ___.”

That is the shared competence the workshop teaches. Coding is useful, but the
transferable skill is building a traceable argument from source to model and
back.
