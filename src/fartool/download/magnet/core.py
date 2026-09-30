from __future__ import annotations

from typing import Any

import feedparser


def fetch_feed(url: str) -> dict[str, Any]:
    """解析 RSS 地址并返回 feedparser 结果。"""
    return dict(feedparser.parse(url))
