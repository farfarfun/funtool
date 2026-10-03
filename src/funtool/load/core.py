from __future__ import annotations

import os
import pickle
from collections.abc import Callable
from typing import Any

import pandas as pd


class DataLoadAndSave:
    """按文件名后缀自动选择序列化方式的数据读写辅助类。"""

    def __init__(self, path_dir: str) -> None:
        """
        :param path_dir: 数据文件所在目录。
        """
        self.path_dir = path_dir

    def file_path(self, filename: str) -> str:
        """拼接 ``path_dir`` 与文件名，返回完整路径。"""
        return os.path.join(self.path_dir, filename)

    def save_pickle(self, data: Any, filename: str) -> None:
        """把 ``data`` 以 pickle 格式写入文件。"""
        with open(self.file_path(filename), 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    def save_json(self, data: pd.DataFrame, filename: str) -> None:
        """把 DataFrame 以 JSON 格式写入文件。"""
        data.to_json(self.file_path(filename))

    def save_csv(self, data: pd.DataFrame, filename: str) -> None:
        """把 DataFrame 以 CSV 格式写入文件。"""
        data.to_csv(self.file_path(filename))

    def load_pickle(self, filename: str) -> Any:
        """从 pickle 文件读取数据。"""
        with open(self.file_path(filename), 'rb') as f:
            data = pickle.load(f)
            return data

    def load_json(self, filename: str) -> pd.DataFrame:
        """从 JSON 文件读取数据为 DataFrame。"""
        return pd.read_json(self.file_path(filename))

    def load_csv(self, filename: str) -> pd.DataFrame:
        """从 CSV 文件读取数据为 DataFrame。"""
        return pd.read_csv(self.file_path(filename))

    def save(self, data: Any, filename: str) -> None:
        """按文件名后缀（``.pkl``/``.csv``/``.json``，默认 pickle）保存数据。"""
        if '.pkl' in filename:
            self.save_pickle(data, filename)
        elif '.csv' in filename:
            self.save_csv(data, filename)
        elif '.json' in filename:
            self.save_json(data, filename)
        else:
            self.save_pickle(data, filename)

    def load(self, filename: str) -> Any:
        """按文件名后缀（``.pkl``/``.csv``/``.json``，默认 pickle）加载数据。"""
        if '.pkl' in filename:
            return self.load_pickle(filename)
        elif '.csv' in filename:
            return self.load_csv(filename)
        elif '.json' in filename:
            return self.load_json(filename)
        else:
            return self.load_pickle(filename)

    def load_save(
        self,
        filename: str,
        fun: Callable[[], Any] | None = None,
        overwrite: bool = False,
    ) -> Any:
        """
        文件已存在且不要求覆盖时直接加载；否则调用 ``fun()`` 生成数据并保存后返回。

        :param filename: 目标文件名。
        :param fun: 文件不存在或需要覆盖时用于生成数据的无参可调用对象。
        :param overwrite: 是否强制重新生成并覆盖已有文件。
        :return: 加载或新生成的数据。
        """
        if os.path.exists(self.file_path(filename)) and not overwrite:
            return self.load(filename)
        else:
            data = fun()
            self.save(data, filename)
            return data
