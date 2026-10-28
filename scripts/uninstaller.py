"""LocalDictionary uninstaller (Windows, standard library only).

Built as uninstall.exe and placed next to localdictionary.exe. It removes the
per-user registrations the app creates (startup entry, Explorer context menu,
Start Menu shortcut) and the release files in its own folder. Files that are
not part of the release, such as the user's data/ folder, are left alone.
"""

from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import time
import winreg
from pathlib import Path

APP_EXE_NAME = "localdictionary.exe"
STARTUP_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_VALUE_NAME = "LocalDictionary"
CONTEXT_MENU_SUBKEYS = [
    r"Software\Classes\*\shell\LocalDictionary",
    r"Software\Classes\Directory\shell\LocalDictionary",
    r"Software\Classes\Directory\Background\shell\LocalDictionary",
]
START_MENU_SHORTCUT_NAME = "Local Dictionary.lnk"
RELEASE_ENTRIES = [
    APP_EXE_NAME,
    "_internal",
    "RELEASE_README.txt",
    "RELEASE_MANIFEST.json",
    "SHA256SUMS.txt",
]
USER_DATA_FILES = ["user_data.db", "history.db", "settings.json"]
CLEANUP_FLAG = "--cleanup"

MB_YESNO = 0x4
MB_ICONQUESTION = 0x20
MB_ICONWARNING = 0x30
MB_ICONINFORMATION = 0x40
MB_DEFBUTTON2 = 0x100
IDYES = 6


def ask(text: str, title: str = "LocalDictionary", default_no: bool = True) -> bool:
    flags = MB_YESNO | MB_ICONQUESTION | (MB_DEFBUTTON2 if default_no else 0)
    return ctypes.windll.user32.MessageBoxW(0, text, title, flags) == IDYES


def show(text: str, title: str = "LocalDictionary", warning: bool = False) -> None:
    icon = MB_ICONWARNING if warning else MB_ICONINFORMATION
    ctypes.windll.user32.MessageBoxW(0, text, title, icon)


def app_is_running() -> bool:
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {APP_EXE_NAME}", "/NH"],
            capture_output=True, text=True, timeout=15,
        ).stdout
    except Exception:
        return False
    return APP_EXE_NAME.lower() in out.lower()


def delete_reg_tree(root, path: str) -> None:
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            while True:
                try:
                    child = winreg.EnumKey(key, 0)
                except OSError:
                    break
                delete_reg_tree(root, f"{path}\\{child}")
        winreg.DeleteKey(root, path)
    except FileNotFoundError:
        pass


def remove_registrations() -> list[str]:
    removed = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, STARTUP_VALUE_NAME)
            removed.append("Windows başlangıç kaydı")
    except FileNotFoundError:
        pass

    for subkey in CONTEXT_MENU_SUBKEYS:
        delete_reg_tree(winreg.HKEY_CURRENT_USER, subkey)
    removed.append("Explorer bağlam menüsü")

    appdata = os.environ.get("APPDATA")
    if appdata:
        shortcut = Path(appdata, "Microsoft", "Windows", "Start Menu", "Programs", START_MENU_SHORTCUT_NAME)
        if shortcut.exists():
            shortcut.unlink()
            removed.append("Başlat menüsü kısayolu")
    return removed


def user_data_dir() -> Path | None:
    local = os.environ.get("LOCALAPPDATA")
    return Path(local, "LocalDictionary") if local else None


def remove_release_files(app_dir: Path) -> list[str]:
    removed = []
    for name in RELEASE_ENTRIES:
        target = app_dir / name
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
            removed.append(name)
        elif target.exists():
            target.unlink()
            removed.append(name)

    data_dir = app_dir / "data"
    if data_dir.is_dir() and not any((data_dir / f).exists() for f in USER_DATA_FILES):
        shutil.rmtree(data_dir, ignore_errors=True)
        removed.append("data")
    return removed


def schedule_self_delete(app_dir: Path) -> None:
    # The running uninstaller cannot delete its own file, so it copies itself to
    # %TEMP% and that copy finishes the removal of the folder.
    temp_copy = Path(tempfile.gettempdir(), f"LocalDictionary-uninstall-{os.getpid()}.exe")
    shutil.copy2(sys.executable, temp_copy)
    subprocess.Popen(
        [str(temp_copy), CLEANUP_FLAG, str(app_dir)],
        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
        close_fds=True,
    )


def cleanup(app_dir: Path) -> int:
    # Runs from %TEMP%: wait for the original uninstall.exe to exit, then remove
    # the folder if it is empty of user files, and finally this copy.
    own_exe = Path(sys.executable)
    original = app_dir / "uninstall.exe"
    for _ in range(60):
        try:
            original.unlink(missing_ok=True)
            break
        except OSError:
            time.sleep(1)
    try:
        app_dir.rmdir()
    except OSError:
        pass
    subprocess.Popen(
        f'cmd /c ping 127.0.0.1 -n 3 >nul & del /f /q "{own_exe}"',
        creationflags=subprocess.CREATE_NO_WINDOW,
        close_fds=True,
    )
    return 0


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == CLEANUP_FLAG:
        return cleanup(Path(sys.argv[2]))

    if not getattr(sys, "frozen", False):
        print("uninstall.exe must be run as the built executable.")
        return 1

    app_dir = Path(sys.executable).resolve().parent
    if not (app_dir / APP_EXE_NAME).exists():
        show(
            "Bu klasörde localdictionary.exe bulunamadı. Güvenlik için hiçbir dosya silinmedi.\n\n"
            "Uygulama klasöründen çalıştırın.",
            warning=True,
        )
        return 1

    if app_is_running():
        show("LocalDictionary çalışıyor. Lütfen uygulamayı kapatıp kaldırmayı tekrar deneyin.", warning=True)
        return 1

    if not ask(
        "LocalDictionary kaldırılsın mı?\n\n"
        "Silinecekler:\n"
        "- Başlangıçta çalıştırma kaydı, Explorer bağlam menüsü, Başlat menüsü kısayolu\n"
        f"- Uygulama dosyaları: {app_dir}\n"
        "  (localdictionary.exe, _internal, sürüm dosyaları ve bu kaldırıcı)\n\n"
        "Kullanıcı verileriniz (geçmiş, ayarlar, önbellek) bu adımda silinmez.",
    ):
        return 0

    removed = remove_registrations()
    removed += remove_release_files(app_dir)

    data = user_data_dir()
    if data and data.exists():
        if ask(
            f"Kullanıcı verileriniz de silinsin mi?\n\n{data}\n\n"
            "Geçmiş, ayarlar ve çeviri önbelleği kalıcı olarak silinir.",
            default_no=True,
        ):
            shutil.rmtree(data, ignore_errors=True)
            removed.append("kullanıcı verileri")

    schedule_self_delete(app_dir)
    show("LocalDictionary kaldırıldı.\n\nTemizlenenler: " + ", ".join(removed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
