import sqlite3

conn = sqlite3.connect('data/dictionary.db')
cur = conn.cursor()

# Remove fragmented single-word EN in Idioms where TR is multi-word
cur.execute("""
    DELETE FROM bilingual 
    WHERE category = 'Idioms' 
    AND tr_lower LIKE '% %' 
    AND en_lower NOT LIKE '% %';
""")
print("Deleted fragmented Idioms rows:", cur.rowcount)

# Prioritize Idioms & Proverbs by updating categories of clean idioms
cur.execute("""
    UPDATE bilingual 
    SET category = 'Idioms & Proverbs' 
    WHERE tr_lower = 'can kulağıyla dinlemek' 
    AND en_lower LIKE '%listen with rapt attention%';
""")

conn.commit()
conn.close()
print("Done cleaning single-word idiom remnants.")
