import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.syntax_engine import SyntaxTranslator

def test_syntax():
    st = SyntaxTranslator()
    test_sentences = [
        "Ayşe works in London.",
        "She works in London.",
        "My brother lives in London.",
        "Ayşe is a teacher.",
        "John lives in Paris.",
        "Ali goes to school.",
        "I want a computer for my brother.",
        "We will meet tomorrow.",
        "I saw a beautiful book yesterday.",
        "The doctor works in the hospital."
    ]

    for s in test_sentences:
        res = st.translate(s, "auto")
        print(f"EN: {s}")
        print(f"TR: {res['translated_text']}")
        for b in res["breakdown"]:
            print(f"  {b['original']} [{b['role']}] -> {b['translated']}")
        print("-" * 50)

    print("\n========== TURKISH TO ENGLISH ==========\n")
    tr_sentences = [
        "O Londra'da çalışıyor.",
        "Ayşe bir öğretmendir.",
        "Ali okula gidiyor.",
        "Ben su içtim."
    ]
    for s in tr_sentences:
        res = st.translate(s, "auto")
        print(f"TR: {s}")
        print(f"EN: {res['translated_text']}")
        print("Breakdown:")
        for b in res["breakdown"]:
            print(f"  {b['original']} [{b['role']}] -> {b['translated']}")
        print("-" * 50)

if __name__ == "__main__":
    test_syntax()

