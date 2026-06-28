from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to sys.path to allow running from anywhere
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ug_nlp.refs import normalize_reference  # noqa: E402

try:
    from parser.pdfminer_parser import PDFMinerParser
except ImportError:
    PDFMinerParser = None
from udb.udb_models import UDBTablet, UDBVerse, write_tablets_to_json  # noqa: E402

FONT2UG: Dict[str, str] = {
    "<": "ʿ",
    ">": "ʾ",
    "∂": "ḏ",
    "@": "ġ",
    "™": "ḥ",
    "∆": "ḫ",
    "≈": "š",
    "‰": "Š",
    "ß": "ṣ",
    "æ": "ś",
    "©": "ṯ",
    "†": "ṭ",
    "Ω": "ẓ",
    "Ω": "ẓ",
    "∑": "⸢",
    "®": "⸣",
    "$": "\u00af",
    "≤": "<",
    "≥": ">",
}
SUBSTITUTIONS = {
    r"a\$": "ā",
    r"e\$": "ē",
    r"i\$": "ī",
    r"o\$": "ō",
    r"u\$": "ū",
    r"a \*\*\$\*\* ": "ā",
    r"e \*\*\$\*\* ": "ē",
    r"i \*\*\$\*\* ": "ī",
    r"o \*\*\$\*\* ": "ō",
    r"u \*\*\$\*\* ": "ū",
}

RE_UDA_HEADING = re.compile(r"UDB\s+(\d+\.\d+)")
ROMAN_COLUMN_RE = r"[IVXLCDM]+[a-z]?"
# Accepts lines like:
#  R1-1. 77: 2 ...
#  10-1. 77:2 ...
#  00-1. 4.309:3 ...
RE_VERSE = re.compile(
    r"^(?P<reader>(?:R\d+|\d{2}|00)-\d)\.?\s+"
    rf"(?P<ref>\d+(?:\.\d+){{0,3}}(?:\s+{ROMAN_COLUMN_RE})?(?::\s*\d+(?:[–-]\d+)?[a-z]?)?)\s*"
    r"(?P<text>.*)$"
)
RE_VERSE_ALT = re.compile(
    r"^(?P<reader>(?:R\d+|\d{2}|00))-(?P<tablet>\d+(?:\.\d+){0,3})"
    rf"(?::(?P<column>{ROMAN_COLUMN_RE}))?\s*:\s*(?P<line>\d+(?:[–-]\d+)?[a-z]?)\s*(?P<text>.*)$"
)
READER_WITH_TABLET_PREFIX = re.compile(r"^(?P<reader>R\d+|\d{2})-\d$")
RE_EDITION_SOURCE_PREFIX = re.compile(
    r"^(?P<label>(?P<reader>R\d+|\d{2})-(?P<section>\d+)\.\s*\d+(?:\.\d+)*)"
    r"(?P<remainder>.*)$"
)
RE_CORR_TOKEN = re.compile(r"\b(CAT|KTU|RS|UT|CTA|TU|DO|PRU)\b", re.I)
RE_INFO_PAGE_MARKER = re.compile(r"^_?-{1,2}\d{1,5}-_?$")
RE_LITERATURE_SCOPE = re.compile(r"^[•·]\s*(.+)$")
RE_LITERATURE_ENTRY = re.compile(r"^-\s*(.+)$")
RE_LITERATURE_YEAR = re.compile(r"\((\d{4}(?:[-/]\d{2,4})?)\)")
RE_AUTHOR_INITIALS = re.compile(
    r"^(?:(?:[A-Z][a-z]{1,2}\.|[A-Z]\.-[A-Z]\.|"
    r"[A-Z]\.|[A-Z]-[A-Z])\s*)+|^[A-Z]\s+"
)
LITERATURE_CATEGORY_PATTERNS = (
    (
        "first_edition",
        re.compile(
            r"\b(?:Editio princeps|publi[ée]\s+pour\s+la\s+premi[èe]re\s+fois)\b",
            re.I,
        ),
    ),
    (
        "preliminary_edition",
        re.compile(r"\b[ÉE]dition pr[ée]liminaire\b", re.I),
    ),
    ("transcription", re.compile(r"\btranscription\b", re.I)),
    ("bibliography", re.compile(r"\bbibliograph(?:ie|y)\b", re.I)),
    ("introduction", re.compile(r"\bintroduction\b", re.I)),
    ("translation", re.compile(r"\b(?:traduction|translation)\b", re.I)),
    ("commentary", re.compile(r"\bcomment(?:aire|ary)\b", re.I)),
    ("notes", re.compile(r"\bnotes?\b", re.I)),
    ("autography", re.compile(r"\bautograph(?:ie|ies|y)\b", re.I)),
    ("photographs", re.compile(r"\b(?:photos?|photographs?)\b", re.I)),
)


class CorrespondenceAccumulator:
    def __init__(self) -> None:
        self._lines: List[str] = []
        self._active = False

    def start(self, line: str) -> None:
        self._active = True
        self._lines.append(line)

    def maybe_append(self, line: str) -> bool:
        if not self._active:
            return False
        norm = line.strip()
        if not norm or not norm.strip("_- ").strip():
            return True
        if self._looks_like_continuation(norm):
            self._lines.append(line)
            return True
        self._active = False
        return False

    def has_value(self) -> bool:
        return bool(self._lines)

    def value(self) -> str:
        return " ".join(ln.strip() for ln in self._lines).strip()

    def _looks_like_continuation(self, norm: str) -> bool:
        cleaned = norm.strip("_- ").strip()
        if cleaned.startswith("="):
            return True
        if RE_CORR_TOKEN.search(cleaned):
            return True
        if re.match(r"^\d+(?:\.\d+)*", cleaned):
            last = self._last_token()
            if last and RE_CORR_TOKEN.fullmatch(last):
                return True
        return False

    def _last_token(self) -> Optional[str]:
        if not self._lines:
            return None
        last_line = self._lines[-1].strip()
        if not last_line:
            return None
        token = last_line.split()[-1].strip().strip("_ *=")
        return token.upper()


def transform_glyphs(text: str) -> str:
    if not text:
        return text
    out = text
    for k, v in SUBSTITUTIONS.items():
        out = re.sub(k, v, out)
    for k, v in FONT2UG.items():
        out = out.replace(k, v)
    out = re.sub(r"(.)#", r"<mark>\1</mark>", out)
    out = out.replace("</mark><mark>", "")
    return out


def normalize_reader_code(reader: str) -> str:
    """Return the scholarly reader code without the PDF's tablet prefix.

    Spaced PDF labels such as ``00-1. 71:2`` and ``R1-4. 106:3`` are parsed by
    :data:`RE_VERSE` as ``00-1`` and ``R1-4``. The final digit belongs to the
    tablet identifier, not to the reader identifier.
    """
    match = READER_WITH_TABLET_PREFIX.fullmatch(reader.strip())
    return match.group("reader") if match else reader.strip()


# Spanish editorial notes the PDF interleaves with readings: "(línea en acadio)"
# (line in Akkadian), "(línea en hurrita)", "(hurrita)", "(R: una línea)",
# "(vacat)", "(R marcas de signos)", "(R)". Genuine reverse-side content such as
# "(R: drt . b . kkr)" carries no such keyword and is preserved.
_EDITORIAL_NOTE_RE = re.compile(
    r"\(\s*(?:"
    r"[^)]*\b(?:l[íi]neas?|acadi[oa]|hurritas?|vacat|marcas|signos?|ilegible)\b[^)]*"
    r"|R\s*:?[\s.\-–—…]*"
    r")\)",
    re.I,
)


def strip_editorial_notes(text: str) -> str:
    """Remove the PDF's Spanish editorial parentheticals from a reading.

    Drops spans such as ``(línea en acadio)``, ``(hurrita)``, ``(R: una línea)``
    and ``(vacat)`` while preserving genuine reverse-side content like
    ``(R: drt . b . kkr)`` (which carries no editorial keyword).
    """
    if not text:
        return text
    return " ".join(_EDITORIAL_NOTE_RE.sub(" ", text).split())


