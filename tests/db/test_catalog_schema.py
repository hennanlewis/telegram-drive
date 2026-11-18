"""Constraints do schema do catálogo, testadas diretamente no banco."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from src.db.connection import connect
from src.services.catalog import files as files_service
from src.services.catalog import folders as folders_service
from src.services.catalog.errors import NameConflictError


def _root_id(database_path: Path) -> int:
    return folders_service.get_root_id(database_path)


def _inbox_id(database_path: Path) -> int:
    return folders_service.get_inbox_id(database_path)


def test_schema_has_catalog_tables(database_path: Path) -> None:
    with connect(database_path) as connection:
        names = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert {
        "users",
        "settings",
        "folders",
        "files",
        "telegram_refs",
        "subtitles",
        "favorites",
        "activity",
        "scan_state",
    } <= names


def test_root_and_inbox_are_reserved(database_path: Path) -> None:
    root_id = _root_id(database_path)
    inbox_id = _inbox_id(database_path)

    with connect(database_path) as connection:
        root = connection.execute(
            "SELECT * FROM folders WHERE id = ?",
            (root_id,),
        ).fetchone()
        inbox = connection.execute(
            "SELECT * FROM folders WHERE id = ?",
            (inbox_id,),
        ).fetchone()

    assert root["parent_id"] is None
    assert root["name"] == "Raiz"
    assert inbox["parent_id"] == root_id
    assert inbox["name"] == "Para organizar"


def test_database_enforces_a_single_root(database_path: Path) -> None:
    with connect(database_path) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO folders (parent_id, name, name_key) VALUES (NULL, 'Outra', 'outra')"
        )


def test_database_enforces_unique_name_per_folder(database_path: Path) -> None:
    root_id = _root_id(database_path)
    folders_service.create_folder(database_path, root_id, "Filmes")

    with connect(database_path) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO folders (parent_id, name, name_key) VALUES (?, 'Filmes', 'filmes')",
            (root_id,),
        )


def test_same_name_is_allowed_in_different_folders(database_path: Path) -> None:
    root_id = _root_id(database_path)
    first = folders_service.create_folder(database_path, root_id, "Filmes")
    second = folders_service.create_folder(database_path, root_id, "Series")

    folders_service.create_folder(database_path, int(first["id"]), "Extras")
    folders_service.create_folder(database_path, int(second["id"]), "Extras")


def test_service_rejects_case_and_accent_variants(database_path: Path) -> None:
    root_id = _root_id(database_path)
    folders_service.create_folder(database_path, root_id, "Ação")

    for variant in ("ação", "AÇÃO", "Ac\u0327a\u0303o"):
        with pytest.raises(NameConflictError):
            folders_service.create_folder(database_path, root_id, variant)


def test_database_enforces_unique_file_name_and_version(database_path: Path) -> None:
    root_id = _root_id(database_path)
    sha = "a" * 64
    files_service.create_file(
        database_path,
        root_id,
        "movie.mkv",
        "video/x-matroska",
        1024,
        sha256=sha,
    )

    with pytest.raises(NameConflictError):
        files_service.create_file(
            database_path,
            root_id,
            "MOVIE.mkv",
            "video/x-matroska",
            1024,
            sha256=sha,
        )

    files_service.create_file(
        database_path,
        root_id,
        "movie.mkv",
        "video/x-matroska",
        2048,
        sha256="b" * 64,
        version=2,
        is_current=False,
    )

    with connect(database_path) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO files (folder_id, name, name_key, mime, size_bytes, sha256)
            VALUES (?, 'Movie.mkv', 'movie.mkv', 'video/x-matroska', 0, ?)
            """,
            (root_id, sha),
        )


