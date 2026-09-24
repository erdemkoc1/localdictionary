import os
import re
import sqlite3
from typing import List, Dict, Any, Tuple, Optional
from src.utils import turkish_lower, get_resource_path
from src.grammar_data import (
    SLANG_IDIOMS_EN_TR,
    SLANG_IDIOMS_TR_EN,
    SLANG_WORDS_EN_TR,
    SLANG_WORDS_TR_EN,
    EXTENDED_VERBS_EN_TR,
    EXTENDED_NOUNS_EN_TR,
    EXTENDED_ADJECTIVES_EN_TR,
    QUESTION_STARTERS_EN,
    QUESTION_STARTERS_TR,
    TURKISH_PRONOUNS_FULL,
    TURKISH_COMPOUND_VERBS,
    TURKISH_CONVERSATIONAL_EXPRESSIONS,
    TURKISH_IMPERATIVE_STEMS,
    TURKISH_COPULA_NEGATION
)


# ==============================================================================
# HIGH-FREQUENCY VOCABULARY OVERRIDES (EN -> TR)
# Overcomes ambiguous, archaic, or overly technical dictionary entries
# e.g., 'school' -> 'okul' (not 'mektep'), 'go' -> 'gitmek' (not 'hareket etmek')
# ==============================================================================

COMMON_VERBS_EN_TR = {
    "go": "gitmek",
    "come": "gelmek",
    "work": "çalışmak",
    "live": "yaşamak",
    "see": "görmek",
    "look": "bakmak",
    "watch": "izlemek",
    "read": "okumak",
    "write": "yazmak",
    "speak": "konuşmak",
    "talk": "konuşmak",
    "eat": "yemek",
    "drink": "içmek",
    "sleep": "uyumak",
    "want": "istemek",
    "need": "ihtiyacı olmak",
    "like": "beğenmek",
    "love": "sevmek",
    "know": "bilmek",
    "think": "düşünmek",
    "understand": "anlamak",
    "meet": "buluşmak",
    "buy": "satın almak",
    "sell": "satmak",
    "take": "almak",
    "give": "vermek",
    "make": "yapmak",
    "do": "yapmak",
    "say": "söylemek",
    "tell": "anlatmak",
    "ask": "sormak",
    "answer": "cevaplamak",
    "help": "yardım etmek",
    "play": "oynamak",
    "listen": "dinlemek",
    "open": "açmak",
    "close": "kapatmak",
    "run": "koşmak",
    "walk": "yürümek",
    "drive": "sürmek",
    "fly": "uçmak",
    "stay": "kalmak",
    "leave": "ayrılmak",
    "wait": "beklemek",
    "start": "başlamak",
    "begin": "başlamak",
    "finish": "bitirmek",
    "stop": "durmak",
    "find": "bulmak",
    "lose": "kaybetmek",
    "learn": "öğrenmek",
    "teach": "öğretmek",
    "call": "aramak",
    "send": "göndermek",
    "pay": "ödemek",
    "bring": "getirmek",
    "put": "koymak",
    "cost": "mal olmak",
    "sit": "oturmak",
    "stand": "ayakta durmak",
    "feel": "hissetmek",
    "try": "denemek",
    "hear": "duymak",
    "create": "yaratmak",
    "build": "inşa etmek",
    "protect": "korumak",
    "fight": "savaşmak",
    "win": "kazanmak",
    "lose": "kaybetmek",
    "kill": "öldürmek",
    "die": "ölmek",
    "change": "değiştirmek",
    "believe": "inanmak",
    "follow": "takip etmek",
    "remember": "hatırlamak",
    "forget": "unutmak"
}

COMMON_NOUNS_EN_TR = {
    "school": "okul",
    "home": "ev",
    "house": "ev",
    "car": "araba",
    "book": "kitap",
    "teacher": "öğretmen",
    "student": "öğrenci",
    "doctor": "doktor",
    "hospital": "hastane",
    "water": "su",
    "bread": "ekmek",
    "food": "yemek",
    "money": "para",
    "friend": "arkadaş",
    "brother": "kardeş",
    "sister": "kız kardeş",
    "father": "baba",
    "mother": "anne",
    "family": "aile",
    "child": "çocuk",
    "children": "çocuklar",
    "person": "kişi",
    "people": "insanlar",
    "man": "adam",
    "woman": "kadın",
    "boy": "erkek çocuk",
    "girl": "kız çocuk",
    "city": "şehir",
    "country": "ülke",
    "world": "dünya",
    "day": "gün",
    "night": "gece",
    "week": "hafta",
    "month": "ay",
    "year": "yıl",
    "morning": "sabah",
    "evening": "akşam",
    "time": "zaman",
    "room": "oda",
    "door": "kapı",
    "window": "pencere",
    "table": "masa",
    "computer": "bilgisayar",
    "phone": "telefon",
    "job": "iş",
    "office": "ofis",
    "street": "sokak",
    "road": "yol",
    "dog": "köpek",
    "cat": "kedi",
    "weather": "hava",
    "question": "soru",
    "problem": "sorun",
    "life": "hayat",
    "story": "hikaye",
    "film": "film",
    "movie": "film",
    "music": "müzik",
    "soldier": "asker",
    "warrior": "savaşçı",
    "hero": "kahraman",
    "leader": "lider",
    "army": "ordu",
    "war": "savaş",
    "peace": "barış",
    "everything": "her şeyi",
    "nothing": "hiçbir şey",
    "everyone": "herkes",
    "everybody": "herkes",
    "someone": "biri",
    "something": "bir şey",
    "anything": "hiçbir şey",
    "god": "Tanrı",
    "jesus": "İsa"
}

COMMON_ADJECTIVES_EN_TR = {
    "good": "iyi",
    "bad": "kötü",
    "big": "büyük",
    "small": "küçük",
    "new": "yeni",
    "old": "eski",
    "young": "genç",
    "beautiful": "güzel",
    "fast": "hızlı",
    "slow": "yavaş",
    "happy": "mutlu",
    "sad": "üzgün",
    "easy": "kolay",
    "hard": "zor",
    "cold": "soğuk",
    "hot": "sıcak",
    "warm": "ılık",
    "rich": "zengin",
    "poor": "fakir",
    "important": "önemli",
    "expensive": "pahalı",
    "cheap": "ucuz",
    "clean": "temiz",
    "dirty": "kirli",
    "long": "uzun",
    "short": "kısa",
    "strong": "güçlü",
    "weak": "zayıf",
    "brave": "cesur",
    "courageous": "cesur",
    "great": "harika",
    "honest": "dürüst",
    "clever": "akıllı",
    "wise": "bilge",
    "kind": "nazik",
    "polite": "kibar",
    "free": "özgür",
    "true": "doğru",
    "false": "yanlış",
    "real": "gerçek"
}

GEOGRAPHIC_NAMES = {
    "london": "Londra",
    "paris": "Paris",
    "berlin": "Berlin",
    "rome": "Roma",
    "ankara": "Ankara",
    "istanbul": "İstanbul",
    "izmir": "İzmir",
    "madrid": "Madrid",
    "new york": "New York",
    "tokyo": "Tokyo",
    "turkey": "Türkiye",
    "england": "İngiltere",
    "germany": "Almanya",
    "france": "Fransa",
    "italy": "İtalya",
    "spain": "İspanya",
    "america": "Amerika",
    "russia": "Rusya"
}

SENTENTIAL_ADVERBS = {
    "maalesef": "unfortunately",
    "ne yazık ki": "unfortunately",
    "ne yazik ki": "unfortunately",
    "aslında": "actually",
    "aslinda": "actually",
    "gerçekten": "really",
    "gercekten": "really",
    "kesinlikle": "definitely",
    "belki": "maybe",
    "muhtemelen": "probably",
    "özellikle": "especially",
    "ozellikle": "especially",
    "sonunda": "finally",
    "genellikle": "generally",
    "elbette": "of course",
    "tabii": "of course",
    "tabi": "of course",
    "tabi ki": "of course",
    "tabiki": "of course",
    "zaten": "already",
    "ayrıca": "also",
    "ayrica": "also",
    "üstelik": "moreover",
    "ustelik": "moreover"
}

COMMON_PERSON_NAMES = {
    "ayşe", "ali", "ahmet", "mehmet", "fatma", "emine", "mustafa", 
    "can", "zeynep", "elif", "deniz", "burak", "selin", "erdem", "kemal",
    "john", "mary", "david", "sarah", "michael", "emma", "james", 
    "anna", "peter", "paul", "tom", "alex", "bob", "lisa", "george", "jesus"
}

ENGLISH_CONTRACTIONS = {
    r"\bhe's\b": "he is",
    r"\bshe's\b": "she is",
    r"\bit's\b": "it is",
    r"\bi'm\b": "i am",
    r"\byou're\b": "you are",
    r"\bwe're\b": "we are",
    r"\bthey're\b": "they are",
    r"\bwho's\b": "who is",
    r"\bwhat's\b": "what is",
    r"\bthat's\b": "that is",
    r"\bthere's\b": "there is",
    r"\bcan't\b": "cannot",
    r"\bwon't\b": "will not",
    r"\bdon't\b": "do not",
    r"\bdoesn't\b": "does not",
    r"\bdidn't\b": "did not",
    r"\bisn't\b": "is not",
    r"\baren't\b": "are not",
    r"\bwasn't\b": "was not",
    r"\bweren't\b": "were not",
    r"\bhaven't\b": "have not",
    r"\bhasn't\b": "has not",
    r"\bhadn't\b": "had not",
    r"\bwouldn't\b": "would not",
    r"\bcouldn't\b": "could not",
    r"\bshouldn't\b": "should not",
    r"\bi've\b": "i have",
    r"\byou've\b": "you have",
    r"\bwe've\b": "we have",
    r"\bthey've\b": "they have",
    r"\bi'll\b": "i will",
    r"\byou'll\b": "you will",
    r"\bhe'll\b": "he will",
    r"\bshe'll\b": "she will",
    r"\bwe'll\b": "we will",
    r"\bthey'll\b": "they will"
}

def expand_english_contractions(text: str) -> str:
    res = text
    for pattern, replacement in ENGLISH_CONTRACTIONS.items():
        matches = list(re.finditer(pattern, res, flags=re.IGNORECASE))
        for m in reversed(matches):
            orig = m.group(0)
            rep = replacement
            if orig[0].isupper():
                rep = rep[0].upper() + rep[1:]
            res = res[:m.start()] + rep + res[m.end():]
    return res

# Merge Extended Vocabulary Pools
COMMON_VERBS_EN_TR.update(EXTENDED_VERBS_EN_TR)
COMMON_NOUNS_EN_TR.update(EXTENDED_NOUNS_EN_TR)
COMMON_ADJECTIVES_EN_TR.update(EXTENDED_ADJECTIVES_EN_TR)

# Reverse Lookups (TR -> EN)
COMMON_VERBS_TR_EN = {v: k for k, v in COMMON_VERBS_EN_TR.items()}
COMMON_NOUNS_TR_EN = {v: k for k, v in COMMON_NOUNS_EN_TR.items()}
COMMON_NOUNS_TR_EN.update({
    "karı": "wife",
    "koca": "husband",
    "eş": "spouse",
    "oğul": "son",
    "kız": "daughter",
    "abla": "older sister",
    "abi": "older brother",
    "ağabey": "older brother",
    "kardeş": "brother",
    "teyze": "aunt",
    "amca": "uncle",
    "dayı": "uncle",
    "hala": "aunt",
    "dede": "grandfather",
    "nine": "grandmother",
    "nene": "grandmother",
    "sevgili": "lover",
    "öğrenci": "student",
    "ogrenci": "student",
    "doktor": "doctor",
    "öğretmen": "teacher",
    "ogretmen": "teacher"
})
COMMON_ADJECTIVES_TR_EN = {v: k for k, v in COMMON_ADJECTIVES_EN_TR.items()}
COMMON_ADJECTIVES_TR_EN.update({
    "bekar": "single",
    "bekâr": "single",
    "evli": "married",
    "hazır": "ready",
    "hazir": "ready",
    "aç": "hungry",
    "ac": "hungry",
    "tok": "full",
    "yorgun": "tired",
    "hasta": "sick",
    "emin": "sure",
    "ciddi": "serious",
    "deli": "crazy",
    "yalnız": "alone",
    "yalniz": "alone",
    "sessiz": "quiet",
    "meşgul": "busy",
    "mesgul": "busy",
    "serbest": "free",
    "müsait": "available",
    "musait": "available",
    "mümkün": "possible",
    "mumkun": "possible",
    "imkansız": "impossible",
    "imkansiz": "impossible",
})
GEOGRAPHIC_NAMES_TR_EN = {turkish_lower(v): k.capitalize() for k, v in GEOGRAPHIC_NAMES.items()}

IRREGULAR_PAST_EN = {
    "go": "went", "see": "saw", "come": "came", "take": "took", "give": "gave",
    "find": "found", "think": "thought", "tell": "told", "leave": "left",
    "feel": "felt", "bring": "brought", "begin": "began", "write": "wrote",
    "hear": "heard", "meet": "met", "pay": "paid", "sit": "sat", "speak": "spoke",
    "read": "read", "grow": "grew", "lose": "lost", "fall": "fell", "send": "sent",
    "build": "built", "understand": "understood", "draw": "drew", "break": "broke",
    "spend": "spent", "cut": "cut", "drive": "drove", "buy": "bought", "wear": "wore",
    "drink": "drank", "eat": "ate", "run": "ran", "know": "knew", "make": "made",
    "say": "said", "sleep": "slept", "win": "won", "teach": "taught", "swim": "swam"
}

def make_3s_present_en(verb: str) -> str:
    parts = verb.split(" ", 1)
    base = parts[0]
    prep = (" " + parts[1]) if len(parts) > 1 else ""
    if base == "have": return "has" + prep
    if base == "be": return "is" + prep
    if base == "do": return "does" + prep
    if base == "go": return "goes" + prep
    if base.endswith(("ss", "sh", "ch", "x", "z", "o")):
        return base + "es" + prep
    if base.endswith("y") and len(base) > 2 and base[-2] not in "aeiou":
        return base[:-1] + "ies" + prep
    return base + "s" + prep

def make_past_en(verb: str) -> str:
    parts = verb.split(" ", 1)
    base = parts[0]
    prep = (" " + parts[1]) if len(parts) > 1 else ""
    if base in IRREGULAR_PAST_EN:
        return IRREGULAR_PAST_EN[base] + prep
    if base.endswith("e"):
        return base + "d" + prep
    if base.endswith("y") and len(base) > 2 and base[-2] not in "aeiou":
        return base[:-1] + "ied" + prep
    return base + "ed" + prep

