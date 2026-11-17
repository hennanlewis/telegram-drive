"""Carregamento e validação da configuração por variáveis de ambiente."""

from __future__ import annotations

import os
import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

BASE_DIR = Path(__file__).resolve().parents[2]
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
VALID_ENVIRONMENTS = frozenset({"development", "test", "production"})
MIN_SECRET_LENGTH = 32

ProcessName = Literal["admin", "viewer"]


class ConfigurationError(RuntimeError):
    """Configuração ausente ou inválida."""


@dataclass(frozen=True, slots=True)
class Settings:
    process: ProcessName
    app_env: str
    log_level: str
    host: str
    port: int
    secret_key: str
    database_path: Path
    session_timeout_minutes: int


def _read(env: Mapping[str, str], key: str, default: str) -> str:
    value = env.get(key)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def _read_int(env: Mapping[str, str], key: str, default: int) -> int:
    raw = env.get(key)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{key} deve ser um número inteiro.") from exc


def _read_secret(
    env: Mapping[str, str],
    key: str,
    process: ProcessName,
    app_env: str,
) -> str:
    value = _read(env, key, "")
    if len(value) >= MIN_SECRET_LENGTH:
        return value
    if app_env == "production":
        raise ConfigurationError(
            f"{key} deve ter pelo menos {MIN_SECRET_LENGTH} caracteres em produção."
        )
    # Ambiente de desenvolvimento/teste: segredo efêmero, nunca versionado.
    return secrets.token_urlsafe(MIN_SECRET_LENGTH)


def load_settings(
    process: ProcessName,
    env: Mapping[str, str] | None = None,
) -> Settings:
    """Monta a configuração do processo a partir do ambiente."""
    source: Mapping[str, str] = os.environ if env is None else env

    app_env = _read(source, "APP_ENV", "development").lower()
    if app_env not in VALID_ENVIRONMENTS:
        raise ConfigurationError(
            f"APP_ENV inválido: {app_env!r}. Use development, test ou production."
        )

    log_level = _read(source, "LOG_LEVEL", "INFO").upper()
    if log_level not in VALID_LOG_LEVELS:
        raise ConfigurationError(f"LOG_LEVEL inválido: {log_level!r}.")

    prefix = "ADMIN" if process == "admin" else "VIEWER"
    host = _read(source, f"{prefix}_HOST", "127.0.0.1")
    default_port = 8081 if process == "admin" else 8080
    port = _read_int(source, f"{prefix}_PORT", default_port)
    if not 1 <= port <= 65535:
        raise ConfigurationError(f"{prefix}_PORT deve estar entre 1 e 65535.")

    if process == "admin" and host not in LOOPBACK_HOSTS:
        raise ConfigurationError(
            "ADMIN_HOST deve ser um endereço de loopback (127.0.0.1, ::1 ou localhost)."
        )

    secret_key = _read_secret(source, f"SECRET_KEY_{prefix}", process, app_env)

    raw_database_path = _read(source, "DATABASE_PATH", "config/database.db")
    database_path = Path(raw_database_path).expanduser()
    if not database_path.is_absolute():
        database_path = BASE_DIR / database_path
    database_path = database_path.resolve()

    timeout_key = (
        "ADMIN_SESSION_TIMEOUT_MINUTES" if process == "admin" else "SESSION_TIMEOUT_MINUTES"
    )
    timeout_default = 30 if process == "admin" else 60
    session_timeout_minutes = _read_int(source, timeout_key, timeout_default)
    if session_timeout_minutes <= 0:
        raise ConfigurationError(f"{timeout_key} deve ser maior que zero.")

    return Settings(
        process=process,
        app_env=app_env,
        log_level=log_level,
        host=host,
        port=port,
        secret_key=secret_key,
        database_path=database_path,
        session_timeout_minutes=session_timeout_minutes,
    )
