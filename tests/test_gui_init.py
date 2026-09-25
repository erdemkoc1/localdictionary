import os
import sys
import tempfile
import unittest

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.gui import TranslatorApp


class TestGuiInitialization(unittest.TestCase):
    def test_gui_uses_isolated_history(self):
        with tempfile.TemporaryDirectory(prefix="localdictionary-gui-test-") as temp_dir:
            app = TranslatorApp(
                settings_file=os.path.join(temp_dir, "settings.json"),
                user_data_dir=temp_dir,
            )
            try:
                app.perform_search("computer")
                app.perform_search("başarı")
                recent = app.history.get_recent()
                self.assertEqual(len(recent), 2)
                self.assertEqual(recent[0]["query"], "başarı")
                self.assertGreaterEqual(len(app.quick_history_frame.winfo_children()), 3)
            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