def is_editorial_apparatus(text: str) -> bool:
    """Identify prose line-mapping notes that are not tablet readings."""
    normalized = " ".join((text or "").split()).strip()
    if not normalized:
        return False
    # A reading that is *entirely* an editorial note (e.g. "(línea en acadio)",
    # "(R)") has nothing left once those notes are stripped.
    if not strip_editorial_notes(normalized).strip():
        return True
    return bool(
        normalized.startswith("=")
        or normalized.startswith(",")
        or re.match(r"^-\s*\d+\s*=", normalized)
        or re.match(
            r"^(?:"
            r"(?:has|have|had|does|do|did|it|they)\b.*\bcorrespond"
            r"|does(?:n['’]t|\s+not)\b.*\bexist"
            r"|corresponds?\s+to\b"
            r"|reproduces?\s+the\s+text\b"
            r")",
            normalized,
            re.I,
        )
    )


def _clean_formatting_markers(text: str) -> str:
    """Remove parser-internal italic markers and normalize whitespace."""
    return " ".join((text or "").replace("_", "").split()).strip()


def normalize_comment(text: str) -> str:
    """Remove PDF formatting artifacts while preserving comment content."""
    cleaned = re.sub(
        r"(?<!\S)-{1,2}\d{1,5}-(?!\S)",
        " ",
        text or "",
    )
    cleaned = cleaned.replace("_", "")
    return " ".join(cleaned.split()).strip()


def parse_literature_scope(scope: str | None) -> Dict[str, Optional[str]]:
    """Classify a bibliography scope and split common column/line ranges."""
    if not scope:
        return {
            "scope_type": "tablet",
            "scope": None,
            "column_start": None,
            "column_end": None,
            "line_start": None,
            "line_end": None,
        }

    cleaned = " ".join(scope.split()).strip()
    result: Dict[str, Optional[str]] = {
        "scope_type": "other",
        "scope": cleaned,
        "column_start": None,
        "column_end": None,
        "line_start": None,
        "line_end": None,
    }
    if len(re.findall(r"\d+\.\d+", cleaned)) > 1:
        result["scope_type"] = "tablet_group"
        return result

    reference = cleaned.split("=", 1)[0].strip()
    cross_column_match = re.match(
        r"^(?P<column_start>[IVXLCDM]+)\s*:\s*"
        r"(?P<line_start>\d+\s*[a-z]?)\s*[-–]\s*:?"
        r"(?P<column_end>[IVXLCDM]+)\s*:\s*"
        r"(?P<line_end>\d+\s*[a-z]?)$",
        reference,
        re.I,
    )
    if cross_column_match:
        result.update({
            "scope_type": "line_range",
            "column_start": cross_column_match.group("column_start").upper(),
            "column_end": cross_column_match.group("column_end").upper(),
            "line_start": cross_column_match.group("line_start").replace(" ", ""),
            "line_end": cross_column_match.group("line_end").replace(" ", ""),
        })
        return result

    line_match = re.match(
        r"^(?P<column>[IVXLCDM]+|1)\s*:\s*"
        r"(?P<start>\d+[a-z]?)"
        r"(?:\s*[-–]\s*(?P<end>\d+[a-z]?))?"
        r"(?:\s+(?:ss|ff)\.?)?$",
        reference,
        re.I,
    )
    if line_match:
        column = line_match.group("column").upper()
        result.update({
            "scope_type": "line_range",
            "column_start": "I" if column == "1" else column,
            "line_start": line_match.group("start"),
            "line_end": line_match.group("end"),
        })
        return result

    unqualified_line_match = re.match(
        r"^(?:\d+\.\d+\s*:\s*)?"
        r"(?P<start>\d+\s*[a-z]?)"
        r"(?:\s*[-–]\s*(?P<end>\d+\s*[a-z]?))?"
        r"(?:\s+(?:ss|ff)\.?)?$",
        reference,
        re.I,
    )
    if unqualified_line_match:
        result.update({
            "scope_type": "line_range",
            "line_start": (
                unqualified_line_match.group("start").replace(" ", "")
            ),
            "line_end": (
                unqualified_line_match.group("end").replace(" ", "")
                if unqualified_line_match.group("end")
                else None
            ),
        })
        return result

    column_match = re.match(
        r"^(?P<start>[IVXLCDM]+)"
        r"(?:\s*[-–]\s*(?P<end>[IVXLCDM]+))?$",
        reference,
        re.I,
    )
    if column_match:
        result.update({
            "scope_type": "column_range",
            "column_start": column_match.group("start").upper(),
            "column_end": (
                column_match.group("end").upper()
                if column_match.group("end")
                else None
            ),
        })
    return result


def _looks_like_literature_author(value: str) -> bool:
    cleaned = value.strip()
    cleaned = re.sub(r"^(?:Comte|Count)\s+", "", cleaned, flags=re.I)
    author = re.sub(r"\s+et\s+al\.?$", "", cleaned, flags=re.I).strip()
    match = RE_AUTHOR_INITIALS.match(author)
    if not match:
        return False
    surname = author[match.end():].strip()
    if not surname or re.search(r"[«»\"()]|\b(?:vol|p{1,2})\.", surname, re.I):
        return False
    return (
        not any(character.isdigit() for character in surname)
        and len(surname.split()) <= 8
        and bool(re.search(r"[A-Za-zÀ-ÖØ-öø-ÿŠŽšžʾ]", surname))
    )


def _split_literature_authors(citation: str) -> tuple[List[str], str]:
    parts = citation.split(",")
    authors: List[str] = []
    consumed = 0
    for part in parts:
        candidates = re.split(
            r"\s+-\s+(?=(?:[A-Z][a-z]{1,2}\.|[A-Z](?:\.|-)))",
            part.strip(),
        )
        if not candidates or not all(
            _looks_like_literature_author(candidate)
            for candidate in candidates
        ):
            break
        authors.extend(
            " ".join(candidate.split()).strip()
            for candidate in candidates
        )
        consumed += 1
    remainder = ",".join(parts[consumed:]).strip(" ,")
    return authors, remainder


def _extract_literature_pages(citation: str) -> List[str]:
    pages: List[str] = []

    def append(value: str) -> None:
        normalized = re.sub(r"\s*[-–]\s*", "-", value.strip())
        if normalized and normalized not in pages:
            pages.append(normalized)

    for match in re.finditer(
        r"\bp{1,2}\.?\s*"
        r"(\d+(?:\s*[-–]\s*\d+)?"
        r"(?:\s*,\s*\d+(?:\s*[-–]\s*\d+)?)*)",
        citation,
        re.I,
    ):
        for value in re.split(r"\s*,\s*", match.group(1)):
            append(value)
    for match in re.finditer(
        r"\)\s*,?\s*(\d+\s*[-–]\s*\d+)\s*\(",
        citation,
    ):
        append(match.group(1))
    return pages


