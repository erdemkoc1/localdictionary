import os
import sys
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

# Ensure imports work
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from src.utils import turkish_lower

# Top English -> Turkish Idioms & Proverbs
ENGLISH_IDIOMS = [
    ("a blessing in disguise", "her şerde bir hayır vardır", "proverb"),
    ("a dime a dozen", "bini bir para, pek çok, değersiz", "idiom"),
    ("a piece of cake", "çocuk oyuncağı, tereyağından kıl çeker gibi", "idiom"),
    ("piece of cake", "çantada keklik, çocuk oyuncağı", "idiom"),
    ("actions speak louder than words", "ayinesi iştir kişinin lafa bakılmaz", "proverb"),
    ("add insult to injury", "yaraya tuz basmak, yangına körükle gitmek", "idiom"),
    ("all in the same boat", "aynı gemide olmak", "idiom"),
    ("an arm and a leg", "dünyanın parası, ateş pahası", "idiom"),
    ("cost an arm and a leg", "ateş pahası olmak, çok pahalıya patlamak", "idiom"),
    ("costs an arm and a leg", "ateş pahası, çok pahalı", "idiom"),
    ("at the drop of a hat", "kaşla göz arasında, tereddütsüz", "idiom"),
    ("back to square one", "sil baştan, başa dönmek", "idiom"),
    ("back to the drawing board", "sil baştan başlamak, yeni bir plan yapmak", "idiom"),
    ("barking up the wrong tree", "yanlış kapıyı çalmak, yanlış hedefe yönelmek", "idiom"),
    ("beat around the bush", "lafı dolandırmak, eveleyip gevelemek", "idiom"),
    ("better late than never", "geç olsun güç olmasın", "proverb"),
    ("bite off more than you can chew", "boyundan büyük işe kalkışmak", "idiom"),
    ("bite the bullet", "dişini sıkmak, acı ilacı içmek", "idiom"),
    ("bite the dust", "nalları dikmek, boylu boyunca serilmek", "idiom"),
    ("break a leg", "şeytanın bacağını kır, bol şans, iyi şanslar", "idiom"),
    ("break the ice", "buzları eritmek, ortamı yumuşatmak", "idiom"),
    ("burn bridges", "gemileri yakmak, geri dönüşü olmayan adım atmak", "idiom"),
    ("burn the candle at both ends", "kendini çok yıpratmak, gece gündüz çalışmak", "idiom"),
    ("burn the midnight oil", "gece gündüz çalışmak, sabahlamak", "idiom"),
    ("by the skin of your teeth", "kıl payı, ucu ucuna", "idiom"),
    ("call it a day", "paydos etmek, bugünlük bu kadar demek", "idiom"),
    ("calm before the storm", "fırtına öncesi sessizlik", "idiom"),
    ("can't judge a book by its cover", "görünüşe aldanmamak gerekir", "proverb"),
    ("you can't judge a book by its cover", "görünüşe aldanmamak gerekir", "proverb"),
    ("caught red-handed", "suçüstü yakalanmak", "idiom"),
    ("cross that bridge when you come to it", "zamanı gelince düşünürüz, dereyi görmeden paçaları sıvama", "proverb"),
    ("cry over spilled milk", "son pişmanlık fayda etmez", "proverb"),
    ("cry over spilt milk", "son pişmanlık fayda etmez", "proverb"),
    ("cry wolf", "yalancı çobanlık yapmak", "idiom"),
    ("curiosity killed the cat", "fazla merak başa bela getirir", "proverb"),
    ("cut corners", "kolaya kaçmak, baştan savma yapmak", "idiom"),
    ("devil's advocate", "şeytanın avukatı", "idiom"),
    ("play devil's advocate", "şeytanın avukatlığını yapmak", "idiom"),
    ("don't put all your eggs in one basket", "bütün yumurtaları aynı sepete koyma", "proverb"),
    ("down to earth", "ayakları yere basan, mütevazı", "idiom"),
    ("easy come, easy go", "haydan gelen huya gider", "proverb"),
    ("elephant in the room", "herkesin bildiği ama kimsenin konuşmadığı sorun", "idiom"),
    ("every cloud has a silver lining", "her işte bir hayır vardır", "proverb"),
    ("face the music", "sonuçlarına katlanmak, cezasını çekmek", "idiom"),
    ("get a taste of your own medicine", "ettiğini bulmak, kendi kazdığı kuyuya düşmek", "idiom"),
    ("get out of hand", "çığırından çıkmak, kontrolden çıkmak", "idiom"),
    ("give someone the benefit of the doubt", "iyi niyetli olduğunu kabul etmek", "idiom"),
    ("give someone the cold shoulder", "soğuk davranmak, yüz vermemek", "idiom"),
    ("go the extra mile", "elinden gelenin fazlasını yapmak", "idiom"),
    ("grass is always greener on the other side", "komşunun tavuğu komşuya kaz görünür", "proverb"),
    ("hear on the grapevine", "kulağına çalınmak, fısıltı gazetesinden duymak", "idiom"),
    ("hear through the grapevine", "kulağına çalınmak, fısıltı gazetesinden duymak", "idiom"),
    ("hit the books", "harıl harıl ders çalışmak", "idiom"),
    ("hit the nail on the head", "tam üstüne basmak, taşı gediğine koymak", "idiom"),
    ("hit the sack", "kafayı vurup yatmak", "idiom"),
    ("in hot water", "başı dertte olmak", "idiom"),
    ("in the blink of an eye", "göz açıp kapayıncaya kadar", "idiom"),
    ("it takes two to tango", "tek elle alkış tutulmaz, kabahat iki tarafta da olur", "proverb"),
    ("it's not rocket science", "atla deve değil, çok karmaşık bir şey değil", "idiom"),
    ("jump on the bandwagon", "modaya uymak, sürüye katılmak", "idiom"),
    ("keep an eye on", "göz kulak olmak", "idiom"),
    ("kill two birds with one stone", "bir taşla iki kuş vurmak", "idiom"),
    ("last straw", "bardağı taşıran son damla", "idiom"),
    ("the last straw", "bardağı taşıran son damla", "idiom"),
    ("leave no stone unturned", "altını üstüne getirmek, her çareye başvurmak", "idiom"),
    ("let sleeping dogs lie", "uyuyan devi uyandırma, eski defterleri açma", "proverb"),
    ("let the cat out of the bag", "baklayı ağzından çıkarmak, sırrı ifşa etmek", "idiom"),
    ("look before you leap", "bin düşün bir söyle, temkinli ol", "proverb"),
    ("make ends meet", "iki yakayı bir araya getirmek", "idiom"),
    ("miss the boat", "treni kaçırmak, fırsatı kaçırmak", "idiom"),
    ("no pain, no gain", "zahmetsiz rahmet olmaz, emeksiz yemek olmaz", "proverb"),
    ("not my cup of tea", "benim harcım değil, bana göre değil", "idiom"),
    ("on cloud nine", "havalara uçmak, etekleri zil çalmak", "idiom"),
    ("on the fence", "kararsız, arafta olmak", "idiom"),
    ("once in a blue moon", "ayda yılda bir, kırk yılda bir", "idiom"),
    ("out of the blue", "damdan düşer gibi, ansızın, gökten iner gibi", "idiom"),
    ("penny for your thoughts", "kara kara ne düşünüyorsun", "idiom"),
    ("practice makes perfect", "işleyen demir ışıldar, tekrar mükemmelleştirir", "proverb"),
    ("pull someone's leg", "biriyle kafa bulmak, dalga geçmek", "idiom"),
    ("raining cats and dogs", "bardaktan boşanırcasına yağmur yağmak", "idiom"),
    ("ring a bell", "tanıdık gelmek, anımsatmak", "idiom"),
    ("rule of thumb", "göz kararı, pratik kural", "idiom"),
    ("see eye to eye", "hemfikir olmak, aynı görüşte olmak", "idiom"),
    ("spill the beans", "ağzındaki baklayı çıkarmak, sırrı açık etmek", "idiom"),
    ("steal someone's thunder", "rol çalmak, başkasının başarısına gölge düşürmek", "idiom"),
    ("straight from the horse's mouth", "ilk ağızdan, yetkili kaynaktan", "idiom"),
    ("take it with a grain of salt", "şüpheyle yaklaşmak, ihtiyatla karşılamak", "idiom"),
    ("take with a grain of salt", "şüpheyle yaklaşmak, ihtiyatla karşılamak", "idiom"),
    ("the ball is in your court", "sıra sende, top sende", "idiom"),
    ("the best of both worlds", "hem nalına hem mıhına, iki tarafın da avantajını kullanmak", "idiom"),
    ("the early bird catches the worm", "erken kalkan yol alır", "proverb"),
    ("through thick and thin", "iyi günde kötü günde, her koşulda", "idiom"),
    ("throw in the towel", "havlu atmak, yenilgiyi kabul etmek", "idiom"),
    ("time flies", "zaman su gibi akıp geçiyor", "idiom"),
    ("turn a blind eye", "göz yummak, görmezden gelmek", "idiom"),
    ("under the weather", "keyifsiz, halsiz, hafif rahatsız", "idiom"),
    ("weather the storm", "fırtınayı atlatmak, zorlukların üstesinden gelmek", "idiom"),
    ("when in Rome, do as the Romans do", "nereye gidersen oranın adetine uy", "proverb"),
    ("wrap one's head around", "aklı ermek, kafası basmak", "idiom"),
    ("you reap what you sow", "ne ekersen onu biçersin", "proverb"),
    ("zero in on", "odaklanmak, hedefe kilitlenmek", "idiom")
]

