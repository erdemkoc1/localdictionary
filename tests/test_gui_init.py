import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui import TranslatorApp

def test_gui_headless():
    print("Testing TranslatorApp instantiation...")
    app = TranslatorApp()
    # Trigger a search
    app.perform_search("computer")
    print(f"Status: {app.status_left.cget('text')}")
    assert len(app.current_results) > 0, "No results returned for 'computer'"
    
    # Test theme toggle
    app.toggle_theme()
    assert app.current_theme == "light"
    app.toggle_theme()
    assert app.current_theme == "dark"
    print("Theme toggle verified!")

    # Test Turkish search
    app.perform_search("başarı")
    print(f"Status: {app.status_left.cget('text')}")
    assert len(app.current_results) > 0, "No results returned for 'başarı'"

    app.destroy()
    print("GUI headless tests passed successfully!")

if __name__ == "__main__":
    test_gui_headless()
