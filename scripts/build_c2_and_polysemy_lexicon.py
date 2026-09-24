"""
Radical C1/C2 & Polysemy Vocabulary Enrichment Pipeline
Downloads CEFR-J C1/C2 profiles, builds comprehensive multi-sense definitions,
and enriches both English and Turkish vocabulary in data/dictionary.db.
"""

import os
import sys
import csv
import urllib.request
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from src.utils import turkish_lower

DB_PATH = os.path.join(base_dir, "data", "dictionary.db")

# 1. Advanced Literary, Intellectual & Academic Turkish Vocabulary with Multiple English Senses
ADVANCED_TURKISH_C2_LEXICON = [
    ("mütekabiliyet", [("reciprocity", "n.", "Primary"), ("mutual reciprocity", "n.", "Law"), ("interchangeability", "n.", "General"), ("counterbalance", "n.", "Diplomacy")]),
    ("muhatap", [("addressee", "n.", "Primary"), ("counterpart", "n.", "Diplomacy"), ("interlocutor", "n.", "Formal"), ("contact person", "n.", "General"), ("the person addressed", "n.", "Common Usage")]),
    ("özveri", [("self-sacrifice", "n.", "Primary"), ("devotion", "n.", "Common Usage"), ("dedication", "n.", "Common Usage"), ("altruism", "n.", "Formal")]),
    ("itidal", [("moderation", "n.", "Primary"), ("composure", "n.", "Common Usage"), ("equanimity", "n.", "Formal"), ("temperance", "n.", "Formal"), ("calmness", "n.", "General")]),
    ("aykırı", [("contrary", "adj.", "Primary"), ("nonconformist", "adj.", "Common Usage"), ("unorthodox", "adj.", "Formal"), ("incompatible", "adj.", "Common Usage"), ("maverick", "adj.", "Informal"), ("aberrant", "adj.", "Academic")]),
    ("basiret", [("foresight", "n.", "Primary"), ("discernment", "n.", "Formal"), ("prudence", "n.", "Formal"), ("insight", "n.", "Common Usage"), ("perspicacity", "n.", "Academic")]),
    ("feraset", [("acumen", "n.", "Primary"), ("sagacity", "n.", "Formal"), ("keen insight", "n.", "Common Usage"), ("shrewdness", "n.", "Common Usage"), ("penetration", "n.", "Formal")]),
    ("münferit", [("isolated", "adj.", "Primary"), ("individual", "adj.", "Common Usage"), ("sporadic", "adj.", "Formal"), ("single", "adj.", "General"), ("discrete", "adj.", "Academic")]),
    ("zaruri", [("essential", "adj.", "Primary"), ("imperative", "adj.", "Common Usage"), ("indispensable", "adj.", "Common Usage"), ("mandatory", "adj.", "Formal"), ("obligatory", "adj.", "Formal")]),
    ("mütereddit", [("hesitant", "adj.", "Primary"), ("undecided", "adj.", "Common Usage"), ("wavering", "adj.", "Common Usage"), ("vacillating", "adj.", "Formal"), ("reluctant", "adj.", "General")]),
    ("kifayetsiz", [("inadequate", "adj.", "Primary"), ("incompetent", "adj.", "Common Usage"), ("insufficient", "adj.", "Common Usage"), ("inept", "adj.", "Formal")]),
    ("müstehcen", [("obscene", "adj.", "Primary"), ("indecent", "adj.", "Common Usage"), ("lewd", "adj.", "Formal"), ("salacious", "adj.", "Formal"), ("vulgar", "adj.", "General")]),
    ("tahakküm", [("domination", "n.", "Primary"), ("hegemony", "n.", "Academic"), ("tyranny", "n.", "Formal"), ("oppression", "n.", "Common Usage"), ("coercion", "n.", "Formal")]),
    ("nüfuz", [("influence", "n.", "Primary"), ("leverage", "n.", "Common Usage"), ("penetration", "n.", "Formal"), ("prestige", "n.", "General"), ("clout", "n.", "Informal")]),
    ("münhasır", [("exclusive", "adj.", "Primary"), ("restricted", "adj.", "Common Usage"), ("sole", "adj.", "Formal"), ("confined to", "adj.", "Law")]),
    ("veciz", [("concise", "adj.", "Primary"), ("pithy", "adj.", "Formal"), ("laconic", "adj.", "Formal"), ("succinct", "adj.", "Common Usage"), ("terse", "adj.", "Academic")]),
    ("mücbir", [("compelling", "adj.", "Primary"), ("coercive", "adj.", "Formal"), ("force majeure", "n.", "Law"), ("unavoidable", "adj.", "Common Usage")]),
    ("ahde vefa", [("pacta sunt servanda", "n.", "Law"), ("fidelity to agreements", "n.", "Formal"), ("keeping one's promise", "n.", "Primary"), ("sanctity of contract", "n.", "Law")]),
    ("tenakuz", [("contradiction", "n.", "Primary"), ("inconsistency", "n.", "Common Usage"), ("paradox", "n.", "Formal"), ("discrepancy", "n.", "Formal")]),
    ("teveccüh", [("favor", "n.", "Primary"), ("goodwill", "n.", "Common Usage"), ("kind attention", "n.", "Formal"), ("affection", "n.", "General")]),
    ("mukavemet", [("resistance", "n.", "Primary"), ("endurance", "n.", "Common Usage"), ("stamina", "n.", "Common Usage"), ("strength of materials", "n.", "Technical")]),
    ("mülahaza", [("deliberation", "n.", "Primary"), ("reflection", "n.", "Common Usage"), ("consideration", "n.", "Formal"), ("thought", "n.", "General")]),
    ("ihtiyat", [("caution", "n.", "Primary"), ("precaution", "n.", "Common Usage"), ("prudence", "n.", "Formal"), ("circumspection", "n.", "Academic")]),
    ("müşkülpesent", [("fastidious", "adj.", "Primary"), ("meticulous", "adj.", "Common Usage"), ("particular", "adj.", "Common Usage"), ("fussy", "adj.", "Informal"), ("exacting", "adj.", "Formal")]),
    ("münazara", [("debate", "n.", "Primary"), ("disputation", "n.", "Formal"), ("polemic", "n.", "Academic"), ("argumentation", "n.", "Formal")]),
    ("münasebet", [("relation", "n.", "Primary"), ("relationship", "n.", "Common Usage"), ("connection", "n.", "Common Usage"), ("relevance", "n.", "Formal"), ("occasion", "n.", "General")]),
    ("müteşekkir", [("grateful", "adj.", "Primary"), ("thankful", "adj.", "Common Usage"), ("obliged", "adj.", "Formal"), ("appreciative", "adj.", "Formal")]),
    ("müeyyide", [("sanction", "n.", "Primary"), ("penalty", "n.", "Common Usage"), ("legal consequence", "n.", "Law"), ("enforcement", "n.", "Formal")]),
    ("metanet", [("fortitude", "n.", "Primary"), ("resilience", "n.", "Common Usage"), ("steadfastness", "n.", "Formal"), ("endurance", "n.", "Common Usage"), ("grit", "n.", "Informal")]),
    ("vahamet", [("gravity", "n.", "Primary"), ("severity", "n.", "Common Usage"), ("criticality", "n.", "Formal"), ("perilous state", "n.", "Formal")]),
    ("zımni", [("implicit", "adj.", "Primary"), ("tacit", "adj.", "Formal"), ("unspoken", "adj.", "Common Usage"), ("implied", "adj.", "Law")]),
    ("tahayyül", [("imagination", "n.", "Primary"), ("visualization", "n.", "Common Usage"), ("envisaging", "n.", "Formal"), ("fantasizing", "n.", "General")]),
    ("tekabül", [("correspondence", "n.", "Primary"), ("equivalence", "n.", "Common Usage"), ("matching", "n.", "General"), ("counterpart", "n.", "Formal")]),
    ("tevazu", [("humility", "n.", "Primary"), ("modesty", "n.", "Common Usage"), ("unpretentiousness", "n.", "Formal"), ("humbleness", "n.", "General")]),
    ("hicap", [("shame", "n.", "Primary"), ("embarrassment", "n.", "Common Usage"), ("modesty", "n.", "Formal"), ("bashfulness", "n.", "General"), ("veil", "n.", "Archaic")]),
    ("kadirşinas", [("appreciative", "adj.", "Primary"), ("grateful", "adj.", "Common Usage"), ("value-acknowledging", "adj.", "Formal"), ("recognizing merit", "adj.", "Formal")]),
    ("mürebbiye", [("governess", "n.", "Primary"), ("tutor", "n.", "Common Usage"), ("educator", "n.", "Formal")]),
    ("müsamaha", [("tolerance", "n.", "Primary"), ("leniency", "n.", "Common Usage"), ("forbearance", "n.", "Formal"), ("indulgence", "n.", "General")]),
    ("içtihat", [("jurisprudence", "n.", "Primary"), ("judicial precedent", "n.", "Law"), ("case law", "n.", "Law"), ("interpretation", "n.", "Formal")]),
    ("tefrişat", [("furnishing", "n.", "Primary"), ("interior fittings", "n.", "Common Usage"), ("decor", "n.", "General"), ("furniture", "n.", "General")]),
    ("hükümranlık", [("sovereignty", "n.", "Primary"), ("reign", "n.", "Common Usage"), ("dominion", "n.", "Formal"), ("supremacy", "n.", "Political")]),
    ("riyakar", [("hypocrite", "n.", "Primary"), ("hypocritical", "adj.", "Primary"), ("two-faced", "adj.", "Common Usage"), ("disingenuous", "adj.", "Formal"), ("sanctimonious", "adj.", "Formal")]),
    ("iltimas", [("favoritism", "n.", "Primary"), ("nepotism", "n.", "Common Usage"), ("cronyism", "n.", "Formal"), ("preferential treatment", "n.", "Formal")]),
    ("müphem", [("vague", "adj.", "Primary"), ("ambiguous", "adj.", "Common Usage"), ("obscure", "adj.", "Formal"), ("equivocal", "adj.", "Academic"), ("indefinite", "adj.", "General")]),
    ("müspet", [("positive", "adj.", "Primary"), ("constructive", "adj.", "Common Usage"), ("affirmative", "adj.", "Formal"), ("empirical", "adj.", "Academic")]),
    ("menfi", [("negative", "adj.", "Primary"), ("adverse", "adj.", "Common Usage"), ("detrimental", "adj.", "Formal"), ("unfavorable", "adj.", "General")]),
]