# Top Turkish -> English Idioms & Proverbs
TURKISH_IDIOMS = [
    ("ağzı kulaklarına varmak", "grin from ear to ear, be thrilled", "idiom"),
    ("akıl akıldan üstündür", "two heads are better than one", "proverb"),
    ("ateş pahası", "cost an arm and a leg, exorbitant, very expensive", "idiom"),
    ("ayda yılda bir", "once in a blue moon, very rarely", "idiom"),
    ("ayinesi iştir kişinin lafa bakılmaz", "actions speak louder than words", "proverb"),
    ("balık baştan kokar", "a fish rots from the head down", "proverb"),
    ("bardağı taşıran son damla", "the last straw, the straw that broke the camel's back", "idiom"),
    ("bardaktan boşanırcasına yağmak", "rain cats and dogs, pour down", "idiom"),
    ("başa gelen çekilir", "what can't be cured must be endured", "proverb"),
    ("bekara karı boşamak kolay", "talk is cheap, easier said than done", "proverb"),
    ("bin düşün bir söyle", "look before you leap", "proverb"),
    ("bir elin nesi var iki elin sesi var", "many hands make light work, unity is strength", "proverb"),
    ("bir taşla iki kuş vurmak", "kill two birds with one stone", "idiom"),
    ("boyundan büyük işe kalkışmak", "bite off more than one can chew", "idiom"),
    ("burun kıvırmak", "turn up one's nose, look down upon", "idiom"),
    ("buzları eritmek", "break the ice", "idiom"),
    ("can kulağıyla dinlemek", "listen with rapt attention, be all ears", "idiom"),
    ("çantada keklik", "in the bag, a sure thing, a piece of cake", "idiom"),
    ("çamur atmak", "sling mud, cast aspersions", "idiom"),
    ("çıkmadık candan ümit kesilmez", "where there is life, there is hope", "proverb"),
    ("çığırından çıkmak", "get out of hand, get out of control", "idiom"),
    ("çocuk oyuncağı", "child's play, a piece of cake", "idiom"),
    ("damlaya damlaya göl olur", "many a little makes a mickle, little drops make a mighty ocean", "proverb"),
    ("damdan düşer gibi", "out of the blue, out of nowhere, unexpectedly", "idiom"),
    ("devede kulak", "a drop in the ocean, a drop in the bucket", "idiom"),
    ("dillere destan olmak", "become legendary, become the talk of the town", "idiom"),
    ("dişini sıkmak", "bite the bullet, grit one's teeth", "idiom"),
    ("dost kara günde belli olur", "a friend in need is a friend indeed", "proverb"),
    ("eli kulağında", "imminent, just around the corner", "idiom"),
    ("elinden gelenin fazlasını yapmak", "go the extra mile", "idiom"),
    ("erken kalkan yol alır", "the early bird catches the worm", "proverb"),
    ("etekleri zil çalmak", "be over the moon, be thrilled, jump for joy", "idiom"),
    ("et tırnaktan ayrılmaz", "blood is thicker than water", "proverb"),
    ("eveleyip gevelemek", "beat around the bush", "idiom"),
    ("evdeki hesap çarşıya uymaz", "the best-laid plans often go awry", "proverb"),
    ("fırtına öncesi sessizlik", "calm before the storm", "idiom"),
    ("geç olsun güç olmasın", "better late than never", "proverb"),
    ("gemileri yakmak", "burn one's bridges, burn one's boats", "idiom"),
    ("göz açıp kapayıncaya kadar", "in the blink of an eye", "idiom"),
    ("göz gezdirmek", "browse, cast an eye over, skim through", "idiom"),
    ("göz yummak", "turn a blind eye, overlook, condone", "idiom"),
    ("gözden düşmek", "fall from grace, lose favor, be discredited", "idiom"),
    ("göze batmak", "stick out like a sore thumb", "idiom"),
    ("göze girmek", "find favor, get into someone's good books", "idiom"),
    ("gülme komşuna gelir başına", "he who laughs last laughs best", "proverb"),
    ("havadan sudan konuşmak", "make small talk, shoot the breeze", "idiom"),
    ("havlu atmak", "throw in the towel, concede defeat", "idiom"),
    ("haydan gelen huya gider", "easy come, easy go", "proverb"),
    ("her işte bir hayır vardır", "every cloud has a silver lining, all happens for the best", "proverb"),
    ("içi içine sığmamak", "be bursting with excitement", "idiom"),
    ("iki yakayı bir araya getirmek", "make ends meet", "idiom"),
    ("ipe un sermek", "drag one's feet, find flimsy excuses", "idiom"),
    ("işleyen demir pas tutmaz", "practice makes perfect, a rolling stone gathers no moss", "proverb"),
    ("iti an çomağı hazırla", "speak of the devil", "proverb"),
    ("iyi günde kötü günde", "through thick and thin, for better or for worse", "idiom"),
    ("kafa bulmak", "pull someone's leg, tease", "idiom"),
    ("kafayı vurup yatmak", "hit the sack", "idiom"),
    ("kaş yaparken göz çıkarmak", "do more harm than good", "idiom"),
    ("kendi kazdığı kuyuya düşmek", "fall into one's own trap, hoist with one's own petard", "idiom"),
    ("kıl payı", "by the skin of one's teeth, by a whisker", "idiom"),
    ("komşunun tavuğu komşuya kaz görünür", "the grass is always greener on the other side", "proverb"),
    ("kulağına küpe olmak", "be a lesson to remember", "idiom"),
    ("küplere binmek", "hit the ceiling, fly into a rage", "idiom"),
    ("lafı dolandırmak", "beat around the bush", "idiom"),
    ("meyve veren ağaç taşlanır", "a fruitful tree is stoned, success breeds envy", "proverb"),
    ("ne ekersen onu biçersin", "you reap what you sow", "proverb"),
    ("nerede birlik orada dirlik", "unity is strength", "proverb"),
    ("paydos etmek", "call it a day", "idiom"),
    ("pireyi deve yapmak", "make a mountain out of a molehill", "idiom"),
    ("sabır acıdır ama meyvesi tatlıdır", "patience is bitter, but its fruit is sweet", "proverb"),
    ("sakla samanı gelir zamanı", "keep a thing seven years and you will find a use for it", "proverb"),
    ("saman altından su yürütmek", "act slyly, pull strings behind the scenes", "idiom"),
    ("sineğin yağını çıkarmak", "skin a flint, squeeze water from a stone", "idiom"),
    ("son pişmanlık fayda etmez", "there is no use crying over spilled milk", "proverb"),
    ("söz gümüşse sükut altındır", "silence is golden", "proverb"),
    ("suya sabuna dokunmamak", "sit on the fence, play it safe", "idiom"),
    ("tatlı dil yılanı deliğinden çıkarır", "gentle words open iron gates, a soft answer turns away wrath", "proverb"),
    ("tencere yuvarlanmış kapağını bulmuş", "birds of a feather flock together", "proverb"),
    ("tereyağından kıl çeker gibi", "smooth as clockwork, without a hitch, like a knife through butter", "idiom"),
    ("uzun lafın kısası", "to make a long story short, in a nutshell", "idiom"),
    ("vakit nakittir", "time is money", "proverb"),
    ("yağmurdan kaçarken doluya tutulmak", "out of the frying pan into the fire", "proverb"),
    ("yanlış hesap Bağdat'tan döner", "it is never too late to turn back from an error", "proverb"),
    ("yaraya tuz basmak", "add insult to injury, rub salt in the wound", "idiom"),
    ("yolun açık olsun", "have a safe trip, godspeed", "idiom"),
    ("zahmetsiz rahmet olmaz", "no pain, no gain", "proverb"),
    ("zaman su gibi akıp geçiyor", "time flies", "idiom"),
    ("zurnanın zırt dediği yer", "the crunch point, where the shoe pinches", "idiom")
]

