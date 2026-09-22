import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.syntax_engine import SyntaxTranslator

def test_syntax():
    st = SyntaxTranslator()
    test_sentences = [
        "I saw a beautiful book yesterday.",
        "She works in London.",
        "We will meet tomorrow.",
        "I want a computer for my brother."
    ]

    for s in test_sentences:
        res = st.translate(s, "en_tr")
        print(f"EN: {s}")
        print(f"TR: {res['translated_text']}")
        print("Breakdown:")
        for b in res["breakdown"]:
            print(f"  {b['original']} [{b['role']}] -> {b['translated']}")
        print("-" * 50)

if __name__ == "__main__":
    test_syntax()
