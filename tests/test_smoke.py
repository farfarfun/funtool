def test_import():
    import fartool  # noqa: F401


def test_paper_import_has_no_network_side_effects(monkeypatch):
    import requests

    def fail_request(*args, **kwargs):
        raise AssertionError("导入模块时不应发起网络请求")

    monkeypatch.setattr(requests, "get", fail_request)
    from fartool.paper import Paper  # noqa: F401
