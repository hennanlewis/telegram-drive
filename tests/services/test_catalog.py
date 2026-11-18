"""Serviços do catálogo: pastas, arquivos, lixeira e auditoria."""

from __future__ import annotations

from pathlib import Path

import pytest
from src.db.connection import connect
from src.repositories import activity as activity_repository
from src.services.catalog import files as files_service
from src.services.catalog import folders as folders_service
from src.services.catalog import paths
from src.services.catalog.errors import (
    FolderNotEmptyError,
    InvalidMoveError,
    InvalidStateError,
    NameConflictError,
    NotFoundError,
    ProtectedFolderError,
)


@pytest.fixture
def root_id(database_path: Path) -> int:
    return folders_service.get_root_id(database_path)


@pytest.fixture
def inbox_id(database_path: Path) -> int:
    return folders_service.get_inbox_id(database_path)


def test_create_and_list_nested_folders(database_path: Path, root_id: int) -> None:
    movies = folders_service.create_folder(database_path, root_id, "Filmes")
    series = folders_service.create_folder(database_path, int(movies["id"]), "Séries")
    season = folders_service.create_folder(database_path, int(series["id"]), "Temporada 1")

    listing = folders_service.list_folder(database_path, int(season["id"]))

    assert [item["name"] for item in listing["breadcrumbs"]] == [
        "Raiz",
        "Filmes",
        "Séries",
        "Temporada 1",
    ]
    assert folders_service.folder_path(database_path, int(season["id"])) == (
        "Raiz / Filmes / Séries / Temporada 1"
    )
    with connect(database_path) as connection:
        assert paths.folder_manifest_path(connection, int(season["id"])) == (
            "Filmes/Séries/Temporada 1"
        )


def test_duplicate_folder_name_in_same_parent_fails(
    database_path: Path,
    root_id: int,
) -> None:
    folders_service.create_folder(database_path, root_id, "Filmes")

    for variant in ("Filmes", "filmes", "FILMES"):
        with pytest.raises(NameConflictError):
            folders_service.create_folder(database_path, root_id, variant)


def test_same_folder_name_in_other_parent_is_allowed(
    database_path: Path,
    root_id: int,
) -> None:
    movies = folders_service.create_folder(database_path, root_id, "Filmes")
    series = folders_service.create_folder(database_path, root_id, "Séries")

    folders_service.create_folder(database_path, int(movies["id"]), "Extras")
    folders_service.create_folder(database_path, int(series["id"]), "Extras")


def test_listing_orders_folders_first_then_files_by_name(
    database_path: Path,
    root_id: int,
) -> None:
    folders_service.create_folder(database_path, root_id, "zeta")
    folders_service.create_folder(database_path, root_id, "Alfa")
    files_service.create_file(database_path, root_id, "beta.mkv", "video/x-matroska", 1)
    files_service.create_file(database_path, root_id, "Ametista.mkv", "video/x-matroska", 1)

    items = folders_service.list_folder(database_path, root_id)["items"]

    assert [(item["kind"], item["name"]) for item in items] == [
        ("folder", "Alfa"),
        ("folder", "Para organizar"),
        ("folder", "zeta"),
        ("file", "Ametista.mkv"),
        ("file", "beta.mkv"),
    ]


def test_rename_folder_updates_path_and_invalidates_manifest(
    database_path: Path,
    root_id: int,
) -> None:
    folder = folders_service.create_folder(database_path, root_id, "Filmes")
    file = files_service.create_file(
        database_path,
        int(folder["id"]),
        "movie.mkv",
        "video/x-matroska",
        1,
    )
    with connect(database_path) as connection:
        connection.execute(
            "UPDATE files SET manifest_synced_at = '2026-01-01T00:00:00Z' WHERE id = ?",
            (file["id"],),
        )

    folders_service.rename_folder(database_path, int(folder["id"]), "Longas")

    assert folders_service.folder_path(database_path, int(folder["id"])) == "Raiz / Longas"
    with connect(database_path) as connection:
        synced = connection.execute(
            "SELECT manifest_synced_at FROM files WHERE id = ?",
            (file["id"],),
        ).fetchone()["manifest_synced_at"]
        assert synced is None
        actions = [
            row["action"]
            for row in activity_repository.list_recent(connection, limit=10)
        ]
    assert "rename" in actions


