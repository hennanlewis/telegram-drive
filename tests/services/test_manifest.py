"""Manifesto FD1: serialização, parsing e tolerância a entradas inválidas."""

from __future__ import annotations

import pytest
from src.services.catalog.manifest import (
    MANIFEST_MAX_CHARS,
    Manifest,
    ManifestError,
    load_manifest,
    parse_manifest,
    serialize_manifest,
)

FILE_ID = "2b1d8f0e-1a3c-4f5e-8a9b-0c1d2e3f4a5b"
SHA256 = "0123456789abcdef" * 4


def _manifest(**overrides: object) -> Manifest:
    values: dict[str, object] = {
        "file_id": FILE_ID,
        "path": "Filmes/Séries/Temporada 1",
        "name": "episodio.mkv",
        "mime": "video/x-matroska",
        "size_bytes": 1024,
        "sha256": SHA256,
        "organized_at": "2026-11-18T12:00:00Z",
    }
    values.update(overrides)
    return Manifest(**values)  # type: ignore[arg-type]


def test_manifest_roundtrip() -> None:
    original = _manifest(version=2, duration_seconds=3600, part="1/2")

    text = serialize_manifest(original)
    loaded = load_manifest(text)

    assert loaded == original
    assert text.splitlines()[0] == "FD1"
    assert "d=3600" in text.splitlines()
    assert "part=1/2" in text.splitlines()


def test_manifest_minimal_roundtrip() -> None:
    original = _manifest()

    loaded = load_manifest(serialize_manifest(original))

    assert loaded == original
    assert loaded.version == 1
    assert loaded.duration_seconds is None
    assert loaded.part is None


def test_manifest_serializes_without_prefix_bar() -> None:
    text = serialize_manifest(_manifest(path=""))

    assert "p=\n" in text or text.endswith("p=")


def test_manifest_ignores_unknown_keys_and_extra_blank_lines() -> None:
    text = "\n".join(
        [
            "FD1",
            "",
            "i=" + FILE_ID,
            "p=Filmes",
            "n=movie.mkv",
            "m=video/x-matroska",
            "s=10",
            "h=" + SHA256,
            "t=2026-11-18T12:00:00Z",
            "x=algo",
            "",
        ]
    )

    loaded = load_manifest(text)

    assert loaded.path == "Filmes"
    assert loaded.name == "movie.mkv"


def test_manifest_normalizes_case_and_timezone() -> None:
    text = "\n".join(
        [
            "FD1",
            "i=" + FILE_ID.upper(),
            "p=Filmes",
            "n=movie.mkv",
            "m=video/x-matroska",
            "s=10",
            "h=" + SHA256.upper(),
            "t=2026-11-18T12:00:00-03:00",
            "v=3",
        ]
    )

    loaded = load_manifest(text)

    assert loaded.file_id == FILE_ID
    assert loaded.sha256 == SHA256
    assert loaded.organized_at == "2026-11-18T15:00:00Z"
    assert loaded.version == 3


@pytest.mark.parametrize(
    "text",
    [
        "",
        "FD2\ni=" + FILE_ID,
        "FD1",
        "FD1\ni=" + FILE_ID,
    ],
)
def test_manifest_rejects_missing_fields(text: str) -> None:
    with pytest.raises(ManifestError):
        load_manifest(text)
    assert parse_manifest(text) is None


def test_manifest_rejects_invalid_uuid() -> None:
    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(file_id="nao-e-uuid"))
    assert parse_manifest(serialize_manifest(_manifest()).replace(FILE_ID, "x")) is None


def test_manifest_rejects_invalid_sha256() -> None:
    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(sha256="abc"))
    assert parse_manifest(
        serialize_manifest(_manifest()).replace(SHA256, "not-a-hash")
    ) is None


@pytest.mark.parametrize("size", [-1, "dez", None, True, 1.5])
def test_manifest_rejects_invalid_size(size: object) -> None:
    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(size_bytes=size))


@pytest.mark.parametrize("version", [0, -1, "um", True, 1.5])
def test_manifest_rejects_invalid_version(version: object) -> None:
    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(version=version))


@pytest.mark.parametrize("part", ["0/1", "2/1", "1", "1/0", "a/b"])
def test_manifest_rejects_invalid_part(part: str) -> None:
    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(part=part))


@pytest.mark.parametrize("duration", [-1, "muito", True, 1.5])
def test_manifest_rejects_invalid_duration(duration: object) -> None:
    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(duration_seconds=duration))


def test_manifest_rejects_invalid_timestamp() -> None:
    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(organized_at="ontem"))


@pytest.mark.parametrize(
    "path",
    ["/Filmes", "Filmes/", "Filmes//Séries", "Filmes\\Séries"],
)
def test_manifest_rejects_invalid_path(path: str) -> None:
    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(path=path))


def test_manifest_rejects_control_characters() -> None:
    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(name="movie\x00.mkv"))


def test_manifest_rejects_long_path_and_name() -> None:
    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(path="a" * 1100))
    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(name="a" * 300))


def test_manifest_respects_caption_limit() -> None:
    text = serialize_manifest(_manifest(path="/".join(["a" * 200] * 4)))

    assert len(text) <= MANIFEST_MAX_CHARS

    with pytest.raises(ManifestError):
        serialize_manifest(_manifest(path="/".join(["a" * 230] * 4)))


def test_manifest_path_about_limit_is_valid() -> None:
    path = "/".join(["a" * 190, "b" * 190, "c" * 190, "d" * 190])
    manifest = _manifest(path=path)

    loaded = load_manifest(serialize_manifest(manifest))

    assert loaded.path == path


def test_manifest_rejects_non_string_input() -> None:
    assert parse_manifest(None) is None  # type: ignore[arg-type]
    with pytest.raises(ManifestError):
        load_manifest(None)  # type: ignore[arg-type]
