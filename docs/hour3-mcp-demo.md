# Hour 3 — "One agent, two libraries" · MCP demo runbook

> Presenter-only. The companion to `hour3-agent-runbook.md`. That one shows an
> agent *building* a tool from a PDF; **this one shows an agent *reaching into two
> live corpora at once*** — the Ugaritic **CUC** (via ContextFabric MCP) and the
> Jewish-text library **Sefaria** (via the Sefaria MCP) — and bridging them.

---

## 0. TL;DR

In ~6–8 minutes you ask one AI agent a comparative question that **no single
database can answer**, and watch it query the Ugaritic **CUC**, the Hebrew-Bible
**BHSA** corpus, and the **Sefaria** library on its own, then lay the results side
by side **with citations**. It makes Hour 1's claim — *Ugarit is the backdrop to
the biblical world* — literally interactive.

**Message:** *"The agent did the plumbing between two unrelated libraries. You
supplied the question and the judgement. That's the new division of labour."*

> **What is an MCP?** A **Model Context Protocol** server is a standard "adaptor
> cable" that lets an AI assistant talk directly to an outside data source — here,
> a corpus engine and a text library — instead of you copy-pasting. (See
> `glossary.md`.)

---

## 1. What you're connecting

| Piece | Type | What it gives the agent |
|-------|------|-------------------------|
| **ContextFabric MCP** (`cfabric-mcp`) | **Local** server you run | Live query access to **CUC** (Ugaritic) **and BHSA** (Hebrew Bible) — one server can serve several corpora: search, retrieve passages, inspect features. |
| **Sefaria Texts MCP** | **Hosted** (`https://mcp.sefaria.org/sse`) | Search/retrieve Tanakh, Talmud, commentaries **with precise citations**. |
| **The agent** | Claude Desktop / Claude Code / Cursor / ChatGPT | Plans the steps, calls all servers, synthesises an answer. |

Serving **BHSA** alongside CUC means the agent can also check the **Hebrew lexeme**
itself (e.g. `MLK/` "king", `ʾšrh` Asherah) — not just the Ugaritic form and a
translation. CUC ↔ BHSA ↔ Sefaria is the full Ugaritic → Hebrew → tradition chain.

**ContextFabric MCP tools** (the agent picks these itself): `list_corpora`,
`describe_corpus`, `list_features`, `describe_feature`, `search`,
`search_syntax_guide`, `get_passages`, `get_node_features`, `search_csv`,
`search_continue`, `get_text_formats`.

> ⚠️ **Paid account required.** Connecting *any* MCP needs a **paid Claude or
> ChatGPT** plan. This is a **presenter demo**, consistent with the rest of Hour 3.

---

## 2. Setup (do this at T‑1 week, then again T‑1 day)

### Fastest path — the tested demo folder
A tested setup lives in **`~/projects/mcp-demo/`** (sibling of this repo). It
creates the environment, fetches CUC + BHSA, writes the launcher + client configs,
and self-verifies all three corpora through MCP calls:
```bash
cd ~/projects/mcp-demo
./setup.sh        # ends with "ALL THREE INTERROGABLE"
./run-mcp.sh      # start the local CUC+BHSA server
```
Then connect your client (configs are generated in `mcp-demo/clients/`). The rest
of this section is the manual version / what that script does.

### a. Install the ContextFabric MCP server
> **Python version (the gotcha):** use **Python 3.13**. The direct
> `cfabric-mcp` package requires Python `>=3.13`; Python 3.12 fails dependency
> resolution.
```bash
uv venv --python 3.13 .venv
uv pip install cfabric-mcp "mcp[cli]" httpx anyio
cfabric-mcp --help        # confirm it installed
```

### b. Fetch the corpora (current method = git clone)
Context-Fabric's HuggingFace downloader is still on the roadmap, so clone the
Text-Fabric repos directly:
```bash
git clone --depth 1 https://github.com/DT-UCPH/cuc.git   corpora/cuc
git clone --depth 1 https://github.com/ETCBC/bhsa.git    corpora/bhsa   # large!
```
Each corpus's data is the directory that contains `otype.tf` (find it with
`find corpora -name otype.tf`). The tested paths are:
```text
corpora/cuc/tf/0.2.7
corpora/bhsa/tf/4b
```

Why BHSA `4b`? `tf/2021` is much larger and was too slow for a live setup check.
`tf/4b` has the features needed for the demo (`lex`, `g_word_utf8`, section
features) and completed its first ContextFabric cache build in about five minutes.
After the `.cfm` cache exists, the combined CUC+BHSA server loaded in under ten
seconds.

