import os
import sys
import json
import hashlib
import sqlite3
from typing import Optional, List, Dict, Any, Tuple
from src.utils import turkish_lower


class UserDataManager:
    """
    Manages local user-generated data:
    1. Translation Cache (sub-millisecond instant lookup for repeated queries)
    2. User Corrections (human-in-the-loop learning from manual edits)
    3. Custom User Glossary (user-defined custom terminology dictionary)
    """
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            if getattr(sys, "frozen", False):
                exe_dir = os.path.dirname(sys.executable)
                db_path = os.path.join(exe_dir, "user_data.db")
            else:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                data_dir = os.path.join(base_dir, "data")
                os.makedirs(data_dir, exist_ok=True)
                db_path = os.path.join(data_dir, "user_data.db")

        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        cur = conn.cursor()

        # 1. Translation Cache Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS translation_cache (
            cache_key TEXT PRIMARY KEY,
            input_text TEXT NOT NULL,
            from_code TEXT NOT NULL,
            to_code TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            breakdown_json TEXT,
            confidence INTEGER DEFAULT 80,
            engine TEXT DEFAULT 'cache',
            show_slang INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON translation_cache(cache_key);")

        # 2. User Corrections Table (Learned Edits)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_lower TEXT NOT NULL,
            from_code TEXT NOT NULL,
            to_code TEXT NOT NULL,
            original_input TEXT NOT NULL,
            corrected_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(input_lower, from_code, to_code)
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_corr_lookup ON user_corrections(input_lower, from_code, to_code);")

        # 3. Custom User Glossary Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_glossary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_term TEXT NOT NULL,
            target_term TEXT NOT NULL,
            lang_pair TEXT DEFAULT 'any',
            case_sensitive INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_glossary_pair ON user_glossary(lang_pair);")

        conn.commit()
        conn.close()

    @staticmethod
    def _compute_cache_key(text: str, from_code: str, to_code: str, show_slang: bool) -> str:
        norm = " ".join(turkish_lower(text).split())
        raw = f"{norm}|{from_code}|{to_code}|{1 if show_slang else 0}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # =========================================================================
    # 1. TRANSLATION CACHE METHODS
    # =========================================================================
    def get_cached_translation(
        self, text: str, from_code: str, to_code: str, show_slang: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Returns cached translation if available, or None."""
        key = self._compute_cache_key(text, from_code, to_code, show_slang)
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT translated_text, breakdown_json, confidence, engine
            FROM translation_cache
            WHERE cache_key = ?
            LIMIT 1;
        """, (key,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        breakdown = []
        if row["breakdown_json"]:
            try:
                breakdown = json.loads(row["breakdown_json"])
            except Exception:
                breakdown = []

        return {
            "translated_text": row["translated_text"],
            "from_code": from_code,
            "to_code": to_code,
            "breakdown": breakdown,
            "confidence": row["confidence"],
            "engine": "cache"
        }

    def set_cached_translation(
        self, 
        text: str = "", 
        from_code: str = "auto", 
        to_code: str = "auto", 
        translated_text: str = "", 
        breakdown: list = None, 
        confidence: int = 80, 
        engine: str = "nmt",
        show_slang: bool = True,
        **kwargs
    ):
        """Stores a translation result in cache."""
        txt = (kwargs.get("source_text") or text).strip()
        f_code = kwargs.get("from_code") or kwargs.get("from_lang") or from_code
        t_code = kwargs.get("to_code") or kwargs.get("to_lang") or to_code
        trans = (kwargs.get("translated_text") or translated_text).strip()
        b_down = kwargs.get("breakdown") if "breakdown" in kwargs else (breakdown or [])
        conf = kwargs.get("confidence", confidence)
        eng = kwargs.get("engine", engine)
        slang = kwargs.get("show_slang", show_slang)

        if not txt or not trans:
            return

        key = self._compute_cache_key(txt, f_code, t_code, slang)
        b_json = json.dumps(b_down, ensure_ascii=False) if b_down else "[]"

        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO translation_cache (
                cache_key, input_text, from_code, to_code, translated_text,
                breakdown_json, confidence, engine, show_slang, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(cache_key) DO UPDATE SET
                translated_text = excluded.translated_text,
                breakdown_json = excluded.breakdown_json,
                confidence = excluded.confidence,
                engine = excluded.engine,
                created_at = CURRENT_TIMESTAMP;
        """, (key, txt, f_code, t_code, trans, b_json, conf, eng, 1 if slang else 0))
        conn.commit()
        conn.close()

    def clear_cache(self):
        """Clears all cached translations."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM translation_cache;")
        conn.commit()
        conn.close()

    # =========================================================================
    # 2. USER CORRECTIONS METHODS (Human-in-the-Loop)
    # =========================================================================
    def get_correction(self, text: str, from_code: str = "auto", to_code: str = "auto", **kwargs) -> Optional[str]:
        """Checks if the user has manually corrected this input before."""
        f_code = kwargs.get("from_code") or kwargs.get("from_lang") or from_code
        t_code = kwargs.get("to_code") or kwargs.get("to_lang") or to_code
        norm = " ".join(turkish_lower(text).split())
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT corrected_text FROM user_corrections
            WHERE input_lower = ? AND from_code = ? AND to_code = ?
            LIMIT 1;
        """, (norm, f_code, t_code))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    def save_correction(
        self, 
        text: str = "", 
        from_code: str = "auto", 
        to_code: str = "auto", 
        corrected_text: str = "",
        **kwargs
    ):
        """
        Saves user's manual correction for a sentence or phrase.
        Also updates translation_cache with highest confidence (100%).
        """
        clean_input = (kwargs.get("source_text") or text).strip()
        clean_corr = (kwargs.get("corrected_text") or corrected_text).strip()
        f_code = kwargs.get("from_code") or kwargs.get("from_lang") or from_code
        t_code = kwargs.get("to_code") or kwargs.get("to_lang") or to_code
        if not clean_input or not clean_corr:
            return

        norm = " ".join(turkish_lower(clean_input).split())

        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_corrections (
                input_lower, from_code, to_code, original_input, corrected_text, created_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(input_lower, from_code, to_code) DO UPDATE SET
                corrected_text = excluded.corrected_text,
                original_input = excluded.original_input,
                created_at = CURRENT_TIMESTAMP;
        """, (norm, f_code, t_code, clean_input, clean_corr))
        conn.commit()
        conn.close()

        # Update cache as well
        self.set_cached_translation(
            clean_input, f_code, t_code, clean_corr,
            breakdown=[{"original": clean_input, "translated": clean_corr, "role": "user_correction", "pos": "corrected"}],
            confidence=100, engine="user_correction"
        )

    def get_all_corrections(self) -> List[Dict[str, Any]]:
        """Returns all user corrections ordered by date."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, original_input, from_code, to_code, corrected_text, created_at
            FROM user_corrections
            ORDER BY created_at DESC;
        """)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def delete_correction(self, correction_id: int):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM user_corrections WHERE id = ?;", (correction_id,))
        conn.commit()
        conn.close()

    # =========================================================================
    # 3. USER GLOSSARY METHODS (Custom Terminology)
    # =========================================================================
    def get_glossary_terms(self, lang_pair: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns list of custom user glossary terms."""
        conn = self._get_connection()
        cur = conn.cursor()
        if lang_pair and lang_pair != "any":
            cur.execute("""
                SELECT id, source_term, target_term, lang_pair, case_sensitive, notes, created_at
                FROM user_glossary
                WHERE lang_pair = ? OR lang_pair = 'any'
                ORDER BY length(source_term) DESC;
            """, (lang_pair,))
        else:
            cur.execute("""
                SELECT id, source_term, target_term, lang_pair, case_sensitive, notes, created_at
                FROM user_glossary
                ORDER BY length(source_term) DESC;
            """)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def add_glossary_term(
        self, 
        source_term: str, 
        target_term: str, 
        lang_pair: str = "any", 
        case_sensitive: bool = False, 
        notes: str = ""
    ) -> int:
        """Adds or updates a custom term in user glossary. Returns inserted row ID."""
        src = source_term.strip()
        tgt = target_term.strip()
        if not src or not tgt:
            return 0

        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_glossary (
                source_term, target_term, lang_pair, case_sensitive, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
        """, (src, tgt, lang_pair, 1 if case_sensitive else 0, notes.strip()))
        conn.commit()
        last_id = cur.lastrowid
        conn.close()
        return last_id

    def delete_glossary_term(self, term_id: int) -> bool:
        """Deletes a glossary term by its ID. Returns True if deleted."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM user_glossary WHERE id = ?;", (term_id,))
        conn.commit()
        cnt = cur.rowcount
        conn.close()
        return cnt > 0

    def apply_glossary_to_text(self, text: str, from_code: str = "auto", to_code: str = "auto", **kwargs) -> str:
        """
        Replaces custom glossary terms found in text with their user-specified definitions.
        Longer terms match first to prevent partial overlaps.
        """
        f_code = kwargs.get("from_code") or kwargs.get("from_lang") or from_code
        t_code = kwargs.get("to_code") or kwargs.get("to_lang") or to_code
        pair = f"{f_code}_{t_code}"
        terms = self.get_glossary_terms(lang_pair=pair)
        if not terms:
            return text

        import re
        result = text
        for t in terms:
            src = t["source_term"]
            tgt = t["target_term"]
            is_case = bool(t.get("case_sensitive", False))
            flags = 0 if is_case else re.IGNORECASE
            pattern = r"\b" + re.escape(src) + r"\b"
            result = re.sub(pattern, tgt, result, flags=flags)

        return result