# 2. English C1/C2 Advanced Vocabulary with Rich Multi-Sense Definitions
ADVANCED_ENGLISH_C2_LEXICON = [
    ("maverick", [("bağımsız düşünen kimse", "n.", "Primary"), ("başına buyruk kişi", "n.", "Common Usage"), ("sürüye uymayan kimse", "n.", "Common Usage"), ("aykırı tip", "n.", "Informal"), ("gelenek dışı", "adj.", "Formal"), ("bağımsız", "adj.", "Common Usage")]),
    ("serendipity", [("mutlu tesadüf", "n.", "Primary"), ("beklenmedik şans eseri keşif", "n.", "Common Usage"), ("hoş sürpriz", "n.", "General"), ("tevafuk", "n.", "Formal")]),
    ("obfuscate", [("muğlaklaştırmak", "v.", "Primary"), ("kafasını karıştırmak", "v.", "Common Usage"), ("anlaşılmaz kılmak", "v.", "Common Usage"), ("örtbas etmek", "v.", "Formal"), ("perdelemek", "v.", "Formal")]),
    ("quintessential", [("en tipik örneği olan", "adj.", "Primary"), ("özünü yansıtan", "adj.", "Common Usage"), ("mükemmel bir örneği olan", "adj.", "Common Usage"), ("has", "adj.", "General"), ("katıksız", "adj.", "General")]),
    ("recalcitrant", [("dik başlı", "adj.", "Primary"), ("inatçı", "adj.", "Common Usage"), ("laf dinlemez", "adj.", "Common Usage"), ("söz dinlemez", "adj.", "Formal"), ("asi", "adj.", "Formal")]),
    ("quandary", [("ikilem", "n.", "Primary"), ("çıkmaz", "n.", "Common Usage"), ("müşkül durum", "n.", "Formal"), ("tereddüt", "n.", "General"), ("bocalama", "n.", "General")]),
    ("clandestine", [("gizli kapaklı", "adj.", "Primary"), ("yasa dışı gizli", "adj.", "Common Usage"), ("gizli", "adj.", "Common Usage"), ("örtülü", "adj.", "Formal")]),
    ("esoteric", [("yalnızca uzmanlarınca anlaşılan", "adj.", "Primary"), ("ezoterik", "adj.", "Formal"), ("içe dönük", "adj.", "Formal"), ("gizli", "adj.", "General")]),
    ("fastidious", [("titiz", "adj.", "Primary"), ("müşkülpesent", "adj.", "Formal"), ("zor beğenen", "adj.", "Common Usage"), ("kılı kırk yaran", "adj.", "Common Usage")]),
    ("garrulous", [("geveze", "adj.", "Primary"), ("lafazan", "adj.", "Common Usage"), ("çok konuşan", "adj.", "General"), ("çenesi düşük", "adj.", "Informal")]),
    ("harangue", [("nutuk çekmek", "v.", "Primary"), ("ateşli konuşma yapmak", "v.", "Common Usage"), ("azarlamak", "v.", "Common Usage"), ("uzun ve sıkıcı nutuk", "n.", "Formal")]),
    ("idiosyncrasy", [("kendine has özellik", "n.", "Primary"), ("kişisel tuhaflık", "n.", "Common Usage"), ("mizaç özelliği", "n.", "Formal"), ("özgün huy", "n.", "General")]),
    ("juxtaposition", [("yan yana koyma", "n.", "Primary"), ("karşıtlık yaratmak için yan yana getirme", "n.", "Formal"), ("kıyaslama", "n.", "Academic")]),
    ("laconic", [("az ve öz", "adj.", "Primary"), ("kısa ve özlü", "adj.", "Common Usage"), ("veciz", "adj.", "Formal"), ("lakonik", "adj.", "Academic")]),
    ("nefarious", [("alçakça", "adj.", "Primary"), ("haince", "adj.", "Common Usage"), ("kötü niyetli", "adj.", "Common Usage"), ("şer dolu", "adj.", "Formal"), ("rezil", "adj.", "General")]),
    ("ostentatious", [("gösterişli", "adj.", "Primary"), ("havalı", "adj.", "Common Usage"), ("göze çarpmak isteyen", "adj.", "Common Usage"), ("şaşaalı", "adj.", "Formal")]),
    ("paradoxical", [("çelişkili gibi görünen", "adj.", "Primary"), ("paradoksal", "adj.", "Common Usage"), ("mantığa aykırı görünen", "adj.", "Formal")]),
    ("pernicious", [("sinsi bir şekilde zararlı", "adj.", "Primary"), ("yıkıcı", "adj.", "Common Usage"), ("öldürücü", "adj.", "Formal"), ("kötücül", "adj.", "Formal")]),
    ("ubiquitous", [("her yerde var olan", "adj.", "Primary"), ("yaygın", "adj.", "Common Usage"), ("her an karşılaşılan", "adj.", "Common Usage"), ("hazır ve nazır", "adj.", "Formal")]),
    ("ephemeral", [("kısa ömürlü", "adj.", "Primary"), ("geçici", "adj.", "Common Usage"), ("fani", "adj.", "Formal"), ("günübirlik", "adj.", "General")]),
    ("anachronism", [("çağ aşımı", "n.", "Primary"), ("zamanlama hatası", "n.", "Common Usage"), ("tarihsel uyumsuzluk", "n.", "Formal")]),
    ("antipathy", [("derin hoşnutsuzluk", "n.", "Primary"), ("antipati", "n.", "Common Usage"), ("nefret", "n.", "Common Usage"), ("itici bulma", "n.", "General")]),
    ("cacophony", [("kulak tırmalayıcı ses", "n.", "Primary"), ("kakofoni", "n.", "Common Usage"), ("ses kargaşası", "n.", "Formal"), ("uyumsuz sesler", "n.", "General")]),
    ("capricious", [("maymun iştahlı", "adj.", "Primary"), ("kaprisli", "adj.", "Common Usage"), ("değişken", "adj.", "Common Usage"), ("öngörülemez", "adj.", "Formal")]),
    ("dichotomy", [("ikilik", "n.", "Primary"), ("dikotomi", "n.", "Common Usage"), ("iki zıt gruba bölünme", "n.", "Formal"), ("çatallanma", "n.", "Academic")]),
    ("disparate", [("tamamen farklı", "adj.", "Primary"), ("birbiriyle bağdaşmayan", "adj.", "Common Usage"), ("ayrık", "adj.", "Academic")]),
    ("eloquent", [("hitabeti güçlü", "adj.", "Primary"), ("belagatli", "adj.", "Formal"), ("etkili konuşan", "adj.", "Common Usage"), ("anlamlı", "adj.", "General")]),
    ("equivocal", [("iki anlamlı", "adj.", "Primary"), ("muğlak", "adj.", "Common Usage"), ("şüpheli", "adj.", "Formal"), ("üstü kapalı", "adj.", "General")]),
    ("exacerbate", [("kötüleştirmek", "v.", "Primary"), ("şiddetlendirmek", "v.", "Common Usage"), ("durumu daha da vahimleştirmek", "v.", "Formal"), ("tırmandırmak", "v.", "General")]),
    ("gregarious", [("sosyal", "adj.", "Primary"), ("insancıl", "adj.", "Common Usage"), ("topluluk içinde yaşamayı seven", "adj.", "Formal"), ("sürü halinde yaşayan", "adj.", "Science")]),
    ("iconoclast", [("gelenek yıkan kimse", "n.", "Primary"), ("putkırıcı", "n.", "Formal"), ("yerleşik inançlara karşı çıkan", "n.", "Formal")]),
    ("ineffable", [("kelimelerle anlatılamaz", "adj.", "Primary"), ("tarif edilemez", "adj.", "Common Usage"), ("sözlere sığmaz", "adj.", "Formal")]),
    ("insidious", [("sinsi", "adj.", "Primary"), ("gizlice ilerleyen tehlike", "adj.", "Common Usage"), ("hilekar", "adj.", "Formal")]),
    ("magnanimous", [("alicenap", "adj.", "Primary"), ("yüce gönüllü", "adj.", "Common Usage"), ("bağışlayıcı", "adj.", "Common Usage"), ("cömert", "adj.", "General")]),
    ("mitigate", [("hafifletmek", "v.", "Primary"), ("azaltmak", "v.", "Common Usage"), ("yatıştırmak", "v.", "Common Usage"), ("etkisini kırmak", "v.", "Formal")]),
    ("panacea", [("her derde deva", "n.", "Primary"), ("tüm sorunların çözümü", "n.", "Common Usage"), ("mucizevi ilaç", "n.", "General")]),
    ("pragmatic", [("pragmatik", "adj.", "Primary"), ("uygulamacı", "adj.", "Common Usage"), ("faydacı", "adj.", "Common Usage"), ("pratik sonuç odaklı", "adj.", "Formal")]),
    ("prolific", [("üretken", "adj.", "Primary"), ("verimli", "adj.", "Common Usage"), ("bol eser veren", "adj.", "Common Usage"), ("bereketli", "adj.", "General")]),
    ("rhetoric", [("hitabet sanatı", "n.", "Primary"), ("retorik", "n.", "Common Usage"), ("süslü laf", "n.", "Informal"), ("etkileyici söz söyleme", "n.", "Formal")]),
    ("synergy", [("sinerji", "n.", "Primary"), ("birlikte çalışma gücü", "n.", "Common Usage"), ("ortak etki", "n.", "Formal")]),
    ("taciturn", [("az konuşan", "adj.", "Primary"), ("ağzı sıkı", "adj.", "Common Usage"), ("ketum", "adj.", "Formal"), ("sessiz", "adj.", "General")]),
    ("tenacious", [("azimli", "adj.", "Primary"), ("pes etmeyen", "adj.", "Common Usage"), ("sıkı sıkıya sarılan", "adj.", "Common Usage"), ("vazgeçmeyen", "adj.", "Formal")]),
    ("venerable", [("saygıdeğer", "adj.", "Primary"), ("muhterem", "adj.", "Formal"), ("hürmete layık", "adj.", "Common Usage"), ("kadim", "adj.", "Literary")]),
    ("vicarious", [("başkası üzerinden yaşanan", "adj.", "Primary"), ("vekaleten", "adj.", "Formal"), ("dolaylı olarak hissedilen", "adj.", "Common Usage")]),
    ("zealous", [("şevkli", "adj.", "Primary"), ("coşkulu", "adj.", "Common Usage"), ("gayretli", "adj.", "Common Usage"), ("tavizsiz taraftar", "adj.", "Formal")]),
]

