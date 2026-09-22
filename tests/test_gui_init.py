import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui import TranslatorApp

def test_gui_headless():
    print("Testing TranslatorApp with History...")
    app = TranslatorApp()

    # Clear previous history for test
    app.history.clear_all()

    # Perform searches
    app.perform_search("computer")
    app.perform_search("başarı")

    # Verify history recorded
    recent = app.history.get_recent()
    print("Recorded history count:", len(recent))
    assert len(recent) == 2, f"Expected 2 history items, got {len(recent)}"
    assert recent[0]["query"] == "başarı"
    assert recent[1]["query"] == "computer"

    # Test quick search from history
    app.quick_search("computer")
    assert len(app.current_results) > 0

    # Test quick chips count
    chips = app.quick_history_frame.winfo_children()
    print("Quick history children count:", len(chips))
    # Should have 1 label + 2 buttons
    assert len(chips) >= 3

    app.destroy()
    print("GUI history headless tests passed successfully!")

if __name__ == "__main__":
    test_gui_headless()
