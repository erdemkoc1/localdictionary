import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db import DictionaryDB

db = DictionaryDB()
tests = [
    'geldi',
    'gitti',
    'okulda',
    'evden',
    'kitaplar',
    'went',
    'running',
    'better',
    'saw',
    'created',
    'worked',
    'göz yummak',
    'damlaya damlaya göl olur',
    'etekleri zil',
    'acube',
    'aradıysam',
    'unbelievable'
]

for t in tests:
    res, ms, d = db.search(t, limit=3)
    print(f"=== '{t}' ({d}, {ms:.2f}ms, {len(res)} hits) ===")
    for r in res[:2]:
        print(f"  [{r['category']}] {r['source']} -> {r['target']} ({r['type']})")

db.close()
