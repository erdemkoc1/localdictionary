"""
Radical Dictionary Expansion & Multi-Sense Polysemy Pipeline
Adds tens of thousands of C1/C2 advanced words, rich polysemy multi-senses,
Kaikki Turkish Wiktionary lemma senses, Academic Word List (AWL), and GRE vocabulary.
"""

import os
import sys
import json
import gzip
import time
import urllib.request
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from src.utils import turkish_lower

DB_PATH = os.path.join(base_dir, "data", "dictionary.db")

# 1. Advanced Literary, Philosophical & Diplomatic Turkish C2 Vocabulary
LITERARY_TURKISH_C2 = [
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
    ("mefhum", [("concept", "n.", "Primary"), ("notion", "n.", "Common Usage"), ("idea", "n.", "General"), ("conception", "n.", "Formal")]),
    ("mertebe", [("rank", "n.", "Primary"), ("degree", "n.", "Common Usage"), ("grade", "n.", "General"), ("echelon", "n.", "Formal"), ("status", "n.", "Common Usage")]),
    ("meşakkat", [("hardship", "n.", "Primary"), ("toil", "n.", "Common Usage"), ("tribulation", "n.", "Formal"), ("trouble", "n.", "General"), ("arduous task", "n.", "Formal")]),
    ("mukadderat", [("destiny", "n.", "Primary"), ("fate", "n.", "Common Usage"), ("predestination", "n.", "Formal"), ("kismet", "n.", "General")]),
    ("mübrem", [("urgent", "adj.", "Primary"), ("pressing", "adj.", "Common Usage"), ("indispensable", "adj.", "Formal"), ("vital", "adj.", "Formal")]),
    ("müessif", [("regrettable", "adj.", "Primary"), ("deplorable", "adj.", "Formal"), ("lamentable", "adj.", "Formal"), ("sad", "adj.", "General")]),
    ("mülga", [("repealed", "adj.", "Primary"), ("abolished", "adj.", "Law"), ("annulled", "adj.", "Formal"), ("defunct", "adj.", "Formal")]),
    ("mümeyyiz", [("discerning", "adj.", "Primary"), ("discriminating", "adj.", "Formal"), ("examiner", "n.", "Formal"), ("capable of distinction", "adj.", "Law")]),
    ("münavebeli", [("alternating", "adj.", "Primary"), ("rotational", "adj.", "Common Usage"), ("by turns", "adv.", "General")]),
    ("müruruzaman", [("statute of limitations", "n.", "Primary"), ("prescription", "n.", "Law"), ("lapse of time", "n.", "Formal")]),
    ("müstehzi", [("sarcastic", "adj.", "Primary"), ("mocking", "adj.", "Common Usage"), ("derisive", "adj.", "Formal"), ("scoffing", "adj.", "Formal"), ("ironic", "adj.", "General")]),
    ("müteakip", [("following", "adj.", "Primary"), ("subsequent", "adj.", "Common Usage"), ("consecutive", "adj.", "Formal"), ("ensuing", "adj.", "Formal")]),
    ("müteessir", [("grieved", "adj.", "Primary"), ("saddened", "adj.", "Common Usage"), ("affected", "adj.", "Formal"), ("heartbroken", "adj.", "General")]),
    ("müteferrik", [("miscellaneous", "adj.", "Primary"), ("scattered", "adj.", "Common Usage"), ("sundry", "adj.", "Formal"), ("disparate", "adj.", "Academic")]),
    ("mütehassıs", [("specialist", "n.", "Primary"), ("expert", "n.", "Common Usage"), ("authority", "n.", "Formal")]),
    ("mütalaa", [("deliberation", "n.", "Primary"), ("study", "n.", "Common Usage"), ("legal opinion", "n.", "Law"), ("reflection", "n.", "Formal")]),
    ("müteveffa", [("deceased", "adj.", "Primary"), ("late", "adj.", "Common Usage"), ("departed", "adj.", "Formal")]),
    ("müşahhas", [("concrete", "adj.", "Primary"), ("tangible", "adj.", "Common Usage"), ("embodied", "adj.", "Formal"), ("substantiated", "adj.", "Academic")]),
    ("payidar", [("everlasting", "adj.", "Primary"), ("enduring", "adj.", "Common Usage"), ("perpetual", "adj.", "Formal"), ("immortal", "adj.", "Literary")]),
    ("peyda", [("arisen", "adj.", "Primary"), ("emerged", "adj.", "Common Usage"), ("manifested", "adj.", "Formal")]),
    ("rabıta", [("bond", "n.", "Primary"), ("link", "n.", "Common Usage"), ("connection", "n.", "General"), ("nexus", "n.", "Formal")]),
    ("refakat", [("accompaniment", "n.", "Primary"), ("escort", "n.", "Common Usage"), ("attendance", "n.", "Formal"), ("companionship", "n.", "General")]),
    ("salahiyet", [("authority", "n.", "Primary"), ("competence", "n.", "Law"), ("jurisdiction", "n.", "Formal"), ("power", "n.", "General")]),
    ("seciye", [("character", "n.", "Primary"), ("disposition", "n.", "Formal"), ("temperament", "n.", "Common Usage"), ("moral nature", "n.", "Formal")]),
    ("selaset", [("fluency", "n.", "Primary"), ("eloquence", "n.", "Common Usage"), ("smoothness of style", "n.", "Literary")]),
    ("suiniyet", [("bad faith", "n.", "Primary"), ("mala fides", "n.", "Law"), ("malice", "n.", "Formal"), ("ill intention", "n.", "Common Usage")]),
    ("şaibe", [("taint", "n.", "Primary"), ("suspicion", "n.", "Common Usage"), ("blemish", "n.", "Formal"), ("stigma", "n.", "General")]),
    ("şayan", [("worthy", "adj.", "Primary"), ("deserving", "adj.", "Common Usage"), ("meriting", "adj.", "Formal")]),
    ("şedid", [("severe", "adj.", "Primary"), ("intense", "adj.", "Common Usage"), ("fierce", "adj.", "Formal"), ("harsh", "adj.", "General")]),
    ("şümullü", [("comprehensive", "adj.", "Primary"), ("exhaustive", "adj.", "Common Usage"), ("all-inclusive", "adj.", "Formal"), ("broad-ranging", "adj.", "General")]),
    ("tahakkuk", [("realization", "n.", "Primary"), ("actualization", "n.", "Formal"), ("materialization", "n.", "Formal"), ("accrual", "n.", "Finance")]),
    ("temayül", [("tendency", "n.", "Primary"), ("inclination", "n.", "Common Usage"), ("propensity", "n.", "Formal"), ("leaning", "n.", "General")]),
    ("teminat", [("guarantee", "n.", "Primary"), ("collateral", "n.", "Finance"), ("security", "n.", "Law"), ("assurance", "n.", "Common Usage")]),
    ("temkin", [("prudence", "n.", "Primary"), ("circumspection", "n.", "Formal"), ("deliberation", "n.", "Formal"), ("caution", "n.", "Common Usage")]),
    ("tensip", [("approval", "n.", "Primary"), ("sanction", "n.", "Formal"), ("designation", "n.", "Law"), ("deeming appropriate", "n.", "Formal")]),
    ("teselsül", [("succession", "n.", "Primary"), ("chain", "n.", "Common Usage"), ("concatenation", "n.", "Formal"), ("sequence", "n.", "General")]),
    ("teşebbüs", [("initiative", "n.", "Primary"), ("enterprise", "n.", "Common Usage"), ("attempt", "n.", "General"), ("venture", "n.", "Finance")]),
    ("tevdi", [("submission", "n.", "Primary"), ("handing over", "n.", "Common Usage"), ("deposit", "n.", "Finance"), ("entrusting", "n.", "Formal")]),
    ("tevessül", [("resort to", "v.", "Primary"), ("attempt", "v.", "Common Usage"), ("undertake", "v.", "Formal")]),
    ("vazıh", [("clear", "adj.", "Primary"), ("lucid", "adj.", "Formal"), ("explicit", "adj.", "Common Usage"), ("distinct", "adj.", "General")]),
    ("vefakar", [("faithful", "adj.", "Primary"), ("loyal", "adj.", "Common Usage"), ("devoted", "adj.", "Common Usage"), ("constant", "adj.", "Formal")]),
    ("velvele", [("uproar", "n.", "Primary"), ("clamor", "n.", "Common Usage"), ("tumult", "n.", "Formal"), ("commotion", "n.", "General")]),
    ("vüsat", [("scope", "n.", "Primary"), ("breadth", "n.", "Common Usage"), ("capacity", "n.", "Formal"), ("amplitude", "n.", "Academic")]),
    ("yadigar", [("memento", "n.", "Primary"), ("keepsake", "n.", "Common Usage"), ("relic", "n.", "Formal"), ("souvenir", "n.", "General")]),
    ("yegane", [("sole", "adj.", "Primary"), ("unique", "adj.", "Common Usage"), ("only", "adj.", "General"), ("singular", "adj.", "Formal")]),
    ("zevahir", [("appearances", "n.", "Primary"), ("outward show", "n.", "Common Usage"), ("facade", "n.", "Formal")]),
    ("zeval", [("decline", "n.", "Primary"), ("downfall", "n.", "Common Usage"), ("ruin", "n.", "Formal"), ("noon", "n.", "Archaic")]),
    ("zımnında", [("for the purpose of", "prep.", "Primary"), ("in the context of", "prep.", "Formal"), ("under the pretext of", "prep.", "Common Usage")]),
    ("zillet", [("humiliation", "n.", "Primary"), ("abasement", "n.", "Formal"), ("ignominy", "n.", "Formal"), ("degradation", "n.", "Common Usage")]),
    ("zuhur", [("manifestation", "n.", "Primary"), ("emergence", "n.", "Common Usage"), ("appearance", "n.", "Formal"), ("outbreak", "n.", "General")])
]