COMMON_TR_VERB_STEMS = {
    "çalış": "çalışmak",
    "gid": "gitmek",
    "git": "gitmek",
    "yaş": "yaşamak",
    "yaşa": "yaşamak",
    "iste": "istemek",
    "ist": "istemek",
    "iç": "içmek",
    "oku": "okumak",
    "gör": "görmek",
    "al": "almak",
    "yap": "yapmak",
    "buluş": "buluşmak",
    "gel": "gelmek",
    "sev": "sevmek",
    "bil": "bilmek",
    "ye": "yemek",
    "y": "yemek",
    "de": "demek",
    "d": "demek",
    "konuş": "konuşmak",
    "yaz": "yazmak",
    "bak": "bakmak",
    "duy": "duymak",
    "otur": "oturmak",
    "uyu": "uyumak"
}

# Auto-expand Turkish verb stems for all vocabulary verbs
for tr_verb in list(COMMON_VERBS_TR_EN.keys()):
    if tr_verb.endswith(("mek", "mak")):
        base_stem = tr_verb[:-3]
        if base_stem not in COMMON_TR_VERB_STEMS:
            COMMON_TR_VERB_STEMS[base_stem] = tr_verb
        if base_stem.endswith("t"):
            soft = base_stem[:-1] + "d"
            if soft not in COMMON_TR_VERB_STEMS:
                COMMON_TR_VERB_STEMS[soft] = tr_verb
        if len(base_stem) > 2 and base_stem[-1] in "aıoueiöü":
            drop_v = base_stem[:-1]
            if drop_v not in COMMON_TR_VERB_STEMS:
                COMMON_TR_VERB_STEMS[drop_v] = tr_verb

# ==============================================================================
# IRREGULAR VERBS MAPPING: Inflected Form -> (Base Lemma, Tense)
# ==============================================================================

IRREGULAR_VERBS = {
    "saw": ("see", "past"),
    "seen": ("see", "past_participle"),
    "went": ("go", "past"),
    "gone": ("go", "past_participle"),
    "came": ("come", "past"),
    "took": ("take", "past"),
    "taken": ("take", "past_participle"),
    "gave": ("give", "past"),
    "given": ("give", "past_participle"),
    "found": ("find", "past"),
    "thought": ("think", "past"),
    "told": ("tell", "past"),
    "became": ("become", "past"),
    "left": ("leave", "past"),
    "felt": ("feel", "past"),
    "put": ("put", "past"),
    "brought": ("bring", "past"),
    "began": ("begin", "past"),
    "begun": ("begin", "past_participle"),
    "kept": ("keep", "past"),
    "held": ("hold", "past"),
    "wrote": ("write", "past"),
    "written": ("write", "past_participle"),
    "stood": ("stand", "past"),
    "heard": ("hear", "past"),
    "let": ("let", "past"),
    "meant": ("mean", "past"),
    "set": ("set", "past"),
    "met": ("meet", "past"),
    "paid": ("pay", "past"),
    "sat": ("sit", "past"),
    "spoke": ("speak", "past"),
    "spoken": ("speak", "past_participle"),
    "read": ("read", "past"),
    "grew": ("grow", "past"),
    "lost": ("lose", "past"),
    "fell": ("fall", "past"),
    "fallen": ("fall", "past_participle"),
    "sent": ("send", "past"),
    "built": ("build", "past"),
    "understood": ("understand", "past"),
    "drew": ("draw", "past"),
    "drawn": ("draw", "past_participle"),
    "broke": ("break", "past"),
    "broken": ("break", "past_participle"),
    "spent": ("spend", "past"),
    "cut": ("cut", "past"),
    "rose": ("rise", "past"),
    "risen": ("rise", "past_participle"),
    "drove": ("drive", "past"),
    "driven": ("drive", "past_participle"),
    "bought": ("buy", "past"),
    "wore": ("wear", "past"),
    "worn": ("wear", "past_participle"),
    "chose": ("choose", "past"),
    "chosen": ("choose", "past_participle"),
    "drank": ("drink", "past"),
    "drunk": ("drink", "past_participle"),
    "ate": ("eat", "past"),
    "eaten": ("eat", "past_participle"),
    "ran": ("run", "past"),
    "knew": ("know", "past"),
    "known": ("know", "past_participle"),
    "got": ("get", "past"),
    "gotten": ("get", "past_participle"),
    "made": ("make", "past"),
    "said": ("say", "past"),
    "slept": ("sleep", "past"),
    "won": ("win", "past"),
    "taught": ("teach", "past"),
    "swam": ("swim", "past"),
    "sang": ("sing", "past"),
    "caught": ("catch", "past"),
    "sold": ("sell", "past"),
    "cost": ("cost", "past"),
    "hit": ("hit", "past")
}

# ==============================================================================
# GRAMMAR SPECIFICATIONS & CLOSED CLASSES
# ==============================================================================

PRONOUNS_EN_TR = {
    "i": {"tr": "ben", "person": "1s"},
    "you": {"tr": "sen", "person": "2s"},
    "he": {"tr": "o", "person": "3s"},
    "she": {"tr": "o", "person": "3s"},
    "it": {"tr": "o", "person": "3s"},
    "we": {"tr": "biz", "person": "1p"},
    "they": {"tr": "onlar", "person": "3p"},
    "me": {"tr": "beni", "person": "1s"},
    "him": {"tr": "onu", "person": "3s"},
    "her": {"tr": "onu", "person": "3s"},
    "us": {"tr": "bizi", "person": "1p"},
    "them": {"tr": "onları", "person": "3p"}
}

POSSESSIVES_EN = {
    "my": "1s",
    "your": "2s",
    "his": "3s",
    "her": "3s",
    "its": "3s",
    "our": "1p",
    "their": "3p"
}

PREPOSITIONS_EN = {
    "in": {"case": "locative", "fallback": "içinde"},
    "at": {"case": "locative", "fallback": "yerinde"},
    "on": {"case": "locative", "fallback": "üzerinde"},
    "to": {"case": "dative", "fallback": "doğru"},
    "from": {"case": "ablative", "fallback": "den"},
    "with": {"case": "postposition", "word": "ile"},
    "for": {"case": "postposition", "word": "için"},
    "about": {"case": "postposition", "word": "hakkında"},
    "without": {"case": "postposition", "word": "olmadan"},
    "under": {"case": "postposition", "word": "altında"},
    "before": {"case": "postposition", "word": "önce"},
    "after": {"case": "postposition", "word": "sonra"}
}

TIME_ADVERBS_EN = {
    "today": "bugün",
    "yesterday": "dün",
    "tomorrow": "yarın",
    "now": "şimdi",
    "always": "her zaman",
    "never": "asla",
    "sometimes": "bazen",
    "often": "sık sık",
    "soon": "yakında",
    "later": "sonra",
    "already": "zaten",
    "tonight": "bu gece"
}

CONJUNCTIONS_EN = {
    "and": "ve",
    "or": "veya",
    "but": "ama",
    "because": "çünkü",
    "if": "eğer",
    "so": "bu yüzden",
    "while": "iken"
}

ENGLISH_STOPWORDS = {
    "the", "a", "an", "is", "am", "are", "was", "were", "in", "on", "at", 
    "to", "for", "with", "from", "of", "and", "or", "but", "i", "you", 
    "he", "she", "it", "we", "they", "my", "your", "his", "her", "our", "their",
    "works", "lives", "will", "can", "must", "do", "does", "did", "have", "has", "not", "want"
}

TURKISH_STOPWORDS = {
    "ve", "veya", "ile", "için", "bir", "bu", "şu", "o", "ben", "sen",
    "biz", "siz", "onlar", "de", "da", "den", "dan", "e", "a", "çünkü",
    "ama", "fakat", "çalışıyor", "çalışır", "gitti", "geldi", "var", "yok",
    "istiyorum", "yaşıyor", "okula", "evde"
}

TURKISH_QUESTION_COPULAS = {
    # 2nd person plural / formal
    "mısınız": {"aux": "Are you", "person": "2p"},
    "misiniz": {"aux": "Are you", "person": "2p"},
    "musunuz": {"aux": "Are you", "person": "2p"},
    "müsünüz": {"aux": "Are you", "person": "2p"},
    "misiniz": {"aux": "Are you", "person": "2p"},
    # 2nd person singular
    "mısın": {"aux": "Are you", "person": "2s"},
    "misin": {"aux": "Are you", "person": "2s"},
    "musun": {"aux": "Are you", "person": "2s"},
    "müsün": {"aux": "Are you", "person": "2s"},
    # 1st person singular
    "mıyım": {"aux": "Am I", "person": "1s"},
    "miyim": {"aux": "Am I", "person": "1s"},
    "muyum": {"aux": "Am I", "person": "1s"},
    "müyüm": {"aux": "Am I", "person": "1s"},
    # 1st person plural
    "mıyız": {"aux": "Are we", "person": "1p"},
    "miyiz": {"aux": "Are we", "person": "1p"},
    "muyuz": {"aux": "Are we", "person": "1p"},
    "müyüz": {"aux": "Are we", "person": "1p"},
    # 3rd person singular
    "mı": {"aux": "Is it", "person": "3s"},
    "mi": {"aux": "Is it", "person": "3s"},
    "mu": {"aux": "Is it", "person": "3s"},
    "mü": {"aux": "Is it", "person": "3s"},
}

INVALID_TITLE_PREV = {
    "mı", "mi", "mu", "mü", "mısın", "misin", "musun", "müsün", "mısınız", "misiniz", "musunuz", "müsünüz",
    "mıyız", "miyiz", "muyuz", "müyüz", "mıyım", "miyim", "muyum", "müyüm",
    "ve", "veya", "ama", "fakat", "çünkü", "de", "da", "bu", "şu", "o", "ben", "sen", "biz", "siz", "onlar",
    "bir", "çok", "cok", "var", "yok", "bekar", "evli", "iyi", "kötü", "güzel", "nasıl", "neden", "ne",
    "nerede", "kim", "lütfen", "lutfen", "evet", "hayır", "hayir", "tamam", "peki", "hazır", "hazir"
}


# ==============================================================================
# TURKISH MORPHOLOGY & PHONOLOGY HELPERS
# ==============================================================================

def get_last_vowel(text: str) -> str:
    """Returns the last Turkish vowel in the text (or 'e' by default)."""
    vowels = [c for c in text.lower() if c in "aıoueiöü"]
    return vowels[-1] if vowels else "e"

def is_back_vowel(vowel: str) -> bool:
    """Returns True if the vowel is a back vowel (a, ı, o, u)."""
    return vowel in "aıou"

def is_hard_consonant(char: str) -> bool:
    """Fıstıkçı Şahap consonant unvoicing test."""
    return char.lower() in "fstkçşhp"

def soften_final_consonant(noun: str) -> str:
    """Applies standard Turkish consonant softening (ünsüz yumuşaması) before vowels."""
    if len(noun) <= 2:
        return noun
    if noun.endswith("k"):
        return noun[:-1] + "ğ"
    elif noun.endswith("p"):
        return noun[:-1] + "b"
    elif noun.endswith("ç"):
        return noun[:-1] + "c"
    elif noun.endswith("t"):
        return noun[:-1] + "d"
    return noun

def attach_possessive_suffix(noun: str, person: str = "1s") -> str:
    """
    Attaches native Turkish possessive suffix to noun (e.g. kardeş -> kardeşim, araba -> arabam).
    """
    if not noun:
        return noun
    last_v = get_last_vowel(noun)
    ends_vowel = noun[-1].lower() in "aıoueiöü"

    # 4-way harmony vowel
    if last_v in "aı":
        h_v = "ı"
    elif last_v in "ei":
        h_v = "i"
    elif last_v in "ou":
        h_v = "u"
    else:
        h_v = "ü"

    if ends_vowel:
        if person == "1s":
            return f"{noun}m"
        elif person == "2s":
            return f"{noun}n"
        elif person == "3s":
            return f"{noun}s{h_v}"
        elif person == "1p":
            return f"{noun}m{h_v}z"
        elif person == "2p":
            return f"{noun}n{h_v}z"
        elif person == "3p":
            ler = "lar" if is_back_vowel(last_v) else "ler"
            return f"{noun}{ler}ı" if is_back_vowel(last_v) else f"{noun}{ler}i"
    else:
        stem = soften_final_consonant(noun)
        if person == "1s":
            return f"{stem}{h_v}m"
        elif person == "2s":
            return f"{stem}{h_v}n"
        elif person == "3s":
            return f"{stem}{h_v}"
        elif person == "1p":
            return f"{stem}{h_v}m{h_v}z"
        elif person == "2p":
            return f"{stem}{h_v}n{h_v}z"
        elif person == "3p":
            ler = "lar" if is_back_vowel(last_v) else "ler"
            return f"{noun}{ler}ı" if is_back_vowel(last_v) else f"{noun}{ler}i"

    return noun

def attach_case_suffix(noun: str, case_type: str, is_proper: bool = False) -> str:
    """
    Attaches Turkish case suffixes with 2-way vowel harmony, consonant harmony, and buffer letters.
    Supports locative (-de/-da/-te/-ta), dative (-e/-a/-ye/-ya), ablative (-den/-dan/-ten/-tan).
    """
    if not noun:
        return noun

    last_v = get_last_vowel(noun)
    ends_vowel = noun[-1].lower() in "aıoueiöü"
    ends_hard = is_hard_consonant(noun[-1])
    is_back = is_back_vowel(last_v)

    if case_type == "locative":
        d_char = "t" if ends_hard else "d"
        v_char = "a" if is_back else "e"
        suffix = f"{d_char}{v_char}"
    elif case_type == "dative":
        v_char = "a" if is_back else "e"
        buffer = "y" if ends_vowel else ""
        stem = noun if is_proper else soften_final_consonant(noun)
        suffix = f"{buffer}{v_char}"
        return f"{noun}'{suffix}" if is_proper else f"{stem}{suffix}"
    elif case_type == "ablative":
        d_char = "t" if ends_hard else "d"
        v_char = "a" if is_back else "e"
        suffix = f"{d_char}{v_char}n"
    else:
        return noun

    return f"{noun}'{suffix}" if is_proper else f"{noun}{suffix}"

def attach_copula_suffix(predicate: str, tense: str = "present") -> str:
    """
    Attaches copula ('to be') suffix to noun/adjective (e.g. öğretmen -> öğretmendir).
    """
    if not predicate:
        return predicate

    last_v = get_last_vowel(predicate)
    ends_hard = is_hard_consonant(predicate[-1])
    ends_vowel = predicate[-1].lower() in "aıoueiöü"

    # 4-way vowel
    if last_v in "aı":
        h_v = "ı"
    elif last_v in "ei":
        h_v = "i"
    elif last_v in "ou":
        h_v = "u"
    else:
        h_v = "ü"

    if tense == "present":
        d_char = "t" if ends_hard else "d"
        return f"{predicate}{d_char}{h_v}r"
    else:
        d_char = "t" if ends_hard else "d"
        buffer = "y" if ends_vowel else ""
        return f"{predicate}{buffer}{d_char}{h_v}"


