import os
import sys
import unittest
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.translator import SentenceTranslator
from src.user_data import UserDataManager

class TestSentenceTranslator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(prefix="localdictionary-translator-test-")
        cls.user_data = UserDataManager(os.path.join(cls.temp_dir.name, "user_data.db"))
        cls.translator = SentenceTranslator(user_data=cls.user_data)

    @classmethod
    def tearDownClass(cls):
        cls.translator.user_data = None
        cls.temp_dir.cleanup()

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

    def test_complex_academic_nmt_sentences(self):
        cases = [
            "Although the empirical evidence seemed conclusive at first glance, the researchers hesitated to publish their findings until the anomalies were systematically eliminated.",
            "Caught between professional ambition and emotional burnout, she realized that relentless productivity had slowly eroded her capacity for genuine joy.",
            "The sudden blackout plunged the bustling subway station into complete darkness, leaving commuters to navigate the echoing corridors with nothing but the faint glow of their smartphones.",
            "As algorithmic automation reshapes global labor markets, the boundary between indispensable human creativity and mere operational redundancy is becoming increasingly blurred.",
            "Had they anticipated the sudden shift in consumer behavior, they would have restructured their core supply chain long before the financial quarter collapsed."
        ]
        for sentence in cases:
            res, from_c, to_c = self.translator.translate(sentence, "en", "tr")
            self.assertEqual(from_c, "en")
            self.assertEqual(to_c, "tr")
            self.assertGreater(len(res), 15)
            # Verify translation output is fluent Turkish rather than empty or identical
            self.assertNotEqual(res, sentence)
            print(f"\n[COMPLEX NMT EN->TR]\nIN : {sentence}\nOUT: {res}")


    def test_multisentence_slang_hybrid(self):
        text = "Benimle denk değilsin. Beni kimse sokak kavgasında yenemez. sikeyim seni."
        res = self.translator.translate(text, "tr", "en", show_slang_profanity=True)
        res_str = res["translated_text"].lower()
        print(f"\n[MULTI-SENTENCE SLANG HYBRID TR->EN]:\nIN : {text}\nOUT: {res['translated_text']}")
        self.assertIn("fuck you", res_str)
        self.assertIn("street fight", res_str)

    def test_greetings_and_titles(self):
        cases = [
            ("merhaba ayşe hanım", "Hello Ms. Ayşe."),
            ("günaydın ali bey", "Good morning Mr. Ali."),
            ("cevap versene bana", "Answer me.")
        ]
        for src, expected in cases:
            res = self.translator.translate(src, "tr", "en")
            print(f"\n[GREETING / TITLE TEST]: {src} -> {res.translated_text}")
            self.assertEqual(res.translated_text.strip(), expected)


if __name__ == "__main__":
    unittest.main()



