import os
import sys
import re
import sqlite3
from typing import Set, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.utils import turkish_lower

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "dictionary.db"))
WIKTIONARY_TSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "wiktionary_tr_en.tsv"))

def clean_text(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Mevcut tr_lower kayıtları taranıyor...")
    cur.execute("SELECT DISTINCT tr_lower FROM bilingual")
    existing_tr = set(r[0] for r in cur.fetchall())
    print(f"Mevcut farklı tr_lower sayısı: {len(existing_tr):,}")

    new_rows = []
    seen_in_batch = set()

    print("Wiktionary tüm çekimli tekil kelimeler taranıyor...")
    with open(WIKTIONARY_TSV, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "\t" not in line:
                continue
            words_part, html_part = line.split("\t", 1)
            forms = [w.strip() for w in words_part.split("|") if w.strip()]
            if not forms:
                continue

            pos_match = re.search(r"<i>(.*?)</i>", html_part)
            pos_str = pos_match.group(1).strip() if pos_match else "kelime"

            meanings = re.findall(r"<li>(.*?)</li>", html_part)
            clean_meanings = []
            for m in meanings:
                m_clean = clean_text(m)
                if m_clean and len(m_clean) < 120:
                    clean_meanings.append(m_clean)

            if not clean_meanings:
                continue

            primary_meaning = "; ".join(clean_meanings[:2])
            headword = forms[0]

            for form in forms:
                f_clean = form.strip()
                if " " in f_clean or "?" in f_clean or "'" in f_clean or len(f_clean) < 2 or len(f_clean) > 30:
                    continue
                if any(c in f_clean for c in "<>{}[]@#$%^&*=+"):
                    continue

                f_lower = turkish_lower(f_clean)
                if f_lower in existing_tr or f_lower in seen_in_batch:
                    continue

                seen_in_batch.add(f_lower)

                if f_clean == headword:
                    en_val = primary_meaning
                    pos_val = pos_str
                    cat_val = "Wiktionary"
                else:
                    en_val = f"{primary_meaning} (Kök: {headword})"
                    pos_val = f"{pos_str} (çekim)"
                    cat_val = "Wiktionary / Çekim"

                en_lower = turkish_lower(en_val)
                new_rows.append((en_val, f_clean, pos_val, cat_val, en_lower, f_lower))

    print(f"Toplam eklenecek benzersiz yeni çekimli kelime sayısı: {len(new_rows):,}")

    if new_rows:
        print("Toplu veritabanına yazılıyor...")
        cur.execute("PRAGMA synchronous = OFF;")
        cur.execute("PRAGMA journal_mode = MEMORY;")
        sql = "INSERT INTO bilingual (en, tr, type, category, en_lower, tr_lower) VALUES (?, ?, ?, ?, ?, ?)"
        batch_size = 50000
        for i in range(0, len(new_rows), batch_size):
            batch = new_rows[i:i + batch_size]
            cur.executemany(sql, batch)
            conn.commit()
            print(f"  Yazıldı: {min(i + batch_size, len(new_rows)):,} / {len(new_rows):,}")

        print("İndeksler güncelleniyor...")
        cur.execute("ANALYZE bilingual;")
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM bilingual")
    total = cur.fetchone()[0]
    print(f"\nTAMAMLANDI! Yeni bilingual toplam kayıt sayısı: {total:,}")
    conn.close()

if __name__ == "__main__":
    main()
