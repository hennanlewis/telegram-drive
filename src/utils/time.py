"""Utilidades de data e hora em UTC."""

from __future__ import annotations

from datetime import UTC, datetime


def utc_now_iso() -> str:
    """Data e hora atuais em UTC, no formato usado pelo catálogo."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