def parse_literature_citation(citation: str) -> Dict[str, object]:
    """Split a UDB bibliography item while retaining the complete citation."""
    normalized = " ".join(citation.replace("_", "").split()).strip()
    citation_type = "literature"
    parsing_text = normalized
    prefix_patterns = (
        (
            "first_edition",
            re.compile(r"^Editio princeps[^:]*:\s*", re.I),
        ),
        (
            "preliminary_edition",
            re.compile(r"^[ÉE]dition pr[ée]liminaire[^:]*:\s*", re.I),
        ),
        (
            "first_edition",
            re.compile(
                r"^Publi[ée]\s+pour\s+la\s+premi[èe]re\s+fois\s+dans\s+",
                re.I,
            ),
        ),
        ("photograph", re.compile(r"^Photos?:\s*", re.I)),
        ("cross_reference", re.compile(r"^Voir\s+", re.I)),
    )
    for kind, pattern in prefix_patterns:
        match = pattern.match(parsing_text)
        if match:
            citation_type = kind
            parsing_text = parsing_text[match.end():].strip()
            break
    parsing_text = re.sub(
        r"^(?:Comte|Count)\s+",
        "",
        parsing_text,
        flags=re.I,
    )
    authors, remainder = _split_literature_authors(parsing_text)
    if not authors:
        for opening in ("«", "“", '"'):
            quote_start = remainder.find(opening)
            if quote_start <= 0:
                continue
            possible_author = remainder[:quote_start].strip(" ,")
            if _looks_like_literature_author(possible_author):
                authors = [possible_author]
                remainder = remainder[quote_start:]
            break
    title: Optional[str] = None
    publication = remainder
    publication_place: Optional[str] = None
    publication_is_container = False

    for opening, closing in (("«", "»"), ("“", "”"), ('"', '"')):
        start = remainder.find(opening)
        end = remainder.find(closing, start + len(opening)) if start >= 0 else -1
        if start >= 0 and end > start:
            title = remainder[start + len(opening):end].strip()
            publication = remainder[end + len(closing):].strip(" ,")
            publication_is_container = True
            break

    years = list(dict.fromkeys(RE_LITERATURE_YEAR.findall(normalized)))
    if title is None:
        journal_match = re.match(
            r"^(?P<container>.+?)\s+"
            r"(?P<volume>(?:vol\.\s*)?(?:\d+|[IVXLCDM]+)"
            r"(?:[/.-]\d+)*)\s*"
            r"\(\d{4}(?:[-/]\d{2,4})?\)",
            remainder,
            re.I,
        )
        place_match = re.match(
            r"^(?P<title>.+),\s*"
            r"(?P<publication>[^,.;]{2,60}\s+"
            r"\(\d{4}(?:[-/]\d{2,4})?\).*)$",
            remainder,
        )
        institution_match = re.match(
            r"^(?P<title>.+?)\.\s+"
            r"(?P<publication>.+\(\d{4}(?:[-/]\d{2,4})?\).*)$",
            remainder,
        )
        volume_match = re.match(
            r"^(?P<title>.+?),\s*(?P<publication>vol\..+)$",
            remainder,
            re.I,
        )
        if journal_match:
            publication = remainder
            publication_is_container = True
        elif place_match:
            title = place_match.group("title").strip()
            publication = place_match.group("publication").strip()
            publication_place = re.split(
                r"\(\d{4}(?:[-/]\d{2,4})?\)",
                publication,
                maxsplit=1,
            )[0].strip(" ,")
        elif institution_match:
            title = institution_match.group("title").strip()
            publication = institution_match.group("publication").strip()
        elif volume_match:
            title = volume_match.group("title").strip()
            publication = volume_match.group("publication").strip()
        else:
            page_start = re.search(r"\bp{1,2}\.", remainder, re.I)
            if page_start:
                title = remainder[:page_start.start()].strip(" ,.")
                publication = remainder[page_start.start():].strip()
            elif remainder:
                title = remainder.strip()
                publication = ""

    container_title: Optional[str] = None
    volume_issue: Optional[str] = None
    before_year = re.split(
        r"\(\d{4}(?:[-/]\d{2,4})?\)",
        publication,
        maxsplit=1,
    )[0].strip(" ,")
    container_match = re.match(
        r"^(?P<container>.+?)\s+"
        r"(?P<volume>(?:vol\.\s*)?(?:\d+|[IVXLCDM]+)"
        r"(?:[/.-]\d+)*)$",
        before_year,
        re.I,
    )
    if container_match and publication_is_container:
        container_title = container_match.group("container").strip(" ,")
        volume_issue = container_match.group("volume").strip()
    elif (
        before_year
        and title is not None
        and publication
        and years
        and publication_is_container
    ):
        container_title = before_year

    categories = [
        category
        for category, pattern in LITERATURE_CATEGORY_PATTERNS
        if pattern.search(normalized)
    ]
    return {
        "citation_type": citation_type,
        "authors": authors,
        "title": title or None,
        "container_title": container_title or None,
        "volume_issue": volume_issue or None,
        "publication_place": publication_place or None,
        "publication_details": publication or None,
        "years": years,
        "pages": _extract_literature_pages(normalized),
        "categories": categories,
        "citation": normalized,
    }


def _split_tablet_comment_lines(lines: List[str]) -> List[str]:
    comments: List[str] = []
    current: List[str] = []
    paragraph_start = re.compile(
        r"^(?:[A-Z][A-Z0-9.-]{1,}\b|Number\b|Note\b|The tablet\b|"
        r"Tablet\b|This\b|These\b|According\b|Comments?:\b)"
    )

    def finish() -> None:
        nonlocal current
        comment = normalize_comment(" ".join(current))
        if comment:
            comments.append(comment)
        current = []

    for raw_line in lines:
        line = _clean_formatting_markers(raw_line)
        if not line:
            finish()
            continue
        if (
            current
            and re.search(r"[.!?][\"')\]]?$", current[-1])
            and paragraph_start.match(line)
            and not re.search(
                r"(?:\b[A-Z]\.|\b[A-Z]\.-[A-Z]\.)$",
                current[-1],
            )
        ):
            finish()
        current.append(line)
    finish()
    unique_comments: List[str] = []
    seen: set[str] = set()
    for comment in comments:
        if comment not in seen:
            unique_comments.append(comment)
            seen.add(comment)
    return unique_comments


def extract_literature_and_comments(
    info_lines: List[str],
) -> tuple[List[Dict[str, object]], List[str]]:
    """Extract scoped bibliography entries and trailing tablet-level prose."""
    literature: List[Dict[str, object]] = []
    comment_lines: List[str] = []
    current_scope: Optional[str] = None
    current_citation: List[str] = []
    in_literature = False
    in_comments = False
    bibliography_heading = re.compile(
        r"^bibliogra(?:ph(?:y|ie)|f[ií]a)"
        r"(?:\s+adicional)?\s*:\s*(.*)$",
        re.I,
    )
    comment_start = re.compile(
        r"^(?:The tablet\b|Tablet\b|Number\b|TEO\b|We\b|"
        r"R\d+-\s+corresponds\b|Line\b|Size\b|Data refer\b|"
        r"Collation\b|Pitard\b|In\s+\d|Text\b|Comments?:\b|"
        r"Note\b|Change\b|According\b)",
        re.I,
    )

    def starts_citation(line: str) -> bool:
        if re.match(
            r"^(?:Editio princeps|[ÉE]dition pr[ée]liminaire|"
            r"Publi[ée]\s+pour\s+la\s+premi[èe]re\s+fois|"
            r"Photos?:|Voir\s+)",
            line,
            re.I,
        ):
            return True
        parsing_line = re.sub(
            r"^(?:Comte|Count)\s+",
            "",
            line,
            flags=re.I,
        )
        authors, _ = _split_literature_authors(parsing_line)
        return bool(authors)

    def citation_is_complete(parts: List[str]) -> bool:
        if not parts:
            return False
        citation = " ".join(parts).strip()
        if not re.search(r"[.!?][\"')\]]?$", citation):
            return False
        return bool(
            RE_LITERATURE_YEAR.search(citation)
            or re.search(r"\bp{1,2}\.?\s*\d", citation, re.I)
            or re.search(r"\b(?:fig|pl)\.?\s*[IVXLCDM\d]", citation, re.I)
        )

    def finish_citation() -> None:
        nonlocal current_citation
        if not current_citation:
            return
        citation = normalize_comment(" ".join(current_citation))
        if citation:
            literature.append({
                **parse_literature_scope(current_scope),
                **parse_literature_citation(citation),
            })
        current_citation = []

    for raw_line in info_lines:
        stripped = raw_line.strip()
        if not stripped or stripped.strip("_").strip() == "":
            if not in_literature:
                comment_lines.append("")
            continue
        if RE_INFO_PAGE_MARKER.match(stripped):
            continue
        cleaned = _clean_formatting_markers(raw_line)
        heading_match = bibliography_heading.match(cleaned)
        scope_match = RE_LITERATURE_SCOPE.match(cleaned)
        entry_match = RE_LITERATURE_ENTRY.match(cleaned)
        if heading_match:
            finish_citation()
            in_literature = True
            in_comments = False
            remainder = heading_match.group(1).strip()
            if remainder:
                if starts_citation(remainder):
                    current_citation = [remainder]
                else:
                    comment_lines.append(remainder)
                    in_comments = True
            continue
        if scope_match:
            finish_citation()
            current_scope = scope_match.group(1).strip()
            in_literature = True
            in_comments = False
            continue
        if entry_match:
            finish_citation()
            entry = entry_match.group(1).strip()
            if re.match(r"^N\.?B\.?\s*:", entry, re.I):
                comment_lines.append(entry)
                in_literature = False
                in_comments = True
                continue
            current_citation = [entry]
            in_literature = True
            in_comments = False
            continue
        if not in_comments and starts_citation(cleaned):
            finish_citation()
            current_citation = [cleaned]
            in_literature = True
            continue
        if current_citation and citation_is_complete(current_citation):
            finish_citation()
            comment_lines.append(raw_line)
            in_comments = True
            continue
        if current_citation and (
            not (
                comment_start.match(cleaned)
                and re.search(r"[.!?][\"')\]]?$", current_citation[-1])
            )
        ):
            current_citation.append(cleaned)
            continue

        finish_citation()
        comment_lines.append(raw_line)
        in_comments = True

    finish_citation()
    return literature, _split_tablet_comment_lines(comment_lines)


