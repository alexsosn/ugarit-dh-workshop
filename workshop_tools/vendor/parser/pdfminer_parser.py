"""
PDF parser implementation using pdfminer.six.

This parser extracts text and formatting information from PDF files with
better preservation of spacing and character-level formatting.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from pdfminer.high_level import extract_pages
from pdfminer.layout import (
    LAParams, LTTextContainer, LTChar, LTAnno,
    LTTextLineHorizontal, LTTextBoxHorizontal, LTPage
)
from pdfminer.pdfpage import PDFPage

from parser.pdf_parser import (
    PDFParser, PageData, BlockData, LineData, SpanData
)

logger = logging.getLogger(__name__)


class PDFMinerParser(PDFParser):
    """
    PDF parser using pdfminer.six library.

    This parser provides better text extraction with proper spacing and detailed
    formatting information (fonts, sizes, positions) compared to PyMuPDF.
    """

    def __init__(self, laparams: Optional[LAParams] = None):
        """
        Initialize the pdfminer parser.

        Args:
            laparams: Layout analysis parameters for pdfminer.
                     If None, uses defaults optimized for the source layout.
        """
        # Optimize LAParams for the source layout
        if laparams is None:
            laparams = LAParams(
                line_overlap=0.5,
                char_margin=2.0,
                line_margin=0.5,
                word_margin=0.1,
                boxes_flow=0.5,
                detect_vertical=False,
                all_texts=False
            )
        self.laparams = laparams

    def get_page_count(self, pdf_path: str) -> int:
        """Get the total number of pages in a PDF file."""
        with open(pdf_path, 'rb') as fp:
            return len(list(PDFPage.get_pages(fp)))

    def extract_pages(
            self,
            pdf_path: str,
            start_page: int = 0,
            end_page: Optional[int] = None
    ) -> List[PageData]:
        """
        Extract pages from a PDF file using pdfminer.six.

        Args:
            pdf_path: Path to the PDF file
            start_page: Zero-based index of the first page to extract
            end_page: Zero-based index of the last page to extract (inclusive)
                     If None, extract until the end of the document

        Returns:
            List of PageData objects with detailed formatting information
        """
        pages_data: List[PageData] = []

        try:
            # Extract pages using pdfminer's high-level API
            for page_num, page_layout in enumerate(
                    extract_pages(pdf_path, laparams=self.laparams)
            ):
                # Skip pages outside the requested range
                if page_num < start_page:
                    continue
                if end_page is not None and page_num > end_page:
                    break

                # Convert pdfminer page to our normalized format
                page_data = self._convert_page(page_layout, page_num)
                pages_data.append(page_data)

        except Exception as e:
            logger.error(f"Error extracting pages from {pdf_path}: {e}")
            raise

        return pages_data

    def _convert_page(self, page_layout: LTPage, page_num: int) -> PageData:
        """
        Convert a pdfminer LTPage to our normalized PageData structure.

        Args:
            page_layout: pdfminer's LTPage object
            page_num: Zero-based page number

        Returns:
            PageData object with blocks, lines, and spans
        """
        page_data = PageData(
            page_number=page_num,
            width=page_layout.width,
            height=page_layout.height
        )

        # Extract text containers (blocks) from the page
        # Sort by y-position (top to bottom) then x-position (left to right)
        text_containers = [
            elem for elem in page_layout
            if isinstance(elem, (LTTextBoxHorizontal, LTTextContainer))
        ]

        # Sort blocks by position (top to bottom, left to right)
        text_containers.sort(
            key=lambda elem: (-elem.y1, elem.x0)
        )

        for container in text_containers:
            block = self._convert_text_container(container, page_layout.height)
            if block.lines:  # Only add non-empty blocks
                page_data.add_block(block)

        return page_data

    def _convert_text_container(
            self,
            container: LTTextContainer,
            page_height: float
    ) -> BlockData:
        """
        Convert a pdfminer text container to BlockData.

        Args:
            container: pdfminer's LTTextContainer or LTTextBox
            page_height: Height of the page (for coordinate conversion)

        Returns:
            BlockData with lines and spans
        """
        block = BlockData(bbox=(container.x0, container.y0, container.x1, container.y1))

        # Extract lines from the container
        lines = [
            elem for elem in container
            if isinstance(elem, LTTextLineHorizontal)
        ]

        # Sort lines by y-position (top to bottom)
        lines.sort(key=lambda line: -line.y1)

        for line_layout in lines:
            line = self._convert_text_line(line_layout, page_height)
            if line.spans:  # Only add non-empty lines
                block.add_line(line)

        return block

    def _convert_text_line(
            self,
            line_layout: LTTextLineHorizontal,
            page_height: float
    ) -> LineData:
        """
        Convert a pdfminer text line to LineData.

        Args:
            line_layout: pdfminer's LTTextLineHorizontal
            page_height: Height of the page (for coordinate conversion)

        Returns:
            LineData with spans grouped by consistent formatting
        """
        line = LineData(bbox=(line_layout.x0, line_layout.y0, line_layout.x1, line_layout.y1))

        # Group consecutive characters with the same formatting into spans
        current_span_chars: List[LTChar] = []
        current_span_text = ""

        for element in line_layout:
            if isinstance(element, LTChar):
                # Check if this character should start a new span
                if current_span_chars and not self._same_format(
                        current_span_chars[-1], element
                ):
                    # Finalize current span
                    span = self._create_span(
                        current_span_chars,
                        current_span_text,
                        page_height
                    )
                    line.add_span(span)
                    current_span_chars = []
                    current_span_text = ""

                # Add character to current span
                current_span_chars.append(element)
                current_span_text += element.get_text()

            elif isinstance(element, LTAnno):
                # LTAnno represents whitespace/newlines
                # Add it to the current span text
                current_span_text += element.get_text()

        # Finalize the last span
        if current_span_chars:
            span = self._create_span(
                current_span_chars,
                current_span_text,
                page_height
            )
            line.add_span(span)

        return line

    def _same_format(self, char1: LTChar, char2: LTChar) -> bool:
        """
        Check if two characters have the same formatting.

        Args:
            char1: First character
            char2: Second character

        Returns:
            True if characters have the same font, size, and style
        """
        return (
                char1.fontname == char2.fontname and
                abs(char1.size - char2.size) < 0.1  # Allow small floating point differences
        )

    def _create_span(
            self,
            chars: List[LTChar],
            text: str,
            page_height: float
    ) -> SpanData:
        """
        Create a SpanData object from a list of characters.

        Args:
            chars: List of LTChar objects with consistent formatting
            text: The text content (pre-extracted for efficiency)
            page_height: Height of the page (for coordinate conversion)

        Returns:
            SpanData with formatting information
        """
        if not chars:
            raise ValueError("Cannot create span from empty character list")

        # Use the first character as representative of the span
        first_char = chars[0]

        # Get font information and normalize the font name
        fontname = self._normalize_fontname(first_char.fontname)
        size = first_char.size

        # Determine flags based on font name and properties
        flags = self._determine_flags(fontname)
        char_flags = self._determine_char_flags(fontname)

        # Get position (use first character's position)
        # Note: pdfminer uses bottom-left origin,
        # We'll keep pdfminer's coordinates for now
        origin = (first_char.x0, first_char.y0)

        # Get color if available
        color = None
        if hasattr(first_char, 'graphicstate') and hasattr(first_char.graphicstate, 'scolor'):
            color = first_char.graphicstate.scolor

        return SpanData(
            text=text,
            font=fontname,
            size=size,
            flags=flags,
            char_flags=char_flags,
            origin=origin,
            color=color
        )

    def _normalize_fontname(self, fontname: str) -> str:
        """
        Normalize a PDF font name by stripping subset prefixes.

        PDF fonts often have prefixes like "PSVEWK+" which need to be removed
        to match the font names expected by parsing.py.

        Args:
            fontname: Raw font name from PDF (e.g., "PSVEWK+Brill-Roman")

        Returns:
            Normalized font name (e.g., "Brill-Roman")
        """
        # Strip subset prefix (e.g., "PSVEWK+")
        if '+' in fontname:
            fontname = fontname.split('+', 1)[1]

        return fontname

    def _determine_flags(self, fontname: str) -> int:
        """
        Determine font flags from font name.

        Flags are used by the existing parser to identify bold, italic, etc.
        Based on fitz conventions:
        - 0: normal
        - 2: italic
        - 20: bold
        - 21: bold + superscript
        - 22: bold + italic

        Args:
            fontname: Name of the font

        Returns:
            Integer flags
        """
        flags = 0

        fontname_lower = fontname.lower()

        # Check for bold
        if 'bold' in fontname_lower:
            flags |= 20

        # Check for italic
        if 'italic' in fontname_lower:
            if flags & 20:  # Already bold
                flags = 22  # Bold + italic
            else:
                flags = 2

        return flags

    def _determine_char_flags(self, fontname: str) -> int:
        """
        Determine character-level flags from font name.

        Args:
            fontname: Name of the font

        Returns:
            Integer character flags
        """
        # Based on the existing parser's expectations
        # Brill-Bold typically has char_flags=24
        fontname_lower = fontname.lower()

        if 'bold' in fontname_lower:
            return 24

        return 0
