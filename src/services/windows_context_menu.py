"""Windows Explorer context-menu registration helpers (for in-app use).

The primary install/uninstall mechanism is the PowerShell scripts at the
project root.  This module provides Python helpers used by tests and by the
optional in-app "Install context menu" action.
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Optional

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

HKCU_ROOT = "HKEY_CURRENT_USER"
SHELL_KEY = r"SOFTWARE\Classes\SystemFileAssociations\.pdf\shell\EditMetadata"
COMMAND_KEY = SHELL_KEY + r"\command"
MENU_LABEL = "Edit metadata"


def install(executable: Path) -> None:
    """Register the context-menu entry for the current user (no admin needed)."""
    if sys.platform != "win32":
        raise OSError("Context-menu registration is only supported on Windows.")

    import winreg

    cmd = f'"{executable}" "%1"'
    logger.info("Installing context menu: %s", cmd)

    with winreg.CreateKeyEx(
        winreg.HKEY_CURRENT_USER, SHELL_KEY, 0, winreg.KEY_WRITE
    ) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, MENU_LABEL)
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, str(executable))

    with winreg.CreateKeyEx(
        winreg.HKEY_CURRENT_USER, COMMAND_KEY, 0, winreg.KEY_WRITE
    ) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)


def uninstall() -> None:
    """Remove the context-menu entry."""
    if sys.platform != "win32":
        return

    import winreg

    logger.info("Uninstalling context menu")
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, COMMAND_KEY)
    except FileNotFoundError:
        pass
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, SHELL_KEY)
    except FileNotFoundError:
        pass


def is_installed() -> bool:
    """Return True when the registry entry already exists."""
    if sys.platform != "win32":
        return False
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, COMMAND_KEY):
            return True
    except FileNotFoundError:
        return False


def get_registered_executable() -> Optional[str]:
    """Return the executable path currently registered, or None."""
    if sys.platform != "win32":
        return None
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, COMMAND_KEY) as key:
            value, _ = winreg.QueryValueEx(key, "")
            return value
    except FileNotFoundError:
        return None