def parse_edition_source_header(line: str) -> Optional[Dict[str, str]]:
    """Parse an edition citation header without confusing it with a reading."""
    cleaned = _clean_formatting_markers(line)
    match = RE_EDITION_SOURCE_PREFIX.match(cleaned)
    if not match:
        return None

    remainder = match.group("remainder").strip()
    if remainder:
        if not remainder.startswith(":"):
            return None
        remainder = remainder[1:].strip()
        # A numeric or column reference after the colon is an actual reading.
        if re.match(rf"^(?:{ROMAN_COLUMN_RE}\s*:\s*)?\d", remainder) or re.match(
            rf"^{ROMAN_COLUMN_RE}\s*(?::|=)", remainder
        ) or re.match(
            rf"^{ROMAN_COLUMN_RE}\s+(?:do|does|has|have|is|was|were)\b",
            remainder,
            re.I,
        ):
            return None

    label = match.group("label").strip()
    return {
        "reader": normalize_reader_code(
            f"{match.group('reader')}-{match.group('section')}"
        ),
        "source_ref": label,
        "citation": remainder,
    }


def extract_edition_sources(
    info_lines: List[str],
) -> tuple[List[Dict[str, str]], List[str]]:
    """Extract wrapped reader/edition citations from a tablet's info block."""
    sources: List[Dict[str, str]] = []
    cleaned_info: List[str] = []
    current: Optional[Dict[str, str]] = None
    citation_parts: List[str] = []

    def finish_current() -> None:
        nonlocal current, citation_parts
        if current is None:
            return
        citation = " ".join(part for part in citation_parts if part).strip()
        if citation:
            sources.append({**current, "citation": citation})
        current = None
        citation_parts = []

    for raw_line in info_lines:
        source = parse_edition_source_header(raw_line)
        if source is not None:
            finish_current()
            current = {
                "reader": source["reader"],
                "source_ref": source["source_ref"],
            }
            citation_parts = [source["citation"]] if source["citation"] else []
            continue

        stripped = raw_line.strip()
        normalized = _clean_formatting_markers(raw_line)
        if current is None:
            cleaned_info.append(raw_line)
            continue

        if RE_INFO_PAGE_MARKER.match(stripped):
            continue
        if not normalized:
            if stripped and not stripped.strip("_").strip():
                # pdfminer italic spans can leave a marker-only continuation.
                continue
            if citation_parts:
                finish_current()
            continue
        if normalized.lower().startswith("note the following") or is_editorial_apparatus(
            normalized
        ):
            finish_current()
            cleaned_info.append(raw_line)
            continue
        if re.match(r"^(?:R\d+|\d{2})-\s*\(", normalized) or re.match(
            r"^(?:The tablet|Change in|According to)\b", normalized, re.I
        ) or normalized.lower() == "xxx":
            finish_current()
            cleaned_info.append(raw_line)
            continue
        if citation_parts and "_" not in raw_line:
            # Edition citations are typographically marked in the PDF. Plain
            # following paragraphs are explanatory apparatus, not citation text.
            finish_current()
            cleaned_info.append(raw_line)
            continue

        citation_parts.append(normalized)

    finish_current()
    return sources, cleaned_info


def _normalize_heading(line: str) -> Optional[str]:
    # Ignore Table of Contents lines which look like "UDB 1.1 ... 5"
    if "..." in line:
        return None
    m = RE_UDA_HEADING.search(line)
    if not m:
        m = RE_UDA_HEADING.search(strip_combining(line))
    return m.group(1) if m else None


def strip_combining(s: str) -> str:
    return s.replace("\u030a", "")


def parse_correspondences(
    text: str, preferred_base: Optional[str] = None
) -> Dict[str, str]:
    corrs: Dict[str, list[str]] = {}
    if not text:
        return {}

    text = " ".join(text.splitlines())
    # Split by '='
    parts = text.split("=")
    for part in parts:
        token = part.strip().strip("_ *")
        token = " ".join(token.replace("_", " ").split())
        if not token:
            continue

        # Heuristic: The first word is the key (e.g. "KTU", "RIH")
        # The whole token is the value (e.g. "KTU 1.174")

        # Split into Key and Rest
        subparts = token.split(None, 1)
        if not subparts:
            continue

        key = subparts[0].upper()

        # Normalize if needed
        norm = normalize_reference(token)
        value = norm if (norm and norm.split()[0].upper() == key) else token
        corrs.setdefault(key, [])
        if value not in corrs[key]:
            corrs[key].append(value)

    preferred_norm = (
        normalize_reference(preferred_base or "") if preferred_base else None
    )
    if preferred_norm:
        for key in ("KTU", "CAT"):
            if key in corrs and len(corrs[key]) > 1:
                corrs[key] = _prioritize_correspondences(corrs[key], preferred_norm)

    return {k: "; ".join(vs) for k, vs in corrs.items()}


def _prioritize_correspondences(values: List[str], preferred_norm: str) -> List[str]:
    indexed = list(enumerate(values))
    scored = []
    for idx, value in indexed:
        norm = normalize_reference(value) or ""
        scored.append((0 if norm == preferred_norm else 1, idx, value))
    scored.sort()
    return [value for _, _, value in scored]


def extract_metadata(info_lines: List[str]) -> tuple[Dict[str, str], List[str]]:
    """Extract structured metadata from info lines and return cleaned info lines."""
    meta: Dict[str, str] = {}
    cleaned: List[str] = []
    patterns = {
        "museum": re.compile(r"^museum:\s*(.+)$", re.I),
        "provenance": re.compile(r"^provenance:\s*(.+)$", re.I),
        "measurements": re.compile(r"^measurements[.:]\s*(.+)$", re.I),
        "genre": re.compile(r"^(?:literary\s+)?genre:\s*(.+)$", re.I),
        "alias_line": re.compile(r"^alias(?:es)?:\s*(.+)$", re.I),
    }
    genre_terms = {
        "myth",
        "ritual",
        "correspondence",
        "letter",
        "administrative",
        "cult",
        "legal",
        "epic",
        "hymn",
    }
    measure_re = re.compile(r"^\d+\s*x\s*\d+(?:\s*x\s*\d+)?\.?$")

    def normalize_line(raw: str) -> str:
        ln = raw.strip().strip("_- ").strip()
        ln = re.sub(r"^[•·]\s*", "", ln)
        return ln

    # 1. Split lines into metadata candidates (top section) and content (rest)
    candidates: List[str] = []
    content_lines: List[str] = []
    header_ended = False
    corrs_acc = CorrespondenceAccumulator()

    for ln in info_lines:
        norm = normalize_line(ln)
        raw_norm = _clean_formatting_markers(ln)
        if corrs_acc.maybe_append(ln):
            continue
        if norm.startswith("=") and not header_ended:
            corrs_acc.start(ln.strip().strip("_"))
            continue
        if not norm:
            if header_ended:
                content_lines.append(ln)
            else:
                candidates.append(ln)
            continue

        if not header_ended:
            # Check for stop conditions
            if _split_literature_authors(raw_norm)[0]:
                header_ended = True
            elif re.match(r"^bibliogra[fp]", norm, re.I):
                header_ended = True
            elif norm.lower().startswith("tablet "):
                header_ended = True
            elif (
                norm.startswith("00-")
                or re.match(r"^R\d", norm)
                or norm.startswith("10-")
            ):
                header_ended = True
            elif norm.startswith("Note the following change"):
                header_ended = True
            elif re.match(r"^(?:-|[•·])\s*", raw_norm):
                header_ended = True
            elif re.match(
                r"^(?:Editio princeps|[ÉE]dition pr[ée]liminaire|"
                r"Publi[ée]\s+pour\s+la\s+premi[èe]re\s+fois|Photos?:)",
                norm,
                re.I,
            ):
                header_ended = True

            if header_ended:
                content_lines.append(ln)
            else:
                candidates.append(ln)
        else:
            content_lines.append(ln)

    # 2. Process candidates for metadata
    unmatched_candidates: List[str] = []

    for ln in candidates:
        norm = normalize_line(ln)
        if not norm:
            unmatched_candidates.append(ln)
            continue

        matched = False
        for key, pat in patterns.items():
            m = pat.match(norm)
            if m:
                meta[key] = m.group(1).strip().strip("_")
                matched = True
                break
        if matched:
            continue

        if not meta.get("measurements") and measure_re.match(norm):
            meta["measurements"] = norm.rstrip(". ").strip("_")
            continue

        if not meta.get("genre") and (
            norm.lower() in genre_terms or norm.lower().startswith("genre")
        ):
            meta["genre"] = norm.split(":", 1)[-1].strip().rstrip(".").strip("_")
            continue

        # Fallback for Museum/Provenance
        provenance_hint = re.search(
            r"\b(?:palace|house|acropolis|room|court|archive|trench|tell|"
            r"temple|ras ibn hani|topographic)\b",
            norm,
            re.I,
        )
        if provenance_hint and not meta.get("provenance"):
            meta["provenance"] = norm.strip("_")
            continue
        if (
            not meta.get("museum")
            and not any(ch.isdigit() for ch in norm)
            and "Editio" not in norm
        ):
            meta["museum"] = norm.strip("_")
            continue
        if meta.get("museum") and not meta.get("provenance"):
            meta["provenance"] = norm.strip("_")
            continue

        unmatched_candidates.append(ln)

    # 3. Reassemble cleaned lines: unmatched candidates + content lines
    cleaned = [
        line
        for line in unmatched_candidates + content_lines
        if not _should_drop_info_line(line)
    ]
    if corrs_acc.has_value():
        meta["correspondences_line"] = corrs_acc.value().strip("_")
    return meta, cleaned


