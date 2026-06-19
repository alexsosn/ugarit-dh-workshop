# 7. Divination and the classification of signs

*Hour 3 · ~5 min reading + leads into notebook `3c` (~10 min)*

> **Status:** outline stub.

> **New term?** *decision tree, JSON, LLM* and other computational terms are
> unpacked in plain language in [glossary.md](glossary.md).

## Divination as conditional structure
Divination texts typically follow an **"if … then …"** pattern:

> **observed sign → interpretation → prognosis (favorable / unfavorable).**

(See the Ugaritic animal birth-omen text **RS 24.247+** = KTU 1.103+1.145 in the sample
data, e.g. *if the newborn has no left thigh → the king will [strike] his enemy*.)

## Ancient algorithms
These conditional series can be modeled as **classification schemes** or
**decision trees** — a clean example of an ancient intellectual practice
translating into a formal data structure.

## The Ugaritic divination manuals

Ugarit left a small but remarkable set of **divination manuals**, edited and translated by
Dennis Pardee (*Ritual and Cult at Ugarit*, 2002) — the texts we model in notebook `3c`.
Four genres survive, each a Western, alphabetic-cuneiform counterpart of a great Mesopotamian
omen series:

| Pardee | RS / RIH (KTU) | Ugaritic genre | Mesopotamian counterpart |
|--------|----------------|----------------|--------------------------|
| **42** | RS 24.247+ (KTU 1.103+1.145) | malformed **animal** fetuses | *Šumma izbu* |
| **43** | RS 24.302 (KTU 1.140) | malformed **human** fetuses | *Šumma sinništu* |
| **44** | RIH 78/14 (KTU 1.163) | **lunar** omens | *Sin* / *Enūma Anu Enlil* |
| **45** | RS 18.041 | **dream** omens (oneiromancy) | dream omens |

Pardee highlights what makes this corpus distinctive:

- **Genuinely Western, not a translation.** The language is almost pure Ugaritic, with very few
  Akkadian or Hittite loanwords, so the tradition is probably *old* — perhaps reaching back to
  the Amorite world of the early second millennium. Ugarit did not invent ominology (that is
  Mesopotamian), yet its texts correspond to **no** known Mesopotamian or Anatolian tablet.
- **It reads as "reasoned."** Where Mesopotamian compendia pile up repeated phenomena (a calf
  with five legs might get two different readings), the Ugaritic texts give **one omen per
  phenomenon** — more a *brief overview of the main possibilities* than an exhaustive list,
  "a reasoned structure rather than a random collection."
- **Overtly "scientific" in form.** They are classed as "science" for their observational form
  ("if such-and-such is observed, such-and-such will follow") and their kinship with **medical**
  diagnostic texts. The knowledge is mantic — not science in the modern sense — *"but for the
  ancients the data were as valid and useful as those in a modern scientific handbook"* (Pardee).

> **Two tablets, not one.** Our sample data bundles the **animal** birth-omens (RS 24.247+) and
> the **lunar** omens (RIH 78/14) together for convenience, but they are *different tablets* —
> notebook `3c` draws them as separate trees. The **human** birth-omens (RS 24.302) and **dream**
> omens (RS 18.041) are too fragmentary to model, but they complete the picture: Ugarit, like
> Babylon, told animal from human teratomancy and read the sky and dreams besides.

## The Mesopotamian background
Ugarit did not invent ominology. The genre's home was Mesopotamia, **one of the largest and most
prestigious bodies of scholarship in the cuneiform world.** Babylonian and Assyrian scholars
compiled huge canonical **omen series**, each pairing an observed sign (the
**protasis**, "if …") with its outcome (the **apodosis**, "then …"). The principal
disciplines included:

- **extispicy** (Babylonian *bārûtu*) — reading the entrails, above all the liver
  and gall-bladder of a sacrificed sheep; the most prestigious technique, used by the
  royal court to sanction decisions of state;
- ***Šumma izbu*** — **teratomancy**: omens from anomalous human and animal births
  ("if a ewe / woman gives birth to …"), the same genre as the Ugaritic *animal* birth-omen
  tablet **RS 24.247+** (KTU 1.103+1.145);
- ***Enūma Anu Enlil*** — celestial / astral omens (eclipses, planets, weather);
- ***Šumma ālu*** — terrestrial omens (the city, houses, animal behaviour, augury).

George also distinguishes **provoked** divination, where the diviner ritually puts a
question to the gods (extispicy; *omina impetrativa*), from **unprovoked** signs that
simply occur and must be decoded (eclipses, births; *omina oblativa*). All of it was
studied in **Akkadian cuneiform**, the international language of Late Bronze Age
scholarship; Ugarit knew this scholarly world — but, as **Pardee** stresses, the Ugaritic omen tablets
are an **independent, Western** development of the shared genre, corresponding to *no* known
Mesopotamian tablet, not copies of Babylonian literature (see *The Ugaritic divination
manuals* above).

> **"Science" — with a caveat worth teaching.** The omen lists *are* a systematic
> intellectual achievement: A. R. George calls them "the outcome of cumulative
> attempts to embrace the entire universe in a system of reciprocal inferences," a
> Babylonian counterpart to a universal "theory of everything." But recent
> scholarship has shown the omens were **not** compiled from real observation —
> diviners generated new entries by rule (analogy, wordplay, symbolism), and the
> series even include **impossible portents** such as "the sun sighted at midnight."
> The *format* is rigorously systematic; the *content* is speculative, not empirical.
> A clean companion to the source-criticism caution about Philo in
> [`01-ugarit-history.md`](01-ugarit-history.md).

> **DH payoff:** because the Babylonian and Ugaritic versions share the
> rigid **protasis → apodosis** ("if → then") structure, the *same* decision-tree
> model fits both. Notebook
> [`3c_divination_trees.ipynb`](../notebooks/3c_divination_trees.ipynb) builds the
> comparison live: the Ugaritic sheep-birth tree beside the Babylonian
> *miscarried-foetus* omens (George no. 12 — the closest parallel) and the vivid human
> *Šumma izbu* Tablet I (no. 35), then the Babylonian lunar-eclipse calendar beside
> Ugarit's handful of sky omens. The "ancient algorithm" point lands hardest with
> parent and offshoot side by side.

*Authoritative edition:* A. R. George, *Babylonian Divinatory Texts Chiefly in the
Schøyen Collection*, CUSAS 18 (Bethesda, MD: CDL Press, 2013) — Old Babylonian
extispicy and omen compendia. The workshop's Babylonian omen data is drawn from it:
**no. 12** (miscarried-foetus teratomancy), **nos. 13–14** (lunar-eclipse omens), and
**no. 35** (*Šumma izbu* Tablet I, human birth omens).

*Ugaritic texts & translations:* Dennis Pardee, *Ritual and Cult at Ugarit*, Writings from the
Ancient World 10 (Atlanta: Society of Biblical Literature, 2002), ch. VI ("Divination"),
texts **42–45** — the source of every Ugaritic omen translation used in this workshop.

## Formalization (notebook `3c`)
Extract: observed sign · its value/variant · consequence · polarity. Encode as
JSON, then visualize as a tree:

```json
{
  "text_id": "RS 24.247+",
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
