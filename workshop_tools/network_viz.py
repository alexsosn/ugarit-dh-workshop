"""Shared access to the vendored browser network renderer."""

from pathlib import Path


_VIS_NETWORK_PATH = (
    Path(__file__).resolve().parent / "vendor/vis-network/vis-network.min.js"
)


def vis_network_javascript() -> str:
    """Return the pinned vis-network source for inline, offline notebook use."""
    return _VIS_NETWORK_PATH.read_text(encoding="utf-8")
