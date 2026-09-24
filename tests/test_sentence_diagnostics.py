import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from src.translator import SentenceTranslator

def run_tests():
    translator = SentenceTranslator()
    
    test_sentences = [
        ("tr", "en", "Selamlar. Bekar mısınız hanımefendi?"),
        ("tr", "en", "Merhaba Ayşe hanım, hazır mısınız?"),
        ("tr", "en", "Bu sınav çocuk oyuncağı."),
        ("en", "tr", "This exam is a piece of cake."),
        ("tr", "en", "Kendimi biraz keyifsiz hissediyorum."),
        ("en", "tr", "I am feeling under the weather."),
        ("tr", "en", "Bu araba ateş pahası."),
        ("en", "tr", "It costs an arm and a leg."),
        ("tr", "en", "Bir taşla iki kuş vurduk."),
        ("en", "tr", "We killed two birds with one stone."),
        ("tr", "en", "Damlaya damlaya göl olur."),
        ("tr", "en", "Gözden düşmek istemiyorum."),
        ("tr", "en", "Can kulağıyla dinlediler."),
        ("tr", "en", "Aç mısınız efendim?"),
        ("tr", "en", "Emin misiniz bu konuda?"),
        ("tr", "en", "Ciddi misin sen?"),
        ("tr", "en", "Bu mümkün mü?"),
        ("tr", "en", "Tatlı dil yılanı deliğinden çıkarır."),
        ("tr", "en", "Sen benim dengim değilsin."),
        ("tr", "en", "Cevap versene bana lütfen."),
    ]

    print("=" * 80)
    print("RUNNING 20-SENTENCE DIAGNOSTIC TEST")
    print("=" * 80)

    # Clear cache for accurate testing
    import sqlite3
    user_db = os.path.join(base_dir, "data", "user_data.db")
    if os.path.exists(user_db):
        conn = sqlite3.connect(user_db)
        conn.execute("DELETE FROM translation_cache;")
        conn.commit()
        conn.close()

    for i, (from_c, to_c, s) in enumerate(test_sentences, 1):
        res = translator.translate(s, from_lang=from_c, to_lang=to_c)
        out = res.translated_text
        eng = res.engine
        conf = res.confidence
        print(f"[{i:02d}] ({from_c}->{to_c})")
        print(f"     IN : {s}")
        print(f"     OUT: {out}")
        print(f"     ENG: {eng} (Conf: {conf})")
        print("-" * 80)

if __name__ == "__main__":
    run_tests()
