"""Testes do executor de migrations e do schema básico."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from src.db.connection import connect
from src.db.migrations import (
    MigrationError,
    applied_versions,
    apply_migrations,
    iter_statements,
)


def table_names(database_path: Path) -> set[str]:
    with connect(database_path) as connection:
        rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    return {row["name"] for row in rows}


def test_migrations_create_foundation_tables_from_empty_database(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "empty.db"

    applied = apply_migrations(database_path)

    assert applied == ["0000_foundation", "0001_catalog"]
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
        "schema_migrations",
    } <= table_names(database_path)


def test_migrations_create_root_and_inbox(database_path: Path) -> None:
    with connect(database_path) as connection:
        root = connection.execute(
            "SELECT id, name, parent_id FROM folders WHERE parent_id IS NULL"
        ).fetchone()
        inbox = connection.execute(
            "SELECT id, name, parent_id FROM folders WHERE name_key = 'para organizar'"
        ).fetchone()
        settings = {
            row["key"]: row["value"]
            for row in connection.execute("SELECT key, value FROM settings").fetchall()
        }

    assert root is not None
    assert root["name"] == "Raiz"
    assert inbox is not None
    assert inbox["parent_id"] == root["id"]
    assert inbox["name"] == "Para organizar"
    assert settings["root_folder_id"] == str(root["id"])
    assert settings["inbox_folder_id"] == str(inbox["id"])


def test_migrations_are_idempotent(database_path: Path) -> None:
    applied_again = apply_migrations(database_path)

    assert applied_again == []
    with connect(database_path) as connection:
        assert applied_versions(connection) == ["0000_foundation", "0001_catalog"]


def test_users_are_unique_case_insensitively(database_path: Path) -> None:
    with connect(database_path) as connection:
        connection.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("Owner", "hash", "admin"),
        )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ("owner", "hash", "viewer"),
            )


def test_user_role_has_check_constraint(database_path: Path) -> None:
    with connect(database_path) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("owner", "hash", "superuser"),
        )


def test_iter_statements_keeps_trigger_body_together() -> None:
    sql = """
    CREATE TABLE sample (value INTEGER);
    CREATE TRIGGER sample_trigger AFTER INSERT ON sample
    BEGIN
        UPDATE sample SET value = value + 1 WHERE rowid = NEW.rowid;
    END;
    """

    statements = iter_statements(sql)

    assert len(statements) == 2
    assert statements[1].startswith("CREATE TRIGGER")


def test_iter_statements_rejects_incomplete_script() -> None:
    with pytest.raises(MigrationError):
        iter_statements("CREATE TABLE sample (value INTEGER)")
