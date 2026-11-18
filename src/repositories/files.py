"""Repositório de arquivos do catálogo."""

from __future__ import annotations

import sqlite3
from typing import Any

from src.db.schema import FILE_STATUS_ACTIVE, FILE_STATUS_MISSING, FILE_STATUS_TRASHED


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def create(
    connection: sqlite3.Connection,
    folder_id: int,
    name: str,
    name_key: str,
    mime: str,
    size_bytes: int,
    sha256: str | None,
    version: int,
    is_current: bool,
) -> dict[str, Any]:
    cursor = connection.execute(
        """
        INSERT INTO files (
            folder_id, name, name_key, mime, size_bytes, sha256, version, is_current
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            folder_id,
            name,
            name_key,
            mime,
            size_bytes,
            sha256,
            version,
            1 if is_current else 0,
        ),
    )
    file = get(connection, int(cursor.lastrowid))
    if file is None:
        raise RuntimeError("Arquivo criado não foi encontrado.")
    return file


def get(connection: sqlite3.Connection, file_id: int) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM files WHERE id = ?",
        (file_id,),
    ).fetchone()
    return None if row is None else _row_to_dict(row)


def list_in_folder(
    connection: sqlite3.Connection,
    folder_id: int,
    *,
    include_missing: bool = False,
) -> list[dict[str, Any]]:
    statuses = [FILE_STATUS_ACTIVE]
    if include_missing:
        statuses.append(FILE_STATUS_MISSING)
    placeholders = ", ".join("?" for _ in statuses)
    rows = connection.execute(
        f"""
        SELECT * FROM files
        WHERE folder_id = ? AND status IN ({placeholders})
        ORDER BY name_key ASC
        """,
        (folder_id, *statuses),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def list_trashed(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT * FROM files
        WHERE status = ?
        ORDER BY trashed_at DESC, name_key ASC
        """,
        (FILE_STATUS_TRASHED,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def find_by_hash(
    connection: sqlite3.Connection,
    sha256: str,
    size_bytes: int,
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT * FROM files
        WHERE sha256 = ? AND size_bytes = ? AND status = ?
        ORDER BY id ASC
        """,
        (sha256, size_bytes, FILE_STATUS_ACTIVE),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def rename(
    connection: sqlite3.Connection,
    file_id: int,
    name: str,
    name_key: str,
    updated_at: str,
) -> dict[str, Any]:
    connection.execute(
        """
        UPDATE files
        SET name = ?, name_key = ?, manifest_synced_at = NULL, updated_at = ?
        WHERE id = ?
        """,
        (name, name_key, updated_at, file_id),
    )
    file = get(connection, file_id)
    if file is None:
        raise RuntimeError("Arquivo renomeado não foi encontrado.")
    return file


def move(
    connection: sqlite3.Connection,
    file_id: int,
    folder_id: int,
    updated_at: str,
) -> dict[str, Any]:
    connection.execute(
        """
        UPDATE files
        SET folder_id = ?, manifest_synced_at = NULL, updated_at = ?
        WHERE id = ?
        """,
        (folder_id, updated_at, file_id),
    )
    file = get(connection, file_id)
    if file is None:
        raise RuntimeError("Arquivo movido não foi encontrado.")
    return file


def mark_trashed(
    connection: sqlite3.Connection,
    file_id: int,
    origin_folder_id: int,
    trashed_at: str,
) -> dict[str, Any]:
    connection.execute(
        """
        UPDATE files
        SET status = ?, trashed_from_folder_id = ?, trashed_at = ?, updated_at = ?
        WHERE id = ?
        """,
        (FILE_STATUS_TRASHED, origin_folder_id, trashed_at, trashed_at, file_id),
    )
    file = get(connection, file_id)
    if file is None:
        raise RuntimeError("Arquivo na lixeira não foi encontrado.")
    return file


def mark_restored(
    connection: sqlite3.Connection,
    file_id: int,
    folder_id: int,
    updated_at: str,
) -> dict[str, Any]:
    connection.execute(
        """
        UPDATE files
        SET status = ?, folder_id = ?, trashed_from_folder_id = NULL,
            trashed_at = NULL, manifest_synced_at = NULL, updated_at = ?
        WHERE id = ?
        """,
        (FILE_STATUS_ACTIVE, folder_id, updated_at, file_id),
    )
    file = get(connection, file_id)
    if file is None:
        raise RuntimeError("Arquivo restaurado não foi encontrado.")
    return file


def mark_manifest_pending_in_subtree(
    connection: sqlite3.Connection,
    folder_id: int,
) -> None:
    connection.execute(
        """
        WITH RECURSIVE subtree (id) AS (
            SELECT id FROM folders WHERE id = ?
            UNION ALL
            SELECT child.id
            FROM folders AS child
            JOIN subtree ON child.parent_id = subtree.id
        )
        UPDATE files
        SET manifest_synced_at = NULL
        WHERE folder_id IN (SELECT id FROM subtree)
        """,
        (folder_id,),
    )
