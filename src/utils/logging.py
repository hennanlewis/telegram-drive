"""Logging estruturado em JSON, sem segredos."""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import IO, Any

_HANDLER_MARKER = "_telegram_drive_handler"


class JsonFormatter(logging.Formatter):
    """Formata registros como uma linha JSON."""

    def __init__(self, process: str) -> None:
        super().__init__()
        self.process = process

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname.lower(),
            "process": getattr(record, "app_process", self.process),
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(
    process: str,
    level: str = "INFO",
    stream: IO[str] | None = None,
) -> logging.Logger:
    """Configura o logger raiz sem duplicar handlers entre factories."""
    root = logging.getLogger()
    root.setLevel(level)

    if not any(getattr(handler, _HANDLER_MARKER, False) for handler in root.handlers):
        handler = logging.StreamHandler(stream or sys.stderr)
        handler.setFormatter(JsonFormatter(process))
        setattr(handler, _HANDLER_MARKER, True)
        root.addHandler(handler)

    return logging.getLogger(process)
