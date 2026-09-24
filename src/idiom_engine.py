"""
Idiom & Proverb Engine (Deyimler ve Atasözleri Motoru)
Handles high-accuracy, natural translation of idioms, proverbs, and multi-word
expressions in both TR -> EN and EN -> TR.
"""

import re
from typing import Optional, Tuple, List, Dict, Any
from src.utils import turkish_lower

# Complete Sentence Proverbs & Fixed Sayings (Exact / Normalized Matching)
# Direction: TR -> EN
TR_PROVERBS_EXACT: Dict[str, str] = {
    "tatlı dil yılanı deliğinden çıkarır": "Gentle words open iron gates.",
    "damlaya damlaya göl olur": "Little drops make a mighty ocean.",
    "ayinesi iştir kişinin lafa bakılmaz": "Actions speak louder than words.",
    "erken kalkan yol alır": "The early bird catches the worm.",
    "ne ekersen onu biçersin": "You reap what you sow.",
    "geç olsun güç olmasın": "Better late than never.",
    "işleyen demir ışıldar": "Practice makes perfect.",
    "işleyen demir pas tutmaz": "A rolling stone gathers no moss.",
    "balık baştan kokar": "A fish rots from the head down.",
    "akıl akıldan üstündür": "Two heads are better than one.",
    "söz gümüşse sükut altındır": "Silence is golden.",
    "vakit nakittir": "Time is money.",
    "birlikten kuvvet doğar": "Unity is strength.",
    "nerede birlik orada dirlik": "Unity is strength.",
    "dost kara günde belli olur": "A friend in need is a friend indeed.",
    "çıkmadık candan ümit kesilmez": "Where there is life, there is hope.",
    "sütten ağzı yanan yoğurdu üfleyerek yer": "Once bitten, twice shy.",
    "sakla samanı gelir zamanı": "Keep a thing seven years and you will find a use for it.",
    "tencere yuvarlanmış kapağını bulmuş": "Birds of a feather flock together.",
    "sabır acıdır ama meyvesi tatlıdır": "Patience is bitter, but its fruit is sweet.",
    "yağmurdan kaçarken doluya tutulmak": "Out of the frying pan into the fire.",
    "zaman su gibi akıp geçiyor": "Time flies.",
    "zahmetsiz rahmet olmaz": "No pain, no gain.",
    "son pişmanlık fayda etmez": "There is no use crying over spilled milk.",
    "haydan gelen huya gider": "Easy come, easy go.",
    "her işte bir hayır vardır": "Every cloud has a silver lining.",
    "bekara karı boşamak kolay": "Talk is cheap.",
    "bin düşün bir söyle": "Look before you leap.",
    "bir elin nesi var iki elin sesi var": "Many hands make light work.",
    "komşunun tavuğu komşuya kaz görünür": "The grass is always greener on the other side.",
    "gülme komşuna gelir başına": "He who laughs last laughs best.",
    "et tırnaktan ayrılmaz": "Blood is thicker than water.",
    "başa gelen çekilir": "What can't be cured must be endured.",
    "iti an çomağı hazırla": "Speak of the devil.",
    "sen benim dengim değilsin": "You are not my equal.",
}

