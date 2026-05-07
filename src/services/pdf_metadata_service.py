"""Core PDF metadata read/write via pikepdf.

Save strategy
─────────────
1. Write the modified PDF to a temp file in the same directory as the
   original (guarantees same filesystem → cheap rename).
2. Use os.replace() for an atomic overwrite of the original path.
3. If anything fails the temp file is removed and the original is intact.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

import pikepdf

from ..models.metadata import PDFMetadata
from ..utils.error_utils import (
    AppError,
    FileAccessError,
    InvalidPDFError,
    SaveError,
    classify_os_error,
)
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

# Docinfo key → PDFMetadata field name
_DOCINFO_MAP: dict[str, str] = {
    "/Title":        "Title",
    "/Author":       "Author",
    "/Subject":      "Subject",
    "/Keywords":     "Keywords",
    "/Creator":      "Creator",
    "/Producer":     "Producer",
    "/CreationDate": "CreationDate",
    "/ModDate":      "ModDate",
}

_FIELD_TO_DOCINFO = {v: k for k, v in _DOCINFO_MAP.items()}


def read_metadata(path: Path) -> PDFMetadata:
    """Read docinfo metadata from *path* and return a PDFMetadata instance."""
    logger.debug("Reading metadata from %s", path)
    try:
        with pikepdf.open(path) as pdf:
            return _extract_metadata(pdf)
    except pikepdf.PasswordError as exc:
        raise FileAccessError(
            "PDF is password-protected.",
            f"This PDF requires a password to open:\n{path}",
        ) from exc
    except pikepdf.PdfError as exc:
        raise InvalidPDFError(
            "Cannot parse PDF.",
            f"pikepdf reported:\n{exc}\n\nFile: {path}",
        ) from exc
    except OSError as exc:
        raise classify_os_error(exc, path) from exc


def write_metadata(path: Path, metadata: PDFMetadata) -> None:
    """Write *metadata* back to *path* using a safe atomic temp-file swap."""
    logger.debug("Writing metadata to %s", path)

    tmp_path: Optional[Path] = None
    try:
        fd, tmp_str = tempfile.mkstemp(
            dir=path.parent,
            suffix=".tmp",
            prefix=".pme_",
        )
        os.close(fd)
        tmp_path = Path(tmp_str)

        with pikepdf.open(path) as pdf:
            _apply_metadata(pdf, metadata)
            pdf.save(tmp_path)

        os.replace(tmp_path, path)
        logger.info("Metadata saved to %s", path)

    except pikepdf.PasswordError as exc:
        _cleanup(tmp_path)
        raise FileAccessError(
            "PDF is password-protected.",
            f"Cannot write to a password-protected PDF:\n{path}",
        ) from exc
    except pikepdf.PdfError as exc:
        _cleanup(tmp_path)
        raise SaveError(
            "Failed to write PDF.",
            f"pikepdf reported:\n{exc}\n\nFile: {path}",
        ) from exc
    except OSError as exc:
        _cleanup(tmp_path)
        raise classify_os_error(exc, path) from exc
    except Exception as exc:
        _cleanup(tmp_path)
        raise SaveError(
            "Unexpected error while saving.",
            f"{type(exc).__name__}: {exc}",
        ) from exc


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _extract_metadata(pdf: pikepdf.Pdf) -> PDFMetadata:
    data: dict[str, Optional[str]] = {}
    docinfo = pdf.docinfo

    for pdf_key, field_name in _DOCINFO_MAP.items():
        raw = docinfo.get(pdf_key)
        if raw is None:
            data[field_name] = None
        else:
            s = str(raw).strip()
            data[field_name] = s if s else None

    return PDFMetadata.from_dict(data)


def _apply_metadata(pdf: pikepdf.Pdf, metadata: PDFMetadata) -> None:
    for field_name, pdf_key in _FIELD_TO_DOCINFO.items():
        value: Optional[str] = getattr(metadata, field_name, None)
        if value and value.strip():
            pdf.docinfo[pdf_key] = pikepdf.String(value.strip())
        elif pdf_key in pdf.docinfo:
            del pdf.docinfo[pdf_key]

    # Keep XMP and docinfo in sync where pikepdf supports it.
    try:
        with pdf.open_metadata(set_pikepdf_as_editor=False) as xmp:
            _sync_xmp(xmp, metadata)
    except Exception as exc:
        # XMP sync is best-effort; docinfo update is the authoritative path.
        logger.warning("XMP sync skipped: %s", exc)


def _sync_xmp(xmp: pikepdf.models.PdfMetadata, meta: PDFMetadata) -> None:
    """Update common XMP fields to match docinfo values."""
    _xmp_set(xmp, "dc:title", meta.Title)
    _xmp_set(xmp, "dc:creator", meta.Author)
    _xmp_set(xmp, "dc:description", meta.Subject)
    _xmp_set(xmp, "pdf:Keywords", meta.Keywords)
    _xmp_set(xmp, "xmp:CreatorTool", meta.Creator)
    _xmp_set(xmp, "pdf:Producer", meta.Producer)
    _xmp_set(xmp, "xmp:CreateDate", meta.CreationDate)
    _xmp_set(xmp, "xmp:ModifyDate", meta.ModDate)


def _xmp_set(xmp: pikepdf.models.PdfMetadata, key: str, value: Optional[str]) -> None:
    if value and value.strip():
        try:
            xmp[key] = value.strip()
        except Exception:
            pass
    else:
        try:
            del xmp[key]
        except (KeyError, Exception):
            pass


def _cleanup(tmp_path: Optional[Path]) -> None:
    if tmp_path is not None and tmp_path.exists():
        try:
            tmp_path.unlink()
        except OSError:
            pass
