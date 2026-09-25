import os
import sys
import unittest

sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db import DictionaryDB

class TestDictionaryDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DictionaryDB()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_exact_en_search(self):
        results, elapsed, direction = self.db.search("computer", mode="en_tr")
        self.assertGreater(len(results), 0)
        self.assertEqual(direction, "EN ➔ TR")
        self.assertLess(elapsed, 20.0) # Should be sub-millisecond, definitely < 20ms
        targets = [r["target"] for r in results]
        self.assertTrue(any("bilgisayar" in t.lower() for t in targets))
        print(f"\n[TEST] EN search 'computer': {len(results)} results in {elapsed:.2f} ms")

    def test_exact_tr_search(self):
        results, elapsed, direction = self.db.search("başarı", mode="tr_en")
        self.assertGreater(len(results), 0)
        self.assertEqual(direction, "TR ➔ EN")
        targets = [r["target"] for r in results]
        self.assertTrue(any("achievement" in t.lower() or "accomplishment" in t.lower() for t in targets))
        print(f"[TEST] TR search 'başarı': {len(results)} results in {elapsed:.2f} ms")

    def test_prefix_search(self):
        results, elapsed, _ = self.db.search("compu", mode="en_tr")
        self.assertGreater(len(results), 0)
        print(f"[TEST] Prefix search 'compu': {len(results)} results in {elapsed:.2f} ms")

    def test_turkish_characters(self):
        results, elapsed, direction = self.db.search("ırmak", mode="auto")
        self.assertGreater(len(results), 0)
        self.assertEqual(direction, "TR ➔ EN")
        targets = [r["target"] for r in results]
        self.assertTrue(any("river" in t.lower() for t in targets))
        print(f"[TEST] Turkish char search 'ırmak': {len(results)} results in {elapsed:.2f} ms")

    def test_no_restricted_source_rows(self):
        self.db.cur.execute("SELECT COUNT(*) FROM bilingual WHERE category LIKE '%TDK%'")
        self.assertEqual(self.db.cur.fetchone()[0], 0)

    def test_database_metadata_exists(self):
        self.db.cur.execute("SELECT value FROM db_metadata WHERE key = 'restricted_source_data_removed'")
        self.assertEqual(self.db.cur.fetchone()[0], "1")

if __name__ == "__main__":
    unittest.main()
