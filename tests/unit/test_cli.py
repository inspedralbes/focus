import json

import pytest

from focus.cli import main, write_state


def test_cli_writes_valid_state_atomically(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    assert main(["test", "--state-file", str(path)]) == 0
    assert json.loads(path.read_text(encoding="utf-8")) == {"state": "test"}
    assert list(tmp_path.glob("*.tmp")) == []


def test_invalid_state_does_not_write(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("original", encoding="utf-8")
    with pytest.raises(ValueError): write_state(path, "unknown")
    assert path.read_text(encoding="utf-8") == "original"
    with pytest.raises(SystemExit): main(["unknown", "--state-file", str(path)])
    assert path.read_text(encoding="utf-8") == "original"


def test_replace_failure_keeps_original_and_cleans_temp(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    path.write_text("original", encoding="utf-8")
    def fail(*args): raise OSError("replace failed")
    monkeypatch.setattr("focus.cli.os.replace", fail)
    with pytest.raises(OSError): write_state(path, "classe")
    assert path.read_text(encoding="utf-8") == "original"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["state.json"]