### c. Run the server with BOTH corpora
```bash
cfabric-mcp \
  --corpus cuc=corpora/cuc/tf/0.2.7 \
  --corpus bhsa=corpora/bhsa/tf/4b \
  --features "g_cons g_word_utf8 lex book chapter verse language line tablet"
```
First run builds `.cfm` caches inside the TF directories; later starts are fast.

### d. Connect the servers in your client (pick ONE client)

> The `mcp-demo` setup writes ready configs with your absolute paths into
> `mcp-demo/clients/` — prefer those over hand-typing the paths below.

**Claude Code (simplest for a live terminal demo):**
```bash
# local server, both corpora (stdio)
claude mcp add cuc-bhsa -- /ABS/PATH/.venv/bin/cfabric-mcp \
  --corpus cuc=/ABS/PATH/corpora/cuc/tf/0.2.7 \
  --corpus bhsa=/ABS/PATH/corpora/bhsa/tf/4b \
  --features "g_cons g_word_utf8 lex book chapter verse language line tablet"
# hosted Sefaria texts server (SSE)
claude mcp add --transport sse sefaria https://mcp.sefaria.org/sse
claude mcp list            # confirm both are connected
```
*(Or just run `mcp-demo/clients/claude_code_setup.generated.sh`.)*

**Claude Desktop:**
- CUC + BHSA: merge `mcp-demo/clients/claude_desktop_config.generated.json` into
  `claude_desktop_config.json` (Settings → Developer → Edit Config). It defines one
  `cuc-bhsa` server with both `--corpus` paths.
- Sefaria: Settings → **Connectors** → **Add custom connector** → URL
  `https://mcp.sefaria.org/sse` → enable. Restart the app.

**ChatGPT:** Settings → enable **Developer Mode** → Apps & Connectors → **Create** →
add the Sefaria SSE URL. For the local CUC+BHSA server, use the OpenAI MCP setup
flow for local tools and point it at `./run-mcp.sh` / the generated config.

> Verify in the client that **all** servers show as connected before you present.

### e. Verified smoke checks
These passed locally from `~/projects/mcp-demo/`:
```bash
./.venv/bin/python verify.py
./.venv/bin/python check_cfabric.py
./.venv/bin/python check_sefaria.py
```

Observed results:
- ContextFabric exposed `cuc` and `bhsa` from one local server.
- CUC query `word g_cons=aṯrt` returned 63 hits, starting at `KTU 1.3 I:15`.
- BHSA query `word lex=>CRH/` returned 40 hits, starting at `Exodus 34:13`.
- Sefaria Texts MCP listed tools including `get_text`, `text_search`, and
  `search_in_book`, and retrieved `Genesis 1:1` and `Deuteronomy 16:21`.

---

## 3. The demo storyboard (~6–8 min)

Pick **one** research bridge (options in §5). Worked example: **Athirat → Asherah.**

| Beat | You say / do | What the agent does | Narrate |
|------|--------------|--------------------|---------|
| 1. Show the reach | "What corpora and tools can you see?" | `list_corpora`, lists Sefaria tools | *"It can see a 3,000-year-old Ugaritic corpus and the whole Jewish library."* |
| 2. Ugaritic side | Ask it to find the goddess **Athirat** in CUC | `search` for `aṯrt` / `rbt aṯrt ym`, `get_passages` → KTU refs | *"Real hits, real tablet references."* |
| 3. Biblical side | Ask for **Asherah** in the Hebrew Bible | Sefaria search/retrieve → verses **with citations** | *"Now the other library, with exact citations."* |
| 4. The bridge | "Put them side by side: what's parallel, what's different?" | Synthesises both, cites both | *"One question, two corpora, one answer."* |
| 5. The catch | Push it to *equate* them / read a broken line | (watch for overreach) | *"Here's where the philologist steps in."* |

Beat 5 is the point: the agent will tend to **flatten** Athirat (Ugaritic consort
of El) into Asherah (biblical) as if identical. Correct it on screen — cognate and
related, **not** the same figure across a millennium. Same human-in-the-loop lesson
as the omen demo.

---

## 4. Exact prompts (copy-paste)

