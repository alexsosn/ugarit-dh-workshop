# Hour 3 — "Watch AI Build a Research Tool" · Presenter Runbook

> Presenter-only. Not a participant reading. This is the script + checklist +
> copy-paste prompts for the closing live demo of Hour 3: a coding agent turns a
> public **UDB** PDF into a queryable **SQLite** database, then we ask it research
> questions in plain language.

---

## 0. TL;DR

In ~20 minutes you show non-coders that **you can commission a real research tool
without writing code** — you *direct* an AI agent and *check* its work. The artifact
is a small SQLite of the Ugaritic Data Bank, queried in natural language. The lesson
lands twice: AI is an accessible builder **and** a fallible one that needs a human
philologist in the loop.

**Message (say it out loud):** *"You don't have to become a programmer. You have to
learn to ask well and to check."*

---

## 1. Where this sits in Hour 3

Hour 3 runs: 3b letter networks → 3c divination trees → **this closing block
(~20 min)**. By now they've seen analyses *run*; now they see a tool get *built*.

**20-minute storyboard**

| Min | Beat | What's on screen |
|-----|------|------------------|
| 0–2 | Framing | One slide: "A PDF is not data. Watch us make it data." |
| 2–12 | **The build** | Agent IDE: inspect PDF → write parser → produce SQLite → sanity-check. |
| 12–16 | **Ask it questions** | Natural-language questions answered from the SQLite. |
| 16–18 | **The catch** | A wrong/hallucinated answer; how a philologist catches it. |
| 18–20 | CTA | `docs/09-get-involved.md`: how to learn Ugaritic + contribute. |

If time is short, cut the build narration, not the **catch** — the caution beat is
the point.

---

## 2. The tool — Google Antigravity (free), with alternatives

Featured tool: **Google Antigravity**, free tier (no credit card; Gemini-class
agent). Best "zero-cost, anyone-can-try-this" story for the audience.

> ⚠️ **Free-tier limits move.** Antigravity's free daily request count has been cut
> repeatedly (hundreds → ~tens/day). Treat the live build as **rehearsed + recorded**
> (see §8). Don't burn your daily quota the morning of the talk.

| Tool | Why you'd pick it | Note for the talk |
|------|-------------------|-------------------|
| **Google Antigravity** (primary) | Free tier, no card, strong agent | Show this live. |
| OpenAI Codex | If you already pay OpenAI | Mention as alternative. |
| Cursor | Familiar IDE UI for screen-share | Mention; cheapest paid entry. |
| Claude Code | Strong multi-step file+code work | Mention; terminal/IDE. |

Say: *"I'm using the free one on purpose — so you can repeat this tonight."*

---

## 3. The data — UDB PDF (licence guardrails)

Source: **The Texts of the Ugaritic Data Bank** (Academia.edu, item `1442697`):
<https://www.academia.edu/1442697/The_Texts_of_the_Ugaritic_Data_Bank>.

**Redistribution-safe model — do not skip:**

- **Each builder downloads the PDF themselves** from Academia.edu and converts it
  **on their own machine**.
- The workshop repo ships **only this runbook + the prompts** — **never** the PDF
  and **never** the resulting SQLite.
- Say this on screen: *"I'm not handing you the data — I'm handing you the recipe.
  You fetch the source yourself; that keeps everyone on the right side of the
  licence."*

**The realistic snag (use it as a teaching moment):** the UDB PDF uses a **custom
font encoding** — naive text extraction yields glyph soup (`<` = ʿ, `≈` = š, `™` =
ḥ, `∆` = ḫ, `©` = ṯ, `†` = ṭ, `@` = ġ, `ß` = ṣ …). When the agent's first extraction
looks like garbage, **don't hide it** — that's the moment to show the audience that
AI + human notices the problem and fixes it. (This mapping is real; UgaritLab's
`udb_pdf_parser.py` carries the same `FONT2UG` table.)

---

## 4. Target artifact — the SQLite schema

Keep it small and legible on screen. Grounded in UgaritLab's real UDB model
(`udb_models.py`: a tablet has correspondences + an info block + verses; a verse has
per-reader readings and comments).

