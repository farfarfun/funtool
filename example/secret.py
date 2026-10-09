"""演示本地加密和解密，不读取或输出任何已保存的密钥。"""

import os

from funtool import decrypt, encrypt


def run1():
    text = os.environ.get("FUNTOOL_EXAMPLE_SECRET", "My super secret message")
    encrypted = encrypt(text)
    assert decrypt(encrypted) == text
    print("加密和解密成功")


if __name__ == "__main__":
    run1()
