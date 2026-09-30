from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from funget import download as funget_download
from funget import multi_thread_download, simple_download

__all__ = [
    "BaseDownLoad",
    "MultiThreadDownload",
    "PyCurlDownLoad",
    "SingleThreadDownload",
    "download",
]


class DownloadError(RuntimeError):
    """表示文件下载失败。"""


class BaseDownLoad:
    """下载器兼容基类。"""

    def __init__(self, session: Any | None = None) -> None:
        self.session = session

    def download(
        self,
        url: str,
        path: str | Path,
        size: int = 0,
        overwrite: bool = False,
    ) -> bool:
        """下载 URL 到本地路径，并返回是否成功。"""
        del size
        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not overwrite:
            return True
        try:
            return self._download(url, target, overwrite=overwrite)
        except (OSError, ValueError) as exc:
            raise DownloadError(f"下载失败: url={url}, path={target}") from exc

    def _download(self, url: str, path: Path, *, overwrite: bool) -> bool:
        raise NotImplementedError


class MultiThreadDownload(BaseDownLoad):
    """使用 `funget` Range 并发下载文件。"""

    def __init__(
        self,
        worker: int = 5,
        chunk_size: int = 10 * 1024 * 1024,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.worker = worker
        self.chunk_size = chunk_size

    def _download(self, url: str, path: Path, *, overwrite: bool) -> bool:
        return multi_thread_download(
            url,
            str(path),
            worker_num=self.worker,
            block_size=max(1, self.chunk_size // (1024 * 1024)),
            overwrite=overwrite,
        )


class SingleThreadDownload(BaseDownLoad):
    """使用 `funget` 单线程下载文件。"""

    def __init__(
        self,
        chunk: int = 1024 * 1024,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.chunk = chunk

    def _download(self, url: str, path: Path, *, overwrite: bool) -> bool:
        return simple_download(
            url,
            str(path),
            chunk_size=self.chunk,
            overwrite=overwrite,
        )


class PyCurlDownLoad(BaseDownLoad):
    """使用可选的 pycurl 后端下载文件。"""

    def _download(self, url: str, path: Path, *, overwrite: bool) -> bool:
        del overwrite
        try:
            import pycurl
        except ImportError as exc:
            raise DownloadError(
                "pycurl 后端未安装，请执行 `pip install fartool[download]`"
            ) from exc

        try:
            with path.open("wb") as output:
                client = pycurl.Curl()
                try:
                    client.setopt(pycurl.URL, url)
                    client.setopt(pycurl.WRITEDATA, output)
                    client.perform()
                finally:
                    client.close()
        except OSError as exc:
            raise DownloadError(f"下载失败: url={url}, path={path}") from exc
        return True


def download(
    url: str,
    path: str | Path,
    size: int = 0,
    session: Any | None = None,
    overwrite: bool = False,
    mode: Literal["auto", "single", "multi", "curl"] = "auto",
) -> bool:
    """下载 URL 到本地路径，默认由 `funget` 自动选择后端。"""
    if mode == "auto":
        return funget_download(url, str(path), overwrite=overwrite)

    backends: dict[str, type[BaseDownLoad]] = {
        "single": SingleThreadDownload,
        "multi": MultiThreadDownload,
        "curl": PyCurlDownLoad,
    }
    try:
        backend = backends[mode]
    except KeyError as exc:
        raise ValueError(f"不支持的下载模式: {mode}") from exc
    return backend(session=session).download(url, path, size, overwrite)
