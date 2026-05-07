"""Shared pytest fixtures."""
from __future__ import annotations
import sys
import os

# Make 'src' importable without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pikepdf
from pathlib import Path


@pytest.fixture
def minimal_pdf(tmp_path: Path) -> Path:
    """Create a minimal valid PDF with no metadata and return its path."""
    pdf_path = tmp_path / "test.pdf"
    pdf = pikepdf.Pdf.new()
    pdf.save(pdf_path)
    return pdf_path


@pytest.fixture
def pdf_with_metadata(tmp_path: Path) -> Path:
    """Create a PDF that already contains all 8 metadata fields."""
    pdf_path = tmp_path / "with_meta.pdf"
    pdf = pikepdf.Pdf.new()
    pdf.docinfo["/Title"] = "Test Title"
    pdf.docinfo["/Author"] = "Jane Doe"
    pdf.docinfo["/Subject"] = "Test Subject"
    pdf.docinfo["/Keywords"] = "alpha, beta"
    pdf.docinfo["/Creator"] = "TestCreator"
    pdf.docinfo["/Producer"] = "TestProducer"
    pdf.docinfo["/CreationDate"] = "D:20240115120000+00'00'"
    pdf.docinfo["/ModDate"] = "D:20240201083000+00'00'"
    pdf.save(pdf_path)
    return pdf_path


@pytest.fixture
def unicode_pdf(tmp_path: Path) -> Path:
    """Create a PDF with Unicode values in metadata."""
    pdf_path = tmp_path / "unicode.pdf"
    pdf = pikepdf.Pdf.new()
    pdf.docinfo["/Title"] = "Ünïcödé Títlé"
    pdf.docinfo["/Author"] = "Ångström, André"
    pdf.docinfo["/Subject"] = "日本語テスト"
    pdf.save(pdf_path)
    return pdf_path


@pytest.fixture
def readonly_pdf(tmp_path: Path) -> Path:
    """Create a read-only PDF."""
    pdf_path = tmp_path / "readonly.pdf"
    pdf = pikepdf.Pdf.new()
    pdf.docinfo["/Title"] = "Read Only"
    pdf.save(pdf_path)
    import stat
    pdf_path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return pdf_path