def add_idioms():
    db_path = os.path.join(base_dir, "data", "dictionary.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    added_en = 0
    added_tr = 0

    print("Checking and adding English idioms...")
    for en_phrase, tr_meanings, wtype in ENGLISH_IDIOMS:
        en_clean = en_phrase.strip()
        en_low = en_clean.lower()
        
        # Check if already exists with same exact phrase
        cur.execute("SELECT 1 FROM bilingual WHERE en_lower = ? LIMIT 1;", (en_low,))
        if not cur.fetchone():
            tr_primary = tr_meanings.split(",")[0].strip()
            cur.execute("""
                INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower)
                VALUES (?, ?, ?, 'Idioms & Proverbs', ?, ?);
            """, (en_clean, tr_meanings, wtype, en_low, turkish_lower(tr_primary)))
            added_en += 1

    print("Checking and adding Turkish idioms...")
    for tr_phrase, en_meanings, wtype in TURKISH_IDIOMS:
        tr_clean = tr_phrase.strip()
        tr_low = turkish_lower(tr_clean)

        # Check if already exists
        cur.execute("SELECT 1 FROM bilingual WHERE tr_lower = ? LIMIT 1;", (tr_low,))
        if not cur.fetchone():
            en_primary = en_meanings.split(",")[0].strip()
            cur.execute("""
                INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower)
                VALUES (?, ?, ?, 'TDK Atasözleri ve Deyimler', ?, ?);
            """, (en_meanings, tr_clean, wtype, en_primary.lower(), tr_low))
            added_tr += 1

    conn.commit()
    conn.close()
    print(f"Done! Added {added_en} English idioms and {added_tr} Turkish idioms without duplicates.")

if __name__ == "__main__":
    add_idioms()
