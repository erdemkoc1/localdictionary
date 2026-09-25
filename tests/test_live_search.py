import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db import DictionaryDB


def run_diagnostics():
    db = DictionaryDB()
    try:
        cases = [
            "geldi", "gitti", "okulda", "evden", "kitaplar", "went", "running",
            "better", "saw", "created", "worked", "göz yummak",
            "damlaya damlaya göl olur", "etekleri zil", "aradıysam", "unbelievable",
        ]
        for term in cases:
            results, elapsed_ms, direction = db.search(term, limit=3)
            print(f"=== '{term}' ({direction}, {elapsed_ms:.2f}ms, {len(results)} hits) ===")
            for result in results[:2]:
                print(f"  [{result['category']}] {result['source']} -> {result['target']}")
    finally:
        db.close()


if __name__ == "__main__":
    run_diagnostics()
