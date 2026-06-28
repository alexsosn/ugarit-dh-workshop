"""
Abstract base classes and data models for PDF parsing.

This module provides an interface for PDF parsing
(pdfminer.six) to ensure consistent data extraction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class SpanData:
    """
    Normalized representation of a text span with formatting information.

    A span is a continuous piece of text with consistent formatting (font, size, style).
    This structure is parser-agnostic and can be populated from pdfminer data.
    """
    text: str
    font: str
    size: float
    flags: int  # Font flags (bold=20, italic=2, superscript=1, etc.)
    char_flags: int  # Character-level flags
    origin: Tuple[float, float]  # (x, y) position of the span
    color: Optional[Tuple[float, float, float]] = None  # RGB color

    def __post_init__(self):
        """Validate span data."""
        if not isinstance(self.text, str):
            raise ValueError(f"text must be str, got {type(self.text)}")
        if not isinstance(self.font, str):
            raise ValueError(f"font must be str, got {type(self.font)}")
        if not isinstance(self.size, (int, float)):
            raise ValueError(f"size must be numeric, got {type(self.size)}")


@dataclass
class LineData:
    """
    Normalized representation of a line of text.

    A line contains multiple spans with potentially different formatting.
    """
    spans: List[SpanData] = field(default_factory=list)
    bbox: Optional[Tuple[float, float, float, float]] = None  # Bounding box (x0, y0, x1, y1)

    def add_span(self, span: SpanData) -> None:
        """Add a span to this line."""
        self.spans.append(span)

    def get_text(self) -> str:
        """Get the full text of this line."""
        return "".join(span.text for span in self.spans)


@dataclass
class BlockData:
    """
    Normalized representation of a text block.

    A block contains multiple lines, typically representing a paragraph or section.
    """
    lines: List[LineData] = field(default_factory=list)
    bbox: Optional[Tuple[float, float, float, float]] = None  # Bounding box

    def add_line(self, line: LineData) -> None:
        """Add a line to this block."""
        self.lines.append(line)

    def get_text(self) -> str:
        """Get the full text of this block."""
        return "".join(line.get_text() for line in self.lines)


@dataclass
class PageData:
    """
    Normalized representation of a PDF page.

    This structure is designed to be compatible with the existing get_records()
    function while abstracting away parser-specific details.
    """
    page_number: int
    blocks: List[BlockData] = field(default_factory=list)
    width: float = 0.0
    height: float = 0.0

    def add_block(self, block: BlockData) -> None:
        """Add a block to this page."""
        self.blocks.append(block)

    def get_text(self, mode: str = "text") -> str:
        """
        Get text from the page in the specified mode.

        Args:
            mode: "text" for plain text, "dict" for dictionary structure

        Returns:
            Text content or dictionary representation
        """
        if mode == "text":
            return "\n".join(block.get_text() for block in self.blocks)
        elif mode == "dict":
            # Return a dict structure compatible with get_text("dict")
            return {
                "width": self.width,
                "height": self.height,
                "blocks": [
                    {
                        "lines": [
                            {
                                "spans": [
                                    {
                                        "text": span.text,
                                        "font": span.font,
                                        "size": span.size,
                                        "flags": span.flags,
                                        "char_flags": span.char_flags,
                                        "origin": span.origin,
                                        "color": span.color,
                                    }
                                    for span in line.spans
                                ],
                                "bbox": line.bbox,
                            }
                            for line in block.lines
                        ],
                        "bbox": block.bbox,
                    }
                    for block in self.blocks
                ]
            }
        else:
            raise ValueError(f"Unknown mode: {mode}")


class PDFParser(ABC):
    """
    Abstract base class for PDF parsers.

    Implementations must provide a method to extract pages from a PDF file
    and return them as normalized PageData objects.
    """

    @abstractmethod
    def extract_pages(
            self,
            pdf_path: str,
            start_page: int = 0,
            end_page: Optional[int] = None
    ) -> List[PageData]:
        """
        Extract pages from a PDF file.

        Args:
            pdf_path: Path to the PDF file
            start_page: Zero-based index of the first page to extract
            end_page: Zero-based index of the last page to extract (inclusive)
                     If None, extract until the end of the document

        Returns:
            List of PageData objects, one per extracted page
        """
        pass

    @abstractmethod
    def get_page_count(self, pdf_path: str) -> int:
        """
        Get the total number of pages in a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Number of pages in the document
        """
        pass