# 2. Rich Polysemy for Core Verbs and Nouns (English and Turkish)
POLYSEMOUS_VERBS_AND_NOUNS = [
    ("break", [
        ("kırmak", "v.", "Primary"),
        ("kopmak", "v.", "Primary"),
        ("bozmak (kural/rekor)", "v.", "Common Usage"),
        ("mola / ara", "n.", "Primary"),
        ("ara vermek", "v.", "Common Usage"),
        ("patlak vermek (savaş/yangın)", "v.", "Common Usage"),
        ("ayrılmak (break up)", "v.", "Idiom"),
        ("arızalanmak (break down)", "v.", "Idiom"),
        ("sözünü tutmamak", "v.", "Idiom"),
        ("bozdurmak (para)", "v.", "Trade/Economic"),
        ("şafak sökmek (day breaks)", "v.", "Literary"),
        ("dalgaların kıyıya vurması", "v.", "General"),
        ("şans / fırsat (lucky break)", "n.", "Informal")
    ]),
    ("draw", [
        ("çizmek", "v.", "Primary"),
        ("çekmek (dikkat/para/kura)", "v.", "Primary"),
        ("berabere kalmak", "v.", "Sports"),
        ("beraberlik", "n.", "Sports"),
        ("çekmece", "n.", "General"),
        ("sonuç çıkarmak (draw conclusion)", "v.", "Formal"),
        ("yaklaşmak (draw near)", "v.", "General"),
        ("kura çekmek", "v.", "Common Usage"),
        ("silah çekmek", "v.", "Action"),
        ("nefes çekmek", "v.", "General")
    ]),
    ("hold", [
        ("tutmak", "v.", "Primary"),
        ("düzenlemek (toplantı/seçim)", "v.", "Primary"),
        ("sahip olmak (unvan/kayıt)", "v.", "Common Usage"),
        ("beklemek (telefonda)", "v.", "Common Usage"),
        ("tahammül etmek / dayanmak", "v.", "Common Usage"),
        ("kavrama / tutuş", "n.", "Primary"),
        ("etki / nüfuz", "n.", "Formal"),
        ("hambal (gemide kargo bölümü)", "n.", "Maritime"),
        ("ertelemek (put on hold)", "v.", "Idiom"),
        ("geçerli olmak (hold true)", "v.", "Academic")
    ]),
    ("strike", [
        ("çarpmak / vurmak", "v.", "Primary"),
        ("grev yapmak", "v.", "Primary"),
        ("grev", "n.", "Primary"),
        ("etkilemek (aklına gelmek)", "v.", "Common Usage"),
        ("saldırı / hava harekatı", "n.", "Military"),
        ("çakmak (kibrit)", "v.", "General"),
        ("keşfetmek (petrol/altın)", "v.", "Trade/Economic"),
        ("çalmak (saat)", "v.", "General"),
        ("uzlaşmaya varmak (strike a deal)", "v.", "Idiom"),
        ("denge kurmak (strike a balance)", "v.", "Idiom")
    ]),
    ("pass", [
        ("geçmek", "v.", "Primary"),
        ("başarmak (sınavı)", "v.", "Primary"),
        ("pas vermek", "v.", "Sports"),
        ("pasaport / geçiş kartı", "n.", "Primary"),
        ("vazgeçmek / pas geçmek", "v.", "Informal"),
        ("dağ geçidi", "n.", "Geography"),
        ("yasalaşmak (kanun)", "v.", "Politics"),
        ("vefat etmek (pass away)", "v.", "Idiom"),
        ("bayılmak (pass out)", "v.", "Idiom"),
        ("nesilden nesile aktarmak (pass down)", "v.", "Idiom")
    ]),
    ("clear", [
        ("açık / net", "adj.", "Primary"),
        ("temizlemek / boşaltmak", "v.", "Primary"),
        ("belirgin / anlaşılır", "adj.", "Common Usage"),
        ("berrak (su/hava)", "adj.", "Common Usage"),
        ("temize çıkarmak (beraat)", "v.", "Law"),
        ("aşmak (engeli)", "v.", "General"),
        ("tahliye etmek", "v.", "Formal"),
        ("net gelir elde etmek", "v.", "Finance"),
        ("açıkça", "adv.", "General"),
        ("tamamen uzaklaşmak (clear off)", "v.", "Idiom")
    ]),
    ("fall", [
        ("düşmek", "v.", "Primary"),
        ("sonbahar", "n.", "Primary"),
        ("düşüş / azalma", "n.", "Common Usage"),
        ("yıkılmak / teslim olmak (kale/rejim)", "v.", "History"),
        ("aşık olmak (fall in love)", "v.", "Idiom"),
        ("ayrı düşmek (fall apart)", "v.", "Idiom"),
        ("yetersiz kalmak (fall short)", "v.", "Idiom"),
        ("geri kalmak (fall behind)", "v.", "Idiom"),
        ("şelale (falls)", "n.", "Geography"),
        ("denk gelmek (tarih)", "v.", "General")
    ]),
    ("açmak", [
        ("open", "v.", "Primary"),
        ("turn on (light/device)", "v.", "Primary"),
        ("unfold / spread", "v.", "Common Usage"),
        ("bloom / blossom (flowers)", "v.", "Common Usage"),
        ("carve / dig (road/tunnel)", "v.", "Common Usage"),
        ("bring up (a topic)", "v.", "Idiom"),
        ("lighten (color)", "v.", "General"),
        ("whet (appetite)", "v.", "Idiom"),
        ("relieve / soothe (mind)", "v.", "General"),
        ("clear up (weather)", "v.", "General")
    ]),
    ("kapatmak", [
        ("close / shut", "v.", "Primary"),
        ("turn off (light/device)", "v.", "Primary"),
        ("cover / conceal", "v.", "Common Usage"),
        ("shut down / terminate (business)", "v.", "Common Usage"),
        ("pay off / settle (debt)", "v.", "Trade/Economic"),
        ("hang up (phone)", "v.", "Common Usage"),
        ("imprison / lock up", "v.", "Law"),
        ("seal (envelope/gap)", "v.", "General"),
        ("monopolize / buy up", "v.", "Trade/Economic"),
        ("put an end to (a subject)", "v.", "Idiom")
    ]),
    ("çekmek", [
        ("pull", "v.", "Primary"),
        ("take (photo)", "v.", "Primary"),
        ("withdraw (money)", "v.", "Banking"),
        ("suffer / endure (pain)", "v.", "Common Usage"),
        ("attract / draw (attention)", "v.", "Common Usage"),
        ("shrink (clothes)", "v.", "General"),
        ("resemble (take after parents)", "v.", "Informal"),
        ("shoot (film)", "v.", "Cinema"),
        ("tow (vehicle)", "v.", "Transport"),
        ("weigh (amount)", "v.", "General"),
        ("take hands off / withdraw (elini çekmek)", "v.", "Idiom")
    ]),
    ("almak", [
        ("take", "v.", "Primary"),
        ("buy / purchase", "v.", "Primary"),
        ("receive / get", "v.", "Primary"),
        ("absorb / contain", "v.", "Common Usage"),
        ("hire / employ", "v.", "Business"),
        ("capture / conquer (city)", "v.", "Military"),
        ("remove / clear away", "v.", "General"),
        ("gain (weight)", "v.", "General"),
        ("borrow (money)", "v.", "Finance"),
        ("take in (clothing)", "v.", "Fashion")
    ]),
    ("vermek", [
        ("give", "v.", "Primary"),
        ("grant / bestow", "v.", "Formal"),
        ("yield / produce (fruit/result)", "v.", "Common Usage"),
        ("pay / spend", "v.", "Trade/Economic"),
        ("commit / assign", "v.", "General"),
        ("cause / impart", "v.", "General"),
        ("give away (daughter in marriage)", "v.", "Cultural"),
        ("shed (light/weight)", "v.", "General"),
        ("pass / hand over", "v.", "Common Usage"),
        ("make / render (decision)", "v.", "Idiom")
    ]),
    ("geçmek", [
        ("pass / cross", "v.", "Primary"),
        ("overtake", "v.", "Transport"),
        ("expire / elapse (time)", "v.", "Common Usage"),
        ("infect / transmit (disease)", "v.", "Medical"),
        ("take effect / be valid", "v.", "Law"),
        ("give up / forfeit (vazgeçmek)", "v.", "Idiom"),
        ("move to / transfer (position)", "v.", "Business"),
        ("undergo / experience (başından geçmek)", "v.", "Idiom"),
        ("pass down / inherit", "v.", "General"),
        ("exceed / surpass", "v.", "General")
    ]),
    ("yol", [
        ("road / way / path", "n.", "Primary"),
        ("method / means / manner", "n.", "Common Usage"),
        ("journey / travel", "n.", "Common Usage"),
        ("course / direction", "n.", "General"),
        ("strip / stripe (pattern)", "n.", "Fashion"),
        ("turn / time (kez/defa)", "n.", "Informal"),
        ("guide / rule (yol yordam)", "n.", "Idiom"),
        ("on the way (yolda)", "adv.", "Common Usage"),
        ("make way (yol vermek)", "v.", "Idiom"),
        ("set out (yola çıkmak)", "v.", "Idiom")
    ]),
    ("göz", [
        ("eye", "n.", "Primary"),
        ("drawer / compartment", "n.", "Common Usage"),
        ("hole / mesh (net/sieve)", "n.", "General"),
        ("spring / source (water)", "n.", "Geography"),
        ("room / cell (building)", "n.", "Architecture"),
        ("look / glance", "n.", "Common Usage"),
        ("keep an eye on (göz kulak olmak)", "v.", "Idiom"),
        ("fall out of favor (gözden düşmek)", "v.", "Idiom"),
        ("overlook (göz yummak)", "v.", "Idiom"),
        ("catch the eye (göze çarpmak)", "v.", "Idiom")
    ])
]

