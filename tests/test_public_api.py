import pytest

from fartool.database import BaseTable
from fartool.download import core as download_core
from fartool.path import path_parse
from fartool.time import time2unix, unix2time


def test_path_parse_returns_absolute_path():
    assert path_parse("README.md").endswith("/README.md")


def test_time_round_trip():
    value = "2024-01-02 03:04:05"
    assert unix2time(time2unix(value)) == value


def test_download_uses_funget_by_default(monkeypatch, tmp_path):
    target = tmp_path / "result.bin"
    calls = []

    def fake_download(url, path, *, overwrite):
        calls.append((url, path, overwrite))
        return True

    monkeypatch.setattr(download_core, "funget_download", fake_download)

    assert download_core.download("https://example.com/a.bin", target) is True
    assert calls == [("https://example.com/a.bin", str(target), False)]


def test_download_rejects_unknown_mode(tmp_path):
    with pytest.raises(ValueError, match="不支持的下载模式"):
        download_core.download("https://example.com/a.bin", tmp_path / "a.bin", mode="bad")


def test_database_requires_columns():
    table = BaseTable(columns=None)
    with pytest.raises(ValueError, match="columns cannot be None"):
        table._properties2kv({})
