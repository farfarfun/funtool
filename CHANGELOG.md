# 更新日志

## 0.6.26

### 新增

- 增加下载、数据库和时间 API 的回归测试。

### 修复

- 移除硬编码会话凭据、导入时网络请求和完整请求头输出。
- 默认 HTTP 下载改用 `funget`，不再隐式依赖 `pycurl`。

### 变更

- **破坏性变更**：包名和发布名由 `funtool`/`farfuntool` 统一为 `fartool`，源码迁移到 `src/fartool/`。请执行 `uv remove farfuntool && uv add fartool`，并将 `import funtool` 改为 `import fartool`。
- Python 最低版本提升到 3.12，以匹配 `funget` 的运行时要求。

### 废弃

- 无。
