import sqlite3

conn = sqlite3.connect('data/dictionary.db')
cur = conn.cursor()
cur.execute("SELECT category, COUNT(*) FROM bilingual WHERE category LIKE '%eyim%' OR category LIKE '%roverb%' OR category LIKE '%tasöz%' GROUP BY category;")
for row in cur.fetchall():
    print(row)

cur.execute("SELECT tr, en, category FROM bilingual WHERE category = 'TDK Atasözleri ve Deyimler' LIMIT 5;")
print("\nSample TDK Atasözleri:")
for row in cur.fetchall():
    print(row)

cur.execute("SELECT en, tr, category FROM bilingual WHERE category = 'Proverb' LIMIT 5;")
print("\nSample Proverb:")
for row in cur.fetchall():
    print(row)
