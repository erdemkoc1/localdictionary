import sys
import os
import unittest
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.settings import SettingsManager, TRANSLATIONS

class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.tmp.close()
        self.sm = SettingsManager(self.tmp.name)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.remove(self.tmp.name)

    def test_default_values(self):
        self.assertEqual(self.sm.get("theme"), "dark")
        self.assertEqual(self.sm.get("language"), "en")
        self.assertFalse(self.sm.get("ctrl_right_click_translate"))
        self.assertFalse(self.sm.get("windows_context_menu"))
        self.assertFalse(self.sm.get("run_on_startup"))
        self.assertEqual(self.sm.get("startup_mode"), "normal")
        self.assertFalse(self.sm.get("always_on_top"))
        self.assertTrue(self.sm.get("minimize_to_tray"))
        self.assertFalse(self.sm.get("selection_translate"))
        self.assertFalse(self.sm.get("double_click_translate"))

    def test_save_and_load(self):
        self.sm.set("theme", "light")
        self.sm.set("language", "en")
        self.sm.set("ctrl_right_click_translate", False)
        self.sm.set("windows_context_menu", True)
        self.sm.set("run_on_startup", True)
        self.sm.set("startup_mode", "minimized")
        self.sm.set("double_click_translate", True)

        # Reload from same file
        sm2 = SettingsManager(self.tmp.name)
        self.assertEqual(sm2.get("theme"), "light")
        self.assertEqual(sm2.get("language"), "en")
        self.assertFalse(sm2.get("ctrl_right_click_translate"))
        self.assertTrue(sm2.get("windows_context_menu"))
        self.assertTrue(sm2.get("run_on_startup"))
        self.assertEqual(sm2.get("startup_mode"), "minimized")
        self.assertTrue(sm2.get("double_click_translate"))

    def test_translations_coverage(self):
        tr_keys = set(TRANSLATIONS["tr"].keys())
        en_keys = set(TRANSLATIONS["en"].keys())
        self.assertEqual(tr_keys, en_keys, f"Missing translation keys: {tr_keys ^ en_keys}")

    def test_get_text(self):
        self.sm.set("language", "tr")
        self.assertEqual(self.sm.get_text("search_btn"), "Ara")
        self.sm.set("language", "en")
        self.assertEqual(self.sm.get_text("search_btn"), "Search")

if __name__ == "__main__":
    unittest.main()
