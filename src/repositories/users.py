"""Repositório de usuários."""

from __future__ import annotations

import sqlite3
from typing import Any

ROLES = ("admin", "editor", "viewer")


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def create_user(
    connection: sqlite3.Connection,
    username: str,
    password_hash: str,
    role: str,
) -> dict[str, Any]:
    cursor = connection.execute(
        """
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
        """,
        (username, password_hash, role),
    )
    row = connection.execute(
        """
        SELECT id, username, role, is_active, created_at, updated_at
        FROM users
        WHERE id = ?
        """,
        (cursor.lastrowid,),
    ).fetchone()
    if row is None:
        raise RuntimeError("Usuário criado não foi encontrado.")
    return _row_to_dict(row)


def get_user_by_username(
    connection: sqlite3.Connection,
    username: str,
) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
        (username,),
    ).fetchone()
    return None if row is None else _row_to_dict(row)


def list_users(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT id, username, role, is_active, created_at, updated_at
        FROM users
        ORDER BY id
        """
    ).fetchall()
    return [_row_to_dict(row) for row in rows]
