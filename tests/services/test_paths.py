"""Nomes, chaves de unicidade e caminhos virtuais."""

from __future__ import annotations

from pathlib import Path

import pytest
from src.services.catalog import folders as folders_service
from src.services.catalog import paths
from src.services.catalog.errors import InvalidNameError


def test_normalize_name_keeps_case_and_trims_unicode() -> None:
    assert paths.normalize_name("Filmes") == "Filmes"
    assert paths.normalize_name("Ac\u0327a\u0303o") == "Ação"


@pytest.mark.parametrize(
    "name",
    [
        "",
        " Filmes",
        "Filmes ",
        "a/b",
        "a\\b",
        ".",
        "..",
        "a\x00b",
        "a\nb",
    ],
)
def test_normalize_name_rejects_invalid_values(name: str) -> None:
    with pytest.raises(InvalidNameError):
        paths.normalize_name(name)


def test_normalize_name_rejects_long_names() -> None:
    with pytest.raises(InvalidNameError):
        paths.normalize_name("a" * (paths.MAX_NAME_LENGTH + 1))


def test_name_key_folds_case_and_accents() -> None:
    assert paths.name_key("Ação") == paths.name_key("AÇÃO")
    assert paths.name_key("Ação") == paths.name_key("ac\u0327a\u0303o")
    assert paths.name_key("Filmes") == "filmes"
    assert paths.name_key("Filmes") != paths.name_key("Filme")


@pytest.mark.parametrize(
    "path",
    ["/Filmes", "Filmes/", "Filmes//Séries", "Filmes\\Séries"],
)
def test_validate_manifest_path_rejects_invalid_values(path: str) -> None:
    with pytest.raises(InvalidNameError):
        paths.validate_manifest_path(path)


def test_validate_manifest_path_accepts_empty_and_normalizes() -> None:
    assert paths.validate_manifest_path("") == ""
    assert paths.validate_manifest_path("Ac\u0327a\u0303o/Filmes") == "Ação/Filmes"


def test_validate_manifest_path_rejects_long_paths() -> None:
    with pytest.raises(InvalidNameError):
        paths.validate_manifest_path("a" * (paths.MAX_PATH_LENGTH + 1))


def test_folder_manifest_path_excludes_root(database_path: Path) -> None:
    root_id = folders_service.get_root_id(database_path)
    movies = folders_service.create_folder(database_path, root_id, "Filmes")
    nested = folders_service.create_folder(database_path, int(movies["id"]), "Séries")

    assert folders_service.folder_path(database_path, root_id) == "Raiz"
    assert folders_service.folder_path(database_path, int(movies["id"])) == "Raiz / Filmes"
    assert folders_service.folder_path(database_path, int(nested["id"])) == (
        "Raiz / Filmes / Séries"
    )
