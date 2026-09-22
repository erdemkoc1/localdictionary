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
        self.assertEqual(self.sm.get("language"), "tr")
        self.assertTrue(self.sm.get("right_click_translate"))

    def test_save_and_load(self):
        self.sm.set("theme", "light")
        self.sm.set("language", "en")
        self.sm.set("right_click_translate", False)

        # Reload from same file
        sm2 = SettingsManager(self.tmp.name)
        self.assertEqual(sm2.get("theme"), "light")
        self.assertEqual(sm2.get("language"), "en")
        self.assertFalse(sm2.get("right_click_translate"))

    def test_translations_coverage(self):
        # Ensure all keys in Turkish exist in English
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
