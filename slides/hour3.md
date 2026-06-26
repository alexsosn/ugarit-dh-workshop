---
marp: true
theme: default
paginate: true
title: "Ugarit & Digital Humanities — Hour 3"
---

<!--
DRAFT deck — co-build. Hour 3 budget (60 min):
formulas 10 (→3a) · networks 10 (→3b) · divination 10 (→3c) ·
modern toolkit + AI-build demo 20 · get-involved 10.
The AI-build demo follows docs/hour3-agent-runbook.md. Notebook cues marked ▶.
-->

# Ugarit & Digital Humanities
## Hour 3 — From texts to structures

Formulas, social networks, decision trees — and AI as a builder.

<!-- 1 min. We move from counting words to recovering structure. -->

---

## Ancient texts are full of formulas

![bg right:40%](../images/baal_stele_louvre_ao15775.jpeg)

- Myth: fixed epithets — *aliyn bʿl* "Mighty Baal", *rkb ʿrpt* "Rider on the Clouds".
- Letters: *tḥm X · l Y rgm* (address), *yšlm lk* (greeting).
- Ritual & admin: repeated instructions and templates.

<!-- 3 min. Figure: Baal stele (Louvre AO 15775). Formulas = repeated n-grams. -->

---

## ▶ Hands-on 3a — find formulas with n-grams

**Notebook:** `3a_ngrams_formulas`

- Count repeated 2- and 3-word clusters across the corpus.
- Real results pop out: **kṯr w ḫss** (the god Kothar-wa-Hasis),
  **rbt aṯrt ym** ("Lady Athirat of the Sea"), **yšu gh w yṣḥ** ("he lifted his voice and cried").

<!-- 9 min including slide. The machine surfaces genuine epithets/formulas from raw text. -->

---

## Letters as social data

- A letter records a relationship: **sender → recipient**, plus mentioned people and places.
- Beyond reading one letter, study the **network** of correspondents.

<!-- 3 min. docs/06. The address formula is structured data hiding in plain sight. -->

---

## ▶ Hands-on 3b — the correspondence network

**Notebook:** `3b_letter_networks`

- Parse *tḥm X / l Y* into **sender → recipient** edges (~40 from the letters).
- Build and draw the graph; find central figures (*mlk* the king, *umy* "my lady").
- Caveat: titles ≠ unique persons; broken tablets bias the graph.

<!-- 9 min including slide. -->

---

## Divination = ancient algorithms

- Omens follow a strict pattern: **observed sign → interpretation → outcome**.
- That's an **if → then** tree — a data structure, three millennia early.

<!-- 3 min. docs/07. The birth-omen series (KTU 1.103) as our case. -->

---

## ▶ Hands-on 3c — the omen decision tree

**Notebook:** `3c_divination_trees`

- A real birth-omen text → a nested JSON tree → a drawn decision tree (~98 nodes).
- Sets up the AI question: *can a model extract this structure for us?*

<!-- 9 min including slide. Bridge straight into the LLM block. -->

---

## LLMs: helpful and dangerous

- **Help:** extract structure, validate JSON, compare trees, explain in plain language.
- **Danger:** invent missing branches (`[…]` gaps), smooth over ambiguity, drop philology.
- The philologist doesn't disappear — they move **up a level**: asking and checking.

<!-- 3 min. The honest core of the AI message. -->

---

## The modern toolkit — the whole picture

> corpus **+** dictionary **+** images **+** bibliography **+** morphology
> **+** Python **+** ContextFabric **+** LLM / agents **+** **human validation**

Each piece you saw today is one layer of a real research stack.

<!-- 2 min. docs/08. Pull the three hours together into one architecture. -->

---

## DEMO — watch AI build a research tool

**A PDF is not data. Watch us make it data.** *(see hour3-agent-runbook.md)*

- A coding agent turns a participant-supplied **UDB** PDF → a local,
  queryable **SQLite**.
- Then we **ask it research questions** in plain language.
- Free tool, local workflow: *you could repeat the method on a source you are
  authorized to process.*

<!-- 10 min. Screen-share the agent (Antigravity free tier). Recording ready as fallback. -->

---

## The catch

- Ask it something the tablet leaves broken — it answers **confidently anyway**.
- Check against the actual text: invented certainty, lost brackets.
- **That catch is the actual skill.** Direct the AI; verify like a scholar.

<!-- 2 min. The caution beat — do not cut this. -->

---

## Get involved & keep learning

- **Contribute:** report errors, help annotate CUC, build a small tool.
- **Stay in touch:** group chat + my inbox *(details on the handout)*.
- **Learn Ugaritic:** UCU · Helsinki · Polis · Huehnergard's grammar.

→ `docs/09-get-involved.md`

<!-- 8 min incl. Q&A. The networking goal. Make the ask concrete: pick one step this week. -->

---

# Thank you

You ran real analyses, built a tool with AI, and learned where it needs *you*.

**The field is more open than it looked this morning.**

— 〔your name / contact〕

<!-- Close warm. Leave contact + chat link on screen during Q&A. -->
