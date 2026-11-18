"""Regras de pastas virtuais."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from src.db.connection import connect, transaction
from src.db.schema import INBOX_FOLDER_NAME
from src.repositories import activity as activity_repository
from src.repositories import files as files_repository
from src.repositories import folders as folders_repository
from src.services.catalog import paths
from src.services.catalog.errors import (
    FolderNotEmptyError,
    InvalidMoveError,
    NameConflictError,
    NotFoundError,
    ProtectedFolderError,
)
from src.utils.time import utc_now_iso


def _require_folder(connection: sqlite3.Connection, folder_id: int) -> dict[str, Any]:
    folder = folders_repository.get(connection, folder_id)
    if folder is None:
        raise NotFoundError(f"Pasta {folder_id} não encontrada.")
    return folder


def _root_id(connection: sqlite3.Connection) -> int:
    root_id = folders_repository.get_root_id(connection)
    if root_id is None:
        raise NotFoundError("A pasta raiz não existe no catálogo.")
    return root_id


def _inbox_id(connection: sqlite3.Connection) -> int:
    inbox_id = folders_repository.get_inbox_id(connection)
    if inbox_id is None:
        raise NotFoundError("A pasta Inbox não existe no catálogo.")
    return inbox_id


def _assert_not_protected(connection: sqlite3.Connection, folder: dict[str, Any]) -> None:
    if folder["parent_id"] is None:
        raise ProtectedFolderError("A raiz não pode ser alterada.")
    if int(folder["id"]) == _inbox_id(connection):
        raise ProtectedFolderError(f"A pasta {INBOX_FOLDER_NAME!r} é reservada.")


def _detail(**values: Any) -> str:
    return json.dumps(values, ensure_ascii=False, sort_keys=True)


def create_folder(database_path: Path, parent_id: int, name: str) -> dict[str, Any]:
    normalized_name = paths.normalize_name(name)
    normalized_key = paths.name_key(normalized_name)

    with connect(database_path) as connection, transaction(connection):
        _require_folder(connection, parent_id)
        try:
            return folders_repository.create(
                connection,
                parent_id,
                normalized_name,
                normalized_key,
            )
        except sqlite3.IntegrityError as exc:
            raise NameConflictError(
                f"Já existe uma pasta chamada {normalized_name!r} nesse destino."
            ) from exc


def list_folder(database_path: Path, folder_id: int) -> dict[str, Any]:
    with connect(database_path) as connection:
        folder = _require_folder(connection, folder_id)
        breadcrumb = paths.breadcrumbs(connection, folder_id)
        child_folders = folders_repository.list_children(connection, folder_id)
        child_files = files_repository.list_in_folder(connection, folder_id)

    items: list[dict[str, Any]] = [
        {
            "id": child["id"],
            "name": child["name"],
            "kind": "folder",
            "status": "active",
            "in_trash": False,
            "size_bytes": None,
            "mime": None,
            "updated_at": child["updated_at"],
        }
        for child in child_folders
    ]
    items.extend(
        {
            "id": child["id"],
            "name": child["name"],
            "kind": "file",
            "status": child["status"],
            "in_trash": child["status"] == "trashed",
            "size_bytes": child["size_bytes"],
            "mime": child["mime"],
            "updated_at": child["updated_at"],
        }
        for child in child_files
    )

    return {
        "folder": {
            "id": folder["id"],
            "parent_id": folder["parent_id"],
            "name": folder["name"],
        },
        "breadcrumbs": breadcrumb,
        "items": items,
    }


def rename_folder(database_path: Path, folder_id: int, name: str) -> dict[str, Any]:
    normalized_name = paths.normalize_name(name)
    normalized_key = paths.name_key(normalized_name)

    with connect(database_path) as connection, transaction(connection):
        folder = _require_folder(connection, folder_id)
        _assert_not_protected(connection, folder)

        if folder["name_key"] == normalized_key and folder["name"] == normalized_name:
            return folder

        try:
            updated = folders_repository.rename(
                connection,
                folder_id,
                normalized_name,
                normalized_key,
                utc_now_iso(),
            )
        except sqlite3.IntegrityError as exc:
            raise NameConflictError(
                f"Já existe uma pasta chamada {normalized_name!r} nesse destino."
            ) from exc

        files_repository.mark_manifest_pending_in_subtree(connection, folder_id)
        activity_repository.record(
            connection,
            "rename",
            folder_id=folder_id,
            detail=_detail(old_name=folder["name"], new_name=normalized_name),
        )
        return updated


def move_folder(database_path: Path, folder_id: int, parent_id: int) -> dict[str, Any]:
    with connect(database_path) as connection, transaction(connection):
        folder = _require_folder(connection, folder_id)
        destination = _require_folder(connection, parent_id)
        _assert_not_protected(connection, folder)

        if int(folder["parent_id"] or 0) == parent_id:
            return folder

        if folders_repository.is_in_subtree(connection, folder_id, parent_id):
            raise InvalidMoveError("Uma pasta não pode ser movida para dentro de si mesma.")

        try:
            updated = folders_repository.move(
                connection,
                folder_id,
                destination["id"],
                utc_now_iso(),
            )
        except sqlite3.IntegrityError as exc:
            raise NameConflictError(
                f"Já existe uma pasta chamada {folder['name']!r} no destino."
            ) from exc

        files_repository.mark_manifest_pending_in_subtree(connection, folder_id)
        activity_repository.record(
            connection,
            "move",
            folder_id=folder_id,
            detail=_detail(
                old_parent_id=folder["parent_id"],
                new_parent_id=parent_id,
            ),
        )
        return updated


def delete_folder(database_path: Path, folder_id: int) -> None:
    with connect(database_path) as connection, transaction(connection):
        folder = _require_folder(connection, folder_id)
        _assert_not_protected(connection, folder)

        child_folders, child_files = folders_repository.count_children(connection, folder_id)
        if child_folders or child_files:
            raise FolderNotEmptyError(
                f"A pasta {folder['name']!r} não está vazia e não pode ser excluída."
            )

        detail = _detail(folder_id=folder["id"], name=folder["name"])
        folders_repository.delete(connection, folder_id)
        activity_repository.record(
            connection,
            "delete",
            detail=detail,
        )


def get_root_id(database_path: Path) -> int:
    with connect(database_path) as connection:
        return _root_id(connection)


def get_inbox_id(database_path: Path) -> int:
    with connect(database_path) as connection:
        return _inbox_id(connection)


def folder_path(database_path: Path, folder_id: int) -> str:
    with connect(database_path) as connection:
        return paths.folder_display_path(connection, folder_id)
