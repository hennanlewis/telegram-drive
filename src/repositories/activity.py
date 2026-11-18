"""Repositório de auditoria."""

from __future__ import annotations

import sqlite3
from typing import Any

AUDIT_ACTIONS = (
    "ingest",
    "move",
    "rename",
    "trash",
    "restore",
    "delete",
    "manifest",
    "duplicate",
)


def record(
    connection: sqlite3.Connection,
    action: str,
    *,
    file_id: int | None = None,
    folder_id: int | None = None,
    detail: str | None = None,
    result: str = "ok",
) -> int:
    if action not in AUDIT_ACTIONS:
        raise ValueError(f"Ação de auditoria inválida: {action!r}.")
    cursor = connection.execute(
        """
        INSERT INTO activity (action, file_id, folder_id, detail, result)
        VALUES (?, ?, ?, ?, ?)
        """,
        (action, file_id, folder_id, detail, result),
    )
    return int(cursor.lastrowid)


def list_recent(
    connection: sqlite3.Connection,
    limit: int = 50,
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT * FROM activity
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def list_for_file(
    connection: sqlite3.Connection,
    file_id: int,
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT * FROM activity
        WHERE file_id = ?
        ORDER BY id ASC
        """,
        (file_id,),
    ).fetchall()
    return [dict(row) for row in rows]
