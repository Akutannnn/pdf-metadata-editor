from __future__ import annotations
from pathlib import Path


def resolve_pdf_path(raw: str) -> Path:
    """Return a normalized absolute Path, stripping surrounding quotes."""
    stripped = raw.strip().strip('"').strip("'")
    return Path(stripped).resolve()


def is_pdf_file(path: Path) -> bool:
    return path.suffix.lower() == ".pdf"


def short_display_path(path: Path, max_len: int = 80) -> str:
    """Return a human-friendly path, ellipsising middle if too long."""
    s = str(path)
    if len(s) <= max_len:
        return s
    keep = (max_len - 3) // 2
    return s[:keep] + "…" + s[-keep:]


def same_filesystem(a: Path, b: Path) -> bool:
    """Return True when both paths live on the same filesystem."""
    try:
        import os
        return os.stat(a).st_dev == os.stat(b).st_dev
    except OSError:
        return a.drive.lower() == b.drive.lower()
