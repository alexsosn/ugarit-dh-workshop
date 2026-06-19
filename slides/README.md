# Slides

Three decks, one per hour, as **Marp** Markdown:

- `hour1.md` — Ugarit, corpora-as-data, the alphabet hypothesis.
- `hour2.md` — genres, TF-IDF keywords, the **genre map** (the headline).
- `hour3.md` — formulas, networks, divination, the AI-build demo, get-involved.

> **Status: first drafts to co-refine.** Structure, figures, timings and speaker
> notes are in place; we tighten wording, swap images, and adjust pacing together.

## How they're built

- Plain Markdown with Marp directives. Slides are separated by `---`.
- **Speaker notes** are HTML comments (`<!-- ... -->`) — visible in Marp's presenter
  view, hidden on the slide.
- **Figures** reference real files in `../images/` (already credited in
  `images/README.md`). `![bg right:40%](...)` places an image on the right.
- Each hands-on slide is marked **▶** and names the notebook to open in Colab.
- Per-hour timing budgets are noted at the top of each file.

## Render to PDF / PPTX / HTML

Using the Marp CLI (no global install needed):

```bash
npx @marp-team/marp-cli@latest slides/hour1.md -o slides/hour1.pdf
npx @marp-team/marp-cli@latest slides/hour2.md -o slides/hour2.html
npx @marp-team/marp-cli@latest slides/hour3.md -o slides/hour3.pptx
```

Or, in VS Code, install the **Marp for VS Code** extension and use the preview /
export buttons. (The decks also read fine as plain outlines if you skip Marp.)

## To do together

- Replace the title/section images where you have stronger ones.
- Decide whether to **reveal** the alphabet-hypothesis result on a slide (Hour 1)
  or keep it a live discovery in the notebook.
- Fill the contact / chat-link placeholder on the final Hour 3 slide
  (mirrors `docs/09-get-involved.md`).
