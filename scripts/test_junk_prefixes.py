import sqlite3

conn = sqlite3.connect('data/dictionary.db')
cur = conn.cursor()

# Check how many entries have junk prefixes or single tokens mapped to multi-word phrases
cur.execute("""
    SELECT en, COUNT(*) FROM bilingual 
    WHERE tr_lower LIKE '% %' AND en_lower IN ('a-', 'the-', 'to-', 'in-', 'on-', 'at-', 'of-', 'for-', 'be-', 'do-', 'get-')
    GROUP BY en 
    ORDER BY COUNT(*) DESC;
""")
for r in cur.fetchall():
    print(r)