```sql
-- tablets: one row per UDB tablet
CREATE TABLE tablets (
    udb_id          TEXT PRIMARY KEY,   -- e.g. "1.77"
    ktu_ref         TEXT,               -- cross-reference (KTU/CAT)
    info            TEXT                -- intro / metadata block
);

-- lines: one row per verse-reading (a verse can have several readers)
CREATE TABLE lines (
    id        INTEGER PRIMARY KEY,
    udb_id    TEXT REFERENCES tablets(udb_id),
    ref       TEXT,    -- e.g. "77:2"
    reader    TEXT,    -- reader/editor id
    text      TEXT,    -- normalized transliteration (after font remap)
    comment   TEXT     -- optional editorial note
);
```

Example questions the DB can answer (have these ready):

```sql
-- How many tablets and lines did we extract?
SELECT (SELECT COUNT(*) FROM tablets) AS tablets,
       (SELECT COUNT(*) FROM lines)   AS lines;

-- Longest tablets by line count
SELECT udb_id, COUNT(*) AS n FROM lines GROUP BY udb_id ORDER BY n DESC LIMIT 10;

-- Lines mentioning Baal (bʿl) after normalization
SELECT udb_id, ref, text FROM lines WHERE text LIKE '%bʿl%' LIMIT 20;

-- Where readers disagree (same ref, >1 distinct reading)
SELECT udb_id, ref, COUNT(DISTINCT text) AS variants
FROM lines GROUP BY udb_id, ref HAVING variants > 1 ORDER BY variants DESC;
```

---

## 5. The live build — step by step (with exact prompts)

Run these prompts **in order** in the agent IDE. After each, narrate what it's doing
in one plain sentence (suggested narration in *italics*). Full copy-paste set is in
**Appendix A**.

**Step 1 — orient the agent.**
> *"First I tell it what we have and what we want."*
```
You are helping me build a small research database from a PDF.
The PDF "udb.pdf" (in this folder) is "The Texts of the Ugaritic Data Bank":
transliterated Ugaritic tablets, each headed "UDB <id>" (e.g. UDB 1.77),
with numbered line references (e.g. 77:2) and sometimes editor comments.
Goal: a SQLite file `udb.sqlite` with tables `tablets` and `lines`
(schema below). Work in small steps and show me samples as you go.
[paste the schema from §4]
```

**Step 2 — extract and EXPECT garbage.**
> *"It reads the PDF. Watch — the text looks broken. That's a real problem, not a bug in the AI."*
```
Extract the raw text of the first 3 tablets and show it to me.
Do not clean anything yet — I want to see the raw extraction.
```
When glyph soup appears, say: *"This PDF ships its own font. The letters are there,
just mislabeled. Let's give it the key."*

**Step 3 — hand over the font map.**
```
This PDF uses a custom font. Apply this character mapping to the extracted
text before parsing (these are glyph -> Ugaritic transliteration):
<  ->  ʿ      >  ->  ʾ      ∂ -> ḏ     @ -> ġ     ™ -> ḥ
∆  ->  ḫ      ≈  ->  š      ß -> ṣ     æ -> ś     © -> ṯ
†  ->  ṭ      Ω  ->  ẓ
Re-extract the same 3 tablets and show the cleaned transliteration.
```

**Step 4 — parse into rows.**
```
Now write a parser: split on "UDB <id>" headings into tablets; within each,
capture line references like "77:2" and their transliteration; keep any
editor comment with its line. Output a few parsed rows as JSON for review
before we touch SQLite.
```

**Step 5 — load SQLite + verify.**
```
Create `udb.sqlite` with the two tables, load all tablets, and run these
checks, showing the output:
- counts of tablets and lines
- the 10 tablets with the most lines
- 10 lines containing "bʿl"
```

**Step 6 — natural-language questions (the payoff).**
> *"Now I stop writing SQL and just ask."*
```
Answer these from udb.sqlite (write the SQL yourself, run it, show results):
1. Which tablet has the most lines?
2. How many lines mention "mlk" (king)?
3. Show three places where two readers give different readings of the same line.
```

If you have **ChatGPT Plus** and want the "custom GPT" flavor: upload `udb.sqlite`
to a GPT with Code Interpreter and ask the same three questions. Otherwise the free
agent above already *is* the natural-language query tool — say so.

---

## 6. The caution beat (do not cut)

Ask the agent (or the GPT) a question the data can't truly answer, e.g.:
```
What does tablet UDB 1.77 say about the god Yam, and is the text certain?
```
Then check it against the actual tablet. Point out, on screen, at least one of:

