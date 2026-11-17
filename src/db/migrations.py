"""Executor de migrations SQL versionadas."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from src.config.settings import BASE_DIR
from src.db.connection import connect

MIGRATIONS_DIR = BASE_DIR / "migrations"


class MigrationError(RuntimeError):
    """Migration inválida ou falha ao aplicar."""


def iter_statements(sql: str) -> list[str]:
    """Divide um script SQL em comandos completos, respeitando triggers."""
    statements: list[str] = []
    buffer = ""
    for line in sql.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            statement = buffer.strip()
            if statement:
                statements.append(statement)
            buffer = ""
    if buffer.strip():
        raise MigrationError("Script SQL termina com um comando incompleto.")
    return statements


def _ensure_ledger(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )


def applied_versions(connection: sqlite3.Connection) -> list[str]:
    _ensure_ledger(connection)
    rows = connection.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()
    return [str(row["version"]) for row in rows]


def discover_migrations(migrations_dir: Path = MIGRATIONS_DIR) -> list[Path]:
    if not migrations_dir.is_dir():
        return []
    return sorted(migrations_dir.glob("*.sql"), key=lambda path: path.name)


def apply_migrations(
    database_path: Path,
    migrations_dir: Path = MIGRATIONS_DIR,
) -> list[str]:
    """Aplica migrations pendentes e retorna as versões aplicadas nesta execução."""
    applied_now: list[str] = []
    with connect(database_path) as connection:
        available = discover_migrations(migrations_dir)
        _ensure_ledger(connection)
        applied = set(applied_versions(connection))

        for migration_path in available:
            version = migration_path.stem
            if version in applied:
                continue

            sql = migration_path.read_text(encoding="utf-8")
            connection.execute("BEGIN IMMEDIATE")
            try:
                for statement in iter_statements(sql):
                    connection.execute(statement)
                connection.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                    (version, datetime.now(UTC).isoformat(timespec="seconds")),
                )
                connection.execute("COMMIT")
            except sqlite3.Error as exc:
                connection.execute("ROLLBACK")
                raise MigrationError(f"Falha ao aplicar {migration_path.name}: {exc}") from exc
            applied_now.append(version)

    return applied_now
