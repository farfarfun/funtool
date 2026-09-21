# funtool

`funtool` 是 farfarfun 的 Python 工具集，提供下载、爬虫、路径、时间和数据库辅助 API。

> ⚠️ PyPI 上的 `funtool` 这个名字已被无关第三方项目占用（[pjanis/funtool](https://github.com/pjanis/funtool)），
> **不要** `pip install funtool`，本仓库真正的发布名是 `farfuntool`。

```bash
uv add farfuntool
```

## 最小示例

```python
from funtool.time import now2time
from funtool.path import path_parse

print(now2time())
print(path_parse("README.md"))
```

## 工具

| tool                          | desc               |
| ------------------------------ | ------------------ |
| [secret](./example/secret.py) | 账号密码的加密解密 |

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
