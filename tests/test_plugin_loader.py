import json
from pathlib import Path
from unittest.mock import patch

from plugin_loader import load_plugins


def _write_plugin(tmp_path: Path, name: str, data: list) -> None:
    (tmp_path / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")
    (tmp_path / f"{name}.png").write_bytes(b"")  # dummy png


VALID_FIELD = {"field": "Name", "corX": 100, "corY": 200, "pause": 1}


def test_valid_plugin_loaded(tmp_path):
    _write_plugin(tmp_path, "test screen", [VALID_FIELD])
    with patch("plugin_loader.PLUGINS_DIR", tmp_path):
        plugins = load_plugins()
    assert "test screen" in plugins
    assert plugins["test screen"].fields[0].field == "Name"


def test_missing_png_skipped(tmp_path):
    (tmp_path / "orphan.json").write_text(json.dumps([VALID_FIELD]), encoding="utf-8")
    with patch("plugin_loader.PLUGINS_DIR", tmp_path):
        plugins = load_plugins()
    assert "orphan" not in plugins


def test_malformed_json_skipped(tmp_path):
    (tmp_path / "bad.json").write_text("not valid json", encoding="utf-8")
    (tmp_path / "bad.png").write_bytes(b"")
    with patch("plugin_loader.PLUGINS_DIR", tmp_path):
        plugins = load_plugins()
    assert "bad" not in plugins


def test_missing_key_skipped(tmp_path):
    bad_field = {"field": "Name", "corX": 10}  # missing corY and pause
    _write_plugin(tmp_path, "incomplete", [bad_field])
    with patch("plugin_loader.PLUGINS_DIR", tmp_path):
        plugins = load_plugins()
    assert "incomplete" not in plugins


def test_plugin_name_lowercased(tmp_path):
    _write_plugin(tmp_path, "FX Interbank", [VALID_FIELD])
    with patch("plugin_loader.PLUGINS_DIR", tmp_path):
        plugins = load_plugins()
    assert "fx interbank" in plugins
