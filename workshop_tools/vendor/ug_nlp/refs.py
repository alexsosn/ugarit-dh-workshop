from __future__ import annotations

import re
from typing import Optional, Dict

KTU_REF_RE = re.compile(
    r"\b\d+\.\d+(?:\s+[IVXLCDM]+)?\s*(?::\s*\d+|\s+[IVXLCDM]+\s+\d+)\b"
)
ROMAN_RE = r"[IVXLCDM]+"
GENRE_DESCRIPTIONS: dict[int, str] = {
    1: "literary and religious texts",
    2: "letters",
    3: "legal texts",
    4: "economic or administrative texts",
    5: "scribal exercises",
    6: "inscriptions on seals, labels, ivories, etc.",
    7: "unclassified texts",
    8: "illegible tablets and uninscribed fragments",
    9: "unpublished texts",
}


def genre_description(n: int) -> str:
    return GENRE_DESCRIPTIONS.get(n, "")


def parse_ugaritic_reference(reference: str) -> Optional[Dict[str, object]]:
    """Parse Ugaritic references in CAT/KTU, RS, or RIH formats.

    Accepts forms like:
      - "CAT 1.14:4", "KTU 1.14 IV 38", or shorthand "1.15 II 16", "2.16:11"
      - "RS 15.111:30", "RS 1994.2401"
      - "RIH 77/25"
    Returns a dict with keys suitable for downstream linking/formatting.
    """
    if not reference:
        return None
    ref = reference.strip()
    # RS
    m = re.match(
        r"^RS\s+(?:(?P<year>\d{2,4})\.)?(?P<num>\d+)(?::(?P<line>\d+(?:[–-]\d+)?))?$",
        ref,
        re.I,
    )
    if m:
        return {
            "source": "RS",
            "year": m.group("year"),
            "number": int(m.group("num")),
            "line": m.group("line"),
        }
    # RIH
    m = re.match(r"^RIH\s+(?P<year>\d+)\/(?P<num>\d+)$", ref, re.I)
    if m:
        return {
            "source": "RIH",
            "year": m.group("year"),
            "number": int(m.group("num")),
        }
    # CAT/KTU with or without prefix, optional column (Roman), optional lines
    # Accept both colon form (e.g., "1.16 II:40") and space form ("1.16 II 40")
    cat_re = rf"^(?:(?P<prefix>CAT|KTU)\s+)?(?P<genre>\d)\.(?P<t1>\d{{1,3}})(?:\.(?P<t2>\d{{1,3}}))?(?:\.(?P<t3>\d{{1,3}}))?(?:\s+(?P<col>{ROMAN_RE}))?(?::(?P<line1>\d+(?:[–-]\d+)?))?(?:\s+(?P<line2>\d+(?:[–-]\d+)?))?$"
    m = re.match(cat_re, ref, re.I)
    if m:
        data: Dict[str, object] = {
            "source": "CAT",
            "genre": int(m.group("genre")),
            "text": int(m.group("t1")),
        }
        if m.group("t2"):
            data["sub1"] = int(m.group("t2"))
        if m.group("t3"):
            data["sub2"] = int(m.group("t3"))
        if m.group("col"):
            data["column"] = m.group("col").upper()
        ln = m.group("line1") or m.group("line2")
        if ln:
            data["line"] = ln
        return data
    return None


def normalize_reference(reference: str) -> Optional[str]:
    if ";" in reference:
        reference = reference.split(";", 1)[0].strip()
    parsed = parse_ugaritic_reference(reference)
    if not parsed:
        return None
    src = parsed.get("source", "CAT")
    if src == "CAT":
        parts = [f"{parsed['genre']}", str(parsed["text"])]
        for key in ("sub1", "sub2"):
            if key in parsed:
                parts.append(str(parsed[key]))
        cat = ".".join(parts)
        col = f" {parsed['column']}" if parsed.get("column") else ""
        line = f":{parsed['line']}" if parsed.get("line") else ""
        return f"CAT {cat}{col}{line}"
    if src == "RS":
        year = parsed.get("year")
        num = parsed.get("number")
        line = f":{parsed['line']}" if parsed.get("line") else ""
        return f"RS {year + '.' if year else ''}{num}{line}"
    if src == "RIH":
        return f"RIH {parsed.get('year')}/{parsed.get('number')}"
    return reference


def reference_anchor(reference: str) -> Optional[str]:
    """Format a reference label for display.

    CUC browser integration removed; return normalised reference as plain text.
    """
    parsed = parse_ugaritic_reference(reference)
    if not parsed:
        return None
    return normalize_reference(reference) or reference
