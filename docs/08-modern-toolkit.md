# The modern philologist's toolkit and the future of DH

*Hour 3 · ≈20 min*

You have now used a real ancient corpus as data: you counted forms, compared
texts, searched for formulae, and built networks. This final section asks what
would make that work stronger, and how new AI tools fit into a philological
workflow without replacing philology.

The short answer is:

> better data **+** better tools **+** human judgment.

## From word forms to morphology

So far, many of our searches have worked with **word forms**: the exact written
shape found in the transliteration. That is useful, but it is limited.

A richer corpus links each word form to information such as:

| Layer | Question it answers |
|-------|---------------------|
| **word form** | What is written here? |
| **lemma** | Which dictionary headword does this belong to? |
| **part of speech** | Is it a noun, verb, particle, name, and so on? |
| **morphology** | What person, number, gender, stem, case, or state is involved? |
| **certainty** | Is the reading secure, damaged, restored, or debated? |

This is called **morphological tagging**. A tagged word is not just a string of
letters; it is a small scholarly claim about what the word is and how it works.

That matters because ancient texts are full of hard cases:

- one written form may belong to more than one lemma;
- a broken tablet may preserve only part of a word;
- an editor may restore missing signs;
- two scholars may prefer different readings;
- a name, noun, or verb may look identical until context decides it.

Good tagging does not remove those problems. It records them clearly enough that
other people, and other tools, can test the analysis.

## Why tagging improves digital analysis

Morphology makes almost every method from the workshop more precise.

With only word forms, a search can tell you where the same spelling occurs. With
lemmas and morphology, you can ask better questions:

- Which texts use the same **verb**, even when the form changes?
- Are two passages similar because they share real vocabulary, or only common
  particles?
- Do ritual texts and letters use the same nouns in different grammatical
  patterns?
- Which formulae repeat exactly, and which repeat with small substitutions?
- How does Ugaritic compare with another Semitic corpus, such as the Hebrew
  Bible, when both corpora have comparable annotation?

In practical terms, better morphology improves **TF-IDF**, **similarity search**,
**clustering**, **formula detection**, **network analysis**, and comparison with
other annotated corpora such as BHSA or the Dead Sea Scrolls.

## The full toolkit

A modern digital philology project is not one tool. It is an ecosystem:

> corpus **+** dictionary **+** images **+** bibliography **+** morphological
> tagging **+** Python **+** ContextFabric **+** LLM / coding agents **+**
> human validation.

Each part does a different job.

- The **corpus** gives you the searchable text.
- The **dictionary** helps connect forms to meanings and lemmas.
- **Images** keep the transliteration accountable to the tablet.
- The **bibliography** records previous scholarship.
- **Morphological tagging** turns text into structured philological data.
- **Python** lets you ask repeatable questions at scale.
- **ContextFabric** stores corpus data as a graph of tablets, lines, words,
  signs, and features.
- **LLMs and agents** can help write code, connect resources, and prototype
  tools.
- **Human validation** decides whether the result is philologically credible.

The last item is not decorative. It is what makes the rest useful.

## LLMs and agents

An **LLM** (large language model) is a text-generating AI system such as ChatGPT,
Claude, or Gemini. It predicts and produces language. That makes it useful for
summarizing, drafting code, explaining errors, and transforming messy text into
structured formats.

An **agent** is an LLM that can take steps toward a goal: read files, run code,
inspect results, revise its work, and try again. In a DH project, an agent might
help build a small search tool, test a notebook, or connect a corpus to a
dictionary.

These tools are powerful, but they are not authorities.

### What they are good at

- extracting structure from semi-regular text;
- writing and debugging small pieces of code;
- building quick prototypes;
- translating a research question into a first-pass data workflow;
- checking whether a table, script, or notebook behaves as expected.

### Where they fail

- they can invent facts, references, or readings;
- they often sound confident when uncertain;
- they may flatten philological nuance;
- they may miss the difference between a secure reading, a restoration, and a
  conjecture;
- they do not know the tablet unless you give them reliable data.

Use AI as a collaborator for speed and structure, not as a substitute for
checking the text.

## MCP: connecting tools without copy-paste

An **MCP** (Model Context Protocol) is a standard way for an AI assistant to
connect to an outside corpus or tool. Instead of copying data into a chat window,
an agent can query a resource directly.

In this workshop context, that means an agent can be connected to resources such
as:

- CUC through ContextFabric;
- BHSA or another annotated Semitic corpus;
- Sefaria through its hosted Texts MCP;
- local notebooks, scripts, and small DH prototypes.

The important idea is not the acronym. The important idea is that future research
tools will increasingly connect corpora, dictionaries, images, bibliography, and
AI assistants into one working environment.

## What to take away

Digital Humanities is not "letting the computer read for us." It is using
structured data to make our questions sharper:

- What repeats?
- What changes?
- Which patterns are visible only at corpus scale?
- Which apparent patterns disappear once we check the text?
- Where does the machine help us see, and where does the philologist need to
  correct it?

For Ugaritic, the next big step is not just more impressive AI. It is better
annotation: lemmas, morphology, uncertain readings, links to images, and links to
scholarship. That is work students can understand, test, and contribute to.

## Further reading

- Franco Moretti, *Distant Reading* (London: Verso, 2013) — the manifesto for
  reading a literary corpus at scale rather than one text at a time; the
  intellectual backdrop to this workshop.
