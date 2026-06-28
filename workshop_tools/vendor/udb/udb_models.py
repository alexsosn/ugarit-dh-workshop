"""
UDB JSON data models.

Structured data models for UDB tablets with JSON serialization support.
These replace the intermediate markdown/HTML formats in the new pipeline.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any


@dataclass
class UDBVerse:
    """
    Individual verse/line reading from a UDB tablet.

    Represents a single verse with multiple reader variants and optional comments.
    """
    ref: str  # Reference (e.g., "77:2", "78:1")
    readings: Dict[str, str] = field(default_factory=dict)  # Reader ID -> text
    comments: Dict[str, str] = field(default_factory=dict)  # Reader ID -> comment

    def to_dict(self) -> Dict[str, Any]:
        """Serialize verse to dictionary for JSON export."""
        return {
            "ref": self.ref,
            "readings": self.readings,
            "comments": self.comments
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UDBVerse:
        """Deserialize verse from dictionary."""
        return cls(
            ref=data["ref"],
            readings=data.get("readings", {}),
            comments=data.get("comments", {})
        )


@dataclass
class UDBTablet:
    """
    Complete UDB tablet with metadata, correspondences, and verses.

    This is the top-level container for a single UDB tablet document.
    """
    udb_id: str  # Tablet identifier (e.g., "1.77", "9.3")
    correspondences: Dict[str, str] = field(default_factory=dict)  # Corpus -> ref mapping
    info: str = ""  # Introductory text/metadata block
    verses: List[UDBVerse] = field(default_factory=list)  # List of verse readings
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tablet to dictionary for JSON export."""
        return {
            "udb_id": self.udb_id,
            "correspondences": self.correspondences,
            "info": self.info,
            "verses": [v.to_dict() for v in self.verses],
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UDBTablet:
        """Deserialize tablet from dictionary."""
        verses_data = data.get("verses", [])
        verses = [UDBVerse.from_dict(v) for v in verses_data]

        return cls(
            udb_id=data["udb_id"],
            correspondences=data.get("correspondences", {}),
            info=data.get("info", ""),
            verses=verses,
            metadata=data.get("metadata", {})
        )

    def get_filename(self) -> str:
        """Get the standard filename for this tablet's JSON file."""
        # Convert "1.77" to "udb_1_77.json"
        safe_id = self.udb_id.replace(".", "_")
        return f"udb_{safe_id}.json"


def write_tablets_to_json(tablets: List[UDBTablet], output_dir: Path | str) -> None:
    """
    Write tablets to individual JSON files.

    Args:
        tablets: List of UDBTablet objects to serialize
        output_dir: Directory to write JSON files to
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for tablet in tablets:
        filename = tablet.get_filename()
        filepath = out_dir / filename

        # Serialize with pretty printing and Unicode support
        json_data = json.dumps(
            tablet.to_dict(),
            ensure_ascii=False,
            indent=2
        )

        filepath.write_text(json_data, encoding="utf-8")


def load_tablets_from_json(json_dir: Path | str) -> List[UDBTablet]:
    """
    Load tablets from JSON files in a directory.

    Args:
        json_dir: Directory containing UDB JSON files

    Returns:
        List of UDBTablet objects loaded from files
    """
    directory = Path(json_dir)
    if not directory.exists():
        return []

    tablets: List[UDBTablet] = []

    # Load all JSON files matching the pattern
    for filepath in sorted(directory.glob("udb_*.json")):
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            tablet = UDBTablet.from_dict(data)
            tablets.append(tablet)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Log error but continue loading other files
            print(f"Warning: Failed to load {filepath}: {e}")
            continue

    return tablets
