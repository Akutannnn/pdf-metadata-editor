"""Tests for metadata read/write mapping via pdf_metadata_service."""
from __future__ import annotations
import pytest
import pikepdf
from pathlib import Path

from src.services.pdf_metadata_service import read_metadata, write_metadata
from src.models.metadata import PDFMetadata


class TestReadMetadata:
    def test_reads_all_fields(self, pdf_with_metadata: Path) -> None:
        meta = read_metadata(pdf_with_metadata)
        assert meta.Title == "Test Title"
        assert meta.Author == "Jane Doe"
        assert meta.Subject == "Test Subject"
        assert meta.Keywords == "alpha, beta"
        assert meta.Creator == "TestCreator"
        assert meta.Producer == "TestProducer"
        assert meta.CreationDate == "D:20240115120000+00'00'"
        assert meta.ModDate == "D:20240201083000+00'00'"

    def test_returns_none_for_missing_fields(self, minimal_pdf: Path) -> None:
        meta = read_metadata(minimal_pdf)
        assert meta.Title is None
        assert meta.Author is None
        assert meta.Subject is None
        assert meta.Keywords is None
        assert meta.Creator is None
        assert meta.Producer is None
        assert meta.CreationDate is None
        assert meta.ModDate is None

    def test_reads_unicode_values(self, unicode_pdf: Path) -> None:
        meta = read_metadata(unicode_pdf)
        assert meta.Title == "Ünïcödé Títlé"
        assert meta.Author == "Ångström, André"
        assert meta.Subject == "日本語テスト"

    def test_raises_on_invalid_pdf(self, tmp_path: Path) -> None:
        from src.utils.error_utils import InvalidPDFError, FileAccessError
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"this is not a pdf")
        with pytest.raises((InvalidPDFError, FileAccessError, Exception)):
            read_metadata(bad)


class TestWriteMetadata:
    def test_writes_all_fields(self, minimal_pdf: Path) -> None:
        meta = PDFMetadata(
            Title="New Title",
            Author="New Author",
            Subject="New Subject",
            Keywords="x, y",
            Creator="CreatorApp",
            Producer="ProducerLib",
            CreationDate="D:20240115000000+00'00'",
            ModDate="D:20240201000000+00'00'",
        )
        write_metadata(minimal_pdf, meta)
        result = read_metadata(minimal_pdf)
        assert result.Title == "New Title"
        assert result.Author == "New Author"
        assert result.Subject == "New Subject"
        assert result.Keywords == "x, y"
        assert result.Creator == "CreatorApp"

    def test_overwrites_existing_metadata(self, pdf_with_metadata: Path) -> None:
        meta = PDFMetadata(Title="Overwritten Title", Author="New Author")
        write_metadata(pdf_with_metadata, meta)
        result = read_metadata(pdf_with_metadata)
        assert result.Title == "Overwritten Title"
        assert result.Author == "New Author"

    def test_clears_field_when_none(self, pdf_with_metadata: Path) -> None:
        meta = PDFMetadata(Title=None, Author="Keep Author")
        write_metadata(pdf_with_metadata, meta)
        result = read_metadata(pdf_with_metadata)
        assert result.Title is None
        assert result.Author == "Keep Author"

    def test_preserves_pdf_content(self, minimal_pdf: Path) -> None:
        """Writing metadata must not corrupt the PDF structure."""
        write_metadata(minimal_pdf, PDFMetadata(Title="Safe"))
        with pikepdf.open(minimal_pdf) as pdf:
            assert pdf.docinfo["/Title"] == "Safe"

    def test_writes_unicode_metadata(self, minimal_pdf: Path) -> None:
        meta = PDFMetadata(Title="日本語", Author="Ångström")
        write_metadata(minimal_pdf, meta)
        result = read_metadata(minimal_pdf)
        assert result.Title == "日本語"
        assert result.Author == "Ångström"

    def test_same_path_after_save(self, minimal_pdf: Path) -> None:
        """The original file path must still exist and be valid after save."""
        original_path = minimal_pdf
        write_metadata(minimal_pdf, PDFMetadata(Title="Same Path"))
        assert original_path.exists()
        result = read_metadata(original_path)
        assert result.Title == "Same Path"

    def test_no_temp_file_left_after_save(self, minimal_pdf: Path) -> None:
        """No .pme_ temp files should remain after a successful save."""
        write_metadata(minimal_pdf, PDFMetadata(Title="Clean"))
        temp_files = list(minimal_pdf.parent.glob(".pme_*"))
        assert temp_files == []

    def test_empty_string_treated_as_none(self, pdf_with_metadata: Path) -> None:
        meta = PDFMetadata(Title="   ", Author="Keep")
        write_metadata(pdf_with_metadata, meta)
        result = read_metadata(pdf_with_metadata)
        assert result.Title is None

    def test_path_with_spaces(self, tmp_path: Path) -> None:
        spaced = tmp_path / "my document with spaces.pdf"
        pdf = pikepdf.Pdf.new()
        pdf.save(spaced)
        write_metadata(spaced, PDFMetadata(Title="Spaces OK"))
        result = read_metadata(spaced)
        assert result.Title == "Spaces OK"
