"""Single metadata form field: label + input + optional helper text."""
from __future__ import annotations
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...utils.date_utils import is_valid_user_date


class MetadataField(QWidget):
    """A labeled form row for one metadata field."""

    value_changed = Signal()

    def __init__(
        self,
        key: str,
        label: str,
        placeholder: str = "",
        multiline: bool = False,
        is_date: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.key = key
        self._is_date = is_date
        self._multiline = multiline
        self._original_value: str = ""

        self._build_ui(label, placeholder, multiline, is_date)
        self._connect_signals()

    # ── Public API ──────────────────────────────────────────────────────────

    def value(self) -> str:
        if self._multiline:
            return self._text_edit.toPlainText().strip()
        return self._line_edit.text().strip()

    def set_value(self, text: str) -> None:
        val = text or ""
        if self._multiline:
            self._text_edit.blockSignals(True)
            self._text_edit.setPlainText(val)
            self._text_edit.blockSignals(False)
        else:
            self._line_edit.blockSignals(True)
            self._line_edit.setText(val)
            self._line_edit.blockSignals(False)
        self._clear_error()

    def set_original_value(self, text: str) -> None:
        self._original_value = text or ""
        self.set_value(self._original_value)

    def reset(self) -> None:
        self.set_value(self._original_value)
        self._clear_error()

    def is_dirty(self) -> bool:
        return self.value() != self._original_value

    def is_valid(self) -> bool:
        if self._is_date:
            return is_valid_user_date(self.value())
        return True

    def mark_invalid(self, message: str) -> None:
        self._helper_label.setText(message)
        self._helper_label.setObjectName("errorText")
        self._helper_label.setVisible(True)
        self._helper_label.style().unpolish(self._helper_label)
        self._helper_label.style().polish(self._helper_label)
        if not self._multiline:
            self._line_edit.setProperty("invalid", True)
            self._line_edit.style().unpolish(self._line_edit)
            self._line_edit.style().polish(self._line_edit)

    def focus_input(self) -> None:
        if self._multiline:
            self._text_edit.setFocus()
        else:
            self._line_edit.setFocus()

    # ── Private ─────────────────────────────────────────────────────────────

    def _build_ui(
        self,
        label: str,
        placeholder: str,
        multiline: bool,
        is_date: bool,
    ) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        # Label row
        label_widget = QLabel(label)
        label_widget.setObjectName("fieldLabel")
        outer.addWidget(label_widget)

        # Input
        if multiline:
            self._text_edit = QTextEdit()
            self._text_edit.setPlaceholderText(placeholder)
            self._text_edit.setFixedHeight(72)
            self._text_edit.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            self._text_edit.setTabChangesFocus(True)
            outer.addWidget(self._text_edit)
            self._line_edit = None  # type: ignore[assignment]
        else:
            self._line_edit = QLineEdit()
            self._line_edit.setPlaceholderText(placeholder)
            self._line_edit.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            self._line_edit.setProperty("invalid", False)
            outer.addWidget(self._line_edit)
            self._text_edit = None  # type: ignore[assignment]

        # Helper / error text
        self._helper_label = QLabel()
        self._helper_label.setObjectName("helperText")
        self._helper_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        if is_date:
            self._helper_label.setText(
                "Format: YYYY-MM-DD  or  YYYY-MM-DD HH:MM:SS"
            )
            self._helper_label.setVisible(True)
        else:
            self._helper_label.setVisible(False)
        outer.addWidget(self._helper_label)

    def _connect_signals(self) -> None:
        if self._multiline:
            self._text_edit.textChanged.connect(self._on_change)
        else:
            self._line_edit.textChanged.connect(self._on_change)

    def _on_change(self) -> None:
        self._clear_error()
        if self._is_date and self.value():
            if not is_valid_user_date(self.value()):
                self._helper_label.setText(
                    "Invalid date — use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"
                )
                self._helper_label.setObjectName("errorText")
                self._helper_label.setVisible(True)
                self._helper_label.style().unpolish(self._helper_label)
                self._helper_label.style().polish(self._helper_label)
                if not self._multiline:
                    self._line_edit.setProperty("invalid", True)
                    self._line_edit.style().unpolish(self._line_edit)
                    self._line_edit.style().polish(self._line_edit)
            else:
                # Restore normal helper text
                self._helper_label.setText(
                    "Format: YYYY-MM-DD  or  YYYY-MM-DD HH:MM:SS"
                )
                self._helper_label.setObjectName("helperText")
                self._helper_label.setVisible(True)
                self._helper_label.style().unpolish(self._helper_label)
                self._helper_label.style().polish(self._helper_label)
        self.value_changed.emit()

    def _clear_error(self) -> None:
        if not self._multiline and self._line_edit is not None:
            self._line_edit.setProperty("invalid", False)
            self._line_edit.style().unpolish(self._line_edit)
            self._line_edit.style().polish(self._line_edit)
        if not self._is_date:
            self._helper_label.setVisible(False)
        else:
            self._helper_label.setObjectName("helperText")
            self._helper_label.setText("Format: YYYY-MM-DD  or  YYYY-MM-DD HH:MM:SS")
            self._helper_label.setVisible(True)
            self._helper_label.style().unpolish(self._helper_label)
            self._helper_label.style().polish(self._helper_label)
