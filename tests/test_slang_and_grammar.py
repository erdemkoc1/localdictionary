import unittest
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.syntax_engine import SyntaxTranslator
from src.db import DictionaryDB


class TestSlangAndGrammar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.translator = SyntaxTranslator()
        cls.db = DictionaryDB()

    @classmethod
    def tearDownClass(cls):
        cls.translator.conn.close()
        cls.db.close()

    def test_slang_idiom_en_to_tr_toggle(self):
        # When slang is enabled
        res_slang = self.translator.translate("What the fuck", direction="en_tr", show_slang_profanity=True)
        self.assertIn("amk", res_slang["translated_text"].lower())

        # When slang is disabled (clean mode)
        res_clean = self.translator.translate("What the fuck", direction="en_tr", show_slang_profanity=False)
        self.assertNotIn("amk", res_clean["translated_text"].lower())
        self.assertIn("böyle", res_clean["translated_text"].lower())

    def test_slang_idiom_tr_to_en_toggle(self):
        # When slang is enabled
        res_slang = self.translator.translate("siktir git", direction="tr_en", show_slang_profanity=True)
        self.assertIn("fuck", res_slang["translated_text"].lower())

        # When slang is disabled
        res_clean = self.translator.translate("siktir git", direction="tr_en", show_slang_profanity=False)
        self.assertNotIn("fuck", res_clean["translated_text"].lower())
        self.assertIn("out of here", res_clean["translated_text"].lower())

    def test_db_search_slang_filtering(self):
        # Search for a slang word with filter enabled (show_slang_profanity=True)
        results_with_slang, _, _ = self.db.search("fuck", limit=20, show_slang_profanity=True)
        slang_cats = [r["category"] for r in results_with_slang]
        self.assertTrue(any(c in ("Argo / Sokak Dili", "Slang", "Argo") for c in slang_cats))

        # Search for a slang word with filter disabled (show_slang_profanity=False)
        results_without_slang, _, _ = self.db.search("fuck", limit=20, show_slang_profanity=False)
        for r in results_without_slang:
            self.assertNotIn(r["category"], ("Argo / Sokak Dili", "Slang", "Argo"))

    def test_continuous_tense(self):
        res_pres_cont = self.translator.translate("She is working in London.", direction="en_tr")
        self.assertEqual(res_pres_cont["translated_text"], "O Londra'da çalışıyor.")

        res_past_cont = self.translator.translate("She was working in London.", direction="en_tr")
        self.assertEqual(res_past_cont["translated_text"], "O Londra'da çalışıyordu.")

    def test_modal_verbs(self):
        res_must = self.translator.translate("You must work.", direction="en_tr")
        self.assertIn("çalışmalısın", res_must["translated_text"].lower())

        res_should = self.translator.translate("We should go.", direction="en_tr")
        self.assertIn("gitmeliyiz", res_should["translated_text"].lower())

        res_want = self.translator.translate("I want to work.", direction="en_tr")
        self.assertIn("çalışmak istiyorum", res_want["translated_text"].lower())

    def test_subject_proper_name_and_past(self):
        res1 = self.translator.translate("Ayşe works in London.", direction="en_tr")
        self.assertEqual(res1["translated_text"], "Ayşe Londra'da çalışıyor.")

        res2 = self.translator.translate("Jesus created everything.", direction="en_tr")
        self.assertEqual(res2["translated_text"], "İsa her şeyi yarattı.")

        res3 = self.translator.translate("He is a brave soldier.", direction="en_tr")
        self.assertIn("cesur", res3["translated_text"].lower())
        self.assertIn("asker", res3["translated_text"].lower())

    def test_wh_questions(self):
        res_q1 = self.translator.translate("Where do you live?", direction="en_tr")
        self.assertIn("nerede", res_q1["translated_text"].lower())
        self.assertIn("yaşıyorsun", res_q1["translated_text"].lower())

        res_q2 = self.translator.translate("What do you want?", direction="en_tr")
        self.assertIn("ne", res_q2["translated_text"].lower())
        self.assertIn("istiyorsun", res_q2["translated_text"].lower())


    def test_turkish_semantics_and_imperatives(self):
        # 1. Colloquial request with devrik word order (the user's reported bug)
        res1 = self.translator.translate("cevap versene bana", direction="tr_en")
        self.assertEqual(res1["translated_text"], "Answer me.")

        # 2. Standard SOV order
        res2 = self.translator.translate("bana cevap ver", direction="tr_en")
        self.assertEqual(res2["translated_text"], "Answer me.")

        # 3. Compound verb with dative pronoun
        res3 = self.translator.translate("bana yardım et", direction="tr_en")
        self.assertEqual(res3["translated_text"], "Help me.")

        # 4. Conversational expressions
        res4 = self.translator.translate("kendine iyi bak", direction="tr_en")
        self.assertEqual(res4["translated_text"], "Take care of yourself.")

        res5 = self.translator.translate("nasılsın", direction="tr_en")
        self.assertEqual(res5["translated_text"], "How are you?")

        # 5. Look at me with dative
        res6 = self.translator.translate("baksana bana", direction="tr_en")
        self.assertEqual(res6["translated_text"], "Look at me.")

        # 6. Polite imperative with connector
        res7 = self.translator.translate("lütfen bana cevap ver", direction="tr_en")
        self.assertEqual(res7["translated_text"], "Please answer me.")


if __name__ == "__main__":
    unittest.main()

