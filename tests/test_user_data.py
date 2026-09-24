import sys
import os
import unittest
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.user_data import UserDataManager
from src.clause_splitter import split_into_clauses, evaluate_confidence


class TestUserDataManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.tmp.close()
        self.udm = UserDataManager(self.tmp.name)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            try:
                os.remove(self.tmp.name)
            except Exception:
                pass

    def test_cache_save_and_retrieve(self):
        self.udm.set_cached_translation(
            source_text="Hello world",
            from_lang="en",
            to_lang="tr",
            translated_text="Merhaba dünya",
            engine="nmt",
            confidence=90
        )
        
        cached = self.udm.get_cached_translation("hello world", "en", "tr")
        self.assertIsNotNone(cached)
        self.assertEqual(cached["translated_text"], "Merhaba dünya")
        self.assertEqual(cached["engine"], "cache")
        self.assertEqual(cached["confidence"], 90)

    def test_corrections_save_and_retrieve(self):
        self.udm.save_correction(
            source_text="Machine learning is awesome.",
            corrected_text="Makine öğrenimi harikadır.",
            from_lang="en",
            to_lang="tr"
        )

        corr = self.udm.get_correction("machine learning is awesome.", "en", "tr")
        self.assertEqual(corr, "Makine öğrenimi harikadır.")

        # Non-existent correction should return None
        self.assertIsNone(self.udm.get_correction("Unknown text", "en", "tr"))

    def test_glossary_crud_and_apply(self):
        # Add term
        term_id = self.udm.add_glossary_term("prompt engineering", "istem mühendisliği", "en_tr")
        self.assertIsInstance(term_id, int)

        terms = self.udm.get_glossary_terms()
        self.assertTrue(any(t["source_term"] == "prompt engineering" for t in terms))

        # Apply glossary to translated text
        text = "Today we study prompt engineering in depth."
        modified = self.udm.apply_glossary_to_text(text, from_lang="en", to_lang="tr")
        self.assertIn("istem mühendisliği", modified)

        # Delete term
        deleted = self.udm.delete_glossary_term(term_id)
        self.assertTrue(deleted)
        terms_after = self.udm.get_glossary_terms()
        self.assertFalse(any(t["id"] == term_id for t in terms_after))


class TestClauseSplitterAndConfidence(unittest.TestCase):
    def test_clause_splitting_english(self):
        long_sentence = (
            "Although the empirical evidence seemed conclusive at first glance, "
            "the researchers hesitated to publish their findings until the anomalies were systematically eliminated."
        )
        clauses = split_into_clauses(long_sentence, lang="en")
        self.assertGreater(len(clauses), 1)

    def test_clause_splitting_turkish(self):
        tr_sentence = (
            "Hava çok soğuk olduğu için dışarı çıkamadık, "
            "oysa arkadaşlarımız sahilde buluşmak üzere sözleşmişlerdi."
        )
        clauses = split_into_clauses(tr_sentence, lang="tr")
        self.assertGreater(len(clauses), 1)

    def test_short_sentence_no_split(self):
        short = "This is a simple sentence."
        clauses = split_into_clauses(short, lang="en")
        self.assertEqual(len(clauses), 1)

    def test_confidence_evaluation(self):
        # Normal good translation
        conf, level = evaluate_confidence(
            input_text="Good morning",
            output_text="Günaydın",
            engine="nmt",
            from_code="en",
            to_code="tr"
        )
        self.assertGreaterEqual(conf, 70)
        self.assertIn(level, ("high", "medium"))

        # User correction should be 100
        conf_user, level_user = evaluate_confidence(
            input_text="Test",
            output_text="Test",
            engine="user_correction",
            from_code="en",
            to_code="tr"
        )
        self.assertEqual(conf_user, 100)
        self.assertEqual(level_user, "high")

        # Untranslated text (exact match when langs differ) should be low
        conf_bad, level_bad = evaluate_confidence(
            input_text="Supercalifragilisticexpialidocious sentence with complex nouns",
            output_text="Supercalifragilisticexpialidocious sentence with complex nouns",
            engine="syntax",
            from_code="en",
            to_code="tr"
        )
        self.assertLess(conf_bad, 65)


if __name__ == "__main__":
    unittest.main()