def test_trashed_file_frees_the_name_for_replacement(database_path: Path) -> None:
    root_id = _root_id(database_path)
    original = files_service.create_file(
        database_path,
        root_id,
        "movie.mkv",
        "video/x-matroska",
        1024,
        sha256="a" * 64,
    )
    trashed = files_service.trash_file(database_path, int(original["id"]))

    replacement = files_service.create_file(
        database_path,
        root_id,
        "movie.mkv",
        "video/x-matroska",
        2048,
        sha256="b" * 64,
    )

    assert trashed["status"] == "trashed"
    assert trashed["folder_id"] == root_id
    assert trashed["trashed_from_folder_id"] == root_id
    assert trashed["trashed_at"] is not None
    assert replacement["status"] == "active"


def test_trashed_file_requires_origin_and_timestamp(database_path: Path) -> None:
    root_id = _root_id(database_path)
    file = files_service.create_file(
        database_path,
        root_id,
        "movie.mkv",
        "video/x-matroska",
        1024,
    )

    with connect(database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE files SET status = 'trashed', trashed_at = '2026-01-01T00:00:00Z' "
                "WHERE id = ?",
                (file["id"],),
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE files SET status = 'trashed', trashed_from_folder_id = ? WHERE id = ?",
                (root_id, file["id"]),
            )


def test_sha256_format_is_validated_by_database(database_path: Path) -> None:
    root_id = _root_id(database_path)

    with connect(database_path) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO files (folder_id, name, name_key, mime, size_bytes, sha256)
            VALUES (?, 'movie.mkv', 'movie.mkv', 'video/x-matroska', 1, 'not-a-hash')
            """,
            (root_id,),
        )


def test_telegram_ref_message_is_unique(database_path: Path) -> None:
    root_id = _root_id(database_path)
    file = files_service.create_file(
        database_path,
        root_id,
        "movie.mkv",
        "video/x-matroska",
        1024,
    )

    with connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO telegram_refs (
                file_id, chat_id, message_id, document_id, access_hash
            ) VALUES (?, -1001234, 10, 55, 66)
            """,
            (file["id"],),
        )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO telegram_refs (
                    file_id, chat_id, message_id, document_id, access_hash
                ) VALUES (?, -1001234, 10, 77, 88)
                """,
                (file["id"],),
            )


def test_subtitle_identity_is_unique_even_with_null_language(database_path: Path) -> None:
    root_id = _root_id(database_path)
    file = files_service.create_file(
        database_path,
        root_id,
        "movie.mkv",
        "video/x-matroska",
        1024,
    )

    with connect(database_path) as connection:
        connection.execute(
            "INSERT INTO subtitles (file_id, source, format) VALUES (?, 'embedded', 'srt')",
            (file["id"],),
        )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO subtitles (file_id, source, format) VALUES (?, 'embedded', 'ass')",
                (file["id"],),
            )


def test_favorite_requires_existing_file(database_path: Path) -> None:
    with connect(database_path) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute("INSERT INTO favorites (file_id) VALUES (99999)")


def test_deleting_file_cascades_references_and_clears_activity(database_path: Path) -> None:
    root_id = _root_id(database_path)
    file = files_service.create_file(
        database_path,
        root_id,
        "movie.mkv",
        "video/x-matroska",
        1024,
    )

    with connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO telegram_refs (
                file_id, chat_id, message_id, document_id, access_hash
            ) VALUES (?, -1001234, 10, 55, 66)
            """,
            (file["id"],),
        )
        connection.execute("INSERT INTO favorites (file_id) VALUES (?)", (file["id"],))
        connection.execute("DELETE FROM files WHERE id = ?", (file["id"],))

        assert connection.execute(
            "SELECT COUNT(*) AS total FROM telegram_refs WHERE file_id = ?",
            (file["id"],),
        ).fetchone()["total"] == 0
        assert connection.execute(
            "SELECT COUNT(*) AS total FROM favorites WHERE file_id = ?",
            (file["id"],),
        ).fetchone()["total"] == 0
        assert connection.execute(
            "SELECT COUNT(*) AS total FROM activity WHERE file_id = ?",
            (file["id"],),
        ).fetchone()["total"] == 0
