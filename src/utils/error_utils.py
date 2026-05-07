from __future__ import annotations
import errno
import os
from pathlib import Path


class AppError(Exception):
    """Application-level error with a human-friendly message."""

    def __init__(self, message: str, detail: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def __str__(self) -> str:
        if self.detail:
            return f"{self.message}\n\n{self.detail}"
        return self.message


class FileAccessError(AppError):
    pass


class InvalidPDFError(AppError):
    pass


class SaveError(AppError):
    pass


def classify_os_error(exc: OSError, path: Path) -> AppError:
    code = exc.errno
    name = str(path)

    if code == errno.ENOENT:
        return FileAccessError(
            "File not found.",
            f"The file could not be located:\n{name}",
        )
    if code == errno.EACCES:
        return FileAccessError(
            "Permission denied.",
            f"You do not have permission to access this file:\n{name}\n\n"
            "Check that the file is not read-only and that you have write access.",
        )
    if code == errno.ENOTEMPTY or code == errno.EEXIST:
        return SaveError(
            "Could not replace the original file.",
            f"A conflict prevented the save operation on:\n{name}",
        )
    # Windows sharing violation (winerror 32)
    if hasattr(exc, "winerror") and exc.winerror == 32:
        return FileAccessError(
            "File is open in another application.",
            f"Close any other programs that have this PDF open, then try again:\n{name}",
        )
    return SaveError(
        "An unexpected file error occurred.",
        f"{type(exc).__name__}: {exc}\n\nPath: {name}",
    )


def is_file_locked(path: Path) -> bool:
    """Quick check: try to open the file for exclusive write access."""
    try:
        with open(path, "r+b"):
            return False
    except OSError:
        return True
