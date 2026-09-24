import os
import sys
import unittest

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui import TranslatorApp, SettingsWindow
from src.platform_win import get_windows_context_menu, get_windows_startup

class TestSettingsAndUI(unittest.TestCase):
    def setUp(self):
        self.app = TranslatorApp()

    def tearDown(self):
        self.app.destroy()

    def test_main_window_has_only_two_tabs(self):
        """Verifies requirement: No Ayarlar tab on the main tabview. Only 2 tabs exist."""
        # Check tabview names
        tab_names = list(self.app.tabview._tab_dict.keys())
        self.assertEqual(len(tab_names), 2)
        self.assertIn(self.app.tab_dict_name, tab_names)
        self.assertIn(self.app.tab_sentence_name, tab_names)

    def test_open_settings_window(self):
        """Verifies clicking settings button opens the dedicated SettingsWindow modal."""
        self.app.open_settings_window()
        self.assertIsNotNone(self.app.settings_window)
        self.assertTrue(self.app.settings_window.winfo_exists())

        sw = self.app.settings_window

        # Test Theme switch
        sw.on_theme_changed("☀️ Açık (Light)")
        self.assertEqual(self.app.current_theme, "light")
        self.assertEqual(self.app.settings.get("theme"), "light")

        sw.on_theme_changed("🌙 Koyu (Dark)")
        self.assertEqual(self.app.current_theme, "dark")
        self.assertEqual(self.app.settings.get("theme"), "dark")

        # Test Always on Top
        sw.always_on_top_switch.select()
        sw.on_always_on_top_changed()
        self.assertTrue(self.app.settings.get("always_on_top"))

        sw.always_on_top_switch.deselect()
        sw.on_always_on_top_changed()
        self.assertFalse(self.app.settings.get("always_on_top"))

        # Test Language switch
        sw.on_language_changed("🇬🇧 English")
        self.assertEqual(self.app.settings.get("language"), "en")
        self.assertEqual(self.app.search_btn.cget("text"), "Search")
        self.assertEqual(self.app.settings_btn.cget("text"), "⚙️ Settings")
        self.assertEqual(self.app.tab_dict_name, "Dictionary")

        sw.on_language_changed("🇹🇷 Türkçe")
        self.assertEqual(self.app.settings.get("language"), "tr")
        self.assertEqual(self.app.search_btn.cget("text"), "Ara")
        self.assertEqual(self.app.settings_btn.cget("text"), "⚙️ Ayarlar")
        self.assertEqual(self.app.tab_dict_name, "Sözlük")

        # Test Dual Right Click Options
        # Option 1: Ctrl + Right Click
        sw.ctrl_rc_switch.select()
        sw.on_ctrl_rc_changed()
        self.assertTrue(self.app.settings.get("ctrl_right_click_translate"))

        sw.ctrl_rc_switch.deselect()
        sw.on_ctrl_rc_changed()
        self.assertFalse(self.app.settings.get("ctrl_right_click_translate"))

        # Option 2: Windows Context Menu
        sw.win_ctx_switch.select()
        sw.on_win_ctx_changed()
        self.assertTrue(self.app.settings.get("windows_context_menu"))
        self.assertTrue(get_windows_context_menu())

        sw.win_ctx_switch.deselect()
        sw.on_win_ctx_changed()
        self.assertFalse(self.app.settings.get("windows_context_menu"))
        self.assertFalse(get_windows_context_menu())

        # Test Startup Options
        sw.startup_switch.select()
        sw.on_startup_changed()
        self.assertTrue(self.app.settings.get("run_on_startup"))
        is_reg, reg_mode = get_windows_startup()
        self.assertTrue(is_reg)

        sw.on_startup_mode_changed("📥 Altta Açık (Simge Durumunda / Tepside)")
        self.assertEqual(self.app.settings.get("startup_mode"), "minimized")
        is_reg, reg_mode = get_windows_startup()
        self.assertTrue(is_reg)
        self.assertEqual(reg_mode, "minimized")

        sw.startup_switch.deselect()
        sw.on_startup_changed()
        self.assertFalse(self.app.settings.get("run_on_startup"))
        is_reg, _ = get_windows_startup()
        self.assertFalse(is_reg)

        # Restore active settings
        sw.ctrl_rc_switch.select()
        sw.on_ctrl_rc_changed()
        sw.win_ctx_switch.select()
        sw.on_win_ctx_changed()

        # Close settings window
        sw.destroy()

    def test_quick_popup_and_button(self):
        # Test QuickTranslatePopup
        self.app.show_quick_popup("test", "test çevirisi", 200, 200)
        self.assertIsNotNone(self.app.current_popup)
        self.assertTrue(self.app.current_popup.winfo_exists())
        self.app.current_popup.safe_destroy()

        # Test QuickTranslateButton
        self.app.show_quick_button("test button", 250, 250)
        self.assertIsNotNone(self.app.current_quick_btn)
        self.assertTrue(self.app.current_quick_btn.winfo_exists())
        self.app.current_quick_btn.safe_destroy()

if __name__ == "__main__":
    unittest.main()
