"""Erros de domínio do catálogo."""

from __future__ import annotations


class CatalogError(ValueError):
    """Erro de regra do catálogo."""


class NotFoundError(CatalogError):
    """Pasta, arquivo ou configuração inexistente."""


class NameConflictError(CatalogError):
    """Já existe um item com o mesmo nome no destino."""


class InvalidNameError(CatalogError):
    """Nome ou caminho inválido."""


class ProtectedFolderError(CatalogError):
    """Pasta reservada não pode ser alterada dessa forma."""


class FolderNotEmptyError(CatalogError):
    """A pasta contém itens e não pode ser excluída."""


class InvalidMoveError(CatalogError):
    """Movimentação criaria um ciclo ou não faz sentido."""


class InvalidStateError(CatalogError):
    """Operação incompatível com o estado atual do item."""
