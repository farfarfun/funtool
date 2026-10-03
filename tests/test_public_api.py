import os

import pytest

from funtool import decrypt, encrypt
from funtool.database import BaseTable, SqliteTable
from funtool.download import core as download_core
from funtool.load import DataLoadAndSave
from funtool.path import join_path, path_parse
from funtool.time import time2unix, unix2time


def test_path_parse_returns_absolute_path():
    assert path_parse("README.md").endswith("/README.md")


def test_join_path_without_parent_resolves_against_cwd():
    # 回归用例：join_path 省略 parent_path 时曾直接崩溃（TypeError），
    # 因为内部把 None 传给 os.path.join 而不是回退到当前工作目录。
    assert join_path("a") == os.path.join(os.getcwd(), "a")


def test_join_path_with_parent():
    assert join_path("a", "/tmp") == "/tmp/a"


def test_encrypt_decrypt_round_trip():
    text = "My super secret message"
    assert decrypt(encrypt(text)) == text


def test_data_load_and_save_exported_from_package():
    loader = DataLoadAndSave("/tmp")
    assert loader.file_path("a.pkl") == os.path.join("/tmp", "a.pkl")


def test_data_load_and_save_pickle_round_trip(tmp_path):
    loader = DataLoadAndSave(str(tmp_path))
    payload = {"a": 1, "b": [1, 2, 3]}
    loader.save(payload, "data.pkl")
    assert loader.load("data.pkl") == payload


def test_data_load_and_save_load_save_generates_once_then_reuses(tmp_path):
    loader = DataLoadAndSave(str(tmp_path))
    calls = []

    def generate():
        calls.append(1)
        return {"value": len(calls)}

    first = loader.load_save("cache.pkl", fun=generate)
    second = loader.load_save("cache.pkl", fun=generate)
    assert first == second == {"value": 1}
    assert len(calls) == 1


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


def test_sqlite_table_insert_update_count_select(tmp_path):
    db_path = tmp_path / "test.db"
    table = SqliteTable(str(db_path), table_name="t", columns=["id", "name"])
    table.execute("create table t (id text, name text)")

    table.insert({"id": "1", "name": "a"})
    assert table.count({"id": "1"}) == 1

    table.update({"name": "b"}, {"id": "1"})
    rows = table.select("select * from table_name where id='1'")
    assert rows == [("1", "b")]
    table.close()


def test_m3u8_module_logger_is_defined():
    # 回归用例：download/m3u8.py 曾经从未定义 logger，info()/下载完成分支
    # 调用 logger.xxx 时必然 NameError（codex #607/#758 均指出过）。
    from funtool.download import m3u8 as m3u8_module

    m3u8_module.info("smoke")
    assert m3u8_module.logger is not None


def test_story_module_logger_is_defined():
    from funtool.download import story as story_module

    story_module.info("smoke")
    assert story_module.logger is not None
