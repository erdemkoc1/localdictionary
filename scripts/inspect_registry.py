import os
import sys
import winreg

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.platform_win import get_app_executable_path, get_windows_context_menu, get_windows_startup

print("Executable path:", get_app_executable_path())
clean_path = get_app_executable_path().strip('"')
print("Exists:", os.path.exists(clean_path))

# Check registry values
def check(path):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as k:
            val, _ = winreg.QueryValueEx(k, "")
            print(f"Key '{path}' value: {val}")
    except Exception as e:
        print(f"Key '{path}' error: {e}")

check(r"Software\Classes\*\shell\LocalDictionary")
check(r"Software\Classes\Directory\shell\LocalDictionary")
check(r"Software\Classes\Directory\Background\shell\LocalDictionary")
