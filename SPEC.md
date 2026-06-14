# Workshop Spec — *Ugarit & Digital Humanities*

> Living specification. Built iteratively from the author's answers. Sections are
> marked **[settled]**, **[draft]**, or **[open]**. Last updated via interview
> round 1.

---

## 1. Purpose & end goals **[settled]**

The workshop is **not** primarily about skill transfer or product marketing. Its
real goals, in priority order:

1. **Reduce fear / build confidence.** Show humanities scholars they can *understand
   and use* digital methods themselves — especially **with AI and agents** as
   accessible helpers, not gatekept expert tools.
2. **Spark interest in Ugarit** — the city, the language, and its literature.
3. **Make connections** — meet participants, find collaborators and future contacts.

**Design consequence:** every exercise should be low-friction, quick to a visible
result, and produce a small "wow". Depth and rigor are secondary to momentum and
encouragement. Avoid anything that makes a non-coder feel stuck.

## 2. Audience **[settled]**

- Antiquity Studies Summer School participants: **mostly non-coders**, humanities
  background (philology, history, religion, ANE studies).
- Likely **no paid LLM subscriptions** (ChatGPT Plus / Claude Pro).
- Variable hardware; will mostly use the cloud.

## 3. Success criteria **[draft — confirm]**

A successful session means participants:
- run real analyses on a real ancient corpus themselves and see it "just work";
- leave curious about Ugarit and unafraid of code + AI;
- know how to continue (links, contacts, a way to stay in touch).

*(Networking outcome — see open question on call-to-action.)*

## 4. Scope **[settled]**

- **In scope:** the workshop repo only — `docs/` readings, `notebooks/`, the
  CUC/HuggingFace loader in `data/`, `images/`, `slides/`.
- **Out of scope (referenced, not built here):** UgaritLab (`dulat`), `ugaritic-nb`,
  the `omens` project, CUC packaging. These are *shown/credited* as "where this
  goes next", not specified or modified.

## 5. Delivery model **[settled]**

- **Hours 1–2:** hands-on — participants run notebooks themselves in Colab.
- **Hour 3 (LLM / agents):** **demo-led** (presenter), since participants likely
  lack paid LLM subscriptions. Provide a watch-along path + free take-home options.

### Headline demo to polish hardest **[settled]**
**The genre map (notebook 2b)** — the corpus clustering itself into genres on a
2-D map, i.e. "the machine discovering what philologists already know." This is the
moment participants should remember.

- **Build:** **interactive UMAP** (Plotly) — scatter of tablets, coloured by genre,
  **hover a point to read that tablet's text/ref**. Goal: *more interactive than
  UgaritLab's current version* (which serves precomputed static projections).
- `umap-learn` installs fine in Colab; keep a PCA fallback so the cell never fails.

### Hour-3 LLM/agents content **[settled — presenter demos]**
1. **UgaritGPT live** — presenter drives the custom GPT (e.g. structure-extraction
   from an omen, corpus questions).
2. **Agent + corpus (MCP)** — an agent using ContextFabric / Sefaria MCP, or a
   coding agent writing a DH snippet live.
3. **PDF → structured UDB** — ChatGPT-based transformation of PDF sources into a
   structured data format to build a UDB-style corpus (the real UgaritLab pipeline).
4. **LLM morphological parsing of CUC** — using an LLM to add the POS/lemma layer
   that CUC 0.1.x lacks. Ties directly to `docs/08-modern-toolkit.md`.

**Through-line [settled]:** *"Watch AI build a research tool."* Presenter
screen-shares a **coding agent** that turns a **public UDB PDF → queryable SQLite**
and stands up a **custom GPT front-end** to ask statistical questions of it. The
message for non-coders: *you could commission this yourself — you don't have to
write the code.* Ends on the caution beat (hallucination / lost philology).

**Agent tool [settled — with caveat]:** feature **Google Antigravity (free tier)**
— no credit card, ~20 agent requests/day (plenty for one rehearsed demo), strong
"zero-cost" story. Mention **OpenAI Codex, Cursor, Claude Code** as alternatives.
⚠️ Free tiers shifted repeatedly through 2025–26, so **record a screen capture of
the full build in advance** as a fallback if limits/network fail live.

**Mechanics [settled]:** screen-share of the web UI / IDE, **not** notebook API
calls (audience has no paid subs). Notebook code for H3 is minimal; the artifact is
the live build + the resulting custom GPT.

### Presentation / rendering **[settled]**
- **Ugaritic is Unicode** and renders fine everywhere — **no font bundling needed.**
- Use **interactive Plotly** for the headline 2b (and where it clearly helps);
  matplotlib is fine elsewhere.