# 3. High-Polysemy Words (Kelimelerin Onlarca Gerçek Anlamı)
POLYSEMOUS_WORDS = [
    ("run", [
        ("koşmak", "v.", "Primary"),
        ("çalıştırmak (motor/sistem)", "v.", "Common Usage"),
        ("işletmek (şirket/dükkan)", "v.", "Common Usage"),
        ("yönetmek", "v.", "Common Usage"),
        ("akmak (su/zaman)", "v.", "General"),
        ("aday olmak (seçimde)", "v.", "Politics"),
        ("devam etmek (süre)", "v.", "General"),
        ("koşu", "n.", "Primary"),
        ("tur", "n.", "General"),
        ("akış", "n.", "General"),
        ("sefer (otobüs/tren)", "n.", "General"),
        ("silsile / dizi", "n.", "General"),
        ("kaçmak (çorap)", "v.", "General"),
        ("karşılaşmak (run into)", "v.", "Idiom"),
        ("tükenmek (run out of)", "v.", "Idiom")
    ]),
    ("set", [
        ("kurmak", "v.", "Primary"),
        ("ayarlamak", "v.", "Common Usage"),
        ("belirlemek", "v.", "Common Usage"),
        ("koymak / yerleştirmek", "v.", "Common Usage"),
        ("batmak (güneş)", "v.", "General"),
        ("hazırlamak (sofra)", "v.", "General"),
        ("takım / küme", "n.", "Primary"),
        ("set (film/sahne)", "n.", "Common Usage"),
        ("belirlenmiş / sabit", "adj.", "Common Usage"),
        ("hazır (all set)", "adj.", "Informal"),
        ("yola çıkmak (set off)", "v.", "Idiom"),
        ("başlamak (set out)", "v.", "Idiom"),
        ("oluşturmak / kurmak (set up)", "v.", "Idiom")
    ]),
    ("turn", [
        ("dönmek", "v.", "Primary"),
        ("döndürmek / çevirmek", "v.", "Primary"),
        ("sapmak (köşeyi)", "v.", "Common Usage"),
        ("dönüşmek (turn into)", "v.", "Common Usage"),
        ("ekşimek (süt)", "v.", "General"),
        ("sıra", "n.", "Primary"),
        ("dönüş / viraj", "n.", "Common Usage"),
        ("nöbet", "n.", "General"),
        ("reddetmek (turn down)", "v.", "Idiom"),
        ("açmak (turn on)", "v.", "Idiom"),
        ("kapatmak (turn off)", "v.", "Idiom"),
        ("ortaya çıkmak (turn out)", "v.", "Idiom"),
        ("teslim etmek (turn in)", "v.", "Idiom"),
        ("başvurmak (turn to)", "v.", "Idiom")
    ]),
    ("bear", [
        ("dayanmak / katlanmak", "v.", "Primary"),
        ("taşımak", "v.", "Common Usage"),
        ("ayı", "n.", "Primary"),
        ("ürün vermek (meyve)", "v.", "General"),
        ("doğurmak", "v.", "Formal"),
        ("beslemek (duygu/kin)", "v.", "Formal"),
        ("akılda tutmak (bear in mind)", "v.", "Idiom"),
        ("tanıklık etmek (bear witness)", "v.", "Formal"),
        ("sonuç vermek (bear fruit)", "v.", "Idiom"),
        ("tahammül etmek", "v.", "Common Usage")
    ]),
    ("fair", [
        ("adil / dürüst", "adj.", "Primary"),
        ("makul / hakkaniyetli", "adj.", "Common Usage"),
        ("açık tenli / sarışın", "adj.", "Common Usage"),
        ("güzel / açık (hava)", "adj.", "General"),
        ("orta / fena değil (fair condition)", "adj.", "General"),
        ("fuar", "n.", "Primary"),
        ("panayır", "n.", "Common Usage"),
        ("kermes", "n.", "General"),
        ("dürüstçe", "adv.", "General"),
        ("hakça", "adv.", "General")
    ]),
    ("matter", [
        ("önemli olmak", "v.", "Primary"),
        ("fark etmek", "v.", "Common Usage"),
        ("madde / cisim", "n.", "Primary"),
        ("konu / mesele", "n.", "Primary"),
        ("sorun / problem", "n.", "Common Usage"),
        ("iltihap / cerahat", "n.", "Medical"),
        ("aslında (as a matter of fact)", "adv.", "Idiom"),
        ("ne olursa olsun (no matter what)", "conj.", "Idiom"),
        ("zaman meselesi (matter of time)", "n.", "Idiom")
    ]),
    ("charge", [
        ("şarj etmek", "v.", "Primary"),
        ("ücret talep etmek", "v.", "Primary"),
        ("suçlamak", "v.", "Law"),
        ("saldırmak / hücum etmek", "v.", "General"),
        ("görevlendirmek", "v.", "Formal"),
        ("ücret / masraf", "n.", "Primary"),
        ("suçlama / itham", "n.", "Law"),
        ("elektrik yükü", "n.", "Science"),
        ("sorumluluk (in charge of)", "n.", "Idiom"),
        ("hücum", "n.", "Military")
    ]),
    ("çıkmak", [
        ("go out / exit", "v.", "Primary"),
        ("come out / emerge", "v.", "Primary"),
        ("climb / ascend", "v.", "Common Usage"),
        ("turn out / happen", "v.", "Common Usage"),
        ("date (somebody)", "v.", "Informal"),
        ("appear / be published", "v.", "Common Usage"),
        ("rise / increase (prices)", "v.", "General"),
        ("quit / leave (job)", "v.", "General"),
        ("be extracted / derived", "v.", "General"),
        ("arise / occur", "v.", "General"),
        ("cost (an amount)", "v.", "Trade/Economic")
    ]),
    ("düşmek", [
        ("fall / drop", "v.", "Primary"),
        ("decrease / decline", "v.", "Common Usage"),
        ("fall down / collapse", "v.", "Common Usage"),
        ("fall upon / be one's duty", "v.", "Formal"),
        ("be captivated / infatuated", "v.", "Slang"),
        ("fall from grace (gözden düşmek)", "v.", "Idiom"),
        ("weaken / deteriorate", "v.", "General"),
        ("land on / hit (shadow/light)", "v.", "General"),
        ("be deducted (discount)", "v.", "Trade/Economic")
    ]),
    ("tutmak", [
        ("hold", "v.", "Primary"),
        ("catch", "v.", "Primary"),
        ("keep", "v.", "Common Usage"),
        ("rent (house/car)", "v.", "Common Usage"),
        ("support / root for (team)", "v.", "Common Usage"),
        ("amount to / total (cost)", "v.", "Trade/Economic"),
        ("succeed / catch on (idea/song)", "v.", "Informal"),
        ("hold back / restrain", "v.", "General"),
        ("stick to / keep (promise)", "v.", "Idiom"),
        ("take effect (cure/medicine)", "v.", "General")
    ])
]

