import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from src.db import DictionaryDB

db = DictionaryDB()

test_queries = [
    "mütekabiliyet",
    "muhatap",
    "özveri",
    "itidal",
    "aykırı",
    "maverick",
    "serendipity",
    "obfuscate",
    "quintessential",
    "quandary",
    "run",
    "set",
    "fair"
]

print("=" * 80)
print("TESTING ADVANCED C1/C2 & POLYSEMY DICTIONARY SEARCH")
print("=" * 80)

for q in test_queries:
    results, elapsed, direction = db.search(q, limit=10)
    print(f"\nQUERY: '{q}' ({direction}) -> {len(results)} results in {elapsed:.2f}ms")
    for r in results[:6]:
        print(f"  • {r['source']} ➔ {r['target']} [{r['type']}] ({r['category']})")
