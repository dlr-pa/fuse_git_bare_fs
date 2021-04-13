"""
:Author: Daniel Mohr
:Email: daniel.mohr@dlr.de
:Date: 2021-04-13 (last change).
:License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.
"""

import fusepy  # https://github.com/fusepy/fusepy
import time


class _empty_attr_mixin():
    _empty_attr = {'st_mode': 16893, 'st_size': 4096}
    _empty_attr['st_uid'], _empty_attr['st_gid'], _ = fusepy.fuse_get_context()
    _empty_attr['st_atime'] = _empty_attr['st_mtime'] = \
        _empty_attr['st_ctime'] = time.time()
