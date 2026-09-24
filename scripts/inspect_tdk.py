import sqlite3

conn = sqlite3.connect('data/tdk_v12.sqlite3.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("TDK tables:", cur.fetchall())

for table in ['madde', 'anlam', 'atasozu', 'ornek']:
    cur.execute(f"PRAGMA table_info({table});")
    print(f"\nSchema for {table}:", cur.fetchall())
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    print(f"Count for {table}:", cur.fetchone()[0])

cur.execute("SELECT * FROM madde LIMIT 3;")
print("\nSample madde:", cur.fetchall())
cur.execute("SELECT * FROM anlam LIMIT 3;")
print("\nSample anlam:", cur.fetchall())
