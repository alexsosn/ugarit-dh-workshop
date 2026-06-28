"""Build a personal-name (PN) gazetteer from the CUC Ugaritic lexicon.

Reads the lexicon (tab-separated; part-of-speech in column 4) and writes the
*bare, normalized* transliteration forms of every entry tagged ``PN`` to
``data/ugaritic_pn.txt`` — one form per line, no glosses, DULAT references, or
etymologies. The list is used by ``data/udb_loader.load_pn_gazetteer`` to
recognise personal names in letters.

Normalization / expansion:
  * ayin variants (ʕ U+0295, ˤ U+02E4) -> ʿ (U+02BF), matching CUC/UDB tokens;
  * ``a/b`` marks a one-character alternative -> both forms are emitted;
  * ``(x)`` marks an optional element -> with and without are emitted;
  * homograph markers like ``(II)`` are dropped; roots and damaged/uncertain
    forms (``ʔ``, ``?``, ``[`` ``]``, ``x``, ``…``) are skipped.

Source: CUC lexicon (cuc-origin/lexicon_and_grammar/ugaritic_lexicon.txt),
column 1 ("our representation of the lexeme"). Provide it with --lexicon.

Usage:
    python -m workshop_tools.build_pn_gazetteer --lexicon /path/to/ugaritic_lexicon.txt
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_AYIN = str.maketrans({"ʕ": "ʿ", "ˤ": "ʿ"})
_DAMAGED = set("?[]x…⸢⸣*")


def _expand_slashes(form: str) -> list[str]:
    i = form.find("/")
    if i <= 0 or i >= len(form) - 1:
        return [form.replace("/", "")]
    pre, a, b, suf = form[: i - 1], form[i - 1], form[i + 1], form[i + 2 :]
    out: list[str] = []
    for branch in (pre + a + suf, pre + b + suf):
        out += _expand_slashes(branch)
    return out


def _expand_optionals(form: str) -> list[str]:
    m = re.search(r"\(([^)]*)\)", form)
    if not m:
        return [form]
    inner = m.group(1)
    if re.fullmatch(r"[IVXLC]+", inner):  # homograph number -> drop
        return _expand_optionals((form[: m.start()] + form[m.end() :]).strip())
    with_ = form[: m.start()] + inner + form[m.end() :]
    without = form[: m.start()] + form[m.end() :]
    return _expand_optionals(with_) + _expand_optionals(without)


def pn_forms(lexicon_path: Path) -> set[str]:
    forms: set[str] = set()
    for line in lexicon_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or "\t" not in line:
            continue
        cols = line.split("\t")
        if len(cols) < 4:
            continue
        lexeme, pos = cols[0].strip(), cols[3].strip()
        if "PN" not in pos or not lexeme or "ʔ" in lexeme or lexeme.startswith("/"):
            continue
        for opt in _expand_optionals(lexeme):
            for form in _expand_slashes(opt):
                form = form.translate(_AYIN).strip()
                if len(form) >= 2 and " " not in form and not (_DAMAGED & set(form)):
                    forms.add(form)
    return forms


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lexicon", required=True, help="path to ugaritic_lexicon.txt")
    ap.add_argument("--output", default="data/ugaritic_pn.txt", help="output gazetteer")
    args = ap.parse_args()

    forms = sorted(pn_forms(Path(args.lexicon).expanduser()))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Ugaritic personal-name (PN) gazetteer.\n"
        "# Bare transliteration forms (ayin normalized to ʿ; alternatives and\n"
        "# optional elements expanded) of entries tagged PN in the CUC lexicon\n"
        "# (cuc-origin/lexicon_and_grammar). Glosses, DULAT references, and\n"
        "# etymologies are NOT included. Regenerate with workshop_tools.build_pn_gazetteer.\n"
    )
    out.write_text(header + "\n".join(forms) + "\n", encoding="utf-8")
    print(f"wrote {len(forms)} PN forms -> {out}")


if __name__ == "__main__":
    main()
