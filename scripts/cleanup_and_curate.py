import os
import sys
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.utils import turkish_lower

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "dictionary.db"))

CURATED_HIGH_PRIORITY = [
    # Verbs
    ("went, departed, left (gitmek geçmiş zamanı)", "gitti", "verb (past)", "Temel Çekim"),
    ("came, arrived (gelmek geçmiş zamanı)", "geldi", "verb (past)", "Temel Çekim"),
    ("saw (görmek geçmiş zamanı)", "gördü", "verb (past)", "Temel Çekim"),
    ("looked, watched (bakmak geçmiş zamanı)", "baktı", "verb (past)", "Temel Çekim"),
    ("took, bought, received (almak geçmiş zamanı)", "aldı", "verb (past)", "Temel Çekim"),
    ("gave, provided (vermek geçmiş zamanı)", "verdi", "verb (past)", "Temel Çekim"),
    ("did, made (yapmak geçmiş zamanı)", "yaptı", "verb (past)", "Temel Çekim"),
    ("became, happened (olmak geçmiş zamanı)", "oldu", "verb (past)", "Temel Çekim"),
    ("spoke, talked (konuşmak geçmiş zamanı)", "konuştu", "verb (past)", "Temel Çekim"),
    ("wrote (yazmak geçmiş zamanı)", "yazdı", "verb (past)", "Temel Çekim"),
    ("read, studied (okumak geçmiş zamanı)", "okudu", "verb (past)", "Temel Çekim"),
    ("called, searched (aramak geçmiş zamanı)", "aradı", "verb (past)", "Temel Çekim"),
    ("liked, loved (sevmek geçmiş zamanı)", "sevdi", "verb (past)", "Temel Çekim"),
    ("found (bulmak geçmiş zamanı)", "buldu", "verb (past)", "Temel Çekim"),
    ("stayed, remained (kalmak geçmiş zamanı)", "kaldı", "verb (past)", "Temel Çekim"),
    ("heard (duymak geçmiş zamanı)", "duydu", "verb (past)", "Temel Çekim"),
    ("asked (sormak geçmiş zamanı)", "sordu", "verb (past)", "Temel Çekim"),
    ("thought (düşünmek geçmiş zamanı)", "düşündü", "verb (past)", "Temel Çekim"),
    ("opened (açmak geçmiş zamanı)", "açtı", "verb (past)", "Temel Çekim"),
    ("closed (kapatmak geçmiş zamanı)", "kapattı", "verb (past)", "Temel Çekim"),
    ("ate (yemek fiilinin geçmiş zamanı)", "yedi", "verb (past)", "Temel Çekim"),
    ("drank (içmek geçmiş zamanı)", "içti", "verb (past)", "Temel Çekim"),
    ("slept (uyumak geçmiş zamanı)", "uyudu", "verb (past)", "Temel Çekim"),

    # Present continuous
    ("coming, arrives (gelmek şimdiki zamanı)", "geliyor", "verb (pres)", "Temel Çekim"),
    ("going, departs (gitmek şimdiki zamanı)", "gidiyor", "verb (pres)", "Temel Çekim"),
    ("doing, making (yapmak şimdiki zamanı)", "yapıyor", "verb (pres)", "Temel Çekim"),
    ("working (çalışmak şimdiki zamanı)", "çalışıyor", "verb (pres)", "Temel Çekim"),
    ("looking, watching (bakmak şimdiki zamanı)", "bakıyor", "verb (pres)", "Temel Çekim"),
    ("reading, studying (okumak şimdiki zamanı)", "okuyor", "verb (pres)", "Temel Çekim"),
    ("writing (yazmak şimdiki zamanı)", "yazıyor", "verb (pres)", "Temel Çekim"),
    ("living, resides (yaşamak şimdiki zamanı)", "yaşıyor", "verb (pres)", "Temel Çekim"),
    ("speaking, talking (konuşmak şimdiki zamanı)", "konuşuyor", "verb (pres)", "Temel Çekim"),

    # Nouns with case suffixes
    ("at home, indoors (ev bulunma hali)", "evde", "noun (loc)", "Temel Çekim"),
    ("from home, out of the house (ev ayrılma hali)", "evden", "noun (abl)", "Temel Çekim"),
    ("to home, home (ev yönelme hali)", "eve", "noun (dat)", "Temel Çekim"),
    ("the house (ev belirtme hali)", "evi", "noun (acc)", "Temel Çekim"),
    ("houses, homes (ev çoğul hali)", "evler", "noun (pl)", "Temel Çekim"),
    
    ("at school, in school (okul bulunma hali)", "okulda", "noun (loc)", "Temel Çekim"),
    ("from school (okul ayrılma hali)", "okuldan", "noun (abl)", "Temel Çekim"),
    ("to school (okul yönelme hali)", "okula", "noun (dat)", "Temel Çekim"),
    ("the school (okul belirtme hali)", "okulu", "noun (acc)", "Temel Çekim"),
    ("schools (okul çoğul hali)", "okullar", "noun (pl)", "Temel Çekim"),

    ("at work; here it is, voila (iş bulunma hali)", "işte", "noun (loc)", "Temel Çekim"),
    ("to work (iş yönelme hali)", "işe", "noun (dat)", "Temel Çekim"),
    ("from work (iş ayrılma hali)", "işten", "noun (abl)", "Temel Çekim"),
    ("the work, the job (iş belirtme hali)", "işi", "noun (acc)", "Temel Çekim"),
    ("works, jobs (iş çoğul hali)", "işler", "noun (pl)", "Temel Çekim"),

    ("in the car, in the vehicle (araba bulunma hali)", "arabada", "noun (loc)", "Temel Çekim"),
    ("from the car (araba ayrılma hali)", "arabadan", "noun (abl)", "Temel Çekim"),
    ("to the car (araba yönelme hali)", "arabaya", "noun (dat)", "Temel Çekim"),
    ("the car (araba belirtme hali)", "arabayı", "noun (acc)", "Temel Çekim"),
    ("cars (araba çoğul hali)", "arabalar", "noun (pl)", "Temel Çekim"),

    ("children, kids (çocuk çoğul hali)", "çocuklar", "noun (pl)", "Temel Çekim"),
    ("the child (çocuk belirtme hali)", "çocuğu", "noun (acc)", "Temel Çekim"),
    ("to the child (çocuk yönelme hali)", "çocuğa", "noun (dat)", "Temel Çekim"),
    ("from the child (çocuk ayrılma hali)", "çocuktan", "noun (abl)", "Temel Çekim"),

    ("books (kitap çoğul hali)", "kitaplar", "noun (pl)", "Temel Çekim"),
    ("the book (kitap belirtme hali)", "kitabı", "noun (acc)", "Temel Çekim"),
    ("in the book (kitap bulunma hali)", "kitapta", "noun (loc)", "Temel Çekim"),
    ("from the book (kitap ayrılma hali)", "kitaptan", "noun (abl)", "Temel Çekim"),

    ("people, humans (insan çoğul hali)", "insanlar", "noun (pl)", "Temel Çekim"),
    ("to the people (insan yönelme hali)", "insanlara", "noun (dat)", "Temel Çekim"),
    ("friends (arkadaş çoğul hali)", "arkadaşlar", "noun (pl)", "Temel Çekim"),

    # High quality Idioms & Proverbs (TR -> EN)
    ("many a little makes a mickle; a penny saved is a penny gained; little drops make a mighty ocean", "damlaya damlaya göl olur", "proverb", "Common Usage"),
    ("turn a blind eye, overlook, condone, tolerate", "göz yummak", "idiom", "Common Usage"),
    ("be thrilled, be overjoyed, be on cloud nine", "etekleri zil çalmak", "idiom", "Common Usage"),
    ("fall from grace, lose favor, be discredited", "gözden düşmek", "idiom", "Common Usage"),
    ("pay attention, heed, give ear to", "kulak asmak", "idiom", "Common Usage"),
    ("eavesdrop, overhear, listen in", "kulak misafiri olmak", "idiom", "Common Usage"),
    ("have a hand in, contribute, do one's bit", "çorbada tuzu bulunmak", "idiom", "Common Usage"),
    ("grin from ear to ear, be all smiles", "ağzı kulaklarına varmak", "idiom", "Common Usage"),
    ("listen with rapt attention, be all ears", "can kulağıyla dinlemek", "idiom", "Common Usage"),
    ("make a mountain out of a molehill", "pireyi deve yapmak", "idiom", "Common Usage"),
    ("imminent, on the verge, just around the corner", "eli kulağında", "idiom", "Common Usage"),
    ("be superseded, lose popularity, be pushed aside", "pabucu dama atılmak", "idiom", "Common Usage"),
    ("nag incessantly, chew someone's ear off", "başının etini yemek", "idiom", "Common Usage"),
    ("spick and span, spotless, cleanly", "bal dök yala", "idiom", "Common Usage"),
    ("lose one's mind, go bananas, lose one's marbles", "kafayı yemek", "idiom", "Common Usage"),
    ("bubble over with excitement, be bursting with joy", "içi içine sığmamak", "idiom", "Common Usage"),
    ("keep one's chin up, be in high spirits", "morali yerinde olmak", "idiom", "Common Usage"),
    ("cry one's eyes out, weep bitterly", "gözyaşlarına boğulmak", "idiom", "Common Usage")
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Bozuk / parçalanmış deyim satırları temizleniyor...")
    # Delete broken fragments for göz yummak
    cur.execute("DELETE FROM bilingual WHERE tr_lower = 'göz yummak' AND en IN ('at.', 'by-', 'over-', 'pass-', 'pass.', 'eyes', 'eyess')")
    
    # Delete fragmented 1-word English matches for damlaya damlaya göl olur
    cur.execute("DELETE FROM bilingual WHERE tr_lower = 'damlaya damlaya göl olur' AND en IN ('begins', 'great-', 'lays', 'makes', 'many-', 'one-step', 'pennies', 'penny''s', 'pounds', 'step''s', 'strokes')")

    # Delete broken fragments for etekleri zil çalmak
    cur.execute("DELETE FROM bilingual WHERE tr_lower = 'etekleri zil çalmak' AND en = 'sweetshop'")

    print("Öncelikli çekim ve deyim kayıtları ekleniyor...")
    insert_sql = "INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower) VALUES (?, ?, ?, ?, ?, ?)"
    for en, tr, pos, cat in CURATED_HIGH_PRIORITY:
        en_lower = turkish_lower(en)
        tr_lower = turkish_lower(tr)
        cur.execute(insert_sql, (en, tr, pos, cat, en_lower, tr_lower))

    conn.commit()
    print("İndeksler güncelleniyor...")
    cur.execute("ANALYZE bilingual;")
    conn.commit()

    conn.close()
    print("Temizleme ve öncelikli eklemeler tamamlandı!")

if __name__ == "__main__":
    main()
