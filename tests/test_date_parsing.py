"""Tests for date_utils: PDF date parsing and normalization."""
from __future__ import annotations
import pytest
from datetime import datetime, timezone, timedelta

from src.utils.date_utils import (
    display_date,
    format_pdf_date,
    is_valid_user_date,
    normalize_user_date,
    parse_pdf_date,
)


class TestParsePdfDate:
    def test_full_utc_date(self) -> None:
        dt = parse_pdf_date("D:20240115120000+00'00'")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 12
        assert dt.minute == 0
        assert dt.second == 0

    def test_positive_offset(self) -> None:
        dt = parse_pdf_date("D:20240115120000+05'30'")
        assert dt is not None
        assert dt.utcoffset() == timedelta(hours=5, minutes=30)

    def test_negative_offset(self) -> None:
        dt = parse_pdf_date("D:20240115120000-08'00'")
        assert dt is not None
        assert dt.utcoffset() == timedelta(hours=-8)

    def test_z_timezone(self) -> None:
        dt = parse_pdf_date("D:20240115120000Z00'00'")
        assert dt is not None
        assert dt.tzinfo == timezone.utc

    def test_short_date(self) -> None:
        dt = parse_pdf_date("D:20240115")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15

    def test_empty_string_returns_none(self) -> None:
        assert parse_pdf_date("") is None
        assert parse_pdf_date("   ") is None

    def test_invalid_string_returns_none(self) -> None:
        assert parse_pdf_date("not a date") is None
        assert parse_pdf_date("2024-01-15") is None


class TestFormatPdfDate:
    def test_roundtrip(self) -> None:
        original = "D:20240115120000+00'00'"
        dt = parse_pdf_date(original)
        assert dt is not None
        reformatted = format_pdf_date(dt)
        assert reformatted == original

    def test_naive_datetime_treated_as_utc(self) -> None:
        dt = datetime(2024, 6, 1, 10, 30, 0)
        result = format_pdf_date(dt)
        assert result.startswith("D:20240601103000")

    def test_format_structure(self) -> None:
        dt = datetime(2024, 3, 15, 8, 5, 9, tzinfo=timezone.utc)
        result = format_pdf_date(dt)
        assert result == "D:20240315080509+00'00'"


class TestNormalizeUserDate:
    @pytest.mark.parametrize("raw,expected_start", [
        ("2024-01-15", "D:20240115"),
        ("2024-01-15 12:30:00", "D:20240115123000"),
        ("2024/01/15", "D:20240115"),
        ("01/15/2024", "D:20240115"),
        ("15.01.2024", "D:20240115"),
        ("2024-01-15T08:00:00", "D:20240115080000"),
    ])
    def test_various_formats(self, raw: str, expected_start: str) -> None:
        result = normalize_user_date(raw)
        assert result is not None
        assert result.startswith(expected_start)

    def test_empty_returns_none(self) -> None:
        assert normalize_user_date("") is None
        assert normalize_user_date("   ") is None

    def test_already_pdf_date_passthrough(self) -> None:
        pdf_date = "D:20240115120000+00'00'"
        result = normalize_user_date(pdf_date)
        assert result == pdf_date

    def test_invalid_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            normalize_user_date("not-a-date")
        with pytest.raises(ValueError):
            normalize_user_date("32/13/9999")


class TestIsValidUserDate:
    def test_empty_is_valid(self) -> None:
        assert is_valid_user_date("") is True
        assert is_valid_user_date("   ") is True

    def test_valid_dates(self) -> None:
        assert is_valid_user_date("2024-01-15") is True
        assert is_valid_user_date("2024-01-15 12:00:00") is True

    def test_invalid_dates(self) -> None:
        assert is_valid_user_date("not a date") is False
        assert is_valid_user_date("99/99/9999") is False


class TestDisplayDate:
    def test_date_only(self) -> None:
        result = display_date("D:20240115000000+00'00'")
        assert result == "2024-01-15"

    def test_with_time(self) -> None:
        result = display_date("D:20240115123045+00'00'")
        assert result == "2024-01-15 12:30:45"

    def test_unparseable_returns_original(self) -> None:
        raw = "D:badvalue"
        assert display_date(raw) == raw
