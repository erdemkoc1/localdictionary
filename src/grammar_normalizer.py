"""
Grammar and Part-of-Speech (POS) Normalizer
Provides unified, clean, and consistent categories for grammar tags and sentence roles.
Prevents duplicate/inconsistent tags such as 'pronoun' vs 'pron.', 'noun' vs 'n.', etc.
Supports Turkish and English localization.
"""

from typing import Optional


# Unified POS mapping table
# Key: normalized lower-case raw tag
# Value: (Turkish Name, English Name)
POS_MAP = {
    # Pronoun / Zamir
    "pronoun": ("Zamir", "Pronoun"),
    "pron.": ("Zamir", "Pronoun"),
    "pron": ("Zamir", "Pronoun"),
    "zamir": ("Zamir", "Pronoun"),
    "prn": ("Zamir", "Pronoun"),
    "pers_pron": ("Zamir", "Pronoun"),
    "poss_pron": ("İyelik Zamiri", "Possessive Pronoun"),

    # Noun / İsim
    "noun": ("İsim", "Noun"),
    "n.": ("İsim", "Noun"),
    "n": ("İsim", "Noun"),
    "isim": ("İsim", "Noun"),
    "ad": ("İsim", "Noun"),
    "noun (loc)": ("İsim (Bulunma)", "Noun (Locative)"),
    "noun (abl)": ("İsim (Ayrılma)", "Noun (Ablative)"),
    "noun (dat)": ("İsim (Yönelme)", "Noun (Dative)"),
    "noun (acc)": ("İsim (Belirtme)", "Noun (Accusative)"),
    "noun (gen)": ("İsim (İyelik)", "Noun (Genitive)"),
    "noun (pl)": ("İsim (Çoğul)", "Noun (Plural)"),
    "noun (ins)": ("İsim (Vasıta)", "Noun (Instrumental)"),
    "noun (çekim)": ("İsim (Çekimli)", "Noun (Inflected)"),
    "indef_np": ("İsim Tamlaması", "Noun Phrase"),
    "def_np": ("Belirtili İsim", "Definite Noun Phrase"),
    "possessive_np": ("İyelik Tamlaması", "Possessive Phrase"),

    # Proper Noun / Özel İsim
    "proper_noun": ("Özel İsim", "Proper Noun"),
    "prop_noun_case": ("Özel İsim (Halli)", "Proper Noun (Cased)"),
    "prop. n.": ("Özel İsim", "Proper Noun"),

    # Adjective / Sıfat
    "adjective": ("Sıfat", "Adjective"),
    "adj.": ("Sıfat", "Adjective"),
    "adj": ("Sıfat", "Adjective"),
    "sıfat": ("Sıfat", "Adjective"),
    "deg_adj": ("Dereceli Sıfat", "Degree Adjective"),
    "adj_np": ("Sıfat Tamlaması", "Adjective Phrase"),
    "def_adj_np": ("Belirtili Sıfat Tamlaması", "Definite Adj. Phrase"),

    # Verb / Fiil
    "verb": ("Fiil", "Verb"),
    "v.": ("Fiil", "Verb"),
    "v": ("Fiil", "Verb"),
    "fiil": ("Fiil", "Verb"),
    "eylem": ("Fiil", "Verb"),
    "verb (çekim)": ("Fiil (Çekimli)", "Verb (Inflected)"),
    "verb (past)": ("Fiil (Geçmiş Zaman)", "Verb (Past)"),
    "verb (pres)": ("Fiil (Şimdiki Zaman)", "Verb (Present)"),
    "verb (fut)": ("Fiil (Gelecek Zaman)", "Verb (Future)"),
    "copula": ("Ek-Fiil", "Copula"),
    "copula_negation": ("Ek-Fiil (Olumsuz)", "Negative Copula"),

    # Adverb / Zarf
    "adverb": ("Zarf", "Adverb"),
    "adv.": ("Zarf", "Adverb"),
    "adv": ("Zarf", "Adverb"),
    "zarf": ("Zarf", "Adverb"),

    # Preposition & Postposition / Edat
    "preposition": ("Edat", "Preposition"),
    "prep.": ("Edat", "Preposition"),
    "prep": ("Edat", "Preposition"),
    "postposition": ("Edat (Sonsöz)", "Postposition"),
    "prep_phrase": ("Edat Öbeği", "Prepositional Phrase"),
    "edat": ("Edat", "Preposition"),

    # Conjunction / Bağlaç
    "conjunction": ("Bağlaç", "Conjunction"),
    "conj.": ("Bağlaç", "Conjunction"),
    "conj": ("Bağlaç", "Conjunction"),
    "bağlaç": ("Bağlaç", "Conjunction"),

    # Determiner & Article / Belirteç
    "determiner": ("Belirteç", "Determiner"),
    "det": ("Belirteç", "Determiner"),
    "det.": ("Belirteç", "Determiner"),
    "article": ("Tanımlık", "Article"),
    "art": ("Tanımlık", "Article"),
    "art.": ("Tanımlık", "Article"),

    # Interjection & Greetings & Idiom & Slang / Ünlem & Selamlama & Deyim & Argo
    "interjection": ("Ünlem", "Interjection"),
    "interj.": ("Ünlem", "Interjection"),
    "ünlem": ("Ünlem", "Interjection"),
    "greeting": ("Ünlem (Selamlama)", "Interjection (Greeting)"),
    "vocative": ("Hitap / Özel İsim", "Vocative / Proper Noun"),
    "title": ("Unvan / San", "Title / Honorific"),
    "title_np": ("Unvan / San", "Title / Honorific"),
    "idiom": ("Deyim / Kalıp", "Idiom / Expression"),
    "deyim": ("Deyim / Kalıp", "Idiom / Expression"),
    "slang": ("Argo", "Slang"),
    "argo": ("Argo", "Slang"),
    "wh_word": ("Soru Sözcüğü", "Interrogative"),

    # Punctuation / Noktalama
    "punct": ("Noktalama", "Punctuation"),
    "punctuation": ("Noktalama", "Punctuation"),
    "noktalama": ("Noktalama", "Punctuation"),

    # Unknown
    "unknown": ("-", "-"),
    "unknown_pos": ("-", "-"),
    "-": ("-", "-"),
    "?": ("-", "-")
}


