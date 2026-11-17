"""Verificação dos assets herdados exigidos pela fundação."""

from __future__ import annotations

import json

from src.config.settings import BASE_DIR


def test_inherited_static_assets_exist() -> None:
    static = BASE_DIR / "src" / "static"

    assert (static / "css" / "style.css").is_file()
    assert (static / "css" / "login.css").is_file()
    assert (static / "css" / "admin.css").is_file()
    assert (static / "icons" / "folder.png").is_file()
    assert (static / "js" / "vendor" / "highlight.min.js").is_file()


def test_mime_map_is_valid_and_points_to_existing_icons() -> None:
    config_path = BASE_DIR / "config" / "mime_map.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    icons_dir = BASE_DIR / "src" / "static" / "icons"

    assert config["icon_map"]
    assert config["mime_overrides"]

    for entry in config["icon_map"]:
        assert (icons_dir / entry["icon"]).is_file(), entry["icon"]
