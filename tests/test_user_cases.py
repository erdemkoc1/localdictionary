import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.syntax_engine import SyntaxTranslator

st = SyntaxTranslator()
tests = [
    "Jesus created everything.",
    "He's a brave soldier.",
    "He is a brave soldier.",
    "He is a brave soldier and he lives in London.",
    "The teacher saw a new car yesterday and she was very happy.",
    "Ayşe works in London and Ali goes to school."
]
for t in tests:
    res = st.translate(t, "auto")
    print(t, "->", res["translated_text"])
    for b in res["breakdown"]:
        print(f"  {b['original']} [{b['role']}, {b.get('pos', '')}] -> {b['translated']}")
    print("-" * 50)