def test_rename_folder_to_existing_name_fails(database_path: Path, root_id: int) -> None:
    folders_service.create_folder(database_path, root_id, "Filmes")
    series = folders_service.create_folder(database_path, root_id, "Séries")

    with pytest.raises(NameConflictError):
        folders_service.rename_folder(database_path, int(series["id"]), "filmes")


def test_root_and_inbox_are_protected(database_path: Path, root_id: int, inbox_id: int) -> None:
    with pytest.raises(ProtectedFolderError):
        folders_service.rename_folder(database_path, root_id, "Outra")

    with pytest.raises(ProtectedFolderError):
        folders_service.delete_folder(database_path, root_id)

    with pytest.raises(ProtectedFolderError):
        folders_service.rename_folder(database_path, inbox_id, "Entrada")

    with pytest.raises(ProtectedFolderError):
        folders_service.delete_folder(database_path, inbox_id)

    extra = folders_service.create_folder(database_path, inbox_id, "subpasta")
    with pytest.raises(ProtectedFolderError):
        folders_service.move_folder(database_path, inbox_id, int(extra["id"]))


def test_move_folder_updates_parent(database_path: Path, root_id: int) -> None:
    movies = folders_service.create_folder(database_path, root_id, "Filmes")
    archive = folders_service.create_folder(database_path, root_id, "Arquivo")

    moved = folders_service.move_folder(
        database_path,
        int(movies["id"]),
        int(archive["id"]),
    )

    assert moved["parent_id"] == archive["id"]
    assert folders_service.folder_path(database_path, int(moved["id"])) == (
        "Raiz / Arquivo / Filmes"
    )


def test_move_folder_to_itself_or_descendant_fails(
    database_path: Path,
    root_id: int,
) -> None:
    parent = folders_service.create_folder(database_path, root_id, "Filmes")
    child = folders_service.create_folder(database_path, int(parent["id"]), "Séries")
    grandchild = folders_service.create_folder(database_path, int(child["id"]), "Temporada")

    for destination in (parent, child, grandchild):
        with pytest.raises(InvalidMoveError):
            folders_service.move_folder(
                database_path,
                int(parent["id"]),
                int(destination["id"]),
            )


def test_move_folder_to_duplicate_name_fails(database_path: Path, root_id: int) -> None:
    destination = folders_service.create_folder(database_path, root_id, "Arquivo")
    folders_service.create_folder(database_path, int(destination["id"]), "Filmes")
    movies = folders_service.create_folder(database_path, root_id, "Filmes")

    with pytest.raises(NameConflictError):
        folders_service.move_folder(
            database_path,
            int(movies["id"]),
            int(destination["id"]),
        )


def test_delete_empty_folder_succeeds(database_path: Path, root_id: int) -> None:
    folder = folders_service.create_folder(database_path, root_id, "Vazia")

    folders_service.delete_folder(database_path, int(folder["id"]))

    with pytest.raises(NotFoundError):
        folders_service.list_folder(database_path, int(folder["id"]))


def test_delete_folder_with_content_fails(database_path: Path, root_id: int) -> None:
    folder = folders_service.create_folder(database_path, root_id, "Cheia")
    folders_service.create_folder(database_path, int(folder["id"]), "Subpasta")

    with pytest.raises(FolderNotEmptyError):
        folders_service.delete_folder(database_path, int(folder["id"]))

    other = folders_service.create_folder(database_path, root_id, "ComArquivo")
    files_service.create_file(
        database_path,
        int(other["id"]),
        "movie.mkv",
        "video/x-matroska",
        1,
    )

    with pytest.raises(FolderNotEmptyError):
        folders_service.delete_folder(database_path, int(other["id"]))


def test_file_move_rename_and_listing(database_path: Path, root_id: int) -> None:
    movies = folders_service.create_folder(database_path, root_id, "Filmes")
    series = folders_service.create_folder(database_path, root_id, "Séries")
    file = files_service.create_file(
        database_path,
        int(movies["id"]),
        "piloto.mkv",
        "video/x-matroska",
        1024,
    )

    renamed = files_service.rename_file(database_path, int(file["id"]), "episodio.mkv")
    moved = files_service.move_file(database_path, int(file["id"]), int(series["id"]))

    assert renamed["name"] == "episodio.mkv"
    assert moved["folder_id"] == series["id"]
    assert folders_service.list_folder(database_path, int(movies["id"]))["items"] == []
    assert [
        item["name"] for item in folders_service.list_folder(
            database_path,
            int(series["id"]),
        )["items"]
    ] == ["episodio.mkv"]


