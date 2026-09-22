import os
import sys
import sqlite3
from typing import List, Dict, Any, Optional

class HistoryManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            if getattr(sys, 'frozen', False):
                # When frozen as an exe, store history.db right next to the exe
                exe_dir = os.path.dirname(sys.executable)
                db_path = os.path.join(exe_dir, "history.db")
            else:
                # In development mode, store in data/history.db
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                data_dir = os.path.join(base_dir, "data")
                os.makedirs(data_dir, exist_ok=True)
                db_path = os.path.join(data_dir, "history.db")

        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT UNIQUE NOT NULL,
            direction TEXT NOT NULL,
            result_count INTEGER DEFAULT 0,
            last_searched TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now'))
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_hist_time ON search_history(last_searched DESC, id DESC);")
        conn.commit()
        conn.close()

    def add_search(self, query: str, direction: str, result_count: int = 0):
        """Add or update a search term in history."""
        q = query.strip()
        if not q or len(q) < 2:
            return

        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO search_history (query, direction, result_count, last_searched)
        VALUES (?, ?, ?, strftime('%Y-%m-%d %H:%M:%f', 'now'))
        ON CONFLICT(query) DO UPDATE SET
            direction = excluded.direction,
            result_count = excluded.result_count,
            last_searched = strftime('%Y-%m-%d %H:%M:%f', 'now');
        """, (q, direction, result_count))
        conn.commit()
        conn.close()

    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of recent searches ordered by last_searched descending."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT query, direction, result_count, 
               datetime(last_searched, 'localtime') as search_time
        FROM search_history
        ORDER BY last_searched DESC, id DESC
        LIMIT ?;
        """, (limit,))
        rows = cur.fetchall()
        results = [dict(r) for r in rows]
        conn.close()
        return results

    def delete_search(self, query: str):
        """Delete a specific search term from history."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM search_history WHERE query = ?;", (query.strip(),))
        conn.commit()
        conn.close()

    def clear_all(self):
        """Clear all search history."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM search_history;")
        conn.commit()
        conn.close()
