import os
import re
import sqlite3
from typing import List, Dict, Any, Tuple, Optional
from src.utils import turkish_lower, get_resource_path

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

# Reverse Lookups (TR -> EN)
COMMON_VERBS_TR_EN = {v: k for k, v in COMMON_VERBS_EN_TR.items()}
COMMON_NOUNS_TR_EN = {v: k for k, v in COMMON_NOUNS_EN_TR.items()}
COMMON_ADJECTIVES_TR_EN = {v: k for k, v in COMMON_ADJECTIVES_EN_TR.items()}
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
    if verb == "have": return "has"
    if verb == "be": return "is"
    if verb == "do": return "does"
    if verb == "go": return "goes"
    if verb.endswith(("ss", "sh", "ch", "x", "z", "o")):
        return verb + "es"
    if verb.endswith("y") and len(verb) > 2 and verb[-2] not in "aeiou":
        return verb[:-1] + "ies"
    return verb + "s"

def make_past_en(verb: str) -> str:
    if verb in IRREGULAR_PAST_EN:
        return IRREGULAR_PAST_EN[verb]
    if verb.endswith("e"):
        return verb + "d"
    if verb.endswith("y") and len(verb) > 2 and verb[-2] not in "aeiou":
        return verb[:-1] + "ied"
    return verb + "ed"

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

        if preferred_pos:
            self.cur.execute(f"""
            SELECT {tgt_col}, type, category 
            FROM bilingual 
            WHERE {col} = ? AND type LIKE ?
            ORDER BY 
                CASE 
                    WHEN category = 'Common Usage' THEN 0 
                    WHEN category = 'General' THEN 1 
                    ELSE 2 
                END 
            LIMIT 5;
            """, (w_lower, f"%{preferred_pos}%"))
            rows = self.cur.fetchall()
            if rows:
                return rows

        self.cur.execute(f"""
        SELECT {tgt_col}, type, category 
        FROM bilingual 
        WHERE {col} = ? 
        ORDER BY 
            CASE 
                WHEN category = 'Common Usage' THEN 0 
                WHEN category = 'General' THEN 1 
                ELSE 2 
            END 
        LIMIT 5;
        """, (w_lower,))
        return self.cur.fetchall()

    def _conjugate_turkish_verb(self, verb_lemma: str, tense: str, person: str = "3s", is_negative: bool = False, can_modal: bool = False) -> str:
        """
        Full 4-way vowel harmony Turkish verb conjugator.
        Handles stems ending in vowels (drop vowel in -iyor), softening (git -> gidiyor),
        negation (-me/-ma/-miyor), modals (-ebilmek), and personal endings.
        """
        if not (verb_lemma.endswith("mek") or verb_lemma.endswith("mak")):
            return verb_lemma

        stem = verb_lemma[:-3]

        # Irregular stem softening
        if stem == "git":
            stem = "gid"
        elif stem == "et":
            stem = "ed"
        elif stem == "tat":
            stem = "tad"

        last_vowels = [c for c in stem if c in "aıoueiöü"]
        last_v = last_vowels[-1] if last_vowels else "e"
        is_back = is_back_vowel(last_v)

        # Modal 'can' (-ebilmek / -abilmek)
        if can_modal:
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

        # 3. Present Continuous / General (-iyor / -ıyor)
        else:
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
        Handles irregular verbs, -s / -es / -ies, and -ed / -ied.
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

    def translate(self, sentence: str, direction: str = "auto") -> Dict[str, Any]:
        sentence = sentence.strip()
        if not sentence:
            return {"translated_text": "", "breakdown": []}

        if direction == "auto":
            direction = self.detect_language(sentence)

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
                        res_clause = self._translate_en_to_tr(part.strip())
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

            return self._translate_en_to_tr(norm_sentence)
        else:
            return self._translate_tr_to_en(sentence)

    def _translate_en_to_tr(self, sentence: str) -> Dict[str, Any]:
        raw_tokens = re.findall(r"\b[\w'-]+\b|[.,!?;]", sentence)
        if not raw_tokens:
            return {"translated_text": "", "breakdown": []}

        breakdown = []
        i = 0
        n = len(raw_tokens)
        subject_person = "3s"
        has_future_modal = False
        has_can_modal = False
        is_negated = False
        copula_predicate = None

        while i < n:
            token = raw_tokens[i]
            t_lower = token.lower()

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
            elif t_lower in ["do", "does", "did"] and i + 1 < n and raw_tokens[i+1].lower() in ["not", "n't"]:
                is_negated = True
                i += 2
                continue
            elif t_lower in ["not", "never"]:
                is_negated = True
                i += 1
                continue

            # 5. Copula verbs (am, is, are, was, were)
            if t_lower in ["is", "am", "are"]:
                copula_predicate = "present"
                i += 1
                continue
            elif t_lower in ["was", "were"]:
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
            is_verb_context = (prev_role == "subject" or has_future_modal or has_can_modal or is_negated)

            lemma, v_tense = self._extract_english_verb_lemma(t_lower)
            if has_future_modal:
                v_tense = "future"

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
                    can_modal=has_can_modal
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

        # 14. SOV Clause Reordering: Connectors + Subject + Time + Adverbials + Objects + Verb
        connectors = [b for b in breakdown if b["role"] == "connector"]
        subjects = [b for b in breakdown if b["role"] == "subject"]
        times = [b for b in breakdown if b["role"] == "time"]
        adverbials = [b for b in breakdown if b["role"] == "adverbial"]
        objects = [b for b in breakdown if b["role"] in ["object", "determiner", "adjective"]]
        verbs = [b for b in breakdown if b["role"] == "verb"]
        puncts = [b for b in breakdown if b["role"] == "punct"]

        reordered = connectors + subjects + times + adverbials + objects + verbs
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

    def _translate_tr_to_en(self, sentence: str) -> Dict[str, Any]:
        """
        Turkish to English syntax translation with morphological parsing and SOV -> SVO reordering.
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

            # 1. Punctuation
            if token in ".,!?;":
                breakdown.append({"original": token, "translated": token, "role": "punct", "pos": "punct"})
                i += 1
                continue

            # 2. Conjunctions
            if t_lower in ["ve", "veya", "ama", "fakat", "çünkü", "eğer"]:
                tr_conj_map = {"ve": "and", "veya": "or", "ama": "but", "fakat": "but", "çünkü": "because", "eğer": "if"}
                breakdown.append({"original": token, "translated": tr_conj_map[t_lower], "role": "connector", "pos": "conj"})
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

            # 4. Pronouns
            if t_lower in ["ben", "sen", "o", "biz", "siz", "onlar"]:
                tr_pronoun_map = {
                    "ben": ("I", "1s"), "sen": ("you", "2s"), "o": ("he", "3s"),
                    "biz": ("we", "1p"), "siz": ("you", "2p"), "onlar": ("they", "3p")
                }
                en_p, p_code = tr_pronoun_map[t_lower]
                subject_person = p_code
                breakdown.append({"original": token, "translated": en_p, "role": "subject", "pos": "pronoun"})
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
            if t_lower in COMMON_PERSON_NAMES or (token[0].isupper() and i == 0):
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
                    if stem_cand in COMMON_TR_VERB_STEMS:
                        tr_infinitive = COMMON_TR_VERB_STEMS[stem_cand]
                        en_base = COMMON_VERBS_TR_EN.get(tr_infinitive, "work")

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
                    if stem_cand in COMMON_TR_VERB_STEMS:
                        tr_infinitive = COMMON_TR_VERB_STEMS[stem_cand]
                        en_base = COMMON_VERBS_TR_EN.get(tr_infinitive, "drink")
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
                    if stem_cand in COMMON_TR_VERB_STEMS:
                        tr_infinitive = COMMON_TR_VERB_STEMS[stem_cand]
                        en_base = COMMON_VERBS_TR_EN.get(tr_infinitive, "meet")
                        en_v = f"will {en_base}"

                        breakdown.append({"original": token, "translated": en_v, "role": "verb", "pos": "v."})
                        found_verb = True
                        break

            if found_verb:
                i += 1
                continue

            # 11. Common Nouns, Adjectives & General Dictionary Lookup
            if t_lower in COMMON_NOUNS_TR_EN:
                breakdown.append({"original": token, "translated": COMMON_NOUNS_TR_EN[t_lower], "role": "object", "pos": "n."})
            elif t_lower in COMMON_ADJECTIVES_TR_EN:
                breakdown.append({"original": token, "translated": COMMON_ADJECTIVES_TR_EN[t_lower], "role": "adjective", "pos": "adj."})
            else:
                matches = self._lookup_word(t_lower, is_en=False)
                if matches:
                    top_en = matches[0][0]
                    top_pos = matches[0][1]
                    role = "verb" if "v." in top_pos else "object"
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

        # 12. English SVO Clause Reordering: Connectors + Subject + Verb/Predicate + Objects + Adverbials + Time
        connectors = [b for b in breakdown if b["role"] == "connector"]
        subjects = [b for b in breakdown if b["role"] == "subject"]
        verbs = [b for b in breakdown if b["role"] == "verb"]
        copulas = [b for b in breakdown if b["role"] == "copula_predicate"]
        objects = [b for b in breakdown if b["role"] in ["object", "determiner", "adjective"]]
        adverbials = [b for b in breakdown if b["role"] in ["adverbial", "possessive"]]
        times = [b for b in breakdown if b["role"] == "time"]
        puncts = [b for b in breakdown if b["role"] == "punct"]

        if copulas:
            reordered = connectors + subjects + copulas + adverbials + times
        else:
            reordered = connectors + subjects + verbs + objects + adverbials + times

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