# Unified Sentence Roles Mapping
# Key: normalized lower-case role name
# Value: (Turkish Name, English Name)
ROLE_MAP = {
    "subject": ("Özne", "Subject"),
    "verb": ("Yüklem", "Predicate"),
    "object": ("Nesne", "Object"),
    "greeting": ("Hitap / Selamlama", "Greeting / Salutation"),
    "vocative": ("Hitap / Seslenme", "Vocative / Address"),
    "title_np": ("Unvan / Hitap", "Honorific / Title"),
    "adverbial": ("Zarf Tümleci", "Adverbial"),
    "time": ("Zaman Belirteci", "Time Adverbial"),
    "connector": ("Bağlantı", "Connector"),
    "determiner": ("Belirteç", "Determiner"),
    "adjective": ("Sıfat Tamlaması", "Adjective Modifier"),
    "copula_predicate": ("Ek-Fiil Yüklemi", "Copula Predicate"),
    "copula_negation": ("Ek-Fiil (Olumsuz)", "Negative Copula"),
    "possessive": ("Tamlayan", "Possessive"),
    "expression": ("Kalıp İfade", "Idiomatic Expression"),
    "idiom": ("Kalıp İfade", "Idiomatic Expression"),
    "punct": ("Noktalama", "Punctuation"),
    "prop_noun_case": ("Özel İsim Tümleci", "Proper Noun Modifier"),
    "question_wh": ("Soru Belirteci", "Interrogative Modifier"),
    "unknown": ("Tümleç", "Complement")
}


def normalize_pos(raw_pos: Optional[str], lang: str = "tr") -> str:
    """
    Normalizes arbitrary POS strings into a consistent, unified label.
    Example: 'pronoun' or 'pron.' -> 'Zamir' (TR) or 'Pronoun' (EN)
    """
    if not raw_pos:
        return "-"
    
    clean = raw_pos.strip().lower()
    
    # 1. Exact match in POS_MAP
    if clean in POS_MAP:
        tr, en = POS_MAP[clean]
        return tr if lang == "tr" else en

    # 2. Substring heuristics
    if "pron" in clean or "zamir" in clean:
        return "Zamir" if lang == "tr" else "Pronoun"
    if "adj" in clean or "sıfat" in clean:
        return "Sıfat" if lang == "tr" else "Adjective"
    if "noun" in clean or clean.startswith("n.") or "isim" in clean:
        return "İsim" if lang == "tr" else "Noun"
    if "verb" in clean or clean.startswith("v.") or "fiil" in clean:
        return "Fiil" if lang == "tr" else "Verb"
    if "adv" in clean or "zarf" in clean:
        return "Zarf" if lang == "tr" else "Adverb"
    if "prep" in clean or "postpos" in clean or "edat" in clean:
        return "Edat" if lang == "tr" else "Preposition"
    if "conj" in clean or "bağlaç" in clean:
        return "Bağlaç" if lang == "tr" else "Conjunction"
    if "punct" in clean or "nokta" in clean:
        return "Noktalama" if lang == "tr" else "Punctuation"
    if "idiom" in clean or "deyim" in clean or "expression" in clean:
        return "Deyim / Kalıp" if lang == "tr" else "Idiom / Phrase"
    if "slang" in clean or "argo" in clean:
        return "Argo" if lang == "tr" else "Slang"
    if "greet" in clean or "selam" in clean:
        return "Ünlem (Selamlama)" if lang == "tr" else "Interjection (Greeting)"
    if "voca" in clean or "hitap" in clean or "title" in clean or "unvan" in clean:
        return "Unvan / San" if lang == "tr" else "Title / Honorific"

    # Default fallback: clean capitalized string
    return raw_pos.strip().title()


def normalize_role(raw_role: Optional[str], lang: str = "tr") -> str:
    """
    Normalizes sentence syntactic roles into clean, user-friendly labels.
    Example: 'subject' -> 'Özne' (TR) or 'Subject' (EN)
    """
    if not raw_role:
        return "-" if lang == "tr" else "-"

    clean = raw_role.strip().lower()
    if clean in ROLE_MAP:
        tr, en = ROLE_MAP[clean]
        return tr if lang == "tr" else en

    if "greet" in clean or "selam" in clean:
        return "Hitap / Selamlama" if lang == "tr" else "Greeting / Salutation"
    if "vocat" in clean or "seslen" in clean or "title" in clean:
        return "Hitap / Seslenme" if lang == "tr" else "Vocative / Address"
    if "subject" in clean or "özne" in clean:
        return "Özne" if lang == "tr" else "Subject"
    if "verb" in clean or "yüklem" in clean or "predicate" in clean:
        return "Yüklem" if lang == "tr" else "Predicate"
    if "object" in clean or "nesne" in clean:
        return "Nesne" if lang == "tr" else "Object"
    if "adv" in clean or "tümleç" in clean:
        return "Zarf Tümleci" if lang == "tr" else "Adverbial"
    if "time" in clean or "zaman" in clean:
        return "Zaman Belirteci" if lang == "tr" else "Time Adverbial"
    if "conn" in clean or "bağlantı" in clean:
        return "Bağlantı" if lang == "tr" else "Connector"

    return raw_role.strip().title()
