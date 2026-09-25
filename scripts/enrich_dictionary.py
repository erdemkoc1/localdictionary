import os
import sys
import re
import sqlite3
import xml.etree.ElementTree as ET
from typing import Set, Tuple, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.utils import turkish_lower

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "dictionary.db"))
ENG_TUR_TEI = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "eng-tur.tei"))
TUR_ENG_TEI = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "tur-eng.tei"))
WIKTIONARY_TSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "wiktionary_tr_en.tsv"))

def clean_text(s: str) -> str:
    if not s:
        return ""
    # Remove HTML tags
    s = re.sub(r"<[^>]+>", "", s)
    # Remove excess whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s

def load_existing_pairs(conn: sqlite3.Connection) -> Set[Tuple[str, str]]:
    print("Mevcut ikili kayıtlar hafızaya yükleniyor...")
    cur = conn.cursor()
    cur.execute("SELECT en_lower, tr_lower FROM bilingual")
    existing = set(cur.fetchall())
    print(f"Toplam {len(existing):,} mevcut çift yüklendi.")
    return existing

def parse_freedict_eng_tur(existing: Set[Tuple[str, str]]) -> List[Tuple[str, str, str, str, str, str]]:
    print("FreeDict English-Turkish işleniyor...")
    if not os.path.exists(ENG_TUR_TEI):
        print("FreeDict eng-tur.tei bulunamadı, atlanıyor.")
        return []

    tree = ET.parse(ENG_TUR_TEI)
    root = tree.getroot()
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    new_rows = []

    for entry in root.findall(".//tei:entry", ns):
        orth = entry.find(".//tei:orth", ns)
        if orth is None or not orth.text:
            continue
        en_word = clean_text(orth.text)
        if not en_word or len(en_word) > 100:
            continue
        en_lower = turkish_lower(en_word)

        # Get part of speech if present
        pos = entry.find(".//tei:pos", ns)
        pos_text = pos.text.strip() if pos is not None and pos.text else "-"

        # Get translations
        for quote in entry.findall(".//tei:quote", ns):
            if quote.text and quote.text.strip():
                tr_word = clean_text(quote.text)
                if not tr_word or len(tr_word) > 150:
                    continue
                tr_lower = turkish_lower(tr_word)
                if (en_lower, tr_lower) not in existing:
                    new_rows.append((en_word, tr_word, pos_text, "FreeDict", en_lower, tr_lower))
                    existing.add((en_lower, tr_lower))

    print(f"FreeDict'ten {len(new_rows):,} yeni çift çıkarıldı.")
    return new_rows

def parse_freedict_tur_eng(existing: Set[Tuple[str, str]]) -> List[Tuple[str, str, str, str, str, str]]:
    print("FreeDict Turkish-English işleniyor...")
    if not os.path.exists(TUR_ENG_TEI):
        print("FreeDict tur-eng.tei bulunamadı, atlanıyor.")
        return []

    tree = ET.parse(TUR_ENG_TEI)
    root = tree.getroot()
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    new_rows = []

    for entry in root.findall(".//tei:entry", ns):
        orth = entry.find(".//tei:orth", ns)
        if orth is None or not orth.text:
            continue
        tr_word = clean_text(orth.text)
        if not tr_word or len(tr_word) > 100:
            continue
        tr_lower = turkish_lower(tr_word)

        pos = entry.find(".//tei:pos", ns)
        pos_text = pos.text.strip() if pos is not None and pos.text else "-"

        for quote in entry.findall(".//tei:quote", ns):
            if quote.text and quote.text.strip():
                en_word = clean_text(quote.text)
                if not en_word or len(en_word) > 150:
                    continue
                en_lower = turkish_lower(en_word)
                if (en_lower, tr_lower) not in existing:
                    new_rows.append((en_word, tr_word, pos_text, "FreeDict", en_lower, tr_lower))
                    existing.add((en_lower, tr_lower))

    print(f"FreeDict TR-EN'den {len(new_rows):,} yeni çift çıkarıldı.")
    return new_rows

