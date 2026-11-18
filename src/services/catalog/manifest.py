"""Manifesto FD1 na legenda das mensagens."""

from __future__ import annotations

import re
import unicodedata
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from src.services.catalog.errors import InvalidNameError
from src.services.catalog.paths import normalize_name, validate_manifest_path

MANIFEST_HEADER = "FD1"
MANIFEST_MAX_CHARS = 1024
PART_PATTERN = re.compile(r"^(\d+)/(\d+)$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(ValueError):
    """Manifesto FD1 inválido."""


@dataclass(frozen=True, slots=True)
class Manifest:
    file_id: str
    path: str
    name: str
    mime: str
    size_bytes: int
    sha256: str
    organized_at: str
    version: int = 1
    duration_seconds: int | None = None
    part: str | None = None


def _validate_text(value: Any, field: str, *, max_length: int = 255) -> str:
    if not isinstance(value, str):
        raise ManifestError(f"{field} deve ser texto.")
    normalized = value.strip()
    if not normalized:
        raise ManifestError(f"{field} é obrigatório.")
    if len(normalized) > max_length:
        raise ManifestError(f"{field} é longo demais.")
    if any(unicodedata.category(character) == "Cc" for character in normalized):
        raise ManifestError(f"{field} não pode conter caracteres de controle.")
    return normalized


def _parse_int(value: Any, field: str) -> int:
    """Aceita inteiros e texto com inteiro; recusa bool, float e lixo."""
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ManifestError(f"{field} deve ser um inteiro.")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ManifestError(f"{field} deve ser um inteiro.") from exc


def _validate_uuid(value: Any) -> str:
    try:
        parsed = uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ManifestError("i deve ser um UUID.") from exc
    return str(parsed)


def _validate_sha256(value: Any) -> str:
    if not isinstance(value, str):
        raise ManifestError("h deve ser texto.")
    normalized = value.strip().lower()
    if not SHA256_PATTERN.fullmatch(normalized):
        raise ManifestError("h deve ser um SHA-256 em hexadecimal.")
    return normalized


def _validate_size(value: Any) -> int:
    size = _parse_int(value, "s")
    if size < 0:
        raise ManifestError("s deve ser um inteiro não negativo.")
    return size


def _validate_version(value: Any) -> int:
    version = _parse_int(value, "v")
    if version < 1:
        raise ManifestError("v deve ser maior ou igual a 1.")
    return version


def _validate_duration(value: Any) -> int | None:
    if value is None or value == "":
        return None
    duration = _parse_int(value, "d")
    if duration < 0:
        raise ManifestError("d não pode ser negativo.")
    return duration


def _validate_part(value: Any) -> str | None:
    if value is None or value == "":
        return None
    match = PART_PATTERN.fullmatch(str(value).strip())
    if match is None:
        raise ManifestError("part deve estar no formato i/n.")
    index, count = (int(group) for group in match.groups())
    if count < 1 or index < 1 or index > count:
        raise ManifestError("part deve ter 1 <= i <= n.")
    return f"{index}/{count}"


def _validate_timestamp(value: Any) -> str:
    if not isinstance(value, str):
        raise ManifestError("t deve ser texto.")
    raw = value.strip()
    if not raw:
        raise ManifestError("t é obrigatório.")
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ManifestError("t deve ser uma data ISO 8601.") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalized(manifest: Manifest) -> Manifest:
    mime = _validate_text(manifest.mime, "m", max_length=255)
    try:
        path = validate_manifest_path(manifest.path)
        name = normalize_name(manifest.name)
    except InvalidNameError as exc:
        raise ManifestError(str(exc)) from exc
    return Manifest(
        file_id=_validate_uuid(manifest.file_id),
        path=path,
        name=name,
        mime=mime,
        size_bytes=_validate_size(manifest.size_bytes),
        sha256=_validate_sha256(manifest.sha256),
        organized_at=_validate_timestamp(manifest.organized_at),
        version=_validate_version(manifest.version),
        duration_seconds=_validate_duration(manifest.duration_seconds),
        part=_validate_part(manifest.part),
    )


def serialize_manifest(manifest: Manifest) -> str:
    """Serializa o manifesto e garante o limite da legenda."""
    normalized = _normalized(manifest)
    lines = [
        MANIFEST_HEADER,
        f"i={normalized.file_id}",
        f"p={normalized.path}",
        f"n={normalized.name}",
        f"m={normalized.mime}",
        f"s={normalized.size_bytes}",
        f"h={normalized.sha256}",
        f"t={normalized.organized_at}",
        f"v={normalized.version}",
    ]
    if normalized.duration_seconds is not None:
        lines.append(f"d={normalized.duration_seconds}")
    if normalized.part is not None:
        lines.append(f"part={normalized.part}")

    text = "\n".join(lines)
    if len(text) > MANIFEST_MAX_CHARS:
        raise ManifestError(
            f"O manifesto passou de {MANIFEST_MAX_CHARS} caracteres."
        )
    return text


def load_manifest(text: str) -> Manifest:
    """Parseia estritamente um manifesto FD1."""
    if not isinstance(text, str):
        raise ManifestError("O manifesto deve ser texto.")

    lines = text.strip().splitlines()
    if not lines or lines[0].strip() != MANIFEST_HEADER:
        raise ManifestError("O manifesto não começa com FD1.")

    values: dict[str, str] = {}
    for line in lines[1:]:
        if not line.strip() or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if key:
            values[key] = raw_value.strip()

    required = ("i", "p", "n", "m", "s", "h", "t")
    if any(key not in values for key in required):
        raise ManifestError("O manifesto tem campos obrigatórios faltando.")

    return _normalized(
        Manifest(
            file_id=values["i"],
            path=values["p"],
            name=values["n"],
            mime=values["m"],
            size_bytes=values["s"],
            sha256=values["h"],
            organized_at=values["t"],
            version=values.get("v", "1"),
            duration_seconds=values.get("d"),
            part=values.get("part"),
        )
    )


def parse_manifest(text: str) -> Manifest | None:
    """Parser tolerante: manifesto inválido leva o arquivo ao Inbox."""
    try:
        return load_manifest(text)
    except (ManifestError, ValueError, TypeError):
        return None