def parse_udb_text(text: str) -> List[Dict[str, object]]:
    text = transform_glyphs(text)
    lines = text.splitlines()

    tablets: List[Dict[str, object]] = []
    current: Optional[Dict[str, object]] = None
    buffer: List[str] = []
    info_lines: List[str] = []
    in_content: bool = False
    in_numbering_note: bool = False

    def flush_current():
        nonlocal current, buffer, info_lines, in_content, in_numbering_note
        if not current:
            return
        sources, info_without_sources = extract_edition_sources(info_lines)
        metadata, cleaned_info = extract_metadata(info_without_sources)
        if sources:
            metadata["sources"] = sources
        literature, tablet_comments = extract_literature_and_comments(cleaned_info)
        if literature:
            metadata["literature"] = literature
        if tablet_comments:
            metadata["tablet_comments"] = tablet_comments
        verses = group_readings(buffer)
        current["verses"] = verses
        current["info"] = "\n".join(cleaned_info).strip()
        current["correspondences"] = parse_correspondences(
            metadata.get("correspondences_line", ""),
            preferred_base=str(current.get("udb", "")),
        )
        if metadata:
            current["metadata"] = metadata
            current.update(metadata)
        tablets.append(current)
        current = None
        buffer = []
        info_lines = []
        in_content = False
        in_numbering_note = False

    for ln in lines:
        heading = _normalize_heading(ln)
        if heading:
            flush_current()
            current = {"udb": heading, "verses": []}
            info_lines = []
            in_content = False
            in_numbering_note = False
            continue
        if current is not None:
            # Identify first verse line to split info vs content
            # Exclude lines that are likely bibliography or notes even if they match verse pattern
            is_verse = False
            ln_stripped = ln.strip()
            normalized_line = _clean_formatting_markers(ln)
            if "change in the numeration" in normalized_line.lower() or (
                normalized_line.lower().startswith("note the following")
                and "numeration" in normalized_line.lower()
            ):
                in_numbering_note = True
                info_lines.append(ln)
                continue
            if parse_edition_source_header(ln_stripped) is not None:
                info_lines.append(ln)
                continue
            match = RE_VERSE.match(ln_stripped)
            alt_match = RE_VERSE_ALT.match(ln_stripped)
            if match or alt_match:
                # Heuristic: if it contains "Note the following" or "Bordreuil" (common in biblio), it's not a verse
                # Unless it's a very short line like "00-1.169: 0"
                if "Note the following" in ln_stripped:
                    is_verse = False
                elif (
                    "Bordreuil" in ln_stripped and len(ln_stripped) > 40
                ):  # Arbitrary length check
                    is_verse = False
                elif match and _looks_like_bibliography_stub(
                    match.group("ref"), match.group("text")
                ):
                    is_verse = False
                elif is_editorial_apparatus(
                    (match or alt_match).group("text")  # type: ignore[union-attr]
                ):
                    is_verse = False
                elif in_numbering_note and (
                    (match or alt_match).group("text").strip() in {"", "."}  # type: ignore[union-attr]
                ):
                    is_verse = False
                else:
                    is_verse = True

            if not in_content and is_verse:
                in_content = True
                in_numbering_note = False
            if in_content:
                buffer.append(ln)
            else:
                info_lines.append(ln)
    flush_current()
    return tablets


def group_readings(lines: List[str]) -> List[Dict[str, object]]:
    by_ref: Dict[str, Dict[str, str]] = {}
    comments: Dict[Tuple[str, str], List[str]] = {}
    order: List[str] = []
    last_key: Optional[Tuple[str, str]] = None
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        m = RE_VERSE.match(ln)
        if m:
            reader = normalize_reader_code(m.group("reader"))
            ref = m.group("ref")
            text = m.group("text").strip()
            if _looks_like_bibliography_stub(ref, text) or is_editorial_apparatus(text):
                last_key = None
                continue
            # If the ref is missing the column/line but the text starts with it,
            # consume leading patterns like ": V : 28a" or ": 3" into the ref.
            if text:
                m_col_line = re.match(
                    rf"^:\s*({ROMAN_COLUMN_RE})\s*:\s*([0-9]+[a-z]?)\s*(.*)$",
                    text,
                )
                if m_col_line:
                    col, line, rest = m_col_line.groups()
                    # If ref already contains a column, avoid duplication
                    if not re.search(r"\s+[IVXLCDM]+$", ref):
                        ref = f"{ref} {col}:{line}"
                    else:
                        ref = f"{ref}:{line}"
                    text = rest
                else:
                    m_line = re.match(r"^:\s*([0-9]+[a-z]?)\s*(.*)$", text)
                    if m_line:
                        line, rest = m_line.groups()
                        ref = f"{ref}:{line}"
                        text = rest
            if ref not in by_ref:
                by_ref[ref] = {}
                order.append(ref)
            if reader in by_ref[ref]:
                raise ValueError(f"duplicate reading for {ref} / {reader}")
            by_ref[ref][reader] = text
            last_key = (ref, reader)
            continue
        m_alt = RE_VERSE_ALT.match(ln)
        if m_alt:
            reader = normalize_reader_code(m_alt.group("reader"))
            tablet = m_alt.group("tablet")
            column = m_alt.group("column")
            line_no = m_alt.group("line")
            if column:
                local_ref = tablet.split(".", 1)[1] if "." in tablet else tablet
                ref = f"{local_ref} {column}:{line_no}"
            else:
                ref = f"{tablet}:{line_no}"
            text = m_alt.group("text").strip()
            if is_editorial_apparatus(text):
                last_key = None
                continue
            if ref not in by_ref:
                by_ref[ref] = {}
                order.append(ref)
            if reader in by_ref[ref]:
                raise ValueError(f"duplicate reading for {ref} / {reader}")
            by_ref[ref][reader] = text
            last_key = (ref, reader)
            continue
        # Comment lines often start with '_' (italic in MD)
        if ln.startswith("_") and last_key:
            cleaned = ln.strip()
            if cleaned.startswith("_") and cleaned.endswith("_"):
                cleaned = cleaned.strip("_").strip()
            comments.setdefault(last_key, []).append(cleaned)
            continue
    verses: List[Dict[str, object]] = []
    for ref in order:
        v = {"ref": ref, "readings": by_ref[ref]}
        # Attach comments per reader if any
        cm = {}
        for reader in by_ref[ref].keys():
            key = (ref, reader)
            if key in comments:
                normalized = normalize_comment("\n".join(comments[key]))
                if normalized:
                    cm[reader] = normalized
        if cm:
            v["comments"] = cm
        verses.append(v)
    return verses


