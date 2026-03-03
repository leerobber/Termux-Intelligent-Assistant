"""
Lightweight conversation memory backed by SQLite (built-in).

Uses a relative path (resolved via paths.py) so there are no hardcoded paths.
Keeps only the last *max_history* messages to limit RAM usage on mobile.
"""
import sqlite3
from typing import Iterator

from assistant.utils.paths import HISTORY_FILE, ensure_data_dir

_SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    role      TEXT NOT NULL,
    content   TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


class Memory:
    """Manages conversation history in a lightweight SQLite database."""

    def __init__(self, max_history: int = 20) -> None:
        ensure_data_dir()
        self._path = HISTORY_FILE
        self._max = max_history
        self._conn = sqlite3.connect(str(self._path))
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    # ------------------------------------------------------------------
    def add(self, role: str, content: str) -> None:
        """Append a message and prune old ones to stay within *max_history*."""
        self._conn.execute(
            "INSERT INTO history (role, content) VALUES (?, ?)", (role, content)
        )
        # Delete oldest rows that exceed the cap
        self._conn.execute(
            """
            DELETE FROM history WHERE id IN (
                SELECT id FROM history ORDER BY id ASC
                LIMIT MAX(0, (SELECT COUNT(*) FROM history) - ?)
            )
            """,
            (self._max,),
        )
        self._conn.commit()

    def recent(self, n: int | None = None) -> list[dict[str, str]]:
        """Return the *n* most recent messages as {role, content} dicts."""
        limit = n or self._max
        cur = self._conn.execute(
            "SELECT role, content FROM history ORDER BY id ASC LIMIT ?", (limit,)
        )
        return [{"role": row[0], "content": row[1]} for row in cur.fetchall()]

    def clear(self) -> None:
        """Wipe conversation history."""
        self._conn.execute("DELETE FROM history")
        self._conn.commit()

    def __iter__(self) -> Iterator[dict[str, str]]:
        return iter(self.recent())

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "Memory":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
