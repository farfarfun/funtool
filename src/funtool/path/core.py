from __future__ import annotations

import os
import shutil

from ..log import logger


def info(msg: object) -> None:
    """把 ``msg`` 转发给模块级 logger 记录为 info 级别日志。"""
    logger.info(msg)


def rename(src: str, dst: str) -> None:
    """若 ``src`` 存在则重命名为 ``dst``，否则记录错误日志。"""
    if os.path.exists(src):
        os.rename(src, dst)
    else:
        logger.error("{} not exist!".format(src))


def removedirs(name: str) -> None:
    """递归删除目录 ``name`` 及其全部内容。"""
    shutil.rmtree(name)


def path_parse(path: str | None) -> str | None:
    """展开 ``~`` 并把相对路径解析为相对当前工作目录的绝对路径；``None`` 原样返回。"""
    if path is None:
        return path
    # ~处理
    path = os.path.expanduser(path)
    if not path.startswith('/'):
        return os.path.join(os.getcwd(), path)
    return path


def path_join(parent_path: str, child_path: str) -> str:
    """把 ``child_path`` 拼接到解析后的 ``parent_path`` 之后。"""
    return os.path.join(path_parse(parent_path), child_path)


def join_path(child_path: str, parent_path: str | None = None) -> str:
    """
    拼接路径；省略 ``parent_path`` 时直接按当前工作目录解析 ``child_path``。

    :param child_path: 子路径。
    :param parent_path: 父路径，省略时回退为当前工作目录。
    """
    if parent_path is None:
        return path_parse(child_path)
    return path_join(parent_path, child_path)


def delete_file(file_path: str) -> None:
    """若 ``file_path`` 对应文件存在则删除。"""
    if exists_file(file_path):
        info('file exist and delete')
        os.remove(file_path)


def exists_dir(file_dir: str, mkdir: bool = False) -> bool:
    """判断目录是否存在，必要时可自动创建。"""
    return exists(file_dir=file_dir, mkdir=mkdir, mode='path')


def exists_file(file_path: str, mkdir: bool = False) -> bool:
    """判断文件是否存在，必要时自动创建其所在目录。"""
    return exists(file_path=file_path, mkdir=mkdir, mode='file')


def exists(
    file_path: str | None = None,
    file_dir: str | None = None,
    file_name: str | None = None,
    mode: str = 'file',
    mkdir: bool = False,
) -> bool:
    """
    文件或者目录是否存在，不存在是否需要新建
    :param file_path: 文件路径
    :param file_dir:  文件目录
    :param file_name: 文件名称
    :param mode:  file-文件，path-目录
    :param mkdir: 目录不存在是否需要新建
    :return: 是否存在
    """

    file_path = path_parse(file_path)
    file_dir = path_parse(file_dir)

    if mode == 'file':
        if file_path is not None:
            file_dir, file_name = os.path.split(file_path)
        elif file_dir is not None and file_name is not None:
            file_path = os.path.join(file_dir, file_name)
        else:
            logger.warning("file_path or file_dir&file_name is needed")
            return False

        if os.path.exists(file_dir) and os.path.isdir(file_dir):
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return True
            else:
                return False
        elif not os.path.exists(file_dir) and mkdir:
            makedirs(file_dir)
        return False

    elif mode == 'path':
        if file_path is not None:
            file_dir, file_name = os.path.split(file_path)
        elif file_dir is None:
            logger.warning("file_path or file_dir is needed")
            return False

        if os.path.exists(file_dir) and os.path.isdir(file_dir):
            return True
        elif mkdir:
            makedirs(file_dir)
        return False

    return False


def exist_and_create(file_dir: str) -> None:
    """目录不存在时创建，存在时什么都不做。"""
    if os.path.exists(file_dir) and os.path.isdir(file_dir):
        return

    os.makedirs(file_dir)


def _file_path(path: str) -> str:
    """返回 ``path`` 所在目录。"""
    return os.path.dirname(path)


def _file_name(path: str) -> str:
    """返回 ``path`` 的文件名部分。"""
    return os.path.basename(path)


def makedirs(name: str, mode: int = 0o777, exist_ok: bool = False) -> None:
    """递归创建目录，等价于 ``os.makedirs``。"""
    os.makedirs(name, mode=mode, exist_ok=exist_ok)


def meta(file_dir: str, file_name: str | None = None, deep: int = 1) -> dict:
    """
    返回文件的基本信息
    :param file_dir: 路径
    :param file_name: 文件名称
    :param deep: 深度
    :return:文件信息
    """
    return {
        'dir': file_dir,
        'name': file_name,
        'path': file_dir if file_name is None else os.path.join(file_dir, file_name),
        'isdir': True if file_name is None else False,
        'deep': deep
    }


def list_file(file_dir: str, deep: int = 1) -> list[str]:
    """
    返回这个目录下所有的文件，深度为deep
    :param file_dir: 路径
    :param deep:深度
    :return: 所有目录和文件
    """
    result = []
    if deep <= 0:
        return result
    for file_name in os.listdir(file_dir):
        tmp_path = os.path.join(file_dir, file_name)
        if os.path.isfile(tmp_path):
            result.append(tmp_path)
        elif os.path.isdir(tmp_path):
            result.extend(list_file(tmp_path, deep=deep - 1))
    return result


def merge_file(source_file: list[str], target_file: str) -> None:
    """把 ``source_file`` 列表中的多个文件按顺序合并写入 ``target_file``。"""
    flag = 0  # 计数器

    info("开始。。。。。")

    with open(target_file, 'w+') as write_file:
        for file_path in source_file:
            with open(file_path, 'r') as f_source:
                for line in f_source:
                    write_file.write(line)
            write_file.write('\n')

    info('done ' + str(flag) + '\t' + target_file)
    info("完成。。。。。")


def split_file(source_file: str, target_dir: str, max_line: int = 2000000) -> None:
    """把 ``source_file`` 按最多 ``max_line`` 行一份，拆分写入 ``target_dir`` 下的多个 CSV 文件。"""
    file_name = _file_name(source_file)
    flag = 0  # 计数器
    name = 1  # 文件名

    info("开始。。。。。")

    def get_filename():
        return str(target_dir) + file_name + '-split-' + str(name) + '.csv'

    write_file = open(get_filename(), 'w+')

    with open(source_file, 'r') as f_source:
        for line in f_source:
            flag += 1

            write_file.write(line)

            if flag == max_line:
                info('done ' + str(flag) + '\t' + get_filename())
                name += 1
                flag = 0

                write_file.close()
                write_file = open(get_filename(), 'w+')
    write_file.close()
    info('done ' + str(flag) + '\t' + get_filename())
    info("完成。。。。。")