# Complete Sentence Proverbs & Fixed Sayings (Exact / Normalized Matching)
# Direction: EN -> TR
EN_PROVERBS_EXACT: Dict[str, str] = {
    "actions speak louder than words": "Ayinesi iştir kişinin lafa bakılmaz.",
    "better late than never": "Geç olsun güç olmasın.",
    "you reap what you sow": "Ne ekersen onu biçersin.",
    "time flies": "Zaman su gibi akıp geçiyor.",
    "no pain, no gain": "Zahmetsiz rahmet olmaz.",
    "no pain no gain": "Zahmetsiz rahmet olmaz.",
    "practice makes perfect": "İşleyen demir ışıldar.",
    "easy come, easy go": "Haydan gelen huya gider.",
    "easy come easy go": "Haydan gelen huya gider.",
    "every cloud has a silver lining": "Her şerde bir hayır vardır.",
    "the early bird catches the worm": "Erken kalkan yol alır.",
    "early bird catches the worm": "Erken kalkan yol alır.",
    "silence is golden": "Söz gümüşse sükut altındır.",
    "time is money": "Vakit nakittir.",
    "a friend in need is a friend indeed": "Dost kara günde belli olur.",
    "where there is life, there is hope": "Çıkmadık candan ümit kesilmez.",
    "where there's life, there's hope": "Çıkmadık candan ümit kesilmez.",
    "once bitten, twice shy": "Sütten ağzı yanan yoğurdu üfleyerek yer.",
    "once bitten twice shy": "Sütten ağzı yanan yoğurdu üfleyerek yer.",
    "unity is strength": "Birlikten kuvvet doğar.",
    "two heads are better than one": "Akıl akıldan üstündür.",
    "a fish rots from the head down": "Balık baştan kokar.",
    "look before you leap": "Bin düşün bir söyle.",
    "it takes two to tango": "Tek elle alkış tutulmaz.",
    "curiosity killed the cat": "Fazla merak başa bela getirir.",
    "birds of a feather flock together": "Tencere yuvarlanmış kapağını bulmuş.",
    "a blessing in disguise": "Her şerde bir hayır vardır.",
    "cry over spilled milk": "Son pişmanlık fayda etmez.",
    "crying over spilled milk": "Son pişmanlık fayda etmez.",
    "it's not rocket science": "Atla deve değil.",
    "it is not rocket science": "Atla deve değil.",
    "not rocket science": "Atla deve değil.",
    "break a leg": "Şeytanın bacağını kır, bol şans!",
    "bite the bullet": "Dişini sık.",
    "spill the beans": "Ağzındaki baklayı çıkar.",
    "call it a day": "Bugünlük bu kadar, paydos.",
    "let's call it a day": "Bugünlük bu kadar diyelim.",
    "hit the sack": "Kafayı vurup yatmak.",
    "out of the blue": "Damdan düşer gibi, ansızın.",
    "once in a blue moon": "Kırk yılda bir, ayda yılda bir.",
    "the last straw": "Bardağı taşıran son damla.",
    "last straw": "Bardağı taşıran son damla.",
    "costs an arm and a leg": "Ateş pahası.",
    "it costs an arm and a leg": "Ateş pahası.",
    "this costs an arm and a leg": "Ateş pahası.",
    "a piece of cake": "Çocuk oyuncağı.",
    "piece of cake": "Çocuk oyuncağı.",
}

