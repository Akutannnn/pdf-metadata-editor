from pathlib import Path

APP_NAME = "PDF Metadata Editor"
APP_VERSION = "1.0.0"
ORG_NAME = "PDFMetadataEditor"

WINDOW_DEFAULT_WIDTH = 620
WINDOW_DEFAULT_HEIGHT = 680
WINDOW_MIN_WIDTH = 480
WINDOW_MIN_HEIGHT = 500

REGISTRY_KEY = r"SOFTWARE\Classes\SystemFileAssociations\.pdf\shell\EditMetadata"
REGISTRY_KEY_COMMAND = REGISTRY_KEY + r"\command"
CONTEXT_MENU_LABEL = "Edit metadata"

SRC_DIR = Path(__file__).parent
PROJECT_DIR = SRC_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"
ICON_PATH = ASSETS_DIR / "app_icon.ico"

LOG_DIR = Path.home() / "AppData" / "Local" / APP_NAME / "Logs"

DATE_FIELDS = {"CreationDate", "ModDate"}
DATE_DISPLAY_FORMAT = "YYYY-MM-DD HH:MM:SS"

METADATA_FIELDS: list[dict] = [
    {"key": "Title",        "label": "Title",         "placeholder": "Document title",           "multiline": False, "date": False},
    {"key": "Author",       "label": "Author",        "placeholder": "Author name(s)",           "multiline": False, "date": False},
    {"key": "Subject",      "label": "Subject",       "placeholder": "Brief description",        "multiline": True,  "date": False},
    {"key": "Keywords",     "label": "Keywords",      "placeholder": "keyword1, keyword2, …",    "multiline": False, "date": False},
    {"key": "Creator",      "label": "Creator",       "placeholder": "Creating application",     "multiline": False, "date": False},
    {"key": "Producer",     "label": "Producer",      "placeholder": "PDF producer library",     "multiline": False, "date": False},
    {"key": "CreationDate", "label": "Creation Date", "placeholder": "YYYY-MM-DD or YYYY-MM-DD HH:MM:SS", "multiline": False, "date": True},
    {"key": "ModDate",      "label": "Modified Date", "placeholder": "YYYY-MM-DD or YYYY-MM-DD HH:MM:SS", "multiline": False, "date": True},
]
