import ast
import os
import pathlib
import socket
import tempfile
import unittest
from unittest.mock import patch

from src.translator import SentenceTranslator
from src.user_data import UserDataManager


class TestOfflineRuntime(unittest.TestCase):
    def test_runtime_source_has_no_network_client_imports(self):
        source_root = pathlib.Path(__file__).resolve().parent.parent / "src"
        forbidden = {"argostranslate", "requests", "urllib", "http", "socket"}
        violations = []
        for path in source_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [(node.module or "").split(".")[0]]
                else:
                    continue
                if forbidden.intersection(names):
                    violations.append((path.name, node.lineno, names))
        # socket is allowed only in the explicit Win32 integration module,
        # which uses ctypes rather than Python sockets.
        violations = [
            item for item in violations
            if not (
                (item[0] == "quick_translate.py" or item[0] == "network_guard.py")
                and "socket" in item[2]
            )
        ]
        self.assertEqual(violations, [])

    def test_translation_works_when_socket_connections_are_blocked(self):
        with tempfile.TemporaryDirectory(prefix="localdictionary-offline-test-") as temp_dir:
            translator = SentenceTranslator(
                user_data=UserDataManager(os.path.join(temp_dir, "user_data.db"))
            )
            with patch.object(socket.socket, "connect", side_effect=AssertionError("network attempted")):
                result = translator.translate("Hello world.", "en", "tr")
            self.assertTrue(result.translated_text)


if __name__ == "__main__":
    unittest.main()
