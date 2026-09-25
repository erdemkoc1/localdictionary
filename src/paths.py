"""Application data paths with explicit, non-cloud-first defaults.

Read-only application resources (dictionary and NMT models) stay next to the
executable. Mutable user data is stored under LOCALAPPDATA by default so it is
not placed in a OneDrive-synced Desktop folder and does not disappear when a
portable application folder is replaced.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

APP_DIR_NAME = "LocalDictionary"
DATA_DIR_ENV = "LOCALDICTIONARY_DATA_DIR"


def get_app_data_dir() -> Path:
    """Return the writable per-user data directory, creating it if needed."""
    override = os.environ.get(DATA_DIR_ENV)
    if override:
        data_dir = Path(override).expanduser()
    elif sys.platform == "win32":
        root = os.environ.get("LOCALAPPDATA")
        if not root:
            root = str(Path.home() / "AppData" / "Local")
        data_dir = Path(root) / APP_DIR_NAME
    else:
        root = os.environ.get("XDG_DATA_HOME")
        base = Path(root).expanduser() if root else Path.home() / ".local" / "share"
        data_dir = base / APP_DIR_NAME

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_user_file(filename: str) -> str:
    """Return the canonical path for a mutable user data file."""
    return str(get_app_data_dir() / filename)


def get_log_dir() -> Path:
    """Return the local log directory."""
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _legacy_data_roots() -> list[Path]:
    roots: list[Path] = []
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        roots.extend((exe_dir / "data", exe_dir))
    else:
        project_dir = Path(__file__).resolve().parent.parent
        roots.append(project_dir / "data")
    return roots


def migrate_legacy_user_file(filename: str) -> Path:
    """Copy one legacy user file without overwriting newer local data.

    The source is intentionally left untouched. This keeps the migration
    reversible and avoids deleting data from a portable or OneDrive folder.
    """
    destination = get_app_data_dir() / filename
    if destination.exists():
        return destination

    for root in _legacy_data_roots():
        source = root / filename
        if not source.is_file() or source.resolve() == destination.resolve():
            continue
        try:
            shutil.copy2(source, destination)
        except OSError:
            continue
        break
    return destination
