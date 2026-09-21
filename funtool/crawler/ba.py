"""需要登录态的商品请求工具。"""

import json
import os

import requests


class BodyGuardPharm:
    """调用商品接口，登录 cookie 只能通过环境变量注入。"""

    headers = {
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.ba.de/",
    }

    def __init__(self, cookies: dict[str, str] | None = None):
        """创建客户端；未传 cookie 时读取 `FUNTOOL_BA_COOKIES` JSON。"""
        raw = os.getenv("FUNTOOL_BA_COOKIES", "{}")
        try:
            configured = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ValueError("FUNTOOL_BA_COOKIES 必须是 JSON 对象") from error
        if not isinstance(configured, dict):
            raise ValueError("FUNTOOL_BA_COOKIES 必须是 JSON 对象")
        self.cookies = cookies if cookies is not None else configured

    def add_cart(self, product_id: int = 169826, qty: int = 1) -> dict:
        """把商品加入购物车并返回服务端 JSON。"""
        response = requests.get(
            "https://www.ba.de/v2/item/add",
            headers=self.headers,
            params={"product_id": product_id, "qty": qty},
            cookies=self.cookies,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
