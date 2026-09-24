import os
import sys
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from src.utils import turkish_lower
from scripts.add_idioms_to_db import ENGLISH_IDIOMS, TURKISH_IDIOMS

# Expanded list of English Idioms and Proverbs
ADDITIONAL_ENGLISH_IDIOMS = [
    ("a piece of cake", "çocuk oyuncağı, çantada keklik, tereyağından kıl çeker gibi", "idiom"),
    ("piece of cake", "çocuk oyuncağı, çantada keklik", "idiom"),
    ("under the weather", "keyifsiz, halsiz, hafif rahatsız", "idiom"),
    ("feeling under the weather", "kendini keyifsiz hissetmek, halsiz olmak", "idiom"),
    ("cost an arm and a leg", "ateş pahası olmak, çok pahalı olmak", "idiom"),
    ("costs an arm and a leg", "ateş pahası, dünyanın parası", "idiom"),
    ("kill two birds with one stone", "bir taşla iki kuş vurmak", "idiom"),
    ("killed two birds with one stone", "bir taşla iki kuş vurduk, bir taşla iki kuş vurdu", "idiom"),
    ("actions speak louder than words", "ayinesi iştir kişinin lafa bakılmaz", "proverb"),
    ("bite the bullet", "dişini sıkmak, acı ilacı içmek", "idiom"),
    ("break a leg", "şeytanın bacağını kır, bol şans, iyi şanslar", "idiom"),
    ("burn one's bridges", "gemileri yakmak, geri dönüşü olmayan adım atmak", "idiom"),
    ("burn bridges", "gemileri yakmak", "idiom"),
    ("call it a day", "paydos etmek, bugünlük bu kadar demek", "idiom"),
    ("cry over spilled milk", "son pişmanlık fayda etmez", "proverb"),
    ("spill the beans", "ağzındaki baklayı çıkarmak, sırrı ifşa etmek", "idiom"),
    ("hit the nail on the head", "taşı gediğine koymak, tam üstüne basmak", "idiom"),
    ("on cloud nine", "etekleri zil çalmak, havalara uçmak", "idiom"),
    ("out of the blue", "damdan düşer gibi, ansızın, birdenbire", "idiom"),
    ("once in a blue moon", "ayda yılda bir, kırk yılda bir", "idiom"),
    ("hit the sack", "kafayı vurup yatmak", "idiom"),
    ("barking up the wrong tree", "yanlış kapıyı çalmak", "idiom"),
    ("beat around the bush", "lafı dolandırmak, eveleyip gevelemek", "idiom"),
    ("better late than never", "geç olsun güç olmasın", "proverb"),
    ("you reap what you sow", "ne ekersen onu biçersin", "proverb"),
    ("time flies", "zaman su gibi akıp geçiyor", "idiom"),
    ("through thick and thin", "iyi günde kötü günde", "idiom"),
    ("throw in the towel", "havlu atmak, pes etmek", "idiom"),
    ("turn a blind eye", "göz yummak, görmezden gelmek", "idiom"),
    ("make ends meet", "iki yakayı bir araya getirmek", "idiom"),
    ("the last straw", "bardağı taşıran son damla", "idiom"),
    ("last straw", "bardağı taşıran son damla", "idiom"),
    ("no pain, no gain", "zahmetsiz rahmet olmaz, emeksiz yemek olmaz", "proverb"),
    ("practice makes perfect", "işleyen demir ışıldar, tekrar mükemmelleştirir", "proverb"),
    ("easy come, easy go", "haydan gelen huya gider", "proverb"),
    ("every cloud has a silver lining", "her şerde bir hayır vardır", "proverb"),
    ("it takes two to tango", "tek elle alkış tutulmaz", "proverb"),
    ("it's not rocket science", "atla deve değil, çok karmaşık bir şey değil", "idiom"),
    ("not rocket science", "atla deve değil", "idiom"),
    ("curiosity killed the cat", "fazla merak başa bela getirir", "proverb"),
    ("the early bird catches the worm", "erken kalkan yol alır", "proverb"),
    ("birds of a feather flock together", "tencere yuvarlanmış kapağını bulmuş", "proverb"),
    ("silence is golden", "söz gümüşse sükut altındır", "proverb"),
    ("time is money", "vakit nakittir", "proverb"),
    ("fall from grace", "gözden düşmek", "idiom"),
    ("listen with rapt attention", "can kulağıyla dinlemek", "idiom"),
    ("be all ears", "can kulağıyla dinlemek, pürdikkat dinlemek", "idiom"),
    ("gentle words open iron gates", "tatlı dil yılanı deliğinden çıkarır", "proverb"),
    ("little drops make a mighty ocean", "damlaya damlaya göl olur", "proverb"),
    ("a friend in need is a friend indeed", "dost kara günde belli olur", "proverb"),
    ("where there is life, there is hope", "çıkmadık candan ümit kesilmez", "proverb"),
    ("once bitten, twice shy", "sütten ağzı yanan yoğurdu üfleyerek yer", "proverb"),
    ("unity is strength", "birlikten kuvvet doğar, nerede birlik orada dirlik", "proverb"),
    ("two heads are better than one", "akıl akıldan üstündür", "proverb"),
    ("a fish rots from the head down", "balık baştan kokar", "proverb"),
    ("look before you leap", "bin düşün bir söyle", "proverb")
]

