"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-13 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import os
import time


class _EmptyAttrMixin():
    # pylint: disable=too-few-public-methods
    _empty_dir_attr = {'st_mode': 16893, 'st_size': 4096,
                       'st_uid': os.geteuid(), 'st_gid': os.getegid()}
    _empty_dir_attr['st_atime'] = _empty_dir_attr['st_mtime'] = \
        _empty_dir_attr['st_ctime'] = int(time.time())
    _empty_file_attr = {'st_mode': 33204,
                        'st_uid': os.geteuid(), 'st_gid': os.getegid()}
    _empty_file_attr['st_atime'] = _empty_file_attr['st_mtime'] = \
        _empty_file_attr['st_ctime'] = int(time.time())
