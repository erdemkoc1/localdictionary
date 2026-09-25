import os
import sys
import unittest

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.syntax_engine import SyntaxTranslator


class TestSyntax(unittest.TestCase):
    def setUp(self):
        self.translator = SyntaxTranslator()

    def tearDown(self):
        self.translator.conn.close()

    def test_english_and_turkish_examples(self):
        english_cases = [
            "Ayşe works in London.",
            "She works in London.",
            "My brother lives in London.",
            "Ayşe is a teacher.",
            "John lives in Paris.",
            "Ali goes to school.",
            "I want a computer for my brother.",
            "We will meet tomorrow.",
            "I saw a beautiful book yesterday.",
            "The doctor works in the hospital.",
        ]
        for sentence in english_cases:
            result = self.translator.translate(sentence, "auto")
            self.assertTrue(result["translated_text"])
            self.assertIsInstance(result["breakdown"], list)

        turkish_cases = [
            "O Londra'da çalışıyor.",
            "Ayşe bir öğretmendir.",
            "Ali okula gidiyor.",
            "Ben su içtim.",
        ]
        for sentence in turkish_cases:
            result = self.translator.translate(sentence, "auto")
            self.assertTrue(result["translated_text"])
            self.assertIsInstance(result["breakdown"], list)


if __name__ == "__main__":
    unittest.main()
