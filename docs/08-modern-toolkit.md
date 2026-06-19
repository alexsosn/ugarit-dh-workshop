# 8. The modern philologist's toolkit and the future of DH

*Hour 3 · ~20 min · closing synthesis*

> **Status:** outline stub.

> **New term?** *morphological tagging, TF-IDF, MCP, LLM, agent, embedding* and
> other computational terms are unpacked in plain language in
> [glossary.md](glossary.md).

## Morphological tagging in CUC
Show a **tagged word**: the link between word-form, lemma, part of speech, and
morphological features. Discuss the hard cases: **homonymy, lacunae,
reconstructions, variant readings**.

## How tagging improves every earlier exercise
Better morphology → better **TF-IDF**, **similarity**, **clustering**,
**formula search**, **network analysis**, and **comparison with other Semitic
corpora** (BHSA, DSS, …).

## The full architecture
> corpus **+** dictionary **+** images **+** bibliography **+** morphological
> tagging **+** Python **+** ContextFabric **+** LLM / coding agents **+**
> **human validation**.

## LLMs and agents — promise and limits

*An **LLM** (large language model) is a text-generating AI such as ChatGPT, Claude,
or Gemini; an **agent** is an LLM allowed to take steps — read files, write and run
code, check results — to reach a goal.*

- **Promise:** structure extraction, code generation/checking, glue between
  corpora and dictionaries, rapid DH prototypes.
- **Limits:** hallucination, false confidence, loss of philological nuance —
  hence human validation is non-negotiable.

## Reserve topics (if time remains)

*An **MCP** (Model Context Protocol) is a standard "plug" that lets an AI assistant
connect directly to an outside corpus or tool — so an agent can query CUC, a
dictionary, or Sefaria without copy-paste.*

- Sefaria MCP + ContextFabric MCP (`cfabric-mcp`) — **a ready live demo:** one
  agent queries CUC and BHSA through a local ContextFabric MCP, then Sefaria
  through its hosted Texts MCP. Tested setup: `~/projects/mcp-demo/`; full
  runbook: `hour3-mcp-demo.md`.
- Coding agents for generating and checking code.
- Automatic preparation of small DH prototypes.

## Further reading
- Franco Moretti, *Distant Reading* (London: Verso, 2013) — the manifesto for reading a
  literary corpus at scale rather than one text at a time; the intellectual backdrop to
  this whole workshop.

## TODO
- [ ] Add a real tagged-word screenshot from CUC.
- [ ] Draw the architecture diagram.
- [ ] Final slide: takeaways + links to all resources.
