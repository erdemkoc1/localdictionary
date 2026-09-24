import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('data/dictionary.db')
cur = conn.cursor()

# Total rows
cur.execute("SELECT COUNT(*) FROM bilingual;")
total_rows = cur.fetchone()[0]

# Unique English words
cur.execute("SELECT COUNT(DISTINCT en_lower) FROM bilingual;")
unique_en = cur.fetchone()[0]

# Unique Turkish words
cur.execute("SELECT COUNT(DISTINCT tr_lower) FROM bilingual;")
unique_tr = cur.fetchone()[0]

print(f"Total rows in bilingual: {total_rows}")
print(f"Unique English lemmas/words: {unique_en}")
print(f"Unique Turkish lemmas/words: {unique_tr}")

# Average meanings per word
cur.execute("""
    SELECT AVG(cnt) FROM (
        SELECT en_lower, COUNT(*) as cnt FROM bilingual GROUP BY en_lower
    );
""")
avg_meanings_en = cur.fetchone()[0]

cur.execute("""
    SELECT AVG(cnt) FROM (
        SELECT tr_lower, COUNT(*) as cnt FROM bilingual GROUP BY tr_lower
    );
""")
avg_meanings_tr = cur.fetchone()[0]

print(f"Average meanings per English word: {avg_meanings_en:.2f}")
print(f"Average meanings per Turkish word: {avg_meanings_tr:.2f}")

# Distribution of meanings count for common English words
sample_common = ["run", "set", "get", "take", "make", "go", "turn", "break", "bear", "sound", "light", "fair", "matter", "state"]
print("\nSample polysemy count for common words:")
for w in sample_common:
    cur.execute("SELECT COUNT(*), GROUP_CONCAT(tr, ' | ') FROM bilingual WHERE en_lower = ? LIMIT 5;", (w,))
    row = cur.fetchone()
    count = row[0]
    sample_meanings = row[1][:120] if row[1] else "None"
    print(f"  Word '{w}': {count} entries -> {sample_meanings}...")

# Check C1/C2 advanced vocabulary presence
sample_advanced = [
    "ephemeral", "ubiquitous", "serendipity", "pernicious", "obfuscate",
    "quintessential", "recalcitrant", "clandestine", "esoteric", "fastidious",
    "garrulous", "harangue", "idiosyncrasy", "juxtaposition", "laconic",
    "maverick", "nefarious", "ostentatious", "paradoxical", "quandary"
]
print("\nAdvanced C1/C2 English words check in DB:")
found_adv = 0
for w in sample_advanced:
    cur.execute("SELECT tr, type, category FROM bilingual WHERE en_lower = ? LIMIT 1;", (w,))
    row = cur.fetchone()
    if row:
        found_adv += 1
        print(f"  [+] {w}: {row[0]} ({row[1]}, {row[2]})")
    else:
        print(f"  [-] {w}: NOT FOUND")
print(f"Found {found_adv}/{len(sample_advanced)} advanced sample words.")
