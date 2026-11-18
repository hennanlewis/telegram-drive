"""Nomes, caminhos virtuais e breadcrumb."""

from __future__ import annotations

import sqlite3
import unicodedata
from typing import Any

from src.repositories import folders as folders_repository
from src.services.catalog.errors import InvalidNameError, NotFoundError

MAX_NAME_LENGTH = 255
MAX_PATH_LENGTH = 1024


def normalize_name(name: str) -> str:
    """Valida e devolve o nome em NFC, sem alterar maiúsculas/minúsculas."""
    if not isinstance(name, str):
        raise InvalidNameError("O nome deve ser um texto.")
    if name != name.strip():
        raise InvalidNameError("O nome não pode ter espaços nas pontas.")
    if not name:
        raise InvalidNameError("O nome é obrigatório.")
    if len(name) > MAX_NAME_LENGTH:
        raise InvalidNameError(f"O nome deve ter no máximo {MAX_NAME_LENGTH} caracteres.")
    if name in {".", ".."}:
        raise InvalidNameError("O nome não pode ser '.' nem '..'.")
    if "/" in name or "\\" in name:
        raise InvalidNameError("O nome não pode conter separadores de caminho.")
    if any(unicodedata.category(character) == "Cc" for character in name):
        raise InvalidNameError("O nome não pode conter caracteres de controle.")
    return unicodedata.normalize("NFC", name)


def name_key(name: str) -> str:
    """Chave de unicidade: NFC + casefold, para nomes com acento."""
    return normalize_name(name).casefold()


def validate_manifest_path(path: str) -> str:
    """Valida o caminho do manifesto, que não tem barra inicial."""
    if not isinstance(path, str):
        raise InvalidNameError("O caminho deve ser um texto.")
    if path == "":
        return ""
    if path.startswith("/") or path.endswith("/"):
        raise InvalidNameError("O caminho não pode começar nem terminar com barra.")
    if "\\" in path:
        raise InvalidNameError("O caminho deve usar '/' como separador.")
    if "//" in path:
        raise InvalidNameError("O caminho não pode ter segmentos vazios.")
    if len(path) > MAX_PATH_LENGTH:
        raise InvalidNameError(f"O caminho deve ter no máximo {MAX_PATH_LENGTH} caracteres.")
    segments = [normalize_name(segment) for segment in path.split("/")]
    return "/".join(segments)


def breadcrumbs(connection: sqlite3.Connection, folder_id: int) -> list[dict[str, Any]]:
    chain = folders_repository.breadcrumbs(connection, folder_id)
    if not chain:
        raise NotFoundError(f"Pasta {folder_id} não encontrada.")
    return chain


def folder_path_parts(connection: sqlite3.Connection, folder_id: int) -> list[str]:
    """Nomes das pastas, sem a raiz, para gravar no manifesto."""
    chain = breadcrumbs(connection, folder_id)
    if chain[0]["parent_id"] is not None:
        # Uma linhagem sem raiz indica catálogo inconsistente.
        raise NotFoundError(f"A pasta {folder_id} não está ligada à raiz.")
    return [folder["name"] for folder in chain[1:]]


def folder_manifest_path(connection: sqlite3.Connection, folder_id: int) -> str:
    return "/".join(folder_path_parts(connection, folder_id))


def folder_display_path(connection: sqlite3.Connection, folder_id: int) -> str:
    chain = breadcrumbs(connection, folder_id)
    return " / ".join(folder["name"] for folder in chain)


def validate_mime(mime: str) -> str:
    if not isinstance(mime, str):
        raise InvalidNameError("O MIME deve ser um texto.")
    normalized = mime.strip()
    if not normalized:
        raise InvalidNameError("O MIME é obrigatório.")
    if len(normalized) > 255:
        raise InvalidNameError("O MIME é longo demais.")
    if any(unicodedata.category(character) == "Cc" for character in normalized):
        raise InvalidNameError("O MIME não pode conter caracteres de controle.")
    return normalized