def download_octanove_c1c2():
    url = "https://raw.githubusercontent.com/openlanguageprofiles/olp-en-cefrj/master/octanove-vocabulary-profile-c1c2-1.0.csv"
    try:
        print("Downloading Octanove CEFR C1/C2 wordlist...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8')
            lines = content.splitlines()
            reader = csv.DictReader(lines)
            words = []
            for row in reader:
                headword = row.get("headword", "").strip()
                pos = row.get("pos", "").strip()
                cefr = row.get("CEFR", "").strip()
                if headword:
                    words.append((headword, pos, cefr))
            print(f"Downloaded {len(words)} C1/C2 words from Octanove.")
            return words
    except Exception as e:
        print(f"Warning: Could not download Octanove CEFR C1/C2: {e}")
        return []

def run_enrichment():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=" * 70)
    print("STARTING C1/C2 & POLYSEMY RADICAL VOCABULARY EXPANSION")
    print("=" * 70)

    # 1. Ingest Advanced Turkish C2 Lexicon
    print("1. Ingesting Advanced Turkish C2 Lexicon...")
    added_tr_c2 = 0
    updated_tr_c2 = 0
    for tr_word, en_senses in ADVANCED_TURKISH_C2_LEXICON:
        tr_low = turkish_lower(tr_word)
        for en_meaning, pos, cat in en_senses:
            en_clean = en_meaning.strip()
            en_low = en_clean.lower()
            cur.execute("SELECT rowid, category FROM bilingual WHERE tr_lower = ? AND en_lower = ? LIMIT 1;", (tr_low, en_low))
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE bilingual SET category = ?, type = ? WHERE rowid = ?;", (cat, pos, row[0]))
                updated_tr_c2 += 1
            else:
                cur.execute("""
                    INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (en_clean, tr_word, pos, cat, en_low, tr_low))
                added_tr_c2 += 1

    print(f"   -> Added {added_tr_c2}, updated {updated_tr_c2} Turkish C2 senses.")

    # 2. Ingest Advanced English C2 Lexicon
    print("2. Ingesting Advanced English C2 Lexicon...")
    added_en_c2 = 0
    updated_en_c2 = 0
    for en_word, tr_senses in ADVANCED_ENGLISH_C2_LEXICON:
        en_low = en_word.lower()
        for tr_meaning, pos, cat in tr_senses:
            tr_clean = tr_meaning.strip()
            tr_low = turkish_lower(tr_clean)
            cur.execute("SELECT rowid, category FROM bilingual WHERE en_lower = ? AND tr_lower = ? LIMIT 1;", (en_low, tr_low))
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE bilingual SET category = ?, type = ? WHERE rowid = ?;", (cat, pos, row[0]))
                updated_en_c2 += 1
            else:
                cur.execute("""
                    INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (en_word, tr_clean, pos, cat, en_low, tr_low))
                added_en_c2 += 1

    print(f"   -> Added {added_en_c2}, updated {updated_en_c2} English C2 senses.")

    # 3. Ingest High-Polysemy Words
    print("3. Ingesting High-Polysemy Multi-Sense Words...")
    added_poly = 0
    updated_poly = 0
    for headword, senses in POLYSEMOUS_WORDS:
        is_tr = any(c in "çğıöşüÇĞİÖŞÜ" for c in headword) or headword in ("çıkmak", "düşmek", "tutmak")
        if not is_tr:
            en_low = headword.lower()
            for tr_meaning, pos, cat in senses:
                tr_clean = tr_meaning.strip()
                tr_low = turkish_lower(tr_clean)
                cur.execute("SELECT rowid FROM bilingual WHERE en_lower = ? AND tr_lower = ? LIMIT 1;", (en_low, tr_low))
                row = cur.fetchone()
                if row:
                    cur.execute("UPDATE bilingual SET category = ?, type = ? WHERE rowid = ?;", (cat, pos, row[0]))
                    updated_poly += 1
                else:
                    cur.execute("""
                        INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower)
                        VALUES (?, ?, ?, ?, ?, ?);
                    """, (headword, tr_clean, pos, cat, en_low, tr_low))
                    added_poly += 1
        else:
            tr_low = turkish_lower(headword)
            for en_meaning, pos, cat in senses:
                en_clean = en_meaning.strip()
                en_low = en_clean.lower()
                cur.execute("SELECT rowid FROM bilingual WHERE tr_lower = ? AND en_lower = ? LIMIT 1;", (tr_low, en_low))
                row = cur.fetchone()
                if row:
                    cur.execute("UPDATE bilingual SET category = ?, type = ? WHERE rowid = ?;", (cat, pos, row[0]))
                    updated_poly += 1
                else:
                    cur.execute("""
                        INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower)
                        VALUES (?, ?, ?, ?, ?, ?);
                    """, (en_clean, headword, pos, cat, en_low, tr_low))
                    added_poly += 1

    print(f"   -> Added {added_poly}, updated {updated_poly} polysemy senses.")

    # 4. Octanove C1/C2 Tagging & Priority Assignment
    octanove_words = download_octanove_c1c2()
    tagged_cefr = 0
    if octanove_words:
        print("4. Tagging and prioritizing C1/C2 entries in DB...")
        for word, pos, cefr in octanove_words:
            w_low = word.lower()
            tag = f"CEFR {cefr}"
            cur.execute("""
                UPDATE bilingual 
                SET category = ? 
                WHERE en_lower = ? AND category NOT IN ('Primary', 'Common Usage', 'Idioms & Proverbs');
            """, (tag, w_low))
            if cur.rowcount > 0:
                tagged_cefr += cur.rowcount
        print(f"   -> Tagged {tagged_cefr} existing rows with CEFR C1/C2 level tags.")

    conn.commit()
    conn.close()
    print("=" * 70)
    print("ENRICHMENT COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_enrichment()
