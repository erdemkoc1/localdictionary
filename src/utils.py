import os
import sys

# Turkish character mapping for accurate case transformations
TR_LOWER_MAP = str.maketrans({
    "I": "ı",
    "İ": "i",
    "Ç": "ç",
    "Ğ": "ğ",
    "Ö": "ö",
    "Ş": "ş",
    "Ü": "ü"
})

TR_UPPER_MAP = str.maketrans({
    "ı": "I",
    "i": "İ",
    "ç": "Ç",
    "ğ": "Ğ",
    "ö": "Ö",
    "ş": "Ş",
    "ü": "Ü"
})

def turkish_lower(text: str) -> str:
    """Convert string to lowercase with proper Turkish dotted/dotless I support."""
    if not text:
        return ""
    return text.translate(TR_LOWER_MAP).lower()

def turkish_upper(text: str) -> str:
    """Convert string to uppercase with proper Turkish dotted/dotless I support."""
    if not text:
        return ""
    return text.translate(TR_UPPER_MAP).upper()

def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    Supports both --onefile (sys._MEIPASS) and --onedir (directory of sys.executable).
    """
    # 1. If running as bundled PyInstaller app
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        
        # Check relative path from exe_dir (e.g. data/dictionary.db)
        candidate1 = os.path.join(exe_dir, relative_path)
        if os.path.exists(candidate1):
            return candidate1

        # Check directly in exe_dir (e.g. dictionary.db)
        candidate2 = os.path.join(exe_dir, os.path.basename(relative_path))
        if os.path.exists(candidate2):
            return candidate2

        # Then check in _MEIPASS (onefile temporary directory)
        if hasattr(sys, '_MEIPASS'):
            candidate3 = os.path.join(sys._MEIPASS, relative_path)
            if os.path.exists(candidate3):
                return candidate3
            candidate4 = os.path.join(sys._MEIPASS, os.path.basename(relative_path))
            if os.path.exists(candidate4):
                return candidate4

    # 2. If running from source code
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_dir, relative_path)
