import os
import sys
import unittest

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui import TranslatorApp

class TestSettingsAndUI(unittest.TestCase):
    def setUp(self):
        self.app = TranslatorApp()

    def tearDown(self):
        self.app.destroy()

    def test_theme_change(self):
        self.app.on_theme_changed("☀️ Açık (Light)")
        self.assertEqual(self.app.current_theme, "light")
        self.assertEqual(self.app.settings.get("theme"), "light")

        self.app.on_theme_changed("🌙 Koyu (Dark)")
        self.assertEqual(self.app.current_theme, "dark")
        self.assertEqual(self.app.settings.get("theme"), "dark")

    def test_language_switch_english_and_turkish(self):
        # Switch to English
        self.app.on_language_changed("🇬🇧 English")
        self.assertEqual(self.app.settings.get("language"), "en")
        self.assertEqual(self.app.search_btn.cget("text"), "Search")
        self.assertEqual(self.app.settings_btn.cget("text"), "⚙️ Settings")
        self.assertEqual(self.app.tab_dict_name, "🔍 Dictionary / Word Search")
        self.assertIn("Dictionary", self.app.tabview.get())

        # Switch back to Turkish
        self.app.on_language_changed("🇹🇷 Türkçe")
        self.assertEqual(self.app.settings.get("language"), "tr")
        self.assertEqual(self.app.search_btn.cget("text"), "Ara")
        self.assertEqual(self.app.settings_btn.cget("text"), "⚙️ Ayarlar")
        self.assertEqual(self.app.tab_dict_name, "🔍 Sözlük / Kelime Arama")

    def test_right_click_settings(self):
        self.app.rc_switch.select()
        self.app.on_rc_switch_changed()
        self.assertTrue(self.app.settings.get("right_click_translate"))

        self.app.rc_switch.deselect()
        self.app.on_rc_switch_changed()
        self.assertFalse(self.app.settings.get("right_click_translate"))

        self.app.on_trigger_changed("Ctrl + Sağ Tık")
        self.assertEqual(self.app.settings.get("right_click_trigger"), "ctrl_right_click")

    def test_quick_popup(self):
        self.app.show_quick_popup("test", "test çevirisi", 200, 200)
        self.assertIsNotNone(self.app.current_popup)
        self.assertTrue(self.app.current_popup.winfo_exists())
        self.app.current_popup.safe_destroy()

if __name__ == "__main__":
    unittest.main()
