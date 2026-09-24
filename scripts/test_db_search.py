import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from src.db import DictionaryDB

db = DictionaryDB()

queries = ["bekar", "can kulağıyla dinlemek", "ateş pahası", "piece of cake", "under the weather", "damlaya damlaya göl olur"]

for q in queries:
    results, elapsed, direction = db.search(q)
    print(f"\nQUERY: '{q}' ({direction}) - {len(results)} results in {elapsed:.2f}ms")
    for r in results[:5]:
        print(f"  -> source: {r['source']} | target: {r['target']} | type: {r['type']} | cat: {r['category']}")
