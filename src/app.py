"""Application bootstrap: argument parsing, validation, Qt setup."""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication, QMessageBox

from .constants import APP_NAME, APP_VERSION, ORG_NAME
from .ui.main_window import MainWindow
from .ui.styles.theme import build_stylesheet
from .utils.logging_utils import get_logger, setup_logging
from .utils.path_utils import resolve_pdf_path

logger = get_logger(__name__)


def parse_pdf_argument() -> Optional[Path]:
    """Return the PDF path from argv[1], or None if none was provided."""
    args = sys.argv[1:]
    if not args:
        return None

    raw = args[0]
    # PyInstaller may pass extra flags; skip anything that looks like a flag.
    if raw.startswith("--"):
        return None

    try:
        return resolve_pdf_path(raw)
    except Exception as exc:
        logger.warning("Could not resolve path %r: %s", raw, exc)
        return None


def run() -> int:
    """Entry point. Returns the process exit code."""
    setup_logging(debug="--debug" in sys.argv)
    logger.info("%s %s starting", APP_NAME, APP_VERSION)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(ORG_NAME)

    # Apply the QSS theme globally
    app.setStyleSheet(build_stylesheet())

    pdf_path = parse_pdf_argument()
    if pdf_path is not None:
        logger.info("Opening file: %s", pdf_path)
        # Basic sanity check before handing to the window
        if not pdf_path.exists():
            _fatal_error(
                app,
                "File not found.",
                f"The file does not exist:\n{pdf_path}",
            )
            return 1

    window = MainWindow(pdf_path=pdf_path)
    window.show()

    return app.exec()


def _fatal_error(app: QApplication, title: str, message: str) -> None:
    """Show a standalone error dialog before the main window opens."""
    dlg = QMessageBox()
    dlg.setWindowTitle(APP_NAME)
    dlg.setIcon(QMessageBox.Icon.Critical)
    dlg.setText(title)
    dlg.setInformativeText(message)
    dlg.exec()
