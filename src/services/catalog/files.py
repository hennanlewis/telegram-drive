"""Regras de arquivos, lixeira e duplicados."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from src.db.connection import connect, transaction
from src.repositories import activity as activity_repository
from src.repositories import files as files_repository
from src.repositories import folders as folders_repository
from src.services.catalog import paths
from src.services.catalog.errors import (
    InvalidStateError,
    NameConflictError,
    NotFoundError,
)
from src.utils.time import utc_now_iso

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _require_folder(connection: sqlite3.Connection, folder_id: int) -> dict[str, Any]:
    folder = folders_repository.get(connection, folder_id)
    if folder is None:
        raise NotFoundError(f"Pasta {folder_id} não encontrada.")
    return folder


def _require_file(connection: sqlite3.Connection, file_id: int) -> dict[str, Any]:
    file = files_repository.get(connection, file_id)
    if file is None:
        raise NotFoundError(f"Arquivo {file_id} não encontrado.")
    return file


def _normalize_sha256(sha256: str | None) -> str | None:
    if sha256 is None or sha256 == "":
        return None
    normalized = sha256.strip().lower()
    if not SHA256_PATTERN.fullmatch(normalized):
        raise ValueError("O hash deve ser um SHA-256 em hexadecimal.")
    return normalized


def _validate_size(size_bytes: int) -> int:
    if isinstance(size_bytes, bool) or not isinstance(size_bytes, int):
        raise ValueError("O tamanho deve ser um inteiro.")
    if size_bytes < 0:
        raise ValueError("O tamanho não pode ser negativo.")
    return size_bytes


def _validate_version(version: int) -> int:
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise ValueError("A versão deve ser um inteiro maior ou igual a 1.")
    return version


def _detail(**values: Any) -> str:
    return json.dumps(values, ensure_ascii=False, sort_keys=True)


def create_file(
    database_path: Path,
    folder_id: int,
    name: str,
    mime: str,
    size_bytes: int,
    sha256: str | None = None,
    version: int = 1,
    is_current: bool = True,
) -> dict[str, Any]:
    normalized_name = paths.normalize_name(name)
    normalized_key = paths.name_key(normalized_name)
    normalized_mime = paths.validate_mime(mime)
    normalized_size = _validate_size(size_bytes)
    normalized_sha = _normalize_sha256(sha256)
    normalized_version = _validate_version(version)

    with connect(database_path) as connection, transaction(connection):
        _require_folder(connection, folder_id)
        try:
            file = files_repository.create(
                connection,
                folder_id,
                normalized_name,
                normalized_key,
                normalized_mime,
                normalized_size,
                normalized_sha,
                normalized_version,
                is_current,
            )
        except sqlite3.IntegrityError as exc:
            raise NameConflictError(
                f"Já existe um arquivo chamado {normalized_name!r} nessa pasta."
            ) from exc

        activity_repository.record(
            connection,
            "ingest",
            file_id=int(file["id"]),
            folder_id=folder_id,
            detail=_detail(name=normalized_name, sha256=normalized_sha),
        )
        return file


def get_file(database_path: Path, file_id: int) -> dict[str, Any]:
    with connect(database_path) as connection:
        return _require_file(connection, file_id)


def rename_file(database_path: Path, file_id: int, name: str) -> dict[str, Any]:
    normalized_name = paths.normalize_name(name)
    normalized_key = paths.name_key(normalized_name)

    with connect(database_path) as connection, transaction(connection):
        file = _require_file(connection, file_id)
        if file["status"] == "trashed":
            raise InvalidStateError("Restaure o arquivo antes de renomeá-lo.")

        if file["name"] == normalized_name:
            return file

        try:
            updated = files_repository.rename(
                connection,
                file_id,
                normalized_name,
                normalized_key,
                utc_now_iso(),
            )
        except sqlite3.IntegrityError as exc:
            raise NameConflictError(
                f"Já existe um arquivo chamado {normalized_name!r} nessa pasta."
            ) from exc

        activity_repository.record(
            connection,
            "rename",
            file_id=file_id,
            folder_id=int(file["folder_id"]),
            detail=_detail(old_name=file["name"], new_name=normalized_name),
        )
        return updated


def move_file(database_path: Path, file_id: int, folder_id: int) -> dict[str, Any]:
    with connect(database_path) as connection, transaction(connection):
        file = _require_file(connection, file_id)
        destination = _require_folder(connection, folder_id)
        if file["status"] == "trashed":
            raise InvalidStateError("Restaure o arquivo antes de movê-lo.")
        if int(file["folder_id"]) == folder_id:
            return file

        try:
            updated = files_repository.move(
                connection,
                file_id,
                folder_id,
                utc_now_iso(),
            )
        except sqlite3.IntegrityError as exc:
            raise NameConflictError(
                f"Já existe um arquivo chamado {file['name']!r} no destino."
            ) from exc

        activity_repository.record(
            connection,
            "move",
            file_id=file_id,
            folder_id=folder_id,
            detail=_detail(
                old_folder_id=file["folder_id"],
                new_folder_id=destination["id"],
            ),
        )
        return updated


def trash_file(database_path: Path, file_id: int) -> dict[str, Any]:
    with connect(database_path) as connection, transaction(connection):
        file = _require_file(connection, file_id)
        if file["status"] == "trashed":
            raise InvalidStateError("O arquivo já está na lixeira.")

        origin_folder_id = int(file["folder_id"])
        _require_folder(connection, origin_folder_id)
        updated = files_repository.mark_trashed(
            connection,
            file_id,
            origin_folder_id,
            utc_now_iso(),
        )
        activity_repository.record(
            connection,
            "trash",
            file_id=file_id,
            folder_id=origin_folder_id,
            detail=_detail(name=file["name"], origin_folder_id=origin_folder_id),
        )
        return updated


def restore_file(database_path: Path, file_id: int) -> dict[str, Any]:
    with connect(database_path) as connection, transaction(connection):
        file = _require_file(connection, file_id)
        if file["status"] != "trashed":
            raise InvalidStateError("O arquivo não está na lixeira.")

        origin_id = file["trashed_from_folder_id"]
        destination = (
            folders_repository.get(connection, int(origin_id))
            if origin_id is not None
            else None
        )
        if destination is None:
            root_id = folders_repository.get_root_id(connection)
            if root_id is None:
                raise NotFoundError("A pasta raiz não existe no catálogo.")
            destination = _require_folder(connection, root_id)

        try:
            updated = files_repository.mark_restored(
                connection,
                file_id,
                int(destination["id"]),
                utc_now_iso(),
            )
        except sqlite3.IntegrityError as exc:
            raise NameConflictError(
                f"Já existe um arquivo chamado {file['name']!r} no destino da restauração."
            ) from exc

        activity_repository.record(
            connection,
            "restore",
            file_id=file_id,
            folder_id=int(destination["id"]),
            detail=_detail(
                restored_to=int(destination["id"]),
                origin_folder_id=origin_id,
            ),
        )
        return updated


def list_trash(database_path: Path) -> list[dict[str, Any]]:
    with connect(database_path) as connection:
        trashed = files_repository.list_trashed(connection)
        folders_by_id = {
            int(folder["id"]): folder
            for folder in (
                folders_repository.get(connection, int(file["trashed_from_folder_id"]))
                for file in trashed
                if file["trashed_from_folder_id"] is not None
            )
            if folder is not None
        }

    result: list[dict[str, Any]] = []
    for file in trashed:
        origin_id = file["trashed_from_folder_id"]
        origin = folders_by_id.get(int(origin_id)) if origin_id is not None else None
        result.append(
            {
                **file,
                "trashed_from_name": None if origin is None else origin["name"],
            }
        )
    return result


def find_duplicates(
    database_path: Path,
    sha256: str,
    size_bytes: int,
) -> list[dict[str, Any]]:
    normalized_sha = _normalize_sha256(sha256)
    if normalized_sha is None:
        return []
    normalized_size = _validate_size(size_bytes)
    with connect(database_path) as connection:
        return files_repository.find_by_hash(connection, normalized_sha, normalized_size)
