import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from src.translator import SentenceTranslator

translator = SentenceTranslator()

sentences = [
    ("en", "tr", "The minister emphasized the principle of reciprocity in bilateral relations."),
    ("en", "tr", "She has always been a maverick who refuses to follow established conventions."),
    ("en", "tr", "Finding this rare manuscript in a small antique shop was sheer serendipity."),
    ("en", "tr", "Her laconic reply left no room for further debate."),
    ("en", "tr", "His explanation only served to obfuscate the real issue."),
    ("tr", "en", "Bu karar mütekabiliyet ilkesi doğrultusunda alındı."),
    ("tr", "en", "Büyük bir özveri ile çalıştı."),
    ("tr", "en", "Öfkesine hakim olup itidal ile hareket etti."),
    ("tr", "en", "Bu durum geleneksel kurallara tamamen aykırı."),
    ("tr", "en", "Ben bu konuda herhangi bir muhatap bulamadım."),
]

print("=" * 80)
print("TESTING ADVANCED C1/C2 SENTENCE TRANSLATIONS")
print("=" * 80)

for from_c, to_c, s in sentences:
    res = translator.translate(s, from_lang=from_c, to_lang=to_c)
    print(f"\n[{from_c.upper()} ➔ {to_c.upper()}]")
    print(f"  IN : {s}")
    print(f"  OUT: {res.translated_text}")
    print(f"  ENG: {res.engine} (Confidence: {res.confidence}%, Level: {res.confidence_level})")
