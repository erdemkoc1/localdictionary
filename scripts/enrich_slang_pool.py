import os
import sys
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.utils import turkish_lower

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "dictionary.db"))

SLANG_ENTRIES = [
    # English -> Turkish
    ("fuck", "sikmek, siktir, kahretsin", "v./excl.", "Argo / Sokak Dili"),
    ("fucking", "lanet, amına koyduğumun, kahrolası", "adj./adv.", "Argo / Sokak Dili"),
    ("fuck off", "siktir git, defol git, toz ol", "excl.", "Argo / Sokak Dili"),
    ("get the fuck out", "siktir git, derhal defol", "excl.", "Argo / Sokak Dili"),
    ("what the fuck", "bu da ne amk, ne sikim, ne oluyor lan", "excl.", "Argo / Sokak Dili"),
    ("wtf", "bu da ne amk, ne sikim", "excl.", "Argo / Sokak Dili"),
    ("shit", "bok, kahretsin, hasiktir", "n./excl.", "Argo / Sokak Dili"),
    ("holy shit", "hasiktir, vay anasını, aman tanrım", "excl.", "Argo / Sokak Dili"),
    ("bullshit", "saçmalık, palavra, bok püsür", "n./excl.", "Argo / Sokak Dili"),
    ("cut the crap", "boş yapmayı kes, zırvalamayı bırak", "idiom", "Argo / Sokak Dili"),
    ("damn", "kahretsin, lanet olsun", "excl.", "Argo / Sokak Dili"),
    ("damn it", "kahretsin, lanet olsun", "excl.", "Argo / Sokak Dili"),
    ("dammit", "kahretsin, lanet olsun", "excl.", "Argo / Sokak Dili"),
    ("bitch", "orospu, kaltak, sürtük", "n.", "Argo / Sokak Dili"),
    ("son of a bitch", "orospu çocuğu, it oğlu it", "idiom/excl.", "Argo / Sokak Dili"),
    ("asshole", "göt lalesi, pislik, yavşak", "n.", "Argo / Sokak Dili"),
    ("bastard", "piç, alçak, hayırsız", "n.", "Argo / Sokak Dili"),
    ("dick", "sik, hıyar, pislik herif", "n.", "Argo / Sokak Dili"),
    ("dickhead", "sik kafalı, hıyar", "n.", "Argo / Sokak Dili"),
    ("cunt", "amcık, aşağılık pislik", "n.", "Argo / Sokak Dili"),
    ("dumbass", "geri zekalı, dangalak, salak", "n.", "Argo / Sokak Dili"),
    ("badass", "taşaklı, havalı, sıkı herif", "n./adj.", "Argo / Sokak Dili"),
    ("motherfucker", "orospu çocuğu, anasını siktiğim", "n./excl.", "Argo / Sokak Dili"),
    ("piss off", "defol git, canımı sıkma", "v./excl.", "Argo / Sokak Dili"),
    ("pissed off", "tepesi atmış, çok öfkeli, zıvanadan çıkmış", "adj.", "Argo / Sokak Dili"),
    ("suck", "berbat olmak, rezalet olmak", "v.", "Argo / Sokak Dili"),
    ("sucks", "berbat, rezalet, çekilmez", "adj./v.", "Argo / Sokak Dili"),
    ("screw up", "sıçıp sıvamak, berbat etmek, batırmak", "v.", "Argo / Sokak Dili"),
    ("screw you", "canın cehenneme, defol", "excl.", "Argo / Sokak Dili"),
    ("shut the fuck up", "çeneni siktiğimin kapa, kes sesini amk", "excl.", "Argo / Sokak Dili"),
    ("shut up", "kapa çeneni, sus, kes sesini", "excl.", "Argo / Sokak Dili"),
    ("crap", "çöp, boktan şey, zırva", "n.", "Argo / Sokak Dili"),
    ("freaking", "lanet olası, acayip", "adj./adv.", "Argo / Sokak Dili"),
    ("loser", "ezik, zavallı, sümsük", "n.", "Argo / Sokak Dili"),
    ("noob", "çaylak, acemi, toy", "n.", "Argo / Sokak Dili"),
    ("dude", "moruk, kanka, birader", "n.", "Argo / Sokak Dili"),
    ("bro", "birader, kanka, dostum", "n.", "Argo / Sokak Dili"),
    ("homie", "kanka, mahalle arkadaşı", "n.", "Argo / Sokak Dili"),
    ("chill out", "sakinleş, rahatla, kafana takma", "v.", "Argo / Sokak Dili"),
    ("calm the fuck down", "sakinleş amk, bir dur lan", "excl.", "Argo / Sokak Dili"),
    ("hang out", "takılmak, takılıp eğlenmek", "v.", "Argo / Sokak Dili"),
    ("rip off", "kazık, dolandırıcılık, fahiş fiyat", "n./v.", "Argo / Sokak Dili"),
    ("no cap", "harbi, yalan yok, yeminle", "slang/adv.", "Argo / Sokak Dili"),
    ("bite me", "çok da umrumda, hadi ordan", "excl.", "Argo / Sokak Dili"),
    ("drop dead", "geber, yok ol", "excl.", "Argo / Sokak Dili"),
    ("kiss my ass", "kıçımı ye, nah sana", "excl.", "Argo / Sokak Dili"),
    ("go to hell", "cehenneme git, cehennemin dibine git", "excl.", "Argo / Sokak Dili"),
    ("who the fuck", "kim ulan, kim lan bu", "phrase", "Argo / Sokak Dili"),
    ("why the fuck", "neden amk, niye lan", "phrase", "Argo / Sokak Dili"),
    ("how the fuck", "nasıl lan, nasıl olur amk", "phrase", "Argo / Sokak Dili"),
    ("where the fuck", "nerede lan, nerede amk", "phrase", "Argo / Sokak Dili"),
    ("don't give a fuck", "zerre umrumda değil, sikimde değil", "idiom", "Argo / Sokak Dili"),
    ("don't give a shit", "zerre umrumda değil, sikimde değil", "idiom", "Argo / Sokak Dili"),

    # Turkish -> English
    ("siktir", "fuck, damn, get lost", "excl.", "Argo / Sokak Dili"),
    ("siktir git", "fuck off, get the fuck out, beat it", "excl.", "Argo / Sokak Dili"),
    ("siktir ol git", "get the fuck out, fuck off", "excl.", "Argo / Sokak Dili"),
    ("hasiktir", "holy shit, fuck, no way", "excl.", "Argo / Sokak Dili"),
    ("amk", "wtf, for fuck's sake, damn it", "excl.", "Argo / Sokak Dili"),
    ("aq", "wtf, damn, for fuck's sake", "excl.", "Argo / Sokak Dili"),
    ("lan", "dude, man, bro, hey", "excl.", "Argo / Sokak Dili"),
    ("ula", "hey you, man", "excl.", "Argo / Sokak Dili"),
    ("lanet olsun", "damn it, curse it", "excl.", "Argo / Sokak Dili"),
    ("kahretsin", "damn it, damn, blast it", "excl.", "Argo / Sokak Dili"),
    ("bok", "shit, crap, feces", "n.", "Argo / Sokak Dili"),
    ("boktan", "shitty, crappy, awful", "adj.", "Argo / Sokak Dili"),
    ("boka sarmak", "go down the toilet, go to shit, deteriorate", "idiom", "Argo / Sokak Dili"),
    ("sıçmak", "shit, fuck up, screw up", "v.", "Argo / Sokak Dili"),
    ("sıçıp batırmak", "fuck up completely, screw up big time", "idiom", "Argo / Sokak Dili"),
    ("kafayı yemek", "lose one's mind, freak out, go crazy", "idiom", "Argo / Sokak Dili"),
    ("kafayı sıyırmak", "go nuts, lose one's marbles", "idiom", "Argo / Sokak Dili"),
    ("boş yapma", "cut the crap, don't talk shit, stop rambling", "idiom", "Argo / Sokak Dili"),
    ("salla", "forget it, brush it off, whatever", "idiom", "Argo / Sokak Dili"),
    ("yavşak", "asshole, slimeball, jerk", "n.", "Argo / Sokak Dili"),
    ("piç", "bastard, prick, rascal", "n.", "Argo / Sokak Dili"),
    ("orospu", "bitch, whore, slut", "n.", "Argo / Sokak Dili"),
    ("orospu çocuğu", "son of a bitch, motherfucker", "idiom/excl.", "Argo / Sokak Dili"),
    ("it oğlu it", "son of a bitch, scoundrel", "idiom", "Argo / Sokak Dili"),
    ("mal", "idiot, dumbass, fool", "n./adj.", "Argo / Sokak Dili"),
    ("hıyar", "jerk, moron, boor", "n.", "Argo / Sokak Dili"),
    ("dingil", "jerk, fool, dimwit", "n.", "Argo / Sokak Dili"),
    ("dangalak", "dumbass, blockhead, fool", "n.", "Argo / Sokak Dili"),
    ("salak", "idiot, moron, stupid", "n./adj.", "Argo / Sokak Dili"),
    ("aptal", "stupid, foolish, idiot", "adj./n.", "Argo / Sokak Dili"),
    ("çuvallamak", "screw up, mess up, fail miserably", "v.", "Argo / Sokak Dili"),
    ("kanka", "bro, buddy, pal, bestie", "n.", "Argo / Sokak Dili"),
    ("moruk", "old timer, dude, bro", "n.", "Argo / Sokak Dili"),
    ("kafa dengi", "cool, like-minded, easygoing", "adj.", "Argo / Sokak Dili"),
    ("yok artık", "no way, unbelievable, get out of here", "excl.", "Argo / Sokak Dili"),
    ("hadi ordan", "get out of here, nonsense, baloney", "excl.", "Argo / Sokak Dili"),
    ("çakma", "fake, knockoff, counterfeit", "adj.", "Argo / Sokak Dili"),
    ("kazık", "rip-off, overly expensive, highway robbery", "n./adj.", "Argo / Sokak Dili"),
    ("kazıklamak", "rip off, overcharge, fleece", "v.", "Argo / Sokak Dili"),
    ("tüymek", "bail out, run away, skedaddle", "v.", "Argo / Sokak Dili"),
    ("kıyak", "awesome, generous, great favor", "adj./n.", "Argo / Sokak Dili")
]

def enrich_database():
    if not os.path.exists(DB_PATH):
        print(f"HATA: {DB_PATH} bulunamadı!")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted_count = 0
    for src, tgt, pos, cat in SLANG_ENTRIES:
        # Determine direction: if src has Turkish chars or is in TR slang list
        # Check both ways
        en_word = src
        tr_word = tgt
        en_lower = turkish_lower(en_word)
        tr_lower = turkish_lower(tr_word)

        # Insert as top priority Common Usage / Argo
        cur.execute("""
            INSERT OR REPLACE INTO bilingual (en, tr, type, category, en_lower, tr_lower)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (en_word, tr_word, pos, cat, en_lower, tr_lower))
        inserted_count += 1

    conn.commit()
    conn.close()
    print(f"BAŞARILI: {inserted_count} argo, sokak dili ve küfür kaydı dictionary.db'ye işlendi!")

if __name__ == "__main__":
    enrich_database()
