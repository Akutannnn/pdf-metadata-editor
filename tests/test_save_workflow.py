"""Tests for the atomic same-path save workflow."""
from __future__ import annotations
import os
import stat
import pytest
import pikepdf
from pathlib import Path
from unittest.mock import patch

from src.services.pdf_metadata_service import read_metadata, write_metadata
from src.services.file_service import validate_for_save
from src.models.metadata import PDFMetadata
from src.utils.error_utils import FileAccessError, SaveError


class TestAtomicSave:
    def test_original_path_unchanged(self, minimal_pdf: Path) -> None:
        original_path = str(minimal_pdf)
        write_metadata(minimal_pdf, PDFMetadata(Title="Atomic"))
        assert str(minimal_pdf) == original_path
        assert minimal_pdf.exists()

    def test_no_extra_files_after_save(self, minimal_pdf: Path) -> None:
        parent = minimal_pdf.parent
        before = set(parent.iterdir())
        write_metadata(minimal_pdf, PDFMetadata(Title="Clean"))
        after = set(parent.iterdir())
        assert after == before, f"Extra files created: {after - before}"

    def test_original_preserved_on_write_failure(self, minimal_pdf: Path) -> None:
        original_size = minimal_pdf.stat().st_size
        original_data = minimal_pdf.read_bytes()

        with patch(
            "src.services.pdf_metadata_service.pikepdf.open",
            side_effect=RuntimeError("Simulated failure"),
        ):
            with pytest.raises(Exception):
                write_metadata(minimal_pdf, PDFMetadata(Title="Fail"))

        assert minimal_pdf.exists()
        assert minimal_pdf.read_bytes() == original_data

    def test_temp_file_cleaned_on_failure(self, minimal_pdf: Path) -> None:
        parent = minimal_pdf.parent

        with patch(
            "src.services.pdf_metadata_service.pikepdf.open",
            side_effect=RuntimeError("Simulated failure"),
        ):
            with pytest.raises(Exception):
                write_metadata(minimal_pdf, PDFMetadata(Title="Fail"))

        temp_files = list(parent.glob(".pme_*"))
        assert temp_files == []

    def test_valid_pdf_after_save(self, minimal_pdf: Path) -> None:
        write_metadata(minimal_pdf, PDFMetadata(Title="Valid PDF"))
        with pikepdf.open(minimal_pdf) as pdf:
            assert pdf.docinfo.get("/Title") is not None

    def test_multiple_saves(self, minimal_pdf: Path) -> None:
        for i in range(5):
            write_metadata(minimal_pdf, PDFMetadata(Title=f"Save {i}"))
        result = read_metadata(minimal_pdf)
        assert result.Title == "Save 4"


class TestFileValidation:
    def test_validates_nonexistent_file(self, tmp_path: Path) -> None:
        ghost = tmp_path / "ghost.pdf"
        with pytest.raises(FileAccessError):
            validate_for_save(ghost)

    def test_validates_non_pdf(self, tmp_path: Path) -> None:
        txt = tmp_path / "doc.txt"
        txt.write_text("hello")
        from src.utils.error_utils import InvalidPDFError, AppError
        with pytest.raises(AppError):
            validate_for_save(txt)

    @pytest.mark.skipif(os.name == "nt", reason="chmod read-only less reliable on Windows CI")
    def test_validates_readonly_file(self, readonly_pdf: Path) -> None:
        with pytest.raises(FileAccessError):
            validate_for_save(readonly_pdf)


class TestMetadataRoundtrip:
    def test_full_roundtrip(self, minimal_pdf: Path) -> None:
        meta_in = PDFMetadata(
            Title="Full Roundtrip Title",
            Author="Jane Smith",
            Subject="Test subject text",
            Keywords="roundtrip, test, pdf",
            Creator="TestCreatorApp",
            Producer="TestProducerLib",
            CreationDate="D:20240115120000+00'00'",
            ModDate="D:20240201083000+00'00'",
        )
        write_metadata(minimal_pdf, meta_in)
        meta_out = read_metadata(minimal_pdf)

        assert meta_out.Title == meta_in.Title
        assert meta_out.Author == meta_in.Author
        assert meta_out.Subject == meta_in.Subject
        assert meta_out.Keywords == meta_in.Keywords
        assert meta_out.Creator == meta_in.Creator
        assert meta_out.Producer == meta_in.Producer

    def test_unicode_roundtrip(self, minimal_pdf: Path) -> None:
        meta_in = PDFMetadata(
            Title="Titre en français",
            Author="Ångström, André",
            Subject="日本語テスト",
            Keywords="ünïcödé, têst",
        )
        write_metadata(minimal_pdf, meta_in)
        meta_out = read_metadata(minimal_pdf)
        assert meta_out.Title == meta_in.Title
        assert meta_out.Author == meta_in.Author
        assert meta_out.Subject == meta_in.Subject

    def test_empty_metadata_roundtrip(self, minimal_pdf: Path) -> None:
        write_metadata(minimal_pdf, PDFMetadata())
        meta_out = read_metadata(minimal_pdf)
        assert meta_out.Title is None
        assert meta_out.Author is None