# 3. Kaikki Turkish Wiktionary Ingestion
KAIKKI_URL = "https://kaikki.org/dictionary/Turkish/kaikki.org-dictionary-Turkish.jsonl"

POS_MAP = {
    "noun": "n.", "verb": "v.", "adj": "adj.", "adv": "adv.",
    "pron": "pron.", "prep": "prep.", "conj": "conj.", "intj": "interj.",
    "name": "proper n.", "phrase": "phrase", "idiom": "idiom"
}

def map_kaikki_category(tags):
    tags_set = set(tags or [])
    if "idiomatic" in tags_set or "proverb" in tags_set:
        return "Idioms & Proverbs"
    if "slang" in tags_set or "colloquial" in tags_set:
        return "Slang"
    if "formal" in tags_set or "literary" in tags_set or "poetic" in tags_set:
        return "Formal"
    if "archaic" in tags_set or "obsolete" in tags_set:
        return "Archaic"
    if "technical" in tags_set or "medicine" in tags_set or "law" in tags_set or "botany" in tags_set:
        return "Technical"
    if "figurative" in tags_set:
        return "Figurative"
    return "Common Usage"

def clean_kaikki_gloss(g):
    if not g:
        return ""
    g = g.strip()
    if g.startswith("synonym of "):
        g = g.replace("synonym of ", "").split(" (“")[0].strip()
    if g.startswith("ellipsis of "):
        g = g.replace("ellipsis of ", "").split(" (“")[0].strip()
    return g

