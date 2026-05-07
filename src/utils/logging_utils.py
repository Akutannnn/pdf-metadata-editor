from __future__ import annotations
import logging
import sys
from pathlib import Path
from ..constants import LOG_DIR, APP_NAME


def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    fmt = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / f"{APP_NAME}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(fmt))
        handlers.append(file_handler)
    except OSError:
        pass

    logging.basicConfig(level=level, format=fmt, handlers=handlers)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
