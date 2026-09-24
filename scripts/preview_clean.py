import sqlite3

conn = sqlite3.connect('data/dictionary.db')
cur = conn.cursor()

# 1. Multi-word Turkish mapped to single-word possessive in English
cur.execute("""
    SELECT COUNT(*) FROM bilingual 
    WHERE tr_lower LIKE '% %' 
    AND (en_lower LIKE "%'s" OR en_lower LIKE "%’s") 
    AND en_lower NOT LIKE '% %';
""")
count_poss = cur.fetchone()[0]
print(f"Junk single-word possessives on multi-word TR: {count_poss}")

# 2. Multi-word Turkish mapped to dangling hyphen
cur.execute("""
    SELECT COUNT(*) FROM bilingual 
    WHERE tr_lower LIKE '% %' 
    AND (en_lower LIKE '%-' OR en_lower LIKE '-%');
""")
count_hyphen = cur.fetchone()[0]
print(f"Junk dangling hyphen on multi-word TR: {count_hyphen}")

# 3. Corrupted Proverb rows where en is a single word
cur.execute("""
    SELECT COUNT(*) FROM bilingual 
    WHERE category = 'Proverb' 
    AND en_lower NOT LIKE '% %';
""")
count_proverb = cur.fetchone()[0]
print(f"Corrupted single-word EN in Proverb category: {count_proverb}")

# 4. Check total rows in bilingual
cur.execute("SELECT COUNT(*) FROM bilingual;")
total = cur.fetchone()[0]
print(f"Total rows in bilingual: {total}")
