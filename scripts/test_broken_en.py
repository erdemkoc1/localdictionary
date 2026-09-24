import sqlite3

conn = sqlite3.connect('data/dictionary.db')
cur = conn.cursor()

cur.execute("""
    SELECT tr, en, category FROM bilingual 
    WHERE en_lower = "piston's"
    LIMIT 5;
""")
print("Sample rows for piston's:")
for r in cur.fetchall():
    print(r)
