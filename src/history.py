import os
import sqlite3
from typing import List, Dict, Any, Optional

from src.paths import migrate_legacy_user_file

MAX_HISTORY_QUERY_CHARS = 512
MAX_HISTORY_ROWS = 500


class HistoryManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(migrate_legacy_user_file("history.db"))
        else:
            parent = os.path.dirname(os.path.abspath(db_path))
            os.makedirs(parent, exist_ok=True)

        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
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
        q = query.strip()[:MAX_HISTORY_QUERY_CHARS]
        if not q or len(q) < 2 or "\x00" in q:
            return

        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM search_history WHERE query = ?;", (q,))
            cur.execute("""
            INSERT INTO search_history (query, direction, result_count)
            VALUES (?, ?, ?);
            """, (q, direction, max(0, min(int(result_count), 2_147_483_647))))
            cur.execute("""
            DELETE FROM search_history
            WHERE id NOT IN (
                SELECT id FROM search_history ORDER BY id DESC LIMIT ?
            )
            """, (MAX_HISTORY_ROWS,))
            conn.commit()
        finally:
            conn.close()

    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of recent searches ordered by id descending."""
        limit = max(1, min(int(limit), MAX_HISTORY_ROWS))
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT query, direction, result_count, 
               datetime(last_searched, 'localtime') as search_time
        FROM search_history
        ORDER BY id DESC
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