# ==============================================================================
# MAIN SYNTAX TRANSLATOR CLASS
# ==============================================================================

class SyntaxTranslator:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = get_resource_path("data/dictionary.db")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cur = self.conn.cursor()

    def detect_language(self, sentence: str) -> str:
        """
        Robust language detection based on vocabulary match count rather than single characters.
        Prevents Turkish proper nouns in English sentences (like 'Ayşe works in London') from causing misclassification.
        """
        words = re.findall(r"\b\w+\b", sentence.lower())
        if not words:
            return "en_tr"

        en_score = sum(1 for w in words if w in ENGLISH_STOPWORDS or w in COMMON_VERBS_EN_TR or w in COMMON_NOUNS_EN_TR)
        tr_score = sum(1 for w in words if w in TURKISH_STOPWORDS)

        # Check dictionary lookups for tokens
        for w in words[:6]:
            if w in ENGLISH_STOPWORDS or w in TURKISH_STOPWORDS:
                continue
            w_lower = turkish_lower(w)
            self.cur.execute("SELECT 1 FROM bilingual WHERE en_lower = ? LIMIT 1;", (w_lower,))
            if self.cur.fetchone():
                en_score += 1
            self.cur.execute("SELECT 1 FROM bilingual WHERE tr_lower = ? LIMIT 1;", (w_lower,))
            if self.cur.fetchone():
                tr_score += 1

        # Check distinctive Turkish letters as secondary weight
        tr_chars = set("çğıöşü")
        distinctive_tr = sum(1 for c in sentence.lower() if c in tr_chars)
        tr_score += distinctive_tr * 0.5

        return "tr_en" if tr_score > en_score else "en_tr"

    def _lookup_word(self, word: str, preferred_pos: Optional[str] = None, is_en: bool = True) -> List[Tuple[str, str, str]]:
        """
        Looks up word in prioritized vocabulary first, then SQLite bilingual database.
        """
        w_lower = turkish_lower(word)

        if is_en:
            # 1. Geographic proper names
            if w_lower in GEOGRAPHIC_NAMES:
                return [(GEOGRAPHIC_NAMES[w_lower], "proper_noun", "Common Usage")]

            # 2. High priority common verbs
            if preferred_pos == "v." and w_lower in COMMON_VERBS_EN_TR:
                return [(COMMON_VERBS_EN_TR[w_lower], "v.", "Common Usage")]

            # 3. High priority common nouns
            if preferred_pos == "n." and w_lower in COMMON_NOUNS_EN_TR:
                return [(COMMON_NOUNS_EN_TR[w_lower], "n.", "Common Usage")]

            # 4. High priority common adjectives
            if preferred_pos == "adj." and w_lower in COMMON_ADJECTIVES_EN_TR:
                return [(COMMON_ADJECTIVES_EN_TR[w_lower], "adj.", "Common Usage")]

            # Fallback high priority if pos not specified
            if not preferred_pos:
                if w_lower in COMMON_NOUNS_EN_TR:
                    return [(COMMON_NOUNS_EN_TR[w_lower], "n.", "Common Usage")]
                if w_lower in COMMON_VERBS_EN_TR:
                    return [(COMMON_VERBS_EN_TR[w_lower], "v.", "Common Usage")]
                if w_lower in COMMON_ADJECTIVES_EN_TR:
                    return [(COMMON_ADJECTIVES_EN_TR[w_lower], "adj.", "Common Usage")]

        col = "en_lower" if is_en else "tr_lower"
        tgt_col = "tr" if is_en else "en"

        def _clean_rows(raw_list):
            clean_list = []
            for r_tgt, r_type, r_cat in raw_list:
                c_tgt = re.sub(r"\(Kök:[^)]*\)", "", r_tgt)
                c_tgt = re.sub(r"\(negates[^)]*\)", "", c_tgt)
                c_tgt = re.sub(r";\s*the\s*not\b.*$", "", c_tgt, flags=re.IGNORECASE)
                c_tgt = c_tgt.strip(" ,;")
                clean_list.append((c_tgt or r_tgt, r_type, r_cat))
            return clean_list

        if preferred_pos:
            self.cur.execute(f"""
            SELECT {tgt_col}, type, category 
            FROM bilingual 
            WHERE {col} = ? AND type LIKE ?
            ORDER BY 
                CASE 
                    WHEN category = 'Common Usage' THEN 0 
                    WHEN category = 'General' THEN 1 
                    WHEN category = 'Wiktionary / Çekim' THEN 20
                    ELSE 2 
                END 
            LIMIT 5;
            """, (w_lower, f"%{preferred_pos}%"))
            rows = self.cur.fetchall()
            if rows:
                return _clean_rows(rows)

        self.cur.execute(f"""
        SELECT {tgt_col}, type, category 
        FROM bilingual 
        WHERE {col} = ? 
        ORDER BY 
            CASE 
                WHEN category = 'Common Usage' THEN 0 
                WHEN category = 'General' THEN 1 
                WHEN category = 'Wiktionary / Çekim' THEN 20
                ELSE 2 
            END 
        LIMIT 5;
        """, (w_lower,))
        return _clean_rows(self.cur.fetchall())

    def _conjugate_turkish_verb(
        self, 
        verb_lemma: str, 
        tense: str, 
        person: str = "3s", 
        is_negative: bool = False, 
        can_modal: bool = False,
        must_modal: bool = False,
        should_modal: bool = False,
        want_modal: bool = False
    ) -> str:
        """
        Full 4-way vowel harmony Turkish verb conjugator.
        Handles stems ending in vowels (drop vowel in -iyor), softening (git -> gidiyor),
        negation (-me/-ma/-miyor), modals (-ebilmek, -malı/-meli, istemek), past continuous, and personal endings.
        """
        if not (verb_lemma.endswith("mek") or verb_lemma.endswith("mak")):
            return verb_lemma

        # 0. Modal: want to (istemek + infinitive)
        if want_modal:
            want_person_map = {
                "1s": "istiyorum" if not is_negative else "istemiyorum",
                "2s": "istiyorsun" if not is_negative else "istemiyorsun",
                "3s": "istiyor" if not is_negative else "istemiyor",
                "1p": "istiyoruz" if not is_negative else "istemiyoruz",
                "2p": "istiyorsunuz" if not is_negative else "istemiyorsunuz",
                "3p": "istiyorlar" if not is_negative else "istemiyorlar"
            }
            w_v = want_person_map.get(person, "istiyor")
            return f"{verb_lemma} {w_v}"

        stem = verb_lemma[:-3]

        last_vowels = [c for c in stem if c in "aıoueiöü"]
        last_v = last_vowels[-1] if last_vowels else "e"
        is_back = is_back_vowel(last_v)

        # 0b. Modal 'must' / 'should' (-malı / -meli)
        if must_modal or should_modal:
            if is_negative:
                neg = "ma" if is_back else "me"
                stem = f"{stem}{neg}"
                is_back = is_back_vowel(get_last_vowel(stem))

            mali = "malı" if is_back else "meli"
            stem = f"{stem}{mali}"

            if person == "1s":
                end = "yım" if is_back else "yim"
                return f"{stem}{end}"
            elif person == "2s":
                end = "sın" if is_back else "sin"
                return f"{stem}{end}"
            elif person == "1p":
                end = "yız" if is_back else "yiz"
                return f"{stem}{end}"
            elif person == "2p":
                end = "sınız" if is_back else "siniz"
                return f"{stem}{end}"
            elif person == "3p":
                end = "lar" if is_back else "ler"
                return f"{stem}{end}"
            else: # 3s
                return stem

        # Modal 'can' (-ebilmek / -abilmek)
        if can_modal:
            if stem in ("git", "et", "tat"):
                stem = {"git": "gid", "et": "ed", "tat": "tad"}[stem]
            buffer = "y" if stem[-1] in "aıoueiöü" else ""
            abil = "abil" if is_back else "ebil"
            stem = f"{stem}{buffer}{abil}"
            last_v = "i"
            is_back = False

        # 4-way vowel harmony
        if last_v in "aı":
            h_vowel = "ı"
        elif last_v in "ei":
            h_vowel = "i"
        elif last_v in "ou":
            h_vowel = "u"
        else:
            h_vowel = "ü"

        # 1. Past Tense (-di/-dı/-du/-dü or -ti/-tı/-tu/-tü)
        if tense == "past":
            if is_negative:
                neg_suffix = "ma" if is_back else "me"
                stem = f"{stem}{neg_suffix}"
                d_char = "d"
                h_vowel = "ı" if is_back else "i"
            else:
                d_char = "t" if is_hard_consonant(stem[-1]) else "d"

            suffix = f"{d_char}{h_vowel}"
            if person == "1s":
                return f"{stem}{suffix}m"
            elif person == "2s":
                return f"{stem}{suffix}n"
            elif person == "1p":
                return f"{stem}{suffix}k"
            elif person == "3p":
                ler = "lar" if is_back else "ler"
                return f"{stem}{suffix}{ler}"
            else: # 3s
                return f"{stem}{suffix}"

        # 2. Future Tense (-ecek / -acak)
        elif tense == "future":
            if stem in ("git", "et", "tat"):
                stem = {"git": "gid", "et": "ed", "tat": "tad"}[stem]
            buffer = "y" if stem[-1] in "aıoueiöü" else ""
            if is_negative:
                neg_suffix = "may" if is_back else "mey"
                stem = f"{stem}{neg_suffix}"
                buffer = ""

            if person == "1s":
                end = "acağım" if is_back else "eceğim"
                return f"{stem}{buffer}{end}"
            elif person == "1p":
                end = "acağız" if is_back else "eceğiz"
                return f"{stem}{buffer}{end}"
            elif person == "2s":
                end = "acaksın" if is_back else "eceksin"
                return f"{stem}{buffer}{end}"
            elif person == "3p":
                end = "acaklar" if is_back else "ecekler"
                return f"{stem}{buffer}{end}"
            else: # 3s
                end = "acak" if is_back else "ecek"
                return f"{stem}{buffer}{end}"

        # 3. Past Continuous (-iyordu / -ıyordu)
        elif tense == "past_continuous":
            if stem in ("git", "et", "tat"):
                stem = {"git": "gid", "et": "ed", "tat": "tad"}[stem]
            if is_negative:
                m_vowel = "mı" if is_back else "mi"
                s = f"{stem}{m_vowel}"
            else:
                s = stem
                if s == "ye": s, h_vowel = "y", "i"
                elif s == "de": s, h_vowel = "d", "i"
                elif s[-1] in "aıoueiöü": s = s[:-1]

            suffix = f"{h_vowel}yor" if not is_negative else "yor"
            if person == "1s":
                return f"{s}{suffix}dum"
            elif person == "2s":
                return f"{s}{suffix}dun"
            elif person == "1p":
                return f"{s}{suffix}duk"
            elif person == "2p":
                return f"{s}{suffix}dunuz"
            elif person == "3p":
                return f"{s}{suffix}lardı"
            else: # 3s
                return f"{s}{suffix}du"

        # 4. Present Continuous / General (-iyor / -ıyor)
        else:
            if stem in ("git", "et", "tat"):
                stem = {"git": "gid", "et": "ed", "tat": "tad"}[stem]
            if is_negative:
                m_vowel = "mı" if is_back else "mi"
                s = f"{stem}{m_vowel}"
            else:
                s = stem
                # Special cases: yemek -> yiyor, demek -> diyor
                if s == "ye":
                    s = "y"
                    h_vowel = "i"
                elif s == "de":
                    s = "d"
                    h_vowel = "i"
                elif s[-1] in "aıoueiöü":
                    s = s[:-1]

            suffix = f"{h_vowel}yor" if not is_negative else "yor"
            if person == "1s":
                return f"{s}{suffix}um"
            elif person == "1p":
                return f"{s}{suffix}uz"
            elif person == "2s":
                return f"{s}{suffix}sun"
            elif person == "3p":
                ler = "lar" if is_back else "ler"
                return f"{s}{suffix}{ler}"
            else: # 3s
                return f"{s}{suffix}"

    def _extract_english_verb_lemma(self, token_lower: str) -> Tuple[str, str]:
        """
        Lemmatizes English inflected verbs to (base_lemma, tense).
        Handles irregular verbs, -s / -es / -ies, -ed / -ied, and -ing forms.
        """
        if token_lower in IRREGULAR_VERBS:
            return IRREGULAR_VERBS[token_lower]

        # 3rd person singular present
        if token_lower in ["goes"]:
            return ("go", "present")
        if token_lower in ["does"]:
            return ("do", "present")
        if token_lower in ["has"]:
            return ("have", "present")

        if token_lower.endswith("ies") and len(token_lower) > 4:
            return (token_lower[:-3] + "y", "present")
        if token_lower.endswith(("shes", "ches", "xes", "sses", "zzes")):
            return (token_lower[:-2], "present")
        if token_lower.endswith("ves") and len(token_lower) > 4:
            return (token_lower[:-1], "present")
        if token_lower.endswith("s") and len(token_lower) > 3 and not token_lower.endswith("ss"):
            return (token_lower[:-1], "present")

        # Continuous / Participle -ing
        if token_lower.endswith("ing") and len(token_lower) > 4:
            if token_lower not in ["morning", "evening", "something", "anything", "nothing", "everything", "king", "ring", "wing", "sing"]:
                # Double consonant: running -> run, swimming -> swim, hitting -> hit, stopping -> stop
                if len(token_lower) > 5 and token_lower[-4] == token_lower[-5] and token_lower[-4] not in "aeiouy":
                    cand_double = token_lower[:-4]
                    if cand_double in COMMON_VERBS_EN_TR:
                        return (cand_double, "continuous")
                # Dropped e: writing -> write, making -> make, living -> live, taking -> take
                cand_e = token_lower[:-3] + "e"
                if cand_e in COMMON_VERBS_EN_TR:
                    return (cand_e, "continuous")
                # Direct: working -> work, reading -> read, going -> go, playing -> play
                cand_direct = token_lower[:-3]
                if cand_direct in COMMON_VERBS_EN_TR:
                    return (cand_direct, "continuous")
                # DB lookups
                self.cur.execute("SELECT 1 FROM bilingual WHERE en_lower = ? AND type LIKE '%v.%' LIMIT 1;", (cand_direct,))
                if self.cur.fetchone():
                    return (cand_direct, "continuous")
                self.cur.execute("SELECT 1 FROM bilingual WHERE en_lower = ? AND type LIKE '%v.%' LIMIT 1;", (cand_e,))
                if self.cur.fetchone():
                    return (cand_e, "continuous")
                return (cand_direct, "continuous")

        # Past -ed
        if token_lower.endswith("ied") and len(token_lower) > 4:
            return (token_lower[:-3] + "y", "past")
        if token_lower.endswith("ed") and len(token_lower) > 3:
            cand_e = token_lower[:-1]
            cand_no_ed = token_lower[:-2]
            if cand_e in COMMON_VERBS_EN_TR:
                return (cand_e, "past")
            if cand_no_ed in COMMON_VERBS_EN_TR:
                return (cand_no_ed, "past")
            # Check SQLite dictionary
            self.cur.execute("SELECT 1 FROM bilingual WHERE en_lower = ? AND type LIKE '%v.%' LIMIT 1;", (cand_e,))
            if self.cur.fetchone():
                return (cand_e, "past")
            self.cur.execute("SELECT 1 FROM bilingual WHERE en_lower = ? AND type LIKE '%v.%' LIMIT 1;", (cand_no_ed,))
            if self.cur.fetchone():
                return (cand_no_ed, "past")
            return (cand_no_ed, "past")

        return (token_lower, "present")

    def translate(self, sentence: str, direction: str = "auto", show_slang_profanity: bool = True) -> Dict[str, Any]:
        sentence = sentence.strip()
        if not sentence:
            return {"translated_text": "", "breakdown": []}

        if direction == "auto":
            direction = self.detect_language(sentence)

        clean_norm = re.sub(r"[^\w\s']", "", sentence).strip()

        # Check whole-sentence slang idiom matches
        if direction == "en_tr":
            if clean_norm.lower() in SLANG_IDIOMS_EN_TR:
                idata = SLANG_IDIOMS_EN_TR[clean_norm.lower()]
                ival = idata["slang"] if show_slang_profanity else idata["clean"]
                p = sentence[-1] if sentence and sentence[-1] in ".!?" else ""
                return {
                    "translated_text": ival.capitalize() + p,
                    "breakdown": [{
                        "original": sentence,
                        "translated": ival,
                        "role": "idiom",
                        "pos": "idiom",
                        "alternatives": [idata["clean"] if show_slang_profanity else idata["slang"]]
                    }]
                }
        else:
            clean_tr = turkish_lower(clean_norm)
            if clean_tr in TURKISH_CONVERSATIONAL_EXPRESSIONS:
                cval = TURKISH_CONVERSATIONAL_EXPRESSIONS[clean_tr]
                p = sentence[-1] if sentence and sentence[-1] in ".!?" else ""
                final_cval = cval.rstrip(".!?") + p if p else cval
                return {
                    "translated_text": final_cval,
                    "breakdown": [{
                        "original": sentence,
                        "translated": cval,
                        "role": "expression",
                        "pos": "idiom"
                    }]
                }
            if clean_tr in SLANG_IDIOMS_TR_EN:
                idata = SLANG_IDIOMS_TR_EN[clean_tr]
                ival = idata["slang"] if show_slang_profanity else idata["clean"]
                p = sentence[-1] if sentence and sentence[-1] in ".!?" else ""
                return {
                    "translated_text": ival.capitalize() + p,
                    "breakdown": [{
                        "original": sentence,
                        "translated": ival,
                        "role": "idiom",
                        "pos": "idiom",
                        "alternatives": [idata["clean"] if show_slang_profanity else idata["slang"]]
                    }]
                }


        if direction == "en_tr":
            # 1. Expand contractions (e.g. He's -> He is, don't -> do not)
            norm_sentence = expand_english_contractions(sentence)

            # 2. Check for multi-clause compound sentences (e.g. "... and he ...", "... but she ...")
            clause_split = re.split(r"(,\s*and\s+|\s+and\s+|,\s*but\s+|\s+but\s+|,\s*because\s+|\s+because\s+|,\s*so\s+|\s+so\s+)", norm_sentence, flags=re.IGNORECASE)
            if len(clause_split) > 1:
                translated_clauses = []
                breakdown = []
                conj_map = {"and": "ve", "but": "ama", "because": "çünkü", "so": "bu yüzden"}
                
                for part in clause_split:
                    p_clean = part.strip().strip(",").strip().lower()
                    if p_clean in conj_map:
                        tr_conj = conj_map[p_clean]
                        translated_clauses.append(tr_conj)
                        breakdown.append({"original": part.strip(), "translated": tr_conj, "role": "connector", "pos": "conj"})
                    elif part.strip():
                        res_clause = self._translate_en_to_tr(part.strip(), show_slang_profanity=show_slang_profanity)
                        if res_clause["translated_text"]:
                            c_text = res_clause["translated_text"].rstrip(".!?; ")
                            if len(translated_clauses) > 0 and c_text:
                                first_w = c_text.split()[0]
                                if first_w.lower() in ["o", "ben", "sen", "biz", "siz", "onlar", "bu", "şu"]:
                                    c_text = turkish_lower(first_w) + c_text[len(first_w):]
                            translated_clauses.append(c_text)
                            breakdown.extend(res_clause.get("breakdown", []))

                final_text = " ".join(translated_clauses).strip()
                if norm_sentence[-1] in ".!?;":
                    final_text += norm_sentence[-1]
                if final_text:
                    final_text = final_text[0].upper() + final_text[1:]
                return {"translated_text": final_text, "breakdown": breakdown}

            return self._translate_en_to_tr(norm_sentence, show_slang_profanity=show_slang_profanity)
        else:
            return self._translate_tr_to_en(sentence, show_slang_profanity=show_slang_profanity)

    def _translate_en_to_tr(self, sentence: str, show_slang_profanity: bool = True) -> Dict[str, Any]:
        raw_tokens = re.findall(r"\b[\w'-]+\b|[.,!?;]", sentence)
        if not raw_tokens:
            return {"translated_text": "", "breakdown": []}

        breakdown = []
        i = 0
        n = len(raw_tokens)
        subject_person = "3s"
        has_future_modal = False
        has_can_modal = False
        has_must_modal = False
        has_should_modal = False
        has_want_modal = False
        is_negated = False
        is_continuous = False
        cont_tense = "present"
        copula_predicate = None
        aux_tense = None

        while i < n:
            token = raw_tokens[i]
            t_lower = token.lower()

            # 0a. Multi-word slang idiom check (longest match first)
            matched_slang = False
            for span_len in (4, 3, 2):
                if i + span_len <= n:
                    span_tokens = [raw_tokens[k].lower() for k in range(i, i + span_len)]
                    span_str = re.sub(r"[^\w\s']", "", " ".join(span_tokens)).strip()
                    if span_str in SLANG_IDIOMS_EN_TR:
                        idata = SLANG_IDIOMS_EN_TR[span_str]
                        ival = idata["slang"] if show_slang_profanity else idata["clean"]
                        breakdown.append({
                            "original": " ".join([raw_tokens[k] for k in range(i, i + span_len)]),
                            "translated": ival,
                            "role": "idiom",
                            "pos": "idiom",
                            "alternatives": [idata["clean"] if show_slang_profanity else idata["slang"]]
                        })
                        i += span_len
                        matched_slang = True
                        break
            if matched_slang:
                continue

            # 0b. Single-word slang check
            if t_lower in SLANG_WORDS_EN_TR:
                sdata = SLANG_WORDS_EN_TR[t_lower]
                sval = sdata["slang"] if show_slang_profanity else sdata["clean"]
                breakdown.append({
                    "original": token,
                    "translated": sval,
                    "role": "slang",
                    "pos": "slang",
                    "alternatives": [sdata["clean"] if show_slang_profanity else sdata["slang"]]
                })
                i += 1
                continue

            # 0c. Wh- Question Starters (e.g. what, where, when, why, who, how)
            if t_lower in QUESTION_STARTERS_EN:
                breakdown.append({
                    "original": token,
                    "translated": QUESTION_STARTERS_EN[t_lower],
                    "role": "question_wh",
                    "pos": "wh_word"
                })
                i += 1
                continue

            # 1. Punctuation
            if token in ".,!?;":
                breakdown.append({"original": token, "translated": token, "role": "punct", "pos": "punct"})
                i += 1
                continue

            # 2. Conjunctions
            if t_lower in CONJUNCTIONS_EN:
                breakdown.append({"original": token, "translated": CONJUNCTIONS_EN[t_lower], "role": "connector", "pos": "conj"})
                i += 1
                continue

            # 3. Time Adverbs
            if t_lower in TIME_ADVERBS_EN:
                breakdown.append({"original": token, "translated": TIME_ADVERBS_EN[t_lower], "role": "time", "pos": "adv"})
                i += 1
                continue

            # 3b. Intensifiers / Degree Adverbs (e.g. "very", "really", "so", "quite")
            if t_lower in ["very", "really", "so", "quite", "too"]:
                int_map = {"very": "çok", "really": "gerçekten", "so": "çok", "quite": "oldukça", "too": "çok"}
                int_tr = int_map[t_lower]
                if i + 1 < n and raw_tokens[i+1] not in ".,!?;":
                    adj_tok = raw_tokens[i+1]
                    adj_matches = self._lookup_word(adj_tok.lower(), preferred_pos="adj.", is_en=True)
                    if adj_matches and ("adj." in adj_matches[0][1] or adj_tok.lower() in COMMON_ADJECTIVES_EN_TR):
                        adj_tr = adj_matches[0][0]
                        if copula_predicate:
                            combined = attach_copula_suffix(f"{int_tr} {adj_tr}", copula_predicate)
                            copula_predicate = None
                        else:
                            combined = f"{int_tr} {adj_tr}"
                        breakdown.append({
                            "original": f"{token} {adj_tok}",
                            "translated": combined,
                            "role": "adjective",
                            "pos": "deg_adj"
                        })
                        i += 2
                        continue

                breakdown.append({"original": token, "translated": int_tr, "role": "adverbial", "pos": "adv"})
                i += 1
                continue

            # 4. Modals and Negations
            if t_lower in ["will", "shall"]:
                has_future_modal = True
                i += 1
                continue
            elif t_lower in ["can", "could"]:
                has_can_modal = True
                i += 1
                continue
            elif t_lower in ["must"]:
                has_must_modal = True
                i += 1
                continue
            elif t_lower in ["should", "ought"]:
                has_should_modal = True
                i += 1
                continue
            elif t_lower == "have" and i + 1 < n and raw_tokens[i+1].lower() == "to":
                has_must_modal = True
                i += 2
                continue
            elif t_lower == "has" and i + 1 < n and raw_tokens[i+1].lower() == "to":
                has_must_modal = True
                i += 2
                continue
            elif t_lower == "want" and i + 1 < n and raw_tokens[i+1].lower() == "to":
                has_want_modal = True
                i += 2
                continue
            elif t_lower == "wants" and i + 1 < n and raw_tokens[i+1].lower() == "to":
                has_want_modal = True
                i += 2
                continue
            elif t_lower in ["do", "does", "did"]:
                if i + 1 < n and raw_tokens[i+1].lower() in ["not", "n't"]:
                    is_negated = True
                    i += 2
                    continue
                # Question auxiliary marker (e.g. "Do you live...", "Where does she work...")
                next_tok = raw_tokens[i+1].lower() if i + 1 < n else ""
                if next_tok in ["you", "he", "she", "it", "we", "they", "i"] or (i + 1 < n and raw_tokens[i+1][0].isupper()):
                    aux_tense = "past" if t_lower == "did" else "present"
                    i += 1
                    continue
            elif t_lower in ["not", "never"]:
                is_negated = True
                i += 1
                continue

            # 5. Continuous Tenses and Copula verbs (am, is, are, was, were)
            if t_lower in ["is", "am", "are"]:
                # Check if followed by continuous verb (e.g. is working, is reading)
                if i + 1 < n and raw_tokens[i+1].lower().endswith("ing") and raw_tokens[i+1].lower() not in ["morning", "evening", "something", "anything", "nothing", "everything"]:
                    is_continuous = True
                    cont_tense = "present"
                    copula_predicate = None
                    i += 1
                    continue
                copula_predicate = "present"
                i += 1
                continue
            elif t_lower in ["was", "were"]:
                if i + 1 < n and raw_tokens[i+1].lower().endswith("ing") and raw_tokens[i+1].lower() not in ["morning", "evening", "something", "anything", "nothing", "everything"]:
                    is_continuous = True
                    cont_tense = "past"
                    copula_predicate = None
                    i += 1
                    continue
                copula_predicate = "past"
                i += 1
                continue

            # 6. Possessive Subject / Noun Chunks (e.g. "My brother lives...", "Our teacher...")
            if t_lower in POSSESSIVES_EN and i + 1 < n:
                poss_person = POSSESSIVES_EN[t_lower]
                # Check optional adjective: "My new car"
                if i + 2 < n and raw_tokens[i+1].lower() in COMMON_ADJECTIVES_EN_TR:
                    adj_tok = raw_tokens[i+1]
                    noun_tok = raw_tokens[i+2]
                    noun_matches = self._lookup_word(noun_tok, preferred_pos="n.", is_en=True)
                    noun_tr = noun_matches[0][0] if noun_matches else noun_tok
                    adj_tr = COMMON_ADJECTIVES_EN_TR[adj_tok.lower()]
                    
                    poss_noun = attach_possessive_suffix(noun_tr, poss_person)
                    combined = f"{adj_tr} {poss_noun}"
                    role = "subject" if i == 0 else "object"
                    if role == "subject":
                        subject_person = "3s"

                    breakdown.append({
                        "original": f"{token} {adj_tok} {noun_tok}",
                        "translated": combined,
                        "role": role,
                        "pos": "possessive_np"
                    })
                    i += 3
                    continue
                else:
                    noun_tok = raw_tokens[i+1]
                    if noun_tok not in ".,!?;":
                        noun_matches = self._lookup_word(noun_tok, preferred_pos="n.", is_en=True)
                        noun_tr = noun_matches[0][0] if noun_matches else noun_tok
                        poss_noun = attach_possessive_suffix(noun_tr, poss_person)
                        
                        role = "subject" if i == 0 else "object"
                        if role == "subject":
                            subject_person = "3s"

                        breakdown.append({
                            "original": f"{token} {noun_tok}",
                            "translated": poss_noun,
                            "role": role,
                            "pos": "possessive_np"
                        })
                        i += 2
                        continue

            # 7. Personal Pronouns
            if t_lower in PRONOUNS_EN_TR:
                p_info = PRONOUNS_EN_TR[t_lower]
                if "person" in p_info and t_lower in ["i", "you", "he", "she", "it", "we", "they"]:
                    subject_person = p_info["person"]
                    role = "subject"
                else:
                    role = "object"
                breakdown.append({"original": token, "translated": p_info["tr"], "role": role, "pos": "pronoun"})
                i += 1
                continue

            # 8. Proper Nouns / Names as Subject (e.g. "Ayşe", "John", "Ali", "London")
            # If capitalized at start followed by verb, or known name
            next_token = raw_tokens[i+1].lower() if i+1 < n else ""
            is_start_token = (i == 0)
            is_followed_by_verb_or_copula = (
                next_token in ["works", "lives", "is", "was", "are", "were", "will", "can", "must", 
                               "has", "have", "had", "saw", "went", "bought", "came", "likes", 
                               "wants", "speaks", "goes", "drinks", "eats", "reads", "studies", "took"]
                or next_token.endswith("s") or next_token.endswith("ed")
            )
            is_known_name = t_lower in COMMON_PERSON_NAMES

            if token[0].isupper() and (is_start_token and is_followed_by_verb_or_copula or is_known_name):
                # Recognized as Proper Name Subject
                subject_person = "3s"
                if t_lower in COMMON_NOUNS_EN_TR:
                    tr_subj = COMMON_NOUNS_EN_TR[t_lower]
                elif t_lower in GEOGRAPHIC_NAMES:
                    tr_subj = GEOGRAPHIC_NAMES[t_lower]
                else:
                    tr_subj = token

                breakdown.append({
                    "original": token,
                    "translated": tr_subj,
                    "role": "subject",
                    "pos": "proper_noun"
                })
                i += 1
                continue

            # 9. Prepositional Phrases (e.g. "in London", "for my brother", "to school")
            if t_lower in PREPOSITIONS_EN and i + 1 < n:
                prep = PREPOSITIONS_EN[t_lower]

                # Pattern A: Preposition + Possessive + Noun ("for my brother", "with our friends")
                if raw_tokens[i+1].lower() in POSSESSIVES_EN and i + 2 < n:
                    poss_person = POSSESSIVES_EN[raw_tokens[i+1].lower()]
                    noun = raw_tokens[i+2]
                    noun_matches = self._lookup_word(noun, preferred_pos="n.", is_en=True)
                    noun_tr = noun_matches[0][0] if noun_matches else noun
                    poss_noun = attach_possessive_suffix(noun_tr, poss_person)

                    if prep.get("case") == "postposition":
                        combined = f"{poss_noun} {prep.get('word', '')}"
                    else:
                        combined = attach_case_suffix(poss_noun, prep.get("case", "locative"), is_proper=False)

                    breakdown.append({
                        "original": f"{token} {raw_tokens[i+1]} {noun}",
                        "translated": combined,
                        "role": "adverbial",
                        "pos": "prep_phrase"
                    })
                    i += 3
                    continue

                # Pattern B: Preposition + Determiner (the/a) + Noun ("in the hospital", "at the door")
                elif raw_tokens[i+1].lower() in ["the", "a", "an"] and i + 2 < n:
                    noun = raw_tokens[i+2]
                    noun_matches = self._lookup_word(noun, preferred_pos="n.", is_en=True)
                    noun_tr = noun_matches[0][0] if noun_matches else noun
                    
                    if prep.get("case") == "postposition":
                        combined = f"{noun_tr} {prep.get('word', '')}"
                    else:
                        combined = attach_case_suffix(noun_tr, prep.get("case", "locative"), is_proper=False)

                    breakdown.append({
                        "original": f"{token} {raw_tokens[i+1]} {noun}",
                        "translated": combined,
                        "role": "adverbial",
                        "pos": "prep_phrase"
                    })
                    i += 3
                    continue

                # Pattern C: Preposition + Noun/Proper Noun ("in London", "to school", "in Paris")
                else:
                    noun = raw_tokens[i+1]
                    if noun not in ".,!?;":
                        is_prop = noun[0].isupper() or (noun.lower() in GEOGRAPHIC_NAMES) or (noun.lower() in COMMON_PERSON_NAMES)
                        noun_matches = self._lookup_word(noun, preferred_pos="n.", is_en=True)
                        noun_tr = noun_matches[0][0] if noun_matches else noun

                        if is_prop and noun_tr:
                            noun_tr = noun_tr.capitalize()

                        if prep.get("case") == "postposition":
                            combined = f"{noun_tr} {prep.get('word', '')}"
                        else:
                            combined = attach_case_suffix(noun_tr, prep.get("case", "locative"), is_proper=is_prop)

                        breakdown.append({
                            "original": f"{token} {noun}",
                            "translated": combined,
                            "role": "adverbial",
                            "pos": "prep_phrase"
                        })
                        i += 2
                        continue

            # 10. Articles (a, an, the)
            if t_lower in ["a", "an"]:
                # Check NP pattern: "a brave soldier" -> adj: brave, noun: soldier
                if i + 2 < n and raw_tokens[i+2] not in ".,!?;":
                    cand_adj = raw_tokens[i+1].lower()
                    cand_noun = raw_tokens[i+2].lower()
                    adj_matches = self._lookup_word(cand_adj, preferred_pos="adj.", is_en=True)
                    noun_matches = self._lookup_word(cand_noun, preferred_pos="n.", is_en=True)
                    if adj_matches and noun_matches and ("adj." in adj_matches[0][1] or cand_adj in COMMON_ADJECTIVES_EN_TR) and ("n." in noun_matches[0][1] or cand_noun in COMMON_NOUNS_EN_TR):
                        adj_tr = adj_matches[0][0]
                        noun_tr = noun_matches[0][0]
                        role = "subject" if i == 0 else "object"
                        if copula_predicate and role == "object":
                            noun_tr = attach_copula_suffix(noun_tr, copula_predicate)
                            copula_predicate = None
                        combined = f"{adj_tr} bir {noun_tr}"
                        breakdown.append({
                            "original": f"{token} {raw_tokens[i+1]} {raw_tokens[i+2]}",
                            "translated": combined,
                            "role": role,
                            "pos": "adj_np"
                        })
                        i += 3
                        continue
                elif i + 1 < n and raw_tokens[i+1] not in ".,!?;":
                    cand_noun = raw_tokens[i+1].lower()
                    noun_matches = self._lookup_word(cand_noun, preferred_pos="n.", is_en=True)
                    if noun_matches and ("n." in noun_matches[0][1] or cand_noun in COMMON_NOUNS_EN_TR):
                        noun_tr = noun_matches[0][0]
                        role = "subject" if i == 0 else "object"
                        if copula_predicate and role == "object":
                            noun_tr = attach_copula_suffix(noun_tr, copula_predicate)
                            copula_predicate = None
                        combined = f"bir {noun_tr}"
                        breakdown.append({
                            "original": f"{token} {raw_tokens[i+1]}",
                            "translated": combined,
                            "role": role,
                            "pos": "indef_np"
                        })
                        i += 2
                        continue

                breakdown.append({"original": token, "translated": "bir", "role": "determiner", "pos": "art"})
                i += 1
                continue
            elif t_lower == "the":
                # Check if followed by adj + noun: "the brave soldier"
                if i + 2 < n and raw_tokens[i+2] not in ".,!?;":
                    cand_adj = raw_tokens[i+1].lower()
                    cand_noun = raw_tokens[i+2].lower()
                    adj_matches = self._lookup_word(cand_adj, preferred_pos="adj.", is_en=True)
                    noun_matches = self._lookup_word(cand_noun, preferred_pos="n.", is_en=True)
                    if adj_matches and noun_matches and ("adj." in adj_matches[0][1] or cand_adj in COMMON_ADJECTIVES_EN_TR) and ("n." in noun_matches[0][1] or cand_noun in COMMON_NOUNS_EN_TR):
                        adj_tr = adj_matches[0][0]
                        noun_tr = noun_matches[0][0]
                        role = "subject" if i == 0 else "object"
                        combined = f"{adj_tr} {noun_tr}"
                        if i == 0:
                            combined = combined.capitalize()
                            subject_person = "3s"
                        breakdown.append({
                            "original": f"{token} {raw_tokens[i+1]} {raw_tokens[i+2]}",
                            "translated": combined,
                            "role": role,
                            "pos": "def_adj_np"
                        })
                        i += 3
                        continue
                # Check if it starts the sentence as subject determiner: "The doctor..."
                if i == 0 and i + 1 < n:
                    noun = raw_tokens[i+1]
                    noun_matches = self._lookup_word(noun, preferred_pos="n.", is_en=True)
                    noun_tr = noun_matches[0][0] if noun_matches else noun
                    subject_person = "3s"
                    breakdown.append({
                        "original": f"{token} {noun}",
                        "translated": noun_tr.capitalize(),
                        "role": "subject",
                        "pos": "def_np"
                    })
                    i += 2
                    continue
                else:
                    i += 1
                    continue

            # 11. Verb Context & Lemmatization
            prev_role = breakdown[-1]["role"] if breakdown else ""
            is_verb_context = (
                prev_role in ["subject", "question_wh"] 
                or has_future_modal 
                or has_can_modal 
                or has_must_modal 
                or has_should_modal 
                or has_want_modal 
                or is_negated 
                or is_continuous 
                or aux_tense is not None
            )

            lemma, v_tense = self._extract_english_verb_lemma(t_lower)
            if has_future_modal:
                v_tense = "future"
            elif is_continuous:
                v_tense = "past_continuous" if cont_tense == "past" else "present"
            elif aux_tense:
                v_tense = aux_tense

            # Check if token is verb
            matches = self._lookup_word(lemma, preferred_pos="v." if is_verb_context else None, is_en=True)
            
            if matches and (is_verb_context or "v." in matches[0][1] or lemma in COMMON_VERBS_EN_TR):
                top_tr = matches[0][0]
                # Ensure it's a verb lemma ending in mek/mak
                if not (top_tr.endswith("mek") or top_tr.endswith("mak")):
                    if lemma in COMMON_VERBS_EN_TR:
                        top_tr = COMMON_VERBS_EN_TR[lemma]

                conjugated = self._conjugate_turkish_verb(
                    top_tr, 
                    tense=v_tense, 
                    person=subject_person, 
                    is_negative=is_negated, 
                    can_modal=has_can_modal,
                    must_modal=has_must_modal,
                    should_modal=has_should_modal,
                    want_modal=has_want_modal
                )

                breakdown.append({
                    "original": token,
                    "translated": conjugated,
                    "role": "verb",
                    "pos": "v.",
                    "alternatives": [m[0] for m in matches[1:3]]
                })
                i += 1
                continue

            # 12. Nouns and Adjectives
            next_t = raw_tokens[i+1].lower() if i + 1 < n else ""
            has_following_noun = (next_t and next_t not in ".,!?;")
            cand_adj_matches = self._lookup_word(t_lower, preferred_pos="adj.", is_en=True)
            if cand_adj_matches and ("adj." in cand_adj_matches[0][1] or t_lower in COMMON_ADJECTIVES_EN_TR) and has_following_noun:
                matches = cand_adj_matches
            else:
                is_noun_context = (prev_role in ["determiner", "adjective"])
                pref_pos = "n." if is_noun_context else None
                matches = self._lookup_word(t_lower, preferred_pos=pref_pos, is_en=True)

            if matches:
                top_tr = matches[0][0]
                top_pos = matches[0][1]
                role = "adjective" if "adj." in top_pos else "object"

                breakdown.append({
                    "original": token,
                    "translated": top_tr,
                    "role": role,
                    "pos": top_pos,
                    "alternatives": [m[0] for m in matches[1:3]]
                })
            else:
                # Proper noun or unknown token fallback
                if token[0].isupper():
                    breakdown.append({"original": token, "translated": token, "role": "object", "pos": "proper_noun"})
                else:
                    breakdown.append({"original": token, "translated": token, "role": "object", "pos": "unknown"})

            i += 1

        # 13. Copula ("to be") Attachment (e.g. "Ayşe is a teacher")
        if copula_predicate and not any(b["role"] == "verb" for b in breakdown):
            if breakdown:
                for b in reversed(breakdown):
                    if b["role"] in ["object", "adjective"]:
                        b["translated"] = attach_copula_suffix(b["translated"], copula_predicate)
                        break

        # 14. SOV Clause Reordering: Connectors + Subject + Time + Adverbials + Objects/Slang/Idiom + Question_Wh + Verb
        connectors = [b for b in breakdown if b["role"] == "connector"]
        subjects = [b for b in breakdown if b["role"] == "subject"]
        times = [b for b in breakdown if b["role"] == "time"]
        adverbials = [b for b in breakdown if b["role"] == "adverbial"]
        objects = [b for b in breakdown if b["role"] in ["object", "determiner", "adjective", "slang", "idiom"]]
        question_whs = [b for b in breakdown if b["role"] == "question_wh"]
        verbs = [b for b in breakdown if b["role"] == "verb"]
        puncts = [b for b in breakdown if b["role"] == "punct"]

        reordered = connectors + subjects + times + adverbials + objects + question_whs + verbs
        words = [b["translated"] for b in reordered if b["translated"]]

        sentence_str = " ".join(words)
        if puncts:
            sentence_str += puncts[-1]["original"]

        if sentence_str:
            sentence_str = sentence_str[0].upper() + sentence_str[1:]

        return {
            "translated_text": sentence_str,
            "breakdown": breakdown
        }

    def _parse_aux_verb(self, aux_token: str, base_en: str, subject_person: str = "3s") -> Tuple[str, bool, bool]:
        """
        Parses auxiliary verb token for Turkish compound verbs.
        Returns: (en_verb_conjugated, is_imperative, is_negative)
        """
        a_lower = turkish_lower(aux_token)

        # 1. Negative imperative: verme, etme, yapma, olma, vermesene, etmesene, yapmasana
        if any(a_lower.startswith(p) for p in ["verme", "etme", "yapma", "olma", "dileme", "kılma"]):
            return (f"do not {base_en}", True, True)

        # 2. Positive imperative / request: ver, et, yap, ol, dile, versene, etsene, yapsana, olsana, dilesene, verin, edin, yapın, olun
        if (
            a_lower.endswith(("sene", "sana"))
            or a_lower in ["ver", "et", "yap", "ol", "dile", "verin", "edin", "yapın", "olun", "veriniz", "ediniz", "yapınız", "olunuz"]
        ):
            return (base_en, True, False)

        # 3. Past: -di/-dı/-du/-dü/-ti/-tı/-tu/-tü
        if any(a_lower.startswith(p) for p in ["verd", "ett", "old", "yapt", "diled", "kıld"]):
            is_neg = "me" in a_lower or "ma" in a_lower
            if is_neg:
                return (f"did not {base_en}", False, True)
            return (make_past_en(base_en), False, False)

        # 4. Continuous: -iyor/-ıyor/-uyor/-üyor
        if any(c in a_lower for c in ["iyor", "ıyor", "uyor", "üyor"]):
            is_neg = "miyor" in a_lower or "mıyor" in a_lower or "müyor" in a_lower or "muyor" in a_lower
            if is_neg:
                v_form = f"does not {base_en}" if subject_person == "3s" else f"do not {base_en}"
            else:
                v_form = make_3s_present_en(base_en) if subject_person == "3s" else base_en
            return (v_form, False, is_neg)

        # 5. Future: -ecek/-acak
        if any(c in a_lower for c in ["ecek", "acak"]):
            is_neg = "meyecek" in a_lower or "mayacak" in a_lower
            if is_neg:
                return (f"will not {base_en}", False, True)
            return (f"will {base_en}", False, False)

        # 6. Modals: ebil/abil, malı/meli
        if "ebil" in a_lower or "abil" in a_lower:
            return (f"can {base_en}", False, False)
        if "meli" in a_lower or "malı" in a_lower:
            return (f"must {base_en}", False, False)

        # 7. Aorist: ederim, eder, verir, yapar, olur
        if a_lower.endswith(("rim", "rım", "rum", "rüm")):
            return (base_en, False, False)

        # Default fallback:
        return (base_en, True, False)

    def _resolve_verb_infinitive(self, stem: str) -> Optional[Tuple[str, str]]:
        """
        Resolves a Turkish verb stem to its infinitive and base English verb.
        Uses cached overrides, then queries the database for [stem]mak or [stem]mek.
        """
        if not stem or len(stem) < 2:
            return None

        # 1. Fast check in COMMON_TR_VERB_STEMS
        if stem in COMMON_TR_VERB_STEMS:
            tr_inf = COMMON_TR_VERB_STEMS[stem]
            en_v = COMMON_VERBS_TR_EN.get(tr_inf, "act")
            return (tr_inf, en_v)

        # 2. Check candidate infinitives in database (stem + mak / stem + mek)
        for inf_cand in [stem + "mak", stem + "mek", stem + "tmak", stem + "tmek"]:
            if inf_cand in COMMON_VERBS_TR_EN:
                return (inf_cand, COMMON_VERBS_TR_EN[inf_cand])

            self.cur.execute("""
                SELECT en, category, type FROM bilingual 
                WHERE tr_lower = ? AND type IN ('v.', 'verb')
                ORDER BY CASE 
                    WHEN category = 'Common Usage' THEN 0 
                    WHEN category = 'General' THEN 1 
                    ELSE 5 
                END ASC
                LIMIT 1;
            """, (inf_cand,))
            row = self.cur.fetchone()
            if row and row[0]:
                raw_en = row[0]
                cleaned_en = re.sub(r"\(.*?\)", "", raw_en).strip()
                if cleaned_en.lower().startswith("to "):
                    cleaned_en = cleaned_en[3:].strip()
                cleaned_en = cleaned_en.split(",")[0].split(";")[0].strip()

                if inf_cand == "aldatmak":
                    cleaned_en = "cheat on"
                elif inf_cand == "bakmak":
                    cleaned_en = "look at"
                elif inf_cand == "dinlemek":
                    cleaned_en = "listen to"
                elif inf_cand == "beklemek":
                    cleaned_en = "wait for"
                elif inf_cand == "inanmak":
                    cleaned_en = "believe in"

                return (inf_cand, cleaned_en)

        return None

    def _parse_turkish_possessive_noun(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Parses inflected Turkish nouns with possessive suffixes and consonant softening reversal
        (e.g., 'dengim' -> stem 'denk' + 1s possessive 'my' -> 'equal',
               'kitabım' -> stem 'kitap' + 1s possessive 'my' -> 'book',
               'ağacım' -> stem 'ağaç' + 1s possessive 'my' -> 'tree').
        """
        w_low = turkish_lower(word)

        # High-precision mapping for conversational kinship / human nouns
        COMMON_POSSESSIVE_NOUNS = {
            "karım": ("karı", "wife", "1s", "my"),
            "karın": ("karı", "wife", "2s", "your"),
            "karısı": ("karı", "wife", "3s", "his"),
            "kocam": ("koca", "husband", "1s", "my"),
            "kocan": ("koca", "husband", "2s", "your"),
            "kocası": ("koca", "husband", "3s", "her"),
            "eşim": ("eş", "spouse", "1s", "my"),
            "eşin": ("eş", "spouse", "2s", "your"),
            "eşi": ("eş", "spouse", "3s", "his/her"),
            "annem": ("anne", "mother", "1s", "my"),
            "annen": ("anne", "mother", "2s", "your"),
            "annesi": ("anne", "mother", "3s", "his/her"),
            "babam": ("baba", "father", "1s", "my"),
            "baban": ("baba", "father", "2s", "your"),
            "babası": ("baba", "father", "3s", "his/her"),
            "oğlum": ("oğul", "son", "1s", "my"),
            "oğlun": ("oğul", "son", "2s", "your"),
            "oğlu": ("oğul", "son", "3s", "his/her"),
            "kızım": ("kız", "daughter", "1s", "my"),
            "kızın": ("kız", "daughter", "2s", "your"),
            "kızı": ("kız", "daughter", "3s", "his/her"),
            "kardeşim": ("kardeş", "brother", "1s", "my"),
            "kardeşin": ("kardeş", "brother", "2s", "your"),
            "kardeşi": ("kardeş", "brother", "3s", "his/her"),
            "ablam": ("abla", "older sister", "1s", "my"),
            "abim": ("abi", "older brother", "1s", "my"),
            "arkadaşım": ("arkadaş", "friend", "1s", "my"),
            "arkadaşın": ("arkadaş", "friend", "2s", "your"),
            "arkadaşı": ("arkadaş", "friend", "3s", "his/her"),
            "sevgilim": ("sevgili", "darling", "1s", "my"),
            "hayatım": ("hayat", "my life/darling", "1s", "my"),
        }
        if w_low in COMMON_POSSESSIVE_NOUNS:
            stem, en_n, person, poss_en = COMMON_POSSESSIVE_NOUNS[w_low]
            return {
                "stem": stem,
                "en_noun": en_n,
                "person": person,
                "poss_en": poss_en,
                "pos": "n.",
                "category": "Common Usage"
            }

        # Root word protection: Never split atomic words into fake possessive stems
        # e.g., 'hanım' is NOT 'han' + 'ım' (inn + my)
        PROTECTED_ROOT_WORDS = {
            "hanım", "hanim", "kadın", "kadin", "torun", "burun", "odun", "resim", "mevsim",
            "isim", "adım", "adim", "durum", "bölüm", "bolum", "çözüm", "cozum", "toplum",
            "verim", "akım", "akim", "bakım", "bakim", "seçim", "secim", "yaşam", "yasam",
            "dönem", "donem", "kavram", "eylem", "üretim", "tüketim", "tanım", "tanim"
        }
        if w_low in PROTECTED_ROOT_WORDS:
            return None
        if w_low in COMMON_NOUNS_TR_EN or w_low in COMMON_ADJECTIVES_TR_EN:
            return None
        self.cur.execute("SELECT 1 FROM bilingual WHERE tr_lower = ? AND category IN ('Common Usage', 'General') AND type IN ('n.', 'noun', 'adj.') LIMIT 1;", (w_low,))
        if self.cur.fetchone():
            return None

        suffixes = [
            ("imiz", "1p", "our"), ("ımız", "1p", "our"), ("ümüz", "1p", "our"), ("umuz", "1p", "our"),
            ("iniz", "2p", "your"), ("ınız", "2p", "your"), ("ünüz", "2p", "your"), ("unuz", "2p", "your"),
            ("leri", "3p", "their"), ("ları", "3p", "their"),
            ("im", "1s", "my"), ("ım", "1s", "my"), ("üm", "1s", "my"), ("um", "1s", "my"),
            ("in", "2s", "your"), ("ın", "2s", "your"), ("ün", "2s", "your"), ("un", "2s", "your"),
            ("si", "3s", "his"), ("sı", "3s", "his"), ("sü", "3s", "his"), ("su", "3s", "his"),
            ("i", "3s", "his"), ("ı", "3s", "his"), ("ü", "3s", "his"), ("u", "3s", "his"),
            ("m", "1s", "my"), ("n", "2s", "your")
        ]

        best_match = None
        best_priority = 999

        for suff, person, poss_en in suffixes:
            if w_low.endswith(suff) and len(w_low) > len(suff) + 1:
                raw_stem = w_low[:-len(suff)]
                cands = []
                # Consonant softening reversal: g/ğ -> k, b -> p, d -> t, c -> ç
                if raw_stem.endswith("g") or raw_stem.endswith("ğ"):
                    cands.append(raw_stem[:-1] + "k")
                if raw_stem.endswith("b"):
                    cands.append(raw_stem[:-1] + "p")
                if raw_stem.endswith("d"):
                    cands.append(raw_stem[:-1] + "t")
                if raw_stem.endswith("c"):
                    cands.append(raw_stem[:-1] + "ç")
                cands.append(raw_stem)

                for cand in cands:
                    if cand in COMMON_NOUNS_TR_EN:
                        return {
                            "stem": cand,
                            "en_noun": COMMON_NOUNS_TR_EN[cand],
                            "person": person,
                            "poss_en": poss_en,
                            "pos": "n.",
                            "category": "Common Usage"
                        }
                    if cand in COMMON_ADJECTIVES_TR_EN:
                        return {
                            "stem": cand,
                            "en_noun": COMMON_ADJECTIVES_TR_EN[cand],
                            "person": person,
                            "poss_en": poss_en,
                            "pos": "adj.",
                            "category": "Common Usage"
                        }

                    self.cur.execute("""
                        SELECT en, type, category,
                            CASE 
                                WHEN category = 'Common Usage' THEN 0 
                                WHEN category = 'General' THEN 1 
                                WHEN category = 'Wiktionary / Çekim' THEN 20
                                ELSE 5 
                            END as prio
                        FROM bilingual 
                        WHERE tr_lower = ? 
                        ORDER BY prio ASC
                        LIMIT 1;
                    """, (cand,))
                    row = self.cur.fetchone()
                    if row:
                        prio = row[3]
                        if prio < best_priority:
                            best_priority = prio
                            best_match = {
                                "stem": cand,
                                "en_noun": row[0],
                                "person": person,
                                "poss_en": poss_en,
                                "pos": row[1],
                                "category": row[2]
                            }
                            if prio == 0:
                                return best_match

        return best_match

    def _translate_tr_to_en(self, sentence: str, show_slang_profanity: bool = True) -> Dict[str, Any]:
        """
        Turkish to English syntax translation with morphological parsing and SOV -> SVO reordering.
        Supports compound verbs, colloquial requests (-sene/-sana), full pronouns, and slang / profanity toggling.
        """
        raw_tokens = re.findall(r"\b[\w'-]+\b|[.,!?;]", sentence)
        if not raw_tokens:
            return {"translated_text": "", "breakdown": []}

        breakdown = []
        i = 0
        n = len(raw_tokens)
        subject_person = "3s"
        copula_predicate = None

        while i < n:
            token = raw_tokens[i]
            t_lower = turkish_lower(token)

            # 0a. Multi-word slang idiom check (longest match first)
            matched_slang = False
            for span_len in (4, 3, 2):
                if i + span_len <= n:
                    span_tokens = [turkish_lower(raw_tokens[k]) for k in range(i, i + span_len)]
                    span_str = re.sub(r"[^\w\s']", "", " ".join(span_tokens)).strip()
                    if span_str in SLANG_IDIOMS_TR_EN:
                        idata = SLANG_IDIOMS_TR_EN[span_str]
                        ival = idata["slang"] if show_slang_profanity else idata["clean"]
                        breakdown.append({
                            "original": " ".join([raw_tokens[k] for k in range(i, i + span_len)]),
                            "translated": ival,
                            "role": "idiom",
                            "pos": "idiom",
                            "alternatives": [idata["clean"] if show_slang_profanity else idata["slang"]]
                        })
                        i += span_len
                        matched_slang = True
                        break
            if matched_slang:
                continue

            # 0b. Single-word slang check
            if t_lower in SLANG_WORDS_TR_EN:
                sdata = SLANG_WORDS_TR_EN[t_lower]
                sval = sdata["slang"] if show_slang_profanity else sdata["clean"]
                breakdown.append({
                    "original": token,
                    "translated": sval,
                    "role": "slang",
                    "pos": "slang",
                    "alternatives": [sdata["clean"] if show_slang_profanity else sdata["slang"]]
                })
                i += 1
                continue

            # 0c. Wh- Question Starters (e.g. ne, nerede, ne zaman, neden, nasıl, kim)
            if t_lower in QUESTION_STARTERS_TR:
                breakdown.append({
                    "original": token,
                    "translated": QUESTION_STARTERS_TR[t_lower],
                    "role": "question_wh",
                    "pos": "wh_word"
                })
                i += 1
                continue

            # 0d. Turkish Standalone Vocatives & Honorifics
            if t_lower in ["hanımefendi", "hanimefendi"]:
                breakdown.append({
                    "original": token,
                    "translated": "ma'am",
                    "role": "vocative",
                    "pos": "vocative"
                })
                i += 1
                continue
            elif t_lower in ["beyefendi"]:
                breakdown.append({
                    "original": token,
                    "translated": "sir",
                    "role": "vocative",
                    "pos": "vocative"
                })
                i += 1
                continue
            elif t_lower in ["efendim"]:
                breakdown.append({
                    "original": token,
                    "translated": "sir",
                    "role": "vocative",
                    "pos": "vocative"
                })
                i += 1
                continue

            # Person Name + Title (e.g. "Ayşe Hanım" -> "Ms. Ayşe", "Ali Bey" -> "Mr. Ali")
            if i + 1 < n and t_lower not in INVALID_TITLE_PREV:
                next_tok = raw_tokens[i+1]
                n_lower = turkish_lower(next_tok)
                if n_lower in ["hanım", "hanim"]:
                    breakdown.append({
                        "original": f"{token} {next_tok}",
                        "translated": f"Ms. {token.capitalize()}",
                        "role": "vocative",
                        "pos": "vocative"
                    })
                    i += 2
                    continue
                elif n_lower in ["bey"]:
                    breakdown.append({
                        "original": f"{token} {next_tok}",
                        "translated": f"Mr. {token.capitalize()}",
                        "role": "vocative",
                        "pos": "vocative"
                    })
                    i += 2
                    continue
                elif n_lower in ["hoca", "hocam"]:
                    breakdown.append({
                        "original": f"{token} {next_tok}",
                        "translated": f"Teacher {token.capitalize()}",
                        "role": "vocative",
                        "pos": "vocative"
                    })
                    i += 2
                    continue

            # 0e. Turkish Greetings & Salutations (e.g. "merhaba", "günaydın", "iyi günler")
            if i + 1 < n:
                two_tok_str = f"{t_lower} {turkish_lower(raw_tokens[i+1])}"
                multi_greetings = {
                    "iyi günler": "Have a nice day",
                    "iyi gunler": "Have a nice day",
                    "iyi akşamlar": "Good evening",
                    "iyi aksamlar": "Good evening",
                    "iyi geceler": "Good night",
                    "hoşça kal": "Goodbye",
                    "hosca kal": "Goodbye",
                    "hoşça kalın": "Goodbye",
                    "hosca kalin": "Goodbye"
                }
                if two_tok_str in multi_greetings:
                    breakdown.append({
                        "original": f"{token} {raw_tokens[i+1]}",
                        "translated": multi_greetings[two_tok_str],
                        "role": "greeting",
                        "pos": "greeting"
                    })
                    i += 2
                    continue

            single_greetings = {
                "merhaba": "Hello",
                "selam": "Hello",
                "selamlar": "Greetings",
                "günaydın": "Good morning",
                "gunaydin": "Good morning",
                "tünaydın": "Good afternoon",
                "tunaydin": "Good afternoon",
                "hoşçakal": "Goodbye",
                "hoscakal": "Goodbye",
                "hoşçakalın": "Goodbye",
                "hoscakalin": "Goodbye",
                "görüşürüz": "See you",
                "gorusuruz": "See you"
            }
            if t_lower in single_greetings:
                breakdown.append({
                    "original": token,
                    "translated": single_greetings[t_lower],
                    "role": "greeting",
                    "pos": "greeting"
                })
                i += 1
                continue

            # 1. Punctuation
            if token in ".,!?;":
                breakdown.append({"original": token, "translated": token, "role": "punct", "pos": "punct"})
                i += 1
                continue

            # 2. Conjunctions & Polite Markers
            if t_lower in ["ve", "veya", "ama", "fakat", "çünkü", "eğer", "lütfen"]:
                tr_conj_map = {
                    "ve": "and", "veya": "or", "ama": "but", "fakat": "but",
                    "çünkü": "because", "eğer": "if", "lütfen": "please"
                }
                breakdown.append({"original": token, "translated": tr_conj_map[t_lower], "role": "connector", "pos": "conj"})
                i += 1
                continue

            # 2a. Turkish Question Copulas (mısınız, misiniz, musunuz, mısın, misin, mı, mi, vb.)
            if t_lower in TURKISH_QUESTION_COPULAS:
                qdata = TURKISH_QUESTION_COPULAS[t_lower]
                breakdown.append({
                    "original": token,
                    "translated": qdata["aux"],
                    "role": "copula_question",
                    "pos": "copula_q",
                    "person": qdata["person"],
                    "aux": qdata["aux"]
                })
                i += 1
                continue

            # 2b. Turkish Copula Negation (değilim, değilsin, değil, değiliz, değilsiniz, değiller, etc.)
            if t_lower in TURKISH_COPULA_NEGATION:
                cneg_data = TURKISH_COPULA_NEGATION[t_lower]
                breakdown.append({
                    "original": token,
                    "translated": cneg_data["en"],
                    "role": "copula_negation",
                    "pos": "copula_negation",
                    "person": cneg_data["person"]
                })
                i += 1
                continue

            # 2c. Sentential Adverbs (maalesef, ne yazık ki, aslında, kesinlikle, vb.)
            matched_adv = False
            for span_len in (3, 2):
                if i + span_len <= n:
                    span_tokens = [turkish_lower(raw_tokens[k]) for k in range(i, i + span_len)]
                    span_str = " ".join(span_tokens)
                    if span_str in SENTENTIAL_ADVERBS:
                        is_start = (i == 0 or (i == 1 and breakdown and breakdown[0]["role"] in ["greeting", "connector"]))
                        breakdown.append({
                            "original": " ".join([raw_tokens[k] for k in range(i, i + span_len)]),
                            "translated": SENTENTIAL_ADVERBS[span_str],
                            "role": "sentential_adverb",
                            "pos": "adv.",
                            "is_sentence_start": is_start
                        })
                        i += span_len
                        matched_adv = True
                        break
            if matched_adv:
                continue

            if t_lower in SENTENTIAL_ADVERBS:
                is_start = (i == 0 or (i == 1 and breakdown and breakdown[0]["role"] in ["greeting", "connector"]))
                breakdown.append({
                    "original": token,
                    "translated": SENTENTIAL_ADVERBS[t_lower],
                    "role": "sentential_adverb",
                    "pos": "adv.",
                    "is_sentence_start": is_start
                })
                i += 1
                continue

            # 3. Time Adverbs
            if t_lower in ["dün", "bugün", "yarın", "şimdi", "her zaman", "asla", "bazen", "yakında", "sonra"]:
                tr_time_map = {
                    "dün": "yesterday", "bugün": "today", "yarın": "tomorrow", "şimdi": "now",
                    "her zaman": "always", "asla": "never", "bazen": "sometimes", "yakında": "soon", "sonra": "later"
                }
                breakdown.append({"original": token, "translated": tr_time_map[t_lower], "role": "time", "pos": "adv"})
                i += 1
                continue

            # 3b. Turkish Compound Verbs (Birleşik Fiiller)
            # Checks 2-token spans: [noun, aux] or devrik [aux, noun]
            if i + 1 < n:
                next_tok = raw_tokens[i+1]
                n_lower = turkish_lower(next_tok)

                # Order A: Noun + Aux (e.g., 'cevap versene', 'yardım et', 'teşekkür ederim')
                if t_lower in TURKISH_COMPOUND_VERBS:
                    matched_comp = False
                    for aux_root, (en_v, is_trans) in TURKISH_COMPOUND_VERBS[t_lower].items():
                        if n_lower.startswith(aux_root) or (aux_root == "et" and n_lower.startswith(("ed", "et"))):
                            en_conjugated, is_imp, is_neg = self._parse_aux_verb(next_tok, en_v, subject_person)
                            breakdown.append({
                                "original": f"{token} {next_tok}",
                                "translated": en_conjugated,
                                "role": "verb",
                                "pos": "v.",
                                "is_imperative": is_imp,
                                "is_transitive": is_trans
                            })
                            i += 2
                            matched_comp = True
                            break
                    if matched_comp:
                        continue

                # Order B: Devrik Aux + Noun (e.g., 'versene cevap', 'etsene yardım')
                if n_lower in TURKISH_COMPOUND_VERBS:
                    matched_comp = False
                    for aux_root, (en_v, is_trans) in TURKISH_COMPOUND_VERBS[n_lower].items():
                        if t_lower.startswith(aux_root) or (aux_root == "et" and t_lower.startswith(("ed", "et"))):
                            en_conjugated, is_imp, is_neg = self._parse_aux_verb(token, en_v, subject_person)
                            breakdown.append({
                                "original": f"{token} {next_tok}",
                                "translated": en_conjugated,
                                "role": "verb",
                                "pos": "v.",
                                "is_imperative": is_imp,
                                "is_transitive": is_trans
                            })
                            i += 2
                            matched_comp = True
                            break
                    if matched_comp:
                        continue

            # 3c. Colloquial requests and imperatives (-sene / -sana)
            if t_lower.endswith(("sene", "sana", "mesene", "masana")):
                is_neg_req = t_lower.endswith(("mesene", "masana"))
                req_stem = t_lower[:-6] if is_neg_req else t_lower[:-4]
                if req_stem in TURKISH_IMPERATIVE_STEMS:
                    base_req_v = TURKISH_IMPERATIVE_STEMS[req_stem]
                elif req_stem in COMMON_TR_VERB_STEMS:
                    tr_inf = COMMON_TR_VERB_STEMS[req_stem]
                    base_req_v = COMMON_VERBS_TR_EN.get(tr_inf, req_stem)
                else:
                    base_req_v = None

                if base_req_v:
                    if req_stem == "bak":
                        base_req_v = "look at"
                    elif req_stem == "dinle":
                        base_req_v = "listen to"

                    v_req_str = f"do not {base_req_v}" if is_neg_req else base_req_v
                    breakdown.append({
                        "original": token,
                        "translated": v_req_str,
                        "role": "verb",
                        "pos": "v.",
                        "is_imperative": True,
                        "is_transitive": req_stem in ["ver", "yap", "al", "oku", "yaz", "ye", "iç", "dinle", "bak", "bekle"]
                    })
                    i += 1
                    continue

            # 3d. Bare & Polite Imperatives (ver, yap, bak, dinle, gelin, bakın)
            is_followed_by_q_copula = (i + 1 < n and turkish_lower(raw_tokens[i+1]) in TURKISH_QUESTION_COPULAS)
            is_imp_word = False
            stem_imp_found = None
            if not is_followed_by_q_copula:
                if t_lower in TURKISH_IMPERATIVE_STEMS:
                    is_imp_word = True
                    stem_imp_found = t_lower
                else:
                    for s in TURKISH_IMPERATIVE_STEMS:
                        for end in ["in", "ın", "un", "ün", "yin", "yın", "yun", "yün", "iniz", "ınız", "ünüz", "unuz"]:
                            if t_lower == s + end:
                                is_imp_word = True
                                stem_imp_found = s
                                break
                        if is_imp_word:
                            break

            if is_imp_word and stem_imp_found:
                base_imp_v = TURKISH_IMPERATIVE_STEMS[stem_imp_found]
                if stem_imp_found == "bak":
                    base_imp_v = "look at"
                elif stem_imp_found == "dinle":
                    base_imp_v = "listen to"

                breakdown.append({
                    "original": token,
                    "translated": base_imp_v,
                    "role": "verb",
                    "pos": "v.",
                    "is_imperative": True,
                    "is_transitive": stem_imp_found in ["ver", "yap", "al", "oku", "yaz", "ye", "iç", "dinle", "bak", "bekle"]
                })
                i += 1
                continue

            # 4. Full Turkish Pronoun Resolution (Nominative, Accusative, Dative, Locative, Ablative, Instrumental, Genitive)
            if t_lower in TURKISH_PRONOUNS_FULL:
                pdata = TURKISH_PRONOUNS_FULL[t_lower]
                p_role = pdata["role"]
                p_case = pdata.get("case", "nominative")

                if p_role == "subject":
                    subject_person = pdata["person"]
                    breakdown.append({"original": token, "translated": pdata["en"], "role": "subject", "pos": "pronoun"})
                elif p_case == "dative":
                    is_transitive_context = False
                    for b in breakdown:
                        if b.get("is_transitive") or b.get("translated") in [
                            "answer", "help", "thank", "call", "tell", "ask", "follow", "visit", "notice", "look at", "listen to", "give"
                        ]:
                            is_transitive_context = True
                            break
                    if not is_transitive_context:
                        for fut_tok in raw_tokens[i+1:]:
                            fut_low = turkish_lower(fut_tok)
                            if fut_low in TURKISH_COMPOUND_VERBS or fut_low in ["cevap", "yardım", "yanıt", "teşekkür"]:
                                is_transitive_context = True
                                break
                            for imp in ["ver", "versene", "bak", "baksana", "et", "etsene", "söyle", "söylesene", "dinle", "dinlesene"]:
                                if fut_low.startswith(imp):
                                    is_transitive_context = True
                                    break

                    tr_word = pdata["en"] if is_transitive_context else pdata.get("prep_en", pdata["en"])
                    breakdown.append({
                        "original": token,
                        "translated": tr_word,
                        "role": "object",
                        "pos": "pronoun",
                        "case": "dative"
                    })
                elif p_case == "accusative":
                    breakdown.append({
                        "original": token,
                        "translated": pdata["en"],
                        "role": "object",
                        "pos": "pronoun",
                        "case": "accusative"
                    })
                elif p_role == "possessive":
                    breakdown.append({
                        "original": token,
                        "translated": pdata["en"],
                        "role": "possessive",
                        "pos": "pronoun",
                        "case": "genitive"
                    })
                else:
                    breakdown.append({
                        "original": token,
                        "translated": pdata["en"],
                        "role": "adverbial",
                        "pos": "pronoun",
                        "case": p_case
                    })
                i += 1
                continue


            # 5. Proper Noun with Apostrophe (e.g. "Londra'da", "Paris'te", "Ayşe'ye", "Ali'den")
            if "'" in token:
                parts = token.split("'", 1)
                stem_raw = parts[0]
                suff = parts[1].lower()
                stem_lower = turkish_lower(stem_raw)

                # Proper place or person name
                if stem_lower in GEOGRAPHIC_NAMES_TR_EN:
                    en_name = GEOGRAPHIC_NAMES_TR_EN[stem_lower]
                else:
                    en_name = stem_raw

                if suff in ["da", "de", "ta", "te"]:
                    combined = f"in {en_name}"
                    role = "adverbial"
                elif suff in ["ya", "ye", "a", "e"]:
                    combined = f"to {en_name}"
                    role = "adverbial"
                elif suff in ["dan", "den", "tan", "ten"]:
                    combined = f"from {en_name}"
                    role = "adverbial"
                elif suff in ["nin", "nın", "nun", "nün", "in", "ın", "un", "ün"]:
                    combined = f"{en_name}'s"
                    role = "possessive"
                else:
                    combined = en_name
                    role = "object"

                breakdown.append({"original": token, "translated": combined, "role": role, "pos": "prop_noun_case"})
                i += 1
                continue

            # 6. Proper Names (e.g. "Ayşe", "Ali", "John")
            if t_lower in COMMON_PERSON_NAMES or (token[0].isupper() and i > 0 and token.isalpha()):
                subject_person = "3s"
                breakdown.append({"original": token, "translated": token, "role": "subject", "pos": "proper_noun"})
                i += 1
                continue

            # 7. Determiners & Numbers (e.g. "bir", "bu", "şu")
            if t_lower == "bir":
                # Check if next token has copula or is noun
                if i + 1 < n and (raw_tokens[i+1].lower().endswith(("dir", "dır", "dur", "dür", "tir", "tır", "tur", "tür"))):
                    # "bir öğretmendir" -> hand off to next token
                    i += 1
                    continue
                breakdown.append({"original": token, "translated": "a", "role": "determiner", "pos": "art"})
                i += 1
                continue
            elif t_lower == "bu":
                breakdown.append({"original": token, "translated": "this", "role": "determiner", "pos": "det"})
                i += 1
                continue
            elif t_lower == "şu":
                breakdown.append({"original": token, "translated": "that", "role": "determiner", "pos": "det"})
                i += 1
                continue

            # 8. Copula Predicate Nouns (e.g. "öğretmendir", "doktordur", "öğrencidir")
            if t_lower.endswith(("dir", "dır", "dur", "dür", "tir", "tır", "tur", "tür")):
                stem = t_lower[:-3]
                stem_en = COMMON_NOUNS_TR_EN.get(stem) or COMMON_ADJECTIVES_TR_EN.get(stem)
                if not stem_en:
                    matches = self._lookup_word(stem, is_en=False)
                    stem_en = matches[0][0] if matches else stem

                # Check if preceded by 'bir'
                prev_orig = raw_tokens[i-1].lower() if i > 0 else ""
                article = "a " if (stem in COMMON_NOUNS_TR_EN and prev_orig != "bir") else ("a " if stem in COMMON_NOUNS_TR_EN else "")
                is_are = "are" if subject_person in ["1p", "2p", "3p"] else ("am" if subject_person == "1s" else "is")

                combined = f"{is_are} {article}{stem_en}".strip()
                breakdown.append({"original": token, "translated": combined, "role": "copula_predicate", "pos": "copula"})
                i += 1
                continue

            # 9. Common Noun with Case Suffix (e.g. "okula", "okulda", "okuldan", "evde", "eve", "hastanede")
            found_case = False
            for case_suff, prep in [
                ("da", "at"), ("de", "at"), ("ta", "at"), ("te", "at"),
                ("dan", "from"), ("den", "from"), ("tan", "from"), ("ten", "from"),
                ("ye", "to"), ("ya", "to"), ("e", "to"), ("a", "to")
            ]:
                if t_lower.endswith(case_suff) and len(t_lower) > len(case_suff):
                    stem = t_lower[:-len(case_suff)]
                    if stem in COMMON_NOUNS_TR_EN:
                        en_noun = COMMON_NOUNS_TR_EN[stem]
                        # Natural prepositions: home -> at home / home, school -> at school / to school
                        if stem == "ev":
                            prep_str = "at home" if prep == "at" else ("from home" if prep == "from" else "home")
                        elif stem == "okul":
                            prep_str = f"{prep} school"
                        elif stem == "hastane":
                            prep_str = "in the hospital" if prep == "at" else f"{prep} the hospital"
                        elif stem == "iş":
                            prep_str = "at work" if prep == "at" else f"{prep} work"
                        else:
                            prep_str = f"{prep} {en_noun}"

                        breakdown.append({"original": token, "translated": prep_str, "role": "adverbial", "pos": "prep_phrase"})
                        found_case = True
                        break

            if found_case:
                i += 1
                continue

            # 10. Turkish Verbs (Continuous, Past, Future)
            found_verb = False
            # Check continuous: -iyor / -ıyor / -uyor / -üyor
            for cont_suff in ["iyor", "ıyor", "uyor", "üyor"]:
                if cont_suff in t_lower:
                    stem_cand = t_lower.split(cont_suff)[0]
                    resolved = self._resolve_verb_infinitive(stem_cand)
                    if resolved:
                        tr_infinitive, en_base = resolved

                        # Determine person
                        if t_lower.endswith(("um", "üm", "ım", "im")):
                            v_person = "1s"
                        elif t_lower.endswith(("uz", "üz")):
                            v_person = "1p"
                        elif t_lower.endswith(("sun", "sün")):
                            v_person = "2s"
                        elif t_lower.endswith(("lar", "ler")):
                            v_person = "3p"
                        else:
                            v_person = subject_person

                        if v_person == "3s":
                            en_v = make_3s_present_en(en_base)
                        else:
                            en_v = en_base

                        breakdown.append({"original": token, "translated": en_v, "role": "verb", "pos": "v."})
                        found_verb = True
                        break

            if found_verb:
                i += 1
                continue

            # Check Past: -di/-dı/-du/-dü/-ti/-tı/-tu/-tü
            for past_suff in ["tim", "tım", "tum", "tüm", "dim", "dım", "dum", "düm",
                              "tik", "tık", "tuk", "tük", "dik", "dık", "duk", "dük",
                              "ti", "tı", "tu", "tü", "di", "dı", "du", "dü"]:
                if t_lower.endswith(past_suff) and len(t_lower) > len(past_suff):
                    stem_cand = t_lower[:-len(past_suff)]
                    resolved = self._resolve_verb_infinitive(stem_cand)
                    if resolved:
                        tr_infinitive, en_base = resolved
                        en_v = make_past_en(en_base)

                        breakdown.append({"original": token, "translated": en_v, "role": "verb", "pos": "v."})
                        found_verb = True
                        break

            if found_verb:
                i += 1
                continue

            # Check Future: -ecek / -acak
            for fut_suff in ["eceğim", "acağım", "eceğiz", "acağız", "ecek", "acak"]:
                if t_lower.endswith(fut_suff) and len(t_lower) > len(fut_suff):
                    stem_cand = t_lower[:-len(fut_suff)]
                    if stem_cand.endswith("y"):
                        stem_cand = stem_cand[:-1]
                    resolved = self._resolve_verb_infinitive(stem_cand)
                    if resolved:
                        tr_infinitive, en_base = resolved
                        en_v = f"will {en_base}"

                        breakdown.append({"original": token, "translated": en_v, "role": "verb", "pos": "v."})
                        found_verb = True
                        break

            if found_verb:
                i += 1
                continue

            # Check Necessity modal: -malı / -meli
            for nec_suff in ["malıyım", "meliyim", "malısın", "melisin", "malı", "meli", "malıyız", "meliyiz", "malısınız", "melisiniz", "malılar", "meliler"]:
                if t_lower.endswith(nec_suff) and len(t_lower) > len(nec_suff):
                    stem_cand = t_lower[:-len(nec_suff)]
                    resolved = self._resolve_verb_infinitive(stem_cand)
                    if resolved:
                        tr_inf, en_b = resolved
                        breakdown.append({"original": token, "translated": f"must {en_b}", "role": "verb", "pos": "v."})
                        found_verb = True
                        break

            if found_verb:
                i += 1
                continue

            # Check Ability modal: -ebilir / -abilir
            for abil_suff in ["ebilirim", "abilirim", "ebilirsin", "abilirsin", "ebilir", "abilir", "ebiliriz", "abiliriz", "ebilirsiniz", "ebilirsiniz", "ebilirler", "abilirler"]:
                if t_lower.endswith(abil_suff) and len(t_lower) > len(abil_suff):
                    stem_cand = t_lower[:-len(abil_suff)]
                    if stem_cand.endswith("y"):
                        stem_cand = stem_cand[:-1]
                    resolved = self._resolve_verb_infinitive(stem_cand)
                    if resolved:
                        tr_inf, en_b = resolved
                        breakdown.append({"original": token, "translated": f"can {en_b}", "role": "verb", "pos": "v."})
                        found_verb = True
                        break

            if found_verb:
                i += 1
                continue

            # 10b. Turkish Possessive Noun Check with Consonant Softening Reversal (e.g. dengim, kitabım, odam, karım)
            poss_noun = self._parse_turkish_possessive_noun(t_lower)
            if poss_noun:
                # If preceded by a possessive pronoun ('my', 'your'), do not duplicate pronoun ('my my equal' -> 'my equal')
                prev_is_poss = bool(breakdown and breakdown[-1].get("role") == "possessive")
                trans_val = poss_noun["en_noun"] if prev_is_poss else f"{poss_noun['poss_en']} {poss_noun['en_noun']}".strip()
                has_copula_neg = any(turkish_lower(t) in TURKISH_COPULA_NEGATION for t in raw_tokens)
                is_subj = (not has_copula_neg) and (not any(b["role"] == "subject" for b in breakdown))
                role = "subject" if is_subj else "object"
                if is_subj:
                    subject_person = "3s"
                breakdown.append({
                    "original": token,
                    "translated": trans_val,
                    "role": role,
                    "pos": "noun (çekim)",
                    "alternatives": [poss_noun["en_noun"]]
                })
                i += 1
                continue

            # 11. Common Nouns, Adjectives & General Dictionary Lookup
            has_copula_neg = any(turkish_lower(t) in TURKISH_COPULA_NEGATION for t in raw_tokens)
            if t_lower in COMMON_NOUNS_TR_EN:
                is_subj = (not has_copula_neg) and (not any(b["role"] == "subject" for b in breakdown))
                role = "subject" if is_subj else "object"
                if is_subj:
                    subject_person = "3s"
                breakdown.append({"original": token, "translated": COMMON_NOUNS_TR_EN[t_lower], "role": role, "pos": "n."})
            elif t_lower in COMMON_ADJECTIVES_TR_EN:
                breakdown.append({"original": token, "translated": COMMON_ADJECTIVES_TR_EN[t_lower], "role": "adjective", "pos": "adj."})
            else:
                matches = self._lookup_word(t_lower, is_en=False)
                if matches:
                    top_en = matches[0][0]
                    top_pos = matches[0][1]
                    is_v = "v." in top_pos or "verb" in top_pos
                    is_subj = (not is_v) and (not has_copula_neg) and (not any(b["role"] == "subject" for b in breakdown))
                    role = "verb" if is_v else ("subject" if is_subj else "object")
                    if is_subj:
                        subject_person = "3s"
                    breakdown.append({
                        "original": token,
                        "translated": top_en,
                        "role": role,
                        "pos": top_pos,
                        "alternatives": [m[0] for m in matches[1:3]]
                    })
                else:
                    breakdown.append({"original": token, "translated": token, "role": "object", "pos": "unknown"})

            i += 1

        # 12. English SVO Clause Reordering: Greetings + Vocatives + Connectors + Subject + Verb/Predicate + Objects + Adverbials + Time
        greetings = [b for b in breakdown if b["role"] == "greeting"]
        vocatives = [b for b in breakdown if b["role"] == "vocative"]
        prefix = greetings + vocatives

        sent_adv_start = [b for b in breakdown if b["role"] == "sentential_adverb" and b.get("is_sentence_start")]
        sent_adv_end = [b for b in breakdown if b["role"] == "sentential_adverb" and not b.get("is_sentence_start")]

        question_whs = [b for b in breakdown if b["role"] == "question_wh"]
        connectors = [b for b in breakdown if b["role"] == "connector"]
        subjects = [b for b in breakdown if b["role"] == "subject"]
        verbs = [b for b in breakdown if b["role"] == "verb"]
        copulas = [b for b in breakdown if b["role"] == "copula_predicate"]
        copula_negs = [b for b in breakdown if b["role"] == "copula_negation"]
        possessives = [b for b in breakdown if b["role"] == "possessive"]
        objects = [b for b in breakdown if b["role"] in ["object", "determiner", "adjective", "slang", "idiom"]]
        adverbials = [b for b in breakdown if b["role"] == "adverbial"]
        times = [b for b in breakdown if b["role"] == "time"]
        puncts = [b for b in breakdown if b["role"] == "punct"]

        copula_questions = [b for b in breakdown if b["role"] == "copula_question"]
        has_imperative = any(b.get("is_imperative") for b in verbs)

        if copula_questions:
            q_aux = copula_questions[0]["aux"]
            preds = [b for b in breakdown if b["role"] in ["adjective", "object", "subject"] and b not in prefix and b not in connectors]
            non_pron_preds = [b for b in preds if b.get("pos") != "pronoun"]
            pred_text = " ".join([b["translated"] for b in non_pron_preds]) if non_pron_preds else (" ".join([b["translated"] for b in preds]) if preds else "")

            # Check if predicate is a singular countable profession/noun
            if pred_text in ["student", "doctor", "teacher", "lawyer", "engineer", "nurse"]:
                pred_text = f"a {pred_text}"

            # Check demonstrative pronoun: "bu doğru mu?" -> "Is this true?"
            if any(b.get("translated") in ["this", "that"] for b in preds):
                dem = "this" if any(b.get("translated") == "this" for b in preds) else "that"
                rem_preds = [b["translated"] for b in preds if b.get("translated") not in ["this", "that"]]
                rem_text = " ".join(rem_preds)
                core_q = f"Is {dem} {rem_text}".strip()
            else:
                core_q = f"{q_aux} {pred_text}".strip()

            voc_words = [b["translated"] for b in vocatives]
            greet_words = [b["translated"] for b in greetings]

            if voc_words:
                core_q = f"{core_q}, {' '.join(voc_words)}"

            if greet_words:
                sentence_str = f"{' '.join(greet_words)}. {core_q}?"
            else:
                sentence_str = f"{core_q}?"

            return {
                "translated_text": sentence_str,
                "breakdown": breakdown
            }
        elif has_imperative:
            # Imperative sentences do not take overt subject pronouns in English
            # e.g., "Answer me.", "Help me.", "Look at me."
            non_pronoun_subjects = [s for s in subjects if s.get("pos") != "pronoun"]
            core = prefix + connectors + non_pronoun_subjects + verbs + possessives + objects + adverbials + times
        elif question_whs:
            if copulas:
                core = prefix + connectors + question_whs + copulas + subjects + possessives + objects + adverbials + times
            elif copula_negs:
                core = prefix + connectors + question_whs + copula_negs + subjects + possessives + objects + adverbials + times
            else:
                core = prefix + connectors + question_whs + verbs + subjects + possessives + objects + adverbials + times
        elif copula_negs:
            subj_person_map = {"1s": "I", "2s": "You", "3s": "It", "1p": "We", "2p": "You", "3p": "They"}
            inferred_subj = subj_person_map.get(copula_negs[0].get("person", "3s"), "It")
            subj_list = subjects if subjects else [{"translated": inferred_subj, "role": "subject", "pos": "pronoun"}]
            core = prefix + connectors + subj_list + copula_negs + possessives + objects + adverbials + times
        elif copulas:
            core = prefix + connectors + subjects + copulas + possessives + objects + adverbials + times
        else:
            core = prefix + connectors + subjects + verbs + possessives + objects + adverbials + times

        prefix_words = [b["translated"] for b in prefix if b["translated"]]
        start_adv_words = [b["translated"] for b in sent_adv_start if b["translated"]]
        core_words = [b["translated"] for b in core if b["translated"] and b not in prefix]
        end_adv_words = [b["translated"] for b in sent_adv_end if b["translated"]]

        parts = []
        if prefix_words:
            parts.append(" ".join(prefix_words))
        if start_adv_words:
            adv_str = " ".join(start_adv_words)
            parts.append(adv_str.capitalize() if not parts else adv_str)
        if core_words:
            parts.append(" ".join(core_words))
        if end_adv_words:
            if parts:
                parts[-1] = parts[-1] + ", " + " ".join(end_adv_words)
            else:
                parts.append(" ".join(end_adv_words))

        if prefix_words and len(parts) > 1:
            rem = " ".join(parts[1:])
            sentence_str = f"{' '.join(prefix_words)}, {rem}" if rem else ' '.join(prefix_words)
        else:
            sentence_str = ", ".join(parts) if (start_adv_words and core_words) else " ".join(parts)

        if puncts:
            sentence_str += puncts[-1]["original"]
        elif has_imperative or greetings or vocatives or sentence_str:
            sentence_str += "."

        if sentence_str:
            sentence_str = sentence_str[0].upper() + sentence_str[1:]

        return {
            "translated_text": sentence_str,
            "breakdown": breakdown
        }