# Inflected & Phrasal Idiom Patterns (TR -> EN)
# Format: (regex_pattern, translation)
TR_PHRASAL_PATTERNS = [
    # Bir taşla iki kuş vurmak
    (r"^\s*bir taşla iki kuş vur(duk|duk ki)\s*[.!?]?$", "We killed two birds with one stone."),
    (r"^\s*bir taşla iki kuş vur(dular)\s*[.!?]?$", "They killed two birds with one stone."),
    (r"^\s*bir taşla iki kuş vur(du)\s*[.!?]?$", "He killed two birds with one stone."),
    (r"^\s*bir taşla iki kuş vur(dum)\s*[.!?]?$", "I killed two birds with one stone."),
    (r"^\s*bir taşla iki kuş vur(uruz|acağız)\s*[.!?]?$", "We will kill two birds with one stone."),
    (r"\bbir taşla iki kuş vur(duk|duk ki)\b", "we killed two birds with one stone"),
    (r"\bbir taşla iki kuş vur(dular)\b", "they killed two birds with one stone"),
    (r"\bbir taşla iki kuş vur(du)\b", "he killed two birds with one stone"),
    (r"\bbir taşla iki kuş vur(dum)\b", "I killed two birds with one stone"),
    (r"\bbir taşla iki kuş vurmak\b", "to kill two birds with one stone"),

    # Can kulağıyla dinlemek
    (r"^\s*can kulağıyla dinle(diler)\s*[.!?]?$", "They listened with rapt attention."),
    (r"^\s*can kulağıyla dinle(dik)\s*[.!?]?$", "We listened with rapt attention."),
    (r"^\s*can kulağıyla dinle(di)\s*[.!?]?$", "He listened with rapt attention."),
    (r"^\s*can kulağıyla dinle(dim)\s*[.!?]?$", "I listened with rapt attention."),
    (r"^\s*can kulağıyla dinle(yin|yiniz)\s*[.!?]?$", "Listen with rapt attention."),
    (r"^\s*can kulağıyla dinle(rler|riz)\s*[.!?]?$", "They listen with rapt attention."),
    (r"\bcan kulağıyla dinle(diler)\b", "listened with rapt attention"),
    (r"\bcan kulağıyla dinlemek\b", "to listen with rapt attention"),

    # Gözden düşmek
    (r"^\s*gözden düşmek istemiyorum\s*[.!?]?$", "I do not want to fall from grace."),
    (r"^\s*gözden düşmek istemiyor\s*[.!?]?$", "He does not want to fall from grace."),
    (r"^\s*gözden düş(tü)\s*[.!?]?$", "He fell from grace."),
    (r"^\s*gözden düş(tüler)\s*[.!?]?$", "They fell from grace."),
    (r"^\s*gözden düş(tüm)\s*[.!?]?$", "I fell from grace."),
    (r"\bgözden düşmek istemiyorum\b", "I do not want to fall from grace"),
    (r"\bgözden düşmek\b", "to fall from grace"),

    # Kendimi keyifsiz hissetmek
    (r"^\s*kendimi (biraz )?keyifsiz hissediyorum\s*[.!?]?$", "I am feeling a bit under the weather."),
    (r"^\s*kendini (biraz )?keyifsiz hissediyor\s*[.!?]?$", "He is feeling a bit under the weather."),
    (r"\bkendimi (biraz )?keyifsiz hissediyorum\b", "I am feeling a bit under the weather"),

    # Ateş pahası
    (r"^\s*bu sınav çocuk oyuncağı\s*[.!?]?$", "This exam is a piece of cake."),
    (r"^\s*bu araba ateş pahası\s*[.!?]?$", "This car costs an arm and a leg."),
    (r"^\s*bu ev ateş pahası\s*[.!?]?$", "This house costs an arm and a leg."),
    (r"^\s*ateş pahası\s*[.!?]?$", "It costs an arm and a leg."),
    (r"\bateş pahası\b", "costs an arm and a leg"),

    # Çocuk oyuncağı / Çantada keklik
    (r"^\s*(çocuk oyuncağı|çantada keklik)\s*[.!?]?$", "A piece of cake."),
    (r"\b(çocuk oyuncağı|çantada keklik)\b", "a piece of cake"),

    # Dişini sıkmak
    (r"^\s*dişini sık(mak)?\s*[.!?]?$", "Bite the bullet."),
    (r"^\s*dişinizi sıkın\s*[.!?]?$", "Bite the bullet."),
    (r"\bdişini sık(mak)?\b", "bite the bullet"),

    # Şeytanın bacağını kırmak
    (r"^\s*şeytanın bacağını kır(mak)?\s*[.!?]?$", "Break a leg."),

    # Havlu atmak
    (r"^\s*havlu at(tı|tılar|tık|tım|mak)\s*[.!?]?$", "Threw in the towel."),
    (r"\bhavlu at(tı|tılar|tık|tım|mak)\b", "threw in the towel"),

    # Göz yummak
    (r"^\s*göz yum(du|dular|duk|dum|mak)\s*[.!?]?$", "Turned a blind eye."),
    (r"\bgöz yum(du|dular|duk|dum|mak)\b", "turned a blind eye"),

    # İki yakayı bir araya getirmek
    (r"^\s*iki yakayı bir araya getir(emiyor|emiyoruz|emedi)\s*[.!?]?$", "Cannot make ends meet."),
    (r"^\s*iki yakayı bir araya getirmek\s*[.!?]?$", "To make ends meet."),
    (r"\biki yakayı bir araya getir(emiyor|emedi)\b", "cannot make ends meet"),

    # Bardağı taşıran son damla
    (r"^\s*bardağı taşıran son damla\s*[.!?]?$", "The last straw."),
    (r"\bbardağı taşıran son damla\b", "the last straw"),

    # Etekleri zil çalmak
    (r"^\s*etekleri zil çal(ıyor|dı)\s*[.!?]?$", "Is on cloud nine."),

    # Damdan düşer gibi
    (r"^\s*damdan düşer gibi\s*[.!?]?$", "Out of the blue."),
    (r"\bdamdan düşer gibi\b", "out of the blue"),

    # Ayda yılda bir
    (r"^\s*ayda yılda bir\s*[.!?]?$", "Once in a blue moon."),
    (r"\bayda yılda bir\b", "once in a blue moon"),
]

