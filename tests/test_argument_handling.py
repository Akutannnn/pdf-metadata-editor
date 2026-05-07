"""Tests for argument parsing and path resolution."""
from __future__ import annotations
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

from src.utils.path_utils import resolve_pdf_path, is_pdf_file, short_display_path


class TestResolvePdfPath:
    def test_plain_path(self, tmp_path: Path) -> None:
        f = tmp_path / "sample.pdf"
        f.touch()
        result = resolve_pdf_path(str(f))
        assert result == f.resolve()

    def test_path_with_spaces(self, tmp_path: Path) -> None:
        f = tmp_path / "my file with spaces.pdf"
        f.touch()
        result = resolve_pdf_path(str(f))
        assert result == f.resolve()

    def test_quoted_path(self, tmp_path: Path) -> None:
        f = tmp_path / "quoted.pdf"
        f.touch()
        quoted = f'"{f}"'
        result = resolve_pdf_path(quoted)
        assert result == f.resolve()

    def test_single_quoted_path(self, tmp_path: Path) -> None:
        f = tmp_path / "single.pdf"
        f.touch()
        result = resolve_pdf_path(f"'{f}'")
        assert result == f.resolve()

    def test_unicode_filename(self, tmp_path: Path) -> None:
        f = tmp_path / "日本語_test.pdf"
        f.touch()
        result = resolve_pdf_path(str(f))
        assert result.name == "日本語_test.pdf"


class TestIsPdfFile:
    def test_pdf_extension(self) -> None:
        assert is_pdf_file(Path("document.pdf")) is True
        assert is_pdf_file(Path("DOCUMENT.PDF")) is True

    def test_non_pdf(self) -> None:
        assert is_pdf_file(Path("document.docx")) is False
        assert is_pdf_file(Path("document.txt")) is False
        assert is_pdf_file(Path("document")) is False


class TestShortDisplayPath:
    def test_short_path_unchanged(self) -> None:
        p = Path("C:/short/path.pdf")
        assert short_display_path(p) == str(p)

    def test_long_path_truncated(self) -> None:
        p = Path("C:/" + "a" * 100 + "/file.pdf")
        result = short_display_path(p, max_len=40)
        assert len(result) <= 43  # allow for ellipsis
        assert "…" in result


class TestParseArgument:
    def test_no_args_returns_none(self) -> None:
        with patch.object(sys, "argv", ["main.py"]):
            from src.app import parse_pdf_argument
            assert parse_pdf_argument() is None

    def test_single_path_arg(self, tmp_path: Path) -> None:
        f = tmp_path / "test.pdf"
        f.touch()
        with patch.object(sys, "argv", ["main.py", str(f)]):
            from src.app import parse_pdf_argument
            result = parse_pdf_argument()
            assert result is not None
            assert result.name == "test.pdf"

    def test_flag_arg_returns_none(self) -> None:
        with patch.object(sys, "argv", ["main.py", "--debug"]):
            from src.app import parse_pdf_argument
            result = parse_pdf_argument()
            assert result is None

    def test_path_with_spaces_in_arg(self, tmp_path: Path) -> None:
        f = tmp_path / "my document.pdf"
        f.touch()
        with patch.object(sys, "argv", ["main.py", str(f)]):
            from src.app import parse_pdf_argument
            result = parse_pdf_argument()
            assert result is not None
            assert "my document" in result.name