# Expanded Turkish Idioms and Proverbs
ADDITIONAL_TURKISH_IDIOMS = [
    ("çocuk oyuncağı", "child's play, a piece of cake", "idiom"),
    ("çantada keklik", "in the bag, a piece of cake, a sure thing", "idiom"),
    ("ateş pahası", "cost an arm and a leg, exorbitant, daylight robbery", "idiom"),
    ("bir taşla iki kuş vurmak", "kill two birds with one stone", "idiom"),
    ("damlaya damlaya göl olur", "little drops make a mighty ocean, many a little makes a mickle", "proverb"),
    ("tatlı dil yılanı deliğinden çıkarır", "gentle words open iron gates, a soft answer turns away wrath", "proverb"),
    ("can kulağıyla dinlemek", "listen with rapt attention, be all ears", "idiom"),
    ("gözden düşmek", "fall from grace, lose favor", "idiom"),
    ("ayinesi iştir kişinin lafa bakılmaz", "actions speak louder than words", "proverb"),
    ("bardağı taşıran son damla", "the last straw, the straw that broke the camel's back", "idiom"),
    ("bardaktan boşanırcasına yağmak", "rain cats and dogs, pour down", "idiom"),
    ("başa gelen çekilir", "what can't be cured must be endured", "proverb"),
    ("bin düşün bir söyle", "look before you leap", "proverb"),
    ("birlikten kuvvet doğar", "unity is strength", "proverb"),
    ("boyundan büyük işe kalkışmak", "bite off more than one can chew", "idiom"),
    ("buzları eritmek", "break the ice", "idiom"),
    ("çıkmadık candan ümit kesilmez", "where there is life, there is hope", "proverb"),
    ("çığırından çıkmak", "get out of hand, get out of control", "idiom"),
    ("damdan düşer gibi", "out of the blue, out of nowhere", "idiom"),
    ("devede kulak", "a drop in the ocean, a drop in the bucket", "idiom"),
    ("dişini sıkmak", "bite the bullet, grit one's teeth", "idiom"),
    ("dost kara günde belli olur", "a friend in need is a friend indeed", "proverb"),
    ("erken kalkan yol alır", "the early bird catches the worm", "proverb"),
    ("etekleri zil çalmak", "be over the moon, be thrilled, jump for joy", "idiom"),
    ("et tırnaktan ayrılmaz", "blood is thicker than water", "proverb"),
    ("geç olsun güç olmasın", "better late than never", "proverb"),
    ("gemileri yakmak", "burn one's bridges", "idiom"),
    ("göz açıp kapayıncaya kadar", "in the blink of an eye", "idiom"),
    ("göz yummak", "turn a blind eye, overlook", "idiom"),
    ("göze girmek", "find favor, get into someone's good books", "idiom"),
    ("göze batmak", "stick out like a sore thumb", "idiom"),
    ("havlu atmak", "throw in the towel, concede defeat", "idiom"),
    ("haydan gelen huya gider", "easy come, easy go", "proverb"),
    ("her işte bir hayır vardır", "every cloud has a silver lining", "proverb"),
    ("iki yakayı bir araya getirmek", "make ends meet", "idiom"),
    ("işleyen demir ışıldar", "practice makes perfect", "proverb"),
    ("işleyen demir pas tutmaz", "a rolling stone gathers no moss", "proverb"),
    ("iti an çomağı hazırla", "speak of the devil", "proverb"),
    ("iyi günde kötü günde", "through thick and thin", "idiom"),
    ("kafayı vurup yatmak", "hit the sack", "idiom"),
    ("kafa bulmak", "pull someone's leg, tease", "idiom"),
    ("kıl payı", "by the skin of one's teeth, by a whisker", "idiom"),
    ("komşunun tavuğu komşuya kaz görünür", "the grass is always greener on the other side", "proverb"),
    ("küplere binmek", "hit the ceiling, fly into a rage", "idiom"),
    ("lafı dolandırmak", "beat around the bush", "idiom"),
    ("ne ekersen onu biçersin", "you reap what you sow", "proverb"),
    ("nerede birlik orada dirlik", "unity is strength", "proverb"),
    ("paydos etmek", "call it a day", "idiom"),
    ("pireyi deve yapmak", "make a mountain out of a molehill", "idiom"),
    ("sabır acıdır ama meyvesi tatlıdır", "patience is bitter, but its fruit is sweet", "proverb"),
    ("sakla samanı gelir zamanı", "keep a thing seven years and you will find a use for it", "proverb"),
    ("son pişmanlık fayda etmez", "there is no use crying over spilled milk", "proverb"),
    ("söz gümüşse sükut altındır", "silence is golden", "proverb"),
    ("suya sabuna dokunmamak", "sit on the fence, play it safe", "idiom"),
    ("sütten ağzı yanan yoğurdu üfleyerek yer", "once bitten, twice shy", "proverb"),
    ("taşı gediğine koymak", "hit the nail on the head", "idiom"),
    ("tencere yuvarlanmış kapağını bulmuş", "birds of a feather flock together", "proverb"),
    ("tereyağından kıl çeker gibi", "smooth as clockwork, like a knife through butter", "idiom"),
    ("uzun lafın kısası", "to make a long story short, in a nutshell", "idiom"),
    ("vakit nakittir", "time is money", "proverb"),
    ("yağmurdan kaçarken doluya tutulmak", "out of the frying pan into the fire", "proverb"),
    ("yaraya tuz basmak", "add insult to injury, rub salt in the wound", "idiom"),
    ("zahmetsiz rahmet olmaz", "no pain, no gain", "proverb"),
    ("zaman su gibi akıp geçiyor", "time flies", "idiom")
]

