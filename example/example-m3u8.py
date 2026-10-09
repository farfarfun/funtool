"""运行方式：python example/example-m3u8.py <m3u8-url> <输出目录> <文件名>。"""

import argparse

from funtool.download.m3u8 import m3u8Downloader


def download(url, output_dir, file_name):
    """下载用户明确提供的 m3u8 地址。"""
    m3u8Downloader().start(url, output_dir, file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("output_dir")
    parser.add_argument("file_name")
    args = parser.parse_args()
    download(args.url, args.output_dir, args.file_name)
