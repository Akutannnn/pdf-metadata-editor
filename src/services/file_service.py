"""File validation checks before opening or saving a PDF."""
from __future__ import annotations
import os
from pathlib import Path

from ..utils.error_utils import AppError, FileAccessError, InvalidPDFError
from ..utils.path_utils import is_pdf_file
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

_PDF_MAGIC = b"%PDF-"


def validate_for_open(path: Path) -> None:
    """Raise AppError if the file cannot be opened for reading."""
    if not path.exists():
        raise FileAccessError(
            "File not found.",
            f"No file exists at:\n{path}",
        )
    if not path.is_file():
        raise FileAccessError(
            "Not a file.",
            f"The path does not point to a regular file:\n{path}",
        )
    if not is_pdf_file(path):
        raise InvalidPDFError(
            "Not a PDF file.",
            f"The selected file does not have a .pdf extension:\n{path}",
        )
    if not os.access(path, os.R_OK):
        raise FileAccessError(
            "Permission denied.",
            f"You do not have read access to:\n{path}",
        )
    _check_pdf_magic(path)


def validate_for_save(path: Path) -> None:
    """Raise AppError if the file cannot be written."""
    validate_for_open(path)
    if not os.access(path, os.W_OK):
        raise FileAccessError(
            "File is read-only.",
            f"You do not have write permission for:\n{path}\n\n"
            "Right-click the file → Properties → uncheck Read-only.",
        )
    parent = path.parent
    if not os.access(parent, os.W_OK):
        raise FileAccessError(
            "Cannot write to folder.",
            f"You do not have write permission for:\n{parent}",
        )


def _check_pdf_magic(path: Path) -> None:
    try:
        with open(path, "rb") as fh:
            header = fh.read(5)
    except OSError as exc:
        raise FileAccessError(
            "Cannot read file.",
            str(exc),
        ) from exc

    if header != _PDF_MAGIC:
        raise InvalidPDFError(
            "Invalid PDF file.",
            f"The file does not appear to be a valid PDF:\n{path}\n\n"
            f"Expected header %PDF-, got: {header!r}",
        )
