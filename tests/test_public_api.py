from funtool.path import path_parse
from funtool.time import time2unix, unix2time


def test_path_parse_returns_absolute_path():
    assert path_parse("README.md").endswith("/README.md")


def test_time_round_trip():
    value = "2024-01-02 03:04:05"
    assert unix2time(time2unix(value)) == value