def _looks_like_bibliography_stub(ref: str, text: str) -> bool:
    ref_text = str(ref or "").strip()
    line_text = str(text or "").strip()
    if not ref_text:
        return False
    if not line_text:
        return not re.search(r":\s*\d", ref_text)
    if re.search(r":\s*\d", ref_text):
        return False
    if not line_text.startswith(":"):
        return False
    if re.match(
        rf"^:\s*(?:{ROMAN_COLUMN_RE}\s*:\s*)?\d+(?:[–-]\d+)?[a-z]?\b",
        line_text,
        re.I,
    ):
        return False
    return True


def _should_drop_info_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if RE_INFO_PAGE_MARKER.match(stripped):
        return True

    compact = re.sub(r"\s+", "", stripped.replace("_", ""))
    if "," not in compact:
        return False
    return bool(
        re.fullmatch(
            r"(?:(?:R\d+|00|10)-|-)??\d(?:\.\d+){1,3}:?,?",
            compact,
        )
    )


def _anchor_for_ref(ref: str) -> str:
    safe = re.sub(r"[^0-9A-Za-z]+", "-", ref).strip("-")
    return f"v-{safe}"


def render_tablet_html(tablet: Dict[str, object], output_dir: Path | str) -> str:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    udb_no = str(tablet.get("udb"))
    filename = f"udb_{udb_no.replace('.', '_')}.html"
    out_path = out_dir / filename

    verses: List[Dict[str, object]] = tablet.get("verses", [])  # type: ignore
    corrs = tablet.get("correspondences", {})  # type: ignore
    corr_html = ""
    if corrs:
        items = [f"<li><strong>{k}</strong>: {v}</li>" for k, v in corrs.items()]
        corr_html = f"<ul>{''.join(items)}</ul>"
    info_html = ""
    info = str(tablet.get("info", "")).strip()

    # Render metadata fields
    meta_parts = []

    # Render correspondences line first (e.g. = RIH 78/9 ...)
    if tablet.get("correspondences_line"):
        # Use html.escape (from imported module)
        meta_parts.append(
            f'<div class="meta-correspondences-line">{html.escape(str(tablet.get("correspondences_line")))}</div>'
        )

    # Order: Museum, Provenance, Measurements, Genre, Alias
    for key in ["museum", "provenance", "measurements", "genre", "alias_line"]:
        val = tablet.get(key)
        if val:
            # Format label if needed, or just the value?
            # The PDF shows just the value for most, but maybe "Museum: ..." if it was explicit?
            # The extraction strips "Museum: ".
            # Let's render as "Label: Value" for some, or just Value?
            # For "Myth", it's just "Myth".
            # For "Ras...", it's just "Ras...".
            # For "43...", it's just "43...".
            # So just the value seems appropriate for these.
            # But maybe add a class for styling.
            meta_parts.append(f'<div class="meta-{key}">{html.escape(str(val))}</div>')

    meta_html = "\n".join(meta_parts)

    if info or meta_html:
        content = ""
        if meta_html:
            content += f'<div class="metadata">{meta_html}</div>'
        if info:
            content += f'<div class="info-block">{_format_block_html(info)}</div>'
        info_html = f'<section class="info"><h2>Info</h2>{content}</section>'

    rows: List[str] = []
    for v in verses:
        ref = str(v.get("ref"))
        ank = _anchor_for_ref(ref)
        readings: Dict[str, str] = v.get("readings", {})  # type: ignore
        v_comments: Dict[str, str] = v.get("comments", {})  # type: ignore
        blocks = []
        for r, txt in readings.items():
            btn = ""
            chtml = ""
            if r in v_comments and v_comments[r].strip():
                cid = f"cmt-{udb_no.replace('.', '_')}-{_anchor_for_ref(ref)}-{r}"
                btn = f' <button class="cmt-btn" onclick="toggleComment(\'{cid}\')" title="Show comment">💬</button>'
                chtml = f'<div id="{cid}" class="comment" hidden>{_format_block_html(v_comments[r])}</div>'
            blocks.append(
                f'<div class="reading"><span class="reader">{r}</span> {txt}{btn}{chtml}</div>'
            )
        rows.append(
            "<tr>"
            f'<td class="ref"><a id="{ank}"></a>{ref}</td>'
            f'<td class="readings">{"".join(blocks)}</td>'
            "</tr>"
        )

    html_content = f"""
<!DOCTYPE html>
<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<title>UDB {udb_no}</title>
<style>
body {{ font-family: -apple-system, system-ui, Segoe UI, Roboto, sans-serif; line-height: 1.4; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 6px 8px; vertical-align: top; }}
th {{ background: #f6f6f6; position: sticky; top: 0; }}
td.ref {{ white-space: nowrap; font-weight: 600; }}
mark {{ background: #ffee88; }}
.readings {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }}
.reading {{ margin: 2px 0; }}
.reader {{ display: inline-block; min-width: 4.5em; color: #555; }}
.info-block {{ white-space: pre-wrap; margin: 0.5rem 0 1rem; }}
.comment {{ white-space: pre-wrap; border-left: 3px solid #ddd; padding-left: 8px; margin: 4px 0 4px 0; }}
.cmt-btn {{ font-size: 0.85em; padding: 2px 6px; margin-left: 6px; }}
.metadata {{ margin-bottom: 1rem; }}
.meta-museum, .meta-provenance, .meta-measurements, .meta-genre, .meta-alias_line {{ margin-bottom: 0.25rem; }}
.meta-correspondences-line {{ font-weight: bold; margin-bottom: 0.5rem; }}
.meta-genre {{ font-style: italic; }} /* Often italic in source? No, "Myth" is plain. But let's keep it simple. */
</style>
</head>
<body>
<h1>UDB {udb_no}</h1>
<section><h2>Correspondences</h2>{corr_html}</section>
{info_html}
<section>
<table>
  <thead>
    <tr><th>Reference</th><th>Readings</th></tr>
  </thead>
  <tbody>
    {"".join(rows)}
  </tbody>
</table>
</section>
<script>
function toggleComment(id) {{
  var el = document.getElementById(id);
  if (!el) return;
  if (el.hasAttribute('hidden')) {{ el.removeAttribute('hidden'); }}
  else {{ el.setAttribute('hidden', ''); }}
}}
</script>
</body>
</html>
"""
    out_path.write_text(html_content, encoding="utf-8")
    return str(out_path)


def _format_inline_html(text: str) -> str:
    """Convert underscore-delimited italic markers to HTML: _italic_ -> <i>italic</i>."""
    return re.sub(r"_(.+?)_", lambda m: f"<i>{m.group(1)}</i>", text)


