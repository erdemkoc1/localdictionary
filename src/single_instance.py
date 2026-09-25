"""Best-effort single-instance guard for the Windows desktop application."""

from __future__ import annotations

import ctypes
import os
import sys


class SingleInstanceGuard:
    def __init__(self, name: str = r"Local\LocalDictionary.App"):
        self.name = name
        self._handle = None

    def acquire(self) -> bool:
        if os.name != "nt" or getattr(sys, "frozen", False) is False:
            return True
        kernel32 = ctypes.windll.kernel32
        kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
        kernel32.CreateMutexW.restype = ctypes.c_void_p
        handle = kernel32.CreateMutexW(None, False, self.name)
        if not handle:
            return False
        if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            kernel32.CloseHandle(handle)
            return False
        self._handle = handle
        return True

    def release(self) -> None:
        if self._handle and os.name == "nt":
            ctypes.windll.kernel32.CloseHandle(self._handle)
        self._handle = None

    def __del__(self):
        try:
            self.release()
        except Exception:
            pass
