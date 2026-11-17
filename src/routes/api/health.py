"""Health check do processo e do banco."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from src.config.settings import Settings
from src.db.connection import database_is_available

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health():
    settings: Settings = current_app.config["SETTINGS"]
    database_ok = database_is_available(settings.database_path)
    status = "ok" if database_ok else "degraded"

    return (
        jsonify(
            {
                "status": status,
                "process": settings.process,
                "database": {"status": "ok" if database_ok else "unavailable"},
            }
        ),
        200 if database_ok else 503,
    )
