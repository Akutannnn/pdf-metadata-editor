"""PDF date string parsing and normalization.

PDF date format: D:YYYYMMDDHHmmSSOHH'mm'
  where O is +, -, or Z for UTC offset.

We accept friendly user input:
  YYYY-MM-DD
  YYYY-MM-DD HH:MM:SS
  YYYY/MM/DD
  MM/DD/YYYY
  DD.MM.YYYY
  ISO 8601 with T separator
"""
from __future__ import annotations
import re
from datetime import datetime, timezone, timedelta
from typing import Optional


_PDF_DATE_RE = re.compile(
    r"^D:(\d{4})(\d{2})(\d{2})"
    r"(\d{2})(\d{2})(\d{2})"
    r"([Z+\-])(\d{2})'?(\d{2})'?$",
    re.ASCII,
)
_PDF_DATE_SHORT_RE = re.compile(r"^D:(\d{4})(\d{2})(\d{2})", re.ASCII)

_FRIENDLY_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y",
    "%d.%m.%Y %H:%M:%S",
    "%d.%m.%Y",
]


def parse_pdf_date(date_str: str) -> Optional[datetime]:
    """Parse a PDF date string into a timezone-aware datetime."""
    if not date_str:
        return None

    s = date_str.strip()

    m = _PDF_DATE_RE.match(s)
    if m:
        y, mo, d, hh, mm, ss, sign, oh, om = m.groups()
        try:
            base = datetime(int(y), int(mo), int(d), int(hh), int(mm), int(ss))
        except ValueError:
            return None

        offset_minutes = int(oh) * 60 + int(om)
        if sign == "Z" or offset_minutes == 0:
            tz = timezone.utc
        elif sign == "+":
            tz = timezone(timedelta(minutes=offset_minutes))
        else:
            tz = timezone(timedelta(minutes=-offset_minutes))
        return base.replace(tzinfo=tz)

    m = _PDF_DATE_SHORT_RE.match(s)
    if m:
        y, mo, d = m.groups()
        try:
            return datetime(int(y), int(mo), int(d), tzinfo=timezone.utc)
        except ValueError:
            return None

    return None


def format_pdf_date(dt: datetime) -> str:
    """Encode a datetime as a PDF date string."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    offset = dt.utcoffset()
    total_seconds = int(offset.total_seconds()) if offset else 0
    sign = "+" if total_seconds >= 0 else "-"
    abs_sec = abs(total_seconds)
    oh, om = divmod(abs_sec // 60, 60)

    return (
        f"D:{dt.year:04d}{dt.month:02d}{dt.day:02d}"
        f"{dt.hour:02d}{dt.minute:02d}{dt.second:02d}"
        f"{sign}{oh:02d}'{om:02d}'"
    )


def display_date(date_str: str) -> str:
    """Convert a PDF date to a friendly display string for the UI."""
    dt = parse_pdf_date(date_str)
    if dt is None:
        return date_str
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
        return dt.strftime("%Y-%m-%d")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def normalize_user_date(raw: str) -> Optional[str]:
    """
    Accept a human-typed date string and return a PDF-format date string,
    or None if the input is empty, or raise ValueError if it can't be parsed.
    """
    raw = raw.strip()
    if not raw:
        return None

    # Already a PDF date?
    if raw.startswith("D:") and parse_pdf_date(raw) is not None:
        return raw

    for fmt in _FRIENDLY_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
            dt = dt.replace(tzinfo=timezone.utc)
            return format_pdf_date(dt)
        except ValueError:
            continue

    raise ValueError(
        f"Cannot parse date: {raw!r}\n"
        "Expected format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"
    )


def is_valid_user_date(raw: str) -> bool:
    """Return True when the string is empty or parseable as a date."""
    if not raw.strip():
        return True
    try:
        normalize_user_date(raw)
        return True
    except ValueError:
        return False
