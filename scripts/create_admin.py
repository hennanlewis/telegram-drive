"""Cria o primeiro administrador por linha de comando."""

from __future__ import annotations

import argparse
import getpass

from dotenv import load_dotenv
from src.config.settings import BASE_DIR, load_settings
from src.db.migrations import apply_migrations
from src.repositories.users import ROLES
from src.services.auth.users import (
    UserAlreadyExistsError,
    UserError,
    create_user,
)
from src.utils.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cria um usuário no banco local.")
    parser.add_argument("--username", help="Nome do usuário. Se omitido, será pedido.")
    parser.add_argument(
        "--role",
        choices=ROLES,
        default="admin",
        help="Papel do usuário (padrão: admin).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv(BASE_DIR / ".env")
    settings = load_settings("admin")
    logger = configure_logging("create_admin", settings.log_level)

    parser = build_parser()
    args = parser.parse_args(argv)

    username = args.username or input("Usuário: ").strip()
    password = getpass.getpass("Senha: ")
    confirmation = getpass.getpass("Confirme a senha: ")
    if password != confirmation:
        logger.error("as senhas não conferem")
        return 1

    apply_migrations(settings.database_path)

    try:
        user = create_user(settings.database_path, username, password, args.role)
    except UserAlreadyExistsError as exc:
        logger.error("%s", exc)
        return 1
    except UserError as exc:
        logger.error("%s", exc)
        return 1

    logger.info(
        "usuário criado",
        extra={"username": user["username"], "role": user["role"]},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
