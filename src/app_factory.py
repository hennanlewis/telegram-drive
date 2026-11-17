"""Application factory compartilhada pelos dois processos."""

from __future__ import annotations

from datetime import timedelta

from flask import Flask

from src.config.settings import ProcessName, Settings, load_settings
from src.db.migrations import apply_migrations
from src.routes.api.health import health_bp
from src.utils.logging import configure_logging


def create_app(process: ProcessName) -> Flask:
    settings: Settings = load_settings(process)
    logger = configure_logging(process, settings.log_level)

    apply_migrations(settings.database_path)

    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
        static_url_path="/static",
    )
    app.config.update(
        SETTINGS=settings,
        SECRET_KEY=settings.secret_key,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=settings.session_timeout_minutes),
    )

    app.register_blueprint(health_bp)

    logger.info(
        "application configured",
        extra={
            "app_process": process,
            "environment": settings.app_env,
            "host": settings.host,
            "port": settings.port,
        },
    )
    return app
