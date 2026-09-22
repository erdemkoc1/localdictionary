import os
import sqlite3
import time
from typing import List, Dict, Any, Optional, Tuple
from src.utils import turkish_lower, get_resource_path

TR_CHARS = set("çğıöşüÇĞİÖŞÜ")

class DictionaryDB:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = get_resource_path(os.path.join("data", "dictionary.db"))
        
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Veritabanı dosyası bulunamadı: {self.db_path}")

        # Connect to SQLite
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cur = self.conn.cursor()
        
        # High-performance read-only pragmas
        self.cur.execute("PRAGMA query_only = ON;")
        self.cur.execute("PRAGMA cache_size = 50000;")
        self.cur.execute("PRAGMA mmap_size = 268435456;") # 256MB memory map
        self.cur.execute("PRAGMA synchronous = OFF;")

    def detect_language(self, query: str) -> str:
        """Detect if input query is more likely Turkish or English."""
        # 1. Distinctive Turkish letters
        if any(c in TR_CHARS for c in query):
            return "tr"

        q_lower = turkish_lower(query)

        # 2. Check exact hit in EN vs TR
        self.cur.execute("SELECT 1 FROM bilingual WHERE en_lower = ? LIMIT 1;", (q_lower,))
        if self.cur.fetchone():
            return "en"

        self.cur.execute("SELECT 1 FROM bilingual WHERE tr_lower = ? LIMIT 1;", (q_lower,))
        if self.cur.fetchone():
            return "tr"

        # Default fallback to English
        return "en"

    def search(self, query: str, mode: str = "auto", limit: int = 100) -> Tuple[List[Dict[str, Any]], float, str]:
        """
        Search dictionary with sub-millisecond range/exact query.
        Returns: (results_list, elapsed_ms, detected_direction)
        """
        query = query.strip()
        if not query:
            return [], 0.0, ""

        t_start = time.perf_counter()
        q_lower = turkish_lower(query)

        # Determine search direction
        direction = mode
        if mode == "auto":
            lang = self.detect_language(query)
            direction = "en_tr" if lang == "en" else "tr_en"

        is_en = (direction == "en_tr")
        src_col = "en_lower" if is_en else "tr_lower"
        upper_bound = q_lower + "\uffff"

        # Query using B-Tree range & exact matching with prioritized sorting
        sql = f"""
        SELECT en, tr, type, category, {src_col}
        FROM bilingual
        WHERE {src_col} >= ? AND {src_col} < ?
        ORDER BY 
            CASE 
                WHEN {src_col} = ? THEN 0
                WHEN category = 'Common Usage' THEN 1
                WHEN category = 'General' THEN 2
                ELSE 3
            END,
            length({src_col}) ASC
        LIMIT ?;
        """

        self.cur.execute(sql, (q_lower, upper_bound, q_lower, limit))
        raw_rows = self.cur.fetchall()

        # If no results and mode was auto, try the other direction
        if not raw_rows and mode == "auto":
            alt_is_en = not is_en
            alt_src_col = "en_lower" if alt_is_en else "tr_lower"
            direction = "en_tr" if alt_is_en else "tr_en"
            alt_sql = f"""
            SELECT en, tr, type, category, {alt_src_col}
            FROM bilingual
            WHERE {alt_src_col} >= ? AND {alt_src_col} < ?
            ORDER BY 
                CASE 
                    WHEN {alt_src_col} = ? THEN 0
                    WHEN category = 'Common Usage' THEN 1
                    WHEN category = 'General' THEN 2
                    ELSE 3
                END,
                length({alt_src_col}) ASC
            LIMIT ?;
            """
            self.cur.execute(alt_sql, (q_lower, upper_bound, q_lower, limit))
            raw_rows = self.cur.fetchall()
            is_en = alt_is_en

        elapsed_ms = (time.perf_counter() - t_start) * 1000

        results = []
        for row in raw_rows:
            results.append({
                "source": row[0] if is_en else row[1],
                "target": row[1] if is_en else row[0],
                "type": row[2] or "-",
                "category": row[3] or "General",
                "direction": "EN ➔ TR" if is_en else "TR ➔ EN"
            })

        return results, elapsed_ms, "EN ➔ TR" if is_en else "TR ➔ EN"

    def get_tr_definitions(self, word: str) -> List[Dict[str, Optional[str]]]:
        """Fetch official TDK Turkish definitions, examples, and authors."""
        w_lower = turkish_lower(word.strip())
        self.cur.execute("""
        SELECT meaning, example, author 
        FROM tr_definitions 
        WHERE word_lower = ? 
        LIMIT 10;
        """, (w_lower,))
        rows = self.cur.fetchall()
        return [{"meaning": r[0], "example": r[1], "author": r[2]} for r in rows]

    def get_en_definition(self, word: str) -> Optional[str]:
        """Fetch Webster's English definition."""
        w_lower = word.strip().lower()
        self.cur.execute("""
        SELECT definition 
        FROM en_definitions 
        WHERE word_lower = ? 
        LIMIT 1;
        """, (w_lower,))
        row = self.cur.fetchone()
        return row[0] if row else None

    def close(self):
        if self.conn:
            self.conn.close()
