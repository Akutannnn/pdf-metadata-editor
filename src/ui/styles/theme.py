"""Application QSS stylesheet and palette helpers."""
from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# Colour tokens
# ──────────────────────────────────────────────────────────────────────────────
BG_APP      = "#F7F8FA"
BG_SURFACE  = "#FFFFFF"
BG_HOVER    = "#F1F3F7"
BG_MUTED    = "#F9FAFB"

BORDER      = "#DDE1EA"
BORDER_FOCUS= "#3B82F6"
BORDER_ERROR= "#EF4444"

TEXT_PRIMARY= "#111827"
TEXT_LABEL  = "#374151"
TEXT_MUTED  = "#6B7280"
TEXT_HELPER = "#9CA3AF"

ACCENT      = "#2563EB"
ACCENT_HOVER= "#1D4ED8"
ACCENT_PRESS= "#1E40AF"
ACCENT_DISABLED = "#93C5FD"

DANGER      = "#DC2626"
SUCCESS     = "#059669"

SCROLLBAR_TRACK  = "#EAEEF3"
SCROLLBAR_THUMB  = "#C4CDD8"
SCROLLBAR_HOVER  = "#9AAAB8"


def build_stylesheet() -> str:
    return f"""
/* ── Window & surfaces ─────────────────────────────────────────── */
QMainWindow, QDialog {{
    background-color: {BG_APP};
}}

QWidget {{
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: {TEXT_PRIMARY};
}}

QWidget#centralWidget {{
    background-color: {BG_APP};
}}

QWidget#fileHeader {{
    background-color: {BG_SURFACE};
    border-bottom: 1px solid {BORDER};
}}

QWidget#formScroll {{
    background-color: transparent;
    border: none;
}}

QWidget#formContainer {{
    background-color: transparent;
}}

QWidget#actionBar {{
    background-color: {BG_SURFACE};
    border-top: 1px solid {BORDER};
}}

/* ── Labels ────────────────────────────────────────────────────── */
QLabel#appTitle {{
    font-size: 15px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

QLabel#filePath {{
    font-size: 11px;
    color: {TEXT_MUTED};
}}

QLabel#fieldLabel {{
    font-size: 12px;
    font-weight: 600;
    color: {TEXT_LABEL};
}}

QLabel#helperText {{
    font-size: 11px;
    color: {TEXT_HELPER};
}}

QLabel#errorText {{
    font-size: 11px;
    color: {DANGER};
}}

QLabel#noFileLabel {{
    font-size: 14px;
    color: {TEXT_MUTED};
}}

QLabel#savedLabel {{
    font-size: 12px;
    color: {SUCCESS};
    font-weight: 500;
}}

/* ── Inputs ────────────────────────────────────────────────────── */
QLineEdit {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 11px;
    font-size: 13px;
    color: {TEXT_PRIMARY};
    selection-background-color: #DBEAFE;
    selection-color: #1E40AF;
}}

QLineEdit:focus {{
    border-color: {BORDER_FOCUS};
    background-color: {BG_SURFACE};
}}

QLineEdit:disabled {{
    background-color: {BG_MUTED};
    color: {TEXT_MUTED};
}}

QLineEdit[invalid="true"] {{
    border-color: {BORDER_ERROR};
    background-color: #FEF2F2;
}}

QTextEdit {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 11px;
    font-size: 13px;
    color: {TEXT_PRIMARY};
    selection-background-color: #DBEAFE;
    selection-color: #1E40AF;
}}

QTextEdit:focus {{
    border-color: {BORDER_FOCUS};
}}

/* ── Buttons ───────────────────────────────────────────────────── */
QPushButton {{
    border-radius: 6px;
    padding: 7px 20px;
    font-size: 13px;
    font-weight: 500;
    min-width: 80px;
}}

QPushButton#saveButton {{
    background-color: {ACCENT};
    color: #FFFFFF;
    border: none;
}}

QPushButton#saveButton:hover {{
    background-color: {ACCENT_HOVER};
}}

QPushButton#saveButton:pressed {{
    background-color: {ACCENT_PRESS};
}}

QPushButton#saveButton:disabled {{
    background-color: {ACCENT_DISABLED};
    color: #FFFFFF;
}}

QPushButton#resetButton {{
    background-color: {BG_SURFACE};
    color: {TEXT_LABEL};
    border: 1px solid {BORDER};
}}

QPushButton#resetButton:hover {{
    background-color: {BG_HOVER};
}}

QPushButton#resetButton:pressed {{
    background-color: {BORDER};
}}

QPushButton#resetButton:disabled {{
    color: {TEXT_HELPER};
    border-color: #EAEDF2;
}}

QPushButton#cancelButton {{
    background-color: transparent;
    color: {TEXT_MUTED};
    border: none;
}}

QPushButton#cancelButton:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_LABEL};
}}

QPushButton#openFileButton {{
    background-color: {ACCENT};
    color: #FFFFFF;
    border: none;
    padding: 9px 24px;
    font-size: 14px;
}}

QPushButton#openFileButton:hover {{
    background-color: {ACCENT_HOVER};
}}

/* ── Scroll area ───────────────────────────────────────────────── */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    width: 8px;
    background-color: transparent;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background-color: {SCROLLBAR_THUMB};
    border-radius: 4px;
    min-height: 28px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {SCROLLBAR_HOVER};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
}}

/* ── Separator ─────────────────────────────────────────────────── */
QFrame[frameShape="4"],
QFrame[frameShape="HLine"] {{
    color: {BORDER};
    max-height: 1px;
}}

/* ── Status bar ────────────────────────────────────────────────── */
QStatusBar {{
    background-color: {BG_APP};
    border-top: 1px solid {BORDER};
    font-size: 11px;
    color: {TEXT_MUTED};
}}

/* ── Tooltip ───────────────────────────────────────────────────── */
QToolTip {{
    background-color: #1F2937;
    color: #F9FAFB;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}}

/* ── Message box ───────────────────────────────────────────────── */
QMessageBox {{
    background-color: {BG_SURFACE};
}}
"""
