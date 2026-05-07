"""Main application window."""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from ..constants import (
    APP_NAME,
    DATE_FIELDS,
    ICON_PATH,
    METADATA_FIELDS,
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)
from ..models.metadata import PDFMetadata
from ..services.file_service import validate_for_open, validate_for_save
from ..services.pdf_metadata_service import read_metadata, write_metadata
from ..utils.date_utils import display_date, normalize_user_date
from ..utils.error_utils import AppError
from ..utils.logging_utils import get_logger
from .widgets.action_bar import ActionBarWidget
from .widgets.file_header import FileHeaderWidget
from .widgets.metadata_field import MetadataField

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, pdf_path: Optional[Path] = None) -> None:
        super().__init__()
        self._current_path: Optional[Path] = None
        self._original_metadata: Optional[PDFMetadata] = None
        self._fields: dict[str, MetadataField] = {}

        self._build_ui()
        self._setup_shortcuts()
        self._apply_icon()
        self._center_window()

        if pdf_path is not None:
            QTimer.singleShot(0, lambda: self._load_file(pdf_path))

    # ── Build UI ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)

        root = QWidget()
        root.setObjectName("centralWidget")
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # File header
        self._header = FileHeaderWidget()
        main_layout.addWidget(self._header)

        # Scrollable form area
        scroll = QScrollArea()
        scroll.setObjectName("formScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        form_container = QWidget()
        form_container.setObjectName("formContainer")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(16)

        # No-file placeholder
        self._no_file_widget = self._build_no_file_widget()
        form_layout.addWidget(self._no_file_widget)

        # Form fields
        self._form_widget = QWidget()
        fields_layout = QVBoxLayout(self._form_widget)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        fields_layout.setSpacing(16)

        for spec in METADATA_FIELDS:
            field = MetadataField(
                key=spec["key"],
                label=spec["label"],
                placeholder=spec["placeholder"],
                multiline=spec["multiline"],
                is_date=spec["date"],
            )
            field.value_changed.connect(self._on_field_changed)
            self._fields[spec["key"]] = field
            fields_layout.addWidget(field)

        fields_layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        form_layout.addWidget(self._form_widget)
        scroll.setWidget(form_container)
        main_layout.addWidget(scroll, stretch=1)

        # Action bar
        self._action_bar = ActionBarWidget()
        self._action_bar.save_clicked.connect(self._on_save)
        self._action_bar.reset_clicked.connect(self._on_reset)
        self._action_bar.cancel_clicked.connect(self.close)
        main_layout.addWidget(self._action_bar)

        self._set_form_visible(False)

    def _build_no_file_widget(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        label = QLabel("No PDF file selected.")
        label.setObjectName("noFileLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        btn = QPushButton("Open PDF File…")
        btn.setObjectName("openFileButton")
        btn.setFixedWidth(180)
        btn.clicked.connect(self._pick_file)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return container

    # ── Shortcuts ────────────────────────────────────────────────────────────

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self._on_save)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self._handle_escape)
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self._pick_file)

    # ── Loading ──────────────────────────────────────────────────────────────

    def _load_file(self, path: Path) -> None:
        try:
            validate_for_open(path)
            metadata = read_metadata(path)
        except AppError as exc:
            self._show_error(str(exc.message), exc.detail)
            return
        except Exception as exc:
            logger.exception("Unexpected error opening %s", path)
            self._show_error(
                "Unexpected error opening file.",
                f"{type(exc).__name__}: {exc}",
            )
            return

        self._current_path = path
        self._original_metadata = metadata

        self._header.set_file(path)
        self.setWindowTitle(f"{path.name}  —  {APP_NAME}")
        self._populate_form(metadata)
        self._set_form_visible(True)
        self._action_bar.set_file_loaded(True)
        self._action_bar.set_dirty(False)

        # Tab to first field
        first_key = METADATA_FIELDS[0]["key"]
        self._fields[first_key].focus_input()

    def _populate_form(self, metadata: PDFMetadata) -> None:
        for key, field in self._fields.items():
            raw = getattr(metadata, key, None) or ""
            if raw and key in DATE_FIELDS:
                raw = display_date(raw)
            field.set_original_value(raw)

    # ── Save / Reset ─────────────────────────────────────────────────────────

    def _on_save(self) -> None:
        if self._current_path is None:
            return

        # Validate date fields first
        for spec in METADATA_FIELDS:
            if spec["date"]:
                field = self._fields[spec["key"]]
                if not field.is_valid():
                    self._show_error(
                        f"Invalid date in '{spec['label']}'.",
                        "Use format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS.",
                    )
                    field.focus_input()
                    return

        # Build metadata from form
        data: dict[str, Optional[str]] = {}
        for key, field in self._fields.items():
            val = field.value()
            if not val:
                data[key] = None
                continue
            if key in DATE_FIELDS:
                try:
                    data[key] = normalize_user_date(val)
                except ValueError as exc:
                    self._show_error(f"Invalid date in '{key}'.", str(exc))
                    self._fields[key].focus_input()
                    return
            else:
                data[key] = val or None

        new_metadata = PDFMetadata.from_dict(data)

        try:
            validate_for_save(self._current_path)
        except AppError as exc:
            self._show_error(exc.message, exc.detail)
            return

        self._action_bar.set_saving(True)
        try:
            write_metadata(self._current_path, new_metadata)
        except AppError as exc:
            self._action_bar.set_saving(False)
            self._show_error(exc.message, exc.detail)
            return
        except Exception as exc:
            self._action_bar.set_saving(False)
            logger.exception("Unexpected save error")
            self._show_error(
                "Unexpected error while saving.",
                f"{type(exc).__name__}: {exc}",
            )
            return

        # Reload to get canonical values (e.g. normalised dates)
        try:
            saved = read_metadata(self._current_path)
        except Exception:
            saved = new_metadata

        self._original_metadata = saved
        self._populate_form(saved)

        self._action_bar.set_saving(False)
        self._action_bar.set_dirty(False)
        self._action_bar.show_saved()

    def _on_reset(self) -> None:
        if self._original_metadata is None:
            return
        self._populate_form(self._original_metadata)
        self._action_bar.set_dirty(False)

    def _on_field_changed(self) -> None:
        dirty = any(f.is_dirty() for f in self._fields.values())
        self._action_bar.set_dirty(dirty)

    # ── File picker ──────────────────────────────────────────────────────────

    def _pick_file(self) -> None:
        start_dir = (
            str(self._current_path.parent) if self._current_path else ""
        )
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF File",
            start_dir,
            "PDF Files (*.pdf);;All Files (*)",
        )
        if path_str:
            self._load_file(Path(path_str))

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _set_form_visible(self, visible: bool) -> None:
        self._form_widget.setVisible(visible)
        self._no_file_widget.setVisible(not visible)

    def _handle_escape(self) -> None:
        if not self._has_unsaved_changes():
            self.close()
        else:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Close without saving?",
                QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Discard:
                self.close()

    def _has_unsaved_changes(self) -> bool:
        return any(f.is_dirty() for f in self._fields.values())

    def _show_error(self, message: str, detail: str = "") -> None:
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Error")
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setText(message)
        if detail:
            dlg.setInformativeText(detail)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.exec()

    def _apply_icon(self) -> None:
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

    def _center_window(self) -> None:
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            x = (geom.width() - self.width()) // 2 + geom.left()
            y = (geom.height() - self.height()) // 2 + geom.top()
            self.move(x, y)

    # ── Close event ──────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes.\n\nSave before closing?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if reply == QMessageBox.StandardButton.Save:
                self._on_save()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
