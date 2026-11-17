"""Testes do health check e da configuração dos processos."""

from __future__ import annotations

import logging
from dataclasses import replace
from pathlib import Path

import pytest
from src.config.settings import ConfigurationError, load_settings


def test_admin_health_reports_database(admin_client, database_path: Path) -> None:
    response = admin_client.get("/api/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload == {
        "status": "ok",
        "process": "admin",
        "database": {"status": "ok"},
    }


def test_viewer_health_reports_database(viewer_client) -> None:
    response = viewer_client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["process"] == "viewer"


def test_health_reports_degraded_when_database_is_unavailable(
    admin_app,
    tmp_path: Path,
) -> None:
    broken_settings = replace(
        admin_app.config["SETTINGS"],
        database_path=tmp_path,
    )
    admin_app.config["SETTINGS"] = broken_settings

    response = admin_app.test_client().get("/api/health")

    assert response.status_code == 503
    assert response.get_json()["status"] == "degraded"
    assert response.get_json()["database"]["status"] == "unavailable"


def test_admin_refuses_non_loopback_bind() -> None:
    with pytest.raises(ConfigurationError):
        load_settings("admin", {"ADMIN_HOST": "0.0.0.0"})


def test_viewer_can_bind_outside_loopback_for_tunnel() -> None:
    settings = load_settings(
        "viewer",
        {
            "VIEWER_HOST": "0.0.0.0",
            "SECRET_KEY_VIEWER": "viewer-" + "b" * 32,
        },
    )

    assert settings.host == "0.0.0.0"


def test_production_requires_session_secret() -> None:
    with pytest.raises(ConfigurationError):
        load_settings("viewer", {"APP_ENV": "production"})


def test_startup_log_does_not_contain_secrets(
    database_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    admin_secret = "admin-secret-" + "x" * 32
    viewer_secret = "viewer-secret-" + "y" * 32
    monkeypatch.setenv("SECRET_KEY_ADMIN", admin_secret)
    monkeypatch.setenv("SECRET_KEY_VIEWER", viewer_secret)
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    caplog.set_level(logging.INFO)

    from src.app_admin import create_admin_app

    create_admin_app()

    assert "application configured" in caplog.text
    assert admin_secret not in caplog.text
    assert viewer_secret not in caplog.text
