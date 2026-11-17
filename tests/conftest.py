"""Fixtures compartilhadas pelos testes."""

from __future__ import annotations

from pathlib import Path

import pytest
from flask import Flask
from src.config.settings import Settings, load_settings
from src.db.migrations import apply_migrations


@pytest.fixture
def database_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "test.db"
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_PATH", str(path))
    monkeypatch.setenv("SECRET_KEY_ADMIN", "admin-" + "a" * 32)
    monkeypatch.setenv("SECRET_KEY_VIEWER", "viewer-" + "b" * 32)
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    apply_migrations(path)
    return path


@pytest.fixture
def settings(database_path: Path) -> Settings:
    return load_settings("admin")


@pytest.fixture
def admin_app(database_path: Path) -> Flask:
    from src.app_admin import create_admin_app

    app = create_admin_app()
    app.config.update(TESTING=True)
    return app


@pytest.fixture
def viewer_app(database_path: Path) -> Flask:
    from src.app_viewer import create_viewer_app

    app = create_viewer_app()
    app.config.update(TESTING=True)
    return app


@pytest.fixture
def admin_client(admin_app: Flask):
    return admin_app.test_client()


@pytest.fixture
def viewer_client(viewer_app: Flask):
    return viewer_app.test_client()