def clean_and_enrich():
    db_path = os.path.join(base_dir, "data", "dictionary.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("1. Cleaning fragmented junk possessives on multi-word Turkish entries...")
    cur.execute("""
        DELETE FROM bilingual 
        WHERE tr_lower LIKE '% %' 
        AND (en_lower LIKE "%'s" OR en_lower LIKE "%’s") 
        AND en_lower NOT LIKE '% %';
    """)
    deleted_poss = cur.rowcount
    print(f"   Deleted {deleted_poss} junk possessive rows.")

    print("2. Cleaning fragmented junk dangling hyphens...")
    cur.execute("""
        DELETE FROM bilingual 
        WHERE tr_lower LIKE '% %' 
        AND (en_lower LIKE '%-' OR en_lower LIKE '-%');
    """)
    deleted_hyphens = cur.rowcount
    print(f"   Deleted {deleted_hyphens} junk hyphen rows.")

    print("3. Cleaning corrupted single-word Proverb rows...")
    cur.execute("""
        DELETE FROM bilingual 
        WHERE category = 'Proverb' 
        AND en_lower NOT LIKE '% %';
    """)
    deleted_proverbs = cur.rowcount
    print(f"   Deleted {deleted_proverbs} corrupted proverb rows.")

    print("4. Enriching English Idioms & Proverbs...")
    all_en = ENGLISH_IDIOMS + ADDITIONAL_ENGLISH_IDIOMS
    added_en = 0
    updated_en = 0
    for en_phrase, tr_meanings, wtype in all_en:
        en_clean = en_phrase.strip()
        en_low = en_clean.lower()
        tr_clean = tr_meanings.strip()
        tr_low = turkish_lower(tr_clean.split(",")[0].strip())

        cur.execute("SELECT rowid, category FROM bilingual WHERE en_lower = ? AND tr_lower = ? LIMIT 1;", (en_low, tr_low))
        existing = cur.fetchone()
        if existing:
            rowid, cat = existing
            if cat not in ('Primary', 'Idioms & Proverbs'):
                cur.execute("UPDATE bilingual SET category = 'Idioms & Proverbs', type = ? WHERE rowid = ?;", (wtype, rowid))
                updated_en += 1
        else:
            cur.execute("""
                INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower)
                VALUES (?, ?, ?, 'Idioms & Proverbs', ?, ?);
            """, (en_clean, tr_clean, wtype, en_low, tr_low))
            added_en += 1

    print(f"   Added {added_en}, updated {updated_en} English idioms.")

    print("5. Enriching Turkish Idioms & Proverbs...")
    all_tr = TURKISH_IDIOMS + ADDITIONAL_TURKISH_IDIOMS
    added_tr = 0
    updated_tr = 0
    for tr_phrase, en_meanings, wtype in all_tr:
        tr_clean = tr_phrase.strip()
        tr_low = turkish_lower(tr_clean)
        en_clean = en_meanings.strip()
        en_low = en_clean.split(",")[0].strip().lower()

        cur.execute("SELECT rowid, category FROM bilingual WHERE tr_lower = ? AND en_lower = ? LIMIT 1;", (tr_low, en_low))
        existing = cur.fetchone()
        if existing:
            rowid, cat = existing
            if cat not in ('Primary', 'Idioms & Proverbs'):
                cur.execute("UPDATE bilingual SET category = 'Idioms & Proverbs', type = ? WHERE rowid = ?;", (wtype, rowid))
                updated_tr += 1
        else:
            cur.execute("""
                INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower)
                VALUES (?, ?, ?, 'Idioms & Proverbs', ?, ?);
            """, (en_clean, tr_clean, wtype, en_low, tr_low))
            added_tr += 1

    print(f"   Added {added_tr}, updated {updated_tr} Turkish idioms.")

    print("6. Verifying 'bekar' -> 'single' is ranked #1 Primary...")
    cur.execute("SELECT 1 FROM bilingual WHERE tr_lower = 'bekar' AND en_lower = 'single';")
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower)
            VALUES ('single', 'bekar', 'adj.', 'Primary', 'single', 'bekar');
        """)
    else:
        cur.execute("UPDATE bilingual SET category = 'Primary' WHERE tr_lower = 'bekar' AND en_lower = 'single';")

    conn.commit()
    conn.close()
    print("Clean and enrich completed successfully!")

if __name__ == "__main__":
    clean_and_enrich()
