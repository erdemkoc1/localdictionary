"""Build a clean, redistributable SQLite dictionary database.

The build is offline, removes legacy definition tables, optionally removes
source-specific categories, deduplicates rows, and verifies SQLite integrity.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import sqlite3
from pathlib import Path
from typing import Sequence

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE_DIR / "data" / "dictionary.db"
DEFAULT_OUTPUT = BASE_DIR / "data" / "dictionary.public.db"


def build_database(
    input_path: Path,
    output_path: Path,
    excluded_categories: Sequence[str] = (),
) -> dict[str, int]:
    if input_path.resolve() == output_path.resolve():
        raise SystemExit("Input and output must be different files")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output_path.with_suffix(output_path.suffix + ".tmp")
    temp_output.unlink(missing_ok=True)
    shutil.copy2(input_path, temp_output)

    conn = sqlite3.connect(temp_output, timeout=60)
    try:
        conn.execute("PRAGMA journal_mode = OFF")
        conn.execute("PRAGMA synchronous = OFF")
        conn.execute("PRAGMA temp_store = MEMORY")
        before = conn.execute("SELECT COUNT(*) FROM bilingual").fetchone()[0]

        conn.execute("DROP TABLE IF EXISTS tr_definitions")
        conn.execute("DROP TABLE IF EXISTS en_definitions")
        removed_excluded = 0
        for category in excluded_categories:
            removed_excluded += conn.execute(
                "DELETE FROM bilingual WHERE category = ?", (category,)
            ).rowcount

        conn.execute("""
            DELETE FROM bilingual
            WHERE id NOT IN (
                SELECT MIN(id) FROM bilingual
                GROUP BY
                    COALESCE(en_lower, ''), COALESCE(tr_lower, ''),
                    COALESCE(type, ''), COALESCE(category, '')
            )
        """)
        after = conn.execute("SELECT COUNT(*) FROM bilingual").fetchone()[0]

        conn.execute("""
            CREATE TABLE IF NOT EXISTS db_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        metadata = {
            "schema_version": "2",
            "dataset_kind": "full-offline-release",
            "built_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "bilingual_records": str(after),
            "release_exclusions_applied": "1",
            "source_and_license_manifest": "DATA_LICENSES.md",
        }
        conn.executemany(
            "INSERT OR REPLACE INTO db_metadata (key, value) VALUES (?, ?)",
            sorted(metadata.items()),
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bi_en ON bilingual(en_lower)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bi_tr ON bilingual(tr_lower)")
        conn.commit()
        conn.execute("VACUUM")
        quick_check = conn.execute("PRAGMA quick_check").fetchone()[0]
        if quick_check != "ok":
            raise RuntimeError(f"SQLite quick_check failed: {quick_check}")
        conn.commit()
    except Exception:
        conn.close()
        temp_output.unlink(missing_ok=True)
        raise
    else:
        conn.close()

    os.replace(temp_output, output_path)
    return {
        "before": int(before),
        "excluded_rows_removed": int(removed_excluded),
        "duplicates_removed": int(before - removed_excluded - after),
        "after": int(after),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--exclude-category",
        action="append",
        default=[],
        help="Remove a source-specific category; may be repeated",
    )
    args = parser.parse_args()
    stats = build_database(args.input, args.output, args.exclude_category)
    print("Public database created:", args.output)
    for key, value in stats.items():
        print(f"{key}: {value:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
