"""Regras de usuários e autenticação."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from src.db.connection import connect
from src.repositories import users as users_repository
from src.services.auth.passwords import hash_password, verify_password

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]{3,32}$")
MIN_PASSWORD_LENGTH = 8


class UserError(ValueError):
    """Dados de usuário inválidos."""


class UserAlreadyExistsError(UserError):
    """Nome de usuário já cadastrado."""


def validate_username(username: str) -> str:
    normalized = username.strip()
    if not USERNAME_PATTERN.fullmatch(normalized):
        raise UserError(
            "Usuário deve ter de 3 a 32 caracteres: letras, números, ponto, hífen ou sublinhado."
        )
    return normalized


def validate_password(password: str) -> str:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise UserError(f"A senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres.")
    return password


def create_user(
    database_path: Path,
    username: str,
    password: str,
    role: str = "admin",
) -> dict[str, Any]:
    if role not in users_repository.ROLES:
        raise UserError(f"Papel inválido: {role!r}.")
    normalized_username = validate_username(username)
    validate_password(password)

    with connect(database_path) as connection:
        try:
            return users_repository.create_user(
                connection,
                normalized_username,
                hash_password(password),
                role,
            )
        except sqlite3.IntegrityError as exc:
            raise UserAlreadyExistsError(
                f"Já existe um usuário com o nome {normalized_username!r}."
            ) from exc


def authenticate_user(
    database_path: Path,
    username: str,
    password: str,
) -> dict[str, Any] | None:
    with connect(database_path) as connection:
        user = users_repository.get_user_by_username(connection, username)

    if user is None or not user["is_active"]:
        return None
    if not verify_password(user["password_hash"], password):
        return None
    return user
