"""Repositório de configurações persistentes."""

from __future__ import annotations

import sqlite3


def get(connection: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    row = connection.execute(
        "SELECT value FROM settings WHERE key = ?",
        (key,),
    ).fetchone()
    return default if row is None else str(row["value"])


def set(connection: sqlite3.Connection, key: str, value: str) -> None:
    connection.execute(
        """
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT (key) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )


def get_int(connection: sqlite3.Connection, key: str) -> int | None:
    raw = get(connection, key)
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None
