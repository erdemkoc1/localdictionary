import os
import sys
import ctypes
from typing import Tuple, Optional

# Windows AppUserModelID for independent taskbar icon grouping
def set_app_user_model_id(app_id: str = "LocalDictionary.App.1.4") -> bool:
    """Sets explicit AppUserModelID so Windows taskbar groups and identifies the app separately."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        return True
    except Exception:
        return False


def get_app_executable_path() -> str:
    """Returns the path to the executable or launch command for Windows integrations."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    
    # Check if compiled desktop executable exists
    candidates = [
        os.path.normpath(r"\OneDrive\Masaüstü\localdictionary\localdictionary.exe"),
        os.path.normpath(r"\OneDrive\Desktop\localdictionary\localdictionary.exe"),
        os.path.normpath(r"\Desktop\localdictionary\localdictionary.exe"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist", "localdictionary", "localdictionary.exe"))
    ]
    for c in candidates:
        if os.path.exists(c):
            return f'"{c}"'
    
    # Fallback to pythonw + main.py
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    main_py = os.path.join(base_dir, "main.py")
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if os.path.exists(pythonw):
        return f'"{pythonw}" "{main_py}"'
    return f'"{sys.executable}" "{main_py}"'


# ---------------- WINDOWS STARTUP (HKCU) ----------------
STARTUP_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_VALUE_NAME = "LocalDictionary"

def set_windows_startup(enabled: bool, mode: str = "normal") -> bool:
    """
    Enables or disables auto-start on Windows boot via HKCU registry.
    mode: 'normal' (foreground window) or 'minimized' (starts in system tray/taskbar).
    """
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                exe = get_app_executable_path()
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

WIN11_CLASSIC_MENU_PARENT = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
WIN11_CLASSIC_MENU_KEY = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"

def _delete_reg_tree(root, path):
    import winreg
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
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
    Enables or disables 'LocalDictionary ile Çevir' in Windows Explorer context menu (HKCU).
    Also configures Windows 11 compatibility so the verb appears immediately without clicking 'Show more options'.
    """
    try:
        import winreg
        if enabled:
            exe_cmd = get_app_executable_path()
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

            # Windows 11 classic context menu bypass for direct visibility
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, WIN11_CLASSIC_MENU_KEY) as k:
                    winreg.SetValueEx(k, "", 0, winreg.REG_SZ, "")
            except Exception:
                pass
        else:
            for base_path in CONTEXT_MENU_SUBKEYS:
                _delete_reg_tree(winreg.HKEY_CURRENT_USER, base_path)
            
            try:
                _delete_reg_tree(winreg.HKEY_CURRENT_USER, WIN11_CLASSIC_MENU_PARENT)
            except Exception:
                pass

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
