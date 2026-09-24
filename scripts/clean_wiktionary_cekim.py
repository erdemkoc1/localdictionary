"""
Database Cleaner Script: Strips lexicographical Wiktionary glosses and '(Kök: ...)' markers
from all 446,000+ inflected rows in dictionary.db to ensure clean translations.
"""

import os
import re
import sqlite3
import time

def clean_database():
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "dictionary.db")
    if not os.path.exists(db_path):
        print("Database not found:", db_path)
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    def clean_gloss(val):
        if not val:
            return val
        # 1. Remove (Kök: ...)
        res = re.sub(r'\s*\(Kök:[^)]*\)', '', val)
        # 2. Remove parenthetical dictionary notes / glosses
        res = re.sub(r'\(negates meaning of the verb [^)]*\)', '', res)
        res = re.sub(r'\(transitive, vulgar, [^)]*\)', '', res)
        res = re.sub(r'\(transitive, vulgar\)', '', res)
        res = re.sub(r'\((?:in)?transitive[^)]*\)', '', res)
        res = re.sub(r'\((?:in)?transitive, [^)]*\)', '', res)
        res = re.sub(r'\(idiomatic, [^)]*\)', '', res)
        res = re.sub(r'\s*;\s*', ', ', res).strip(' ,;')
        return res

    conn.create_function('clean_gloss', 1, clean_gloss)

    t0 = time.time()
    cur.execute("SELECT COUNT(*) FROM bilingual WHERE en LIKE '%(Kök:%'")
    count_before = cur.fetchone()[0]
    print(f"Dirty rows before cleaning: {count_before}")

    if count_before > 0:
        cur.execute("UPDATE bilingual SET en = clean_gloss(en) WHERE en LIKE '%(Kök:%'")
        conn.commit()
        print(f"Updated {cur.rowcount} rows in {time.time() - t0:.2f}s.")

    cur.execute("SELECT COUNT(*) FROM bilingual WHERE en LIKE '%(Kök:%'")
    count_after = cur.fetchone()[0]
    print(f"Dirty rows after cleaning: {count_after}")
    conn.close()

if __name__ == "__main__":
    clean_database()
