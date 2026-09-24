import unittest
from src.grammar_normalizer import normalize_pos, normalize_role


class TestGrammarNormalizer(unittest.TestCase):
    def test_pos_normalization_turkish(self):
        # Pronouns
        self.assertEqual(normalize_pos("pronoun", "tr"), "Zamir")
        self.assertEqual(normalize_pos("pron.", "tr"), "Zamir")
        self.assertEqual(normalize_pos("pron", "tr"), "Zamir")
        self.assertEqual(normalize_pos("zamir", "tr"), "Zamir")

        # Nouns
        self.assertEqual(normalize_pos("n.", "tr"), "İsim")
        self.assertEqual(normalize_pos("noun", "tr"), "İsim")
        self.assertEqual(normalize_pos("noun (loc)", "tr"), "İsim (Bulunma)")
        self.assertEqual(normalize_pos("noun (pl)", "tr"), "İsim (Çoğul)")

        # Adjectives
        self.assertEqual(normalize_pos("adj.", "tr"), "Sıfat")
        self.assertEqual(normalize_pos("adjective", "tr"), "Sıfat")
        self.assertEqual(normalize_pos("deg_adj", "tr"), "Dereceli Sıfat")

        # Verbs
        self.assertEqual(normalize_pos("v.", "tr"), "Fiil")
        self.assertEqual(normalize_pos("verb", "tr"), "Fiil")
        self.assertEqual(normalize_pos("verb (çekim)", "tr"), "Fiil (Çekimli)")

        # Punctuation & Unknown
        self.assertEqual(normalize_pos("punct", "tr"), "Noktalama")
        self.assertEqual(normalize_pos("unknown", "tr"), "-")
        self.assertEqual(normalize_pos("", "tr"), "-")

    def test_pos_normalization_english(self):
        self.assertEqual(normalize_pos("pronoun", "en"), "Pronoun")
        self.assertEqual(normalize_pos("pron.", "en"), "Pronoun")
        self.assertEqual(normalize_pos("n.", "en"), "Noun")
        self.assertEqual(normalize_pos("adj.", "en"), "Adjective")
        self.assertEqual(normalize_pos("v.", "en"), "Verb")
        self.assertEqual(normalize_pos("punct", "en"), "Punctuation")

    def test_role_normalization(self):
        self.assertEqual(normalize_role("subject", "tr"), "Özne")
        self.assertEqual(normalize_role("verb", "tr"), "Yüklem")
        self.assertEqual(normalize_role("object", "tr"), "Nesne")
        self.assertEqual(normalize_role("adverbial", "tr"), "Zarf Tümleci")
        self.assertEqual(normalize_role("time", "tr"), "Zaman Belirteci")
        self.assertEqual(normalize_role("connector", "tr"), "Bağlantı")

        self.assertEqual(normalize_role("subject", "en"), "Subject")
        self.assertEqual(normalize_role("verb", "en"), "Predicate")
        self.assertEqual(normalize_role("object", "en"), "Object")


if __name__ == "__main__":
    unittest.main()
