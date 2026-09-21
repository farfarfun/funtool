"""电影资源页面解析工具。"""

import re

import requests
from lxml import html


def get_html(keywd: str, url: str) -> str:
    """获取搜索页面 HTML。"""
    response = requests.get(
        url % keywd,
        params={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()
    return response.content.decode("utf-8")


def get_movielink(text: str) -> list[tuple[str, str]]:
    """从搜索页面提取资源链接和类型。"""
    tree = html.fromstring(text)
    links = []
    for item in tree.xpath('//div[@class="clearfix search-item"]'):
        link = item.xpath('div[2]/div/a/@href')
        kind = item.xpath("em/text()")
        if link and kind:
            links.append((link[0], kind[0]))
    return links


def get_downloadlink(link: str, type_link: str = "电影") -> str:
    """获取资源页跳转到下载页面的链接。"""
    channel = "tv" if type_link == "电视剧" else "movie"
    response = requests.get(
        "http://www.zimuzu.tv/resource/index_json/rid/%s/channel/%s"
        % (link.split("/")[-1], channel),
        params={"User-Agent": "Mozilla/5.0", "Referer": "http://www.zimuzu.tv%s" % link},
        timeout=30,
    )
    response.raise_for_status()
    data = "".join(response.content.decode("utf-8").split("=")[1:])
    match = re.search(r'<h3><a href(.*?) target', data)
    if not match:
        raise ValueError("资源页面未找到下载链接")
    return match.group(1).replace("\\", "").replace('"', "").strip()


def get_download(url: str) -> list[dict[str, str]]:
    """从资源页面提取百度云和电驴下载链接。"""
    response = requests.get(url, params={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    tree = html.fromstring(response.content.decode("utf-8"))
    result = []
    for item in tree.xpath('//div[@class="tab-content info-content"]//div[@class="tab-content info-content"]'):
        names = item.xpath('div[1]//div[@class="title"]/span[1]/text()')
        bdy = item.xpath('div[1]//div[@class="title"]/ul/li[2]/a/@href')
        ed2k = item.xpath('div[2]//ul[@class="down-links"]/li[2]/a/@href')
        result.extend({"name": name, "bdy": cloud, "ed2k": magnet} for name, cloud, magnet in zip(names, bdy, ed2k))
    return result
