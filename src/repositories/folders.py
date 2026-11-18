"""Repositório da árvore de pastas virtuais."""

from __future__ import annotations

import sqlite3
from typing import Any

from src.db.schema import INBOX_FOLDER_SETTING, ROOT_FOLDER_SETTING
from src.repositories import settings as settings_repository


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def create(
    connection: sqlite3.Connection,
    parent_id: int | None,
    name: str,
    name_key: str,
) -> dict[str, Any]:
    cursor = connection.execute(
        """
        INSERT INTO folders (parent_id, name, name_key)
        VALUES (?, ?, ?)
        """,
        (parent_id, name, name_key),
    )
    folder = get(connection, int(cursor.lastrowid))
    if folder is None:
        raise RuntimeError("Pasta criada não foi encontrada.")
    return folder


def get(connection: sqlite3.Connection, folder_id: int) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM folders WHERE id = ?",
        (folder_id,),
    ).fetchone()
    return None if row is None else _row_to_dict(row)


def list_children(connection: sqlite3.Connection, parent_id: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT * FROM folders
        WHERE parent_id = ?
        ORDER BY name_key ASC
        """,
        (parent_id,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def rename(
    connection: sqlite3.Connection,
    folder_id: int,
    name: str,
    name_key: str,
    updated_at: str,
) -> dict[str, Any]:
    connection.execute(
        """
        UPDATE folders
        SET name = ?, name_key = ?, updated_at = ?
        WHERE id = ?
        """,
        (name, name_key, updated_at, folder_id),
    )
    folder = get(connection, folder_id)
    if folder is None:
        raise RuntimeError("Pasta renomeada não foi encontrada.")
    return folder


def move(
    connection: sqlite3.Connection,
    folder_id: int,
    parent_id: int,
    updated_at: str,
) -> dict[str, Any]:
    connection.execute(
        """
        UPDATE folders
        SET parent_id = ?, updated_at = ?
        WHERE id = ?
        """,
        (parent_id, updated_at, folder_id),
    )
    folder = get(connection, folder_id)
    if folder is None:
        raise RuntimeError("Pasta movida não foi encontrada.")
    return folder


def delete(connection: sqlite3.Connection, folder_id: int) -> None:
    connection.execute("DELETE FROM folders WHERE id = ?", (folder_id,))


def count_children(connection: sqlite3.Connection, folder_id: int) -> tuple[int, int]:
    folder_count = connection.execute(
        "SELECT COUNT(*) AS total FROM folders WHERE parent_id = ?",
        (folder_id,),
    ).fetchone()["total"]
    file_count = connection.execute(
        "SELECT COUNT(*) AS total FROM files WHERE folder_id = ?",
        (folder_id,),
    ).fetchone()["total"]
    return int(folder_count), int(file_count)


def get_root_id(connection: sqlite3.Connection) -> int | None:
    configured = settings_repository.get_int(connection, ROOT_FOLDER_SETTING)
    if configured is not None:
        return configured
    row = connection.execute(
        "SELECT id FROM folders WHERE parent_id IS NULL"
    ).fetchone()
    return None if row is None else int(row["id"])


def get_inbox_id(connection: sqlite3.Connection) -> int | None:
    configured = settings_repository.get_int(connection, INBOX_FOLDER_SETTING)
    if configured is not None:
        return configured
    row = connection.execute(
        "SELECT id FROM folders WHERE name_key = 'para organizar' AND parent_id IS NOT NULL"
    ).fetchone()
    return None if row is None else int(row["id"])


def breadcrumbs(connection: sqlite3.Connection, folder_id: int) -> list[dict[str, Any]]:
    """Retorna a linhagem da raiz até a pasta informada."""
    rows = connection.execute(
        """
        WITH RECURSIVE chain (id, parent_id, name, depth) AS (
            SELECT id, parent_id, name, 0
            FROM folders
            WHERE id = ?
            UNION ALL
            SELECT parent.id, parent.parent_id, parent.name, chain.depth + 1
            FROM folders AS parent
            JOIN chain ON parent.id = chain.parent_id
        )
        SELECT id, parent_id, name
        FROM chain
        ORDER BY depth DESC
        """,
        (folder_id,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def is_in_subtree(
    connection: sqlite3.Connection,
    root_id: int,
    candidate_id: int,
) -> bool:
    row = connection.execute(
        """
        WITH RECURSIVE subtree (id) AS (
            SELECT id FROM folders WHERE id = ?
            UNION ALL
            SELECT child.id
            FROM folders AS child
            JOIN subtree ON child.parent_id = subtree.id
        )
        SELECT 1 FROM subtree WHERE id = ? LIMIT 1
        """,
        (root_id, candidate_id),
    ).fetchone()
    return row is not None