# Inflected & Phrasal Idiom Patterns (EN -> TR)
EN_PHRASAL_PATTERNS = [
    # A piece of cake
    (r"^\s*(this\s+exam|the\s+exam)\s+is\s+(a\s+)?piece of cake\s*[.!?]?$", "Bu sınav çocuk oyuncağı."),
    (r"^\s*this\s+is\s+(a\s+)?piece of cake\s*[.!?]?$", "Bu çocuk oyuncağı."),
    (r"^\s*(it's|it\s+is)\s+(a\s+)?piece of cake\s*[.!?]?$", "Çocuk oyuncağı."),
    (r"^\s*(a\s+)?piece of cake\s*[.!?]?$", "Çocuk oyuncağı."),
    (r"\b(a\s+)?piece of cake\b", "çocuk oyuncağı"),

    # Under the weather
    (r"^\s*(i\s+am|i'm)\s+feeling\s+under the weather\s*[.!?]?$", "Kendimi biraz keyifsiz hissediyorum."),
    (r"^\s*(i\s+feel)\s+under the weather\s*[.!?]?$", "Kendimi keyifsiz hissediyorum."),
    (r"^\s*(he\s+is|he's|she\s+is|she's)\s+feeling\s+under the weather\s*[.!?]?$", "Kendini biraz keyifsiz hissediyor."),
    (r"\bfeeling\s+under the weather\b", "kendini keyifsiz hissetmek"),
    (r"\bunder the weather\b", "keyifsiz"),

    # Costs an arm and a leg
    (r"^\s*(this\s+car|the\s+car)\s+costs?\s+an\s+arm\s+and\s+a\s+leg\s*[.!?]?$", "Bu araba ateş pahası."),
    (r"^\s*(this\s+house|the\s+house)\s+costs?\s+an\s+arm\s+and\s+a\s+leg\s*[.!?]?$", "Bu ev ateş pahası."),
    (r"^\s*(it\s+)?costs?\s+an\s+arm\s+and\s+a\s+leg\s*[.!?]?$", "Ateş pahası."),
    (r"\bcosts?\s+an\s+arm\s+and\s+a\s+leg\b", "ateş pahası"),

    # Killed two birds with one stone
    (r"^\s*(we\s+)?killed\s+two birds with one stone\s*[.!?]?$", "Bir taşla iki kuş vurduk."),
    (r"^\s*(they\s+)?killed\s+two birds with one stone\s*[.!?]?$", "Bir taşla iki kuş vurdular."),
    (r"^\s*(he\s+|she\s+)?killed\s+two birds with one stone\s*[.!?]?$", "Bir taşla iki kuş vurdu."),
    (r"^\s*(i\s+)?killed\s+two birds with one stone\s*[.!?]?$", "Bir taşla iki kuş vurdum."),
    (r"^\s*kill\s+two birds with one stone\s*[.!?]?$", "Bir taşla iki kuş vurmak."),
    (r"\bkilled\s+two birds with one stone\b", "bir taşla iki kuş vurdu"),
    (r"\bkill\s+two birds with one stone\b", "bir taşla iki kuş vurmak"),

    # Bite the bullet
    (r"^\s*bite\s+the\s+bullet\s*[.!?]?$", "Dişini sık."),
    (r"\bbite\s+the\s+bullet\b", "dişini sıkmak"),

    # Spill the beans
    (r"^\s*spill\s+the\s+beans\s*[.!?]?$", "Ağzındaki baklayı çıkar."),
    (r"\bspill\s+the\s+beans\b", "ağzındaki baklayı çıkarmak"),

    # Call it a day
    (r"^\s*call\s+it\s+a\s+day\s*[.!?]?$", "Paydos etmek."),
    (r"\bcall\s+it\s+a\s+day\b", "paydos etmek"),

    # Out of the blue
    (r"^\s*out\s+of\s+the\s+blue\s*[.!?]?$", "Damdan düşer gibi."),
    (r"\bout\s+of\s+the\s+blue\b", "damdan düşer gibi"),

    # Once in a blue moon
    (r"^\s*once\s+in\s+a\s+blue\s+moon\s*[.!?]?$", "Ayda yılda bir."),
    (r"\bonce\s+in\s+a\s+blue\s+moon\b", "ayda yılda bir"),

    # The last straw
    (r"^\s*(the\s+)?last\s+straw\s*[.!?]?$", "Bardağı taşıran son damla."),
    (r"\b(the\s+)?last\s+straw\b", "bardağı taşıran son damla"),

    # Through thick and thin
    (r"^\s*through\s+thick\s+and\s+thin\s*[.!?]?$", "İyi günde kötü günde."),
    (r"\bthrough\s+thick\s+and\s+thin\b", "iyi günde kötü günde"),

    # Turn a blind eye
    (r"^\s*turned?\s+a\s+blind\s+eye\s*[.!?]?$", "Göz yumdu."),
    (r"\bturned?\s+a\s+blind\s+eye\b", "göz yummak"),

    # Make ends meet
    (r"^\s*make\s+ends\s+meet\s*[.!?]?$", "İki yakayı bir araya getirmek."),
    (r"\bmake\s+ends\s+meet\b", "iki yakayı bir araya getirmek"),

    # Hit the nail on the head
    (r"^\s*hit\s+the\s+nail\s+on\s+the\s+head\s*[.!?]?$", "Taşı gediğine koymak."),
    (r"\bhit\s+the\s+nail\s+on\s+the\s+head\b", "taşı gediğine koymak"),
]