def _format_block_html(block: str, force_italic: bool = False) -> str:
    """Convert UDB info blocks and comments to HTML.

    Supports:
    - Top-level bullet lists with line continuations
    - Group markers starting with "• " which start a titled sub-list
    - Nested bullet lists under each "• " group
    - Inline italics using underscore delimiters (_text_) on the same logical line

    Heuristic: a bullet item continues until a blank line, next bullet ('- ' / '_- '),
    or next group marker ('• '). Continuation lines are appended to the same <li> with a<br>.

    If ``force_italic`` is True, returns the entire block as a single italicized
    paragraph with line breaks preserved (used for comment bubbles).
    """
    if force_italic:
        cleaned = [
            ln.strip("_ ").strip()
            for ln in block.splitlines()
            if ln.strip("_ ").strip()
        ]
        if not cleaned:
            return ""
        return f"<i>{'<br>'.join(html.escape(s) for s in cleaned)}</i>"

    # Normalize noisy underscore lines from pdfminer output
    norm_lines: List[str] = []
    for ln in block.splitlines():
        raw = ln.rstrip()
        if raw.strip() in {"", "_", "-"}:
            continue
        stripped = raw.strip()
        if stripped.startswith("_") and stripped.endswith("_") and len(stripped) > 1:
            inner = stripped.strip("_ ").strip()
            if inner:
                raw = f"_{inner}_"
            else:
                continue
        elif stripped.startswith("_"):
            inner = stripped.lstrip("_ ").strip()
            raw = f"_{inner}_" if inner else ""
        elif stripped.endswith("_"):
            inner = stripped.rstrip("_ ").strip()
            raw = f"_{inner}_" if inner else ""
        if raw:
            norm_lines.append(raw)

    lines = norm_lines

    def collect_item(start_idx: int) -> tuple[str, int]:
        """Collect a bullet item with following continuation lines.

        Returns (html_li_string, next_index).
        """
        i = start_idx
        first = lines[i].strip()
        content = (
            first[2:]
            if first.startswith("- ")
            else first[3:]
            if first.startswith("_- ")
            else first
        )
        parts = [content]
        i += 1
        while i < len(lines):
            s = lines[i].strip()
            if not s:
                # blank line ends the item
                break
            if s.startswith("- ") or s.startswith("_- ") or s.startswith("• "):
                break
            # continuation line; append
            parts.append(lines[i])
            i += 1
        # join with <br> and apply inline formatting
        joined = _format_inline_html("<br>".join(parts))
        return f"<li>{joined}</li>", i

    html_parts: List[str] = []
    i = 0
    # Top-level list being built
    pending_ul: List[str] = []

    def flush_ul():
        nonlocal pending_ul
        if pending_ul:
            html_parts.append(f"<ul>{''.join(pending_ul)}</ul>")
            pending_ul = []

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            # paragraph break; flush any open list
            flush_ul()
            i += 1
            continue
        if s.startswith("• "):
            # Group marker: flush preceding list, add header, then start a new list context
            flush_ul()
            # Group title is the rest of the line after the bullet dot
            group_title = s[2:].strip()
            html_parts.append(
                f'<div class="biblio-group"><div class="biblio-title">• {html.escape(group_title)}</div>'
            )
            # Collect following list items under this group
            i += 1
            group_items: List[str] = []
            while i < len(lines):
                s2 = lines[i].strip()
                if not s2:
                    # blank ends sub-list
                    break
                if s2.startswith("• "):
                    # next group; stop here to outer loop
                    break
                if s2.startswith("- ") or s2.startswith("_- "):
                    li, i = collect_item(i)
                    group_items.append(li)
                    continue
                # Non-bullet content directly under group; treat as continuation to previous item if any
                if group_items:
                    # append as continuation to the last <li>
                    extra = _format_inline_html(lines[i])
                    group_items[-1] = group_items[-1][:-5] + f"<br>{extra}</li>"
                else:
                    # or a paragraph within the group
                    html_parts.append(_format_inline_html(lines[i]))
                i += 1
            if group_items:
                html_parts.append(f"<ul>{''.join(group_items)}</ul>")
            html_parts.append("</div>")
            continue
        if s.startswith("- ") or s.startswith("_- "):
            li, i = collect_item(i)
            pending_ul.append(li)
            continue
        # Plain paragraph line; flush any list and emit paragraphish line
        flush_ul()
        html_parts.append(_format_inline_html(line))
        i += 1

    flush_ul()
    # Add minimal styles for biblio groups
    return "\n".join(html_parts)


def write_reverse_index(
    tablets: List[Dict[str, object]], path: Path | str, output_dir: Path | str
) -> None:
    """Write a reverse index mapping normalized refs to UDB anchors.

    Includes:
      - CAT/KTU tablet base -> page
      - CAT/KTU tablet + :line -> page#anchor
      - RS base -> page (no per-line mapping available)
    """
    out: Dict[str, str] = {}
    for t in tablets:
        udb_no = str(t.get("udb"))
        page = f"udb_{udb_no.replace('.', '_')}.html"
        corrs: Dict[str, str] = t.get("correspondences", {})  # type: ignore
        # Base tablet mapping for CAT/KTU/TU and RS, plus any other known tokens from info
        for key in ("CAT", "KTU", "TU"):
            if key in corrs:
                base = corrs[key]
                # Normalize to CAT prefix
                base_norm = normalize_reference(base) or base
                out[base_norm] = page
                # Also provide KTU form if CAT returned
                if base_norm.startswith("CAT "):
                    out[base_norm.replace("CAT ", "KTU ")] = page
        if "RS" in corrs:
            out[corrs["RS"]] = page
        # Pass through other correspondences like UT, CTA, DO, PRU as base-page mappings
        for key in ("UT", "CTA", "DO", "PRU"):
            if key in corrs:
                out[corrs[key]] = page
        # Per-verse anchors for CAT/KTU
        verses: List[Dict[str, object]] = t.get("verses", [])  # type: ignore
        # Derive CAT tablet tag like "CAT 1.77"
        cat_base = None
        for key in ("CAT", "KTU", "TU"):
            if key in corrs:
                base_norm = normalize_reference(corrs[key]) or corrs[key]
                if base_norm.startswith("CAT "):
                    cat_base = base_norm
                    break
        if cat_base:
            for v in verses:
                ref = str(v.get("ref"))
                # Append :line (i.e., 77:2 -> CAT 1.77:2)
                if ":" in ref:
                    line = ref.split(":", 1)[1]
                    anchor_id = f"v-{re.sub(r'[^0-9A-Za-z]+', '-', ref)}"
                    out[f"{cat_base}:{line}"] = f"{page}#{anchor_id}"
                    out[f"{cat_base.replace('CAT ', 'KTU ')}:{line}"] = (
                        f"{page}#{anchor_id}"
                    )
    Path(path).write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def write_index_json(tablets: List[Dict[str, object]], path: Path | str) -> None:
    data = [
        {
            "udb": t.get("udb"),
            "correspondences": t.get("correspondences", {}),
        }
        for t in tablets
    ]
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def write_reverse_index_from_html(html_dir: Path | str, out_path: Path | str) -> None:
    """Build a reverse index from already-rendered UDB HTML files.

    Extract correspondences (RS, KTU/CAT/TU, UT, CTA, DO, PRU, etc.) and per-verse
    anchors from each HTML page under ``html_dir`` and write a JSON mapping.
    """
    import bs4  # type: ignore

    out: Dict[str, str] = {}
    html_dir = Path(html_dir)
    for p in sorted(html_dir.glob("udb_*.html")):
        page = p.name
        try:
            soup = bs4.BeautifulSoup(p.read_text(encoding="utf-8"), "html.parser")
        except Exception:
            continue
        # Correspondences list
        for li in soup.select("section > ul li"):
            strong = li.find("strong")
            if not strong:
                continue
            key = (strong.get_text(" ", strip=True) or "").upper()
            # The value is the text after the strong label and optional colon
            full = li.get_text(" ", strip=True) or ""
            value = full
            if ":" in full:
                try:
                    value = full.split(":", 1)[1].strip()
                except Exception:
                    value = full
            # value can be like "RS 12.061" or "KTU 1.77" etc.
            # Keep only normalized corpus forms where applicable.
            if key in {"CAT", "KTU", "TU"}:
                base_norm = normalize_reference(value) or value
                out[base_norm] = page
                if base_norm.startswith("CAT "):
                    out[base_norm.replace("CAT ", "KTU ")] = page
            elif key == "RS":
                out[value] = page
            elif key in {"UT", "CTA", "DO", "PRU"}:
                out[value] = page
        # Per-verse anchors: derive CAT/KTU base from correspondences if present
        cat_base = None
        for k in ("CAT", "KTU", "TU"):
            # recover from the ul again
            pass
        # Alternatively take from page filename: udb_G_T.html -> CAT G.T
        m = re.match(r"^udb_(\d+)_(\d+)\.html$", page)
        if m:
            cat_base = f"CAT {int(m.group(1))}.{int(m.group(2))}"
        if cat_base:
            for row in soup.select("table tbody tr"):
                ref_cell = row.find("td", class_="ref")
                a = ref_cell.find("a") if ref_cell else None
                if not a or not a.get("id"):
                    continue
                ref_text = (ref_cell.get_text(" ", strip=True) or "").strip()
                if not ref_text or ":" not in ref_text:
                    continue
                line = ref_text.split(":", 1)[1].strip()
                anchor_id = a.get("id")
                out[f"{cat_base}:{line}"] = f"{page}#{anchor_id}"
                out[f"{cat_base.replace('CAT ', 'KTU ')}:{line}"] = (
                    f"{page}#{anchor_id}"
                )
        # done file
    Path(out_path).write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _render_pdfminer_line(line) -> str:
    """Render a pdfminer LineData into text with underscore-delimited italic markers."""
    if not getattr(line, "spans", None):
        return ""
    merged_spans: List[Tuple[str, bool]] = []
    current_text = ""
    current_italic = (line.spans[0].flags & 2) != 0
    for span in line.spans:
        is_italic = (span.flags & 2) != 0
        if is_italic == current_italic:
            current_text += span.text
        else:
            merged_spans.append((current_text, current_italic))
            current_text = span.text
            current_italic = is_italic
    merged_spans.append((current_text, current_italic))

    line_text = ""
    for text, is_italic in merged_spans:
        if is_italic:
            if not text.strip():
                line_text += text
            else:
                prefix = ""
                suffix = ""
                if text.startswith(" "):
                    prefix = " "
                    text = text.lstrip(" ")
                if text.endswith(" "):
                    suffix = " "
                    text = text.rstrip(" ")
                if text:
                    line_text += f"{prefix}_{text}_{suffix}"
                else:
                    line_text += prefix + suffix
        else:
            line_text += text
    return line_text.rstrip("\n")


