"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-10-06 (last change).
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
    | -rw-rw-r--    | 664  | 33204   | 100644   | normal file     |
    | -rwxrwxr-x    | 775  | 33277   | 100755   | executable file |
    | lrwxrwxrwx    | -    | 41471   | 120000   | symbolic link   |
    | drwxrwxr-x    | 775  | 16893   | -        | directory       |
    | -rw-r-----    | 640  | 33184   | -        | normal file     |
    | -rwxr-x---    | 750  | 33256   | -        | executable file |
    | drwxrwx---    | 770  | 16888   | -        | directory       |
    +---------------+------+---------+----------+-----------------+
    """
    # pylint: disable=too-few-public-methods
    _empty_dir_attr = {'st_mode': 16893, 'st_size': 4096,
                       'st_uid': os.geteuid(), 'st_gid': os.getegid()}
    _empty_dir_attr['st_atime'] = _empty_dir_attr['st_mtime'] = \
        _empty_dir_attr['st_ctime'] = int(time.time())
    _empty_file_attr = {'st_mode': 33204,
                        'st_uid': os.geteuid(), 'st_gid': os.getegid()}
    _empty_file_attr['st_atime'] = _empty_file_attr['st_mtime'] = \
        _empty_file_attr['st_ctime'] = int(time.time())