def clean_sentence_for_matching(text: str) -> str:
    """Removes trailing and leading punctuation and normalizes spaces."""
    cleaned = re.sub(r"[^\w\s']", " ", text)
    return " ".join(cleaned.split())

def match_idiom(
    text: str, 
    from_code: str, 
    to_code: str
) -> Optional[Tuple[str, List[Dict[str, Any]], str, int]]:
    """
    Checks if a sentence or clause matches a proverb, idiom, or idiomatic phrase.
    Returns: (translated_text, breakdown, engine_label, confidence) or None.
    """
    text_stripped = text.strip()
    if not text_stripped:
        return None

    punct = text_stripped[-1] if text_stripped[-1] in ".!?" else "."

    # 1. Exact Proverb / Idiom Full Sentence Matching
    if from_code == "tr":
        norm_tr = turkish_lower(clean_sentence_for_matching(text_stripped))
        if norm_tr in TR_PROVERBS_EXACT:
            target = TR_PROVERBS_EXACT[norm_tr]
            final_out = target.rstrip(".!?") + punct
            bd = [{"original": text_stripped, "translated": final_out, "role": "proverb", "pos": "idiom"}]
            return final_out, bd, "idiom_exact", 98
    else:
        norm_en = clean_sentence_for_matching(text_stripped).lower()
        if norm_en in EN_PROVERBS_EXACT:
            target = EN_PROVERBS_EXACT[norm_en]
            final_out = target.rstrip(".!?") + punct
            bd = [{"original": text_stripped, "translated": final_out, "role": "proverb", "pos": "idiom"}]
            return final_out, bd, "idiom_exact", 98

    # 2. Phrasal / Inflected Idiom Pattern Matching
    if from_code == "tr":
        for pattern, replacement in TR_PHRASAL_PATTERNS:
            if re.search(pattern, text_stripped, flags=re.IGNORECASE):
                words = text_stripped.split()
                if len(words) <= 10:
                    if pattern.startswith("^"):
                        final_out = replacement.rstrip(".!?") + punct
                    else:
                        subbed = re.sub(pattern, replacement, text_stripped, flags=re.IGNORECASE).strip()
                        subbed = subbed[0].upper() + subbed[1:] if subbed else subbed
                        final_out = subbed.rstrip(".!?") + punct
                    bd = [{"original": text_stripped, "translated": final_out, "role": "idiom_phrase", "pos": "idiom"}]
                    return final_out, bd, "idiom_phrase", 95
    else:
        for pattern, replacement in EN_PHRASAL_PATTERNS:
            if re.search(pattern, text_stripped, flags=re.IGNORECASE):
                words = text_stripped.split()
                if len(words) <= 10:
                    if pattern.startswith("^"):
                        final_out = replacement.rstrip(".!?") + punct
                    else:
                        subbed = re.sub(pattern, replacement, text_stripped, flags=re.IGNORECASE).strip()
                        subbed = subbed[0].upper() + subbed[1:] if subbed else subbed
                        final_out = subbed.rstrip(".!?") + punct
                    bd = [{"original": text_stripped, "translated": final_out, "role": "idiom_phrase", "pos": "idiom"}]
                    return final_out, bd, "idiom_phrase", 95

    return None
