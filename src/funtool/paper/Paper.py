from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import requests
from bs4 import BeautifulSoup

PUBLICATIONS_URL = "https://app.webofknowledge.com/api/rrc/author/publications"
DETAIL_URL = "https://apps.webofknowledge.com/InboundService.do"


class PaperRequestError(RuntimeError):
    """表示论文服务请求或解析失败。"""


def get_list(
    author_id: str,
    *,
    cookies: Mapping[str, str],
    headers: Mapping[str, str] | None = None,
    timeout: float = 30,
) -> list[dict[str, Any]]:
    """查询作者论文列表，调用方必须显式提供有效会话 cookie。"""
    params = {
        "authorId": author_id,
        "batch": "true",
        "limit": "50",
        "offset": "0",
        "order": "desc",
        "sort": "year",
    }
    try:
        response = requests.get(
            PUBLICATIONS_URL,
            headers=headers,
            params=params,
            cookies=cookies,
            timeout=timeout,
        )
        response.raise_for_status()
        payload = json.loads(response.text)
        return payload["hits"]
    except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
        raise PaperRequestError(f"论文列表请求失败: author_id={author_id}") from exc


def get_detail(
    meta: dict[str, Any],
    *,
    cookies: Mapping[str, str],
    headers: Mapping[str, str] | None = None,
    timeout: float = 30,
) -> str:
    """查询论文详情并把解析出的字段写入 ``meta``。"""
    try:
        ut = str(meta["ut"])
    except KeyError as exc:
        raise ValueError("论文元数据缺少 ut 字段") from exc

    params = {
        "customersID": "RRC",
        "mode": "FullRecord",
        "product": "WOS",
        "action": "retrieve",
        "UT": ut,
    }
    try:
        response = requests.get(
            DETAIL_URL,
            headers=headers,
            params=params,
            cookies=cookies,
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise PaperRequestError(f"论文详情请求失败: ut={ut}") from exc

    soup = BeautifulSoup(response.text, "lxml")
    source_title = soup.find("p", class_="sourceTitle")
    meta["sourceTitle"] = source_title.get_text(strip=True) if source_title else ""
    for line in soup.find_all("p", class_="FR_field"):
        values = [item.get_text(strip=True).strip(":") for item in line.find_all()]
        if len(values) >= 2:
            meta[values[0]] = values[1]
    return response.text
