import os
import sys
import unittest
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.history import HistoryManager

class TestHistoryManager(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.hm = HistoryManager(db_path=self.temp_db.name)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_add_and_retrieve(self):
        self.hm.add_search("computer", "EN ➔ TR", 100)
        self.hm.add_search("başarı", "TR ➔ EN", 100)
        
        recent = self.hm.get_recent()
        self.assertEqual(len(recent), 2)
        # Most recent first
        self.assertEqual(recent[0]["query"], "başarı")
        self.assertEqual(recent[1]["query"], "computer")

    def test_update_existing(self):
        self.hm.add_search("computer", "EN ➔ TR", 100)
        self.hm.add_search("başarı", "TR ➔ EN", 100)
        # Re-search computer
        self.hm.add_search("computer", "EN ➔ TR", 100)

        recent = self.hm.get_recent()
        self.assertEqual(len(recent), 2)
        # "computer" should now be the first item
        self.assertEqual(recent[0]["query"], "computer")

    def test_delete_and_clear(self):
        self.hm.add_search("apple", "EN ➔ TR", 50)
        self.hm.add_search("orange", "EN ➔ TR", 50)
        self.hm.delete_search("apple")

        recent = self.hm.get_recent()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["query"], "orange")

        self.hm.clear_all()
        recent = self.hm.get_recent()
        self.assertEqual(len(recent), 0)

if __name__ == "__main__":
    unittest.main()
