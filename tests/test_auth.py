"""Testes de criação e autenticação do primeiro administrador."""

from __future__ import annotations

from pathlib import Path

import pytest
from src.services.auth.passwords import hash_password, verify_password
from src.services.auth.users import (
    UserAlreadyExistsError,
    UserError,
    authenticate_user,
    create_user,
)


def test_create_admin_and_authenticate(database_path: Path) -> None:
    created = create_user(database_path, "owner", "senha-forte", "admin")

    assert created["username"] == "owner"
    assert created["role"] == "admin"

    authenticated = authenticate_user(database_path, "owner", "senha-forte")
    assert authenticated is not None
    assert authenticated["role"] == "admin"


def test_authentication_rejects_wrong_password(database_path: Path) -> None:
    create_user(database_path, "owner", "senha-forte", "admin")

    assert authenticate_user(database_path, "owner", "senha-errada") is None


def test_authentication_rejects_unknown_user(database_path: Path) -> None:
    assert authenticate_user(database_path, "ninguem", "senha-forte") is None


def test_duplicate_username_is_rejected(database_path: Path) -> None:
    create_user(database_path, "owner", "senha-forte", "admin")

    with pytest.raises(UserAlreadyExistsError):
        create_user(database_path, "OWNER", "outra-senha", "viewer")


@pytest.mark.parametrize("username", ["", "ab", "nome com espaço", "acentuação"])
def test_invalid_usernames_are_rejected(database_path: Path, username: str) -> None:
    with pytest.raises(UserError):
        create_user(database_path, username, "senha-forte", "admin")


def test_short_password_is_rejected(database_path: Path) -> None:
    with pytest.raises(UserError):
        create_user(database_path, "owner", "curta", "admin")


def test_password_is_hashed() -> None:
    password_hash = hash_password("senha-forte")

    assert "senha-forte" not in password_hash
    assert verify_password(password_hash, "senha-forte")
    assert not verify_password(password_hash, "senha-errada")
