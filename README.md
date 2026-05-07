# PDF Metadata Editor

A clean, native Windows 10 desktop utility for editing PDF file metadata.
Right-click any PDF in Windows Explorer → **Edit metadata** → edit and save.

---

## Screenshots

> **[Screenshot: Main window — form pre-filled with PDF metadata]**
>
> **[Screenshot: Dirty state — Save button enabled, field values changed]**
>
> **[Screenshot: Explorer context menu — "Edit metadata" entry]**
>
> **[Screenshot: No-file state — "Open PDF File…" prompt]**

---

## What it does

- Opens a PDF directly from the Windows Explorer right-click menu
- Prefills all editable metadata fields from the current file
- Lets you edit: **Title**, **Author**, **Subject**, **Keywords**, **Creator**, **Producer**, **Creation Date**, **Modified Date**
- Saves back to the **same file path** — no duplicates, no Save As
- Uses an atomic temp-file swap so the original is safe if a save fails
- Validates date inputs inline with friendly error messages
- Supports Unicode file paths and metadata values

---

## Requirements

| Tool | Version |
|------|---------|
| Python | 3.12+ |
| Windows | 10 or 11 |

Python packages (auto-installed by scripts):

```
PySide6 >= 6.6.0
pikepdf >= 8.10.0
```

---

## Dev setup

```powershell
# Clone or download the project, then:
cd pdf-metadata-editor

# Create a venv and install dependencies
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt -r requirements-dev.txt
```

---

## Run locally (from source)

```powershell
# Open a specific PDF
.\run_dev.ps1 -PdfPath "C:\Documents\sample.pdf"

# Open with the file picker
.\run_dev.ps1

# Or directly:
.venv\Scripts\python main.py "C:\Documents\sample.pdf"
```

---

## Run tests

```powershell
.venv\Scripts\pytest
```

Or with coverage:

```powershell
.venv\Scripts\pytest --cov=src --cov-report=term-missing
```

---

## Build executable

```powershell
# Full clean build
.\build.ps1 -Clean

# The output is at:
#   dist\PDFMetadataEditor\PDFMetadataEditor.exe
```

The build script:
1. Creates `.venv` if it doesn't exist
2. Installs all dependencies
3. Generates `assets/app_icon.ico`
4. Runs PyInstaller with the provided `.spec` file
5. Reports the output path

The result is a **folder-based** distribution (`--onedir`), which starts faster than a single-file bundle. Distribute the entire `dist\PDFMetadataEditor\` folder.

---

## Install Explorer context menu

After building:

```powershell
# Uses the default dist\ path automatically
.\install_context_menu.ps1

# Or specify a custom executable location
.\install_context_menu.ps1 -ExePath "C:\Tools\PDFMetadataEditor\PDFMetadataEditor.exe"
```

**No administrator rights are required.**  
The entry is registered under `HKEY_CURRENT_USER` and only affects your Windows user account.

Registry key written:
```
HKCU\SOFTWARE\Classes\SystemFileAssociations\.pdf\shell\EditMetadata
HKCU\SOFTWARE\Classes\SystemFileAssociations\.pdf\shell\EditMetadata\command
```

Command registered:
```
"C:\...\PDFMetadataEditor.exe" "%1"
```

`%1` is automatically replaced by Windows Explorer with the clicked file's full path (properly quoted).

---

## Uninstall context menu

```powershell
.\uninstall_context_menu.ps1
```

This removes both registry keys.  No files are deleted.

---

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+S` | Save |
| `Ctrl+O` | Open file picker |
| `Esc` | Close (prompts if unsaved changes) |
| `Tab` | Move to next field |
| `Shift+Tab` | Move to previous field |

---

## Architecture overview

