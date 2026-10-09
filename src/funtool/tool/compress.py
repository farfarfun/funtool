import gzip
import os
from pathlib import Path
import shutil
import tarfile
import zipfile

"""
# gz： 即gzip。通常仅仅能压缩一个文件。与tar结合起来就能够实现先打包，再压缩。
# tar： linux系统下的打包工具。仅仅打包。不压缩
# tgz：即tar.gz。先用tar打包，然后再用gz压缩得到的文件
# zip： 不同于gzip。尽管使用相似的算法，能够打包压缩多个文件。只是分别压缩文件。压缩率低于tar。
# rar：打包压缩文件。最初用于DOS，基于window操作系统。
"""


def _safe_member_path(target_dir, member_name):
    """返回归档成员在目标目录中的安全路径，越界时抛出 ValueError。"""
    target = Path(target_dir).resolve()
    member_path = (target / member_name).resolve()
    try:
        member_path.relative_to(target)
    except ValueError as exc:
        raise ValueError(f"归档成员路径越出目标目录: {member_name}") from exc
    return member_path


def _validate_member_paths(target_dir, members):
    """验证所有归档成员都会写入 ``target_dir`` 内。"""
    for member in members:
        _safe_member_path(target_dir, member)


def un_gz(file_path, target_path=None):
    """
    ungz zip file
    # gz
    # 因为gz一般仅仅压缩一个文件，全部常与其它打包工具一起工作。比方能够先用tar打包为XXX.tar,然后在压缩为XXX.tar.gz
    # 解压gz，事实上就是读出当中的单一文件
    """
    file_path = os.fspath(file_path)
    target_path = os.fspath(target_path) if target_path else file_path.replace(".gz", "")
    target_path = target_path.replace(".tgz", ".tar")

    # 创建gzip对象
    with gzip.GzipFile(file_path) as g_file, open(target_path, "wb") as output:
        shutil.copyfileobj(g_file, output)
    return target_path


def un_tar(file_path, target_dir=None):
    """
    untar zip file
    # tar
    # XXX.tar.gz解压后得到XXX.tar，还要进一步解压出来。
    # 注：tgz与tar.gz是同样的格式，老版本号DOS扩展名最多三个字符，故用tgz表示。
    # 因为这里有多个文件，我们先读取全部文件名称。然后解压。例如以下：
    # 注：tgz文件与tar文件同样的解压方法。
    """
    file_path = os.fspath(file_path)
    target_dir = os.fspath(target_dir) if target_dir else file_path + "_files"

    Path(target_dir).mkdir(parents=True, exist_ok=True)
    with tarfile.open(file_path) as tar:
        members = tar.getmembers()
        _validate_member_paths(target_dir, (member.name for member in members))
        # ``data`` 过滤器还会拒绝设备文件及越界的符号/硬链接。
        tar.extractall(target_dir, members=members, filter="data")


def un_zip(file_path, target_dir=None):
    """
    unzip zip file
    """
    file_path = os.fspath(file_path)
    target_dir = os.fspath(target_dir) if target_dir else file_path + "_files"

    Path(target_dir).mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(file_path) as zip_file:
        members = zip_file.infolist()
        _validate_member_paths(target_dir, (member.filename for member in members))
        zip_file.extractall(target_dir, members=members)


def un_rar(file_path, target_dir=None):
    """
    unrar zip file
    # rar
    # 由于rar通常为window下使用，须要额外的Python包rarfile。
    #
    # 可用地址： http://sourceforge.net/projects/rarfile.berlios/files/rarfile-2.4.tar.gz/download
    #
    # 解压到Python安装文件夹的/Scripts/文件夹下，在当前窗体打开命令行,
    #
    # 输入Python setup.py install
    #
    # 安装完毕。
    """
    import rarfile
    file_path = os.fspath(file_path)
    target_dir = os.fspath(target_dir) if target_dir else file_path + "_files"
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    with rarfile.RarFile(file_path) as rar:
        members = rar.infolist()
        _validate_member_paths(target_dir, (member.filename for member in members))
        if any(member.is_symlink() for member in members):
            raise ValueError("RAR 归档不支持包含符号链接的成员")
        rar.extractall(path=target_dir, members=members)


def decompress(file_path, target_dir=None):
    file_path = os.fspath(file_path)
    target_dir = os.fspath(target_dir) if target_dir else file_path + "_files"
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    file_name = os.path.basename(file_path)
    extension = file_name.split('.')[-1]
    if extension in ('gz', 'tgz'):
        target_path = un_gz(file_path)
        un_tar(target_path, target_dir)
    elif extension == 'zip':
        un_zip(file_path, target_dir)
    elif extension == 'rar':
        un_rar(file_path, target_dir)
    else:
        raise Exception('Not implement yet, please write the issue.')
