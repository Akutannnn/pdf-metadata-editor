"""File header bar: shows the selected PDF's name and full path."""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...utils.path_utils import short_display_path


class FileHeaderWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("fileHeader")
        self._build_ui()

    def set_file(self, path: Path) -> None:
        self._name_label.setText(path.name)
        self._path_label.setText(short_display_path(path.parent, max_len=90))
        self._path_label.setToolTip(str(path))

    def clear(self) -> None:
        self._name_label.setText("No file selected")
        self._path_label.setText("")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(2)

        self._name_label = QLabel("No file selected")
        self._name_label.setObjectName("appTitle")
        self._name_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self._name_label)

        self._path_label = QLabel("")
        self._path_label.setObjectName("filePath")
        self._path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self._path_label)