```
pdf-metadata-editor/
├── main.py                         Entry point (adds src/ to sys.path)
├── src/
│   ├── app.py                      Bootstrap: argv parsing, Qt setup, QSS
│   ├── constants.py                App-wide constants and field definitions
│   ├── models/
│   │   └── metadata.py             PDFMetadata dataclass
│   ├── services/
│   │   ├── pdf_metadata_service.py pikepdf read/write + atomic save
│   │   ├── file_service.py         Pre-open/pre-save validation
│   │   └── windows_context_menu.py Registry install/uninstall helpers
│   ├── ui/
│   │   ├── main_window.py          QMainWindow: wires everything together
│   │   ├── styles/theme.py         QSS stylesheet (single source of truth)
│   │   └── widgets/
│   │       ├── metadata_field.py   Labeled field row (QLineEdit / QTextEdit)
│   │       ├── file_header.py      File name + path display strip
│   │       └── action_bar.py       Save / Reset / Cancel + saved indicator
│   └── utils/
│       ├── date_utils.py           PDF ↔ human date parsing/formatting
│       ├── path_utils.py           Path normalization, display helpers
│       ├── error_utils.py          Typed AppError hierarchy + OS error mapping
│       └── logging_utils.py        File + stdout logging setup
└── tests/
    ├── conftest.py                  PDF fixtures (minimal, full, unicode, readonly)
    ├── test_metadata_mapping.py     Read/write field mapping
    ├── test_date_parsing.py         Date parse/format/normalize/display
    ├── test_argument_handling.py    sys.argv parsing, path resolution
    └── test_save_workflow.py        Atomic save, rollback, roundtrip
```

**Data flow:**

```
Explorer "%1" argument
        │
        ▼
  app.py::parse_pdf_argument()
        │
        ▼
  MainWindow._load_file()
        │
        ├─► file_service.validate_for_open()
        │
        ├─► pdf_metadata_service.read_metadata()   (pikepdf)
        │
        └─► populate form fields
                │
                ▼  (user edits)
        MainWindow._on_save()
                │
                ├─► date_utils.normalize_user_date()
                ├─► file_service.validate_for_save()
                └─► pdf_metadata_service.write_metadata()
                        │
                        ├─► pikepdf.open(original)
                        ├─► modify docinfo + XMP
                        ├─► pdf.save(temp_file)
                        └─► os.replace(temp_file, original)
```

---

## Known edge cases

| Situation | Behaviour |
|-----------|-----------|
| PDF open in another app | Save fails with "File is open in another application" message. Close the other app and retry. |
| Password-protected PDF | Opens for reading (with existing metadata) but save is blocked with a clear error. |
| Read-only file | Detected before attempting save; error shown with instructions to remove read-only attribute. |
| XMP sync failure | Logged as a warning; docinfo (the primary metadata store) is always written. Non-fatal. |
| Malformed existing date | Displayed as-is in the form. User can correct it; it will be normalized on save. |
| No file argument at launch | Shows "Open PDF File…" button — click to pick a file via the system dialog. |

---

## Manual QA checklist

- [ ] **Open from Explorer:** right-click a PDF → "Edit metadata" → window appears with correct filename in title bar
- [ ] **Pre-fill:** all existing metadata fields are populated; empty fields are blank (not "None")
- [ ] **Dirty state:** Save/Reset buttons disabled initially; enabling only after editing a field
- [ ] **Save:** click Save → file written, "Saved" indicator appears, buttons reset to disabled
- [ ] **Reset:** edit fields → click Reset → fields restored to last-saved values
- [ ] **Ctrl+S:** save via keyboard shortcut
- [ ] **Date validation:** enter "not-a-date" in Creation Date → red helper text; Save blocked
- [ ] **Date normalization:** enter "2024-06-15" → after save, date stored as PDF format `D:...`
- [ ] **Unicode path:** open a PDF in a path with accents (e.g. `C:\Résumés\`) → loads correctly
- [ ] **Unicode values:** set Author to `Ångström` → saves and reloads correctly
- [ ] **Read-only file:** attempt to save a read-only PDF → clear error dialog
- [ ] **Locked file:** attempt to save a PDF open exclusively in Acrobat → locked-file error
- [ ] **No argument:** launch `PDFMetadataEditor.exe` with no args → "Open PDF File…" state
- [ ] **Non-PDF argument:** launch with a .txt file → "Not a PDF file" error dialog
- [ ] **Close with unsaved:** edit a field → close window → "Save / Discard / Cancel" prompt
- [ ] **No temp files:** confirm no `.pme_*` files remain in the PDF's folder after save
- [ ] **Same path:** confirm the PDF's full path and filename are unchanged after save
