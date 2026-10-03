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

## 第三方代码

`src/funtool/convert/curl2py.py` 的解析逻辑改写自 [spulec/uncurl](https://github.com/spulec/uncurl)
（Apache License 2.0，原始版权 © 2012 Steve Pulec）。该文件保留来源与许可证说明，与本仓库
整体的 MIT 协议不冲突（Apache-2.0 允许在其他协议项目中使用，只需保留原始版权与许可证声明）。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
