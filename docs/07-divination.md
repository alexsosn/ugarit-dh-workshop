# 7. Divination and the classification of signs

*Hour 3 · ~5 min reading + leads into notebook `3c` (~10 min)*

> **Status:** outline stub.

## Divination as conditional structure
Divination texts typically follow an **"if … then …"** pattern:

> **observed sign → interpretation → prognosis (favorable / unfavorable).**

(See the birth-omen text KTU 1.103 in the sample data: *k tld att w … → mlk …*.)

## Ancient algorithms
These conditional series can be modeled as **classification schemes** or
**decision trees** — a clean example of an ancient intellectual practice
translating into a formal data structure.

## Formalization (notebook `3c`)
Extract: observed sign · its value/variant · consequence · polarity. Encode as
JSON, then visualize as a tree:

```json
{
  "text_id": "KTU 1.103",
  "type": "divination",
  "nodes": [
    {"condition": "observed_sign", "value": "...", "outcome": "...", "polarity": "favorable"}
  ]
}
```

## Where LLMs help — and where they are dangerous
- **Help:** extract structure, validate JSON, compare two trees, generate explanations.
- **Danger:** **invent** missing elements, **smooth over** ambiguity, **lose**
  philological detail.

> **Central idea:** this is the boundary between philology, data modeling, and
> LLM tooling — keep the human in the loop.

## TODO
- [ ] Pick the exact omen text(s) to model live.
- [ ] Add a rendered decision-tree figure.
