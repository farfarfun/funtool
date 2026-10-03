from __future__ import annotations

import os
import sqlite3
import time
from time import strftime
from typing import Any

import pandas as pd

from ..log import log


class BaseTable:
    """按 ``columns`` 拼接 SQL 的轻量数据表基类，子类需实现 ``execute``。"""

    def __init__(self, table_name: str = 'default_table', columns: list[str] | None = None) -> None:
        """
        :param table_name: 表名。
        :param columns: 参与拼接 SQL 的列名列表。
        """
        self.table_name = table_name
        self.columns = columns
        self.logger = log(table_name)

    def execute(self, sql: str) -> Any:
        """执行 SQL 语句，子类必须实现。"""
        raise NotImplementedError("子类必须实现 execute")

    def insert(self, properties: dict) -> Any:
        """按 ``properties`` 插入一行数据，忽略主键冲突。"""
        properties = self.encode(properties)
        keys, values = self._properties2kv(properties)

        sql = """insert or ignore into {} ({}) values ({})""".format(self.table_name, ', '.join(keys),
                                                                     ', '.join(values))
        return self.execute(sql)

    def update(self, properties: dict, condition: dict) -> Any:
        """按 ``condition`` 匹配的行，把对应列更新为 ``properties`` 中的值。"""
        properties = self.encode(properties)
        equal = self._properties2equal(properties)
        equal2 = self._properties2equal(condition)
        sql = """update  {} set {} where {}""".format(self.table_name, ', '.join(equal), ' and '.join(equal2))
        return self.execute(sql)

    def decode(self, properties: dict) -> dict:
        """读取后对属性做反向转换，默认原样返回，子类可覆盖。"""
        return properties

    def encode(self, properties: dict) -> dict:
        """写入前对属性做转换，默认原样返回，子类可覆盖。"""
        return properties

    def count(self, properties: dict) -> int:
        """按 ``properties`` 中非空字段作为等值条件统计匹配行数。"""
        properties = properties or {}
        values = []
        for key in self.columns:
            value = str(properties.get(key, ''))
            if len(value) > 0 and len(key) > 0:
                values.append("{}='{}'".format(key, value))

        sql = """select count(1) from {} where {}""".format(self.table_name, ' and '.join(values))

        rows = self.execute(sql)
        for row in rows:
            return row[0]
        return 0

    def select_all(self) -> list:
        """查询当前表的全部行。"""
        return self.select("select * from table_name")

    def select(self, sql: str) -> list:
        """执行查询类 SQL（``table_name`` 占位符会被替换为真实表名）并返回所有行。"""
        sql = self.sql_format(sql)

        rows = self.execute(sql)
        return [] if rows is None else [row for row in rows]

    def _properties2kv(self, properties: dict) -> tuple[list[str], list[str]]:
        """按 ``columns`` 顺序，把非空属性拆成待插入的列名、值两个列表。"""
        if self.columns is None:
            raise ValueError("columns cannot be None")
        keys = []
        values = []
        for key in self.columns:
            value = str(properties.get(key, '')).replace("'", '')
            if len(key) > 0 and len(value) > 0:
                keys.append(key)
                values.append("'{}'".format(value))
        return keys, values

    def _properties2equal(self, properties: dict) -> list[str]:
        """按 ``columns`` 顺序，把非空属性拼接成 ``key=value`` 等值条件列表。"""
        if self.columns is None:
            raise ValueError("columns cannot be None")
        equals = []
        for key in self.columns:
            value = properties.get(key, None)
            if len(key) > 0 and value is not None:
                if isinstance(value, str):
                    equals.append("{}='{}'".format(key, value))
                else:
                    equals.append("{}={}".format(key, value))
        return equals

    def sql_format(self, sql: str) -> str:
        """把 SQL 中的 ``table_name`` 占位符替换为实际表名。"""
        sql = sql.replace('table_name', self.table_name)
        return sql


class SqliteTable(BaseTable):
    """基于 SQLite 的 :class:`BaseTable` 实现。"""

    def __init__(self, db_path: str, *args: Any, **kwargs: Any) -> None:
        """
        :param db_path: SQLite 数据库文件路径，所在目录不存在时会自动创建。
        """
        super().__init__(*args, **kwargs)
        self.db_path = db_path
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def execute(self, sql: str) -> sqlite3.Cursor:
        """执行 SQL 并提交事务；失败时记录异常上下文后重新抛出。"""
        try:
            rows = self.cursor.execute(sql)
            self.conn.commit()
            return rows
        except sqlite3.Error:
            self.logger.exception("执行 SQL 失败: {}", sql)
            raise

    def execute_without_commit(self, sql: str) -> sqlite3.Cursor:
        """执行 SQL 但不提交事务；失败时记录异常上下文后重新抛出。"""
        try:
            rows = self.cursor.execute(sql)
            return rows
        except sqlite3.Error:
            self.logger.exception("执行 SQL 失败: {}", sql)
            raise

    def close(self) -> None:
        """关闭游标与数据库连接。"""
        self.cursor.close()
        self.conn.close()

    def select_pd(self, sql: str = "select * from table_name") -> pd.DataFrame:
        """执行查询并以 DataFrame 形式返回结果。"""
        sql = self.sql_format(sql)
        return pd.read_sql(sql, self.conn)

    def save_and_truncate(self) -> pd.DataFrame:
        """把当前表导出为 CSV 备份，再清空表并执行 VACUUM 回收空间。"""
        result = pd.read_sql("select * from {}".format(self.table_name), self.conn)

        count = len(result)
        path = ('{}/{}-{}-{}'.format(os.path.dirname(self.db_path), self.table_name, count,
                                     strftime("%Y%m%d#%H:%M:%S", time.localtime())))
        result.to_csv(path)
        self.logger.info("save to csv:{}->{}".format(count, path))

        self.execute("delete from {}".format(self.table_name))
        self.logger.info("delete from {}".format(self.table_name))
        self.execute("VACUUM")
        self.logger.info("VACUUM")
        return result

    def vacuum(self) -> None:
        """执行 SQLite ``VACUUM``，整理并回收磁盘空间。"""
        self.execute("VACUUM")

    def insert_list(self, property_list: list[dict]) -> bool:
        """按 ``columns`` 顺序批量插入多行数据，主键冲突的行会被忽略。"""
        values = [tuple([properties.get(key, '') for key in self.columns]) for properties in property_list]
        sql = "insert or ignore into {} values ({})".format(self.table_name, ','.join(['?'] * len(self.columns)))

        self.cursor.executemany(sql, values)
        self.conn.commit()
        return True
