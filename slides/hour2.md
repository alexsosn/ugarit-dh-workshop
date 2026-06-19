---
marp: true
theme: default
paginate: true
title: "Ugarit & Digital Humanities — Hour 2"
---

<!--
DRAFT deck — co-build. Hour 2 budget (60 min):
genres 10 · TF-IDF keywords 20 (→2a) · the genre map 25 (→2b, HEADLINE) · discussion 5.
2b is the moment to land. Figures in ../images/. Notebook cues marked ▶.
-->

# Ugarit & Digital Humanities
## Hour 2 — From words to genres

Can a machine *see* the genres without being told them?

<!-- 1 min. Today's headline question. Keep it suspenseful. -->

---

## The genres of Ugaritic texts

![bg right:38%](../images/0000215274_OG.JPG)

- **Myth / epic** — Baal, Kirta, Aqhat (KTU 1.x)
- **Ritual** — sacrifices, calendars, liturgies
- **Divination** — omens, conditional "if → then"
- **Letters** (KTU 2.x) · **Legal / economic** (KTU 3–4) · **Lexical** (KTU 5)

<!-- 3 min. The map of genres. KTU's first digit already encodes a coarse genre. -->

---

## The KTU numbering already hints at genre

- **1** literary & religious · **2** letters · **3** legal · **4** economic · **5** scribal
- A useful prior — but is genre also visible in the **words themselves**?

**Central question:** how much genre can we recover from vocabulary alone?

<!-- 2 min. Sets up the whole hour: vocabulary vs the official label. -->

---

## Distinctive words: the TF-IDF idea

- Common words (*and*, *to*, *the*) are everywhere — they don't *characterise* a text.
- **TF-IDF** rewards words frequent **in one tablet** but rare **across the corpus**.
- Result: each tablet's *signature* vocabulary.

<!-- 3 min. Intuition only, no math. "Which words are surprisingly common here?" -->

---

## ▶ Hands-on 2a — keywords & guess-the-genre

**Notebook:** `2a_tfidf_keywords`

- Compute TF-IDF keywords per tablet.
- **Game:** read the keywords, guess the genre, then check.
- Caveat: CUC has **no lemmas** — word *forms* only; homographs blur the signal.

<!-- 17 min including this slide. Make the guessing interactive with the room. -->

---

## From keywords to a map

- Turn each tablet into a **vector** of its vocabulary.
- Similar vocabulary → near in "vocabulary space".
- Squash to 2-D so we can **see** it.

<!-- 2 min. Bridge to the headline. Each dot will be a tablet. -->

---

## ▶ Hands-on 2b — the genre map ⭐

**Notebook:** `2b_similarity_clustering` — **today's headline**

- Interactive **UMAP** scatter — **hover any point to read that tablet**.
- Coloured by the *known* genre.
- **The question:** do the colours land in separate regions on their own?

<!-- 20 min including this slide. This is THE moment. Run it live, hover a few tablets, let them gasp.
BACKUP: screenshot the rendered map in advance (save to ../images/genre_map.png) in case the live run fails. -->

---

## The reveal

- Letters cluster with letters; myths pull away from rituals — **mostly unsupervised**.
- Then `KMeans` groups them **blind** and we cross-tab against real genres.
- The machine **rediscovers** much of what philologists already know.

<!-- 2 min. The payoff. Emphasise: nobody told it the genres. -->

---

## Where machine and scholars disagree

- Ritual ↔ divination blur (shared cultic vocabulary).
- Short / damaged tablets drift.
- **Disagreements are interesting** — they point to real questions, not just errors.

<!-- 2 min. Intellectual honesty + a hook for further research. -->

---

## Recap — Hour 2

- Vocabulary alone carries a lot of **genre signal**.
- TF-IDF → vectors → a map that *means* something.
- The machine agrees with philologists — and its disagreements are leads.

**Next:** from words to **structures** — formulas, networks, decision trees. → Hour 3.

<!-- 1 min. Bridge to Hour 3. -->
