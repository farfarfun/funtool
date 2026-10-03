# 更新日志

## 未发布

### 新增

- 增加下载、数据库、时间、路径、加解密、`load`/`save` 往返 API 的回归测试，覆盖
  `join_path` 缺省参数崩溃、`m3u8`/`story` 模块 `logger` 未定义、`SqliteTable`
  增改查链路等回归点。
- `funtool.load` 补齐 `DataLoadAndSave` 的包级导出；顶层 `__init__` 补齐 `encrypt`/`decrypt` 导出，
  `funtool.path` 补齐 `join_path` 导出，修复示例脚本的导入错误。

### 修复

- 移除硬编码会话凭据、导入时网络请求和完整请求头输出。
- 默认 HTTP 下载改用 `funget`，不再隐式依赖 `pycurl`；`pycurl` 后端缺失时的安装提示改回
  真实发布名 `farfuntool[download]`（此前误写成不可安装的 `funtool[download]`）。
- 修复解压工具 `un_tar`/`un_zip` 未校验成员路径导致的路径穿越（zip-slip）风险；修复 `decompress` 对 `.gz`/`.tgz` 误传相对路径的调用错误；`un_rar` 不再用 `os.chdir` 改变进程全局工作目录。
- 修复 `download/m3u8.py`、`download/story.py` 缺失 `logger` 定义导致下载完成/失败分支必然
  `NameError` 的问题；下载分片重试失败路径改用 `farlog` 记录异常上下文（不再静默吞错），
  不再用 `print` 输出诊断信息（含 m3u8 解密 key，避免敏感信息落日志）；`logger.warn` 改为
  未废弃的 `logger.warning`。
- 修复 `path.join_path(child_path)`（省略 `parent_path`）必然 `TypeError` 的问题：原实现把
  默认值 `None` 直接传给 `os.path.join`，现回退为按当前工作目录解析 `child_path`。
- 为 `path/core.py`、`database/core.py`（`BaseTable`/`SqliteTable`）、`load/core.py`
  （`DataLoadAndSave`）的全部公开函数/方法补齐类型标注与中文 docstring（#758 finding 6）。
- 修复示例脚本 `example/example-log.py`、`example/path-example.py`、`example/secret.py` 引用
  不存在的 `logtool`/`pathtool` 模块路径和未导出的 `encrypt`/`decrypt`，并修复
  `example-log.py` 中未定义的裸 `info(...)` 调用（应为 `logger.info(...)`）。
- 撤销此前被自动化流水线误执行的仓库改名（`fartool`，PyPI 从未发布、404）：仓库名、导入名、源码目录名统一恢复为 `funtool`，发布名维持既有历史例外 `farfuntool` 不变；`uv.lock` 同步重新生成。
- 补充 `convert/curl2py.py` 改写自第三方 `uncurl`（Apache-2.0）的来源与许可证说明。
- `pyproject.toml` 新增 `[tool.ruff.lint] ignore = ["PLE1205"]`：farlog 的 `{}` 占位符调用
  被 ruff 误判为 stdlib logging 的 `%s` 语法并误报参数过多（沿用组织既有做法 #695）。

### 变更

- 源码目录迁移到 `src/funtool/`，符合标准 `src/<pkg>/` 布局（包名与仓库名、导入名保持一致）。
- Python 最低版本提升到 3.12，以匹配组织自有下载库 `funget` 的运行时要求。
- `farlog` 依赖下限提升到 `>=1.1.7`，匹配组织兼容包版本要求。

### 废弃

- 无。
