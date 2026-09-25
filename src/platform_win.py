import os
import sys
import ctypes
from typing import Tuple, Optional
APP_ID = "LocalDictionary.App.1.42"

# Windows AppUserModelID for independent taskbar icon grouping
def set_app_user_model_id(app_id: str = APP_ID) -> bool:
    """Sets explicit AppUserModelID so Windows taskbar groups and identifies the app separately."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        return True
    except Exception:
        return False


def get_app_executable_path() -> Optional[str]:
    """Return the current frozen executable command for Windows integrations.

    Source-code runs deliberately return ``None``. Registering an arbitrary
    Desktop/dist executable would create a persistence path for a different
    binary and is never done implicitly.
    """
    if getattr(sys, "frozen", False):
        return f'"{os.path.abspath(sys.executable)}"'
    return None


# ---------------- WINDOWS STARTUP (HKCU) ----------------
STARTUP_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_VALUE_NAME = "LocalDictionary"

def set_windows_startup(enabled: bool, mode: str = "normal") -> bool:
    """
    Enables or disables auto-start on Windows boot via HKCU registry.
    mode: 'normal' (foreground window) or 'minimized' (starts in system tray/taskbar).
    """
    exe = get_app_executable_path() if enabled else None
    if enabled and not exe:
        print("Hata: Otomatik başlatma yalnızca paketlenmiş EXE sürümünde etkinleştirilebilir.")
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                if mode == "minimized":
                    val_data = f'{exe} --minimized'
                else:
                    val_data = f'{exe}'
                winreg.SetValueEx(key, STARTUP_VALUE_NAME, 0, winreg.REG_SZ, val_data)
            else:
                try:
                    winreg.DeleteValue(key, STARTUP_VALUE_NAME)
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        print(f"Hata: Windows başlangıç kaydı güncellenemedi: {e}")
        return False


def get_windows_startup() -> Tuple[bool, str]:
    """Checks whether LocalDictionary is configured in Windows Run registry and returns (enabled, mode)."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY_PATH, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, STARTUP_VALUE_NAME)
            if "--minimized" in str(val):
                return (True, "minimized")
            return (True, "normal")
    except Exception:
        return (False, "normal")


# ---------------- WINDOWS EXPLORER CONTEXT MENU (HKCU) ----------------
CONTEXT_MENU_SUBKEYS = [
    r"Software\Classes\*\shell\LocalDictionary",
    r"Software\Classes\Directory\shell\LocalDictionary",
    r"Software\Classes\Directory\Background\shell\LocalDictionary"
]

def _delete_reg_tree(root, path):
    import winreg
    access = winreg.KEY_READ | winreg.KEY_WRITE | winreg.DELETE
    try:
        with winreg.OpenKey(root, path, 0, access) as key:
            while True:
                try:
                    sub = winreg.EnumKey(key, 0)
                    _delete_reg_tree(root, f"{path}\\{sub}")
                except OSError:
                    break
        winreg.DeleteKey(root, path)
    except FileNotFoundError:
        pass
    except Exception:
        pass

def notify_shell_change():
    """Notifies Windows Explorer to instantly refresh context menu and associations."""
    try:
        # SHCNE_ASSOCCHANGED = 0x08000000, SHCNF_IDLIST = 0x0000
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
    except Exception:
        pass

def set_windows_context_menu(enabled: bool, menu_text: str = "LocalDictionary ile Çevir") -> bool:
    """
    Enables or disables only LocalDictionary's dedicated HKCU shell keys.
    Shared Windows shell/CLSID configuration is never modified.
    """
    try:
        import winreg
        if enabled:
            exe_cmd = get_app_executable_path()
            if not exe_cmd:
                print("Hata: Windows sağ tık menüsü yalnızca paketlenmiş EXE sürümünde etkinleştirilebilir.")
                return False
            exe_clean = exe_cmd.strip('"').split('"')[0] if '"' in exe_cmd else exe_cmd.split()[0]
            
            for base_path in CONTEXT_MENU_SUBKEYS:
                # Create main context key
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base_path) as k:
                    winreg.SetValueEx(k, "", 0, winreg.REG_SZ, menu_text)
                    winreg.SetValueEx(k, "MUIVerb", 0, winreg.REG_SZ, menu_text)
                    if os.path.exists(exe_clean):
                        winreg.SetValueEx(k, "Icon", 0, winreg.REG_SZ, f'"{exe_clean}"')
                
                # Create command subkey
                cmd_path = f"{base_path}\\command"
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_path) as k:
                    if "Background" in base_path:
                        winreg.SetValueEx(k, "", 0, winreg.REG_SZ, f'{exe_cmd}')
                    else:
                        winreg.SetValueEx(k, "", 0, winreg.REG_SZ, f'{exe_cmd} "%1"')

        else:
            for base_path in CONTEXT_MENU_SUBKEYS:
                _delete_reg_tree(winreg.HKEY_CURRENT_USER, base_path)

        notify_shell_change()
        return True
    except Exception as e:
        print(f"Hata: Windows sağ tık menüsü güncellenemedi: {e}")
        return False


def get_windows_context_menu() -> bool:
    """Checks if the HKCU context menu key exists."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CONTEXT_MENU_SUBKEYS[0], 0, winreg.KEY_READ) as _:
            return True
    except Exception:
        return False
