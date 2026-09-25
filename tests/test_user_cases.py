import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.syntax_engine import SyntaxTranslator


def run_diagnostics():
    translator = SyntaxTranslator()
    try:
        cases = [
            "Jesus created everything.",
            "He's a brave soldier.",
            "He is a brave soldier.",
            "He is a brave soldier and he lives in London.",
            "The teacher saw a new car yesterday and she was very happy.",
            "Ayşe works in London and Ali goes to school.",
        ]
        for sentence in cases:
            result = translator.translate(sentence, "auto")
            print(sentence, "->", result["translated_text"])
            for item in result["breakdown"]:
                print(f"  {item['original']} [{item['role']}] -> {item['translated']}")
    finally:
        translator.conn.close()


if __name__ == "__main__":
    run_diagnostics()
