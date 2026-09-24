import sqlite3

conn = sqlite3.connect('data/dictionary.db')
cur = conn.cursor()

# Find entries where Turkish is multi-word idiom, but English is single hyphenated fragment or truncated word
cur.execute("""
    SELECT tr, en, category FROM bilingual 
    WHERE tr = 'can kulağıyla dinlemek' 
    LIMIT 20;
""")
print("Entries for 'can kulağıyla dinlemek':")
for r in cur.fetchall():
    print(r)

# Check how many entries have single letter or dangling hyphen in en
cur.execute("""
    SELECT COUNT(*) FROM bilingual 
    WHERE en LIKE '%-' OR en LIKE '-%' OR LENGTH(en) = 1;
""")
print("\nDangling hyphen or single char EN entries:", cur.fetchone()[0])

# Check duplicate counts
cur.execute("""
    SELECT tr_lower, en_lower, COUNT(*) 
    FROM bilingual 
    GROUP BY tr_lower, en_lower 
    HAVING COUNT(*) > 1 
    LIMIT 10;
""")
print("\nSample duplicates:")
for r in cur.fetchall():
    print(r)
