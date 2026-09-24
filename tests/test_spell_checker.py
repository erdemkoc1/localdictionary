import unittest
from src.db import DictionaryDB
from src.spell_checker import SpellChecker
from src.syntax_engine import SyntaxTranslator
from src.translator import SentenceTranslator


class TestSpellCheckerAndTenses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DictionaryDB()
        cls.sc = SpellChecker(db_conn=cls.db.conn)
        cls.st = SyntaxTranslator(db_path=cls.db.db_path)
        cls.tr = SentenceTranslator(syntax_engine=cls.st)

    def test_word_spell_suggestions(self):
        # Turkish de-asciification
        self.assertEqual(self.sc.get_word_suggestion("aldatti"), "aldattı")
        self.assertEqual(self.sc.get_word_suggestion("karim"), "karım")
        self.assertEqual(self.sc.get_word_suggestion("guzel"), "güzel")
        self.assertEqual(self.sc.get_word_suggestion("ogretmen"), "öğretmen")
        
        # English typo
        en_sugg = self.sc.get_word_suggestion("computr", is_en=True)
        self.assertEqual(en_sugg, "compute")  # or computer

    def test_sentence_spell_suggestion(self):
        sugg = self.sc.get_sentence_suggestion("karim beni aldatti maalesef")
        self.assertIsNotNone(sugg)
        self.assertIn("karım", sugg)
        self.assertIn("aldattı", sugg)
        self.assertEqual(sugg, "karım beni aldattı maalesef")

    def test_karim_aldatti_translations(self):
        # Syntax engine directly
        res1 = self.st.translate("karım beni aldattı maalesef", direction="tr_en")
        self.assertEqual(res1["translated_text"], "My wife cheated on me, unfortunately.")

        res2 = self.st.translate("karım beni aldattı", direction="tr_en")
        self.assertEqual(res2["translated_text"], "My wife cheated on me.")

        res3 = self.st.translate("maalesef karım beni aldattı", direction="tr_en")
        self.assertEqual(res3["translated_text"], "Unfortunately, my wife cheated on me.")

        # Kinship noun protection (not snow)
        self.assertFalse(any("snow" in b.get("translated", "").lower() for b in res1["breakdown"]))
        self.assertTrue(any("wife" in b.get("translated", "").lower() for b in res1["breakdown"]))


if __name__ == "__main__":
    unittest.main()
