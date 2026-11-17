"""Processo do visualizador."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from src.app_factory import create_app

BASE_DIR = Path(__file__).resolve().parents[1]


def create_viewer_app() -> Flask:
    return create_app("viewer")


if __name__ == "__main__":
    load_dotenv(BASE_DIR / ".env")
    application = create_viewer_app()
    settings = application.config["SETTINGS"]
    application.run(host=settings.host, port=settings.port, debug=False)
