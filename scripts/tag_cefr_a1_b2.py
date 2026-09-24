"""
Download and Tag CEFR A1-B2 words from CEFR-J profile.
"""

import os
import sys
import csv
import urllib.request
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(base_dir, "data", "dictionary.db")

url = "https://raw.githubusercontent.com/openlanguageprofiles/olp-en-cefrj/master/cefrj-vocabulary-profile-1.5.csv"

def tag_a1_b2():
    print("Downloading CEFR-J A1-B2 vocabulary profile...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode('utf-8')
        lines = content.splitlines()
        reader = csv.DictReader(lines)
        entries = []
        for row in reader:
            headword = row.get("headword", "").strip()
            cefr = row.get("CEFR", "").strip()
            pos = row.get("pos", "").strip()
            if headword and cefr:
                entries.append((headword.lower(), pos, f"CEFR {cefr}"))

    print(f"Downloaded {len(entries)} CEFR A1-B2 profile entries.")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tagged = 0
    for word_low, pos, tag in entries:
        cur.execute("""
            UPDATE bilingual 
            SET category = ? 
            WHERE en_lower = ? AND category NOT IN ('Primary', 'Common Usage', 'Idioms & Proverbs', 'CEFR C1', 'CEFR C2');
        """, (tag, word_low))
        tagged += cur.rowcount

    conn.commit()
    conn.close()
    print(f"Tagged {tagged} rows with CEFR A1-B2 levels!")

if __name__ == "__main__":
    tag_a1_b2()