- **invented certainty** — it states a reading the tablet marks as broken/`[…]`;
- **smoothed ambiguity** — it picks one reader and hides the disagreement;
- **lost philology** — it drops brackets/uncertainty the editor encoded.

Land it: *"The tool is real and useful. It is also confidently wrong sometimes. The
philologist doesn't disappear — they move up a level, to asking and checking."*

---

## 7. Pre-flight checklist

**T‑1 week**
- [ ] Install the agent IDE; sign in; confirm the **free tier still works** and note
      today's request limit.
- [ ] Download the UDB PDF from Academia.edu to your demo machine as `udb.pdf`.
- [ ] Do a **full dry run** end-to-end; fix prompts that wander.
- [ ] **Record a screen capture** of the successful run (§8).
- [ ] Build and keep a **prebuilt `udb.sqlite`** locally (do not commit it).

**T‑1 day**
- [ ] Re-test the agent free tier (limits/models can change overnight).
- [ ] Stage the folder: `udb.pdf`, an empty workspace, prompts in a scratch file.
- [ ] Charge laptop; test screen-share + font rendering of cuneiform/ʿʾ diacritics.
- [ ] Queue the fallback recording in a tab.

**T‑5 min**
- [ ] Close other apps / notifications; zoom the editor font for the room.
- [ ] Open prompts scratch file; confirm network.
- [ ] Have `docs/09-get-involved.md` open for the closing CTA.

---

## 8. Fallback plan (assume something breaks)

Priority order if the live build stalls (quota hit, network, agent loop):

1. **Switch to the recording.** Narrate over your pre-recorded successful run. The
   audience can't tell, and the lesson is identical.
2. **Use the prebuilt SQLite.** Skip building; jump to §5 Step 6 (the questions) on
   your local `udb.sqlite`. The payoff (NL questions + the catch) survives.
3. **Screenshots slide.** Last resort: 4–5 captures (raw glyph soup → mapped text →
   schema → a query result) walked through as slides.

Never debug live for more than ~60 seconds — cut to fallback and keep momentum.

---

## 9. Risks & mitigations

| Risk | Mitigation |
|------|-----------|
| Free-tier quota exhausted mid-demo | Don't pre-burn it; recording + prebuilt DB ready. |
| Agent loops / over-engineers | Prompts force *small steps + show samples*; you can paste a known-good parser from your dry run. |
| PDF font glyph soup confuses room | It's scripted as the teaching beat — lean in, then apply the map. |
| Custom-GPT path needs ChatGPT Plus | Default to the free agent as the NL-query tool; GPT is "optional polish". |
| Licence worry | Never ship PDF/SQLite; "recipe not data" line; non-commercial CC BY-NC. |
| Cuneiform won't render on projector | Pre-test fonts; transliteration (Latin) is the fallback display. |

---

## Appendix A — Prompt library (copy-paste)

*(All six prompts from §5, in order, kept verbatim so you can paste from one place.)*

1. Orientation + schema — §5 Step 1
2. Raw extraction (expect garbage) — §5 Step 2
3. Font map + re-extract — §5 Step 3
4. Parser → JSON sample — §5 Step 4
5. Build SQLite + verify — §5 Step 5
6. Natural-language questions — §5 Step 6
7. Caution probe — §6

> Keep these in a plain `.txt` on the demo machine; paste, don't retype.

## Appendix B — Schema DDL + sample SQL

See §4 (the `CREATE TABLE` block and the four example queries). Keep a `.sql` file
with these so you can run them directly if you fall back to the prebuilt DB.

## Appendix C — Talking points for non-coders

- *"A PDF is a picture of data. We're turning the picture back into data."*
- *"I never wrote the parser — I described the goal and checked the result."*
- *"The agent got it wrong once on purpose-ish. Catching that is the actual skill."*
- *"Everything here used a free tool and a public PDF. You can redo it tonight."*
- Bridge to CTA: *"If that felt doable — here's how to actually learn Ugaritic and
  help build these corpora."* → `docs/09-get-involved.md`.

---

*Companion docs: `docs/hour3-mcp-demo.md` (the other Hour-3 agent demo — one agent
querying CUC + Sefaria live via MCP), `docs/00-resources.md` (tools/corpora),
`docs/07-divination.md` and notebook `3c` (the omen-tree LLM beat),
`docs/08-modern-toolkit.md` (the architecture this demo instantiates), `SPEC.md` §5
(Hour-3 design decisions).*
