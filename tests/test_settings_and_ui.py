import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.gui import TranslatorApp, SettingsWindow


class TestSettingsAndUI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="localdictionary-test-")
        self.app = TranslatorApp(
            settings_file=os.path.join(self.temp_dir.name, "settings.json"),
            user_data_dir=self.temp_dir.name,
        )

    def tearDown(self):
        try:
            self.app.destroy()
        finally:
            self.temp_dir.cleanup()

    def test_main_window_has_only_two_tabs(self):
        tab_names = list(self.app.tabview._tab_dict.keys())
        self.assertEqual(len(tab_names), 2)
        self.assertIn(self.app.tab_dict_name, tab_names)
        self.assertIn(self.app.tab_sentence_name, tab_names)

    def test_first_launch_is_english_and_global_features_are_opt_in(self):
        self.assertEqual(self.app.settings.get("language"), "en")
        self.assertFalse(self.app.settings.get("ctrl_right_click_translate"))
        self.assertFalse(self.app.settings.get("selection_translate"))
        self.assertFalse(self.app.settings.get("double_click_translate"))
        self.assertFalse(self.app.settings.get("right_click_translate"))
        self.assertFalse(self.app.settings.get("windows_context_menu"))
        self.assertFalse(self.app.settings.get("run_on_startup"))
        self.assertFalse(self.app.quick_service.running)

    def test_open_settings_window_and_persist_language(self):
        self.app.open_settings_window()
        self.assertIsNotNone(self.app.settings_window)
        window = self.app.settings_window
        window.on_language_changed("🇹🇷 Türkçe")
        self.assertEqual(self.app.settings.get("language"), "tr")

        reloaded = type(self.app.settings)(
            os.path.join(self.temp_dir.name, "settings.json")
        )
        self.assertEqual(reloaded.get("language"), "tr")

    def test_quick_feature_toggle_starts_and_stops_service(self):
        self.app.open_settings_window()
        window = self.app.settings_window
        window.selection_switch.select()
        window.on_selection_changed()
        self.assertTrue(self.app.settings.get("selection_translate"))
        self.assertTrue(self.app.quick_service.running)

        window.selection_switch.deselect()
        window.on_selection_changed()
        self.assertFalse(self.app.settings.get("selection_translate"))
        self.app.quick_service.stop()
        self.assertFalse(self.app.quick_service.running)

    def test_in_app_toggle_never_writes_windows_registry(self):
        self.app.open_settings_window()
        window = self.app.settings_window
        with patch("src.gui.set_windows_context_menu", return_value=True) as context:
            with patch("src.gui.set_windows_startup", return_value=True) as startup:
                window.win_ctx_switch.select()
                window.on_win_ctx_changed()
                window.win_ctx_switch.deselect()
                window.on_win_ctx_changed()
        self.assertEqual(context.call_count, 2)
        self.assertEqual(startup.call_count, 0)

    def test_quick_popup_and_button(self):
        self.app.show_quick_popup("test", "test çevirisi", 200, 200)
        self.assertTrue(self.app.current_popup.winfo_exists())
        self.app.current_popup.safe_destroy()

        self.app.show_quick_button("test button", 250, 250)
        self.assertTrue(self.app.current_quick_btn.winfo_exists())
        self.app.current_quick_btn.safe_destroy()


if __name__ == "__main__":
    unittest.main()