def parse_wiktionary_tr_en(existing: Set[Tuple[str, str]]) -> List[Tuple[str, str, str, str, str, str]]:
    print("Wiktionary Turkish-English çekim ve kök çiftleri işleniyor...")
    if not os.path.exists(WIKTIONARY_TSV):
        print("wiktionary_tr_en.tsv bulunamadı, atlanıyor.")
        return []

    new_rows = []
    seen_inflections = set()

    with open(WIKTIONARY_TSV, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "\t" not in line:
                continue
            words_part, html_part = line.split("\t", 1)
            forms = [w.strip() for w in words_part.split("|") if w.strip()]
            if not forms:
                continue

            # Extract POS
            pos_match = re.search(r"<i>(.*?)</i>", html_part)
            pos_str = pos_match.group(1).strip() if pos_match else "word"

            # Extract meanings
            meanings = re.findall(r"<li>(.*?)</li>", html_part)
            clean_meanings = []
            for m in meanings:
                m_clean = clean_text(m)
                if m_clean and len(m_clean) < 150:
                    clean_meanings.append(m_clean)

            if not clean_meanings:
                continue

            primary_meaning = "; ".join(clean_meanings[:2])
            headword = forms[0]
            head_lower = turkish_lower(headword)
            mean_lower = turkish_lower(primary_meaning)

            # 1. Add headword
            if (mean_lower, head_lower) not in existing:
                new_rows.append((primary_meaning, headword, pos_str, "Wiktionary", mean_lower, head_lower))
                existing.add((mean_lower, head_lower))

            # 2. Add inflected forms (up to 25 common forms per headword to avoid bloat)
            for form in forms[1:26]:
                if len(form) < 2 or len(form) > 35 or form in seen_inflections:
                    continue
                # Skip strange symbols
                if any(c in form for c in "<>{}[]@#$%^&*=+"):
                    continue

                seen_inflections.add(form)
                form_lower = turkish_lower(form)
                
                # Contextualized target meaning for inflected form
                inf_target = f"{primary_meaning} (Kök: {headword})"
                inf_target_lower = turkish_lower(inf_target)

                if (inf_target_lower, form_lower) not in existing:
                    new_rows.append((inf_target, form, f"{pos_str} (çekim)", "Wiktionary / Çekim", inf_target_lower, form_lower))
                    existing.add((inf_target_lower, form_lower))

    print(f"Wiktionary'den {len(new_rows):,} yeni çekim ve kök çifti çıkarıldı.")
    return new_rows

def get_english_irregular_and_inflections(existing: Set[Tuple[str, str]]) -> List[Tuple[str, str, str, str, str, str]]:
    print("İngilizce düzensiz fiiller, sıfatlar ve çoğullar hazırlanıyor...")
    
    CURATED = [
        # (EN form, TR meaning, POS, category)
        ("went", "gitti, ayrıldı (go fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("gone", "gitmiş, gitmiş olan (go fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("saw", "gördü, fark etti (see fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("seen", "görülmüş, gördü (see fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("came", "geldi, ulaştı (come fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("ate", "yedi (eat fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("eaten", "yenmiş (eat fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("drank", "içti (drink fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("drunk", "içmiş, sarhoş (drink fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("wrote", "yazdı (write fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("written", "yazılmış, yazılı (write fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("took", "aldı, götürdü (take fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("taken", "alınmış, tutulmuş (take fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("gave", "verdi (give fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("given", "verilmiş, belirli (give fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("made", "yaptı, üretti (make fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("did", "yaptı (do fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("done", "yapılmış, bitmiş (do fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("said", "dedi, söyledi (say fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("told", "anlattı, söyledi (tell fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("bought", "satın aldı (buy fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("sold", "sattı (sell fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("found", "buldu (find fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("lost", "kaybetti, kayıp (lose fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("heard", "duydu, işitti (hear fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("felt", "hissetti (feel fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("ran", "koştu (run fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("sat", "oturdu (sit fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("stood", "ayakta durdu, bekledi (stand geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("spoke", "konuştu (speak fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("spoken", "konuşulan (speak fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("met", "tanıştı, buluştu (meet fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("built", "inşa etti, kurdu (build fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("left", "ayrıldı, terk etti; sol (leave geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("brought", "getirdi (bring fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("thought", "düşündü, fikir (think fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("taught", "öğretti (teach fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("caught", "yakaladı (catch fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("fought", "savaştı, kavga etti (fight geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("won", "kazandı (win fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("knew", "bildi, tanıdı (know fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("known", "bilinen, tanınan (know fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("grew", "büyüdü, yetişti (grow fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("thrown", "atılmış, fırlatılmış (throw 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("drew", "çizdi (draw fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("drawn", "çizilmiş (draw fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("flew", "uçtu (fly fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("flown", "uçmuş (fly fiilinin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("swam", "yüzdü (swim fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("slept", "uyudu (sleep fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("kept", "tuttu, sakladı (keep fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("paid", "ödedi (pay fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("spent", "harcadı, geçirdi (spend geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("sent", "gönderdi (send fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("held", "tuttu, düzenledi (hold geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("read", "okudu (read fiilinin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("understood", "anladı (understand geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("broke", "kırdı, bozdu (break geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("broken", "kırık, bozuk (break 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("wore", "giydi, taktı (wear geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("worn", "giyilmiş, yıpranmış (wear 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("chose", "seçti (choose geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("chosen", "seçilmiş (choose 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("drove", "sürdü, kullandı (drive geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("driven", "sürülmüş (drive 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("rode", "bindi (ride geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("ridden", "binilmiş (ride 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("became", "oldu, haline geldi (become geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("began", "başladı (begin geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("begun", "başlamış (begin 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("forgot", "unuttu (forget geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("forgotten", "unutulmuş (forget 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("forgave", "affetti (forgive geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("forgiven", "affedilmiş (forgive 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("hid", "sakladı, gizlendi (hide geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("hidden", "saklı, gizli (hide 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("led", "yönetti, önderlik etti (lead geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("woke", "uyandı (wake geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("woken", "uyanmış (wake 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("rose", "yükseldi, doğdu (rise geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("risen", "yükselmiş (rise 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("stole", "çaldı (steal geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("stolen", "çalınmış, çalıntı (steal 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("sang", "şarkı söyledi (sing geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("sung", "söylenmiş şarkı (sing 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("fell", "düştü (fall geçmiş zamanı)", "verb (past)", "İngilizce Düzensiz Fiil"),
        ("fallen", "düşmüş (fall 3. hali)", "verb (pp)", "İngilizce Düzensiz Fiil"),
        ("cut", "kesti, kesik (cut geçmiş/3. hali)", "verb", "İngilizce Düzensiz Fiil"),
        ("hit", "vurdu, çarptı (hit geçmiş/3. hali)", "verb", "İngilizce Düzensiz Fiil"),
        ("hurt", "incitti, acıttı (hurt geçmiş/3. hali)", "verb", "İngilizce Düzensiz Fiil"),
        ("cost", "mal oldu, fiyat (cost geçmiş/3. hali)", "verb", "İngilizce Düzensiz Fiil"),
        ("shut", "kapattı, kapalı (shut geçmiş/3. hali)", "verb", "İngilizce Düzensiz Fiil"),
        ("let", "izin verdi (let geçmiş/3. hali)", "verb", "İngilizce Düzensiz Fiil"),
        ("set", "kurdu, ayarladı (set geçmiş/3. hali)", "verb", "İngilizce Düzensiz Fiil"),

        # Common regular verb past forms & participles
        ("created", "yarattı, oluşturdu (create geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("worked", "çalıştı (work geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("lived", "yaşadı (live geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("looked", "baktı (look geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("watched", "izledi (watch geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("wanted", "istedi (want geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("needed", "ihtiyaç duydu (need geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("liked", "beğendi, sevdi (like geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("loved", "sevdi (love geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("asked", "sordu, istedi (ask geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("answered", "cevapladı (answer geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("helped", "yardım etti (help geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("played", "oynadı, çaldı (play geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("listened", "dinledi (listen geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("opened", "açtı (open geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("closed", "kapattı (close geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("walked", "yürüdü (walk geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("stayed", "kaldı (stay geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("waited", "bekledi (wait geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("started", "başladı, başlattı (start geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("finished", "bitirdi, bitti (finish geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("stopped", "durdu, durdurdu (stop geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("learned", "öğrendi (learn geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("called", "aradı, seslendi (call geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("tried", "denedi, çabaladı (try geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("changed", "değişti, değiştirdi (change geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("believed", "inandı (believe geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),
        ("remembered", "hatırladı (remember geçmiş zamanı)", "verb (past)", "İngilizce Çekim"),

        # Common -ing forms
        ("running", "koşma, koşan, çalışan (run fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("working", "çalışma, çalışan (work fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("going", "gidiş, giden (go fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("coming", "geliş, gelen (come fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("living", "yaşayan, yaşam (live fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("doing", "yapma, eden (do fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("making", "yapım, yapan (make fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("saying", "söyleyiş, deyiş, atasözü (say fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("thinking", "düşünme, fikir (think fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("reading", "okuma (read fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("writing", "yazı, yazma (write fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("playing", "oynama, çalış (play fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),
        ("learning", "öğrenme, bilgi (learn fiilinin -ing hali)", "verb/noun", "İngilizce Çekim"),

        # Comparatives & Superlatives
        ("better", "daha iyi (good sıfatının karşılaştırma / comparative hali)", "adj/adv", "İngilizce Derecelendirme"),
        ("best", "en iyi (good sıfatının üstünlük / superlative hali)", "adj/adv", "İngilizce Derecelendirme"),
        ("worse", "daha kötü (bad sıfatının comparative hali)", "adj/adv", "İngilizce Derecelendirme"),
        ("worst", "en kötü (bad sıfatının superlative hali)", "adj/adv", "İngilizce Derecelendirme"),
        ("more", "daha çok, daha fazla (many/much comparative hali)", "adj/adv", "İngilizce Derecelendirme"),
        ("most", "en çok, en fazla, çoğu (superlative)", "adj/adv", "İngilizce Derecelendirme"),
        ("less", "daha az (little comparative hali)", "adj/adv", "İngilizce Derecelendirme"),
        ("least", "en az (little superlative hali)", "adj/adv", "İngilizce Derecelendirme"),
        ("faster", "daha hızlı (fast comparative hali)", "adj/adv", "İngilizce Derecelendirme"),
        ("fastest", "en hızlı (fast superlative hali)", "adj/adv", "İngilizce Derecelendirme"),
        ("bigger", "daha büyük (big comparative hali)", "adj", "İngilizce Derecelendirme"),
        ("biggest", "en büyük (big superlative hali)", "adj", "İngilizce Derecelendirme"),
        ("smaller", "daha küçük (small comparative hali)", "adj", "İngilizce Derecelendirme"),
        ("smallest", "en küçük (small superlative hali)", "adj", "İngilizce Derecelendirme"),
        ("easier", "daha kolay (easy comparative hali)", "adj", "İngilizce Derecelendirme"),
        ("easiest", "en kolay (easy superlative hali)", "adj", "İngilizce Derecelendirme"),
        ("harder", "daha zor, daha sıkı (hard comparative hali)", "adj/adv", "İngilizce Derecelendirme"),
        ("hardest", "en zor (hard superlative hali)", "adj/adv", "İngilizce Derecelendirme"),
        ("happier", "daha mutlu (happy comparative hali)", "adj", "İngilizce Derecelendirme"),
        ("happiest", "en mutlu (happy superlative hali)", "adj", "İngilizce Derecelendirme"),

        # Irregular Plurals
        ("children", "çocuklar (child çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul"),
        ("people", "insanlar, kişiler, halk (person çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul"),
        ("men", "adamlar, erkekler (man çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul"),
        ("women", "kadınlar (woman çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul"),
        ("teeth", "dişler (tooth çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul"),
        ("feet", "ayaklar (foot çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul"),
        ("mice", "fareler (mouse çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul"),
        ("geese", "kazlar (goose çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul"),
        ("lives", "hayatlar, yaşamlar (life çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul"),
        ("wives", "eşler, karılar (wife çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul"),
        ("knives", "bıçaklar (knife çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul"),
        ("leaves", "yapraklar (leaf çoğul hali)", "noun (pl)", "İngilizce Düzensiz Çoğul")
    ]

    new_rows = []
    for en_w, tr_w, pos, cat in CURATED:
        en_lower = turkish_lower(en_w)
        tr_lower = turkish_lower(tr_w)
        if (en_lower, tr_lower) not in existing:
            new_rows.append((en_w, tr_w, pos, cat, en_lower, tr_lower))
            existing.add((en_lower, tr_lower))

    print(f"Toplam {len(new_rows):,} İngilizce çekim/düzensiz kalıp hazırlandı.")
    return new_rows

def main():
    if not os.path.exists(DB_PATH):
        print(f"HATA: {DB_PATH} bulunamadı!")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    existing = load_existing_pairs(conn)

    all_new_rows = []
    all_new_rows.extend(get_english_irregular_and_inflections(existing))
    all_new_rows.extend(parse_freedict_eng_tur(existing))
    all_new_rows.extend(parse_freedict_tur_eng(existing))
    all_new_rows.extend(parse_wiktionary_tr_en(existing))

    print(f"\nToplam eklenecek yeni kayıt sayısı: {len(all_new_rows):,}")

    if all_new_rows:
        print("Kayıtlar veritabanına toplu (batch) olarak yazılıyor...")
        cur.execute("PRAGMA synchronous = OFF;")
        cur.execute("PRAGMA journal_mode = MEMORY;")

        sql = "INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower) VALUES (?, ?, ?, ?, ?, ?)"
        batch_size = 50000
        for i in range(0, len(all_new_rows), batch_size):
            batch = all_new_rows[i:i + batch_size]
            cur.executemany(sql, batch)
            conn.commit()
            print(f"  Yazıldı: {min(i + batch_size, len(all_new_rows)):,} / {len(all_new_rows):,}")

        print("Veritabanı indeksleri optimize ediliyor...")
        cur.execute("ANALYZE bilingual;")
        conn.commit()

    # Final stats
    cur.execute("SELECT COUNT(*) FROM bilingual")
    total_bi = cur.fetchone()[0]
    print(f"\nİŞLEM TAMAMLANDI! Güncel bilingual tablo boyutu: {total_bi:,} satır.")

    conn.close()

if __name__ == "__main__":
    main()
