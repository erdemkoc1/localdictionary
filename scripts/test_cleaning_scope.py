import sqlite3

conn = sqlite3.connect('data/dictionary.db')
cur = conn.cursor()

cur.execute("""
    SELECT COUNT(*) FROM bilingual 
    WHERE tr_lower LIKE '% %' 
    AND (en_lower LIKE '%-' OR en_lower LIKE '-%' OR en_lower LIKE "%'s" OR en_lower LIKE "%’s");
""")
count = cur.fetchone()[0]
print(f"Broken fragmented multi-word entries to clean: {count}")

cur.execute("""
    SELECT tr, en, category FROM bilingual 
    WHERE tr_lower LIKE '% %' 
    AND (en_lower LIKE '%-' OR en_lower LIKE '-%' OR en_lower LIKE "%'s" OR en_lower LIKE "%’s")
    LIMIT 10;
""")
for r in cur.fetchall():
    print("Sample:", r)