def run_radical_expansion():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=" * 80)
    print("RADICAL EXPANSION: EXPANDING VOCABULARY TO C2 LEVEL & DEEP POLYSEMY")
    print("=" * 80)

    cur.execute("SELECT COUNT(*) FROM bilingual;")
    initial_count = cur.fetchone()[0]
    print(f"Initial bilingual entries: {initial_count:,}")

    # Phase 1: Ingest Literary Turkish C2
    print("\nPhase 1: Ingesting Literary & Intellectual Turkish C2 Lexicon...")
    added_tr_c2 = 0
    for tr_word, en_senses in LITERARY_TURKISH_C2:
        tr_low = turkish_lower(tr_word)
        for en_meaning, pos, cat in en_senses:
            en_clean = en_meaning.strip()
            en_low = en_clean.lower()
            cur.execute("SELECT rowid FROM bilingual WHERE tr_lower = ? AND en_lower = ? LIMIT 1;", (tr_low, en_low))
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE bilingual SET category = ?, type = ? WHERE rowid = ?;", (cat, pos, row[0]))
            else:
                cur.execute("INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower) VALUES (?, ?, ?, ?, ?, ?);",
                            (en_clean, tr_word, pos, cat, en_low, tr_low))
                added_tr_c2 += 1
    print(f"   -> Added {added_tr_c2} new literary Turkish C2 senses, updated priorities for all.")

    # Phase 2: Ingest Core Polysemy
    print("\nPhase 2: Ingesting Deep Polysemy for Core Verbs, Nouns & Idioms...")
    added_poly = 0
    for headword, senses in POLYSEMOUS_VERBS_AND_NOUNS:
        is_tr = any(c in "çğıöşüÇĞİÖŞÜ" for c in headword) or headword in ("açmak", "kapatmak", "çekmek", "almak", "vermek", "geçmek", "yol", "göz")
        if not is_tr:
            en_low = headword.lower()
            for tr_meaning, pos, cat in senses:
                tr_clean = tr_meaning.strip()
                tr_low = turkish_lower(tr_clean)
                cur.execute("SELECT rowid FROM bilingual WHERE en_lower = ? AND tr_lower = ? LIMIT 1;", (en_low, tr_low))
                row = cur.fetchone()
                if row:
                    cur.execute("UPDATE bilingual SET category = ?, type = ? WHERE rowid = ?;", (cat, pos, row[0]))
                else:
                    cur.execute("INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower) VALUES (?, ?, ?, ?, ?, ?);",
                                (headword, tr_clean, pos, cat, en_low, tr_low))
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
                else:
                    cur.execute("INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower) VALUES (?, ?, ?, ?, ?, ?);",
                                (en_clean, headword, pos, cat, en_low, tr_low))
                    added_poly += 1
    print(f"   -> Ingested {added_poly} new polysemy senses.")

    # Phase 3: Kaikki Turkish Wiktionary Ingestion
    print("\nPhase 3: Downloading & Ingesting Kaikki Turkish Wiktionary (45,949 entries)...")
    t0 = time.time()
    req = urllib.request.Request(KAIKKI_URL, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'gzip'})
    kaikki_rows = []
    seen_in_kaikki = set()

    with urllib.request.urlopen(req, timeout=30) as resp:
        with gzip.GzipFile(fileobj=resp) as gz:
            for line in gz:
                try:
                    data = json.loads(line.decode('utf-8'))
                except Exception:
                    continue
                word = data.get('word', '').strip()
                pos_raw = data.get('pos', 'noun')
                pos_clean = POS_MAP.get(pos_raw, f"{pos_raw}.")
                senses = data.get('senses', [])
                if not word or not senses:
                    continue

                for s in senses:
                    tags = s.get('tags') or []
                    if 'form-of' in tags:
                        continue
                    glosses = s.get('glosses') or []
                    if not glosses:
                        continue
                    g_clean = clean_kaikki_gloss(glosses[0])
                    if not g_clean or len(g_clean) > 140:
                        continue

                    cat = map_kaikki_category(tags)
                    tr_low = turkish_lower(word)
                    en_low = g_clean.lower()
                    key = (tr_low, en_low)
                    if key in seen_in_kaikki:
                        continue
                    seen_in_kaikki.add(key)
                    kaikki_rows.append((g_clean, word, pos_clean, cat, en_low, tr_low))

    print(f"   Downloaded and extracted {len(kaikki_rows):,} valid lemma senses in {time.time()-t0:.1f}s.")
    
    # Batch filter against DB
    print("   Inserting new Kaikki senses into database...")
    to_insert_kaikki = []
    for en, tr, pos, cat, en_l, tr_l in kaikki_rows:
        cur.execute("SELECT 1 FROM bilingual WHERE tr_lower = ? AND en_lower = ? LIMIT 1;", (tr_l, en_l))
        if not cur.fetchone():
            to_insert_kaikki.append((en, tr, pos, cat, en_l, tr_l))

    if to_insert_kaikki:
        cur.executemany("INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower) VALUES (?, ?, ?, ?, ?, ?);",
                        to_insert_kaikki)
        conn.commit()
    print(f"   -> Successfully added {len(to_insert_kaikki):,} new Kaikki Turkish Wiktionary senses.")

    # Phase 4: Ingest Academic Word Lists (AWL) & GRE Words
    print("\nPhase 4: Downloading & Tagging Academic Word List (AWL) and GRE Vocabulary...")
    awl_url = "https://raw.githubusercontent.com/lpmi-13/machine_readable_wordlists/master/Academic/AWL/AWL.json"
    gre_url = "https://raw.githubusercontent.com/bhargavyagnik/GRE-Flashcards/master/data.json"
    
    # 4a. AWL
    try:
        req = urllib.request.Request(awl_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            awl_data = json.loads(r.read().decode('utf-8'))
            awl_words = set()
            for sublist, headwords in awl_data.items():
                for hw, forms in headwords.items():
                    awl_words.add(hw.lower())
                    for form in forms:
                        awl_words.add(form.lower())
            print(f"   Loaded {len(awl_words)} academic word forms from AWL.")
            # Tag existing entries in DB
            tagged_awl = 0
            for w in awl_words:
                cur.execute("""
                    UPDATE bilingual 
                    SET category = 'CEFR C1' 
                    WHERE en_lower = ? AND category NOT IN ('Primary', 'Common Usage', 'Idioms & Proverbs');
                """, (w,))
                tagged_awl += cur.rowcount
            print(f"   -> Tagged {tagged_awl:,} rows with Academic CEFR C1 priority.")
    except Exception as e:
        print(f"   Warning on AWL: {e}")

    # 4b. GRE Flashcards
    try:
        req = urllib.request.Request(gre_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            gre_data = json.loads(r.read().decode('utf-8'))
            gre_words = gre_data.get('Word', {})
            print(f"   Loaded {len(gre_words)} advanced GRE headwords.")
            tagged_gre = 0
            for w in gre_words.values():
                w_low = w.lower().strip()
                cur.execute("""
                    UPDATE bilingual 
                    SET category = 'CEFR C2' 
                    WHERE en_lower = ? AND category NOT IN ('Primary', 'Common Usage', 'Idioms & Proverbs', 'CEFR C1');
                """, (w_low,))
                tagged_gre += cur.rowcount
            print(f"   -> Tagged {tagged_gre:,} rows with Advanced GRE CEFR C2 priority.")
    except Exception as e:
        print(f"   Warning on GRE: {e}")

    conn.commit()

    # Final Stats
    cur.execute("SELECT COUNT(*) FROM bilingual;")
    final_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT en_lower) FROM bilingual;")
    unique_en = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT tr_lower) FROM bilingual;")
    unique_tr = cur.fetchone()[0]

    conn.close()

    print("\n" + "=" * 80)
    print("RADICAL EXPANSION COMPLETED SUCCESSFULLY!")
    print(f"Initial bilingual entries : {initial_count:,}")
    print(f"Final bilingual entries   : {final_count:,} (+{final_count - initial_count:,})")
    print(f"Unique English lemmas     : {unique_en:,}")
    print(f"Unique Turkish lemmas     : {unique_tr:,}")
    print("=" * 80)

if __name__ == "__main__":
    run_radical_expansion()