def _merge_pdfminer_rows(
    pages, y_tolerance: float = 2.0, comment_x_threshold: float = 240.0
) -> List[str]:
    """Merge multi-column pdfminer rows so ref + text live on a single line.

    If a row appears in the right-hand comment column (x beyond ``comment_x_threshold``),
    wrap it in underscores so it is treated as an italic comment line.
    """
    merged: List[str] = []
    for page in pages:
        entries: List[Tuple[float, float, str]] = []
        for block in page.blocks:
            for line in block.lines:
                text = _render_pdfminer_line(line)
                if not text or text.strip() == "_":
                    continue
                bbox = getattr(line, "bbox", None) or (0.0, 0.0, 0.0, 0.0)
                y_top = bbox[3]
                x_left = bbox[0]
                entries.append((y_top, x_left, text.strip()))
        if not entries:
            merged.append("")
            continue
        entries.sort(key=lambda t: (-t[0], t[1]))
        rows: List[List[Tuple[float, str]]] = []
        current_y = None
        current_row: List[Tuple[float, str]] = []
        for y_top, x_left, text in entries:
            if current_y is None or abs(current_y - y_top) > y_tolerance:
                if current_row:
                    rows.append(current_row)
                current_y = y_top
                current_row = [(x_left, text)]
            else:
                current_row.append((x_left, text))
        if current_row:
            rows.append(current_row)
        for row in rows:
            row.sort(key=lambda t: t[0])
            texts = [part for _x, part in row]
            row_text = " ".join(texts)
            has_ref = any(RE_VERSE.match(t) or RE_VERSE_ALT.match(t) for t in texts)
            if not has_ref:
                min_x = min(x for x, _ in row)
                if min_x >= comment_x_threshold and not (
                    row_text.startswith("_") and row_text.endswith("_")
                ):
                    row_text = f"_{row_text}_"
            merged.append(row_text)
        merged.append("")
    return merged


def _extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """Extract text from PDF using pdfminer with underscore-delimited italic markers."""
    if PDFMinerParser is None:
        raise ImportError(
            "PDFMinerParser not available. Install pdfminer.six and ensure parser.pdfminer_parser is importable."
        )

    try:
        parser = PDFMinerParser()
        pages = parser.extract_pages(pdf_path)
        lines = _merge_pdfminer_rows(pages)
        return "\n".join(lines)
    except Exception as e:
        print(f"PDFMiner extraction failed: {e}")
        return None


def _tablets_to_models(tablets: List[Dict[str, object]]) -> List[UDBTablet]:
    """Convert legacy tablet dicts to UDBTablet dataclasses for JSON export."""
    models: List[UDBTablet] = []
    for t in tablets:
        udb_id = str(t.get("udb") or t.get("udb_id") or "")
        verses: List[UDBVerse] = []
        for v in t.get("verses", []):  # type: ignore
            readings: Dict[str, str] = {}
            for k, vv in (v.get("readings", {}) or {}).items():
                raw = str(vv)
                if is_editorial_apparatus(raw):
                    continue  # drop a reading that is wholly an editorial note
                readings[k] = strip_editorial_notes(raw)  # strip embedded notes
            verses.append(
                UDBVerse(
                    ref=str(v.get("ref", "")),
                    readings=readings,
                    comments={
                        k: str(vv) for k, vv in (v.get("comments", {}) or {}).items()
                    },
                )
            )
        metadata = (
            t.get("metadata", {}) if isinstance(t.get("metadata", {}), dict) else {}
        )
        models.append(
            UDBTablet(
                udb_id=udb_id,
                correspondences=t.get("correspondences", {}) or {},
                info=str(t.get("info", "") or ""),
                verses=verses,
                metadata=metadata,
            )
        )
    return models


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Convert UDB PDF/Text to per-tablet HTML with anchors."
    )
    ap.add_argument(
        "--input-pdf",
        dest="input_pdf",
        help="Path to UDB PDF (e.g., pdfs/Ugaritic_data_bank.pdf)",
    )
    ap.add_argument(
        "--input-text", dest="input_text", help="Path to pre-extracted UDB text"
    )
    ap.add_argument(
        "--output-dir", default="data/udb_html", help="Directory to write HTML files"
    )
    ap.add_argument(
        "--output-json", dest="output_json", help="Path to write full parsed JSON"
    )

    ap.add_argument(
        "--save-text",
        dest="save_text",
        action="store_true",
        help="Also save processed text next to outputs",
    )
    ap.add_argument(
        "--index-json", default="data/udb_index.json", help="Path to write index JSON"
    )
    ap.add_argument(
        "--reverse-index",
        dest="reverse_index",
        default=None,
        help="Optional path to write reverse index JSON",
    )
    ap.add_argument(
        "--only",
        dest="only_udb",
        default=None,
        help="Render only this UDB tablet (e.g., 1.77)",
    )
    ap.add_argument(
        "--stats", dest="stats_json", default=None, help="Write per-tablet stats JSON"
    )
    args = ap.parse_args(argv)

    raw_text: Optional[str] = None
    if args.input_text:
        raw_text = Path(args.input_text).read_text(encoding="utf-8")
    elif args.input_pdf:
        raw_text = _extract_text_from_pdf(args.input_pdf)
    else:
        ap.error("Provide either --input-text or --input-pdf")

    if not raw_text:
        print("Failed to extract text from input.")
        return 2

    tablets = parse_udb_text(raw_text)
    if args.only_udb:
        tablets = [t for t in tablets if str(t.get("udb")) == args.only_udb]

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stats = []
    for t in tablets:
        render_tablet_html(t, out_dir)
        stats.append(
            {
                "udb": t.get("udb"),
                "verses": len(t.get("verses", [])),
                "has_info": bool(t.get("info")),
                "corrs": list((t.get("correspondences") or {}).keys()),
            }
        )

    write_index_json(tablets, args.index_json)
    if args.output_json:
        out_path = Path(args.output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        models = _tablets_to_models(tablets)
        if out_path.suffix.lower() == ".json" or (
            out_path.exists() and out_path.is_file()
        ):
            payload = [t.to_dict() for t in models]
            out_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        else:
            write_tablets_to_json(models, out_path)
    if args.reverse_index:
        write_reverse_index(tablets, args.reverse_index, out_dir)
    if args.stats_json:
        Path(args.stats_json).write_text(
            json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if args.save_text:
        (out_dir / "udb_processed.txt").write_text(
            transform_glyphs(raw_text), encoding="utf-8"
        )

    print(f"Wrote {len(tablets)} tablets to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
