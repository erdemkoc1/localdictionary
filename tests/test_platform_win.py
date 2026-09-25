import unittest
from unittest.mock import patch

from src import platform_win


class TestWindowsIntegrations(unittest.TestCase):
    def test_source_mode_never_registers_startup(self):
        with patch.object(platform_win, "get_app_executable_path", return_value=None):
            self.assertFalse(platform_win.set_windows_startup(True, "minimized"))

    def test_source_mode_never_registers_context_menu(self):
        with patch.object(platform_win, "get_app_executable_path", return_value=None):
            self.assertFalse(platform_win.set_windows_context_menu(True))

    def test_shared_windows_clsid_is_not_part_of_owned_keys(self):
        self.assertFalse(any("CLSID" in key for key in platform_win.CONTEXT_MENU_SUBKEYS))
        self.assertFalse(hasattr(platform_win, "WIN11_CLASSIC_MENU_PARENT"))


if __name__ == "__main__":
    unittest.main()
