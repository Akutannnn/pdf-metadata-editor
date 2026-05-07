"""Bottom action bar: Save, Reset, Cancel buttons + saved indicator."""
from __future__ import annotations
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class ActionBarWidget(QWidget):
    save_clicked = Signal()
    reset_clicked = Signal()
    cancel_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("actionBar")
        self._build_ui()
        self._saved_timer = QTimer(self)
        self._saved_timer.setSingleShot(True)
        self._saved_timer.timeout.connect(self._hide_saved_label)

    # ── Public API ──────────────────────────────────────────────────────────

    def set_dirty(self, dirty: bool) -> None:
        self._save_btn.setEnabled(dirty)
        self._reset_btn.setEnabled(dirty)
        if dirty:
            self._hide_saved_label()

    def set_file_loaded(self, loaded: bool) -> None:
        self._save_btn.setEnabled(False)
        self._reset_btn.setEnabled(False)
        self._cancel_btn.setEnabled(loaded)

    def show_saved(self) -> None:
        self._saved_label.setVisible(True)
        self._saved_timer.start(2500)

    def set_saving(self, saving: bool) -> None:
        self._save_btn.setEnabled(not saving)
        self._save_btn.setText("Saving…" if saving else "Save")

    # ── Private ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(10)

        self._saved_label = QLabel("  Saved")
        self._saved_label.setObjectName("savedLabel")
        self._saved_label.setVisible(False)
        layout.addWidget(self._saved_label)

        layout.addStretch()

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setObjectName("cancelButton")
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self.cancel_clicked)
        layout.addWidget(self._cancel_btn)

        self._reset_btn = QPushButton("Reset")
        self._reset_btn.setObjectName("resetButton")
        self._reset_btn.setEnabled(False)
        self._reset_btn.setToolTip("Restore all fields to their last-saved values")
        self._reset_btn.clicked.connect(self.reset_clicked)
        layout.addWidget(self._reset_btn)

        self._save_btn = QPushButton("Save")
        self._save_btn.setObjectName("saveButton")
        self._save_btn.setEnabled(False)
        self._save_btn.setDefault(True)
        self._save_btn.clicked.connect(self.save_clicked)
        layout.addWidget(self._save_btn)

    def _hide_saved_label(self) -> None:
        self._saved_label.setVisible(False)