### Call to action — "get involved & keep learning" **[settled]**
Final slide + a repo page (`docs/09-get-involved.md`) covering:
- **Contribute to the corpus** (CUC / UDB annotation & extension).
- **Contact the author directly** (email/handle in repo + slide).
- **Star/follow on GitHub** (workshop repo + CUC / UgaritLab).
- **Join a group chat** (link TBD).
- **Where to learn Ugaritic:** UCU, **Helsinki University**, **Polis**
  (polisjerusalem.org/language/ugaritic/), + a curated **self-study** resource list
  (author to supply; overlaps `docs/00-resources.md`).

## 6. Execution environments **[settled — multi-target]**

Target all three, in priority order:
1. **Google Colab** — primary. **Bootstrap: first cell `!git clone` the public
   GitHub repo, then `%cd` into it.** The first notebook call to `load_texts()`
   downloads CUC JSONL from HuggingFace into a local cache; no API key required.
2. **Binder** — launch the whole repo in-browser from GitHub.
3. **Local venv** — `pip install -r requirements.txt` for power users.

- **Hosting:** public GitHub — **`github.com/alexsosn/ugarit-dh-workshop`**.
  Colab/Binder badges point here; bootstrap cell clones this URL.
- **Design consequence:** every notebook starts with a Colab-safe bootstrap cell
  (clone if needed, no-op locally); data access is identical across all three.

### Hands-on style **[settled]**
H1–H2 notebooks end with a small **"your turn"** challenge cell (e.g. change the
KTU number or target word and re-run) plus a hint — engagement without risk of
anyone getting stuck.

### Slides **[settled — co-build]**
`slides/` is built **iteratively together**: I draft structure/outline and figures
from `docs/`; we refine the deck in passes. Not a hand-off either way.

### H3 UDB source & licence **[settled]**
The agent demo converts ***The Texts of the Ugaritic Data Bank***, produced by the
Spanish UDB team (Cunchillos, Vita, and Zamora 2003). UDB was formerly accessible
online and is now sold as an Accordance Bible Software package; PDFs of the UDB
texts and concordance are listed on Juan-Pablo Vita's Academia page
(`https://csic.academia.edu/JuanPabloVita`). **Redistribution-safe model:** each
person who builds the tool **downloads the PDF themselves and converts it to
SQLite themselves**; the workshop repo ships **only the instructions + the agent
prompt**, **never** the PDF or the resulting database.

## 6a. Timeline **[settled]**

- **Workshop date: 17 July 2026** (~5 weeks from spec date 11 Jun 2026).
- **Build target:** dry-run-ready by **early July** to leave rehearsal slack —
  critical for the H3 live agent demo + screen-capture fallback.
- **Priority order under the deadline:** (1) hands-on H1–H2 notebooks + Colab
  bootstrap; (2) headline interactive 2b; (3) get-involved materials; (4) H3 live
  build rehearsal + fallback recording.

---

## 7. Open items (content only — no design decisions left)

All design questions resolved across rounds 1–5. Remaining items are **content the
author will supply**, not blockers to building:

- [ ] Group-chat invite link, public contact handle/email, and the self-study
      Ugaritic resource list → for `docs/09-get-involved.md`.
- [ ] Spoken language of delivery (materials stay English regardless).
- [ ] Author to confirm the exact agent prompt wording for the H3 build (I'll draft).

---

## 8. Decision log

| Round | Decision |
|-------|----------|
| 1 | Scope = workshop only. |
| 1 | Goal = inspire/de-mystify + spark Ugarit interest + networking (not skills/marketing). |
| 1 | Engagement = hands-on H1–H2; H3 LLM more demo (no paid subs). |
| 1 | Environments = Colab (primary) + Binder + local venv. |
| 2 | Colab bootstrap = `!git clone` public repo. Hosting = public personal account. |
| 2 | Headline = genre map (2b); polish hardest. |
| 2 | H3 = presenter demos: UgaritGPT, agent+MCP, PDF→UDB, LLM morph-tagging of CUC. |
| 3 | 2b = interactive UMAP + hover, beating UgaritLab's static version. |
| 3 | No font work — Ugaritic Unicode renders fine; use Plotly where it helps. |
| 3 | CTA = contribute / contact / GitHub / group chat + "where to learn Ugaritic". |
| 4 | H3 spine = "watch AI build a research tool" (coding agent: UDB PDF→SQLite→custom GPT). |
| 4 | Agent tool = Antigravity free tier; alternatives mentioned; record fallback capture. |
| 4 | Repo = github.com/alexsosn/ugarit-dh-workshop. |
| 4 | Workshop date = 17 Jul 2026; dry-run-ready by early July. |
| 5 | H1–H2 get "your turn" challenge cells. |
| 5 | Slides co-built iteratively (not a hand-off). |
| 5 | H3 source = UDB PDF/concordance via Juan-Pablo Vita's Academia page; self-download + self-convert, no redistribution. |
