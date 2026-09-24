import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "data", "dictionary.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Remove the corrupt abbreviation mappings
cur.execute("DELETE FROM bilingual WHERE tr_lower IN ('bana', 'beni') AND en IN ('M.E.', 'ME', 'Me.', 'Melar', '(i.)')")
cur.execute("DELETE FROM bilingual WHERE tr_lower = 'bize' AND en IN ('U.S.', 'US', 'u.s.')")
cur.execute("DELETE FROM bilingual WHERE tr_lower = 'onu' AND en IN ('as', 'AS', 'As')")

# 2. Insert clean Common Usage entries
clean_pronouns = [
    ("me", "bana", "pron.", "Common Usage", "me", "bana"),
    ("to me", "bana", "pron.", "Common Usage", "to me", "bana"),
    ("me", "beni", "pron.", "Common Usage", "me", "beni"),
    ("us", "bize", "pron.", "Common Usage", "us", "bize"),
    ("to us", "bize", "pron.", "Common Usage", "to us", "bize"),
    ("us", "bizi", "pron.", "Common Usage", "us", "bizi"),
    ("him", "onu", "pron.", "Common Usage", "him", "onu"),
    ("her", "onu", "pron.", "Common Usage", "her", "onu"),
    ("it", "onu", "pron.", "Common Usage", "it", "onu"),
    ("to him", "ona", "pron.", "Common Usage", "to him", "ona"),
    ("to her", "ona", "pron.", "Common Usage", "to her", "ona"),
    ("you", "sana", "pron.", "Common Usage", "you", "sana"),
    ("to you", "sana", "pron.", "Common Usage", "to you", "sana"),
    ("you", "seni", "pron.", "Common Usage", "you", "seni"),
    ("you", "size", "pron.", "Common Usage", "you", "size"),
    ("to you", "size", "pron.", "Common Usage", "to you", "size"),
    ("you", "sizi", "pron.", "Common Usage", "you", "sizi"),
    ("them", "onları", "pron.", "Common Usage", "them", "onlari"),
    ("to them", "onlara", "pron.", "Common Usage", "to them", "onlara"),
]

for en, tr, wtype, cat, en_l, tr_l in clean_pronouns:
    cur.execute("INSERT OR REPLACE INTO bilingual (en, tr, type, category, en_lower, tr_lower) VALUES (?, ?, ?, ?, ?, ?)",
                (en, tr, wtype, cat, en_l, tr_l))

conn.commit()
print("Prune & insert completed.")
cur.execute("SELECT en, category FROM bilingual WHERE tr_lower = 'bana'")
print("New 'bana' entries:", cur.fetchall())
conn.close()