def test_trash_hides_file_and_restore_returns_to_origin(
    database_path: Path,
    root_id: int,
) -> None:
    folder = folders_service.create_folder(database_path, root_id, "Filmes")
    file = files_service.create_file(
        database_path,
        int(folder["id"]),
        "movie.mkv",
        "video/x-matroska",
        1024,
    )

    trashed = files_service.trash_file(database_path, int(file["id"]))

    assert trashed["status"] == "trashed"
    assert trashed["trashed_from_folder_id"] == folder["id"]
    assert folders_service.list_folder(database_path, int(folder["id"]))["items"] == []
    trash = files_service.list_trash(database_path)
    assert [(item["name"], item["trashed_from_name"]) for item in trash] == [
        ("movie.mkv", "Filmes")
    ]

    with pytest.raises(InvalidStateError):
        files_service.trash_file(database_path, int(file["id"]))
    with pytest.raises(InvalidStateError):
        files_service.rename_file(database_path, int(file["id"]), "outro.mkv")
    with pytest.raises(InvalidStateError):
        files_service.move_file(database_path, int(file["id"]), root_id)

    restored = files_service.restore_file(database_path, int(file["id"]))

    assert restored["status"] == "active"
    assert restored["folder_id"] == folder["id"]
    assert restored["trashed_from_folder_id"] is None
    assert restored["trashed_at"] is None
    assert [
        item["name"]
        for item in folders_service.list_folder(database_path, int(folder["id"]))["items"]
    ] == ["movie.mkv"]


def test_restore_fails_when_name_is_taken(database_path: Path, root_id: int) -> None:
    file = files_service.create_file(
        database_path,
        root_id,
        "movie.mkv",
        "video/x-matroska",
        1024,
    )
    files_service.trash_file(database_path, int(file["id"]))
    files_service.create_file(
        database_path,
        root_id,
        "movie.mkv",
        "video/x-matroska",
        2048,
    )

    with pytest.raises(NameConflictError):
        files_service.restore_file(database_path, int(file["id"]))


def test_duplicate_detection_uses_hash_and_size(database_path: Path, root_id: int) -> None:
    sha = "c" * 64
    first = files_service.create_file(
        database_path,
        root_id,
        "a.mkv",
        "video/x-matroska",
        1024,
        sha256=sha,
    )
    second = files_service.create_file(
        database_path,
        root_id,
        "b.mkv",
        "video/x-matroska",
        1024,
        sha256=sha,
    )
    files_service.create_file(
        database_path,
        root_id,
        "c.mkv",
        "video/x-matroska",
        2048,
        sha256=sha,
    )

    matches = files_service.find_duplicates(database_path, sha, 1024)

    assert [item["id"] for item in matches] == [first["id"], second["id"]]
    assert files_service.find_duplicates(database_path, sha.upper(), 1024) == matches


def test_audit_records_catalog_actions(database_path: Path, root_id: int) -> None:
    folder = folders_service.create_folder(database_path, root_id, "Filmes")
    file = files_service.create_file(
        database_path,
        int(folder["id"]),
        "movie.mkv",
        "video/x-matroska",
        1024,
    )
    files_service.rename_file(database_path, int(file["id"]), "filme.mkv")
    files_service.move_file(database_path, int(file["id"]), root_id)
    files_service.trash_file(database_path, int(file["id"]))
    files_service.restore_file(database_path, int(file["id"]))

    with connect(database_path) as connection:
        actions = [
            row["action"] for row in activity_repository.list_for_file(connection, int(file["id"]))
        ]

    assert actions == ["ingest", "rename", "move", "trash", "restore"]


def test_unknown_ids_raise_not_found(database_path: Path, root_id: int) -> None:
    with pytest.raises(NotFoundError):
        folders_service.list_folder(database_path, 99999)
    with pytest.raises(NotFoundError):
        files_service.get_file(database_path, 99999)
    with pytest.raises(NotFoundError):
        folders_service.create_folder(database_path, 99999, "Filmes")
