import os
import sys
import threading
from typing import Optional, Tuple
from src.utils import get_resource_path

class SentenceTranslator:
    def __init__(self):
        self._is_initialized = False
        self._init_lock = threading.Lock()
        self._models_dir = None

    def _ensure_initialized(self):
        if self._is_initialized:
            return

        with self._init_lock:
            if self._is_initialized:
                return

            # Determine models directory
            models_path = get_resource_path(os.path.join("data", "models"))
            if not os.path.exists(models_path):
                # Fallback to current directory models
                models_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "models"))

            os.environ["ARGOS_PACKAGES_DIR"] = models_path
            self._models_dir = models_path

            import argostranslate.package
            import argostranslate.translate

            # Cache the modules
            self._argos_pkg = argostranslate.package
            self._argos_tr = argostranslate.translate
            self._is_initialized = True

    def detect_lang(self, text: str) -> str:
        """Simple heuristic to detect Turkish vs English."""
        tr_chars = set("çğıöşüÇĞİÖŞÜ")
        if any(c in tr_chars for c in text):
            return "tr"
        
        # Check common Turkish words vs English words
        words = set(text.lower().split()[:10])
        common_tr = {"ve", "bir", "bu", "da", "de", "için", "ile", "çok", "var", "yok"}
        if words.intersection(common_tr):
            return "tr"

        return "en"

    def translate(self, text: str, from_lang: str = "auto", to_lang: str = "auto") -> Tuple[str, str, str]:
        """
        Translate sentence offline using CPU NMT.
        Returns: (translated_text, from_code, to_code)
        """
        text = text.strip()
        if not text:
            return "", "", ""

        self._ensure_initialized()

        if from_lang == "auto":
            from_code = self.detect_lang(text)
            to_code = "tr" if from_code == "en" else "en"
        else:
            from_code = from_lang
            to_code = to_lang

        # Perform translation via Argos Translate
        result = self._argos_tr.translate(text, from_code, to_code)
        return result, from_code, to_code
