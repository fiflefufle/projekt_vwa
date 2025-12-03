import sqlite3
from contextlib import contextmanager
from typing import Iterator

DB_PATH = "app/app.db"

@contextmanager
def open_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,   # ← DŮLEŽITÉ: povolí použití v jiném vlákně
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
    finally:
        conn.close()
