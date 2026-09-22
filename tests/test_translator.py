import os
import sys
import unittest

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.translator import SentenceTranslator

class TestSentenceTranslator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.translator = SentenceTranslator()

    def test_en_to_tr_translation(self):
        text = "Hello world, this is a test sentence."
        res, from_c, to_c = self.translator.translate(text, "en", "tr")
        print(f"\n[TEST NMT EN->TR]: {text} -> {res}")
        self.assertEqual(from_c, "en")
        self.assertEqual(to_c, "tr")
        self.assertGreater(len(res), 0)

    def test_tr_to_en_translation(self):
        text = "Bugün hava gerçekten çok güzel."
        res, from_c, to_c = self.translator.translate(text, "tr", "en")
        print(f"[TEST NMT TR->EN]: {text} -> {res}")
        self.assertEqual(from_c, "tr")
        self.assertEqual(to_c, "en")
        self.assertGreater(len(res), 0)

if __name__ == "__main__":
    unittest.main()
