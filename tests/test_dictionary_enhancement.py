import sys
import os
import unittest

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db import DictionaryDB

class TestDictionaryEnhancement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DictionaryDB()
        cls.db.search("warmup")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_turkish_inflections(self):
        cases = ["geldi", "gitti", "okulda", "evden", "kitaplar", "çocuklar", "yaptı"]
        for word in cases:
            results, elapsed_ms, direction = self.db.search(word, limit=5)
            self.assertGreater(len(results), 0, f"No results for Turkish inflection: {word}")
            self.assertEqual(direction, "TR ➔ EN", f"Wrong direction for {word}")
            self.assertLess(elapsed_ms, 50.0, f"Search took too long: {elapsed_ms}ms")

    def test_english_inflections_and_irregulars(self):
        cases = ["went", "saw", "running", "better", "created", "worked"]
        for word in cases:
            results, elapsed_ms, direction = self.db.search(word, limit=5)
            self.assertGreater(len(results), 0, f"No results for English word: {word}")
            self.assertEqual(direction, "EN ➔ TR", f"Wrong direction for {word}")
            self.assertLess(elapsed_ms, 50.0, f"Search took too long: {elapsed_ms}ms")

    def test_idioms_and_proverbs(self):
        idioms = [
            ("damlaya damlaya göl olur", ["lake", "mickle", "niceliğe", "penny"]),
            ("göz yummak", ["blind eye", "overlook", "condone", "görmezlikten"]),
            ("etekleri zil", ["thrilled", "overjoyed", "sevinmek"])
        ]
        for query, expected_keywords in idioms:
            results, elapsed_ms, direction = self.db.search(query, limit=5)
            self.assertGreater(len(results), 0, f"No results for idiom: {query}")
            all_targets = " ".join([r["target"].lower() for r in results])
            matched = any(kw.lower() in all_targets for kw in expected_keywords)
            self.assertTrue(matched, f"None of keywords {expected_keywords} found in {all_targets}")

    def test_fallbacks(self):
        # Common bilingual entry remains available without monolingual data.
        res, ms, d = self.db.search("computer", mode="en_tr")
        self.assertGreater(len(res), 0)
        self.assertIn("bilgisayar", res[0]["target"].lower())

        # Morphological analysis test for complex suffix
        res, ms, d = self.db.search("aradıysam")
        self.assertGreater(len(res), 0)
        self.assertIn("aramak", res[0]["source"])

if __name__ == "__main__":
    unittest.main()