```
1) What text corpora and tools do you currently have access to? List them and,
   for the Ugaritic one, describe its structure (objects and a few features).

2) In the Ugaritic corpus (CUC), find occurrences of the goddess Athirat —
   search the word form "aṯrt" and the epithet "rbt aṯrt ym" ("Lady Athirat of
   the Sea"). Show the matching lines with their KTU references. If you need the
   query syntax, consult the corpus's search-syntax guide first.

3) Now in the Hebrew Bible corpus (BHSA), find the Asherah lexeme `>CRH/`
   (`word lex=>CRH/`) and report how many times it occurs and in which books.

4) Now use Sefaria: pull a few of those Asherah passages as readable verses WITH
   precise citations.

5) Put all three together: the Ugaritic Athirat material (CUC), the Hebrew lexeme
   counts (BHSA), and the cited verses (Sefaria). What is genuinely parallel, and
   what is different? Cite each source.

6) A skeptic says "Athirat just is Asherah." Argue both for and against, and be
   explicit about what the texts do NOT let us conclude.
```

> Keep these in a plain `.txt` on the demo machine; paste, don't retype.

---

## 5. Alternative bridges (pick by your audience)

- **Lotan → Leviathan.** Ugaritic *ltn*, the twisting seven-headed serpent slain by
  Baal/Anat (KTU 1.5 I) ↔ biblical **Leviathan** (Isaiah 27:1, Psalm 74:14, Job).
  Great visual payoff.
- **"Rider on the clouds."** Ugaritic *rkb ʿrpt*, Baal's epithet ↔ Psalm 68:5
  ("rider in the heavens / on the clouds"). A tight phrase-level parallel.
- **El the father-god.** Ugaritic *il* ↔ biblical **El / Elohim** names.
- **Death personified.** Ugaritic **Mot** (*mt*, "Death") ↔ death imagery in
  Hosea 13:14, Isaiah 25:8.

Each is one swap in prompt 2–3. Rehearse whichever you choose.

---

## 6. Fallback plan (assume something breaks)

1. **Recording.** Pre-record a clean run; narrate over it. (Required, not optional.)
2. **Sefaria-only.** The hosted server is the more reliable half. If local
   `cfabric-mcp` won't start, do the biblical search live and show **pre-captured**
   CUC results from your rehearsal.
3. **Screenshots.** 4–5 captures: tool list → CUC hits → Sefaria citations →
   side-by-side → the correction.

Never debug the local server live for more than ~60 seconds — cut to fallback.

---

## 7. Risks & mitigations

| Risk | Mitigation |
|------|-----------|
| MCP needs a paid plan | Presenter-only; say so; audience reproduces with free tools later. |
| Local `cfabric-mcp` path/corpus issues | Rehearse the exact `--corpus` path; keep the Sefaria-only fallback. |
| Agent guesses CUC query syntax wrong | Prompt tells it to call `search_syntax_guide` first. |
| Network / Sefaria rate limits | Recording fallback; keep prompts few and pointed. |
| Agent over-equates Athirat = Asherah | **That's the teaching beat** — lean in and correct it. |
| Cuneiform won't render on projector | Latin transliteration is the fallback display. |

---

## 8. Data use & licences

- **CUC**: CC BY-NC 4.0 — educational/non-commercial, attribution.
- **BHSA**: ETCBC, CC BY-NC-SA 4.0 — attribute the ETCBC; share-alike.
- **Sefaria**: most texts are openly licensed, but terms vary by text/translation —
  see Sefaria's *Copyright and Data Use* page before redistributing anything you
  capture. For a live, non-redistributed demo you're fine.

---

## 9. Why this belongs at the end

It instantiates the architecture from `08-modern-toolkit.md`: **corpus +
dictionary + LLM/agent + human validation**, now *across* corpora. It also closes
the loop opened in Hour 1 (Ugarit as biblical backdrop) — not as a claim on a
slide, but as something the room watched an agent assemble, and a philologist
correct, in real time.

*Companion docs: `hour3-agent-runbook.md` (the PDF→SQLite build),
`08-modern-toolkit.md` (the architecture), `00-resources.md` (tools & corpora),
`glossary.md` (MCP, agent, LLM defined).*

---

### Source notes
- Local verification, 2026-06-17: `~/projects/mcp-demo/verify.py` confirmed one
  local `cfabric-mcp` serving CUC `tf/0.2.7` and BHSA `tf/4b`, plus Sefaria Texts
  MCP over SSE.
- ContextFabric MCP setup & tool list: context-fabric.ai/docs/mcp/guides/server-setup.
- Sefaria MCPs (Texts MCP `https://mcp.sefaria.org/sse`; paid-account requirement):
  developers.sefaria.org/docs/the-sefaria-mcp.
