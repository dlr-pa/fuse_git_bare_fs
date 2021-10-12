"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-12 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os
import time


class _EmptyAttrMixin():
    """
    provide some standard st_modes:

    +---------------+------+---------+----------+-----------------+
    | symbolic mode | mode | st_mode | git mode | comment         |
    +---------------+------+---------+----------+-----------------+
    | -rw-r--r--    | 644  | 33188   | 100644   | normal file     |
    | -rwxr-xr-x    | 755  | 33261   | 100755   | executable file |
    | lrwxrwxrwx    | -    | 41471   | 120000   | symbolic link   |
    | drwxr-xr-x    | 755  | 16877   | -        | directory       |
    | -rw-r-----    | 640  | 33184   | -        | normal file     |
    | -rwxr-x---    | 750  | 33256   | -        | executable file |
    | drwxr-x---    | 750  | 16872   | -        | directory       |
    +---------------+------+---------+----------+-----------------+

    0o100644 == 33188
    0o100755 == 33261
    0o120000 == 40960
    """
    # pylint: disable=too-few-public-methods
    _empty_dir_attr = {'st_mode': 16877, 'st_size': 4096,
                       'st_uid': os.geteuid(), 'st_gid': os.getegid()}
    _empty_dir_attr['st_atime'] = _empty_dir_attr['st_mtime'] = \
        _empty_dir_attr['st_ctime'] = int(time.time())
    _empty_file_attr = {'st_mode': 33188,
                        'st_uid': os.geteuid(), 'st_gid': os.getegid()}
    _empty_file_attr['st_atime'] = _empty_file_attr['st_mtime'] = \
        _empty_file_attr['st_ctime'] = int(time.time())
